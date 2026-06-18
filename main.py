import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import ValidationError
from schemas import AskRequest, AskResponse, AnalyticsResponse
from ragpipeline import ingest_document, process_query
from database import init_db, log_query
from analytics import get_analytics_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AWS Agreement RAG API", version="1.0.0")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest():
    try:
        num_chunks = ingest_document()
        return {"message": f"Successfully ingested document into {num_chunks} chunks."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to ingest document.")

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")
    
    try:
        result = process_query(request.question)
        
        log_query(
            question=request.question,
            answer=result["answer"],
            answer_found=result["answer_found"],
            response_time=result["response_time"]
        )

        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
            response_time=result["response_time"],
            confidence=result["confidence"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during query processing.")

@app.get("/analytics", response_model=AnalyticsResponse)
def analytics():
    try:
        data = get_analytics_data()
        return AnalyticsResponse(**data)
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve analytics data.")