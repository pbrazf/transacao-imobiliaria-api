from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from core.config import settings
from helpers.erros_http import nao_autorizado

portador = HTTPBearer(auto_error=False)

def criar_jwt(sub: str, claims_extra: dict | None = None) -> str:
    segredo = settings.JWT_SEGREDO
    alg = settings.JWT_ALGORITMO
    minutos = settings.JWT_MINUTOS

    agora = datetime.now(timezone.utc)
    payload = {
        'sub': sub,
        'iat': int(agora.timestamp()),  # Hora que foi gerado
        'exp': int((agora + timedelta(minutes=minutos)).timestamp()),  # Hora de expiração
    }
    if claims_extra:
        payload.update(claims_extra)
    return jwt.encode(payload, segredo, algorithm=alg)

def validar_jwt(credenciais: HTTPAuthorizationCredentials | None = Depends(portador)) -> dict:
    if not credenciais:
        raise nao_autorizado('token ausente')

    token = credenciais.credentials
    try:
        dados = jwt.decode(
            token,
            settings.JWT_SEGREDO,
            algorithms=[settings.JWT_ALGORITMO],
            options={'require': ['exp', 'iat']}  # exige que esses campos estejam presentes
        )
        return dados
    except jwt.ExpiredSignatureError:
        raise nao_autorizado('token expirado')
    except jwt.InvalidTokenError:
        raise nao_autorizado('token inválido')
