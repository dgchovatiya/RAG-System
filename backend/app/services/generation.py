"""
AI answer generation service using OpenAI's chat completion API.
Constructs prompts from retrieved FAQs and generates contextual responses.
"""

from openai import AsyncOpenAI
from typing import List
import logging

from app.models.schemas import RetrievedFAQ

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates AI responses using OpenAI's LLM with retrieved context"""
    
    # System prompt defines the AI's role and behavior
    SYSTEM_PROMPT = """You are a helpful legal information assistant. Your role is to provide clear, accurate answers based on the FAQ context provided.

Guidelines:
- Base your answer primarily on the provided FAQ context
- If the context doesn't fully answer the question, acknowledge what information is available
- Always include a disclaimer that this is general legal information, not legal advice
- Be concise but thorough
- Use plain language that non-lawyers can understand
- Suggest consulting with a qualified attorney for specific situations"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Initialized AnswerGenerator with model: {model}")
    
    def _build_context(self, retrieved_faqs: List[RetrievedFAQ]) -> str:
        """
        Format retrieved FAQs into context string for the prompt.
        
        Args:
            retrieved_faqs: List of FAQs retrieved from vector search
            
        Returns:
            Formatted context string
        """
        if not retrieved_faqs:
            return "No relevant FAQs were found in the database."
        
        context_parts = ["Here are the relevant FAQs from our database:\n"]
        for idx, faq in enumerate(retrieved_faqs, 1):
            context_parts.append(f"\nFAQ {idx} (Category: {faq.category}, Relevance: {faq.similarity_score:.2f}):")
            context_parts.append(f"Question: {faq.question}")
            context_parts.append(f"Answer: {faq.answer}")
        
        return "\n".join(context_parts)
    
    def _build_user_prompt(self, user_query: str, context: str) -> str:
        """
        Construct the user prompt combining query and context.
        
        Args:
            user_query: The user's question
            context: Formatted FAQ context
            
        Returns:
            Complete user prompt string
        """
        return f"""{context}

User Question: {user_query}

Please provide a helpful answer based on the FAQ context above. If the context doesn't fully address the question, acknowledge the limitations and recommend consulting with an attorney."""
    
    async def generate_answer(
        self, 
        user_query: str, 
        retrieved_faqs: List[RetrievedFAQ]
    ) -> str:
        """
        Generate AI response using retrieved FAQs as context.
        
        Args:
            user_query: The user's question
            retrieved_faqs: FAQs retrieved from vector search
            
        Returns:
            AI-generated answer string
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            context = self._build_context(retrieved_faqs)
            user_prompt = self._build_user_prompt(user_query, context)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer of length {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            # Return fallback message instead of crashing
            return self._get_fallback_response(retrieved_faqs)
    
    def _get_fallback_response(self, retrieved_faqs: List[RetrievedFAQ]) -> str:
        """
        Provide fallback response if OpenAI API fails.
        Returns the most relevant FAQ answer directly.
        """
        if not retrieved_faqs:
            return "I apologize, but I'm unable to provide an answer at this time. Please try again later or consult with a legal professional."
        
        # Return the most relevant FAQ
        best_faq = retrieved_faqs[0]
        return f"""Based on our FAQ database:

{best_faq.answer}

Note: This is general legal information from our FAQ database. For advice specific to your situation, please consult with a qualified attorney.

(AI generation temporarily unavailable - showing direct FAQ match)"""
