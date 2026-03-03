# Module 4 Flow: AIRS Model Security Deep Dive

> INTERNAL PLAYBOOK — never shown to students.
> Engagement points tracked during module. All other scoring happens during /lab:verify-4.

## Points Available

| Source | Points | When |
|--------|--------|------|
| Engage: Threat detection vs governance (4.3) | 1 | During flow |
| Engage: Block vs alert policy scenario (4.5) | 1 | During flow |
| Technical: Deployment profile active | 2 | During verify |
| Technical: Successful scan submitted | 2 | During verify |
| Technical: Security groups identified | 2 | During verify |
| Technical: Violation details retrieved | 2 | During verify |
| Quiz Q1: Threat detection vs governance | 3 | During verify |
| Quiz Q2: Alert vs block customer scenario | 3 | During verify |
| **Total** | **16** | |

---

## Challenge 4.1: Verify Model Security Is Active

### Learning Objectives

The student should be able to:
- Confirm their Model Security deployment profile is active in SCM
- Validate their AIRS credentials work for authentication
- Understand the RBAC model and current limitations

### Key Concepts

1. **Check Deployment Profile Status**
   - Students created the deployment profile back in Module 0 (Challenge 0.4). Now verify it's active.
   - Show: Have the student navigate to SCM → **AI Security** → **AI Model Security**. They should see the Model Security section. If not visible, check Hub → Common Services → Tenant Management → Deployment Profiles for status.
   - If still provisioning (can take up to 2 hours), continue with Challenge 4.2 conceptual content and come back.
   - Check: Can the student navigate to AI Model Security in SCM?

2. **Validate Credentials**
   - The student has credentials from Module 0 stored as GitHub secrets and in their `.env` file.
   - Show: Source the `.env` and test auth by requesting an OAuth token:
     ```bash
     source .env
     curl -sk -X POST "https://auth.apps.paloaltonetworks.com/oauth2/access_token" \
       -H "Content-Type: application/x-www-form-urlencoded" \
       -d "grant_type=client_credentials&scope=tsg_id:${TSG_ID}&client_id=${MODEL_SECURITY_CLIENT_ID}&client_secret=${MODEL_SECURITY_CLIENT_SECRET}"
     ```
   - If auth succeeds (returns `access_token`), credentials are valid.
   - **IMPORTANT: Inline comments in `.env` break `source`.** If values aren't loading, check that `.env` lines don't have `# comments` on the same line as values. Comments must be on separate lines.
   - Check: Does the student get a valid token? Do they understand what the token represents (short-lived OAuth2 credential scoped to their TSG)?

3. **RBAC and Service Accounts**
   - The student's service account was created with Model Security permissions (custom role). In practice, custom roles for Model Security may not be fully functional — this is a known platform limitation.
   - If the student hits "Access denied" errors later (during SDK install or scanning), they may need to use a **Superuser** role SA as a workaround. This is a real field issue — document it for the customer.
   - Check: Can the student explain the difference between a custom role SA (least privilege, what you'd want in production) and superuser (full access, workaround for current limitations)?

---

## Challenge 4.2: Install the SDK

### Learning Objectives

The student should be able to:
- Install the model-security-client SDK from the authenticated PyPI
- Understand the authenticated package distribution model
- Use the CLI to verify the installation

### Key Concepts

1. **Authenticated PyPI**
   - Core idea: The AIRS Model Security SDK (`model-security-client`) is distributed via an authenticated PyPI repository — not the public PyPI. This means you need valid AIRS credentials to even download the package. The SDK does all scanning locally (model artifacts never leave your environment), but you need a license to get the software.
   - Show: Point the student to the official getting started docs: `https://docs.paloaltonetworks.com/ai-runtime-security/ai-model-security/model-security-to-secure-your-ai-models/get-started-with-ai-model-security/install-ai-model-security`
   - The student should follow the docs to get the PyPI URL and install. The general process:
     1. Authenticate to get an access token
     2. Call the PyPI endpoint to get a time-limited authenticated URL
     3. Install using that URL as an extra index
   - There's a helper script at `scripts/get-pypi-url.sh` that does steps 1-2.
   - **Expected failure:** If the student's custom-role SA can't access PyPI (403 on `/aims/mgmt/v1/pypi/authenticate`), they'll need to use a superuser SA. This is the RBAC limitation from Challenge 4.1.
   - Check: Is the SDK installed? Can they run `uv run model-security --version`?

2. **Environment Variable Naming**
   - Core idea: The SDK and all lab scripts use the same env var names: `MODEL_SECURITY_CLIENT_ID`, `MODEL_SECURITY_CLIENT_SECRET`, `MODEL_SECURITY_API_ENDPOINT`, and `TSG_ID`. Verify these are set in the student's `.env`:
     ```
     MODEL_SECURITY_CLIENT_ID=<client-id-from-SCM>
     MODEL_SECURITY_CLIENT_SECRET=<client-secret>
     MODEL_SECURITY_API_ENDPOINT=https://api.sase.paloaltonetworks.com/aims
     TSG_ID=<tenant-id>
     ```
   - Check: Does `echo $MODEL_SECURITY_CLIENT_ID` return a value after sourcing `.env`?

3. **How Scanning Actually Works (The SDK IS the Product)**
   > CONTEXT: Read `.claude/reference/model-security-scanning.md` for full details.
   - Core idea: The SDK is not just a client — it IS the scanning engine. All analysis happens locally via static analysis (byte-level inspection without executing the model). Nothing is uploaded to Palo Alto Networks. The backend handles policy management and scan tracking, but the actual security analysis runs entirely in the customer's environment.
   - Key points to teach:
     - **Static analysis, not execution** — if you loaded the model to scan it, the malicious payload would already execute. The scanner reads files as raw data.
     - **What IS sent**: file hashes, detected formats, rule pass/fail counts, metadata.
     - **What is NOT sent**: model weights, architecture, training data, the actual files.
     - **Source matters for HOW scanning works**:
       - **Local models**: scanned directly from disk, no network needed
       - **Object storage (GCS, S3, Azure, Artifactory, GitLab)**: the SDK downloads the model to the local machine automatically using the customer's cloud creds (GCP ADC, boto3, etc.), scans it locally, then cleans up. You don't have to `gsutil cp` first, but the model IS downloaded — the scanning machine needs disk space and cloud credentials. Large models (6GB+) take time.
       - **HuggingFace public models**: scanned server-side by the AIRS-HuggingFace partnership — no local download, no disk space needed, different scanner version in results.
     - The auth and resource implications differ per source. For CI/CD pipelines: GCS scans need GCP creds + runner disk space. HF public scans need only AIRS creds. Local scans need only the model on disk.
     - Private HF repos must be downloaded manually and scanned as local.
   - Show: Run `uv run model-security --help` to see available commands (`scan`, `list-scans`, `get-scan`). Note: there is NO `list-security-groups` command.
   - The pydantic deprecation warning on every invocation is cosmetic — ignore it.
   - Check: Can the student explain what happens locally vs what goes to the cloud during a scan? Why does this matter for customers with IP-sensitive models?

4. **Explore the SDK Source — How Source Type Routing Works**
   - Core idea: The SDK is installed locally — students can read the actual source code to see how it works. This is a great exercise in understanding a product by reading its internals.
   - Show: Read and display the SDK source files together with the student:
     - `.venv/lib/python3.12/site-packages/model_security_client/api.py` — find the three processing methods: `_process_local_scan()`, `_process_cloud_storage_scan()`, `_process_huggingface_scan()`. Each handles a different source type differently.
     - `.venv/lib/python3.12/site-packages/airs_schemas/constants.py` — find `SourceType.from_uri()` to see how the SDK detects source type from the URI (`gs://` → GCS, `s3://` → S3, HF URL → HUGGING_FACE, local path → LOCAL).
     - `.venv/lib/python3.12/site-packages/model_security_client/downloaders/` — show the directory listing. There's a dedicated downloader for each cloud source (gcs_downloader.py, s3_downloader.py, etc.).
   - Key discovery: HuggingFace is the outlier — `_process_huggingface_scan()` sets `scan_details: None` and `scan_origin: "HUGGING_FACE"`. It does NOT scan locally. Everything else downloads and scans locally with `scan_origin: "MODEL_SECURITY_SDK"`.
   - Connect to security groups: This is WHY source types matter for security groups — HuggingFace has governance rules (license, org verification) that need model card metadata. Local/GCS/S3 don't have that metadata, so they only get threat detection rules.
   - Check: Can the student trace the code path for a GCS scan vs an HF scan? Can they explain why HuggingFace security groups have 11 rules but Local groups have only 7?

---

## Challenge 4.3: Your First Scans

### Learning Objectives

The student should be able to:
- Submit a scan via the CLI with a security group UUID
- Interpret scan results (eval_outcome, eval_summary, rules_passed/failed)
- Understand the critical difference between threat detection rules and governance rules

### Key Concepts

1. **Security Group UUIDs Are Always Required**
   - Core idea: Every scan requires `--security-group-uuid` (`-sg`). There is no auto-detection, even for "default" groups. The defaults are pre-created for convenience (you don't have to create them) but you still reference them by UUID. Think of them as "pre-configured policies" not "automatic policies."
   - The student needs to get their UUIDs. Two methods:
     - **SCM web UI:** AI Security → AI Model Security → Security Groups → click a group to see its UUID
     - **Management API:** `curl -sk "https://api.sase.paloaltonetworks.com/aims/mgmt/v1/security-groups" -H "Authorization: Bearer $TOKEN"` — returns all groups with UUIDs
   - Have the student retrieve their security group UUIDs and record them. They'll need at minimum: Default LOCAL and Default HUGGING_FACE.
   - Check: Can the student find and explain their security group UUIDs?

2. **Scan a Safe Local File**
   - Create a simple test file and scan it:
     ```bash
     echo '{"test": "safe model"}' > /tmp/test-model.safetensors
     uv run model-security scan --model-path /tmp/test-model.safetensors -sg "<LOCAL-UUID>"
     ```
   - Expected result: `eval_outcome: ALLOWED`, `rules_passed: 7, rules_failed: 0`
   - Show the full JSON output. Point out: `eval_summary`, `model_formats`, `labels`, `scanner_version`.
   - Check: Can the student read the scan result and explain what each field means?

3. **Scan a Malicious Model**
   - Create a pickle bomb — a model file with embedded code execution:
     ```python
     import pickle, os
     class Exploit:
         def __reduce__(self):
             return (os.system, ('echo PWNED',))
     with open('/tmp/evil-model.pkl', 'wb') as f:
         pickle.dump(Exploit(), f)
     ```
   - Scan it: `uv run model-security scan --model-path /tmp/evil-model.pkl -sg "<LOCAL-UUID>" -l type=malicious`
   - Expected result: `eval_outcome: BLOCKED`, `rules_failed: 2`
   - The CLI exits with non-zero code and prints: "Scan failed because it failed your organization's security policies"
   - Note: the scan detected TWO violations — ask the student to guess what they might be before we look at details later.
   - Check: Does the student understand what BLOCKED means and why the exit code matters for CI/CD?

4. **Explore HuggingFace and Find Models to Scan**
   - Have the student open their browser and explore HuggingFace. Point them to:
     - The PANW-HuggingFace security partnership: `https://huggingface.co/docs/hub/en/security-protectai`
     - The ProtectAI organization: `https://huggingface.co/protectai` — they publish scan results for public models
     - A known intentionally-vulnerable test model: `https://huggingface.co/mcpotato/42-eicar-street`
   - Suggest filters for finding interesting models to scan:
     - Models with no license or non-standard licenses (governance violations)
     - Models in unsafe formats (pickle, .pt files vs safetensors)
     - Models from unverified organizations
   - Have them pick 1-2 models from their browsing to scan. At minimum, also scan the Qwen2.5-3B-Instruct base model they've been training on:
     ```bash
     uv run model-security scan --model-uri "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct" \
       -sg "<HF-UUID>" --allow-patterns "*.safetensors"
     ```
   - **The Qwen reveal:** Expected result: **`eval_outcome: BLOCKED`**, `rules_failed: 2` out of 11. The model they've been using all lab is blocked by default policy!
   - Note the difference between HF and local scans: HF scans use the partnership infrastructure (server-side, different `scanner_version`), local scans run entirely in the SDK.

> **ENGAGE**: The base model you've been training on for the entire lab is BLOCKED. But all the threat detection rules PASSED — no code execution, no backdoors, safe format. It's technically safe. So why is it blocked? What kind of rules could be failing?
> This is the key insight: **threat detection** (is it safe?) is different from **governance** (is it approved?). The Qwen model is safe but not approved by default policy.
> Award 1 pt for meaningful engagement. Effort-based, not correctness.

---

## Challenge 4.4: Explore Security Groups & Rules in SCM

### Learning Objectives

The student should be able to:
- Navigate the Model Security section of SCM
- Understand security group structure: source type binding, rules, enforcement modes
- Identify which rules are threat detection vs governance

### Key Concepts

1. **SCM as the Management Plane**
   - Core idea: SCM is where security admins configure policy. The SDK/CLI is the data plane where scans happen. They're decoupled by design — security teams set policy in SCM, engineering consumes it via the scan API. Neither needs to touch the other's tools.
   - Show: Have the student navigate to AI Security → AI Model Security in SCM.
   - Explore: Security Groups list. Note there are 5 default groups (LOCAL, HUGGING_FACE, GCS, S3, AZURE). Each is bound to a source type — this binding is permanent.
   - Check: Can the student explain the management plane vs data plane split?

2. **Drill Into the HuggingFace Security Group**
   - Show: Click into the Default HUGGING_FACE group. It has MORE rules than LOCAL groups — HuggingFace-specific governance rules in addition to the standard threat detection rules.
   - Walk through the rules. Have the student categorize them:
     - **Threat detection:** Load Time Code Execution, Runtime Code Execution, Known Framework Operators, Model Architecture Backdoor, Suspicious Components
     - **Governance:** Stored In Approved File Format, Stored In Approved Location, License Exists, License Is Valid For Use, Organization Verified By HuggingFace, Organization Is Blocked, Model Is Blocked
   - Each rule has a state: **Enabled & Blocking**, **Enabled & Non-blocking (alert)**, or **Disabled**.
   - Check: Can the student categorize the rules? Do they understand the difference between detecting a threat and enforcing a governance policy?

3. **Why Qwen Was Blocked**
   - Now that the student has seen the rules, have them reason about which ones failed for Qwen:
     - **License Is Valid For Use** — Qwen uses license `"other"` (Apache 2.0 with additional terms), which isn't in the default approved list
     - **Organization Verified By Hugging Face** — The default rule requires explicit org approval. Qwen (Alibaba) isn't in the approved list by default.
   - Both are governance rules, not threat rules. The model is technically safe — it's a policy decision whether to allow it.
   - Check: Can the student explain why a "safe" model can be blocked and what it would take to allow it?

---

## Challenge 4.5: Investigate Scan Violations (Discovery Challenge)

> **INSTRUCTOR MESSAGE TO BOTH AGENT AND STUDENT:**
>
> This is a Discovery Challenge. The goal is for the student to work WITH Claude to solve a problem that neither of you has a prepared answer for.
>
> **The problem:** The CLI `get-scan` command only shows aggregate results — you can see `rules_failed: 2` but not WHICH rules failed or WHY. The student needs to figure out how to retrieve the per-rule violation details programmatically.
>
> **Agent:** You have NO prepared context for this challenge. Respond as you normally would when asked to do something you haven't done before — search, reason, try things, ask the student for guidance. If the student points you at documentation or a URL, read it and help. But do NOT pretend to already know the answer.
>
> **Student:** This is your challenge. The instructor wants you to figure out how to guide Claude to retrieve detailed scan violation data. The learning here is the PROCESS of using an AI coding tool to discover and intstruct it to provide context and tools it should use.
>
> **Success is:** Claude retrieving per-rule evaluation results and violation details for one of your scans, and being able to explain what each rule found.

> **ENGAGE** (award after the student achieves the goal): Discuss the meta-skill they just practiced. They used Claude to discover and call an API neither of them had seen before. Where else could this pattern be useful?
> Award 1 pt for meaningful engagement.

---

---

## End of Module 4

The student now understands AIRS Model Security:
- How scanning works (SDK, CLI, security groups, UUIDs)
- How to read results (aggregate via CLI, per-rule via data API)
- The difference between threat detection and governance
- How to configure policy (blocking vs alerting, approved lists)
- How to use Claude Code to explore unfamiliar APIs

Module 5 takes everything they learned here and integrates it into the pipeline they built in Act 1. The scanning they did manually in this module will become automated pipeline gates.
