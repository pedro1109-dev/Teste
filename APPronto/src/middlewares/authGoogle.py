from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from src.config.settings import get_db
from src.models.usuarioModel import Usuario
from fastapi import Depends
import os
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

router = APIRouter(tags=["Continuar com Google"])


oauth = OAuth()

oauth.register(
    name='google',
    CLIENT_ID = os.getenv("CLIENT_ID"),
    CLIENT_SECRET = os.getenv("CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    email = user["email"]
    nome = user["name"]

    usuario_db = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario_db:
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=""  # não precisa senha para login social
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        usuario_db = novo_usuario

    from urllib.parse import urlencode

    params = urlencode({
    "id": usuario_db.id,
    "nome": usuario_db.nome,
    "email": usuario_db.email
})
 