# Decisions Log Entry Template

Use when appending a new decision to `docs/state/02-decisions-log.md`.

## Format

```markdown
### YYYY-MM-DD — Short title in sentence case

- **Decision:** What was decided, in concrete terms.
- **Rationale:** Why this choice over the alternatives.
- **Status:** Active | Superseded by ... | Approved, pending ... | Rejected | Deferred
- **Follow-up:** One concrete next step, or "None."
```

## Style Rules

- Title: present tense, self-explanatory outside the session context.
- Decision: actionable statement, not a description of the discussion.
- Rationale: 1-3 sentences max. Connect cause to effect.
- Status: use exact values above — consistent filtering lets Hermy or Josh query by status.
- Follow-up: exactly one actionable item. If nothing is needed, write "None."

## Examples

```markdown
### 2026-06-20 — Branch protection unavailable on free GitHub plan for private repos

- **Decision:** Since GitHub enforces branch protection rules only on paid Team plans for private repos, Hermy will self-enforce: push to feature branches only, open PRs, and wait for Josh to merge.
- **Rationale:** The ruleset Josh created is decorative on a free private repo. Self-enforcement gives the same safety without paying for GitHub Team.
- **Status:** Active. Self-enforcement begins now.
- **Follow-up:** If the repo ever moves to a Team organization, re-enable the ruleset for real enforcement.
```

```markdown
### 2026-06-20 — Use OpenRouter as the first cheap-model gateway

- **Decision:** Add OpenRouter before wiring multiple direct model providers.
- **Rationale:** One provider credential can test multiple cheap-model routes and reduce provider sprawl while learning what workloads actually need cheaper models.
- **Status:** Approved, pending credential/config setup.
- **Follow-up:** Add OpenRouter through the real Hermes CLI/auth environment; verify exact model IDs before setting auxiliary/delegation defaults.
```
