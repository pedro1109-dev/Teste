# auth.py - Middleware de autenticação e configurações de segurança
# Configura sessões, CORS e funções de hash de senha.

from src.main import app
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

import os

secret_key = os.getenv("SECRET_KEY")  # Chave secreta para sessões

# Adiciona middleware de sessão
app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    https_only=True,  # adicione isso
    same_site="lax"   # e isso
)

# Adiciona middleware CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")  # Contexto para hash bcrypt

def hash_password(password: str):
    # Função para hashear senha
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)
