# Incident Response: Telegram Token Exposure

## Scope

This document tracks remediation for exposed Telegram bot credentials in source and git history.

## Execution status (2026-02-15)

- Local history rewrite completed with `git-filter-repo`.
- Working tree secret scan: no Telegram token pattern hits.
- Local history secret scan after rewrite: no Telegram token pattern hits.
- Remote force-push still required to propagate rewritten history.

## Immediate containment

1. Rotate all exposed tokens in BotFather.
2. Revoke old tokens.
3. Update runtime env (`BOT_TOKEN`) in secure storage only.

## Verification checklist

1. Old token returns authorization failure.
2. New token starts bot successfully with required env vars.
3. Working tree secret scan shows no token patterns.

## Local history cleanup procedure

Use this only after token rotation is complete.

```powershell
git filter-repo --replace-text .\reports\audit\evidence\filter-repo-replacements.txt --force
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

Then validate:

```powershell
git log -p --all | rg --pcre2 \"\\d{8,10}:[A-Za-z0-9_-]{35}\" -n
```

Expected result: no matches.

## Remote migration steps

1. Force-push rewritten branches and tags:
   - `git push --force --all`
   - `git push --force --tags`
2. Notify team to discard old clones.
3. Require fresh clone:
   - `git clone <repo-url>`

## Postmortem controls

- Enforce env-based config only.
- Keep `.env` ignored.
- Add CI security gates (`bandit`, `pip-audit`).
- Add pre-commit secret scanning in follow-up.

## Audit log placeholders

- Rotation timestamp: `TO_FILL_BY_OWNER`
- Rotated bot ids: `TO_FILL_BY_OWNER`
- Validation evidence location: `reports/audit/evidence/`
