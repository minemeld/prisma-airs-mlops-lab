# Lab System Architecture

> Reference doc for agents working on the AIRS MLOps Lab. Describes how all the pieces connect, conventions to follow, and how to iterate on the system.

## System Overview

This is a Claude Code-guided hands-on lab where Claude acts as a Socratic mentor. Students are PANW security consultants learning ML security. The agent guides them through 8 modules across 3 acts, teaching concepts through code exploration, executing mechanical steps for them, and assessing understanding through quizzes.

The student interacts via slash commands (`/lab:module N`, `/lab:verify-N`, etc.). The agent reads internal playbooks (flow files) that the student never sees directly, presents concepts from the project's actual code, and tracks progress in a JSON state file.

## File Structure

```
prisma-airs-mlops-lab/
├── CLAUDE.md                              # Mentor persona, rules, scoring, all agent behavior
├── lab.config.yaml                        # Lab identity, scenarios, requirements, leaderboard
├── lab/
│   ├── .progress.json                     # Student state (module, challenge, scores, blockers)
│   ├── .visuals/                          # Generated HTML diagrams (gitignored)
│   ├── LAB-0.md ... LAB-7.md             # Student-facing reference cards
│   ├── LAB_GUIDE.md                       # High-level curriculum overview
│   └── topics/
│       └── module-N/                      # Deep-dive topic guides for /lab:explore
│           ├── topic-name.md
│           └── ...
├── .claude/
│   ├── commands/lab/
│   │   ├── module.md                      # /lab:module N — entry point, loads everything
│   │   ├── explore.md                     # /lab:explore TOPIC — guided deep dive
│   │   ├── verify-0.md ... verify-7.md    # /lab:verify-N — assessment + scoring
│   │   ├── progress.md                    # /lab:progress — dashboard
│   │   ├── quiz.md                        # /lab:quiz — redirect to verify
│   │   ├── visual.md                      # /lab:visual — HTML diagram generation
│   │   └── flows/
│   │       └── module-0.md ... module-7.md  # Internal playbooks (never shown to students)
│   └── reference/
│       ├── lab-system-architecture.md     # THIS FILE
│       ├── workshop-context.md            # Instructor context, CSP, credits
│       ├── airs-provisioning.md           # AIRS setup steps
│       ├── airs-tech-docs/                # Product documentation
│       └── research/                      # ML security threat research
└── scenarios/
    ├── ts-workshop/                       # Instructor-led workshop scenario
    │   ├── config.yaml                    # GCP constraints, naming, cross-lab
    │   └── flows/                         # Optional overlay flow files
    └── public/                            # Public/self-guided scenario
```

## How `/lab:module N` Works

When a student types `/lab:module 3`, this sequence executes (defined in `module.md`):

1. **Git fetch** — check for upstream updates
2. **Verify `gh` targets correct repo** — `gh repo set-default origin` (prevents upstream footgun)
3. **Detect working branch** — store `$BRANCH` for all `gh workflow run -r $BRANCH` calls
4. **Read `lab.config.yaml`** — lab identity, scenarios, leaderboard URL
5. **Read `lab/.progress.json`** — student state, onboarding check
6. **Read `lab/LAB-3.md`** — student-facing objectives (present to student)
7. **Read `.claude/commands/lab/flows/module-3.md`** — internal playbook (agent's guide)
8. **Read scenario overlay** (if `scenarios/{scenario}/flows/module-3.md` exists)
9. **Read scenario config** (`scenarios/{scenario}/config.yaml`)
10. **Check blockers** — warn on active blockers
11. **Present objectives** — from LAB-3.md
12. **Follow flow file** — challenge by challenge
13. **Track engagement** — write points immediately after each ENGAGE marker
14. **Check hard stops** — enforce presentation breaks if scenario requires

## Flow File Template (The New Pattern)

Module 3 is the prototype. All flow files should follow this structure:

```markdown
# Module N Flow: [Title]

> INTERNAL PLAYBOOK — never shown to students.

## Points Available
| Source | Points | When |
|--------|--------|------|
| Engage: [topic] | 1 | During flow |
| Technical: [check] | 2 | During verify |
| Quiz Q1 | 3 | During verify |
| **Total** | **X** | |

## Challenge N.X: [Title]

### Learning Objectives
The student should be able to:
- [Observable outcome — verb + specific]

### Key Concepts
Teach these BEFORE the student takes action. One at a time, wait for response.

1. **[Concept Name]**
   - Core idea: [1-3 sentences — what to understand]
   - Show: [file path to read and display inline, or [VISUAL] for diagram]
   - Check: [understanding intent — NOT exact question text]

### Action
[What to execute after concepts are understood]

### Debrief
[What to observe, connect to previous/next modules, customer relevance]

### Deep Dive
For `/lab:explore`: `lab/topics/module-N/[topic].md`
```

### Key Conventions

- **`Core idea:`** — Brief explanation. The agent uses this as background knowledge but teaches conversationally, not by reading it verbatim.
- **`Show:`** — File path to READ and DISPLAY INLINE. The agent must paste code into a fenced code block because the Read tool output is not visible to the student. Can also mark `[VISUAL]` to trigger `/lab:visual` for HTML diagram generation.
- **`Check:`** — Describes what understanding to probe for, NOT an exact question. The agent formulates natural questions from the intent. Example: "Can the student explain WHY..." not "Ask: Why is the model separate?"
- **`> ENGAGE:`** — Point-scoring moment (1 pt). Effort-based, not correctness. Write to `modules.N.engagement_points` immediately after.
- **`> CONTEXT:`** — Read a reference doc for background (don't dump on student).

### What NOT to Put in Flow Files

- Verbatim scripted questions (use `Check:` intent instead)
- Hints sections (removed — agent re-teaches Key Concepts when student is stuck)
- Duplicated content from LAB-x.md or topics
- Self-paced branching logic (workshop-only for now)

## LAB-x.md — Student Reference Cards

Student-facing documents read at module start. Kept slim — no duplication with flows.

```markdown
# Module N: [Title]

## Overview
[2-3 sentences]

## Objectives
- [Observable outcomes matching flow Learning Objectives]

## Prerequisites
- [What must be complete]

## Challenges
### N.1: [Title]
[1-2 sentence description]

## Customer Context
[2-3 talking points — the "so what" for consultants]

## What's Next
[Transition, hard stop warning if applicable]
```

**Rule:** LAB files contain ONLY what the student needs to see independently. All teaching logic, scoring, and agent behavior lives in the flow file.

## Topic Files — Deep Dives for `/lab:explore`

Located at `lab/topics/module-N/[topic-name].md`. Triggered when student runs `/lab:explore [topic]`.

**Role:** Supplemental depth beyond the main flow. Essential concepts have been bubbled up into flow Key Concepts. Topics provide ADDITIONAL exploration for curious students.

**Structure:**
```markdown
# [Topic Name] — Deep Dive

> Supplemental depth for /lab:explore. Essential concepts are taught in the Module N flow.

## Additional Topics
### [Subtopic]
[Explanation]
**Explore:** [What to read/try]

## Key Files
- [file paths relevant to this topic]

## Student Activities
- [Hands-on exploration tasks]

## Customer Talking Point
"[Consultant-ready statement]"
```

## Verify Files — Assessment

Located at `.claude/commands/lab/verify-N.md`. Triggered by `/lab:verify-N`.

**Structure:**
1. Hard blocker re-check (list of blocker keys with commands)
2. Technical checks (bash commands, pass/fail, points)
3. Quiz (questions one at a time, scored 0-3 per question with retry flow)
4. Scoring summary table
5. Progress.json field updates
6. Leaderboard webhook call
7. Module completion feedback collection

**Quiz scoring:**
| Attempt | Points |
|---------|--------|
| Correct first try | 3 |
| Correct after retry | 2 |
| Correct after guidance | 1 |
| Given by mentor | 0 |

**Quiz questions must align with flow Learning Objectives.** If the flow teaches "why self-host," the quiz should test that — not something taught only in a topic file.

## Visual System

The `/lab:visual` command (`.claude/commands/lab/visual.md`) generates self-contained HTML files.

- **Output:** `lab/.visuals/[module]-[challenge]-[concept].html`
- **Design:** Zero dependencies, dark theme (#0f172a), 100-300 lines, single viewport
- **Types:** Architecture diagram, pipeline flow, request flow (sequence), comparison table
- **Trigger:** `[VISUAL]` marker in a Key Concept's `Show:` field, or agent's judgment
- **gitignored** — generated per-session, not committed

## Scoring System

**Three sources, two timing windows:**

During `/lab:module N` (flow):
- **Engagement** (1 pt each) — at `> ENGAGE:` markers. Effort-based. Written to `modules.N.engagement_points` IMMEDIATELY.

During `/lab:verify-N`:
- **Technical checks** — automated pass/fail with point values
- **Quiz** — 0-3 pts per question

Instructor-only:
- **Collaboration bonuses** — via leaderboard `post-bonus.sh`

**Progress.json fields per module:**
```json
{
  "modules": {
    "3": {
      "status": "complete",
      "challenges_completed": ["3.1", "3.2", "3.3", "3.4"],
      "engagement_points": 2,
      "points_awarded": 15,
      "quiz_scores": {"q1": 3, "q2": 2, "q3": 3},
      "verified": true,
      "verified_at": "2026-03-03T04:00:00Z"
    }
  }
}
```

**Leaderboard:** After every verify, call `bash lab/verify/post-verification.sh <MODULE> "$STUDENT_ID"`.
**Feedback:** After verify, collect student feedback + mentor observations via `post-feedback.sh`.

## Scenario System

Defined in `lab.config.yaml`. Student selects during onboarding.

| Scenario | Hard Stops | Leaderboard | Use Case |
|----------|-----------|-------------|----------|
| ts-workshop | true | true | Instructor-led, presentation breaks |
| ts-self-paced | false | true | Async self-guided |
| internal | false | false | Internal PAN teams |
| public | false | false | Open source |

**Overlay mechanism:** `scenarios/{scenario}/flows/module-N.md` can supplement or override base flows. Currently placeholder `.gitkeep` files — not yet populated.

**Hard stops:** Checked at end of module. Key break: between Modules 3 and 4 (AIRS presentation).

## CLAUDE.md — The Agent's Brain

Everything about agent behavior lives here. Key sections:

| Section | What it controls |
|---------|-----------------|
| Your Role | Socratic mentor, one concept at a time, celebrate progress |
| Bias Toward Action | Teach concepts first, then execute mechanically |
| Pacing Rules | 1-2 paragraphs max, always end with question |
| Flow Files Are Guides | Not scripts — agent asks naturally from Check intents |
| Content Delivery Rules | Code display (paste inline!), visual aids, formatting, pacing enforcement |
| Scenario System | Loading order, overlays, hard stops |
| Onboarding Flow | Mandatory first-run: name, scenario, progress init |
| Hard Blockers | Named blockers, warning severity, re-check on verify |
| Scoring & Points | Engagement/technical/quiz, anti-cheat, leaderboard |
| Module Completion Feedback | Student + mentor observations after each verify |
| Language Support | Match student's language, keep tech terms in English |

## How to Iterate on a Module

1. **Edit the flow file** (`.claude/commands/lab/flows/module-N.md`)
   - This is the primary source of truth for teaching content
   - Follow the template: Learning Objectives → Key Concepts → Action → Debrief
   - Use `Show:` with real file paths and `Check:` with understanding intent
   - Add `[VISUAL]` markers where diagrams help

2. **Update LAB-N.md** to match
   - Keep objectives aligned with flow Learning Objectives
   - Keep challenge descriptions brief (details are in the flow)

3. **Update verify-N.md** quiz questions
   - Quiz must test what the flow teaches (aligned with Learning Objectives)
   - Don't test deep-dive content that only lives in topic files

4. **Update topic files** if teaching content moved
   - Topics are supplemental — remove content that duplicated into flow Key Concepts
   - Add deeper material for `/lab:explore`

5. **Test** — fresh `progress.json`, new Claude session, run `/lab:module N` end-to-end

## Common Pitfalls

- **Agent reads file but student can't see it** — The Read tool output is collapsed. Agent MUST paste relevant code into a fenced code block in the response text.
- **`gh` targeting upstream repo** — Module 0 runs `gh repo set-default origin`. Always pass `-R` when unsure.
- **Workflows running on wrong branch** — Always use `gh workflow run -r $BRANCH`. Without `-r`, runs `main` which has AIRS scanning that fails early.
- **Engagement points lost** — Write to progress.json IMMEDIATELY after each ENGAGE, not batched. Context compression or session restart loses unbatched points.
- **Quiz testing unexplored content** — If the flow doesn't teach it, the quiz shouldn't test it. Deep-dive topics are bonus, not assessed.
- **`---` horizontal rules** — Don't render in Claude Code terminal. Use `━━━━━━━━━━━` unicode separators instead.
- **Over-prescribing questions** — `Check:` describes intent ("can they explain WHY...") not verbatim text. Let the agent be conversational.

## Cross-Lab Applicability

The same system architecture is used across all three AIRS labs:
- `prisma-airs-mlops-lab` (this repo)
- `airs-redteam-lab`
- `airs-runtime-agent-lab`

All share: CLAUDE.md structure, `.claude/commands/lab/` commands, flow file patterns, progress.json schema, leaderboard integration, scenario system. Templates and conventions from this doc apply to all three.
