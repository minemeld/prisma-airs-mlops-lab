# How AI Model Security Scanning Works

> Reference for the lab agent. Use this to explain scanning concepts to students.

## The Core Principle: Static Analysis, Not Execution

Model scanning is **static analysis** — it inspects model files WITHOUT executing their code. This is critical:
- If you loaded the model to scan it, the malicious payload would already execute
- Byte-level inspection reads model files as raw data
- A custom unpickler interprets opcodes without reaching Python's execution state

## Scanning Flow

```
Model File (local/GCS/HF/S3/Azure/Artifactory/GitLab)
    │
    ▼
Format Introspection ─── What type of file is this?
    │
    ▼
Threat Taxonomy Mapping ─── What threats apply to this format?
    │
    ▼
Deep Scan ─── Byte-level analysis for each applicable threat
    │
    ▼
Rule Evaluation ─── Check against security group rules
    │
    ▼
Aggregate Outcome ─── ALLOWED | BLOCKED | ERROR
```

## Key Architecture: Models Stay Local

Models are NOT uploaded to Palo Alto Networks. The scan runs entirely in the customer's environment via the SDK/CLI.

**What IS sent to the AIRS backend:**
- File hashes (SHA-1)
- Detected formats (pickle, safetensors, onnx, etc.)
- Rule pass/fail counts (aggregate summary)
- Scan metadata (timestamp, security group, labels)

**What is NOT sent:**
- Model weights
- Model architecture details
- Training data
- The actual model files

The SDK IS the scanning engine — it contains the detection logic. The backend handles policy management, scan tracking, and the SCM UI.

## Source-Specific Scanning

| Source | Auth Required | How It Works |
|--------|-------------|--------------|
| **Local** | None (filesystem) | SDK reads files directly from disk |
| **HuggingFace** | None for public models | Scanned via AIRS-HuggingFace partnership (server-side, `scan_origin: "HUGGING_FACE"`) |
| **GCS** | Google Application Default Credentials | SDK provides native access — handles credential resolution, download, and cleanup automatically |
| **S3** | boto3 / AWS credentials | SDK provides native access |
| **Azure** | Microsoft Entra ID | SDK provides native access |
| **Artifactory** | `ARTIFACTORY_TOKEN` | SDK provides native access |
| **GitLab** | `GITLAB_TOKEN` | SDK provides native access |

**Key distinctions:**
- **HuggingFace public models** are scanned server-side by the partnership infrastructure — no local download, no disk space, different `scanner_version` in results (`scan_origin: "HUGGING_FACE"`). Private HF repos must be downloaded manually and scanned as local.
- **Object storage models** (GCS, S3, Azure, etc.) — the SDK **downloads the model locally** using the customer's cloud credentials, scans it on the local machine, then optionally cleans up. The SDK automates the download (you don't need to `gsutil cp` first), but the model IS downloaded to `~/.cache/airsms/` and scanned locally (`scan_origin: "MODEL_SECURITY_SDK"`). This means the scanning machine needs: (1) cloud credentials, (2) disk space for the model, (3) network access to the storage.
- The "native access without requiring manual downloads" from release notes means the SDK handles the download lifecycle — it does NOT mean server-side scanning.

**Auth implications for pipelines:** Object storage scans require cloud credentials (GCP ADC, AWS IAM role, etc.) AND sufficient disk space on the CI/CD runner. Large models (6GB+) will take time to download before scanning begins. HuggingFace public scans need only AIRS credentials and have no local resource requirements.

## The Two Types of Rules

### Threat Detection Rules (All Source Types)
These check if the model is technically safe:
- **Load Time Code Execution** — Detects code that runs on `pickle.load()`, `torch.load()`, etc. (e.g., `os.system` in pickle bytecode)
- **Runtime Code Execution** — Detects code that runs during inference (e.g., malicious Keras Lambda layers)
- **Model Architecture Backdoor** — Detects modified neural network layers with hidden trigger behavior
- **Known Framework Operators** — Identifies dangerous TensorFlow/Keras/ONNX operators
- **Suspicious Model Components** — Unusual components that may enable future exploitation
- **Stored In Approved File Format** — Enforces safe formats (safetensors preferred over pickle)
- **Stored In Approved Location** — Validates storage path against approved prefixes

### Governance Rules (HuggingFace Source Type Only)
These check organizational policy:
- **License Exists** — Model has a license in its card
- **License Is Valid For Use** — License type is in the approved list (default: apache-2.0, mit, bsd-3.0)
- **Organization Verified By HuggingFace** — Model org has HF verification badge
- **Organization Is Blocked** — Explicit blocklist for specific orgs
- **Model Is Blocked** — Explicit blocklist for specific models

## Verdict Logic

```
BLOCKED = At least one BLOCKING-enabled rule detected an issue
ALLOWED = No blocking rules failed (can still have alerting-rule failures)
ERROR   = Scan itself failed
PENDING = Scan in progress
```

**Key insight:** `BLOCKED` is a policy decision, not just a threat detection. The same model can be `ALLOWED` or `BLOCKED` depending on which security group scans it and how rules are configured.

## SDK Package

- Package: `model-security-client` (with optional extras: `[gcp]`, `[aws]`, `[azure]`, `[all]`)
- Distributed via authenticated PyPI (requires valid AIRS credentials to download)
- Python 3.11, 3.12, or 3.13
- CLI commands: `model-security scan`, `model-security list-scans`, `model-security get-scan`
- SDK env vars: `MODEL_SECURITY_CLIENT_ID`, `MODEL_SECURITY_CLIENT_SECRET`, `TSG_ID`, `MODEL_SECURITY_API_ENDPOINT`

## SDK Internals: How Source Type Routing Works

The SDK has three distinct code paths based on source type (visible in the SDK source at `model_security_client/api.py`):

**`_process_local_scan()`** — Local files
- Reads files directly from disk
- Runs the scanner locally (`_scan_model()`)
- Submits results with `scan_origin: "MODEL_SECURITY_SDK"` and full `scan_details`

**`_process_cloud_storage_scan()`** — GCS, S3, Azure, Artifactory, GitLab
- Uses source-specific downloaders (`downloaders/gcs_downloader.py`, `s3_downloader.py`, etc.)
- Downloads model to `~/.cache/airsms/{source}/` using customer's cloud credentials
- Scans locally with the same scanner engine as local scans
- Submits results with `scan_origin: "MODEL_SECURITY_SDK"` and full `scan_details`
- Optionally cleans up downloaded files

**`_process_huggingface_scan()`** — HuggingFace public models
- Does NOT download or scan locally
- Sends only the URI, file patterns, and security group UUID to the AIRS backend
- Sets `scan_origin: "HUGGING_FACE"` and `scan_details: None`
- The backend handles the download and scanning server-side
- Results come back with a different `scanner_version` than local scans

Source type detection happens in `airs_schemas/constants.py` via `SourceType.from_uri()`:
- `gs://` → GCS, `s3://` → S3, `az://` → Azure
- `huggingface.co` URLs → HUGGING_FACE
- Everything else (local paths) → LOCAL

### Why Source Types Matter for Security Groups

Source type binding on security groups is NOT about where scanning happens — it's about **what rules can apply**:

| Source | Available Rules | Why |
|--------|----------------|-----|
| LOCAL, GCS, S3, Azure | 7 threat detection rules only | Raw files — no model card, no license metadata, no org info |
| HUGGING_FACE | 11 rules (7 threat + 4 governance) | HF provides metadata: licenses, org verification, model cards |

HuggingFace governance rules (License Exists, License Is Valid, Org Verified, Org Blocked, Model Blocked) require metadata that only HuggingFace provides. You can't scan a GCS file with an HF security group because the governance rules would have no metadata to evaluate.

## API Surfaces

The SDK exposes CLI commands (`scan`, `list-scans`, `get-scan`) and a Python API via `ModelSecurityAPIClient`. The SDK's `get-scan` only returns aggregate summary (rules_passed/failed counts), NOT per-rule details.

Per-rule evaluation details (which rules passed/failed, violation descriptions, remediation steps) are available through other means — students discover these in the lab's Discovery Challenge (Module 4.5).

## Supported Model Formats (52+)

Includes: SafeTensors, Pickle, PyTorch, TensorFlow (SavedModel, Lite, Hub), Keras, ONNX, GGUF, NeMo, Llamafile, LightGBM, SKLearn, JAX/Flax, OpenVINO, TensorRT, NumPy, and many more including compressed archives (ZIP, TAR, 7z).

## Threat Intelligence: Insights DB

- Powered by 16,000+ security researchers (Huntr community)
- Scans every public HuggingFace model
- Classifications: Safe, Unsafe, Suspicious
- Public at: https://protectai.com/insights
- Vulnerability warnings avg 30 days before NVD via Sightline (https://sightline.protectai.com/)
