from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.rag_service import RAGService


# ========================================
# Paths
# ========================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"

DATA_DIR = BASE_DIR / "data"


# ========================================
# RAG Service
# ========================================

rag_service: Optional[RAGService] = None


# ========================================
# Application Lifespan
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global rag_service

    print("Starting RAG service...")

    try:

        rag_service = RAGService()

        print("RAG service started successfully.")

    except Exception as exc:

        print(
            f"Failed to start RAG service: {exc}"
        )

        rag_service = None

    yield

    print("RAG service stopped.")


# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="Groq + ChromaDB RAG API",
    version="1.0.0",
    lifespan=lifespan,
)


# ========================================
# Static Files
# ========================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# ========================================
# Request Model
# ========================================

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
    )

    top_k: Optional[int] = Field(
        default=5,
        ge=1,
        le=50,
    )

    source: Optional[str] = None


# ========================================
# Home Page
# ========================================

@app.get("/")
def home():

    return FileResponse(
        TEMPLATES_DIR / "index.html"
    )


# ========================================
# Documents
# ========================================

@app.get("/documents")
def get_documents():

    if not DATA_DIR.exists():

        return {
            "documents": []
        }

    supported_extensions = {
        ".pdf",
        ".txt",
        ".md",
    }

    documents = []

    for file in sorted(DATA_DIR.iterdir()):

        if (
            file.is_file()
            and file.suffix.lower()
            in supported_extensions
        ):

            documents.append({
                "name": file.name,
                "type": file.suffix.lower().replace(
                    ".",
                    ""
                ),
            })

    return {
        "documents": documents,
        "count": len(documents),
    }


# ========================================
# Health Check
# ========================================

@app.get("/health")
def health():

    if rag_service is None:

        return {
            "status": "starting",
            "indexed_chunks": 0,
        }

    return {
        "status": "ok",
        "indexed_chunks": (
            rag_service.store.count()
        ),
    }


# ========================================
# RAG Query
# ========================================

@app.post("/rag/query")
def query_rag(
    payload: QuestionRequest,
):

    if rag_service is None:

        raise HTTPException(
            status_code=503,
            detail="RAG service is not ready.",
        )

    try:

        return rag_service.ask(
            question=payload.question,
            top_k=payload.top_k,
            source=payload.source,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc