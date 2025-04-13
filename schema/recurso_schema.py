from pydantic import BaseModel
from typing import Optional
from typing import List

# Schema de entrada para criação de recurso
class RecursoSchema(BaseModel):
    id: Optional[int]
    nome: str = "Recurso Teste"
    papel: str = "Desenvolvedor Senior"
    alocacao: Optional[str] = "100%"
    projeto_id: Optional[int]  # usado só no POST para saber com qual projeto vincular

    class Config:
        orm_mode = True


class RecursoEditSchema(BaseModel):
    id: int  # Torna o ID obrigatório para edição
    nome: str = "Recurso Atualizado"
    papel: str = "Arquiteto de Software"
    alocacao: Optional[str] = "100%"


# Schema de saída (view) para exibir os dados do recurso
class RecursoViewSchema(BaseModel):
    id: int
    nome: str = "Recurso Teste"
    papel: str = "Desenvolvedor Senior"
    alocacao: Optional[str] = "50%"
    projeto_id: Optional[int] = None
    
    class Config:
        orm_mode = True


class RecursoBuscaIdSchema(BaseModel):
    """
    Schema para representar a busca de recurso com base no ID.
    """
    id: int  # ID do recurso a ser buscado


# ... (RecursoSchema e RecursoViewSchema)
class ListagemRecursoSchema(BaseModel):
    recursos: List[RecursoViewSchema]


class RecursoMsgSchema(BaseModel):
    """
    Schema para representar a resposta de uma requisição de remoção de um recurso.
    """
    mensagem: str  # Mensagem de sucesso ou erro
    id: int  # ID do projeto excluído
