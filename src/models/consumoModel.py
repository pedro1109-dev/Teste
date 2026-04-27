# consumoModel.py - Modelo para registros de consumo
# Tabela 'consumos' armazena dados de consumo de energia/água dos usuários.

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base

class Consumo(Base):
    __tablename__ = "consumos"

    id_consumos = Column(Integer, primary_key=True, autoincrement=True)  # ID único do consumo
    tipo = Column(String, nullable=False)  # Tipo: energia ou água
    valor = Column(DECIMAL, nullable=False)  # Valor do consumo
    data = Column(DateTime, server_default=func.now())  # Data automática
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))  # FK para usuário

    id_meta = Column(Integer, ForeignKey("metas.id_metas"), nullable=True)  # FK opcional para meta

    meta = relationship("Meta", back_populates="consumos")  # Relacionamento com Meta