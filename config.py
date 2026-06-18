import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "query_logs.db")
PDF_PATH = os.path.join(BASE_DIR, "AWS Customer Agreement.pdf")
CHROMA_PATH = os.path.join(BASE_DIR, "vectorstore", "chroma_db")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4