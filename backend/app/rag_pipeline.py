import logging
from typing import Optional
import torch

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings as LlamaSettings,
    PromptTemplate
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers import get_response_synthesizer

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from chromadb import HttpClient
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq
from .config import settings

logger = logging.getLogger(__name__)

# --- Fixed Model Choices ---
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
# LLM_MODEL_NAME = "google/flan-t5-base"
LLM_MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

# --- Global query engine ---
query_engine = None
index: Optional[VectorStoreIndex] = None

# --- Custom Prompt Template ---
QA_TEMPLATE_STR = (
    "You are an assistant specialized in answering questions based *only* on the provided context.\n"
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, answer the query.\n"
    "If the context does not contain the information needed to answer the query, "
    "respond with: 'I cannot answer this question based on the provided document(s).'\n"
    "Query: {query_str}\n"
    "Answer: "
)
QA_PROMPT_TEMPLATE = PromptTemplate(QA_TEMPLATE_STR)


def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline with fixed ChromaDB and HuggingFace models.
    """
    global query_engine
    global index
    logger.info(f"Initializing RAG pipeline with Embedding: {EMBED_MODEL_NAME}, LLM: {LLM_MODEL_NAME}")

    # --- Determine device for HuggingFace models ---
    if settings.hf_device and settings.hf_device.startswith("cuda") and not torch.cuda.is_available():
        logger.warning(f"HF_DEVICE is set to '{settings.hf_device}' but CUDA is not available. Falling back to CPU.")
        effective_hf_device = "cpu"
    elif settings.hf_device:
        effective_hf_device = settings.hf_device
    elif torch.cuda.is_available():
        effective_hf_device = "cuda"
        logger.info("CUDA available. Using 'cuda' for HuggingFace models by default.")
    else:
        effective_hf_device = "cpu"
        logger.info("CUDA not available. Using 'cpu' for HuggingFace models.")

    # 1. Configure HuggingFace Embedding Model
    logger.info(f"Loading embedding model: {EMBED_MODEL_NAME} on device: {effective_hf_device}")
    embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL_NAME,
        device=effective_hf_device
    )

    # 2. Configure  LLM
    logger.info(f"Loading LLM: {LLM_MODEL_NAME} with device_map: '{settings.hf_llm_device_map}'")
    # To use Hugginface locally
    # llm = HuggingFaceLLM(
    #     model_name=LLM_MODEL_NAME,
    #     tokenizer_name=LLM_MODEL_NAME,
    #     context_window=settings.llm_context_window,
    #     max_new_tokens=settings.llm_max_new_tokens,
    #     generate_kwargs={"temperature": settings.llm_temperature, "do_sample": settings.llm_temperature > 0.0},
    #     device_map=settings.hf_llm_device_map,
    # )

    # To use Groq
    llm = Groq(model="llama3-70b-8192", api_key=settings.llm_model_api_key)
    # llm = OpenAI( model="gpt-4o-mini",  api_key="some key")

    logger.info("LLM loaded.")

    # 3. Configure Node Parser (Chunking)
    node_parser = SentenceSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    # 4. Configure ChromaDB Vector Store and Storage Context
    logger.info(f"Setting up ChromaDB. Path: {settings.chroma_persist_dir}, Collection: {settings.chroma_collection_name}")
    # db = HttpClient(host="localhost", port=8000) # when running on local machine
    db = HttpClient(host="chromadb", port=8000) # when using Docker
    
    chroma_collection = db.get_or_create_collection("mydocs")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    logger.info(f"ChromaDB client initialized.")

    # 5. Configure LlamaIndex Global Settings
    LlamaSettings.llm = llm
    LlamaSettings.embed_model = embed_model
    LlamaSettings.node_parser = node_parser

    # 6. Load or Create Index
    # index: Optional[VectorStoreIndex] = None
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    logger.info(f"Loaded index from collection: {chroma_collection}")

    if index is None: # Should not happen if creation path works
         logger.error("Index could not be loaded or created. Critical failure.")
         raise RuntimeError("Failed to initialize the index.")

    # 7. Create Query Engine
    logger.info("Creating query engine...")
    response_synthesizer = get_response_synthesizer(
        response_mode="compact",
        text_qa_template=QA_PROMPT_TEMPLATE,
        llm=llm
    )
    query_engine = index.as_query_engine(
        response_synthesizer=response_synthesizer,
        similarity_top_k=settings.similarity_top_k,
    )

    if query_engine is None:
        logger.error("Query engine could not be created. Critical failure.")
    logger.info("RAG pipeline initialized successfully.")


def add_document_to_index(file_path: str):
    global query_engine
    global index

    if query_engine is None or query_engine.retriever is None: # type: ignore
        logger.error("Query engine or retriever not initialized. Cannot add document.")
        raise RuntimeError("RAG Pipeline is not ready.")

    try:
        logger.info(f"Loading document: {file_path}")
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()

        if not documents:
            logger.warning(f"No processable content found in file: {file_path}")
            return

        logger.info(f"Ingesting {len(documents)} document chunk(s) into the index...")
        # index = query_engine.retriever.index # type: ignore
        for doc in documents:
            index.insert(document=doc)
        logger.info(f"Successfully ingested document(s) from: {file_path}. Changes persisted to ChromaDB.")
    except Exception as e:
        logger.error(f"Failed to ingest document {file_path}: {e}")
        raise

def query_documents(query_text: str) -> str:
    global query_engine
    if query_engine is None:
        logger.error("Query engine not initialized. Cannot query.")
        raise RuntimeError("RAG Pipeline is not ready.")

    logger.info(f"Received query: {query_text}")
    try:
        response = query_engine.query(query_text)
        logger.info(f"Generated response (first 100 chars): {str(response)[:100]}...")
        return str(response)
    except Exception as e:
        logger.exception(f"Error during query processing for: '{query_text}'")
        raise RuntimeError(f"Error processing query: {e}")