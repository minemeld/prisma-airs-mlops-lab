# Deployment Pipeline (Gates 2 and 3) — Deep Dive

> This is supplemental depth for `/lab:explore`. The essential concepts (Gate 2 merge+publish, Gate 3 deploy) are taught in the Module 3 flow. This guide goes deeper.

## Additional Topics

### Pipeline Chaining (auto_chain)
Gates can auto-chain via GitHub Actions `workflow_run` triggers: Gate 1 completion triggers Gate 2, which triggers Gate 3. This creates a fully automated pipeline from training to deployment.

**Explore:** Read `.github/workflows/gate-2-publish.yaml` — look for the `workflow_run` trigger at the top. What conditions must be met for chaining to fire? What happens if Gate 1 fails — does Gate 2 still trigger?

**Why this matters:** In production, you want the pipeline to be autonomous but with kill switches. AIRS scanning (Module 5) will add go/no-go decisions at each gate transition.

### App-Only Deploys
`deploy-app.yaml` is a separate workflow that deploys ONLY the Cloud Run application without touching the model endpoint. This is triggered on pushes to `main`.

**Explore:** Read `.github/workflows/deploy-app.yaml`. Why is this separate from Gate 3? When would you deploy the app without redeploying the model? (Answer: code changes, UI updates, config changes — anything that doesn't change the model weights.)

### Manifest Provenance System
`scripts/manifest.py` tracks artifact provenance through the pipeline. Each gate reads and updates the manifest to record: what was scanned, what was the scan result, what artifact was produced, and where it was published.

**Explore:** Read `scripts/manifest.py`. What fields does the manifest contain? How does Gate 3 verify that the model it deploys actually came from Gate 2 and not from somewhere else?

**Security insight:** Without manifest verification, an attacker could replace the model artifact in GCS between Gate 2 and Gate 3. The manifest provides a chain of custody — but only if Gate 3 actually checks it (which it doesn't on `lab-start`).

## Key Files
- `.github/workflows/gate-2-publish.yaml` — merge + publish workflow
- `.github/workflows/gate-3-deploy.yaml` — deploy endpoint + app workflow
- `.github/workflows/deploy-app.yaml` — code-only deploys
- `scripts/manifest.py` — provenance tracking

## Student Activities
- Map the artifact locations at each gate (where does the model live?)
- Disable auto_chain and trigger gates manually — what changes?
- Read the manifest after Gate 2 and identify what provenance data is recorded

## Customer Talking Point
"Gate-based pipelines give you audit points. At each gate, you can scan, verify provenance, and make go/no-go decisions. This is where AIRS fits into the workflow."
