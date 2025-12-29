from langchain_google_vertexai import VertexAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Optional
import os

from app.config import get_settings
from app.services.pdf_processor import PDFContent


class VectorStoreService:
    """Manages document embeddings using ChromaDB."""
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize embeddings
        self.embeddings = VertexAIEmbeddings(
            model_name=settings.embedding_model,
            project=settings.project_id,
        )
        
        # Initialize ChromaDB with persistence
        self.persist_directory = settings.chroma_persist_dir
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="documents"
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def add_document(
        self, 
        doc_id: str, 
        title: str, 
        content: PDFContent
    ) -> int:
        """Add a document to the vector store. Returns number of chunks created."""
        documents = []
        
        for page in content.pages:
            if not page.text.strip():
                continue
                
            # Split page into chunks
            chunks = self.text_splitter.split_text(page.text)
            
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": doc_id,
                        "title": title,
                        "page_number": page.page_number,
                    }
                )
                documents.append(doc)
        
        if documents:
            self.vectorstore.add_documents(documents)
        
        return len(documents)
    
    def search(
        self, 
        query: str, 
        k: int = 5,
        doc_ids: Optional[list[str]] = None
    ) -> list[Document]:
        """Search for relevant document chunks."""
        # Build filter if document IDs are specified
        filter_dict = None
        if doc_ids:
            filter_dict = {"doc_id": {"$in": doc_ids}}
        
        results = self.vectorstore.similarity_search(
            query, 
            k=k,
            filter=filter_dict
        )
        
        return results
    
    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks for a document from the vector store."""
        # Get all chunk IDs for this document
        self.vectorstore.delete(where={"doc_id": doc_id})


# Singleton instance
_vectorstore_service: Optional[VectorStoreService] = None


def get_vectorstore_service() -> VectorStoreService:
    """Get or create the vector store service singleton."""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = VectorStoreService()
    return _vectorstore_service