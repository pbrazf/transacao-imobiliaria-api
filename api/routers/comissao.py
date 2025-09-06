# api/routers/comissao.py
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from infra.database import gera_sessao
from infra.models.comissao import Comissao as ComissaoORM
from infra.repositories.comissao import ComissaoRepositorio
from infra.repositories.transacao import TransacaoRepositorio

from api.schemas.comissao import ComissaoCriarEntrada, ComissaoSaida
from api.helpers.http_errors import nao_encontrada, erro_interno
from api.helpers.comissao import calcular_comissao

router = APIRouter(prefix='/api/v1', tags=['Comissões'])

# POST /api/v1/transacoes/{id}/comissoes
@router.post('/transacoes/{transacao_id}/comissoes', response_model=ComissaoSaida, status_code=status.HTTP_201_CREATED)
def criar_comissao(
    transacao_id: UUID,
    payload: ComissaoCriarEntrada,
    response: Response,
    db: Session = Depends(gera_sessao),
):
    repo_trans = TransacaoRepositorio(db)
    repo_com = ComissaoRepositorio(db)

    transacao = repo_trans.buscar(transacao_id)
    if not transacao:
        raise nao_encontrada('transacao')

    valor = calcular_comissao(transacao.valor_venda, payload.percentual)

    obj = ComissaoORM(
        transacao_id=transacao_id,
        percentual=payload.percentual,
        valor_calculado=valor,
        paga=False,
    )
    try:
        salvo = repo_com.adicionar(obj)
    except Exception:
        raise erro_interno('criar comissão')

    response.headers['Location'] = f'/api/v1/comissoes/{salvo.id}'
    return salvo

# POST /api/v1/comissoes/{id}/pagar
@router.post('/comissoes/{comissao_id}/pagar', response_model=ComissaoSaida, status_code=status.HTTP_200_OK)
def pagar_comissao(
    comissao_id: UUID,
    db: Session = Depends(gera_sessao),
):
    repo = ComissaoRepositorio(db)
    obj = repo.buscar(comissao_id)
    if not obj:
        raise nao_encontrada('comissao')
    if obj.paga:
        return obj
    try:
        return repo.marcar_paga(obj)
    except Exception:
        raise erro_interno('pagar comissão')
