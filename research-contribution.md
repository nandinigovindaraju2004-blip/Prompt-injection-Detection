# Research Contribution Outline

**Working title:** A Hybrid Rule-Based and Machine-Learning Framework for Explainable Prompt
Injection Detection in Large Language Model Applications

## Abstract sketch
Prompt injection remains one of the top security risks for LLM-integrated applications
(OWASP LLM Top 10, #1 as of 2024-2025). Purely rule-based filters are precise but brittle to
paraphrase; purely ML-based filters generalize but lack explainability and require large
labeled corpora. We propose a hybrid detector that blends a curated regex rule library with a
TF-IDF + Logistic Regression classifier, combined via a dominance-weighted score, and paired
with category-level explanations and confidence levels.

## Contributions claimed
1. A hybrid scoring function (see `server/services/detectionEngine.js`) that avoids the
   "weak signal dilution" problem of naive averaging.
2. A 10-category attack taxonomy (instruction override, prompt leakage, role override,
   jailbreak, hidden instruction, data extraction, tool manipulation, context poisoning, RAG
   injection, encoding evasion) usable as a labeling schema for future datasets.
3. An explainability layer that reports *which* rule matched and *why*, rather than a bare
   Safe/Malicious label — directly addressing a common critique of ML-only filters.
4. A logged dataset schema (`PromptLog`) designed to support continuous retraining
   (adaptive learning) as new attacks are observed in production.

## Evaluation plan (for the paper)
- Expand `dataset/prompts.csv` (currently a small seed set) to a few thousand labeled
  examples — mix public jailbreak/prompt-injection datasets (e.g. from HuggingFace) with your
  own collected samples.
- Report precision/recall/F1 for: rules only, ML only, hybrid.
- Ablation: measure how much the "dominance rule" changes accuracy vs. plain averaging.
- Latency benchmark: rule engine vs. ML subprocess vs. combined pipeline.
- (Stretch) Compare TF-IDF+LogReg against a DistilBERT fine-tune on the same dataset.

## Honest limitations to disclose
- The regex rule set is hand-curated and English-centric; multilingual attacks will evade it
  until rules/embeddings are extended (see ROADMAP.md).
- The ML classifier's seed dataset here is small (~50 rows) for demonstration; a credible
  research result needs a substantially larger, more diverse labeled corpus.
- RAG-specific injection detection currently only pattern-matches the phrase "retrieved
  context" — a production version needs to actually scan retrieved documents, not just the
  user's literal prompt text.
