# Legal Q&A RAG System

A lightweight Retrieval-Augmented Generation (RAG) system for answering legal FAQs using OpenAI and vector search.

## Features

- 🔍 Semantic search over legal FAQs using vector embeddings
- 🤖 AI-generated contextual answers using OpenAI GPT
- 📊 Interaction logging for review and analytics
- 🐳 Fully containerized with Docker
- ⚡ Fast API backend with async support
- 💻 Clean React frontend with Tailwind CSS

## Architecture

```
Frontend (React) → Backend (FastAPI) → Vector DB (Qdrant) + OpenAI API
                         ↓
                   Interaction Logs (SQLite)
```

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Vector Database**: Qdrant
- **AI/ML**: OpenAI (Embeddings + GPT-4)
- **Logging**: SQLite
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd RAG-System
```

2. Configure environment variables
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
```

3. Start all services
```bash
docker-compose up --build
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
RAG-System/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── config.py    # Configuration management
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   ├── api/         # API routes
│   │   └── data/        # FAQ dataset
│   └── requirements.txt
├── frontend/            # React application
│   └── src/
├── docker-compose.yml   # Service orchestration
└── README.md
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/ask` - Submit a question and get AI-generated answer
- `GET /api/logs` - Retrieve interaction history
- `GET /api/health` - System health check

## License

MIT
