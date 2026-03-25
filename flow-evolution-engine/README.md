# HyperAgent Flow Evolution System

A true HyperAgent-style full-stack loop:

**GENERATE VARIANTS → EXECUTE → EVALUATE → SELECT BEST → MUTATE → REPEAT**

## Key Capabilities

- Multi-variant generation (A/B/C per version group)
- Competitive execution and scoring across all variants
- **Strict selection pressure**: only top-1 or top-2 survive, all others discarded
- Winner-driven mutation into next generation (non-linear, winner-parented)
- **Diversity in mutation**: each evolution creates exactly 3 children per winner:
  - conservative
  - aggressive
  - hybrid
- **Meta-evolution layer** that learns and biases future prompts using:
  - mutation strategy effectiveness
  - structure patterns from winning flows
  - prompt strategy quality

## Backend (FastAPI + SQLite)

### Data model

- `flows`: `id`, `version_group`, `variant_id`, `parent_id`, `score`, `mutation_type`, `flow_json`
- `evaluations`: `flow_id`, `score`, `signals_json`
- `evolution_history`: `parent_flow`, `child_flow`, `mutation_type`, `performance_delta`
- `meta_learning`: `mutation_type`, `avg_score`, `success_rate`, `wins`, `trials`

### API endpoints

- `POST /ingest`
- `POST /generate-variants`
- `POST /run-competition`
- `POST /select-winners`
- `POST /evolve-winners`
- `GET /flows`
- `GET /flows/{version_group}`
- `GET /best-flow`
- `GET /evolution-history`
- `GET /mutation-insights`
- `GET /meta-learning`

## LLM config

- `OLLAMA_URL=http://ollama-mobius-sales.mobiusdtaas.ai/`
- `OLLAMA_MODEL=llama3:instruct`

## Run

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set API if needed:

```bash
VITE_API_BASE=http://localhost:8000
```
