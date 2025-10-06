"""
API route handlers for the RAG Q&A system.
Defines endpoints for querying, logging, and health checks.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
import logging

from app.models.schemas import QueryRequest, QueryResponse, InteractionLog, HealthResponse
from app.services.embeddings import EmbeddingService
from app.services.retrieval import FAQRetriever
from app.services.generation import AnswerGenerator
from app.models.database import Database
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["rag"])

# Global service instances (initialized in main.py)
embedding_service: EmbeddingService = None
faq_retriever: FAQRetriever = None
answer_generator: AnswerGenerator = None
database: Database = None


def set_services(embedding, retrieval, generation, db):
    """
    Initialize route-level service instances.
    Called from main.py after services are created.
    """
    global embedding_service, faq_retriever, answer_generator, database
    embedding_service = embedding
    faq_retriever = retrieval
    answer_generator = generation
    database = db


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Main Q&A endpoint: accepts a question and returns AI-generated answer.
    
    Process:
    1. Generate embedding for user query
    2. Search vector database for similar FAQs
    3. Generate contextualized answer using LLM
    4. Log the interaction
    5. Return response with sources
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        # Step 1: Generate query embedding
        query_embedding = await embedding_service.generate_embedding(request.query)
        
        # Step 2: Retrieve relevant FAQs
        settings = get_settings()
        retrieved_faqs = await faq_retriever.search(
            query_embedding=query_embedding,
            top_k=settings.top_k_results,
            score_threshold=settings.similarity_threshold
        )
        
        # Check if we found relevant FAQs
        if not retrieved_faqs:
            logger.warning("No relevant FAQs found above threshold")
            answer = (
                "I couldn't find any relevant information in our FAQ database for your question. "
                "This might be outside the scope of our current knowledge base. "
                "Please consider rephrasing your question or consulting with a legal professional directly."
            )
            sources = []
        else:
            # Step 3: Generate AI answer
            answer = await answer_generator.generate_answer(request.query, retrieved_faqs)
            sources = retrieved_faqs if request.include_sources else []
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 4: Log interaction
        await database.log_interaction(
            user_query=request.query,
            retrieved_faq_ids=[faq.faq_id for faq in retrieved_faqs],
            ai_response=answer,
            response_time_ms=response_time_ms,
            relevance_scores=[faq.similarity_score for faq in retrieved_faqs],
            error_occurred=False
        )
        
        logger.info(f"Successfully processed query in {response_time_ms}ms")
        
        # Step 5: Return response
        return QueryResponse(
            answer=answer,
            sources=sources,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        # Log error
        response_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        
        try:
            await database.log_interaction(
                user_query=request.query,
                retrieved_faq_ids=[],
                ai_response=f"Error: {str(e)}",
                response_time_ms=response_time_ms,
                relevance_scores=[],
                error_occurred=True
            )
        except Exception as log_error:
            logger.error(f"Failed to log error: {log_error}")
        
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again."
        )


@router.get("/logs", response_model=List[dict])
async def get_interaction_logs(limit: int = 50):
    """
    Retrieve interaction history for review and analysis.
    
    Args:
        limit: Maximum number of logs to return (default: 50)
        
    Returns:
        List of interaction log entries
    """
    try:
        logs = await database.get_logs(limit=limit)
        logger.info(f"Retrieved {len(logs)} interaction logs")
        return logs
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve interaction logs"
        )


@router.get("/stats")
async def get_statistics():
    """
    Get system statistics and analytics.
    
    Returns:
        Dictionary with query statistics
    """
    try:
        stats = await database.get_stats()
        stats["faqs_in_database"] = faq_retriever.get_faq_count()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check endpoint.
    Verifies all components are operational.
    """
    try:
        # Check Qdrant connection
        faq_count = faq_retriever.get_faq_count()
        qdrant_connected = faq_count >= 0
        
        # Check OpenAI configuration
        settings = get_settings()
        openai_configured = bool(settings.openai_api_key)
        
        status = "healthy" if (qdrant_connected and openai_configured) else "degraded"
        
        return HealthResponse(
            status=status,
            qdrant_connected=qdrant_connected,
            openai_configured=openai_configured,
            faqs_loaded=faq_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            qdrant_connected=False,
            openai_configured=False,
            faqs_loaded=0
        )
