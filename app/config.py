import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
if os.getenv("VERCEL"):
    os.environ.setdefault("HF_HOME", "/tmp/hf")
    os.environ.setdefault("XDG_CACHE_HOME", "/tmp")
ROOT = Path(__file__).resolve().parent.parent
SERVERLESS = bool(os.getenv("VERCEL"))


class Settings:
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size, chunk_overlap, top_k = 500, 50, 3
    sample_docs = ROOT / "data" / "sample_docs"
    public_dir = ROOT / "public"
    chroma_path = str(ROOT / "chroma_db")
    # Serverless filesystems are read-only except /tmp
    model_cache = "/tmp/fastembed" if SERVERLESS else str(ROOT / ".cache" / "fastembed")
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    allowed_ext = (".pdf", ".txt", ".md")


settings = Settings()
