import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .utils import save_upload_file, cleanup_file
from .rag_pipeline import initialize_rag_pipeline, add_document_to_index, query_documents, query_engine
import os # For os.path.basename

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Reduce verbosity from noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.WARNING) # Chroma telemetry
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

class UploadResponse(BaseModel):
    message: str
    filename: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing RAG pipeline...")
    try:
        initialize_rag_pipeline()
        logger.info("RAG pipeline initialization complete.")
    except Exception as e:
        logger.exception("FATAL: Failed to initialize RAG pipeline during startup.")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title="Document Q&A API (ChromaDB + HuggingFace)",
    description="API using fixed ChromaDB and HuggingFace models for document Q&A.",
    version="2.0.0",
    lifespan=lifespan
)

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post("/upload", response_model=UploadResponse)
async def upload_document_endpoint(file: UploadFile = File(...)):
    if not file.filename:
         raise HTTPException(status_code=400, detail="No filename provided.")
    filename = os.path.basename(file.filename)
    logger.info(f"Received file upload request: {filename}")

    temp_file_path = None
    try:
        temp_file_path = await save_upload_file(file)
        add_document_to_index(temp_file_path)
        return UploadResponse(message="File uploaded and processed successfully.", filename=filename)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Error processing upload file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        if temp_file_path:
            cleanup_file(temp_file_path)

@app.post("/query", response_model=QueryResponse)
async def query_index_endpoint(request: QueryRequest):
    logger.info(f"Received query request: {request.query}")
    try:
        answer = query_documents(request.query)
        return QueryResponse(answer=answer)
    except RuntimeError as re: # Catch specific runtime errors from RAG pipeline
        logger.error(f"Runtime error during query: {re}")
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        logger.exception(f"Unexpected error processing query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.get("/health")
async def health_check_endpoint():
    status = "ready" if query_engine else "initializing_or_failed"
    return JSONResponse(content={"status": status})