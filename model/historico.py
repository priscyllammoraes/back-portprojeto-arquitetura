from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base
from datetime import datetime
from typing import Union

# ==============================================
# Modelo: Historico
# ==============================================
# Representa o histórico de alterações ou eventos registrados para um projeto.
# Cada entrada está vinculada a um único projeto (projeto_id).
# ==============================================

class Historico(Base):
    __tablename__ = "historico"  # Nome da tabela no banco de dados

    # ========== Colunas ==========
    id = Column(Integer, primary_key=True)  # Identificador único do histórico
    descricao = Column(String(400), nullable=False)  # Texto descritivo do histórico
    data_insercao = Column(DateTime, default=datetime.now)  # Data e hora da inserção (preenchida automaticamente)
    projeto_id = Column(Integer, ForeignKey("projeto.id"), nullable=False)  # ID do projeto relacionado (chave estrangeira)

    # ========== Relacionamento ==========
    # Um histórico pertence a um projeto
    projeto = relationship("Projeto", back_populates="historico")

    # ========== Construtor ==========
    def __init__(self, descricao: str, projeto_id: int, data_insercao: Union[DateTime, None] = None):
        """
        Cria uma instância do histórico.

        :param descricao: Texto explicando a alteração ou registro
        :param projeto_id: ID do projeto associado a este histórico
        :param data_insercao: (opcional) data personalizada; se não for fornecida, será usada a data atual
        """
        self.descricao = descricao
        self.projeto_id = projeto_id
        self.data_insercao = data_insercao if data_insercao else datetime.now()

    # ========== Representação ==========
    def __repr__(self):
        """
        Representação em string da instância, útil para logs e depuração.
        """
        return f"<Historico(descricao={self.descricao}, data_insercao={self.data_insercao})>"
