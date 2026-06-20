# VentureIQ — AI-Powered Multi-Agent Startup Validator

> Validate your startup idea in 60 seconds using 7 specialized AI agents.

**Live Demo:** [https://ventureiq.onrender.com](https://ventureiq.onrender.com)

![VentureIQ](https://img.shields.io/badge/VentureIQ-Multi--Agent%20AI-blue?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Pipeline-6366f1?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge)
![Live](https://img.shields.io/badge/Live-ventureiq.onrender.com-success?style=for-the-badge)

---

## What is VentureIQ?

Every year, thousands of Indian founders waste months and lakhs of rupees building products nobody wants — simply because they skipped proper validation. Market research, competitor analysis, financial modeling, and risk assessment each take days when done manually.

**VentureIQ solves this in under 60 seconds.**

Submit your startup idea → 7 AI agents analyze it in parallel → get a definitive **GO / NO-GO verdict** with scores, insights, revenue projections, and a downloadable PDF report.

---

## Features

- **7 Specialized AI Agents** running in parallel via LangGraph
- **Real-time web search** via Tavily — grounded data, not stale model weights
- **GO / NO-GO Verdict** with overall score and confidence percentage
- **Revenue Projections** — Year 1/2/3 bar chart
- **Pivot Advisor** — if NO-GO, suggests 3 actionable pivot strategies automatically
- **Interactive AI Chat** — ask follow-up questions about your analysis
- **PDF Report** — professional, downloadable report for co-founders and investors
- **Live Agent Graph** — watch agents activate in real-time via ReactFlow

---

## Agent Pipeline

```
                    ┌─────────────────┐
                    │ Input Processor │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼                  ▼
  ┌───────────────┐  ┌──────────────┐  ┌────────────┐  ┌─────────────────┐
  │Market Research│  │  Competitors │  │ Financials │  │ Risk Assessment │
  └───────┬───────┘  └──────┬───────┘  └─────┬──────┘  └────────┬────────┘
          │                  │                │                   │
          └──────────────────┴────────────────┴───────────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │    Synthesizer      │
                                    └─────────┬──────────┘
                                              │
                              ┌───────────────┴──────────────┐
                              │  verdict == NO-GO?            │
                              ▼                               ▼
                    ┌──────────────────┐                    END
                    │  Pivot Advisor   │
                    └──────────────────┘
```

---

## Tech Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Backend   | FastAPI · LangGraph · LangChain · Python 3.11+  |
| Frontend  | React · Vite · Tailwind CSS · Framer Motion     |
| AI        | OpenRouter · meta-llama/llama-3.3-70b-instruct  |
| Search    | Tavily Web Search API                           |
| Graph UI  | ReactFlow                                       |
| Charts    | Recharts                                        |
| Streaming | WebSockets                                      |
| PDF       | ReportLab                                       |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenRouter API key → [openrouter.ai](https://openrouter.ai)
- Tavily API key → [tavily.com](https://tavily.com)

### 1. Clone the repo

```bash
git clone https://github.com/sachinn854/VentureIQ.git
cd VentureIQ
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENROUTER_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
MODEL_NAME=meta-llama/llama-3.3-70b-instruct
ALLOWED_ORIGIN=http://localhost:5173
```

Start backend:

```bash
uvicorn backend.main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### 4. Docker (optional)

```bash
docker-compose up --build
```

---

## Project Structure

```
startup-validator/
├── backend/
│   ├── agents/              # 7 AI agents
│   │   ├── input_processor.py
│   │   ├── market_research.py
│   │   ├── competitor_analysis.py
│   │   ├── financial_feasibility.py
│   │   ├── risk_assessment.py
│   │   ├── synthesizer.py
│   │   └── pivot_advisor.py
│   ├── graph/               # LangGraph pipeline
│   │   └── startup_graph.py
│   ├── schemas/             # Pydantic models
│   │   └── models.py
│   ├── security/            # Rate limiting + input sanitizer
│   ├── tools/               # Tavily search + calculator
│   ├── main.py              # FastAPI app + WebSocket + Chat
│   ├── pdf_generator.py     # ReportLab PDF export
│   └── config.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── IdeaInput.jsx
│       │   ├── AgentGraph.jsx
│       │   ├── StreamingPanel.jsx
│       │   ├── VerdictCard.jsx
│       │   ├── ChatPanel.jsx
│       │   └── ChatWidget.jsx
│       ├── hooks/
│       │   └── useWebSocket.js
│       └── utils/
│           └── stripMarkdown.js
└── docker-compose.yml
```

---

## API Reference

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/api/analyze`            | Start analysis, returns `run_id`   |
| WS     | `/ws/{run_id}`            | Real-time event stream             |
| POST   | `/api/chat/{run_id}`      | Ask questions about the analysis   |
| GET    | `/api/report/{run_id}/pdf`| Download PDF report                |
| GET    | `/health`                 | Health check                       |

---

## Built for FlowZint AI Hackathon 2026

**Category:** Open Innovation

VentureIQ democratizes startup validation — a capability previously accessible only to well-funded teams — and makes it available to any founder in India, regardless of resources, background, or location.

---

## License

MIT
