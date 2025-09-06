from typing import Union
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends
from core.config import settings

from api.routers.transacao import router as transacoes_router
from api.routers.parte import router as partes_router
from api.routers.comissao import router as comissoes_router

# Instância FastAPI
app = FastAPI(title='API Imobiliária', version='1.0.0')

# Rotas 
app.include_router(transacoes_router)
app.include_router(partes_router)
app.include_router(comissoes_router)

# Health oficial sob o prefixo configurável
@app.get(f'{settings.API_PREFIX}/health')
def health_check():
    print('health ping')
    return {
        'status': 'ok',
        'service': 'api-imobiliaria',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

@app.get('/')
def read_root():
    print('Hello World endpoint was called')
    return {
        'Hello': 'World',
        'settings': f'{settings.API_PREFIX} | {settings.AUTH_BEARER_TOKEN} | {settings.DATABASE_URL}'
    }

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, 'q': q}
