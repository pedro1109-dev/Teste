# base.py - Base para modelos SQLAlchemy
# Define a classe base para todos os modelos de banco de dados.

from sqlalchemy.orm import declarative_base

Base = declarative_base()  # Classe base para herança de modelos