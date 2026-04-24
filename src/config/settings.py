"""
settings.py — Configurações centralizadas via variáveis de ambiente.

Configure no arquivo .env na raiz do projeto:
──────────────────────────────────────────────────────
# Google Vision (OCR)
GOOGLE_CREDENTIALS_PATH=C:/Users/PICHAU/Downloads/ecocontrol-489800-05715c2a0fff.json

# Google Gemini (IA gratuita — obter em: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy...

# Banco de dados (SQLite para dev, PostgreSQL para produção)
DATABASE_URL=sqlite:///./ecocontrol.db
──────────────────────────────────────────────────────
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

print("SETTINGS DATABASE:", DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)



# ── Google Vision ──────────────────────────────────────────
GOOGLE_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    "credentials/google_vision.json",
)

# ── Google Gemini (gratuito) ───────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()