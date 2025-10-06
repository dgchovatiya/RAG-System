# 🏗️ Architecture Documentation

Technical architecture and design decisions for the Legal Q&A RAG System.

## System Overview

This system implements a **Retrieval-Augmented Generation (RAG)** pipeline that combines:

1. **Vector database** for semantic search (Qdrant)
2. **Embedding model** for text-to-vector conversion (OpenAI)
3. **Large Language Model** for answer generation (GPT-4)

## Architecture Layers

### 1. Frontend Layer (React)

**Technology**: React 18 + Vite + Tailwind CSS

**Components**:

```
src/
├── App.jsx                    # Main application component
├── components/
│   ├── QueryInput.jsx        # Question submission form
│   ├── ResponseDisplay.jsx   # AI answer display
│   ├── SourceFAQs.jsx        # Retrieved FAQ sources
│   ├── InteractionLog.jsx    # Query history sidebar
│   └── LoadingSpinner.jsx    # Loading state indicator
└── services/
    └── api.js                # Backend API communication
```

**Key Design Decisions**:

- **Component-based architecture**: Modular, reusable UI components
- **Tailwind CSS**: Utility-first styling for rapid development
- **Axios for HTTP**: Clean API abstraction layer
- **State management**: React hooks (useState, useEffect) - sufficient for MVP scale

### 2. Backend Layer (FastAPI)

**Technology**: FastAPI + Python 3.11

**Structure**:

```
app/
├── main.py                   # Application entry point
├── config.py                 # Configuration management
├── models/
│   ├── schemas.py           # Pydantic data models
│   └── database.py          # SQLite interaction logging
├── services/
│   ├── embeddings.py        # OpenAI embedding service
│   ├── retrieval.py         # Qdrant vector search
│   └── generation.py        # LLM answer generation
├── api/
│   └── routes.py            # API endpoint handlers
└── data/
    └── legal_faqs.json      # FAQ dataset
```

**Key Design Decisions**:

- **Async/await**: All I/O operations are async for better performance
- **Dependency injection**: Settings loaded once and cached
- **Pydantic validation**: Automatic request/response validation
- **Service layer pattern**: Clear separation of concerns
- **Error handling**: Graceful degradation with fallback responses

### 3. Data Layer

#### Vector Database (Qdrant)

**Purpose**: Store and search FAQ embeddings

**Configuration**:

- **Distance metric**: Cosine similarity
- **Vector dimension**: 1536 (OpenAI text-embedding-3-small)
- **Collection**: `legal_faqs`

**Data Flow**:

```
FAQ Text → OpenAI Embedding API → 1536-dim Vector → Qdrant Storage
                                                           ↓
User Query → Embedding → Vector Search → Top 2 Similar FAQs
```

#### Interaction Logs (SQLite)

**Purpose**: Store query history for review and analytics

**Schema**:

```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_query TEXT NOT NULL,
    retrieved_faq_ids TEXT NOT NULL,      -- JSON array
    ai_response TEXT NOT NULL,
    response_time_ms INTEGER NOT NULL,
    relevance_scores TEXT NOT NULL,       -- JSON array
    error_occurred BOOLEAN DEFAULT FALSE
);
```

## RAG Pipeline Flow

### End-to-End Request Flow

```
1. User submits question
         ↓
2. Frontend → POST /api/ask
         ↓
3. Backend: Generate query embedding
         ↓ (OpenAI API call ~200ms)
4. Backend: Search Qdrant for similar FAQs
         ↓ (Vector search ~10-50ms)
5. Backend: Retrieve top 2 FAQs above similarity threshold (0.7)
         ↓
6. Backend: Build prompt with context
         ↓
7. Backend: Call OpenAI GPT-4 for answer generation
         ↓ (LLM API call ~1-2s)
8. Backend: Log interaction to SQLite
         ↓
9. Backend: Return response to frontend
         ↓
10. Frontend: Display answer + sources
```

### Detailed Component Interactions

#### 1. Embedding Service (`embeddings.py`)

**Responsibility**: Convert text to vector embeddings

```python
Input: "What is the statute of limitations?"
       ↓
OpenAI API: text-embedding-3-small
       ↓
Output: [0.123, -0.456, 0.789, ..., 0.234]  # 1536 dimensions
```

**API Usage**:

- **Cost**: $0.00002 per 1K tokens (~$0.02 for 1000 FAQs)
- **Speed**: ~200ms per query
- **Batch processing**: Supports multiple texts in one call

#### 2. Retrieval Service (`retrieval.py`)

**Responsibility**: Semantic search over FAQ database

```python
Input: Query vector [1536 dims]
       ↓
Qdrant: Cosine similarity search
       ↓
Filter: similarity_score >= 0.7
       ↓
Output: Top 2 FAQs with scores
```

**Similarity Scoring**:

- **Cosine similarity**: Measures angle between vectors (0-1 scale)
- **Threshold 0.7**: Ensures only relevant FAQs are retrieved
- **No matches**: System provides "not found" message

#### 3. Generation Service (`generation.py`)

**Responsibility**: Generate contextual answers using LLM

**Prompt Structure**:

```
System Prompt:
- Define role: "Legal information assistant"
- Set guidelines: Base answer on context, add disclaimer
- Set tone: Clear, accurate, plain language

User Prompt:
- Context: Retrieved FAQ 1, FAQ 2 with relevance scores
- Question: User's query
- Instruction: Generate answer with limitations acknowledgment
```

**LLM Configuration**:

- **Model**: GPT-4-turbo-preview (best quality)
- **Temperature**: 0.7 (balanced creativity vs. consistency)
- **Max tokens**: 500 (concise answers)
- **Cost**: ~$0.03 per query

## Design Patterns

### 1. Service Layer Pattern

**Why**: Separation of business logic from API layer

```
API Route → Service Method → External API/Database
```

**Benefits**:

- Easy to test (mock services)
- Reusable across multiple routes
- Clear responsibility boundaries

### 2. Dependency Injection

**Implementation**: Settings loaded once via `lru_cache`

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # Loaded from .env
```

**Benefits**:

- Single source of configuration
- Environment-specific settings
- No hardcoded values

### 3. Graceful Degradation

**Fallback Strategy**:

```
OpenAI API fails
    ↓
Return most relevant FAQ directly
    ↓
Add disclaimer: "AI generation temporarily unavailable"
```

**Benefits**:

- System never crashes
- Users always get some response
- Errors logged for debugging

## Scalability Considerations

### Current Capacity

- **FAQs**: 10 (can scale to 10,000+ without code changes)
- **Concurrent users**: 10-20 (single Docker container)
- **Response time**: 1-3 seconds average

### Scaling Path

#### Horizontal Scaling (1,000+ users)

1. **Load balancer** → Multiple FastAPI instances
2. **Qdrant cluster** → Distributed vector search
3. **Redis cache** → Cache frequent query embeddings
4. **PostgreSQL** → Replace SQLite for logs

#### Vertical Scaling (10,000+ FAQs)

1. **Optimize embeddings**: Switch to smaller model (384 dims)
2. **Hybrid search**: Combine vector + keyword search
3. **Filtering**: Add metadata filters (category, date, priority)
4. **Reranking**: Second-stage reranking model for precision

### Cost Projections

**100 queries/day**:

- Embeddings: $0.0002 × 100 = $0.02/day
- LLM: $0.03 × 100 = $3/day
- **Total**: ~$90/month

**1,000 queries/day**:

- **Total**: ~$900/month
- **Optimization**: Implement caching (50% cost reduction)

## Security Architecture

### Current Implementation

1. **Environment variables**: API keys in `.env` (not committed)
2. **CORS**: Restricted to localhost (development)
3. **Input validation**: Pydantic models + length limits
4. **Error handling**: No sensitive data in error messages

### Production Hardening Required

1. **Authentication**: JWT tokens for user identification
2. **Rate limiting**: Prevent abuse (e.g., 10 queries/minute/user)
3. **API key rotation**: Automatic OpenAI key rotation
4. **HTTPS**: TLS encryption for all traffic
5. **Input sanitization**: Prevent injection attacks
6. **Audit logging**: Who asked what, when

## Monitoring & Observability

### Current Logging

- **Level**: INFO (development), WARNING (production)
- **Format**: Timestamp + Logger + Level + Message
- **Storage**: Console output (captured by Docker)

### Recommended Production Monitoring

1. **Application logs**: Structured JSON logs to ELK stack
2. **Metrics**: Prometheus + Grafana
   - Query volume
   - Response times (p50, p95, p99)
   - Error rates
   - OpenAI API costs
3. **Tracing**: OpenTelemetry for request tracing
4. **Alerts**: PagerDuty for critical errors

## Technology Trade-offs

### Why Qdrant over alternatives?

| Option           | Pros                                    | Cons                                | Decision                 |
| ---------------- | --------------------------------------- | ----------------------------------- | ------------------------ |
| **Qdrant** | Fast, Docker-friendly, production-ready | Requires separate service           | ✅**Chosen**       |
| Pinecone         | Fully managed, scalable                 | Cloud-only, costs money             | ❌ Not flexible for demo |
| ChromaDB         | Lightweight, simple                     | Less mature, fewer features         | ❌ Less production-ready |
| In-memory        | No dependencies                         | Doesn't scale, data lost on restart | ❌ Not extensible        |

### Why FastAPI over Flask?

| Feature         | FastAPI           | Flask      |
| --------------- | ----------------- | ---------- |
| Async support   | ✅ Native         | ❌ Limited |
| API docs        | ✅ Auto-generated | ❌ Manual  |
| Type validation | ✅ Pydantic       | ❌ Manual  |
| Performance     | ✅ High           | ❌ Lower   |

### Why React over alternatives?

| Framework       | Pros                                           | Cons                      | Decision                  |
| --------------- | ---------------------------------------------- | ------------------------- | ------------------------- |
| **React** | Widely known, component reuse, large ecosystem | Requires build step       | ✅**Chosen**        |
| Vue             | Simpler learning curve                         | Less common in enterprise | ❌ Skills transferability |
| Vanilla JS      | No dependencies                                | Harder to maintain        | ❌ Not scalable           |
| Next.js         | SSR, SEO-friendly                              | Overkill for demo         | ❌ Over-engineering       |

## Future Enhancements

### Features

1. **Multi-document upload**: Users can add their own documents
2. **Category filtering**: Filter by legal category before search
3. **Citation tracking**: Show exact FAQ sections used
4. **Feedback loop**: Users rate answer quality (used for retraining)
5. **Multi-language**: Support Spanish, French legal FAQs

## Performance Optimization

### Current Optimizations

1. **Async I/O**: All API calls non-blocking
2. **Batch embeddings**: Generate all FAQ embeddings in one call
3. **Cached settings**: Configuration loaded once
4. **Connection pooling**: HTTP client reuse

---

**This architecture is designed for:**

- ✅ **Simplicity**: Easy to understand and modify
- ✅ **Scalability**: Can grow from 10 to 10,000 FAQs
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Production-readiness**: Industry-standard technologies
