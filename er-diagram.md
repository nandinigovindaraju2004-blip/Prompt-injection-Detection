# ER Diagram

```
┌────────────────────────┐          ┌──────────────────────────────────┐
│         User            │          │            PromptLog                │
├────────────────────────┤          ├──────────────────────────────────┤
│ _id (ObjectId, PK)       │ 1     * │ _id (ObjectId, PK)                   │
│ username (unique)        │◄────────│ user (ObjectId, FK -> User._id)      │
│ email (unique)           │         │ username                             │
│ passwordHash              │         │ originalPrompt                       │
│ role: user|admin          │         │ sanitizedPrompt                      │
│ createdAt / updatedAt      │         │ verdict: safe|malicious              │
└────────────────────────┘          │ riskScore (0-100)                    │
                                       │ confidenceLevel                      │
                                       │ ruleScore                            │
                                       │ mlScore                              │
                                       │ attackCategories [String]            │
                                       │ explanation                          │
                                       │ aiResponse                           │
                                       │ ipAddress                            │
                                       │ detectionTimeMs                      │
                                       │ createdAt / updatedAt                │
                                       └──────────────────────────────────┘
```

**Relationship:** One `User` has many `PromptLog` documents (1:N), referenced via
`PromptLog.user`. Indexes exist on `createdAt`, `verdict`, and `user` to keep dashboard
aggregation queries fast as log volume grows.

## Notes on schema choices

- `attackCategories` is an array because a single prompt can trigger multiple rule
  categories at once (e.g. an instruction-override attack that also contains a prompt-leakage
  phrase).
- `ruleScore` and `mlScore` are stored separately (not just the blended `riskScore`) so the
  admin dashboard / research analysis can evaluate each detector's standalone accuracy over
  time — this is what powers the "detection accuracy report" deliverable.
- `sanitizedPrompt` is only populated when `verdict === "malicious"`; `aiResponse` is only
  populated when `verdict === "safe"` — the two are mutually exclusive by design (a malicious
  prompt is never forwarded to the LLM).
