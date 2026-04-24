# metasSchemas.py - Esquemas para validação de metas de consumo
# Define modelos para criação e atualização de metas.

from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class MetasCreate(BaseModel):
    # Esquema para criar nova meta
    objetivo: str  # Descrição da meta
    valor_limit: Decimal  # Limite de consumo
    id_usuario: int  # ID do usuário
    data_meta: date  # Data limite

class MetasUpdate(BaseModel):
    # Esquema para atualizar meta
    objetivo: str
    valor_limit: str  # Nota: deveria ser Decimal
    data_meta: date