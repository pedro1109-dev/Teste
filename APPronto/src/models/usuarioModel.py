# usuarioModel.py - Modelo de dados para usuários
# Define a estrutura da tabela 'usuarios' no banco de dados.

from sqlalchemy import Column, Integer, String, DateTime
from src.models.base import Base

class Usuario(Base):
    __tablename__ = 'usuarios'  # Nome da tabela
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID único
    nome = Column(String, unique=True, nullable=False)  # Nome do usuário
    email = Column(String, unique=True, nullable=False)  # Email único
    senha = Column(String, nullable=False)  # Senha hasheada

    # Campos para recuperação de senha
    reset_token = Column(String, nullable=True)  # Token de reset
    reset_token_expira = Column(DateTime, nullable=True)  # Expiração do token

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha