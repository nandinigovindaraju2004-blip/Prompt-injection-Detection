# Roadmap: Turning stretch features into working code

This project already implements the core spec end-to-end. Below is concretely how to build
each "2026 novel" feature on top of what exists — not just a wishlist.

## 1. Adaptive learning from new attacks
- `PromptLog` already stores every prompt + verdict + score. Write a scheduled job
  (`node-cron` in `server/`, or a separate script) that:
  1. Exports recent logs where an admin has manually corrected a verdict (add a
     `humanReviewed` / `correctedLabel` field to `PromptLog`).
  2. Appends them to `dataset/prompts.csv`.
  3. Re-runs `notebooks/train_model.py`.
  4. Hot-swaps `server/ml/model_artifacts/*.joblib` (the Node subprocess reloads them on
     every call already, since `predict.py` loads from disk each invocation).

## 2. Multilingual detection
- Swap the TF-IDF vectorizer for a multilingual sentence embedding model (e.g.
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) and a lightweight classifier
  (Logistic Regression on embeddings, or a small MLP) — the `predict.py` interface (prompt in,
  `{label, confidence, ml_score}` out) doesn't need to change, only its internals.
- Add translated rule variants or use a language-agnostic approach: translate the incoming
  prompt to English (via a translation API) before running the existing rule engine, logging
  the detected source language.

## 3. RAG-specific attack detection
- Current stub: the `rag_injection` rule in `ruleEngine.js` matches the literal phrase
  "retrieved context". Real implementation: expose a second detection entrypoint,
  `detectPromptInjection(userPrompt, retrievedChunks)`, that runs the same rule+ML pipeline
  against each retrieved chunk *before* it's concatenated into the LLM context — this catches
  injection payloads planted in documents/websites the RAG pipeline pulls in, not just what
  the user typed.

## 4. Continuous retraining
- Same mechanism as (1), but scheduled unconditionally (e.g. weekly) rather than only on
  human-corrected labels — retrain on the full accumulated `PromptLog` corpus, holding out a
  validation split, and only promote the new model if its held-out F1 beats the current one
  (store `metadata.json`'s accuracy per version, compare before swapping).

## 5. Confidence-calibrated risk scoring
- Already implemented: `confidenceLevel` in `detectionEngine.js`. To go further, replace the
  hand-picked thresholds with a calibrated probability (e.g. `sklearn.calibration.
  CalibratedClassifierCV`) so "confidence" has a rigorous statistical meaning rather than a
  bucketed heuristic.

## 6. Production-grade ML serving
- Replace the per-request `python3 predict.py` subprocess (`server/services/mlEngine.js`)
  with a persistent FastAPI/Flask microservice loaded once at startup, called over HTTP with
  a connection pool — removes ~50-100ms of Python interpreter startup latency per request.
