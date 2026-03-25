# Flow Evolution Engine (HyperAgent Demo)

Complete full-stack demo application that ingests PDF/text, extracts decision flows with an LLM, visualizes and executes flows, evaluates output quality, and evolves better versions over time.

## Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, Python
- **Frontend**: React (Vite), Tailwind CSS, Axios, React Flow, Chart.js
- **LLM**: Ollama-compatible API
  - `OLLAMA_URL=http://ollama-mobius-sales.mobiusdtaas.ai/`
  - `OLLAMA_MODEL=llama3:instruct`

## Project Structure

```text
flow-evolution-engine/
  backend/
    app/
      main.py
      db.py
      models.py
      schemas.py
      services/
        ingestion_service.py
        extraction_service.py
        execution_engine.py
        evaluation_engine.py
        evolution_engine.py
        ollama_client.py
    main.py
  frontend/
    src/
      App.jsx
      pages/
        Dashboard.jsx
        FlowViewer.jsx
        Evolution.jsx
      components/
        UploadBox.jsx
        FlowGraph.jsx
        ExecutionPanel.jsx
        EvolutionChart.jsx
      services/api.js
```

## Backend Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

API docs: `http://localhost:8000/docs`

### Backend Endpoints

- `POST /ingest` (PDF/text upload)
- `POST /extract-flow`
- `POST /execute-flow`
- `POST /evaluate`
- `POST /evolve`
- `GET /flows`
- `GET /best-flow`
- `GET /evolution-log`

## Frontend Run

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Set backend base URL if needed:

```bash
VITE_API_BASE=http://localhost:8000
```

## HyperAgent Loop

1. Ingest PDF/text
2. Extract decision flow via LLM
3. Visualize as graph
4. Execute flow on scenario
5. Evaluate performance
6. Evolve flow to next version
7. Track score improvements in evolution chart/log
