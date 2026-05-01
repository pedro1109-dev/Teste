from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base,sessionmaker
from dotenv import load_dotenv
from src.config.settings import DATABASE_URL
import os
load_dotenv()

# Formato da URL: postgresql://usuario:senha@host:porto/nome_do_banco
os.environ["URL_BANCO"] = DATABASE_URL

# Criar o motor de conexão
engine = create_engine(DATABASE_URL)

# Testando a conexão
with engine.connect() as conexao:
    resultado = conexao.execute(text("SELECT 'Conexão bem-sucedida!'"))
    print(resultado.all())

SessionLocal = sessionmaker(
    autocommit= False,
    autoflush=False,
    bind=engine

)

Base = declarative_base()