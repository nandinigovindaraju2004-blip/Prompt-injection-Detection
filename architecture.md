# System Architecture

## High-level flow

```
┌─────────────┐     JWT Bearer      ┌──────────────────┐
│  Next.js UI │ ──────────────────► │   Express API     │
│ (client/)   │ ◄────────────────── │   (server/)        │
└─────────────┘      JSON            └──────────┬─────────┘
                                                  │
                     ┌────────────────────────────┼─────────────────────────┐
                     ▼                             ▼                         ▼
             ┌───────────────┐           ┌──────────────────┐      ┌─────────────────┐
             │  ruleEngine.js │           │  mlEngine.js       │      │  MongoDB          │
             │  (regex rules) │           │  (spawns Python)   │      │  users, promptlogs │
             └───────┬────────┘           └─────────┬─────────┘      └─────────────────┘
                     │                                │
                     └──────────────┬─────────────────┘
                                     ▼
                          ┌────────────────────┐
                          │ detectionEngine.js  │
                          │ risk score + verdict│
                          └──────────┬──────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                                 ▼
             verdict = malicious                verdict = safe
                     │                                 │
                     ▼                                 ▼
             ┌───────────────┐                ┌─────────────────┐
             │ sanitizer.js   │                │ openaiService.js │
             │ mask/strip     │                │ call OpenAI API   │
             └───────────────┘                └─────────────────┘
```

## Why a hybrid detector?

- **Rule engine**: near-zero latency, 100% explainable ("matched pattern X"), but brittle —
  attackers can paraphrase around fixed regexes.
- **ML classifier**: generalizes to novel phrasing the rules haven't seen, but is a black box
  and needs labeled data to stay current.
- **Blend**: `detectionEngine.js` averages both scores (50/50) but has a *dominance rule* — if
  either signal is very confident (rule ≥ 80, or ML ≥ 90), that signal alone can push the
  final score to block, so a confident detector is never diluted by a weak one.

## Process boundary: Node ↔ Python

For this project's scale, `mlEngine.js` spawns a short-lived `python3 predict.py <prompt>`
process per request and reads its JSON stdout. This avoids running two long-lived servers for
a student/demo project. For production traffic, replace this with a persistent Flask/FastAPI
microservice (`server/ml/predict_service.py` — stub described in ROADMAP.md) called over HTTP
with connection pooling, so you're not paying Python interpreter startup cost per request.

## Data flow for a single prompt submission

1. Client POSTs `{ text }` to `/api/prompts` with `Authorization: Bearer <jwt>`.
2. `authenticate` middleware verifies the JWT, attaches `req.user`.
3. `promptController.submitPrompt` calls `detectPromptInjection(text)`.
4. That function runs `runRuleEngine` (sync, regex) and `runMlClassifier` (async, subprocess)
   concurrently — well, sequentially awaited but each is fast (~50-150ms for the Python call).
5. Risk score + verdict computed.
6. If malicious → `sanitizePrompt` produces a redacted version; OpenAI is **never called**.
7. If safe → `getAiResponse` calls OpenAI Chat Completions and returns the answer.
8. Everything is persisted to `PromptLog` (original text, sanitized text, scores, categories,
   explanation, AI response, IP, latency).
9. Response returned to client; UI renders the risk bar, category chips, explanation, and
   either the sanitized prompt or the AI response.
