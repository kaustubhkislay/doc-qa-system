from langchain_google_vertexai import ChatVertexAI
from langchain_core.documents import Document
from typing import Optional

from app.config import get_settings
from app.services.vectorstore import get_vectorstore_service
from app.models.schemas import QueryResponse, Source


class LLMService:
    """Handles question answering using RAG."""
    
    def __init__(self):
        settings = get_settings()
        
        self.llm = ChatVertexAI(
            model_name=settings.llm_model,
            project=settings.project_id,
            temperature=0.2,
            max_output_tokens=2048,
        )
        
        self.vectorstore = get_vectorstore_service()
    
    def _build_context(self, documents: list[Document]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        
        for doc in documents:
            source_info = f"[{doc.metadata['title']}, Page {doc.metadata['page_number']}]"
            context_parts.append(f"{source_info}\n{doc.page_content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_sources(self, documents: list[Document]) -> list[Source]:
        """Extract unique sources from retrieved documents."""
        seen = set()
        sources = []
        
        for doc in documents:
            key = (doc.metadata["doc_id"], doc.metadata["page_number"])
            if key not in seen:
                seen.add(key)
                sources.append(Source(
                    document_id=doc.metadata["doc_id"],
                    document_title=doc.metadata["title"],
                    page_number=doc.metadata["page_number"],
                    excerpt=doc.page_content[:200] + "..."
                ))
        
        return sources
    
    def answer_question(
        self,
        question: str,
        doc_ids: Optional[list[str]] = None,
        top_k: int = 5
    ) -> QueryResponse:
        """Answer a question using retrieved document context."""
        
        # Retrieve relevant chunks
        documents = self.vectorstore.search(
            query=question,
            k=top_k,
            doc_ids=doc_ids
        )
        
        if not documents:
            return QueryResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                sources=[]
            )
        
        # Build context and prompt
        context = self._build_context(documents)
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document excerpts.
        
Use ONLY the information from the excerpts below to answer the question. If the excerpts don't contain enough information to fully answer the question, say so.

When citing information, mention which document and page it came from.

Document Excerpts:
{context}

Question: {question}

Answer:"""

        # Generate response
        response = self.llm.invoke(prompt)
        
        return QueryResponse(
            answer=response.content,
            sources=self._build_sources(documents)
        )


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service