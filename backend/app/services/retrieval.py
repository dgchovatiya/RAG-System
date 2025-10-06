"""
Vector-based FAQ retrieval using Qdrant.
Handles FAQ indexing and semantic search operations.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import json
import logging

from app.models.schemas import FAQ, RetrievedFAQ

logger = logging.getLogger(__name__)


class FAQRetriever:
    """Manages FAQ storage and retrieval in Qdrant vector database"""
    
    def __init__(
        self, 
        host: str, 
        port: int, 
        collection_name: str,
        embedding_dimension: int = 1536
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        logger.info(f"Initialized FAQRetriever connecting to {host}:{port}")
    
    async def initialize_collection(self):
        """
        Create Qdrant collection if it doesn't exist.
        Uses cosine distance for similarity measurement.
        """
        collections = self.client.get_collections().collections
        collection_exists = any(c.name == self.collection_name for c in collections)
        
        if not collection_exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
        else:
            logger.info(f"Collection {self.collection_name} already exists")
    
    async def index_faqs(self, faqs: List[FAQ], embeddings: List[List[float]]):
        """
        Store FAQs with their embeddings in Qdrant.
        
        Args:
            faqs: List of FAQ objects
            embeddings: Corresponding embedding vectors
        """
        if len(faqs) != len(embeddings):
            raise ValueError("Number of FAQs must match number of embeddings")
        
        points = []
        for idx, (faq, embedding) in enumerate(zip(faqs, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "faq_id": faq.id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category,
                    "keywords": faq.keywords
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Indexed {len(points)} FAQs into Qdrant")
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 2,
        score_threshold: float = 0.7,
        category_filter: Optional[str] = None
    ) -> List[RetrievedFAQ]:
        """
        Search for similar FAQs using vector similarity.
        
        Args:
            query_embedding: Vector representation of user query
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            category_filter: Optional category to filter results
            
        Returns:
            List of RetrievedFAQ objects with similarity scores
        """
        search_params = {
            "collection_name": self.collection_name,
            "query_vector": query_embedding,
            "limit": top_k,
            "score_threshold": score_threshold
        }
        
        # Add category filter if specified
        if category_filter:
            search_params["query_filter"] = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category_filter)
                    )
                ]
            )
        
        results = self.client.search(**search_params)
        
        retrieved_faqs = []
        for result in results:
            faq = RetrievedFAQ(
                faq_id=result.payload["faq_id"],
                question=result.payload["question"],
                answer=result.payload["answer"],
                category=result.payload["category"],
                similarity_score=result.score
            )
            retrieved_faqs.append(faq)
        
        logger.info(f"Retrieved {len(retrieved_faqs)} FAQs with scores above {score_threshold}")
        return retrieved_faqs
    
    def get_faq_count(self) -> int:
        """Return the total number of FAQs in the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception:
            return 0
