# Module 2 Flow: Train Your Model

> INTERNAL PLAYBOOK — never shown to students.
> Engagement points tracked during module. All other scoring happens during /lab:verify-2.

## Points Available

| Source | Points | When |
|--------|--------|------|
| Engage: skip_scan design (2.1) | 1 | During flow |
| Engage: LoRA merge rationale (2.3) | 1 | During flow |
| Technical: Training output in GCS | 2 | During verify |
| Quiz Q1: LoRA vs merged model | 3 | During verify |
| Quiz Q2: extra_special_tokens | 3 | During verify |
| **Total** | **10** | |

---

## Challenge 2.1: Understand Before You Run

### Flow

You would not deploy infrastructure you do not understand. The same rule applies to ML pipelines. Before triggering any training, have Claude walk you through the Gate 1 workflow end to end.

Use `/explore training-pipeline` in Claude Code for guided exploration.

Study `gate-1-train.yaml` and `train_advisor.py`. You should be able to answer:

- What triggers the workflow? What inputs can you customize?
- How does the training script get to the Vertex AI worker? (Hint: GCS FUSE)
- What base model does it start from? What dataset does it train on?
- What is the LoRA configuration? How many parameters does it add?
- Where do the trained artifacts end up?

**About the scan step:** The workflow has a scan job (`gate1-scan-base-model`) that can scan the base model before training. Notice it also has a `skip_scan` input. For Modules 2-3, we're skipping the scan — our focus is understanding the pipeline mechanics first. You'll configure AIRS scanning in Module 4 and add it to the pipeline in Module 5. Point out the scan step to the student so they know it exists, but don't run it yet.

> **ENGAGE**: "The workflow has a `skip_scan` input that lets you bypass the security scan. Why would you design a pipeline with a security step that can be skipped?"
> Award 1 pt for meaningful engagement. No wrong answers — teach if needed.
> (Answer: Incremental adoption — you don't want security tooling to block the entire pipeline before it's configured. Also useful for pre-approved models, emergency hotfixes, or when scanning infrastructure isn't ready yet. In production, you'd restrict who can set skip_scan via branch protection or required reviewers.)

### Hints

**Hint 1 (Concept):** Gate 1 has two phases: an optional security scan of the base model (skipped for now), and a Vertex AI CustomJob that runs the training script on a GPU. The training script uses the PEFT library for LoRA fine-tuning -- it freezes the base model weights and trains a small adapter on top.

**Hint 2 (Approach):** Read `.github/workflows/gate-1-train.yaml` top to bottom. Trace the data flow: inputs at the top define what gets trained, the training job launches on Vertex AI, and artifacts land in GCS. Notice the scan job exists but we're using `skip_scan=true` for now. Then read `model-tuning/train_advisor.py` for the training logic.

**Hint 3 (Specific):** Ask Claude:

```
"Walk me through gate-1-train.yaml step by step. For each job and step, explain what it does and why. Then do the same for train_advisor.py -- focus on the LoRA configuration."
```

Key things to look for in the workflow:
- `workflow_dispatch` inputs (line 8-57) -- these are your customization points
- The scan step exists but uses `skip_scan` input (we skip it for now — Module 5 enables it)
- Training uses `pytorch-gpu.2-4.py310:latest` container with GCS FUSE
- The `--no-4bit` flag avoids bitsandbytes compatibility issues
- Output goes to the staging bucket under `raw-models/{output_name}/{run_id}/`

---

## Challenge 2.2: Customize and Train

### Flow

Now that you understand the pipeline, run it. Choose your own configuration and trigger a training job.

**Decisions to make:**
- **output_name**: Pick a name for your model (e.g., your name + "advisor")
- **max_steps**: 50 for a quick test (~15 min), 200+ for better quality (~30-45 min)
- **machine_type**: `a2-highgpu-1g` (A100, fastest) or `g2-standard-12` (L4, cost-effective)

**Important:** Use `skip_scan=true` when triggering. We're focusing on the training pipeline mechanics in this module. AIRS scanning gets configured in Module 4 and integrated into the pipeline in Module 5. For now, you're building without the security layer — and in Module 3 you'll see exactly what that means when you deploy with zero checks.

Trigger the Gate 1 workflow via GitHub Actions. Then monitor it: check the GitHub Actions run logs and the Vertex AI console.

### Baseline Check (IMPORTANT — do this before moving to 2.3)

After triggering the workflow, **wait ~60-90 seconds** and verify the GitHub Actions job gets past the initial setup steps before moving the student to Challenge 2.3. Check with:

```bash
gh run list --workflow="Gate 1: Train Model" --limit 1
# Then get the run ID and check job status:
gh run view <RUN_ID> --json status,jobs
```

**What to look for:**
- The `Train on Vertex AI` job should reach "Launch Vertex AI Training Job" step (takes ~30-60s)
- If it fails in the first minute, it's a config issue — debug before moving on

**Common early failures:**
- `PERMISSION_DENIED` on GCS operations → IAM roles missing on GitHub Actions SA (Challenge 0.2b)
- `PERMISSION_DENIED` on Vertex AI → `roles/aiplatform.user` missing
- Workflow env vars still placeholders → check `STAGING_BUCKET` and `PROJECT_ID` in the workflow file
- Scan step fails (if `skip_scan` wasn't set) → PyPI auth or security group UUIDs not configured

**If it fails:** Debug the issue with the student — this is learning. Common IAM failures are documented in CLAUDE.md under "Common Pipeline Failures."

**If the GH Actions job succeeds** (submits the Vertex AI job): The training itself runs on GCP, not GitHub. The GH Actions run will complete quickly (~60s) while the actual training continues on Vertex AI for 15-30+ minutes. Check Vertex AI job state:

```bash
gcloud ai custom-jobs list --region=us-central1 --project=$(gcloud config get-value project) --sort-by=~createTime --limit=1 --format="table(displayName,state,createTime)"
```

**Expected Vertex AI states:** `JOB_STATE_PENDING` (GPU provisioning, 5-15 min) → `JOB_STATE_RUNNING` (training) → `JOB_STATE_SUCCEEDED`

Only proceed to Challenge 2.3 once you've confirmed the job is at least `PENDING` on Vertex AI.

**Send the student to check both UIs themselves:**
- **GitHub Actions:** `https://github.com/{their-repo}/actions` — have them click into the run to see the job steps and logs
- **Vertex AI Console:** `https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={project-id}` — have them find their training job and observe the state

This builds familiarity with both monitoring surfaces. They'll use both throughout the lab.

### Hints

**Hint 1 (Concept):** `workflow_dispatch` means you can trigger the workflow manually with custom inputs. You can do this from the GitHub web UI (Actions tab) or from the CLI using `gh workflow run`. The training job runs on Vertex AI, not on the GitHub Actions runner -- the runner just submits the job and (optionally) waits.

**Hint 2 (Approach):** Use the `gh` CLI to trigger the workflow. You need to pass your chosen inputs as `-f` flags. After triggering, watch the run in GitHub Actions and check the Vertex AI console for the training job.

**Hint 3 (Specific):**

```bash
BRANCH=$(git branch --show-current)
gh workflow run "Gate 1: Train Model" -r "$BRANCH" \
  -f base_model="Qwen/Qwen2.5-3B-Instruct" \
  -f base_model_source="huggingface_public" \
  -f dataset="ethanolivertroy/nist-cybersecurity-training" \
  -f output_name="my-security-advisor" \
  -f max_steps="50" \
  -f machine_type="a2-highgpu-1g" \
  -f skip_scan="true"
```

Monitor progress:
```bash
gh run list --workflow="Gate 1: Train Model" --limit 3
gh run watch  # Interactive watcher
```

Check the Vertex AI console:
`https://console.cloud.google.com/vertex-ai/training/custom-jobs`

---

## Challenge 2.3: While You Wait -- Understanding the Merge

### Flow

Training takes time. Use it wisely. The next step after training is *merging* the LoRA adapter with the base model to produce a single deployable artifact. This is a critical concept -- understand it now.

Use `/explore merge-process` in Claude Code for guided exploration.

Read `model-tuning/merge_adapter.py` and answer:

- What is a LoRA adapter? Why can you not deploy it by itself?
- What does `merge_and_unload()` actually do?
- Why is the output saved as safetensors (not pickle)?
- Why does the merge script fix `extra_special_tokens` in the tokenizer config?
- Why does the merge run on CPU? (No GPU needed)

> **ENGAGE**: "Why can't you deploy a LoRA adapter directly? What problem does merging solve?"
> Award 1 pt for meaningful engagement. No wrong answers — teach if needed.
> (Answer: A LoRA adapter is a delta on top of frozen base weights — it's not a standalone model. You need both the base + adapter to produce outputs. Merging combines them into one artifact for deployment.)

### Hints

**Hint 1 (Concept):** A LoRA adapter is a set of small weight matrices that modify the base model's behavior. It is not a standalone model -- it is a *delta* on top of the base. To deploy, you merge the adapter weights into the base model weights, producing a single unified model. This is a math operation (matrix addition), not training, so no GPU is needed.

**Hint 2 (Approach):** Read `model-tuning/merge_adapter.py` -- it is relatively short and well-commented. Focus on:
- How it loads the base model and adapter separately
- The `merge_and_unload()` call that combines them
- The safetensors output format
- The tokenizer compatibility fix for vLLM

**Hint 3 (Specific):** Ask Claude:

```
"Read model-tuning/merge_adapter.py and explain each section. What goes in, what comes out, and why do we need this step? Also explain the extra_special_tokens fix -- what breaks without it?"
```

Key insight: The merged model is the artifact that gets *scanned by AIRS* and *deployed to Vertex AI*. If you only scanned the adapter, you would miss the full picture. If you only scanned the base model, you would miss any modifications from training.

---

## Challenge 2.4: Check Your Work

### Flow

Once training completes, verify that the artifacts are where they should be. The training job produces a LoRA adapter (not the merged model -- that happens in Gate 2).

Confirm:
- The adapter files exist in GCS at the expected path
- A manifest.json was created alongside the adapter
- The GitHub Actions run shows a successful summary with the output path

### Hints

**Hint 1 (Concept):** The training output includes adapter weight files (small, typically 50-200MB), a training configuration, and a model manifest that tracks provenance. The manifest is how later gates know where this adapter came from and what scans it has passed.

**Hint 2 (Approach):** Use `gcloud storage ls` to browse the output directory. Check the GitHub Actions run summary (visible in the web UI or via `gh run view`). Read the manifest to see what provenance information was recorded.

**Hint 3 (Specific):**

```bash
# List training output (replace with your output_name and run_id)
gcloud storage ls gs://your-model-bucket/raw-models/my-security-advisor/ --recursive

# Get the run ID from the latest Gate 1 run
gh run view --json conclusion,displayTitle

# Download and inspect the manifest
gcloud storage cat gs://your-model-bucket/raw-models/my-security-advisor/<run-id>/manifest.json | python -m json.tool
```

The manifest should show: model name, base model, dataset, training config, and any Gate 1 scan results.
