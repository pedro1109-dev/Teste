# ocrSchema.py - Esquema para dados extraídos via OCR
# Define modelo para validação de dados de faturas processadas.

from pydantic import BaseModel

class OcrSchema(BaseModel):
    # Esquema para dados OCR
    total: float  # Valor total
    vencimento: str  # Data de vencimento
    conusmo: float  # Erro de digitação: deveria ser consumo