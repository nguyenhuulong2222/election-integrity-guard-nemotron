## Integrity incident

> FICTIONAL DEMO. This template is used by people, by the Duo integrity flow (BLOCK findings), and by the scheduled monitor job (live-site drift).

**Detected by:** (Duo integrity flow / monitor job / person)
**Related MR or pipeline:**
**Severity:** BLOCK / WARN

### What was found

<!-- The finding as reported by the checker, in plain language. -->

### Public impact if published

<!-- For example, "voters would be sent to a lookalike polling-place lookup site". -->

### Response checklist

- [ ] Confirm the finding by hand
- [ ] If the live site is affected, redeploy the last known-good `main` commit
- [ ] Rotate credentials if a compromised account is suspected
- [ ] Notify the communications lead before posting any public correction
- [ ] Record the root cause and close with a link to the fix MR

/label ~"integrity-incident"
