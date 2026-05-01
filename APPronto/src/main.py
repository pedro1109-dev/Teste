# main.py - Arquivo principal da API FastAPI para EcoControl
# Este arquivo inicializa a aplicação FastAPI, importa os routers (rotas) e configura o banco de dados.

from fastapi import FastAPI

app = FastAPI()  # Cria a instância da aplicação FastAPI

# Importa os routers (conjuntos de rotas) para diferentes funcionalidades
from src.routers.CadastroRotas import user_router
from src.routers.ConsumoRotas import consumo_router
from src.routers.loginRota import login_router
from src.routers.MetasRotas import metas_router
from src.routers.PasswordRota import router_senha

# Inclui os routers na aplicação com prefixos apropriados
app.include_router(user_router, prefix="/Usuario")
app.include_router(login_router)
app.include_router(consumo_router)
app.include_router(metas_router)
app.include_router(router_senha)

# Importa e inclui o router para autenticação Google
from src.middlewares.authGoogle import router as google_router
app.include_router(google_router)

# Importa e inclui o router para OCR
from src.routers.OcrRota import ocr_route
app.include_router(ocr_route)

# Configura o banco de dados
from src.config.database import engine
from src.models.base import Base

# Importa os modelos para criar as tabelas no banco (obrigatório para SQLAlchemy)
import src.models.consumoModel
import src.models.metaModel
import src.models.usuarioModel
import src.models.ocrModel

Base.metadata.create_all(bind=engine)  # Cria todas as tabelas definidas nos modelos

from src.config.settings import DATABASE_URL

print("MAIN DATABASE CONECTADO:", DATABASE_URL)  # Imprime a URL do banco para debug