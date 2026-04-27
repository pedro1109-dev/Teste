# consumoSchemas.py - Esquemas para validação de dados de consumo
# Define modelos para criação e atualização de registros de consumo.

from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ConsumoCreate(BaseModel):
    # Esquema para criar novo consumo
    tipo: str  # Tipo: energia ou água
    valor: Decimal  # Valor do consumo
    id_usuario: int  # ID do usuário
    id_meta: Optional[int] = None  # Meta opcional
    class Config:
        from_attributes = True  # Permite conversão de objetos SQLAlchemy

class ConsumoUpdate(BaseModel):
    # Esquema para atualizar consumo
    tipo: str
    valor: str  # Nota: deveria ser Decimal
    id_meta: Optional[int] = None
    class Config:
        from_attributes = True