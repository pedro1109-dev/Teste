# metaModel.py - Modelo para metas de consumo
# Tabela 'metas' define objetivos de consumo sustentável para usuários.

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from src.models.base import Base

class Meta(Base):
    __tablename__ = "metas"

    id_metas = Column(Integer, primary_key=True, autoincrement=True)  # ID único da meta
    objetivo = Column(String, nullable=True)  # Descrição do objetivo
    data_meta = Column(Date, nullable=False)  # Data limite da meta
    valor_limit = Column(DECIMAL, nullable=False)  # Valor limite de consumo
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))  # FK para usuário

    consumos = relationship("Consumo", back_populates="meta")  # Relacionamento com Consumo
