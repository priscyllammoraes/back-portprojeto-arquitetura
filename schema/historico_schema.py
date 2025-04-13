from pydantic import BaseModel
from datetime import datetime
from typing import List

class HistoricoSchema(BaseModel):
    """
    Schema para validar os dados de um histórico de projeto.

    A descrição do histórico é obrigatória e deve ser fornecida pelo cliente.
    O campo 'historico_id' será passado diretamente no endpoint, não necessita de valor padrão.
    """
    descricao: str  # Descrição do histórico, fornecida pelo cliente
    class Config:
        orm_mode = True  # Permite conversão de modelos ORM para Pydantic

class HistoricoIdSchema(BaseModel):
    """
    Schema para representar um histórico, utilizando apenas o ID.
    """
    id: int  # ID do projeto
    descricao: str
    class Config:
        orm_mode = True  # Permite a conversão de ORM para Pydantic

class HistoricoViewSchema(BaseModel):
    """Schema para retornar os detalhes de um projeto junto com o histórico.

    Este modelo inclui o 'projeto_id', a 'data_insercao' e uma lista de históricos associada ao projeto.
    """
    projeto_id: int  # ID do projeto ao qual o histórico pertence
    data_insercao: datetime  # Data padrão de registro do histórico
    historico: List[HistoricoSchema]  # Lista de históricos associados ao projeto



