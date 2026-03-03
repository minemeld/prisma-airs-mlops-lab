Verify Module 3: Deploy & Serve

Read lab/.progress.json for student_id, scenario, and blockers.

## Hard Blocker Re-check

Re-check all items in the blockers array:
- `gcp-project-invalid`: Run `gcloud config get-value project` — returns valid ID?
- `gcs-buckets-missing`: Buckets accessible? pipeline-config.yaml not placeholder?
- `gcp-iam-invalid`: github-actions-sa exists? WIF pool exists?
- `airs-credentials-missing`: AIRS secrets present in `gh secret list`?

If any previously blocked item is now resolved, remove from blockers and celebrate.

## Technical Checks

### Check 3.1: App Deployed (2 pts)
```bash
gcloud run services describe cloud-security-advisor --region=us-central1 --format='value(status.url)' 2>/dev/null
```
- **Pass:** Returns a URL
- **Fail:** Cloud Run service not found or not deployed
- **Points:** 2

### Check 3.2: App Responds (2 pts)
Curl the URL's /health endpoint or send a test chat message.
- **Pass:** Gets a valid response (health check OK or chat response)
- **Fail:** App not responding. Check Vertex AI endpoint status, IAM, Cloud Run logs.
- **Points:** 2

## Quiz (3 questions, 9 pts max)

Present questions ONE AT A TIME. Wait for answer before moving on.
Accept answers demonstrating correct understanding — don't require exact wording.
Do NOT provide answers before the student attempts them (anti-cheat).

Score per question:
| Attempt | Points |
|---------|--------|
| Correct on first try | 3 pts |
| Correct after one retry | 2 pts |
| Correct after guidance | 1 pt |
| Answer given by mentor | 0 pts |

Flow per question:
1. Present the question. Wait.
2. If correct: Award points, explain briefly, move to next.
3. If wrong: "Not quite. Think about [concept]. Want to try again?"
4. If wrong again: Offer guidance — re-teach the relevant concept from the flow's Key Concepts.
5. If still wrong: Give answer with full explanation. 0 pts.

### Q1: "Why does this application use a custom fine-tuned model instead of calling a commercial API like OpenAI or Anthropic?"
**Expected:** Data sovereignty/control — the organization owns the model and training data, can run it in their own infrastructure, doesn't send sensitive queries to third parties. Also: compliance requirements, specialization on domain-specific knowledge (NIST/cybersecurity), cost at scale, no vendor lock-in.
- 3 pts: explains multiple reasons (control, compliance, specialization, data sovereignty)
- 2 pts: gets 1-2 reasons but misses the broader picture
- 1 pt: minimal understanding
- 0 pts: cannot answer

### Q2: "Describe the three layers of model serving in this deployment. What role does each play?"
**Expected:** (1) Serving framework (vLLM) — loads model on GPU, manages inference, exposes API. (2) Inference endpoint — the API that accepts prompts and returns completions (OpenAI-compatible format). (3) Application — user-facing service (FastAPI on Cloud Run), handles auth and business logic, calls the inference endpoint. Model runs on GPU, app runs on CPU — they're separated.
- 3 pts: describes all three layers with their roles and the GPU/CPU separation
- 2 pts: gets the separation but unclear on roles or missing a layer
- 1 pt: minimal understanding
- 0 pts: cannot answer

### Q3: "Walk through the 3-gate pipeline. What does each gate produce, and what security checks exist right now?"
**Expected:** Gate 1 trains and produces a LoRA adapter. Gate 2 merges adapter with base model, publishes to GCS. Gate 3 deploys model to GPU endpoint and app to Cloud Run. Currently NO security scans are enforcing — models flow from training to production unchecked. That's the gap Modules 5-7 will fix.
- 3 pts: describes all 3 gates AND identifies that no security is enforcing
- 2 pts: describes gates but misses the security gap
- 1 pt: minimal understanding
- 0 pts: cannot answer

## End of Act 1

IMPORTANT: This is the end of Act 1 (Build It). Before suggesting Module 4:

"Module 3 verified! This completes Act 1 — you've built a complete ML pipeline from training to deployment. There is typically an instructor-led AIRS presentation between Acts 1 and 2. Check with your instructor before starting Module 4."

Ask the student to prepare a brief summary for the group discussion: what they built, architecture decisions, training choices.

## Scoring Summary

| Check | Result | Points |
|-------|--------|--------|
| App Deployed | PASS/FAIL | /2 |
| App Responds | PASS/FAIL | /2 |
| Engagement (from flow) | — | /2 |
| Quiz Q1: Why custom model | /3 | |
| Quiz Q2: Serving components | /3 | |
| Quiz Q3: Pipeline + security gap | /3 | |
| **Total** | | **/15** |

Update lab/.progress.json:
```
modules.3.status = "complete"
modules.3.verified = true
modules.3.challenges_completed = ["3.1", "3.2", "3.3", "3.4"]
modules.3.engagement_points = [from flow]
modules.3.points_awarded = [total of ALL points including engagement]
modules.3.quiz_scores = {"q1": X, "q2": Y, "q3": Z}
leaderboard_points += modules.3.points_awarded (subtract previously awarded to avoid double-counting)
```

## Leaderboard

```bash
bash lab/verify/post-verification.sh 3 "$STUDENT_ID"
```
