from fastapi import APIRouter, HTTPException

from app.services.llm import get_llm_service
from app.models.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Ask a question about your documents."""
    
    try:
        llm_service = get_llm_service()
        
        response = llm_service.answer_question(
            question=request.question,
            doc_ids=request.document_ids,
            top_k=request.top_k
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )