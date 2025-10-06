"""
Main FastAPI application entry point.
Initializes services, loads FAQs, and configures the API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from pathlib import Path

from app.config import get_settings
from app.api import routes
from app.services.embeddings import EmbeddingService
from app.services.retrieval import FAQRetriever
from app.services.generation import AnswerGenerator
from app.models.database import Database
from app.models.schemas import FAQ

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Legal Q&A RAG System",
    description="Retrieval-Augmented Generation system for legal FAQs",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize all services and load FAQ data on application startup.
    This runs once when the server starts.
    """
    logger.info("Starting application initialization...")
    settings = get_settings()
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        db = Database(db_path="data/interactions.db")
        await db.initialize()
        
        # Initialize services
        logger.info("Initializing embedding service...")
        embedding_service = EmbeddingService(
            api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        
        logger.info("Initializing FAQ retriever...")
        faq_retriever = FAQRetriever(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=settings.qdrant_collection_name,
            embedding_dimension=settings.embedding_dimension
        )
        await faq_retriever.initialize_collection()
        
        logger.info("Initializing answer generator...")
        answer_generator = AnswerGenerator(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.max_tokens
        )
        
        # Load and index FAQs if collection is empty
        faq_count = faq_retriever.get_faq_count()
        if faq_count == 0:
            logger.info("Loading FAQs from JSON file...")
            faq_data_path = Path(__file__).parent / "data" / "legal_faqs.json"
            
            with open(faq_data_path, "r") as f:
                faq_data = json.load(f)
            
            faqs = [FAQ(**faq) for faq in faq_data["faqs"]]
            logger.info(f"Loaded {len(faqs)} FAQs")
            
            # Generate embeddings for all FAQ questions
            logger.info("Generating embeddings for FAQs...")
            questions = [faq.question for faq in faqs]
            embeddings = await embedding_service.generate_embeddings_batch(questions)
            
            # Index FAQs in Qdrant
            logger.info("Indexing FAQs in vector database...")
            await faq_retriever.index_faqs(faqs, embeddings)
            logger.info("FAQ indexing complete!")
        else:
            logger.info(f"FAQs already loaded: {faq_count} entries found")
        
        # Set services in routes module
        routes.set_services(embedding_service, faq_retriever, answer_generator, db)
        
        logger.info("Application initialization complete!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise


# Include API routes
app.include_router(routes.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Legal Q&A RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
