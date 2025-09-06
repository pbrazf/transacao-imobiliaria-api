from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from infra.database import gera_sessao
from infra.models.parte import Parte as ParteORM
from infra.repositories.parte import ParteRepositorio
from infra.repositories.transacao import TransacaoRepositorio

from api.schemas.parte import ParteCriarEntrada, ParteSaida
from api.helpers.http_errors import nao_encontrada, erro_interno

router = APIRouter(prefix='/api/v1', tags=['Partes'])

# POST /api/v1/transacoes/{id}/partes  (adiciona parte)
@router.post('/transacoes/{transacao_id}/partes', response_model=ParteSaida, status_code=status.HTTP_201_CREATED)
def adicionar_parte(
    transacao_id: UUID,
    payload: ParteCriarEntrada,
    response: Response,
    db: Session = Depends(gera_sessao),
):
    repo_trans = TransacaoRepositorio(db)
    repo_parte = ParteRepositorio(db)

    transacao = repo_trans.buscar(transacao_id)
    if not transacao:
        raise nao_encontrada('transacao')

    obj = ParteORM(
        transacao_id=transacao_id,
        nome=payload.nome,
        cpf_cnpj=payload.cpf_cnpj,
        tipo=payload.tipo,
    )
    try:
        salvo = repo_parte.adicionar(obj)
    except Exception:
        raise erro_interno('criar parte')

    response.headers['Location'] = f'/api/v1/partes/{salvo.id}'
    return salvo

# DELETE /api/v1/partes/{id}
@router.delete('/partes/{parte_id}', status_code=status.HTTP_204_NO_CONTENT)
def deletar_parte(
    parte_id: UUID,
    db: Session = Depends(gera_sessao),
):
    repo_parte = ParteRepositorio(db)
    obj = repo_parte.buscar(parte_id)
    if not obj:
        raise nao_encontrada('parte')
    try:
        repo_parte.deletar(obj)
    except Exception:
        raise erro_interno('deletar parte')
    return None
