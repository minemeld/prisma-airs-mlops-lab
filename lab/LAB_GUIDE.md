# AIRS MLOps Lab: Secure LLM Supply Chain

**Role:** DevSecOps Engineer  
**Objective:** Secure an AI pipeline against supply chain attacks using Palo Alto Networks Prisma AIRS (AI Runtime Security).

---

## 📚 Curriculum

### Module 1: The Foundation - Secure Training (Gate 1)
**Goal:** Train a "Cloud Security Advisor" LLM on NIST cybersecurity guidelines.
- **Workflow:** `Gate 1: Train Model` (`gate-1-train.yaml`)
- **Security Check:** AIRS scans the base model (e.g., HuggingFace) *before* training starts. Malicious models are blocked.
- **Outcome:** A fine-tuned model trained on Vertex AI.

### Module 2: Safe Publishing (Gate 2)
**Goal:** Publish the trained model to a secure registry.
- **Workflow:** `Gate 2: Publish Model` (`gate-2-publish.yaml`)
- **Security Check:** AIRS scans the *trained* model artifacts in staging storage to ensure no poisoning occurred during training.
- **Outcome:** A "blessed" model in the Production Registry.

### Module 3: Deployment & Verification (Gate 3)
**Goal:** Deploy the application with runtime protection.
- **Workflow:** `Gate 3: Deploy` (`gate-3-deploy.yaml`)
- **Security Check:** Pre-deployment AIRS scan + Cloud Run deployment with A/B testing capability.
- **Outcome:** A live `cloud-security-advisor` service protected by AIRS.

---

## 🛠️ Architecture

### 3-Gate Security Model
1. **Gate 1 (Input):** Scan base model downloads (Prevent ingress of bad models).
2. **Gate 2 (Output):** Scan trained artifacts (Prevent publishing compromised models).
3. **Gate 3 (Runtime):** Verify before deploy + Runtime firewall.

### Decoupled Inference
The application runs as a lightweight UI/API service on Cloud Run, while the heavy LLM inference runs on:
- **Local:** Bundled in container (default for dev).
- **Vertex AI:** Managed endpoint (production scale).
- **Cloud Run:** Dedicated inference service GPU/CPU.

---

## 🚀 Lab Instructions

### Step 1: Run Gate 1 (Train)
Trigger the training workflow:
```bash
BRANCH=$(git branch --show-current)
gh workflow run "Gate 1: Train Model" -r "$BRANCH" \
  -f base_model=distilbert-base-uncased \
  -f base_model_source=huggingface_public
```
*Observe AIRS scanning the model download. If blocked, the pipeline fails safely.*

> **Important:** Always pass `-r "$BRANCH"` to `gh workflow run`. Without it, `gh` defaults to the `main` branch, which may have different workflow steps (e.g., AIRS scanning that requires credentials not yet configured).

### Step 2: Run Gate 2 (Publish)
After training succeeds, verify and publish:
```bash
gh workflow run "Gate 2: Publish Model" -r "$BRANCH" \
  -f model_source=gs://your-model-bucket/raw-models/...
```

### Step 3: Run Gate 3 (Deploy)
Deploy the secured application:
```bash
gh workflow run "Gate 3: Deploy" -r "$BRANCH" \
  -f deployment_strategy=canary
```

---

## 🔍 Troubleshooting

See [docs/CICD_LEARNINGS.md](../docs/CICD_LEARNINGS.md) for details on known issues like:
- Vertex AI permission errors (`roles/aiplatform.user`)
- HuggingFace URL formats
- Model scanning failures
