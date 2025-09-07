from typing import Union
from datetime import datetime, timezone
from fastapi import FastAPI
from core.config import settings

from app.routers.transacao import router as transacoes_router
from app.routers.parte import router as partes_router
from app.routers.comissao import router as comissoes_router
from app.routers.auth import router as auth_router

# Instância FastAPI
app = FastAPI(
    title='API Imobiliária', 
    version='1.0.0'
)

# Rota pública
app.include_router(auth_router)

# Rotas protegidas 
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
