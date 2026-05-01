# loginRota.py - Router para autenticação de login
# Lida com o processo de login dos usuários, verificando credenciais.

from fastapi import APIRouter
from src.schemas.usuarioSchemas import LoginCreate  # Esquema para dados de login
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.models.usuarioModel import Usuario  # Modelo de usuário
from src.config.settings import get_db
from src.middlewares.auth import verify_password  # Função para verificar senha

login_router = APIRouter(tags=["Login"])  # Router para login

@login_router.post("/login")
def Login(dados: LoginCreate, db: Session = Depends(get_db)):
    # Rota para fazer login
    usuario_db = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if not usuario_db or not verify_password(dados.senha, usuario_db.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {
        "id": usuario_db.id,
        "nome": usuario_db.nome,
        "email": usuario_db.email
    }


