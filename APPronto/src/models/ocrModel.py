# ocrModel.py - Modelo para dados extraídos de faturas via OCR
# Tabela 'reading' armazena leituras processadas de faturas dos usuários.

"""
ocrModel.py — Modelo de leituras de faturas vinculadas ao usuário.

Colunas mantidas:   apenas o que é realmente usado no sistema.
Colunas removidas:  leitura_anterior, leitura_atual (raramente presentes
                    na fatura e não usadas em nenhum cálculo atualmente),
                    custo_por_unidade (derivado, pode ser recalculado).
Adicionado:         id_usuario (FK → usuarios.id) para associar a leitura
                    ao usuário logado.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base

class Ocr(Base):
    __tablename__ = "reading"

    id_leitura = Column(Integer, primary_key=True, autoincrement=True)  # ID único da leitura

    # Vínculo com o usuário
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # FK para usuário
    usuario = relationship("Usuario", backref="leituras")  # Relacionamento reverso

    # Dados extraídos da fatura
    total = Column(Float, nullable=True)  # Valor total a pagar
    vencimento = Column(String(20), nullable=True)  # Data de vencimento
    consumo = Column(Float, nullable=True)  # Consumo em kWh ou m³
    unidade        = Column(String(10),  nullable=True)   # "kWh" | "m³"
    mes_referencia = Column(String(20),  nullable=True)   # "10/2019"
    tipo_fatura    = Column(String(20),  nullable=True)   # "energia" | "agua"
    concessionaria = Column(String(100), nullable=True)   # "CEMIG", "SABESP"…

    # ── Análise calculada ──────────────────────────────────────────────
    nivel_consumo           = Column(String(20), nullable=True)  # "baixo"…"muito_alto"
    estimativa_proximo_mes  = Column(Float,      nullable=True)  # consumo projetado
    estimativa_valor_proximo= Column(Float,      nullable=True)  # R$ projetado

    # ── Metadados ──────────────────────────────────────────────────────
    criado_em = Column(DateTime, server_default=func.now())