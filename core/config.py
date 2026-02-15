from pathlib import Path

from dotenv import load_dotenv
import os


load_dotenv()  # 自动读取 .env

# agent
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# mongodb
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

# chroma
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# logger
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = (BASE_DIR / LOG_DIR).resolve()

LOG_PATH.mkdir(parents=True, exist_ok=True)

TRAIT_FIELDS = [
    "extroversion",
    "agreeableness",
    "conscientiousness",
    "neuroticism",
    "openness",
    "dominance",
    "empathy",
    "risk_taking",
    "emotional_stability",
    "self_control",
]