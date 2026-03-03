# Module 5 Flow: Integrate AIRS into Pipeline

> INTERNAL PLAYBOOK — never shown to students.
> Engagement points tracked during module. All other scoring happens during /lab:verify-5.

## Points Available

| Source | Points | When |
|--------|--------|------|
| Engage: Non-zero exit code (5.1) | 1 | During flow |
| Engage: SDK gap discussion (5.4) | 1 | During flow |
| Technical: Gate 2 scan added | 2 | During verify |
| Technical: Gate 3 manifest verification | 2 | During verify |
| Technical: Successful pipeline run | 2 | During verify |
| Technical: Scan labels in SCM | 2 | During verify |
| Technical: Evaluation summary in GH Actions | 2 | During verify |
| Quiz Q1: Scan failure flow | 3 | During verify |
| **Total** | **15** | |

---

## Challenge 5.0: Fix the Qwen Policy (Setup for Pipeline Integration)

### Learning Objectives

The student should be able to:
- Make an informed policy decision about governance rules
- Modify security group rules in SCM
- Re-scan to verify the change, understanding that detection and enforcement are independent

### Key Concepts

1. **The Policy Decision**
   - Core idea: In Module 4, the student discovered that Qwen is BLOCKED by default HF governance rules (license type `"other"` not approved, org not HF-verified). Before integrating AIRS into the pipeline, these rules need to be addressed — otherwise the pipeline will fail on every scan of the base model.
   - This is a real enterprise decision. In the lab, change the rules. In production, security/legal/compliance would weigh in.
   - Two options: add `other` to approved licenses + add Qwen to approved orgs, OR change both rules from blocking to non-blocking (alert-only). Recommend non-blocking — detections still appear in reports but don't block the pipeline.
   - Show: Navigate to Default HUGGING_FACE security group in SCM. Modify the two failing rules.
   - Check: Can the student explain the difference between disabling a rule and setting it to non-blocking?

2. **Re-scan and Verify**
   - Re-scan Qwen with the same HF security group UUID.
   - Expected: `eval_outcome: ALLOWED` but `rules_failed: 2` — same detection, different enforcement.
   - This is the key value prop: **same detection, configurable enforcement.**
   - Check: Does the student understand the enterprise pattern: dev=alert, prod=block?

---

## Challenge 5.1: Add Scanning to Gate 2

### Flow

**What to modify:** `.github/workflows/gate-2-publish.yaml`

**Where the scan goes:** After the merge step completes (the merged model exists in GCS staging) and before the publish step copies artifacts to the approved location.

**Decisions to make:**
- Which security group should Gate 2 use? (blocking vs warning)
- Should the scan use `--warn-only` or strict mode?
- What happens to the pipeline when the scan fails?

> **ENGAGE**: "A non-zero exit code from scan_model.py stops the workflow. Why is that the right behavior for Gate 2?"
> Award 1 pt for meaningful engagement. No wrong answers — teach if needed.
> (Answer: If the scan fails/blocks, the compromised model never reaches the production registry. The publish step never runs.)

### Hints

**Hint 1 (Concept):** Look at how Gate 1 already handles scanning. The pattern is the same: call `airs/scan_model.py` with the model path, security group UUID, and check the exit code.

**Hint 2 (Approach):** The scan step needs: AIRS credentials (from GitHub secrets), the model path in GCS, and the security group UUID. Exit code 0 = ALLOWED, exit code 1 = BLOCKED or ERROR.

**Hint 3 (Specific):** In GitHub Actions, a non-zero exit code causes the job to fail by default. This is the desired behavior — blocked model never reaches production registry.

---

## Challenge 5.2: Add Manifest Verification to Gate 3

### Flow

**What to modify:** `.github/workflows/gate-3-deploy.yaml`

**The verification tool:** `scripts/manifest.py verify --require-scan gate2`

**What to test:**
1. Trigger Gate 3 with a model that has a valid Gate 2 scan in its manifest — should succeed
2. Trigger Gate 3 with a model that has no Gate 2 scan — should fail
3. Understand the `skip_manifest_check` emergency override

### Hints

**Hint 1 (Concept):** The manifest tracks lineage, scan records, and deployment history. Each gate adds its own records. Gate 3 reads the manifest and checks for required entries.

**Hint 2 (Approach):** Run `python scripts/manifest.py show --manifest manifest.json` to see what a manifest looks like. The `verify` subcommand checks for required scan entries.

**Hint 3 (Specific):** Add a verification step early in Gate 3, before deployment. Download manifest from GCS, run verify, proceed only if it passes.

---

## Challenge 5.3: Label Your Scans

### Flow

**Minimum labels to include:**

| Label Key | Value | Purpose |
|-----------|-------|---------|
| `gate` | gate1, gate2, gate3 | Which pipeline stage |
| `run_id` | `$GITHUB_RUN_ID` | Link scan to pipeline execution |
| `model_version` | v2.0.0 or similar | Which version |
| `environment` | staging, production | Deployment target |
| `base_model` | Qwen/Qwen2.5-3B | Training provenance |

### Hints

**Hint 1 (Concept):** Check the AIRS SDK docs and release notes for label support.

**Hint 2 (Approach):** GitHub Actions provides env vars: `$GITHUB_RUN_ID`, `$GITHUB_SHA`, `$GITHUB_REF_NAME`. These create a direct link from SCM scans back to pipeline runs.

**Hint 3 (Specific):** Labels connect scans to business context. Version labels (`model_version`, `dataset_version`) make compliance queries possible.

---

## Challenge 5.4: Enrich Scan Output for Developers

### Flow

**What the SDK gives you today:**
- `eval_outcome`, `eval_summary`, `uuid`, labels

**What the SDK does NOT give you:** Per-rule evaluation details (only available in SCM). This is a real product gap.

> **ENGAGE**: "Per-rule details require SCM access — developers can't see them in CI/CD. How would you frame this limitation to a customer?"
> Award 1 pt for meaningful engagement. No wrong answers — teach if needed.
> (Answer: Feature request conversation — bridge the gap with what's available now, flag for product team.)

**What to build:**
1. Modify `scan_model.py` to output structured JSON
2. Add a GitHub Actions step writing a formatted summary to `$GITHUB_STEP_SUMMARY`
3. Include: verdict badge, rule summary, scan UUID, labels, SCM link

### Hints

**Hint 1 (Concept):** `scan_model.py` has `--output-json` which saves full scan response. Use this in workflow, then build summary in a subsequent step.

**Hint 2 (Approach):** Write rich markdown to `$GITHUB_STEP_SUMMARY` for visible scan results on the workflow run page.

**Hint 3 (Specific):** The honest framing for customers: aggregate counts available in CI/CD, per-rule details require SCM. Here's how to bridge that gap now, and here's the feature request.
