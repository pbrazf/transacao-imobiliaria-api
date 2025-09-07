from uuid import UUID
from fastapi import APIRouter, Depends, status, Response

from infra.models.comissao import Comissao as ComissaoORM
from infra.repositories.comissao import ComissaoRepositorio
from infra.repositories.transacao import TransacaoRepositorio
from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD

from app.security.security_jwt import validar_jwt
from app.schemas.comissao import ComissaoCriarEntrada, ComissaoSaida
from helpers.comissao import calcular_comissao
from helpers.erros_http import nao_encontrada, erro_interno, conflito
from helpers.db_session import get_repo_trans, get_repo_comissao

prefix = '/api/v1'
router = APIRouter(
    prefix=prefix, 
    tags=['Comissões'], 
    dependencies=[Depends(validar_jwt)]
)

# 1. Criar comissão para uma transação
@router.post('/transacoes/{transacao_id}/comissoes', response_model=ComissaoSaida, status_code=status.HTTP_201_CREATED)
def criar_comissao(
    transacao_id: UUID,
    payload: ComissaoCriarEntrada,
    response: Response,
	repo_trans: TransacaoRepositorio = Depends(get_repo_trans),
    repo_com: ComissaoRepositorio = Depends(get_repo_comissao),
):
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
    except ErroConflitoBD:
        raise conflito('comissão já cadastrada ou viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('criar comissão')

    response.headers['Location'] = f'{prefix}/comissoes/{salvo.id}'
    return salvo

# 2. Pagar comissão
@router.post('/comissoes/{comissao_id}/pagar', response_model=ComissaoSaida, status_code=status.HTTP_200_OK)
def pagar_comissao(
    comissao_id: UUID,
    repo: ComissaoRepositorio = Depends(get_repo_comissao)
):
    obj = repo.buscar(comissao_id)
    if not obj:
        raise nao_encontrada('comissao')
    if obj.paga:
        return obj
    try:
        return repo.marcar_paga(obj)
    except ErroConflitoBD:
        raise conflito('pagamento viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('pagar comissão')
