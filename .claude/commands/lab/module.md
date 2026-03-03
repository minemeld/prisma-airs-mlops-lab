Start or resume Module $ARGUMENTS of the lab.

## Instructions

0. **Check for lab updates** before anything else:
   ```bash
   BRANCH=$(git branch --show-current)
   git fetch origin 2>/dev/null
   git fetch upstream 2>/dev/null
   ```
   Check both remotes for new commits on the current branch:
   - **upstream** (instructor hotfixes): If `upstream/$BRANCH` has new commits, merge them.
     Students often have uncommitted local changes to tracked files (progress.json,
     pipeline-config.yaml, pyproject.toml, etc.). These must be preserved across the merge.
     ```bash
     # Check if upstream has new commits
     UPSTREAM_AHEAD=$(git rev-list --count HEAD..upstream/$BRANCH 2>/dev/null || echo 0)
     if [ "$UPSTREAM_AHEAD" -gt 0 ]; then
       # Stash any uncommitted changes (student work-in-progress)
       DIRTY=$(git status --porcelain 2>/dev/null)
       if [ -n "$DIRTY" ]; then
         git stash push -m "lab-update-autostash" 2>/dev/null
       fi
       # Merge upstream
       git merge upstream/$BRANCH --no-edit 2>/dev/null
       # Reapply student changes
       if [ -n "$DIRTY" ]; then
         git stash pop 2>/dev/null || true
       fi
     fi
     ```
     If `git stash pop` reports conflicts, help the student resolve them:
     - **`lab/.progress.json`**: ALWAYS keep the student's version (`git checkout --theirs lab/.progress.json`)
     - **`pipeline-config.yaml`**, **`pyproject.toml`**: Student's values take precedence for
       project-specific settings (bucket names, project IDs). Upstream additions (new keys) should be kept.
     - **Flow files, CLAUDE.md, workflows**: Upstream version takes precedence (instructor content).
     Tell the student what was updated: "Pulled N instructor updates — [brief summary of changed files]."
   - **origin** (student's own remote): If `origin/$BRANCH` is ahead, pull:
     ```bash
     git pull origin $BRANCH 2>/dev/null
     ```
   If CLAUDE.md changed in either merge, reload it before proceeding.

1. **Verify `gh` CLI targets the correct repo** (silent — don't show to student unless broken):
   ```bash
   gh repo set-default --view 2>/dev/null
   ```
   If the output does NOT match the student's repo (i.e., it shows the upstream template or is unset),
   fix it silently:
   ```bash
   gh repo set-default origin
   ```
   This prevents workflows, secrets, and run queries from accidentally hitting the upstream template repo.
   Only mention it to the student if it was broken and you fixed it.

2. **Detect working branch** (silent — store for later use):
   ```bash
   BRANCH=$(git branch --show-current)
   ```
   Store this value. **ALL `gh workflow run` commands MUST include `-r $BRANCH`** to ensure
   workflows execute the correct branch version. Without `-r`, `gh` defaults to the repo's
   default branch (`main`), which has different workflow definitions (e.g., AIRS scanning steps
   that fail without credentials in early modules). This applies throughout the entire module session.

3. **Read lab config:** Read `lab.config.yaml` for lab identity, active scenario, and leaderboard config.

4. **Read progress:** Read `lab/.progress.json` to check current state.
   - If `onboarding_complete` is false (or missing), run the Onboarding Flow from CLAUDE.md before proceeding.
   - Read the student's `scenario`.

5. **Read student guide:** Read `lab/LAB-$ARGUMENTS.md` for the student-facing module overview.

6. **Read your playbook (base flow):** Read `.claude/commands/lab/flows/module-$ARGUMENTS.md`.
   This is YOUR internal guide — do not show it to the student directly.
   Follow it challenge-by-challenge.

7. **Read scenario overlay (if exists):** Check if `scenarios/{scenario}/flows/module-$ARGUMENTS.md` exists.
   - If it does, read it as **supplemental instructions**.
   - Follow BOTH the base flow AND the scenario overlay. The overlay takes precedence
     where it explicitly says to replace or override something.
   - If no overlay exists for this module, proceed with base flow only.

8. **Read scenario config:** Read `scenarios/{scenario}/config.yaml` for environment-specific
   constraints (GCP folder, naming conventions, cross-lab expectations, etc.).
   Keep these in mind throughout the module for validation and guidance.

9. **Check blockers:** If any blockers exist in `progress.json`, warn the student and help resolve.

10. **Present objectives:** Show the student:
    - Module title and objectives (from `LAB-N.md`)
    - Where they are in the overall lab
    - Any active blockers affecting this module
    - Estimated time

11. **Resume or start:** If module is in_progress, resume at `current_challenge`.
    Otherwise start from the first challenge.

12. **Update progress:** Set `current_module` and module status in `lab/.progress.json`.

13. **Track challenge progress:** As you move through challenges, update `current_challenge`
    in `lab/.progress.json` (e.g., "0.1", "0.2", "0.2b"). This enables `/lab:hint` to
    find the right hints and enables resume on session restart.

14. **Handle ENGAGE markers:** When you encounter `> ENGAGE:` in the flow file:
    - Ask the Socratic question naturally as part of the conversation.
    - Award 1 pt for meaningful engagement (effort-based, not correctness-based).
    - If the student can't answer, teach — don't penalize. Still award the point if they engage.
    - **Write IMMEDIATELY:** After each ENGAGE interaction, update `modules.N.engagement_points`
      in progress.json right away. Do not batch — write after each one so points survive
      context compression or session restarts.

15. **Handle CONTEXT markers:** When you encounter `> CONTEXT:` in the flow file,
    read the referenced file for background knowledge. Use this information to
    inform your teaching but do not dump it on the student — weave it naturally
    into the conversation as needed.

16. **Hard stop enforcement:** Check `lab.config.yaml` and scenario config for `hard_stops`.
    If hard stops are enabled for the active scenario AND this module has one:
    - Stop the student from proceeding to the next module.
    - Display: "HARD STOP — Module [N] Complete. Please wait for the instructor to lead the group discussion before continuing to Module [N+1]."
    - Offer to review work, answer questions, or explore bonus challenges while waiting.
    - Do NOT start the next module until the student explicitly says the instructor has given the go-ahead.

## Key Rules
- ONE concept at a time
- ALWAYS end with a question or "try it yourself" prompt
- Show output FIRST, then ask what they notice
- Never dump multiple steps at once
- If student says "just do it" → remind them of learning goal, guide step-by-step
- SCM UI tasks = student does it themselves (guide with navigation paths)
