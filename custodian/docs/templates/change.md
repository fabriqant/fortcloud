# Change record — template

Copy this file for each restricted-environment change. The pipeline's evidence link should point to the stored record.

## Change

- **Pipeline:** `pipe-...`
- **Environment:** `prod`
- **Owner:** team
- **Date:** YYYY-MM-DD
- **Summary:** what changed and why

## Controls

- [ ] Reviewed by at least 2 approvers; names or review link: ...
- [ ] Unit tests passed: link
- [ ] Integration tests passed: link
- [ ] Security test passed: link
- [ ] Deployer identity scoped to this environment: `ci-...`
- [ ] Secrets referenced, not embedded; rotation current
- [ ] Audit entry written to the declared immutable sink: link

## Rollback

- **Target:** previous-release
- **Automated:** yes
- **Last drill:** YYYY-MM-DD
- **Rollback evidence:** link

## Verification

```bash
fortcloud-custodian check --strict --out ./artifacts
```

- [ ] Exit code 0
- [ ] `change-control.md` and `audit-trail.md` attached to the change record
