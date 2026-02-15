# Liftotron Remediation Plan (2026-02-15)

## Prioritization Framework
- P0: 0-24h (security incident and blockers)
- P1: 1-7 days (stability and reproducibility)
- P2: 1-4 weeks (hardening and governance)

## P0 (0-24h)
1. Rotate and revoke all exposed Telegram tokens.
- Owner: repo-owner
- Verification:
  - Old token fails auth.
  - New token works only via env/secret manager.
  - Secret regex scan returns zero source hits.

2. Remove hardcoded token usage from runtime paths.
- Owner: repo-owner
- Verification:
  - `BOT_TOKEN` read from environment only.
  - Startup fails fast with clear error when env var missing.

3. Add emergency guardrails for command abuse.
- Owner: repo-owner
- Verification:
  - Unauthorized chats/users cannot execute `/lift` and `/gm`.
  - Authorized path still functional.

## P1 (1-7 days)
1. Consolidate `bot.py` and `bot2.py` into one canonical runtime module.
- Owner: repo-owner
- Verification:
  - Single executable entrypoint.
  - No undefined symbol findings in static checks.

2. Establish deterministic dependencies.
- Owner: repo-owner
- Verification:
  - Add manifest (`requirements.txt` or `pyproject.toml` + lock approach).
  - Fresh environment reproduces installation exactly.

3. Patch vulnerable dependency graph.
- Owner: repo-owner
- Verification:
  - `pip-audit` returns no known vulnerabilities for production dependency set.
  - If blockers remain, file documented risk acceptance with expiry date.

4. Fix MarkdownV2 input handling.
- Owner: repo-owner
- Verification:
  - `/lift` with Markdown-reserved chars does not break message send.
  - No unescaped user input reaches Markdown parser.

## P2 (1-4 weeks)
1. Introduce minimal automated test suite.
- Scope:
  - Handler authz checks
  - GM state transitions
  - Error-handler behavior
  - Scheduler wiring smoke test
- Verification:
  - Tests run in CI on each PR.

2. Add CI quality gate.
- Gate contents:
  - `ruff`
  - `mypy`
  - secret scan
  - dependency audit
  - unit smoke tests
- Verification:
  - Failing gate blocks merge.

3. Add governance and operations docs.
- Scope:
  - README setup/runbook
  - incident response runbook for token rotation
  - release and rollback notes
- Verification:
  - New contributor can start bot from docs only.

## Exit Criteria for Status Change
- Red -> Yellow:
  - All critical findings closed (especially secret incident actions complete).
- Yellow -> Green:
  - No open critical/major findings; only minor/info with tracked owner and target date.
