# Liftotron Deep Audit Report (2026-02-15)

## 1. Executive Summary
- Scope: `liftotron` only (`bot.py`, `bot2.py`, git history, repo metadata).
- Audit depth: Deep audit (security, correctness, reliability, maintainability, supply chain, operability, testability).
- Overall verdict: **Red**.
- Primary blocker: exposed Telegram credentials in source and commit history.

## 2. Method and Baseline
### Baseline
- Commit: `0dea07420e1e499a90d84b371fa84b175e11c0d6`
- Python runtime snapshot: `reports/audit/evidence/python-version.txt`
- Pip snapshot: `reports/audit/evidence/pip-version.txt`
- Workspace state: `reports/audit/evidence/git-status.txt`

### Executed checks
- Static syntax check: `py_compile`
- Lint: `ruff`
- Type analysis: `mypy`
- Security static scan: `bandit`
- Dependency vulnerability scan: `pip-audit`
- Secret scans: working tree + git history regex scans (redacted outputs)
- Structural diff and inventory checks

Command status summary: `reports/audit/evidence/command-exit-codes.txt`

## 3. Architecture and Code Inventory
### File inventory
- Runtime candidates: `bot.py` (210 LOC), `bot2.py` (277 LOC)
- No README, no dependency manifest, no CI workflows in this repo snapshot.

Evidence:
- `reports/audit/evidence/file-inventory.txt`
- `reports/audit/evidence/line-counts.txt`
- `reports/audit/evidence/repo-metadata-checks.txt`

### Handler and scheduler map
- Command handlers: `/start`, `/lift`, `/gm`, `/rollins`, `/nako` (+ `/debug` in `bot2.py`)
- Message handler: `Filters.text` -> `check_gm`
- Daily jobs: `send_gm` (05:00), `reset_gm_users` (00:00), `check_all_gm_sent` (09:00), `send_poem` (22:00)

Evidence:
- `reports/audit/evidence/handler-scheduler-map.txt`

### Divergence risk (`bot.py` vs `bot2.py`)
- Diff shortstat: `1 file changed, 169 insertions(+), 102 deletions(-)`
- `bot2.py` appears to be a partially refactored variant while `bot.py` still contains unresolved references.

Evidence:
- `reports/audit/evidence/bot-diff-shortstat.txt`
- `reports/audit/evidence/bot-diff.txt`

## 4. Findings (Severity-ordered)
Full machine-readable findings: `reports/audit/2026-02-15-liftotron-findings.json`

### Critical
1. `LFT-SEC-001` Hardcoded Telegram token in source (`bot.py:184`, `bot2.py:20`).
2. `LFT-SEC-002` Token exposure present in git history (multiple redacted hits).

### Major
1. `LFT-SEC-003` Missing command authorization boundaries.
2. `LFT-SEC-004` `/lift` forwards unescaped user input with `MarkdownV2`.
3. `LFT-COR-001` `bot.py` includes undefined names and runtime-invalid references.
4. `LFT-REL-001` Error handling pattern can fail and suppress actionable telemetry.
5. `LFT-REL-002` Group-member completeness model is inherently partial.
6. `LFT-SUP-001` No deterministic dependency manifest/lock.
7. `LFT-SUP-002` Known vulnerabilities in dependency graph (`tornado 6.1` in audit env).
8. `LFT-MNT-001` Dual divergent runtime files create regression and ownership risk.
9. `LFT-OPS-001` Missing governance artifacts (README/runbook/CI policy).
10. `LFT-TST-001` No automated tests.

## 5. Incident Section (Secrets Exposure)
### Confirmed state
- Active token pattern exists in working tree and multiple times in git history.
- Evidence is redacted in reports to avoid further leakage.

### Immediate containment actions (P0)
1. Rotate all Telegram bot tokens via BotFather immediately.
2. Invalidate old credentials and treat as compromised.
3. Verify old token rejection and new token operation using secured env vars only.
4. Limit token access scope to deployment runtime.

### Verification checklist
- Old token returns auth failure.
- New token works only when injected through environment/secret store.
- Source tree no longer matches token pattern scan.
- History scanning policy decided (retain with rotation proof vs rewrite with documented change control).

## 6. Quality, Testing, and Reproducibility Notes
- `py_compile` passed, but this is insufficient for runtime safety.
- `ruff`, `mypy`, `bandit`, `pip-audit` all returned non-zero and identified actionable issues.
- `safety` requires interactive login and currently cannot run unattended in CI as configured.

Evidence:
- `reports/audit/evidence/ruff-check.txt`
- `reports/audit/evidence/mypy-check.txt`
- `reports/audit/evidence/bandit-check.txt`
- `reports/audit/evidence/pip-audit.txt`
- `reports/audit/evidence/safety-scan.txt`

## 7. Risk Matrix and Overall Rating
- Risk matrix: `reports/audit/2026-02-15-liftotron-risk-matrix.json`
- Overall status: **Red** (ungemitigte critical findings vorhanden)

## 8. Recommended Next Steps (linked to remediation plan)
- Execute P0 incident actions within 24h.
- Consolidate runtime to one file and introduce deterministic dependencies.
- Add baseline CI quality gate (lint + type + secret scan + dependency audit + smoke tests).

Detailed action plan: `reports/audit/2026-02-15-liftotron-remediation-plan.md`

## 9. Assumptions and Limits
- Audit is constrained to repository state at commit `0dea074`.
- No production environment access was used; operational verification steps are documented for maintainer execution.
- All published evidence is intentionally redacted for secret-like tokens.
