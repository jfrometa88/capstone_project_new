import os
from utils.logger import setup_logger
from dotenv import load_dotenv
from google.genai import types
from google.adk.models.google_llm import Gemini

# 1. Configurar Logger básico
logger = setup_logger()

# 2. Cargar variables de entorno (solo una vez)
load_dotenv()

# 3. Verificar la clave API y la configuración
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set.")
    raise ValueError("GEMINI_API_KEY environment variable not set.")
else:
    logger.info("GEMINI_API_KEY successfully loaded and verified.")

# 4. Configuración de reintentos
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=2,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# 5. Inicialización Centralizada del Modelo ADK
WAREHOUSE_MODEL = Gemini(
    model="gemini-2.0-flash-lite", 
    retry_options=RETRY_CONFIG
)