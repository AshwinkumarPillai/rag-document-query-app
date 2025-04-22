import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class Settings(BaseSettings):
    # HuggingFace Device
    hf_device: str | None = Field(None, env="HF_DEVICE") # General device hint
    hf_llm_device_map: str = Field("auto", env="HF_LLM_DEVICE_MAP") # Specific for LLM

    # ChromaDB
    chroma_persist_dir: str = Field("./data/chroma_db", env="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field("my-documents-collection", env="CHROMA_COLLECTION_NAME")

    # RAG
    chunk_size: int = Field(512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(50, env_prefix="", env="CHUNK_OVERLAP") # Note: env_prefix for pydantic-settings v2
    similarity_top_k: int = Field(3, env="SIMILARITY_TOP_K")

    # LLM Generation
    llm_max_new_tokens: int = Field(256, env="LLM_MAX_NEW_TOKENS")
    llm_temperature: float = Field(0.1, env="LLM_TEMPERATURE")
    llm_context_window: int = Field(512, env="LLM_CONTEXT_WINDOW")

    # LLM Model
    llm_model_api_key: str = Field(None, env="LLM_MODEL_API_KEY")

    # Data Dirs
    upload_dir: str = Field("./data/uploads", env="UPLOAD_DIR")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'
        # For pydantic-settings v2, if CHUNK_OVERLAP is not prefixed in .env
        # you might need to configure env_prefix globally or per field.
        # For simplicity, I removed env_prefix for CHUNK_OVERLAP, assuming it's in .env as CHUNK_OVERLAP

settings = Settings()

logger.error(f"UPLOAD_DIR from env: '{os.environ.get('UPLOAD_DIR')}'")

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
if settings.chroma_persist_dir:
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)

logger.info(f"Configuration loaded:")
logger.info(f"  Chroma Path: {settings.chroma_persist_dir}/{settings.chroma_collection_name}")
logger.info(f"  Chunk Size: {settings.chunk_size}, Overlap: {settings.chunk_overlap}")