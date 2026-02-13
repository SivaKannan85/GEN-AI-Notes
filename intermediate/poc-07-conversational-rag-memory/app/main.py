"""FastAPI app for POC 7 conversational RAG with memory."""
from fastapi import FastAPI, HTTPException, status

from app.config import get_settings
from app.models import AskRequest, AskResponse, HealthResponse, IngestRequest, IngestResponse
from app.rag_engine import get_engine

settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)


@app.get("/", response_model=HealthResponse)
async def health() -> HealthResponse:
    engine = get_engine()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        indexed_documents=engine.indexed_documents(),
    )


@app.post("/documents/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    count = get_engine().ingest(request.documents)
    return IngestResponse(message="Documents indexed", indexed_documents=count)


@app.post("/chat/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    try:
        result = get_engine().ask(
            session_id=request.session_id,
            question=request.question,
            top_k=request.top_k,
        )
        return AskResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.delete("/reset")
async def reset() -> dict[str, str]:
    get_engine().clear()
    return {"message": "Engine reset"}
