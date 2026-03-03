# Troubleshooting Guide

Common issues encountered during AIRS MLOps Lab setup and their solutions.

---

## SDK and Authentication Issues

### 1. "uv sync fails with private PyPI resolution error"

**Symptom:**
```
error: Failed to download: model-security-client
  Caused by: No solution found when resolving dependencies
```

**Cause:** The `model-security-client` wheels are Python 3.12 only. When uv tries to resolve dependencies, it evaluates Python 3.13+ markers and fails because no compatible wheels exist.

**Solution:** Install directly into existing venv instead of using `uv sync`:
```bash
# If you already have a venv
uv pip install "model-security-client[gcp]>=0.3.0"

# Or create a fresh venv with explicit Python 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install "model-security-client[gcp]>=0.3.0"
```

---

### 2. "Superuser role required for PyPI auth endpoint"

**Symptom:**
```
Error: 403 Forbidden - Insufficient permissions for /mgmt/v1/pypi/authenticate
```

**Cause:** The AIRS private PyPI authentication endpoint requires elevated permissions beyond the standard `airs_model_api_all` role.

**Solution:**
1. Request superuser role for your service account in Strata Cloud Manager
2. Or use a pre-authenticated URL from someone with superuser access:
   ```bash
   # Get authenticated PyPI URL (requires superuser)
   # Ensure MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET are set
   ./scripts/get-pypi-url.sh

   # Use the URL in pip install
   pip install --extra-index-url "$PYPI_URL" "model-security-client[gcp]>=0.3.0"
   ```

---

### 3. "Model URI must be full HuggingFace URL"

**Symptom:**
```
Error: Invalid model_uri format: distilbert/distilbert-base-uncased
```

**Cause:** The AIRS SDK validates that HuggingFace model URIs are full URLs, not simple model IDs.

**Solution:** Use full URL format:
```python
# Wrong
model_uri = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

# Correct
model_uri = "https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
```

The CLI script (`scripts/scan_model.py`) handles this conversion automatically for simple model IDs.

---

### 4. "Private PyPI token expired"

**Symptom:**
```
Error: 401 Unauthorized when accessing private PyPI
```

**Cause:** The OAuth token in the PyPI URL expires after ~1 hour.

**Solution:**
- For local development: Run `./scripts/get-pypi-url.sh` to get a fresh URL
- For CI/CD: Generate the URL as a step in your workflow, or cache the installed package in your container image

---

## GCP Deployment Issues

### 5. "Container Registry permission denied"

**Symptom:**
```
ERROR: (gcloud.builds.submit) PERMISSION_DENIED
```

**Cause:** Container Registry (`gcr.io`) has different IAM permissions than Artifact Registry. Even with owner role, Cloud Build may fail due to legacy permission model.

**Solution:** Use Artifact Registry instead:
```bash
# Create Artifact Registry repository
gcloud artifacts repositories create airs-mlops-lab \
  --repository-format=docker \
  --location=us-central1

# Build and push locally
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/$PROJECT_ID/airs-mlops-lab/app:latest .
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/$PROJECT_ID/airs-mlops-lab/app:latest
```

---

### 6. "Cloud Run deployment fails with org policy error"

**Symptom:**
```
ERROR: (gcloud.run.services.add-iam-policy-binding) PERMISSION_DENIED:
One or more users named in the policy do not belong to a permitted customer.
```

**Cause:** Organization policy blocks `allUsers` IAM bindings, preventing public access to Cloud Run services.

**Solution:** Use authenticated access instead of public:
```bash
# Deploy without --allow-unauthenticated
gcloud run deploy airs-mlops-lab \
  --image=$IMAGE \
  --region=us-central1 \
  --memory=2Gi

# Access with identity token
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  "$SERVICE_URL/predict"
```

---

### 7. "Image won't run on Cloud Run"

**Symptom:**
```
Container failed to start. Failed to start and then listen on the port defined by the PORT environment variable.
```

Or in Cloud Run logs:
```
exec format error
```

**Cause:** Image was built for wrong architecture. M1/M2 Macs build `arm64` images by default, but Cloud Run requires `amd64`.

**Solution:** Build with explicit platform:
```bash
docker build --platform linux/amd64 -t $IMAGE .
```

Verify architecture before pushing:
```bash
docker inspect $IMAGE | grep Architecture
# Should show: "Architecture": "amd64"
```

---

### 8. "Cloud Run cold start timeout"

**Symptom:**
```
Container called exit(1).
```

With logs showing model loading interrupted.

**Cause:** Default timeout (60s) insufficient for loading ML models.

**Solution:** Increase timeout and memory:
```bash
gcloud run deploy airs-mlops-lab \
  --image=$IMAGE \
  --memory=2Gi \
  --timeout=300 \
  --region=us-central1
```

---

## CI/CD Issues

### 9. "GitHub Actions can't authenticate to GCP"

**Symptom:**
```
Error: google-github-actions/auth failed with: unable to retrieve access token
```

**Cause:** Workload Identity Federation misconfigured, or service account doesn't have required permissions.

**Troubleshooting steps:**

1. Verify WIF pool exists:
   ```bash
   gcloud iam workload-identity-pools list --location=global
   ```

2. Verify provider configuration:
   ```bash
   gcloud iam workload-identity-pools providers describe github \
     --workload-identity-pool=github-actions \
     --location=global
   ```

3. Check service account binding:
   ```bash
   gcloud iam service-accounts get-iam-policy \
     github-actions-deployer@$PROJECT_ID.iam.gserviceaccount.com
   ```

4. Verify attribute mapping includes `repository_owner`:
   ```
   attribute.repository_owner=assertion.repository_owner
   ```

---

### 10. "AIRS scan fails in CI but works locally"

**Symptom:**
```
Error: Scan failed: Authentication error
```

**Cause:** Missing environment variables in GitHub Actions workflow.

**Solution:** Add secrets to repository:
```bash
gh secret set MODEL_SECURITY_CLIENT_ID --body "your-client-id"
gh secret set MODEL_SECURITY_CLIENT_SECRET --body "your-secret"
gh secret set TSG_ID --body "your-tsg-id"
```

And reference in workflow:
```yaml
- name: Run AIRS scan
  env:
    MODEL_SECURITY_CLIENT_ID: ${{ secrets.MODEL_SECURITY_CLIENT_ID }}
    MODEL_SECURITY_CLIENT_SECRET: ${{ secrets.MODEL_SECURITY_CLIENT_SECRET }}
    TSG_ID: ${{ secrets.TSG_ID }}
  run: uv run python scripts/scan_model.py MODEL --ci
```

---

### 11. "Workflow fails on PR but should only deploy on main"

**Symptom:** PR workflow runs deploy job and fails.

**Cause:** Missing condition on deploy job.

**Solution:** Add conditional to deploy job:
```yaml
deploy:
  needs: [push, scan]
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

---

## Security Group Configuration

### 12. "Default security groups return unexpected results"

**Symptom:** Scan returns BLOCKED but you expected ALLOWED, or vice versa.

**Cause:** TSG-configured default security groups have specific rules that may differ from expectations.

**Reference - Default Security Group UUIDs:**

| Source Type | UUID | Description |
|-------------|------|-------------|
| HUGGING_FACE | `00000000-0000-0000-0000-000000000003` | HuggingFace Hub models |
| LOCAL | `00000000-0000-0000-0000-000000000001` | Local filesystem models |
| GCS | `00000000-0000-0000-0000-000000000002` | Google Cloud Storage models |

**Solution:**
1. View security group rules in Strata Cloud Manager
2. Create custom security group if defaults don't match requirements
3. Override default with `--security-group UUID` flag:
   ```bash
   python scripts/scan_model.py MODEL --security-group YOUR-CUSTOM-UUID
   ```

---

### 13. "Scan result only shows summary, no detailed violations"

**Symptom:** API returns `rules_failed: 3` but no details on which rules.

**Cause:** The basic scan API response includes only summary counts. Detailed violation information requires viewing in SCM UI or using additional API endpoints.

**Solution:**
1. Note the scan UUID from the response
2. View full details in Strata Cloud Manager:
   ```
   AIRS > Model Security > Scans > [scan-uuid]
   ```
3. Or query the scan details API if available in your SDK version

---

## Dependency Issues

### 14. "transformers version conflict with huggingface-hub"

**Symptom:**
```
error: could not find compatible versions for huggingface-hub
```

**Cause:** Default `huggingface-hub>=1.2.4` conflicts with transformers requirements.

**Solution:** Pin huggingface-hub to compatible range:
```toml
[project]
dependencies = [
    "huggingface-hub>=0.34,<1.0",  # Compatible with transformers
    "transformers[torch]>=4.57",
]
```

---

### 15. "torch installation fails on M1/M2 Mac"

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement torch
```

**Cause:** PyTorch wheels may not be available for all Python versions on Apple Silicon.

**Solution:** Use Python 3.12 (best compatibility):
```bash
uv venv --python 3.12
uv sync
```

Or install PyTorch separately:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| uv sync fails | Use `uv pip install` directly |
| PyPI 403 | Request superuser role |
| Model URI error | Use full `https://huggingface.co/` URL |
| Container Registry denied | Use Artifact Registry |
| org policy blocks public | Use authenticated access |
| exec format error | Build with `--platform linux/amd64` |
| WIF auth fails | Check pool/provider/binding |
| AIRS scan fails in CI | Add secrets to repo |
| Unexpected scan results | Check security group rules in SCM |
