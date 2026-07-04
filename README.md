# Prompt Injection Detection
## What's implemented

| Module | Status |
|---|---|
| JWT auth (register/login/bcrypt/profile) | ✅ |
| Prompt submission + history + search + filters | ✅ |
| Rule-based detection engine (15 attack patterns, 10 categories) | ✅ |
| ML classifier (TF-IDF + Logistic Regression, trained model included) | ✅ |
| Hybrid risk scoring (0-100) with dominance logic | ✅ |
| Explainable AI output (why a prompt was flagged) | ✅ |
| Prompt sanitizer (mask/strip/redact) | ✅ |
| OpenAI GPT integration (only called on Safe verdict) | ✅ |
| Analytics dashboard (totals, daily attacks, categories, risk distribution) | ✅ |
| CSV + PDF report export | ✅ |
| Full-text logging (prompt, sanitized prompt, risk, category, time, user, IP) | ✅ |
| Dark mode, responsive UI | ✅ |
| Unit tests for detection engine | ✅ |
| Random Forest model (trained + compared against Logistic Regression) | ✅ |
| Confidence levels (low/medium/high/very high) | ✅ |

### Extension points (see `docs/ROADMAP.md`)
- Adaptive learning loop (retrain on newly logged attacks)
- Multilingual detection (swap TF-IDF for multilingual embeddings)
- RAG-specific injection detection (dedicated rules + retrieval-context scanning already
  stubbed in `ruleEngine.js` under `rag_injection` — extend with real vector-store hooks)
- DistilBERT/transformer classifier as a drop-in replacement for the sklearn model
- Continuous retraining pipeline (cron job calling `notebooks/train_model.py` against
  `PromptLog` data exported to CSV)

---

## Architecture

```
Browser (Next.js/React/Tailwind)
        │  REST (JWT bearer)
        ▼
Express API  ──►  MongoDB (users, prompt logs)
    │
    ├─► ruleEngine.js        (regex pattern library, instant)
    ├─► mlEngine.js  ──►  Python (TF-IDF + LogisticRegression) via subprocess
    ├─► detectionEngine.js   (blends rule + ML scores → risk score + verdict)
    ├─► sanitizer.js         (masks/strips malicious spans)
    └─► openaiService.js     (called only if verdict === "safe")
```

Full diagram: `docs/architecture.md`. ER diagram: `docs/er-diagram.md`.

---

## Quick start

### 1. Train the ML model (already trained artifacts are included, but to retrain)
```bash
pip install scikit-learn pandas numpy joblib --break-system-packages
python3 notebooks/train_model.py
```

### 2. Backend
```bash
cd server
cp .env.example .env        # fill in MONGO_URI, JWT_SECRET, OPENAI_API_KEY
npm install
npm run dev                 # http://localhost:5000
```
Requires a running MongoDB instance (local or MongoDB Atlas) and `python3` with the
`scikit-learn`/`joblib` packages available on PATH for the ML subprocess call.

### 3. Frontend
```bash
cd client
cp .env.example .env.local
npm install
npm run dev                 # http://localhost:3000
```

### 4. Run tests
```bash
cd server
npx jest
```

---

## API summary

| Method | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT |
| GET | `/api/auth/profile` | Current user |
| POST | `/api/prompts` | Submit + analyze a prompt |
| GET | `/api/prompts` | History (search/filter/paginate) |
| GET | `/api/prompts/:id` | Single log detail |
| GET | `/api/dashboard/summary` | Totals + detection rate |
| GET | `/api/dashboard/daily-attacks` | Time series |
| GET | `/api/dashboard/attack-categories` | Category breakdown |
| GET | `/api/dashboard/risk-distribution` | Risk score histogram |
| GET | `/api/reports/csv` | CSV export |
| GET | `/api/reports/pdf` | PDF export |

Full API docs: `docs/api-documentation.md`.

---

## Tech stack (as specified)

Frontend: Next.js, React, Tailwind, (JS by default — add `tsconfig.json` to switch to TS)
Backend: Node.js, Express
Database: MongoDB (Mongoose)
ML: Python, scikit-learn, pandas, numpy (TF-IDF + Logistic Regression + Random Forest)
Auth: JWT + bcrypt
Visualization: Recharts
AI: OpenAI GPT API

## Research contribution

This project's hybrid design — rule-based detection for known attack signatures blended
with a statistical ML classifier for generalization to novel/paraphrased attacks, combined
with explainable per-category output and confidence-scored verdicts — is the basis for the
paper outline in `docs/research-contribution.md`.

## Deployment

See `docs/deployment-guide.md` for Vercel (frontend) + Render (backend) + MongoDB Atlas
instructions.
