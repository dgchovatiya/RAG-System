"""
OpenAI Embedding Service for converting text to vector representations.
Handles API calls to OpenAI's embedding model with error handling.
"""

from openai import AsyncOpenAI
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages text-to-vector conversion using OpenAI embeddings"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized EmbeddingService with model: {model}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Convert a single text string to vector embedding.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple texts to embeddings in a single API call.
        More efficient than calling generate_embedding multiple times.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
