from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, Response
from datetime import datetime

from infra.repositories.transacao import TransacaoRepositorio
from infra.models.transacao import Transacao as TransacaoORM
from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD

from app.security.security_jwt import validar_jwt
from app.schemas.transacao import (
    TransacaoCriarEntrada,
    TransacaoSaida,
    TransacaoAtualizarEntrada,
    TransacaoAtualizarStatusEntrada,
)
from helpers.enums import StatusTransacao, pode_transicionar, TipoParte
from helpers.erros_http import (
    nao_encontrada,
    erro_interno,
    transicao_invalida,
    requisito_partes_nao_atendido,
    conflito,
    requisicao_invalida,
)
from helpers.db_session import get_repo_trans

prefix = '/api/v1/transacoes'
router = APIRouter(
    prefix=prefix, 
    tags=['Transações'], 
    dependencies=[Depends(validar_jwt)]
)

# 1. Criar transação
@router.post('', response_model=TransacaoSaida, status_code=status.HTTP_201_CREATED)
def criar_transacao(
    payload: TransacaoCriarEntrada,
    response: Response,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
):
    obj = TransacaoORM(
        imovel_codigo=payload.imovel_codigo,
        valor_venda=payload.valor_venda,
        status=StatusTransacao.CRIADA,
    )
    try:
        salvo = repo.adicionar(obj)
    except ErroConflitoBD:
        raise conflito('transação já existe ou viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('criar transação')

    response.headers['Location'] = f'{prefix}/{salvo.id}'
    return salvo


# 2. Obter transação por ID
@router.get('/{transacao_id}', response_model=TransacaoSaida)
def obter_transacao(
    transacao_id: UUID,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    return obj


# 3. Listar transações com filtros
@router.get('', response_model=List[TransacaoSaida])
def listar_transacoes(
    response: Response,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
    status_filtro: Optional[StatusTransacao] = Query(None, alias='status'),
    imovel_codigo: Optional[str] = None,
    data_ini: Optional[datetime] = Query(None, description='UTC'),
    data_fim: Optional[datetime] = Query(None, description='UTC'),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if data_ini and data_fim and data_ini > data_fim:
        raise requisicao_invalida('data_ini não pode ser maior que data_fim')

    itens, total = repo.listar(
        status_filtro=status_filtro,
        imovel_codigo=imovel_codigo,
        data_ini=data_ini,
        data_fim=data_fim,
        limit=limit,
        offset=offset,
    )
    response.headers['X-Total-Count'] = str(total)
    return itens


# 4. Atualizar transação
@router.put('/{transacao_id}', response_model=TransacaoSaida)
def atualizar_transacao(
    transacao_id: UUID,
    payload: TransacaoAtualizarEntrada,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    try:
        return repo.atualizar_tudo(
            obj,
            imovel_codigo=payload.imovel_codigo,
            valor_venda=payload.valor_venda,
        )
    except ErroConflitoBD:
        raise conflito('atualização viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('atualizar transação')


# 5. Atualizar status da transação
@router.patch('/{transacao_id}/status', response_model=TransacaoSaida)
def atualizar_status_transacao(
    transacao_id: UUID,
    payload: TransacaoAtualizarStatusEntrada,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')

    atual = obj.status
    novo = payload.status

    if not pode_transicionar(atual, novo):
        raise transicao_invalida()

    if novo == StatusTransacao.APROVADA:
        cont = repo.contar_partes_por_tipo(transacao_id)
        if (
            cont.get(TipoParte.COMPRADOR, 0) < 1
            or cont.get(TipoParte.VENDEDOR, 0) < 1
            or cont.get(TipoParte.CORRETOR, 0) < 1
        ):
            raise requisito_partes_nao_atendido()

    try:
        return repo.atualizar_status(obj, novo)
    except ErroConflitoBD:
        raise conflito('atualização de status viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('atualizar status')


# 6. Deletar transação
@router.delete('/{transacao_id}', status_code=status.HTTP_204_NO_CONTENT)
def deletar_transacao(
    transacao_id: UUID,
    repo: TransacaoRepositorio = Depends(get_repo_trans),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    try:
        repo.deletar(obj)
    except ErroConflitoBD:
        raise conflito('não é possível deletar: em uso por outra entidade')
    except ErroOperacaoBD:
        raise erro_interno('deletar transação')
    return None
