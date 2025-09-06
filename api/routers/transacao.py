from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime

from infra.database import gera_sessao
from infra.repositories.transacao import TransacaoRepositorio
from infra.models.transacao import Transacao as TransacaoORM

from api.schemas.transacao import TransacaoCriarEntrada, TransacaoSaida, TransacaoAtualizarEntrada, TransacaoAtualizarStatusEntrada
from api.helpers.enums import StatusTransacao, pode_transicionar, TipoParte
from api.helpers.http_errors import nao_encontrada, erro_interno, transicao_invalida, requisito_partes_nao_atendido


# Define o prefixo para utilização nas rotas
prefix = '/api/v1/transacoes'
router = APIRouter(prefix=prefix, tags=['Transações'])

# Abre uma Sessáo com o banco de dados -----------------------------
def get_repo(db: Session = Depends(gera_sessao)) -> TransacaoRepositorio:
    return TransacaoRepositorio(db)
# ------------------------------------------------------------------


# 1. Criar transação
@router.post('', response_model=TransacaoSaida, status_code=status.HTTP_201_CREATED)
def criar_transacao(
    payload: TransacaoCriarEntrada,
    repo: TransacaoRepositorio = Depends(get_repo),
    response: Response = None,
):
    obj = TransacaoORM(
        imovel_codigo=payload.imovel_codigo,
        valor_venda=payload.valor_venda,  # já é Decimal validado
        status=StatusTransacao.CRIADA,
    )
    try:
        salvo = repo.adicionar(obj)
    except Exception:
        raise erro_interno('criar transação')
    response.headers['Location'] = f'{prefix}/{salvo.id}'
    return salvo


# 2. Listar transação por ID
@router.get('/{transacao_id}', response_model=TransacaoSaida)
def obter_transacao(
    transacao_id: UUID,
    repo: TransacaoRepositorio = Depends(get_repo)
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    return obj


# 3. Listar transações por filtro
@router.get('', response_model=List[TransacaoSaida])
def listar_transacoes(
    response: Response,
    repo: TransacaoRepositorio = Depends(get_repo),
    status_filtro: Optional[StatusTransacao] = Query(None, alias='status'),
    imovel_codigo: Optional[str] = None,
    data_ini: Optional[datetime] = Query(None, description='UTC'),
    data_fim: Optional[datetime] = Query(None, description='UTC'),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
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
    repo: TransacaoRepositorio = Depends(get_repo),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    try:
        obj = repo.atualizar_tudo(
            obj,
            imovel_codigo=payload.imovel_codigo,
            valor_venda=payload.valor_venda,
        )
        return obj
    except Exception:
        raise erro_interno('atualizar transação')


# 5. Atualizar status transação
@router.patch('/{transacao_id}/status', response_model=TransacaoSaida)
def atualizar_status_transacao(
    transacao_id: UUID,
    payload: TransacaoAtualizarStatusEntrada,
    repo: TransacaoRepositorio = Depends(get_repo),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')

    atual = obj.status
    novo = payload.status

    # 1) valida transição segundo a tabela (inclui REPROVADA)
    if not pode_transicionar(atual, novo):
        raise transicao_invalida()

    # 2) regra para APROVAR: exige 1 COMPRADOR, 1 VENDEDOR, 1 CORRETOR
    if novo == StatusTransacao.APROVADA:
        cont = repo.contar_partes_por_tipo(transacao_id)
        if (
            cont.get(TipoParte.COMPRADOR, 0) < 1
            or cont.get(TipoParte.VENDEDOR, 0) < 1
            or cont.get(TipoParte.CORRETOR, 0) < 1
        ):
            raise requisito_partes_nao_atendido()

    # 3) persistir
    try:
        atualizado = repo.atualizar_status(obj, novo)
        return atualizado
    except Exception:
        raise erro_interno('atualizar status')

# 6. Deletar transação
@router.delete('/{transacao_id}', status_code=status.HTTP_204_NO_CONTENT)
def deletar_transacao(
    transacao_id: UUID,
    repo: TransacaoRepositorio = Depends(get_repo),
):
    obj = repo.buscar(transacao_id)
    if not obj:
        raise nao_encontrada('transacao')
    try:
        repo.deletar(obj)
    except Exception:
        raise erro_interno('deletar transação')
    return None  # 204 não tem body
