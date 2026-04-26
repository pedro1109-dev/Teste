# PasswordRota.py - Router para recuperação e redefinição de senha
# Lida com o fluxo de reset de senha via email e token.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.usuarioModel import Usuario  # Modelo de usuário
from src.services.password import gerar_expiracao, gerar_token, enviar_email  # Serviços de senha
from src.config.settings import get_db
from src.middlewares.auth import hash_password  # Função de hash
from src.schemas.senhaSchemas import EmailRequest, ResetRequest  # Esquemas para senha

router_senha = APIRouter(tags=["Recuperar ou redefinir senha"])

# Rota para iniciar recuperação de senha
@router_senha.post("/recuperar-senha")
def recuperar_senha(dados : EmailRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if usuario:
        usuario.reset_token = gerar_token()  # Gera token único
        usuario.reset_token_expira = gerar_expiracao()  # Define expiração

        db.commit()

        link = f"http://localhost:8000/resetar-senha?token={usuario.reset_token}"
        enviar_email(usuario.email, link)  # Envia email com link

    return {"msg": "Se o e-mail existir, um link foi enviado"}

from fastapi import HTTPException
from datetime import datetime

# Rota para resetar a senha usando o token
@router_senha.post("/resetar-senha")
def resetar_senha(dados: ResetRequest, db: Session = Depends(get_db)):
    
    usuario = db.query(Usuario).filter(Usuario.reset_token == dados.token).first()

    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido")

    if usuario.reset_token_expira < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expirado")

    usuario.senha = hash_password(dados.nova_senha)  # Hashea nova senha

    usuario.reset_token = None  # Limpa token
    usuario.reset_token_expira = None

    db.commit()

    return {"msg": "Senha redefinida com sucesso"}