"""
Configuration settings for the Maritime Case Generator.

This file contains all configurable parameters for the application based on
the actual settings used in the 04_Case_Generation.ipynb notebook.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base paths - matching the actual paths used in the notebook
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Data"
OUTPUT_DIR = BASE_DIR / "Output"
CHECKPOINT_DIR = DATA_DIR / "Checkpoints"
LOG_DIR = DATA_DIR / "Logs"
GENERATED_CASES_DIR = OUTPUT_DIR / "Generated_Cases"

# Ensure directories exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CHECKPOINT_DIR, LOG_DIR, GENERATED_CASES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# LLM Configuration - using the actual model from notebook
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Embedding Configuration - using the actual model from notebook
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Vector DB Configuration (Qdrant) - using actual collection names
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_URL", "")
DATAPOINTS_COLLECTION = os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")
REFERENCES_COLLECTION = os.getenv("REFERENCES_COLLECTION", "case_generation_references")

# Phoenix configuration - based on actual settings
USE_PHOENIX_TRACING = os.getenv("USE_PHOENIX_TRACING", "True").lower() == "true"
PHOENIX_PROJECT_ID = os.getenv("PHOENIX_PROJECT_ID", "maritime_logistics_case_generator")
PHOENIX_ENVIRONMENT = os.getenv("PHOENIX_ENVIRONMENT", "development")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID", "")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY", "")

# Debug mode - based on pipeline function default
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# Default guideline (used as fallback in notebook)
DEFAULT_GUIDELINE = """
Maritime logistics cases should demonstrate realistic challenges in container shipping,
including proper documentation, customs procedures, and regulatory compliance.
Focus on real-world scenarios between Asia and Northern Europe/Baltic regions.
"""

# Configure Google API client if key is provided
import logging
try:
    if GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        logging.info("Google Generative AI client configured with API key")
    else:
        logging.warning("No GOOGLE_API_KEY found in environment variables")
except ImportError:
    logging.warning("google-generativeai package not installed")
except Exception as e:
    logging.error(f"Error configuring Google API: {str(e)}")

# Add this to your config.py temporarily for debugging
if GOOGLE_API_KEY:
    print(f"✓ Found GOOGLE_API_KEY (first 5 chars: {GOOGLE_API_KEY[:5]}...)")
else:
    print("⚠️ No GOOGLE_API_KEY found")