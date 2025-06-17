import os
import logging
from typing import Optional

# API Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Data Configuration
DATA_DIR = "data"
USER_PROGRESS_FILE = "user_progress.json"
PROBLEMS_HISTORY_FILE = "problems_history.json"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Rate Limiting
MAX_RETRIES = 3
RETRY_DELAY = 1

# UI Configuration
DEFAULT_USER_ID = "default_user"
MAX_HINT_LEVELS = 4
MAX_PROBLEMS_PER_GENERATION = 10

# File Upload Limits
MAX_CODE_LENGTH = 10000
SUPPORTED_LANGUAGES = ["python", "java", "cpp", "javascript", "go", "rust", "c"]

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT
    )
    return logging.getLogger(__name__)
