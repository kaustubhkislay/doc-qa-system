from google.cloud import storage
from google.cloud import firestore
from datetime import datetime
import uuid
from typing import Optional

from app.config import get_settings
from app.models.schemas import DocumentMetadata


class StorageService:
    """Handles file storage in GCS and metadata in Firestore."""
    
    def __init__(self):
        settings = get_settings()
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.bucket_name)
        self.db = firestore.Client()
        self.collection = self.db.collection("documents")
    
    def upload_pdf(self, file_content: bytes, filename: str) -> str:
        """Upload PDF to Cloud Storage. Returns the storage path."""
        doc_id = str(uuid.uuid4())
        storage_path = f"documents/{doc_id}/{filename}"
        
        blob = self.bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type="application/pdf")
        
        return storage_path
    
    def download_pdf(self, storage_path: str) -> bytes:
        """Download PDF from Cloud Storage."""
        blob = self.bucket.blob(storage_path)
        return blob.download_as_bytes()
    
    def delete_pdf(self, storage_path: str) -> None:
        """Delete PDF from Cloud Storage."""
        blob = self.bucket.blob(storage_path)
        blob.delete()
    
    def save_metadata(self, metadata: DocumentMetadata) -> None:
        """Save document metadata to Firestore."""
        self.collection.document(metadata.id).set(metadata.model_dump())
    
    def get_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata from Firestore."""
        doc = self.collection.document(doc_id).get()
        if doc.exists:
            return DocumentMetadata(**doc.to_dict())
        return None
    
    def list_documents(self, collection: Optional[str] = None) -> list[DocumentMetadata]:
        """List all documents, optionally filtered by collection."""
        query = self.collection
        if collection:
            query = query.where("collection", "==", collection)
        
        docs = query.stream()
        return [DocumentMetadata(**doc.to_dict()) for doc in docs]
    
    def delete_metadata(self, doc_id: str) -> None:
        """Delete document metadata from Firestore."""
        self.collection.document(doc_id).delete()


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create the storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service