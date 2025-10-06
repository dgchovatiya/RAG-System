"""
Pydantic models for request/response validation and data structure.
These models ensure type safety and automatic validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FAQ(BaseModel):
    """Structure of a single FAQ entry"""
    id: str = Field(..., description="Unique identifier for the FAQ")
    question: str = Field(..., description="The FAQ question text")
    answer: str = Field(..., description="The detailed answer to the FAQ")
    category: str = Field(..., description="Legal category (e.g., Personal Injury)")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")


class RetrievedFAQ(BaseModel):
    """FAQ with relevance score from vector search"""
    faq_id: str
    question: str
    answer: str
    category: str
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")


class QueryRequest(BaseModel):
    """User's question submission"""
    query: str = Field(..., min_length=5, max_length=500, description="User's question")
    include_sources: bool = Field(default=True, description="Whether to return source FAQs")


class QueryResponse(BaseModel):
    """AI-generated answer with metadata"""
    answer: str = Field(..., description="AI-generated contextual answer")
    sources: List[RetrievedFAQ] = Field(default_factory=list, description="Retrieved source FAQs")
    response_time_ms: int = Field(..., description="Time taken to generate response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InteractionLog(BaseModel):
    """Log entry for a user interaction"""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_query: str
    retrieved_faq_ids: List[str]
    ai_response: str
    response_time_ms: int
    relevance_scores: List[float]
    error_occurred: bool = False


class HealthResponse(BaseModel):
    """System health check response"""
    status: str
    qdrant_connected: bool
    openai_configured: bool
    faqs_loaded: int
