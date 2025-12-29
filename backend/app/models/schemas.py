from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentMetadata(BaseModel):
    """Metadata for an uploaded document."""
    id: str
    title: str
    filename: str
    page_count: int
    upload_date: datetime
    storage_path: str
    collection: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""
    message: str
    document_id: str


class DocumentListResponse(BaseModel):
    """Response containing list of documents."""
    documents: list[DocumentMetadata]


class QueryRequest(BaseModel):
    """Request to query documents."""
    question: str = Field(..., min_length=1, max_length=1000)
    document_ids: Optional[list[str]] = None
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    """A source citation for an answer."""
    document_id: str
    document_title: str
    page_number: int
    excerpt: str


class QueryResponse(BaseModel):
    """Response to a document query."""
    answer: str
    sources: list[Source]
    
    
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"