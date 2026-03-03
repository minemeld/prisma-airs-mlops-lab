# Palo Alto Networks AIRS Model Scanning - Deep Dive Research

**Date**: 2026-02-04
**Researcher**: Ava Sterling (Claude Researcher)
**Subject**: Prisma AIRS AI Model Security - SDK, Scanning, Verdicts, and CI/CD Best Practices

---

## Table of Contents

1. [How Model Scanning Works](#1-how-model-scanning-works)
2. [Verdict Types and EvalOutcome](#2-verdict-types-and-evaloutcome)
3. [Pickle vs Safetensors Handling](#3-pickle-vs-safetensors-handling)
4. [Security Groups](#4-security-groups)
5. [Known Malicious Models on HuggingFace](#5-known-malicious-models-on-huggingface)
6. [CI/CD Best Practices](#6-cicd-best-practices)
7. [Strategic Analysis](#7-strategic-analysis)

---

## 1. How Model Scanning Works

### Architecture Overview

Prisma AIRS AI Model Security scans ML model artifacts at the file level, inspecting model weights, metadata, serialization format, and embedded code. It supports **35+ model formats** including PyTorch (.pt, .bin), TensorFlow (SavedModel, .h5), ONNX, GGUF, NeMo, and safetensors.

### Scan Process

1. **Format Introspection**: AIRS first identifies the model format through file introspection
2. **Threat Taxonomy Mapping**: After determining the model type, AIRS maps it to its taxonomy of model vulnerability threats
3. **Deep Scan Coordination**: AIRS coordinates specific deeper scans required for that model format
4. **Rule Evaluation**: Results are evaluated against all enabled rules in the associated Security Group
5. **Aggregate Outcome**: An aggregate evaluation outcome is computed based on rule results and the group's configured threshold

### What It Scans For

AIRS detects the following threat categories:

| Threat Category | Description | Severity |
|---|---|---|
| **Deserialization Threats** | Arbitrary code execution during model loading via pickle/marshal | Critical/High |
| **Malicious Code Execution** | Embedded malicious payloads that execute at load or inference time | Critical |
| **Neural Backdoors** | "Manchurian Candidate" models with hidden triggers that alter behavior | High |
| **Runtime Threats** | Code that executes malicious operations during model inference | High |
| **Unapproved Formats** | Models stored in formats not approved by policy (e.g., GGUF) | Medium |
| **Invalid Licenses** | Models with licenses incompatible with organizational policy | Low/Medium |
| **Insecure Formats** | Formats inherently vulnerable to code injection (pickle-based) | Medium/High |

### Security Rules

Rules are the core enforcement mechanism. Each rule corresponds to a grouped set of specific threats. Key characteristics:

- Rules can be set to **Block** (hard fail) or **Alert** (warning only)
- Rules are associated with Security Groups
- A model fails if any **blocking** rule detects a violation
- Non-blocking rules record findings without preventing model approval
- The Default security groups have some blocking rules enabled, so 1/7 rules commonly triggers on pickle-based models

### Scan Response Structure

> **CORRECTED (2026-02-05):** The original JSON example below was fabricated. The actual SDK response structure is documented here from live testing.

```json
{
  "uuid": "a1b2c3d4-...",
  "eval_outcome": "BLOCKED",
  "eval_summary": {
    "rules_passed": 6,
    "rules_failed": 1,
    "total_rules": 7
  },
  "security_group_uuid": "00000000-0000-0000-0000-000000000002",
  "security_group_name": "Default GCS",
  "model_uri": "gs://bucket/model",
  "source_type": "GCS",
  "model_formats": ["openvino_bin"],
  "total_files_scanned": 12,
  "total_files_skipped": 0
}
```

**Note:** The SDK does NOT return `violations`, `findings`, per-rule detail, or severity counts. Only aggregate `rules_passed`/`rules_failed`/`total_rules` are available.

---

## 2. Verdict Types and EvalOutcome

### SDK Enum: `EvalOutcome`

> **CORRECTED (2026-02-05):** The original version of this section contained hallucinated verdict values (`FAIL`, `MALICIOUS`, `WARNING`) that do not exist in the SDK. The corrected information below is based on live SDK testing.
>
> **CREDENTIALS NOTE (2026-03-03):** Use `MODEL_SECURITY_CLIENT_ID` and `MODEL_SECURITY_CLIENT_SECRET` — these are what the SDK reads from the environment. All lab scripts standardized on this naming.

The AIRS SDK uses an enum `EvalOutcome` with exactly **4 values**:

| EvalOutcome | Meaning | CI/CD Action |
|---|---|---|
| **ALLOWED** | No blocking rules failed | Exit 0 |
| **BLOCKED** | At least one blocking-enabled rule detected an issue | Exit 1 (or Exit 0 with `--warn-only`) |
| **PENDING** | Scan still in progress | Wait/retry |
| **ERROR** | Scan encountered an error | Exit 1 |

**Values that DO NOT exist:** `MALICIOUS`, `FAIL`, `WARNING`, `PASS`. These were hallucinated during AI-assisted development and never appeared in any actual scan response.

### Verdict Logic — Depends on Security Group Blocking Config

The critical insight: `eval_outcome` depends on whether the triggering rule has `Blocking: On` in the Security Group configuration in SCM:

```
Same model, same 1/7 rule failure:
  Warning-only group (all blocking OFF)  → eval_outcome: ALLOWED
  Blocking group (all blocking ON)       → eval_outcome: BLOCKED
  Default GCS group (some blocking ON)   → eval_outcome: BLOCKED
```

- `rules_failed` counts ALL rules that detected issues (blocking OR non-blocking)
- `eval_outcome` is BLOCKED only when a **blocking-enabled** rule detects an issue
- A model can have `rules_failed > 0` and still be `ALLOWED`

### Important SDK Quirk

The SDK returns enum objects, NOT strings:

```python
# Raw: EvalOutcome.BLOCKED (not "BLOCKED")
# Must parse:
verdict = str(raw_verdict).split(".")[-1].upper()
```

### BLOCKED Is a Policy Decision, Not a Threat Detection

**BLOCKED** means the security group's rules flagged something (unapproved format, insecure serialization, etc.). The model itself may be perfectly safe, but it violates organizational security policy. This is configurable — you can adjust which rules block vs. alert in SCM.

In CI/CD, **BLOCKED should NOT necessarily halt the pipeline** when using `--warn-only` mode. The `--warn-only` flag treats BLOCKED as exit 0 with a warning, while ERROR always exits 1.

---

## 3. Pickle vs Safetensors Handling

### Pickle: The Dangerous Default

Pickle is Python's built-in serialization format used extensively by PyTorch. It is **inherently unsafe** because:

- Pickle serializes Python objects by creating a program to reconstruct them
- The `__reduce__` method allows arbitrary code execution during deserialization
- Loading a pickle file (`torch.load()`) executes embedded code automatically
- Over **80% of models on HuggingFace** use pickle-based serialization

**AIRS scanning behavior for pickle models:**
- Pickle-based models (.pt, .bin) are always inspected for deserialization threats
- Default security groups with blocking rules flag pickle format as a policy violation under "Insecure Formats" or "Unapproved Formats"
- This explains why Default groups commonly BLOCK with 1/7 rules failing — the pickle format itself triggers a blocking rule
- A model can be pickle-based AND safe (no malicious payloads) but still get BLOCKED by policy

### Safetensors: The Safe Alternative

Safetensors (developed by HuggingFace) is designed to be safe by construction:

- Only stores model weights (tensors) and a single JSON metadata object
- Does NOT allow arbitrary code serialization
- Cannot execute code during deserialization
- Is the recommended format for all new models

**AIRS scanning behavior for safetensors:**
- Safetensors models pass the deserialization/format rules
- However, safetensors models are NOT immune to all threats:
  - The metadata JSON can be exploited via Hydra's `instantiate()` function
  - Config files alongside safetensors (config.json) can contain malicious `_target_` values
  - Unit 42 found CVEs in libraries that process safetensors metadata (Uni2TS: CVE-2026-22584, FlexTok)

### Other Format Considerations

| Format | Risk Level | Notes |
|---|---|---|
| PyTorch (.pt, .bin) | HIGH | Pickle-based, inherent code execution risk |
| TensorFlow SavedModel | MEDIUM | Can contain arbitrary Python ops |
| ONNX | LOW | Protocol buffer format, no code execution |
| Safetensors | LOW | Tensors only, but metadata can be exploited |
| NeMo (.nemo) | HIGH | TAR archive with YAML config, exploitable via Hydra (CVE-2025-23304) |
| GGUF | MEDIUM | May be flagged as "unapproved format" by strict profiles |
| Keras (.h5) | MEDIUM | HDF5 format, limited execution risk |

### Why Default Groups Often Block on Pickle Models

Based on observed behavior (1/7 rules failing on Default GCS group), the explanation is:

1. Default security groups have a rule checking for **insecure serialization formats** (pickle) with `Blocking: On`
2. Since most models (including Qwen2.5 LoRA adapters) use pickle-based PyTorch format, this rule commonly triggers
3. The verdict is BLOCKED (policy violation) — the model is not malicious, just uses an insecure format
4. The `warn` group (all blocking OFF) returns ALLOWED for the same model with the same `rules_failed` count

---

## 4. Security Groups

### Architecture

Security Groups are the organizational unit for scan policies. Each group:
- Has a **Source Type** (Local, Object Storage, HuggingFace)
- Contains a set of **enabled/disabled rules**
- Has a **threshold** for aggregate evaluation
- Is identified by a **UUID**

### Source Type Matching (Critical Rule)

**The security group source type MUST match the model source.**

| Source Type | Use For | Example |
|---|---|---|
| **Local** | Models on local filesystem | `/path/to/model/` |
| **Object Storage** (GCS/S3/Azure) | Models in cloud storage | `gs://bucket/model/` or `s3://bucket/model/` |
| **HuggingFace** | Models on HuggingFace Hub | `https://huggingface.co/org/model` |

You CANNOT use a HuggingFace security group to scan a local model, and vice versa.

### Security Group UUIDs (Template)

The `scan_model.py` SECURITY_GROUPS dict ships with placeholder UUIDs (`00000000-...`). Each student must discover their own tenant's UUIDs in SCM → AI Model Security → Security Groups (Module 4.2).

Every SCM tenant comes with pre-created default security groups — one per source type:

| Key | Placeholder UUID | Name | Source Type | Purpose |
|---|---|---|---|---|
| `local` | `00000000-...-000001` | Default LOCAL | LOCAL | Scanning local model files |
| `gcs-default` | `00000000-...-000002` | Default GCS | GCS | Scanning models in GCS buckets |
| `hf` | `00000000-...-000003` | Default HUGGING_FACE | HF | Scanning HuggingFace models |
| `warn` | `00000000-...-000004` | Custom (warn-only) | GCS | All rules set to alert, no blocking |
| `block` | `00000000-...-000005` | Custom (blocking) | GCS | All rules set to block |

Students can either pass UUIDs directly via `--security-group <uuid>` or edit the dict in `scan_model.py`. Auto-detection will fail with a helpful error if placeholder UUIDs are still in place.

### Object Storage Scanning Nuance

For GCS/S3/Azure models, AIRS requires **both** `model_path` (local downloaded copy) and `model_uri` (original cloud location):

```bash
model-security scan \
  --security-group-uuid "00000000-0000-0000-0000-000000000002" \
  --model-path "/tmp/downloaded-model/" \
  --model-uri "gs://your-model-bucket/raw-models/clean-advisor" \
  --model-name "clean-advisor"
```

This means the model must be downloaded locally first, then scanned with the GCS security group while providing the original URI for provenance tracking.

### GCS Access Limitations

From project experience: The AIRS GCS security group has limited access. Timestamped training output paths may fail because the security service cannot access all GCS paths. The `gs://your-model-bucket/raw-models/clean-advisor` path has been confirmed to work.

### Customizing Security Groups

Via Strata Cloud Manager (SCM):
1. Navigate to AI Security > AI Model Security > Model Security Groups
2. Create a Group with the appropriate Source Type
3. Enable/disable individual security rules
4. Configure rules as Block or Alert
5. Set severity thresholds

---

## 5. Known Malicious Models on HuggingFace

### Real-World Examples Discovered (2024-2025)

#### JFrog Discovery: ~100 Malicious Models (2024)
- Found approximately 100 models on HuggingFace with malicious payloads
- Notable example: **baller423/goober2** - PyTorch model with payload injected via pickle's `__reduce__` method
- Payload established reverse shells for remote code execution

#### ReversingLabs "NullifAI" Technique (February 2025)
- Found 2 models evading HuggingFace's existing security scanning
- Used PyTorch format but zipped with 7z instead of ZIP (bypassed `torch.load()` scanning)
- Payload created reverse shells connecting to hardcoded IP addresses
- Checked OS type (Windows/Linux/macOS) for platform-specific exploitation
- Models went unnoticed for 8+ months before detection

#### JFrog: Three Zero-Day PickleScan Vulnerabilities (June 2025)
- Discovered 3 zero-day bypasses in PickleScan (industry-standard scanner)
- **CRC Error Bypass**: Intentional CRC errors in ZIP archives cause PickleScan to fail but PyTorch still loads
- **Subclass Bypass**: Using subclasses of dangerous imports instead of exact module names
- **Blacklist Bypass**: `Bdb.run` instead of `exec`, asyncio gadgets
- Fixed in PickleScan v0.0.31 (September 2025)

#### Unit 42: Metadata-Based RCE (2025)
- **NVIDIA NeMo** (CVE-2025-23304): 700+ HuggingFace models affected, including NVIDIA's `parakeet` model
- **Salesforce Uni2TS** (CVE-2026-22584): Morai foundation model with hundreds of thousands of downloads
- **Apple ml-flextok**: Research models from EPFL VILAB
- Attack vector: Hydra's `instantiate()` function via malicious `_target_` values in metadata

### Scale of the Problem

As of April 2025 (Protect AI + HuggingFace partnership):
- **4.47 million** unique model versions scanned
- **1.41 million** repositories evaluated
- **352,000** unsafe/suspicious issues found
- **51,700** models flagged
- **80%+** of models use pickle-based serialization

### Well-Known Models with Pickle Issues

Most standard HuggingFace models use pickle by default. Even popular, legitimate models like:
- `distilbert-base-uncased` (PyTorch .bin files are pickle)
- `bert-base-uncased`
- Most PyTorch-based models pre-safetensors conversion

These are NOT malicious but would trigger format-based rules in AIRS security groups with blocking enabled.

---

## 6. CI/CD Best Practices

### Pipeline Architecture

```
Gate 1: Pre-Training Scan
  - Scan base model BEFORE training
  - Catches known-malicious base models
  - Use HuggingFace security group for HF models

Gate 2: Post-Training Scan
  - Scan trained/fine-tuned model artifacts
  - Catches any corruption or injection during training
  - Use LOCAL or GCS security group

Gate 3: Pre-Deployment Scan
  - Final scan before production deployment
  - Last line of defense
  - Match security group to deployment source
```

### Verdict Handling Strategy

> **CORRECTED (2026-02-05):** Removed hallucinated `MALICIOUS`, `FAIL`, `WARNING`, `PASS` values.

```python
# Recommended exit code logic — only 4 verdicts exist
if verdict == "ERROR":
    sys.exit(1)
elif verdict == "BLOCKED":
    if args.warn_only:
        sys.exit(0)  # Policy violation, not malicious — warn and continue
    else:
        sys.exit(1)
elif verdict == "ALLOWED":
    sys.exit(0)
else:
    # PENDING or unexpected — treat as error
    sys.exit(1)
```

### Environment Variables Required

```bash
# Authentication
MODEL_SECURITY_CLIENT_ID=<service-account-id>
MODEL_SECURITY_CLIENT_SECRET=<service-account-secret>
TSG_ID=<tenant-service-group-id>

# API Endpoint
MODEL_SECURITY_API_ENDPOINT=https://api.sase.paloaltonetworks.com/aims
```

### GitHub Actions Integration Pattern

```yaml
- name: Scan Model with AIRS
  env:
    MODEL_SECURITY_CLIENT_ID: ${{ secrets.MODEL_SECURITY_CLIENT_ID }}
    MODEL_SECURITY_CLIENT_SECRET: ${{ secrets.MODEL_SECURITY_CLIENT_SECRET }}
    TSG_ID: ${{ secrets.TSG_ID }}
  run: |
    # Security group auto-detected from model path source type.
    # Override with --security-group UUID or shorthand key if needed.
    python airs/scan_model.py \
      --model-path "$MODEL_PATH" \
      --warn-only \
      --output-json scan-report.json

- name: Parse Scan Results
  run: |
    VERDICT=$(python -c "
    import json
    with open('scan-report.json') as f:
        data = json.load(f)
    v = str(data.get('eval_outcome', 'UNKNOWN'))
    print(v.split('.')[-1].upper())
    ")
    SCAN_UUID=$(python -c "
    import json
    with open('scan-report.json') as f:
        data = json.load(f)
    print(data.get('uuid', 'unknown'))
    ")
    echo "verdict=$VERDICT" >> $GITHUB_OUTPUT
    echo "scan_uuid=$SCAN_UUID" >> $GITHUB_OUTPUT
```

### SDK Selection

Two SDK packages exist:

1. **`model-security-client`** (Official/recommended)
   - Install: `pip install "model-security-client[all]"` (with extra-index-url)
   - Client: `ModelSecurityAPIClient(base_url=...)`
   - Method: `client.scan(security_group_uuid=..., model_path=..., model_uri=...)`

2. **`pan_modelsecurity`** (Alternative/community)
   - Uses `Scanner()` and `AiProfile(profile_name=...)`
   - Method: `scanner.sync_scan(ai_profile=..., model_uri=...)`

The project currently uses `model-security-client`, which is the correct choice.

### Report Preservation

Always save scan reports as CI/CD artifacts:

```yaml
- name: Upload Scan Report
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: airs-scan-report
    path: scan-report.json
```

---

## 7. Strategic Analysis

### Second-Order Effects

1. **The pickle problem is systemic**: 80%+ of HuggingFace models are pickle-based. Default security groups with blocking rules will flag these. Organizations must decide between strict policy (block all pickle) and pragmatic policy (alert on pickle via warning-only groups).

2. **Safetensors is necessary but not sufficient**: While safetensors prevents pickle-based attacks, the Unit 42 research shows that metadata-based attacks (via Hydra, config files) create NEW attack surfaces even in "safe" formats. The attack surface is shifting from serialization to configuration.

3. **Scanner evasion is an active arms race**: JFrog found 3 zero-day bypasses in PickleScan in 2025. AIRS has its own scanning engine (not PickleScan), but the same principles apply - attackers will find bypasses. Defense in depth (multiple scan gates, runtime monitoring) is essential.

4. **The BLOCKED vs ALLOWED distinction is operationally critical**: Many teams initially set up pipelines that hard-fail on BLOCKED, causing false-positive pipeline failures. The correct pattern is: ERROR = hard stop, BLOCKED = warning + configurable gate (use `--warn-only`), ALLOWED = proceed.

### Three Moves Ahead

1. **Model format migration**: The industry is moving toward safetensors as default. PyTorch 2.x already defaults to weights-only loading. Within 12-18 months, pickle-based models will increasingly be treated as legacy/suspicious by default.

2. **Supply chain attestation**: Expect AIRS and similar tools to add model signing and provenance verification (similar to software SBOMs). The Protect AI acquisition positions Palo Alto to lead here.

3. **Runtime protection convergence**: Model scanning (pre-deployment) and runtime monitoring (post-deployment) are converging. AIRS already has both capabilities. The future is continuous scanning, not just gate-based scanning.

---

## Sources

- [Palo Alto Networks - How to Integrate Prisma AIRS Model Scanning in CI/CD Pipeline](https://live.paloaltonetworks.com/t5/community-blogs/how-to-integrate-prisma-airs-model-scanning-in-ci-cd-pipeline/ba-p/1244238)
- [Palo Alto Networks - AIRS Python SDK (GitHub)](https://github.com/PaloAltoNetworks/aisecurity-python-sdk)
- [Palo Alto Networks - Prisma AIRS Documentation](https://docs.paloaltonetworks.com/ai-runtime-security)
- [Palo Alto Networks - Understanding Model Security Rules](https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/understanding-ai-model-security-rules)
- [Palo Alto Networks - Customizing Security Groups](https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/get-started-with-ai-model-security/customizing-security-groups)
- [Palo Alto Networks - Scanning Models](https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/get-started-with-ai-model-security/scanning-models)
- [Palo Alto Networks - Supported Model Formats](https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/supported-model-formats)
- [Unit 42 - Remote Code Execution With Modern AI/ML Formats and Libraries](https://unit42.paloaltonetworks.com/rce-vulnerabilities-in-ai-python-libraries/)
- [Palo Alto Networks - Prisma AIRS 2.0 Blog](https://www.paloaltonetworks.com/blog/2025/11/ai-black-box-problem-prisma-airs-2-0/)
- [ReversingLabs - Malicious ML Models on Hugging Face (NullifAI)](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face)
- [The Hacker News - Malicious ML Models Leverage Broken Pickle Format](https://thehackernews.com/2025/02/malicious-ml-models-found-on-hugging.html)
- [JFrog - Zero-Day PickleScan Vulnerabilities](https://jfrog.com/blog/unveiling-3-zero-day-vulnerabilities-in-picklescan/)
- [JFrog - Data Scientists Targeted by Malicious HuggingFace Models](https://jfrog.com/blog/data-scientists-targeted-by-malicious-hugging-face-ml-models-with-silent-backdoor/)
- [Dark Reading - Hugging Face AI Platform Riddled With 100 Malicious Models](https://www.darkreading.com/application-security/hugging-face-ai-platform-100-malicious-code-execution-models)
- [HuggingFace - Pickle Scanning Documentation](https://huggingface.co/docs/hub/en/security-pickle)
- [HuggingFace - Protect AI 4M Models Scanned](https://huggingface.co/blog/pai-6-month)
- [Splunk - Paws in the Pickle Jar](https://www.splunk.com/en_us/blog/security/paws-in-the-pickle-jar-risk-vulnerability-in-the-model-sharing-ecosystem.html)
