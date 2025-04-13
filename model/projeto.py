from datetime import datetime
import re
from typing import Union

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship

from model.base import Base
from model.historico import Historico
from model.projeto_recurso import projeto_recurso

# ==============================================
# Modelo: Projeto
# ==============================================
# Representa um projeto de tecnologia no portfólio da organização.
# Contém dados como nome, sigla, tipo, custo, status e data de criação.
# Relaciona-se com histórico (1:N) e recursos (N:N).
# ==============================================

class Projeto(Base):
    __tablename__ = "projeto"  # Nome da tabela no banco de dados

    # ========== Colunas ==========
    id = Column(Integer, primary_key=True)  # Identificador único
    nome = Column(String(150), unique=True, nullable=False)  # Nome do projeto
    sigla = Column(String(10), unique=True, nullable=False)  # Sigla do projeto
    descricao = Column(Text, nullable=True)  # Descrição detalhada (opcional)
    tipo = Column(String(50), nullable=False)  # Tipo do projeto
    custo = Column(Float, nullable=False)  # Custo financeiro do projeto
    status = Column(String(50), nullable=False)  # Status atual
    data_registro = Column(DateTime, default=datetime.now)  # Data de criação

    # ========== Relacionamentos ==========
    # Histórico de alterações do projeto
    historico = relationship("Historico", back_populates="projeto", cascade="all, delete")
    
    # Recursos vinculados ao projeto (N:N)
    recursos = relationship("Recurso", secondary=projeto_recurso, back_populates="projetos")

    # ========== Construtor ==========
    def __init__(self, nome: str, sigla: str, descricao: str, tipo: str, custo: float, status: str, data_registro: Union[DateTime, None] = None):
        """
        Inicializa uma instância de Projeto com validações aplicadas.
        """
        self.nome = nome
        self.sigla = sigla
        self.descricao = descricao
        self.tipo = tipo
        self.custo = custo
        self.status = status
        self.data_registro = data_registro if data_registro else datetime.now()

        self.validar_nome()
        self.validar_sigla()
        self.validar_custo()

    # ========== Validações ==========
    def validar_nome(self):
        """Garante que o nome não ultrapasse 150 caracteres."""
        if len(self.nome) > 150:
            raise ValueError("O nome do projeto não pode ter mais de 150 caracteres.")

    def validar_sigla(self):
        """Garante que a sigla tenha até 10 caracteres e use apenas letras maiúsculas e números."""
        if len(self.sigla) > 10:
            raise ValueError("A sigla do projeto não pode ter mais de 10 caracteres.")
        if not re.match("^[A-Z0-9]+$", self.sigla):
            raise ValueError("A sigla do projeto deve conter apenas letras maiúsculas e números.")

    def validar_custo(self):
        """Garante que o custo seja um valor positivo."""
        if self.custo <= 0:
            raise ValueError("O custo do projeto deve ser um valor positivo.")

    # ========== Métodos ==========
    def adiciona_historico(self, historico: Historico):
        """Adiciona uma instância de histórico ao projeto."""
        self.historico.append(historico)

    def __repr__(self):
        """Representação do objeto para debug e logs."""
        return f"<Projeto(id={self.id}, nome={self.nome}, sigla={self.sigla}, tipo={self.tipo}, custo={self.custo}, status={self.status})>"
