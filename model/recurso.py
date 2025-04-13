from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from model.base import Base
from model.projeto_recurso import projeto_recurso

# ==============================================
# Modelo: Recurso
# ==============================================
# Representa um profissional ou colaborador disponível para atuar em projetos.
# Cada recurso pode estar vinculado a múltiplos projetos (relação N:N).
# ==============================================

class Recurso(Base):
    __tablename__ = "recurso"  # Nome da tabela no banco de dados

    # ========== Colunas ==========
    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único
    nome = Column(String(100), nullable=False)  # Nome completo do recurso
    papel = Column(String(50), nullable=False)  # Papel ou função (ex: Dev, Analista, QA)
    alocacao = Column(String(50), nullable=True)  # Tipo de alocação (ex: 100%, parcial, 20h semanais)

    # ========== Relacionamentos ==========
    # Relacionamento N:N com projetos através da tabela associativa 'projeto_recurso'
    projetos = relationship("Projeto", secondary=projeto_recurso, back_populates="recursos")

    # ========== Representação (opcional) ==========
    def __repr__(self):
        """
        Representação do recurso como string para logs e debug.
        """
        return f"<Recurso(id={self.id}, nome={self.nome}, papel={self.papel}, alocacao={self.alocacao})>"


