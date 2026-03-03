Verify Module 4: AIRS Deep Dive

Read lab/.progress.json for student_id, scenario, and blockers.

## Hard Blocker Re-check

Re-check all items in the blockers array:
- `gcp-project-invalid`: valid GCP project set?
- `gcs-buckets-missing`: buckets accessible?
- `gcp-iam-invalid`: SA and WIF configured?
- `airs-credentials-missing`: AIRS secrets present? (This one is CRITICAL for Module 4+)

If any previously blocked item is now resolved, remove from blockers and celebrate.

## Technical Checks

### Check 4.1: Deployment Profile (2 pts)
Ask student to confirm AI Model Security is visible in their SCM console (AI Security → AI Model Security).
- **Pass:** Student can navigate to Model Security dashboard
- **Fail:** Deployment profile not yet active (may need time)
- **Points:** 2

### Check 4.2: Credentials Validated (2 pts)
Ask student to run a scan (or show a recent scan result) proving AIRS auth works. Any verdict counts — the point is auth success.
- **Pass:** Scan completed with any verdict (ALLOWED or BLOCKED)
- **Fail:** Auth errors or scan failures
- **Points:** 2

### Check 4.3: Security Groups (2 pts)
Ask student to name at least 2 default security groups and their source types (e.g., "Default Local" → LOCAL, "Default GCS" → GCS). They should know UUIDs or how to find them.
- **Pass:** Can name 2+ groups with correct source types
- **Fail:** Cannot identify security groups
- **Points:** 2

### Check 4.4: Violation Details Retrieved (2 pts)
Ask student to show they retrieved per-rule evaluation or violation details (from Challenge 4.5 Discovery Challenge). They should have found a way to get detailed rule-by-rule results — either via API, SCM web UI drill-down, or another method.
- **Pass:** Can show per-rule results (which rules passed/failed, violation descriptions, or remediation steps) for at least one scan
- **Fail:** Only has aggregate scan summary (rules_passed/failed counts), never got per-rule detail
- **Points:** 2

**Verification context (for agent use during verify only):**
The data API at `/aims/data/v1/scans/{uuid}/evaluations` and `/aims/data/v1/scans/{uuid}/rule-violations` provides per-rule details. The student may have found this via pan.dev docs, web search, or exploring the SCM UI. Any method that gets per-rule detail counts as a pass. If they used SCM UI only (not API), that's still a pass but note it for the scoring — the API discovery was the stretch goal.

## Quiz (2 questions, 6 pts max)

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

### Q1: "The Qwen model was BLOCKED but all threat detection rules PASSED. Explain why, and what's the difference between threat detection and governance rules?"
**Expected:** Threat detection rules check if a model is technically safe (code execution, backdoors, unsafe formats). Governance rules check organizational policy (approved licenses, verified orgs, approved locations). Qwen failed governance rules (license type 'other' not approved, org not verified) despite being technically safe. These are policy decisions, not security detections.
- 3 pts: explains both rule types AND the Qwen-specific failures (license + org)
- 2 pts: gets the concept but vague on specifics
- 1 pt: minimal understanding
- 0 pts: cannot answer

### Q2: "A customer wants different scanning policies for dev and production environments. How would you set this up with AIRS security groups, and what's the benefit?"
**Expected:** Create separate security groups for each environment (or use the same group with different rule enforcement modes). Dev environment: rules set to non-blocking/alert so teams can iterate without friction. Production: rules set to blocking so nothing untested reaches production. Same detection engine, configurable enforcement. The benefit: security teams maintain visibility everywhere while adapting strictness to context.
- 3 pts: explains the multi-environment setup AND articulates why (iteration speed vs production safety)
- 2 pts: knows the concept but weak on implementation
- 1 pt: minimal understanding
- 0 pts: cannot answer

## Scoring Summary

| Check | Result | Points |
|-------|--------|--------|
| Deployment Profile | PASS/FAIL | /2 |
| Credentials Validated | PASS/FAIL | /2 |
| Security Groups | PASS/FAIL | /2 |
| Violation Details | PASS/FAIL | /2 |
| Engagement (from flow) | — | /2 |
| Quiz Q1: Threat vs governance | /3 | |
| Quiz Q2: Multi-env policy | /3 | |
| **Total** | | **/16** |

Update lab/.progress.json:
```
modules.4.status = "complete"
modules.4.verified = true
modules.4.challenges_completed = ["4.1", "4.2", "4.3", "4.4", "4.5"]
modules.4.engagement_points = [from flow]
modules.4.points_awarded = [total of ALL points including engagement]
modules.4.quiz_scores = {"q1": X, "q2": Y}
leaderboard_points += modules.4.points_awarded (subtract previously awarded to avoid double-counting)
```

## Leaderboard

```bash
bash lab/verify/post-verification.sh 4 "$STUDENT_ID"
```

Congratulate and suggest `/lab:module 5`.
