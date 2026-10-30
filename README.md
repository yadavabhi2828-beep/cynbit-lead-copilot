# Cynbit Lead-to-Proposal AI Copilot

> AI/ML Engineer Intern assessment - *Identify an AI Opportunity for Cynbit* · Abhishek Yadav

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yadavabhi2828-beep/cynbit-lead-copilot/blob/main/demo.ipynb)

An AI copilot that turns an inbound enquiry into a **qualified, routed, evidence-grounded first response** in seconds, with a human approving every message.

```
Lead → Extract → Score → Retrieve → Draft → Human review → CRM / reply
        rules+LLM  rubric   TF-IDF     template/LLM + guardrails
```

## Deliverables

| Required deliverable | Where |
|---|---|
| AI Opportunity Report | [`docs/01_AI_Opportunity_Report.md`](docs/01_AI_Opportunity_Report.md) |
| AI/ML Proof of Concept | this repo - `app.py` (Streamlit), `api.py` (FastAPI), `copilot/` (library) |
| Interactive Demo (Colab) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yadavabhi2828-beep/cynbit-lead-copilot/blob/main/demo.ipynb) · [`demo.ipynb`](demo.ipynb) |
| Technical Approach Report | [`docs/02_Technical_Approach_Report.md`](docs/02_Technical_Approach_Report.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |

## Why this opportunity
Cynbit's revenue starts with enquiries (service discovery, product demos, BitElevate, careers). Triage, fit-checking and tailored replies are manual and repetitive. The copilot automates that first mile while keeping humans in control. Full reasoning and the six-option comparison are in the Opportunity Report.

## Features
- **Intent & routing**: new project, product demo, training, career, vendor pitch, spam, unclear → sales / product team / BitElevate / HR / ignore.
- **Extraction**: service line, industry, budget (₹, $, lakh/crore, ranges), timeline/urgency, requirements; English and Hinglish.
- **Explainable score** (0-100) with five components, tier (HOT/WARM/COLD) and response SLA.
- **Grounded retrieval** over Cynbit's public services, products, program and 13 case studies.
- **Draft reply + discovery questions**, every claim traceable to retrieved evidence.
- **Guardrails**: untrusted-input handling, no invented numbers/ids/guarantees, automatic template fallback.
- **Works with no API key** (offline mode); optional Anthropic or OpenAI refinement.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                 # demo UI
uvicorn api:app --reload             # API docs at http://127.0.0.1:8000/docs
pytest -q                            # 40 tests
python eval/run_eval.py              # evaluation -> eval/RESULTS.md
```
Optional LLM mode: `cp .env.example .env`, add a key, `pip install anthropic` (or `openai`). `LLM_PROVIDER=auto` uses whichever key is present.

```bash
curl -X POST http://127.0.0.1:8000/v1/triage -H "Content-Type: application/json" \
  -d '{"name":"Priya","company":"MediCore","email":"priya@medicore.in","message":"Need an AI assistant for appointment reminders, budget ₹8 lakhs, within 6 weeks. Please send a proposal."}'
```

## Evaluation (offline baseline, synthetic data)
| Set | n | Intent | Tier | Service line | Retrieval hit |
|---|---|---|---|---|---|
| Dev | 17 | 1.00 | 1.00 | 1.00 | 1.00 |
| Held-out (harder) | 10 | 0.50 | 0.60 | 0.50 | 0.60 |

The dev set was written while building the rules, so it is a regression guard. The held-out result is the honest estimate (tiny n) and shows where keyword rules fail; the LLM refinement stage targets those cases but has **not** been measured here. Details: Technical Approach §6.

## Project structure
```
copilot/      schemas, extract, score, knowledge (retrieval), draft, llm, pipeline, utils
data/         knowledge/*.json (curated from cynbit.in), sample_leads.json, holdout_leads.json
app.py        Streamlit UI (single lead + batch triage)
api.py        FastAPI service
tests/        pytest suite      eval/   evaluation harness and RESULTS.md
docs/         reports and architecture
```

## Deploy the demo
Push to GitHub → [share.streamlit.io](https://share.streamlit.io) → select repo, branch `main`, file `app.py`. No secrets needed for offline mode; add `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` in the app's Secrets to enable LLM mode.

## Limitations
Synthetic leads; no access to Cynbit's CRM or pricing; case studies use headline text only; website figures are company-reported. See the reports for the full list and roadmap.

## Data & attribution
Knowledge base compiled by hand from public pages of https://www.cynbit.in on 30 Oct 2026 (see `data/knowledge/SOURCES.md`). This is an independent assessment submission, not an official Cynbit product.
