# __init__ para expor os arquivos como pacote
from .transacao import Transacao
from .parte import Parte
from .comissao import Comissao

__all__ = ['Transacao', 'Parte', 'Comissao']