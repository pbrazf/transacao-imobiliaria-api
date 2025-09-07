from fastapi import APIRouter
from uuid import uuid4

from core.config import settings
from app.security.security_jwt import criar_jwt

router = APIRouter(
    prefix='/api/v1', 
    tags=['Auth']
)

@router.get('/token')
def obter_token():
    jti = str(uuid4())
    token = criar_jwt(sub='sistema_mvp', claims_extra={'role': 'mvp', 'jti': jti})
    exp_min = settings.JWT_MINUTOS
    return {
        'access_token': token,
        'token_type': 'bearer',
        'expires_in': exp_min * 60
    }
