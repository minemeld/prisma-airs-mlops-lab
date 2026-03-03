Verify Module 0: Environment Setup

Read lab/.progress.json for student_id, scenario, and blockers.

## Hard Blocker Re-check

Re-check all items in the blockers array:
- `gcp-project-invalid`: Run `gcloud config get-value project` — returns valid ID?
- `gcs-buckets-missing`: Run `gcloud storage ls gs://[bucket]` — succeeds? Check pipeline-config.yaml not placeholder.
- `gcp-iam-invalid`: Run `gcloud iam service-accounts list` — github-actions-sa exists? WIF pool exists?
- `airs-credentials-missing`: Run `gh secret list` — MODEL_SECURITY_CLIENT_ID, MODEL_SECURITY_CLIENT_SECRET, TSG_ID present?

If any previously blocked item is now resolved, remove from blockers and celebrate:
"Your [X] blocker is resolved! You now have access to [what this unlocks]."

## Technical Checks

### Check 0.1: GCP Auth (1 pt)
```bash
gcloud auth list --filter="status:ACTIVE" --format="value(account)"
```
- **Pass:** Returns an active account email
- **Fail:** No active account. Add `gcp-project-invalid` to blockers.
- **Points:** 1

### Check 0.2: GCP Project (3 pts)
```bash
gcloud config get-value project
```
- **Pass:** Returns valid project ID (not empty, not `(unset)`)
- **Workshop bonus:** Verify project name matches student's expected naming pattern under TS lab folder (+1 pt)
- **Fail:** No project set. Add `gcp-project-invalid` to blockers.
- **Points:** 2 base + 1 workshop naming bonus = 3

### Check 0.3: GCS Buckets (2 pts)
Read `.github/pipeline-config.yaml`. Verify bucket names are NOT placeholders (`your-model-bucket`).
Run `gcloud storage ls` on both staging and blessed bucket paths.
- **Pass:** Real buckets, accessible
- **Fail:** Placeholders or inaccessible. Add `gcs-buckets-missing` to blockers.
- **Points:** 2

### Check 0.4: GCP IAM (3 pts)
```bash
gcloud iam service-accounts list --project=$(gcloud config get-value project) --format="value(email)" | grep github-actions-sa
gcloud iam workload-identity-pools list --location=global --format="value(name)" 2>/dev/null
gh secret list | grep -E "GCP_WORKLOAD_IDENTITY_PROVIDER|GCP_SERVICE_ACCOUNT"
```
- **Pass:** SA exists + WIF pool exists + GCP secrets set
- **Fail:** Add `gcp-iam-invalid` to blockers. HARD BLOCKER for Modules 2+.
- **Points:** 3

### Check 0.5: GitHub CLI (2 pts)
```bash
gh auth status
gh workflow list
```
- **Pass:** Authenticated + 4 workflows visible
- **Fail:** Need to authenticate with `gh auth login`
- **Points:** 2

### Check 0.6: AIRS Secrets (3 pts)
```bash
gh secret list
```
- **Pass:** MODEL_SECURITY_CLIENT_ID, MODEL_SECURITY_CLIENT_SECRET, TSG_ID all present
- **Fail:** Add `airs-credentials-missing` if not already blocked. Note: does NOT fail the entire module — student can proceed to Modules 1-3.
- **Points:** 3

### Check 0.7: Upstream Remote (1 pt)
```bash
git remote -v | grep upstream
```
- **Pass:** Upstream remote configured pointing to airs-labs/prisma-airs-mlops-lab
- **Fail:** Missing upstream remote
- **Points:** 1

## Quiz (2 questions, 6 pts max)

Present questions ONE AT A TIME. Wait for answer before moving on.
Accept answers demonstrating correct understanding — don't require exact wording.
Do NOT provide answers before the student attempts them (anti-cheat).

Score per question:
| Attempt | Points |
|---------|--------|
| Correct on first try | 3 pts |
| Correct after one retry | 2 pts |
| Correct after hint | 1 pt |
| Answer given by mentor | 0 pts |

Flow per question:
1. Present the question. Wait.
2. If correct: Award points, explain briefly, move to next.
3. If wrong: "Not quite. Think about [concept]. Want to try again?"
4. If wrong again: Offer a hint.
5. If still wrong: Give answer with full explanation. 0 pts.

### Q1: "Why does the lab use a private repo created from the template, instead of a public fork?"
**Expected:** GitHub secrets would be exposed in a public repo. The repo contains deployment configurations, bucket names, and workflow definitions that could enable info disclosure. Private repos keep secrets scoped and deployment details hidden.
- 3 pts: mentions secrets exposure AND deployment config / info disclosure
- 2 pts: mentions one of the above
- 1 pt: vague answer about "security" without specifics
- 0 pts: cannot answer

### Q2: "If pipeline-config.yaml still has 'your-model-bucket' as the staging bucket, what breaks and when?"
**Expected:** Gate 1 training output has nowhere to go (GCS write fails). Gate 2 merge can't find artifacts. The pipeline fails at the first GCS operation — immediate failure when any workflow tries to read or write model artifacts.
- 3 pts: identifies specific failure point (GCS operations in workflows) and explains cascade
- 2 pts: knows it will break but vague on where/when
- 1 pt: minimal understanding
- 0 pts: cannot answer

## Scoring Summary

| Check | Result | Points |
|-------|--------|--------|
| GCP Auth | PASS/FAIL | /1 |
| GCP Project | PASS/FAIL | /3 |
| GCS Buckets | PASS/FAIL | /2 |
| GCP IAM | PASS/FAIL/BLOCKED | /3 |
| GitHub CLI | PASS/FAIL | /2 |
| AIRS Secrets | PASS/FAIL/BLOCKED | /3 |
| Upstream Remote | PASS/FAIL | /1 |
| Engagement (from flow) | — | /4 |
| Quiz Q1 | /3 | |
| Quiz Q2 | /3 | |
| **Total** | | **/25** |

**Engagement reconciliation:** Read `modules.0.engagement_points` from progress.json.
If the value is 0 or missing but the module was completed, ask the student:
"During the module we discussed topics like dedicated service accounts, WIF security,
and credit consumption. How many of those discussions do you recall participating in?"
Use their response + your conversation history to set the correct engagement total.

Update lab/.progress.json:
```
modules.0.status = "complete"
modules.0.verified = true
modules.0.challenges_completed = ["0.1", "0.2", "0.2b", "0.3", "0.4", "0.5"]
modules.0.engagement_points = [from flow]
modules.0.points_awarded = [total of ALL points including engagement]
modules.0.quiz_scores = {"q1": X, "q2": Y}
leaderboard_points += modules.0.points_awarded (subtract previously awarded to avoid double-counting)
```

## Leaderboard

```bash
bash lab/verify/post-verification.sh 0 "$STUDENT_ID"
```

Congratulate and suggest `/lab:module 1`.
