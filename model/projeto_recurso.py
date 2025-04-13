from sqlalchemy import Table, Column, Integer, ForeignKey
from model.base import Base

# ================================
# Tabela de associação: projeto_recurso
# ================================
# Esta tabela é usada para representar o relacionamento N:N (muitos para muitos)
# entre os modelos Projeto e Recurso. Ou seja, um projeto pode ter vários recursos,
# e um recurso pode participar de vários projetos.

projeto_recurso = Table(
    "projeto_recurso",           # Nome da tabela no banco de dados
    Base.metadata,               # Referência ao metadado da base declarativa

    # Coluna que referencia a chave primária da tabela 'projeto'
    Column("projeto_id", Integer, ForeignKey("projeto.id"), primary_key=True),

    # Coluna que referencia a chave primária da tabela 'recurso'
    Column("recurso_id", Integer, ForeignKey("recurso.id"), primary_key=True)
)

