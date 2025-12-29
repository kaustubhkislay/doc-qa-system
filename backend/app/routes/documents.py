from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
import uuid
import json
from typing import Optional

from app.services.storage import get_storage_service
from app.services.pdf_processor import extract_pdf_content
from app.services.vectorstore import get_vectorstore_service
from app.models.schemas import (
    DocumentMetadata, 
    DocumentUploadResponse, 
    DocumentListResponse
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    collection: Optional[str] = Form(None)
):
    """Upload a PDF document for Q&A."""
    
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 50MB"
        )
    
    try:
        # Extract text from PDF
        pdf_content = extract_pdf_content(content)
        
        if pdf_content.page_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Could not extract any content from the PDF"
            )
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Upload to Cloud Storage
        storage = get_storage_service()
        storage_path = storage.upload_pdf(content, file.filename)
        
        # Save metadata
        metadata = DocumentMetadata(
            id=doc_id,
            title=title,
            filename=file.filename,
            page_count=pdf_content.page_count,
            upload_date=datetime.utcnow(),
            storage_path=storage_path,
            collection=collection
        )
        storage.save_metadata(metadata)
        
        # Add to vector store
        vectorstore = get_vectorstore_service()
        chunk_count = vectorstore.add_document(doc_id, title, pdf_content)
        
        return DocumentUploadResponse(
            message=f"Document uploaded successfully. Created {chunk_count} searchable chunks.",
            document_id=doc_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(collection: Optional[str] = None):
    """List all uploaded documents."""
    storage = get_storage_service()
    documents = storage.list_documents(collection)
    return DocumentListResponse(documents=documents)


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """Get a specific document's metadata."""
    storage = get_storage_service()
    metadata = storage.get_metadata(document_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return metadata


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated data."""
    storage = get_storage_service()
    metadata = storage.get_metadata(document_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from vector store
        vectorstore = get_vectorstore_service()
        vectorstore.delete_document(document_id)
        
        # Delete from Cloud Storage
        storage.delete_pdf(metadata.storage_path)
        
        # Delete metadata
        storage.delete_metadata(document_id)
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )