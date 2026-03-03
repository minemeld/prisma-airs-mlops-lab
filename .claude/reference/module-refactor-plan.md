# Module Refactor Plan — Remaining Modules

> Agent prompt: Use this document to refactor the remaining lab modules (0, 1, 2, 5, 6, 7) to the new objective-driven teaching structure. Modules 3 and 4 are already done and serve as the reference implementations.

## What Was Done and Why

The lab's teaching system was restructured from scripted questions + hints to an objective-driven exploration model. The core problems were:
- Flow files had scripted verbatim questions making the agent robotic
- 3-level hint system duplicated content from topic files
- Agent barreled through challenges ("bias toward action") without pausing to teach
- LAB-x.md student guides duplicated flow file content
- No output style guidance (agent did file reads but didn't show code to students)
- No visual capability

## The New Template

Every challenge in a flow file follows this structure:

```markdown
## Challenge N.X: [Title]

### Learning Objectives
The student should be able to:
- [Observable outcome — verb + specific]

### Key Concepts
Teach these BEFORE the student takes action. One at a time, wait for response.

1. **[Concept Name]**
   - Core idea: [1-3 sentences — what to understand]
   - Show: [file path to read and DISPLAY INLINE, or [VISUAL] for diagram]
   - Check: [understanding intent — NOT verbatim questions]

### Action
[What to execute after concepts are understood. Mechanical steps.]

### Debrief
[What to observe, connect to previous/next modules, customer relevance.]

### Deep Dive
For `/lab:explore`: `lab/topics/module-N/[topic].md`
```

### Key Conventions

- **`Core idea:`** — Agent's background knowledge, taught conversationally (not read verbatim)
- **`Show:`** — File path to READ and DISPLAY INLINE in a code block. The Read tool output is NOT visible to students — you MUST paste code into the response
- **`Check:`** — Understanding intent, not exact words. Agent formulates natural questions
- **`[VISUAL]`** — Triggers `/lab:visual` to generate an HTML diagram in `lab/.visuals/`
- **`> ENGAGE:`** — Point-scoring moment (1 pt each, effort-based). Write to progress.json immediately
- **No `### Hints` sections** — removed entirely. Agent re-teaches Key Concepts when stuck, suggests `/lab:explore`
- **No scripted questions** — Check describes WHAT to probe, agent asks naturally
- **Show-first approach** — Lead with code exploration, not lectures. Show the Dockerfile, ask "what's missing?" — not "The architecture is decoupled because..."

### LAB-x.md Format (Student Reference Card)

Slim format — no duplication with flow:
```markdown
# Module N: [Title]
## Overview (2-3 sentences)
## Objectives (matching flow Learning Objectives)
## Prerequisites
## Challenges (1-2 sentence descriptions each)
## Customer Context (2-3 talking points)
## What's Next
```

### Topic Files (Deep Dive Supplements)

Topics are for `/lab:explore` — supplemental depth beyond the main flow. Essential concepts were bubbled up into flow Key Concepts. Topics provide ADDITIONAL exploration. Format:
```markdown
# [Topic] — Deep Dive
> Supplemental depth for /lab:explore. Essential concepts taught in Module N flow.
## Additional Topics
## Key Files
## Student Activities
## Customer Talking Point
```

## Critical System References

Read these BEFORE starting any module refactor:

1. **Lab system architecture:** `.claude/reference/lab-system-architecture.md` — full system overview, file structure, conventions
2. **Model security scanning:** `.claude/reference/model-security-scanning.md` — how scanning works, SDK internals, source types, API surfaces
3. **AIRS provisioning:** `.claude/reference/airs-provisioning.md` — deployment profiles, TSG, IAM
4. **CLAUDE.md** — mentor config, Content Delivery Rules, pacing, scoring

## Completed Modules (Reference Implementations)

### Module 3: Deploy & Serve
- **Pattern:** Show-first exploration (Dockerfile → what's missing? → server.py → inference_client → visual)
- **Key innovation:** Use case context ("What You Built and Why") + high-level serving components (vLLM, endpoints, chat templates for security consultant audience)
- **Discovery:** Cloud Run 403 auth as a teaching moment (let them hit the wall, then teach)
- **File:** `.claude/commands/lab/flows/module-3.md`

### Module 4: AIRS Model Security Deep Dive
- **Pattern:** Install SDK from docs → scan safe/malicious/HF models → explore SCM rules → Discovery Challenge
- **Key innovations:**
  - SDK source code exploration (students read `api.py` to understand source type routing)
  - Qwen base model BLOCKED by governance rules (threat detection vs governance teaching moment)
  - Discovery Challenge (agent genuinely has NO context, student drives API exploration)
  - HuggingFace browser exploration (find models, protectai org, mcpotato/42-eicar-street)
- **Validated findings:** Custom role RBAC bug (superuser needed), security group UUIDs always required, per-rule details via `/aims/data/v1/` API
- **File:** `.claude/commands/lab/flows/module-4.md`

### Module 5 (Partial): Challenge 5.0
- Policy fix moved from Module 4 to Module 5 as setup for pipeline integration
- Student fixes Qwen governance rules → re-scan → ALLOWED → pipeline can now work
- **File:** `.claude/commands/lab/flows/module-5.md` (5.0 added, rest needs refactor)

## Environment Variable Convention

**Standardized on `MODEL_SECURITY_*`** across the entire project:
- `MODEL_SECURITY_CLIENT_ID` — service account client ID
- `MODEL_SECURITY_CLIENT_SECRET` — service account secret
- `MODEL_SECURITY_API_ENDPOINT` — API endpoint (default: `https://api.sase.paloaltonetworks.com/aims`)
- `TSG_ID` — tenant service group ID

No more `AIRS_MS_*` anywhere. Module 3 has a preflight migration check for students on old naming.

## Source Documents for Research

When refactoring each module, consult these for accurate technical content:

### In the repo
- `.claude/reference/model-security-scanning.md` — SDK internals, scanning flow, source types
- `.claude/reference/airs-provisioning.md` — IAM, deployment profiles, known bugs
- `.claude/reference/airs-tech-docs/ai-model-security.md` — full product docs
- `.claude/reference/research/airs-model-scanning-deep-dive.md` — threat research
- `.claude/reference/research/ml-model-security-threats-2026.md` — real incidents

### External (for deeper research)
- Tech docs: `/Users/syoungberg/projects/work/docs/airs/tech-docs/ai-model-security/`
- Champions summit: `/Users/syoungberg/projects/work/docs/airs/champions-summit-2026/`
- Slack archive: `/Users/syoungberg/projects/work/docs/slack/prisma-airs-champion/`
- Workshop content: `/Users/syoungberg/projects/work/code/internal/github/workshop-content/docs/modules/model-security/`
- PoV test scenarios: `/Users/syoungberg/projects/work/docs/airs/internal/guides/prisma-airs-ai-model-security-pov-test-scenarios/`

## Validation Approach

Use the student test account for validating operations:

**Test repo:** `/Users/syoungberg/projects/work/student-lab/latam-syoungberg-prisma-airs-mlops-lab/`
**Credentials:** In `.env` (MODEL_SECURITY_* naming, model-sec SA — has RBAC limitation)
**Superuser SA:** In `syoungberg-scm-management.csv` (full access)
**TSG:** 1543177838
**GCS bucket:** `gs://syoungberg-airs-lab/`
**GCP project:** `syoungberg-prod`

**Security group UUIDs (validated):**
- Default LOCAL: `a7ae2286-5a2d-4dc6-9e98-7055916725cc`
- Default HUGGING_FACE: `0ef6dadc-70ff-4fab-b4e5-854046bb7a56`
- Default GCS: `c472b2b9-5823-47cd-bda1-8a83f3b536b6`
- Default S3: `0909be6c-d578-4464-8dd9-891a739a76ff`
- Default AZURE: `2a5947ac-eac4-4912-a0be-62d09470a3dc`

**Validated scan results:**
- Safe safetensors → ALLOWED, 7/7 passed
- Pickle bomb → BLOCKED, 2/7 failed (PAIT-PKL-100 + unapproved format)
- Qwen HF → BLOCKED, 2/11 failed (license `other` + org not verified)
- Data API at `/aims/data/v1/scans/{uuid}/evaluations` and `/aims/data/v1/scans/{uuid}/rule-violations` — working with superuser

**Known issues:**
- Custom role SA: all operations fail with "Access denied" (scan, list-scans, PyPI) — superuser required
- `.env` inline comments break `source` — comments must be on separate lines
- SDK pydantic deprecation warning on every invocation — cosmetic, ignore
- No `list-security-groups` CLI command — use management API or SCM web UI

## Modules to Refactor

### Module 0: Environment Setup (Large — 468 lines)
**Current state:** Lots of operational setup challenges (GCP, IAM, GitHub CLI, AIRS creds)
**Approach:** Mostly mechanical setup — Key Concepts should focus on WHY each component exists, not just how to configure it. Show-first where possible (show the workflow file, ask what it needs before setting up IAM).
**Special considerations:**
- Module 3 preflight migration check handles env var naming for existing students
- Module 0 flow should use `MODEL_SECURITY_*` for new students
- AIRS credential setup (Challenge 0.4) should explain the RBAC situation and that custom role may not work (superuser workaround)
- The `gh repo set-default origin` safeguard must remain
- The `-r $BRANCH` workflow targeting must remain

### Module 1: ML Fundamentals & HuggingFace (184 lines)
**Current state:** Entirely conceptual — quiz-based, challenges are exploration
**Approach:** Good candidate for show-first pattern. Students explore HuggingFace, model formats, LoRA concepts. Key Concepts should guide exploration with specific things to find and discuss.
**Special considerations:**
- This is where students learn about model formats (pickle vs safetensors) — connects directly to Module 4's scanning
- HuggingFace exploration here pairs with Module 4's scanning of HF models
- No pipeline operations — purely educational

### Module 2: Train Your Model (216 lines)
**Current state:** Mix of concepts and execution. Training on Vertex AI.
**Approach:** Key Concepts before triggering training (what is LoRA, why these params, what will happen). Then execute. Good debrief opportunity while waiting for training.
**Special considerations:**
- Training takes time (50 steps = ~5 min on A100) — use wait time for teaching
- merge_adapter.py CPU vs GPU discussion (from testing session) is good teaching content
- Connect to Module 3: the artifacts produced here flow into the deployment pipeline

### Module 5: Pipeline Integration (120 lines + Challenge 5.0 added)
**Current state:** Challenge 5.0 (policy fix) already added. Rest needs refactor.
**This is the most critical module to get right.** Students add AIRS scanning to the CI/CD pipeline.
**Approach:**
- 5.0: Fix Qwen policy so pipeline can pass (already written)
- 5.1+: Add scanning to Gate 2 (modify `gate-2-publish.yaml`)
- Need to understand: what scanning step goes where, what env vars it needs, what happens on fail
- Students should examine the existing `gate-1-train.yaml` scanning step (from Module 4 SDK exploration) and replicate the pattern
**Special considerations:**
- The workflow uses `MODEL_SECURITY_*` secrets — students need to understand this
- Exit code behavior: SDK returns non-zero on BLOCKED → workflow step fails → gate blocks
- `--warn-only` flag vs strict blocking — connect to the alert/block policy concept from Module 4
- Scan labels in CI/CD (e.g., `-l gate=2 -l pipeline_run=$GITHUB_RUN_ID`) for traceability
- Students should trigger the pipeline and watch it work with scanning enabled
**Validation:** Actually trigger the pipeline on the test repo and verify scanning works

### Module 6: Threat Zoo (132 lines)
**Current state:** Execution-heavy — create malicious models, scan them
**Approach:** Key Concepts before each threat type: what is the threat, how does it work, why is it dangerous. Then create the threat model and scan. Show the violation details.
**Special considerations:**
- `scripts/create_threat_models.py` — verify this works with current SDK
- Pickle bomb (already tested — works)
- Keras exploits, format comparison — need to test
- Connect scan results back to the specific rules from Module 4

### Module 7: Gaps & Poisoning (166 lines)
**Current state:** Capstone — what AIRS can't catch, data poisoning, behavioral attacks
**Approach:** More discussion-oriented. Key Concepts about the limitations of static analysis. What requires runtime protection (connect to the other AIRS labs). Customer conversations about defense in depth.
**Special considerations:**
- Data poisoning demo (`scripts/create_threat_models.py` variants)
- This is where the "defense in depth" story comes together: Model Security (this lab) + Runtime Security (other lab) + Red Teaming
- Good place for a final synthesis visual showing where all AIRS products fit

## Process for Each Module

1. **Read the current flow file** — understand existing content and what @author: annotations exist (check both upstream and downstream clones)
2. **Read the corresponding LAB-N.md, verify-N.md, and topic files** — understand the full context
3. **Research source docs** — check tech docs, Slack archive, and champions summit content for accurate information
4. **Rewrite the flow file** using the new template (Learning Objectives → Key Concepts → Action → Debrief)
5. **Update LAB-N.md** to reference card format
6. **Update topic files** — remove duplication with new Key Concepts, add deeper material
7. **Update verify-N.md** — align quiz questions with Learning Objectives, use "guidance" not "hint" in retry flow
8. **Validate** — test operations against the student test account where applicable
9. **Commit and push** to `lab` branch

## Style Guidelines

- Lead with code exploration, not lectures
- One Key Concept per agent message (pacing enforcement from CLAUDE.md)
- `Check:` is intent ("can they explain WHY...") not exact words
- Show actual project files — Dockerfile, server.py, workflow YAML, scan_model.py
- Connect every module to the customer conversation: "what would you tell a customer about this?"
- Use `[VISUAL]` for architecture, pipeline flows, and request sequences
- The agent should feel like a curious collaborator, not a textbook
- Discovery Challenge pattern (Module 4.5): agent genuinely has NO prepared context, student drives
