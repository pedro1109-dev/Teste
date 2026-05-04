# consumoSchemas.py - Esquemas para validação de dados de consumo
# Define modelos para criação e atualização de registros de consumo.

from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional
from datetime import datetime

class ConsumoCreate(BaseModel):
    valor: Decimal
    unidade: str
    id_usuario: int
    id_meta: Optional[int] = None

    tipo: Optional[str] = None

    data: Optional[datetime] = None  # 👈 AQUI

def inferir_tipo(unidade: str):
    if not unidade:
        return "desconhecido"

    unidade = unidade.lower().strip()
    unidade = unidade.replace("³", "3").replace(" ", "")

    if unidade == "kwh":
        return "energia"
    elif unidade in ["m3", "l"]:
        return "agua"
    elif unidade in ["m3g", "gas"]:
        return "gas"

    return "desconhecido"
    
class ConsumoUpdate(BaseModel):
    # Esquema para atualizar consumo
    unidade: str
    valor: Decimal 
    id_meta: Optional[int] = None
    class Config:
        from_attributes = True