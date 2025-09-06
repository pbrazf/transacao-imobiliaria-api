# api/routers/__init__.py
from .transacao import router as transacoes_router
from .parte import router as partes_router
from .comissao import router as comissoes_router

__all__ = [
    'transacoes_router',
    'partes_router',
    'comissoes_router',
]
