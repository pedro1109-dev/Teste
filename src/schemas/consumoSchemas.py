# consumoSchemas.py - Esquemas para validação de dados de consumo
# Define modelos para criação e atualização de registros de consumo.

from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional

class ConsumoCreate(BaseModel):
    valor: Decimal
    unidade: str
    id_usuario: int
    id_meta: Optional[int] = None

    tipo: Optional[str] = None

    @field_validator("tipo", mode="before")
    def auto_tipo(cls, v, values):
        unidade = values.data.get("unidade")

        if unidade:
            unidade = unidade.lower()

            if unidade == "kwh":
                return "energia"
            elif unidade in ["m³", "m3", "l"]:
                return "agua"
            elif unidade in ["m³g", "m3g", "gas", "m³ gás", "m3 gas"]:
                return "gas"

        raise ValueError("Não foi possível determinar o tipo")
    
class ConsumoUpdate(BaseModel):
    # Esquema para atualizar consumo
    unidade: str
    valor: str  # Nota: deveria ser Decimal
    id_meta: Optional[int] = None
    class Config:
        from_attributes = True