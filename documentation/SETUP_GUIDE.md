# 🚀 Legal Q&A RAG System - Setup Guide

Complete guide to set up and run the Legal Q&A RAG System.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Important**: Never commit your `.env` file to version control!

### 2. Verify Configuration

Your `backend/.env` should contain:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Qdrant Configuration (these defaults work with Docker)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Vector Search Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
TOP_K_RESULTS=2
SIMILARITY_THRESHOLD=0.7

# LLM Configuration
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
MAX_TOKENS=500
```

## 🐳 Running with Docker (Recommended)

### One-Command Startup

From the project root directory:

```bash
docker-compose up --build
```

This will:
1. Start Qdrant vector database (ports 6333, 6334)
2. Start FastAPI backend (port 8000)
3. Start React frontend (port 3000)
4. Automatically load and index the 10 legal FAQs
5. Initialize the logging database

### First-Time Setup Notes

- **First run takes 2-3 minutes**: Docker needs to download images and install dependencies
- **FAQ indexing**: Backend automatically generates embeddings and indexes FAQs on first startup
- **Watch the logs**: You'll see "Application initialization complete!" when ready

### Access the Application

Once running, access:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### Stopping the Application

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## 💻 Local Development (Without Docker)

### Backend Setup

1. **Create Python virtual environment**:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start Qdrant** (using Docker):
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

4. **Configure environment**:
```bash
# Update backend/.env with:
QDRANT_HOST=localhost  # Change from 'qdrant' to 'localhost'
```

5. **Run backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Node.js dependencies**:
```bash
cd frontend
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Access frontend**: http://localhost:3000

## 🧪 Testing the System

### 1. Health Check

Visit: http://localhost:8000/api/health

Expected response:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "openai_configured": true,
  "faqs_loaded": 10
}
```

### 2. Try Sample Queries

Use these questions to test the system:

1. **Personal Injury**: "What is the statute of limitations for personal injury?"
2. **Contract Law**: "Can I break a contract without penalty?"
3. **Employment**: "What constitutes wrongful termination?"
4. **Property**: "What are my rights as a landlord to evict a tenant?"
5. **Criminal**: "What are my rights if I'm arrested?"

### 3. Verify Logging

Check the logs:
- Visit http://localhost:3000 and click "Show History"
- Or call the API: http://localhost:8000/api/logs

## 📊 System Architecture

```
┌──────────────────────────────────────────────────┐
│ User Browser (http://localhost:3000)             │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼ HTTP/REST API
┌──────────────────────────────────────────────────┐
│ FastAPI Backend (http://localhost:8000)          │
│  ┌────────────────────────────────────────┐     │
│  │ /api/ask  - Question answering         │     │
│  │ /api/logs - Interaction history        │     │
│  │ /api/health - System status            │     │
│  └────────────────────────────────────────┘     │
│                                                   │
│  ┌──────────────┐    ┌──────────────────┐       │
│  │ OpenAI API   │    │ Qdrant Vector DB │       │
│  │ - Embeddings │    │ - 10 FAQs stored │       │
│  │ - GPT-4      │    │ - Semantic search│       │
│  └──────────────┘    └──────────────────┘       │
│                                                   │
│  ┌──────────────────────────────────────┐       │
│  │ SQLite Database                       │       │
│  │ - Interaction logs                    │       │
│  │ - Query history                       │       │
│  └──────────────────────────────────────┘       │
└──────────────────────────────────────────────────┘
```

## 🔍 API Endpoints

### POST /api/ask

Submit a question and get AI-generated answer.

**Request**:
```json
{
  "query": "What is the statute of limitations?",
  "include_sources": true
}
```

**Response**:
```json
{
  "answer": "The statute of limitations varies by state...",
  "sources": [
    {
      "faq_id": "faq_001",
      "question": "What is the statute of limitations...",
      "answer": "...",
      "category": "Personal Injury",
      "similarity_score": 0.89
    }
  ],
  "response_time_ms": 1243,
  "timestamp": "2025-10-06T14:30:00Z"
}
```

### GET /api/logs

Retrieve interaction history.

**Query Parameters**:
- `limit` (optional): Number of logs to return (default: 50)

**Response**: Array of log entries

### GET /api/stats

Get system statistics.

**Response**:
```json
{
  "total_queries": 42,
  "avg_response_time_ms": 1250.5,
  "total_errors": 0,
  "faqs_in_database": 10
}
```

### GET /api/health

Health check endpoint.

## 🐛 Troubleshooting

### Port Already in Use

If ports 3000, 6333, or 8000 are already in use:

```bash
# Find and stop the process using the port (Windows)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or change ports in docker-compose.yml
```

### OpenAI API Errors

**Error**: "OpenAI API key not configured"
- **Solution**: Ensure your `.env` file has `OPENAI_API_KEY=sk-...`
- **Restart**: `docker-compose restart backend`

**Error**: "Rate limit exceeded"
- **Solution**: You've exceeded OpenAI's rate limits. Wait a few minutes.

**Error**: "Insufficient quota"
- **Solution**: Add credits to your OpenAI account.

### Qdrant Connection Failed

**Error**: "Failed to connect to Qdrant"
- **Solution**: Ensure Qdrant container is running: `docker ps | grep qdrant`
- **Restart**: `docker-compose restart qdrant`

### Frontend Can't Connect to Backend

**Error**: "Network Error" or "Failed to fetch"
- **Solution 1**: Verify backend is running: http://localhost:8000/api/health
- **Solution 2**: Check CORS settings in `backend/app/main.py`
- **Solution 3**: Clear browser cache and reload

### FAQs Not Loading

**Error**: "faqs_loaded: 0" in health check
- **Solution**: Delete Qdrant storage and restart:
  ```bash
  docker-compose down -v
  docker-compose up --build
  ```

### Database Errors

**Error**: "Failed to log interaction"
- **Solution**: Ensure `backend/data/` directory exists and is writable
- **Restart**: `docker-compose restart backend`

## 📝 Data Files

### FAQ Dataset

Location: `backend/app/data/legal_faqs.json`

Contains 10 legal FAQs across 5 categories:
- Personal Injury (2)
- Contract Law (2)
- Employment Law (2)
- Property Law (2)
- Criminal Law (2)

### Interaction Logs

Location: `backend/data/interactions.db` (created automatically)

SQLite database storing:
- User queries
- Retrieved FAQ IDs
- AI responses
- Response times
- Relevance scores

## 🔐 Security Notes

- **API Keys**: Never commit `.env` files to Git
- **Production**: Use proper authentication for production deployment
- **CORS**: Update CORS settings in `main.py` for production domains
- **Rate Limiting**: Implement rate limiting for production use

## 📈 Performance Expectations

- **Query Response Time**: 1-3 seconds
- **Embedding Generation**: ~200ms per query
- **Vector Search**: ~10-50ms
- **LLM Generation**: ~1-2 seconds
- **Concurrent Users**: System handles 10-20 concurrent users in current setup

## 🚀 Next Steps

After successful setup:

1. **Test sample queries** to verify the system works
2. **Review interaction logs** to see how queries are handled
3. **Experiment with different questions** to test retrieval accuracy
4. **Check API documentation** at http://localhost:8000/docs
5. **Review the code** to understand the RAG pipeline

## 💡 Tips for Best Results

- **Specific questions**: More specific questions get better retrieval results
- **Legal terminology**: Using proper legal terms improves matching
- **Question format**: Phrase queries as questions (e.g., "What is..." vs "statute of limitations")
- **Category awareness**: The system knows 5 legal categories - questions within these areas work best

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **OpenAI API Docs**: https://platform.openai.com/docs/

---

**Questions or Issues?** Check the troubleshooting section above or review the application logs for detailed error messages.
