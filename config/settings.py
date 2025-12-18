# OPENSEARCH_HOST = "localhost"
# OPENSEARCH_PORT = 9200
# OPENSEARCH_INDEX = "documents"


from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", 9200))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "documents")

ENABLE_DATE_FILTER = os.getenv("ENABLE_DATE_FILTER", "true").lower() == "true"
ENABLE_SIZE_FILTER = os.getenv("ENABLE_SIZE_FILTER", "true").lower() == "true"
ENABLE_FILETYPE_FILTER = os.getenv("ENABLE_FILETYPE_FILTER", "true").lower() == "true"

MAX_RESULT_WINDOW = int(os.getenv("MAX_RESULT_WINDOW", 10000))
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 20))
