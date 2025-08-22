from typing import Union
from datetime import datetime, timezone
from fastapi import FastAPI
from core.config import settings

app = FastAPI()


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
