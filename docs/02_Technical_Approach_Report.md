# Technical Approach Report - Lead-to-Proposal AI Copilot

## 1. Scope
Input: one inbound enquiry (`name, company, email, message`). Output: structured understanding, score/tier/route/SLA, grounding evidence, a draft reply and discovery questions, plus a stage trace. Delivered as a Python package, Streamlit app, FastAPI endpoint and tests.

## 2. Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for diagrams. Four stages: **Extract → Score → Retrieve → Draft**, orchestrated by `LeadCopilot.process()`.

## 3. Data pipeline

| Data | Source | Handling |
|---|---|---|
| Knowledge base (12 services, 3 products, 1 program, 13 case studies, 1 process) | Public cynbit.in pages, curated by hand into JSON (`data/knowledge/`) | Each entry has `id, type, title, description, tags, url`; `SOURCES.md` records provenance. Tags are retrieval keywords, not claims. |
| Leads | 27 synthetic enquiries (`data/sample_leads.json` dev set, `data/holdout_leads.json` held-out set) with expected labels | Cover project, product demo, training, career, vendor, spam, unclear, Hinglish, prompt-injection |
| Runtime leads | Form/webhook/e-mail | Validated by Pydantic; max 4,000 characters; PII masked in logs |

Retrieval index: TF-IDF (unigram+bigram, sublinear tf, English stop words) over `title ×2 + description + tags`; cosine similarity via `linear_kernel`. Offers (services/products/program) and case studies are searched separately so the draft always mixes capabilities and proof.

## 4. Model and method choices

| Decision | Choice | Rationale | Alternative considered |
|---|---|---|---|
| Numeric extraction (budget, timeline) | Regex rules | Exact, testable, free; handles ₹/$/lakh/crore, ranges, Hinglish cues | LLM extraction - less reliable on numbers |
| Intent & service line | Keyword rules, **optionally refined by an LLM** | Works offline; LLM adds robustness to unusual phrasing | Fine-tuned classifier - needs labelled history Cynbit has not shared |
| Scoring | Deterministic weighted rubric (budget 25, urgency 20, specificity 20, intent strength 20, contact quality 15) + budget-floor rule | Explainable, auditable, injection-proof | Learned model - revisit with won/lost data |
| Retrieval | TF-IDF | Small corpus, exact product names matter, zero cost, no external service | Dense embeddings + reranker - planned upgrade, easy to swap behind `KnowledgeBase.search` |
| Drafting | Template offline; LLM (Anthropic or OpenAI, low temperature) when a key exists | Always functional; better prose when available | Fully LLM - fragile without guardrails |
| Framework | Plain Python + Pydantic | Small, readable, no heavy orchestration needed for four steps | LangChain/LlamaIndex - consistent with Cynbit's stack, adds weight not value at this size |

Tier thresholds: HOT ≥ 65, WARM 40-64, COLD < 40; budgets below ₹25,000 are capped at COLD; careers/vendors/spam are `NOT_A_PROSPECT` and get no sales draft.

## 5. Prompt engineering and safety

Two prompts (`copilot/extract.py`, `copilot/draft.py`):

1. **Extraction prompt** - role + closed label sets + JSON-only output. The lead is wrapped in `<lead>` tags and declared *untrusted data*. The result may overwrite only semantic fields; budget and urgency stay rule-based.
2. **Drafting prompt** - role, hard rules (use only `<context>`, no prices/promises/invented metrics, <170 words, reply in the lead's language, ≤2 citations), JSON schema with `cited_ids`.

Guardrails applied to every LLM draft (`check_guardrails`):
- cited ids must be a subset of retrieved ids;
- any currency amount or percentage/multiplier must already appear in the lead text or retrieved evidence;
- "guarantee" language is rejected; length is capped;
- on any violation, or invalid JSON, or API error, the system **falls back to the template draft** and records why.

Additional controls: untrusted-input delimiting; score decided by code; every draft marked `requires_human_review`; PII masking utility for logs.

## 6. Evaluation

`python eval/run_eval.py` runs the deterministic baseline (no LLM) on two synthetic sets. Results are in `eval/RESULTS.md`.

| Set | n | Intent acc. | Tier acc. | Service-line acc. | Retrieval hit-rate |
|---|---|---|---|---|---|
| Dev (written while designing rules) | 17 | 1.00 | 1.00 | 1.00 | 1.00 |
| Held-out (harder, written beforehand) | 10 | 0.50 | 0.60 | 0.50 | 0.60 |

**Interpretation.** The dev score is a regression guard, not evidence of accuracy. The held-out result is the honest estimate (with n=10 it is only indicative). Error analysis of the misses: vague phrasing without service keywords ("fix scaling on our servers", "payment gateway integration failing"), a vendor pitch that also contained a request-like phrase ("Do you need any resources"), and a product enquiry that did not name the product ("monitor reviews across Google"). These are exactly the cases the LLM refinement stage targets; **I could not measure that improvement because no API key was available in the build environment** - the next step is to run the same harness with `LLM_PROVIDER=anthropic|openai`. Production evaluation should use Cynbit's real, human-labelled inbox, tracking tier accuracy, routing accuracy, draft acceptance rate and edit distance.

Unit/integration tests (40, `pytest -q`): parsing, regression on the dev set, determinism, injection resistance, budget floor, retrieval, guardrail rejection, LLM fallback, PII masking, API.

## 7. Execution plan

| Phase | Duration | Deliverable | Exit criterion |
|---|---|---|---|
| 0. Assessment build (this repo) | 1 day | Working PoC, tests, reports | Runs offline end-to-end |
| 1. Data & baseline | Week 1 | Export 300-500 past enquiries from the inbox/CRM; label intent, tier, outcome; refresh KB with full case-study pages | Baseline accuracy measured on real data |
| 2. LLM refinement & tuning | Week 2 | Run harness with chosen provider; tune thresholds/weights; add Hinglish tests | ≥ target accuracy on held-out real data |
| 3. Shadow pilot | Weeks 3-4 | Copilot runs on live leads, sales team sees suggestions but replies manually | Draft acceptance and time-to-reply measured |
| 4. Assisted production | Weeks 5-6 | Website-form webhook → API → CRM task + draft in inbox; feedback buttons | HOT-lead SLA compliance improves vs baseline |
| 5. Learn & expand | Ongoing | Learn weights from won/lost; embeddings + reranker; website assistant reusing the KB | Quarterly review of KPIs |

Cost note: offline mode costs nothing; in LLM mode each lead needs two short calls, so spend scales linearly with enquiry volume and is small relative to one hour of staff time (verify with the chosen provider's current pricing).

## 8. Limitations and future work
- Rule-based intent is brittle on novel phrasing (see §6); LLM stage mitigates but is unmeasured here.
- Synthetic data only; thresholds are judgement-based.
- Case-study text is headline-level; ingest full pages for richer grounding.
- Single-turn: no follow-up conversation handling or e-mail threading.
- Planned: dense retrieval + reranker, feedback loop, learned scoring, CRM connectors, multilingual evaluation, bias review of free-mail/company signals.
