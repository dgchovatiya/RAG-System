# ⚡ Quick Start - Legal Q&A RAG System

## 🎯 5-Minute Setup

### Step 1: Add Your OpenAI API Key

Create the environment file:

```bash
# Windows PowerShell
cd backend
"OPENAI_API_KEY=your-key-here" | Out-File -FilePath .env -Encoding utf8

# Mac/Linux
cd backend
echo "OPENAI_API_KEY=your-key-here" > .env
```

Replace `your-key-here` with your actual OpenAI API key.

### Step 2: Start the System

From the project root:

```bash
docker-compose up --build
```

**First-time startup takes 2-3 minutes** (downloads Docker images and installs dependencies).

### Step 3: Access the Application

Once you see "Application initialization complete!":

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🧪 Test It Out

### Try These Sample Questions:

1. "What is the statute of limitations for personal injury?"
2. "Can I break a contract without penalty?"
3. "What constitutes wrongful termination?"
4. "What are my rights if I'm arrested?"

### Expected Behavior:

1. **Enter question** → Click "Ask Question"
2. **Wait 2-3 seconds** → See loading spinner
3. **View answer** → AI-generated response appears
4. **Check sources** → Expand to see which FAQs were used
5. **View history** → Click "Show History" to see past queries

## ✅ Verify Everything Works

### 1. Check Health Status

Visit: http://localhost:8000/api/health

Should show:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "openai_configured": true,
  "faqs_loaded": 10
}
```

### 2. Check API Documentation

Visit: http://localhost:8000/docs

You should see interactive Swagger UI with all endpoints.

### 3. Check Qdrant

Visit: http://localhost:6333/dashboard

Should show the `legal_faqs` collection with 10 points.

## 🐛 Common Issues

### "OpenAI API key not configured"

**Fix**:
```bash
# Verify .env file exists
cat backend/.env

# Should show: OPENAI_API_KEY=sk-...
# If not, recreate it with your key
```

Then restart:
```bash
docker-compose restart backend
```

### Port Already in Use

**Fix**: Stop the process using the port or change ports in `docker-compose.yml`

### FAQs Not Loading (faqs_loaded: 0)

**Fix**: Reset everything:
```bash
docker-compose down -v
docker-compose up --build
```

## 📊 What's Happening Under the Hood

```
Your Question
    ↓
1. Convert to vector (embedding) [~200ms]
    ↓
2. Search Qdrant for similar FAQs [~50ms]
    ↓
3. Send FAQs + question to GPT-4 [~1-2s]
    ↓
4. Get AI-generated answer
    ↓
5. Log interaction to SQLite
    ↓
Display answer + sources
```

## 🎓 Understanding RAG

**What Just Happened?**

1. **Retrieval**: System found the 2 most relevant FAQs from the database
2. **Augmentation**: Added those FAQs as context to the AI prompt
3. **Generation**: GPT-4 generated an answer based on the context

**Why This Matters?**

- AI answers are **grounded in real data** (your FAQs)
- No hallucination - AI can only answer based on what's in the database
- You can **update FAQs** without retraining the model
- **Source attribution** - see which FAQs informed each answer

## 🚀 Next Steps

1. **Try different questions** - test the retrieval quality
2. **Check the logs** - see how queries are processed
3. **Read SETUP_GUIDE.md** - comprehensive documentation
4. **Read ARCHITECTURE.md** - understand the technical design
5. **Modify FAQs** - add your own legal questions

## 🛑 Stop the System

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## 📚 Full Documentation

- **SETUP_GUIDE.md** - Detailed setup, troubleshooting, local development
- **ARCHITECTURE.md** - Technical architecture, design decisions, scaling
- **README.md** - Complete project overview

---

**You're all set!** The system is now running and ready to answer legal questions. 🎉
