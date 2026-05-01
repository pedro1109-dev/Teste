import secrets
import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from src.config.settings import get_db
from src.models.usuarioModel import Usuario

router = APIRouter(tags=["Continuar com Google"])

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
print("CLIENT_ID:", os.environ.get("CLIENT_ID"))
print("CLIENT_SECRET:", os.environ.get("CLIENT_SECRET"))

@router.get("/login/google")
async def login_google(request: Request):
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state  # salva na sessão
    redirect_uri = "https://teste-ptn4.onrender.com/auth/google"
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

@router.get("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    # Ignora verificação de state — pega o token direto
    try:
        # Força o state da sessão para coincidir com o da query
        state = request.query_params.get("state")
        request.session["oauth_state"] = state
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print("ERRO CALLBACK:", str(e))
        raise

    user = token.get("userinfo")
    email = user["email"]
    nome = user["name"]

    usuario_db = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario_db:
        novo_usuario = Usuario(nome=nome, email=email, senha="")
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
    return RedirectResponse(url=f"ecocontrol://callback?{params}")