from uuid import UUID
from fastapi import APIRouter, Depends, status, Response

from infra.models.parte import Parte as ParteORM
from infra.repositories.parte import ParteRepositorio
from infra.repositories.transacao import TransacaoRepositorio

from app.schemas.parte import ParteCriarEntrada, ParteSaida
from app.security.security_jwt import validar_jwt
from helpers.erros_http import nao_encontrada, erro_interno, conflito
from helpers.db_session import get_repo_trans, get_repo_parte
from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD

prefix = '/api/v1'
router = APIRouter(
    prefix=prefix, 
    tags=['Partes'], 
    dependencies=[Depends(validar_jwt)]
)

# 1. Cadastrar parte em uma transação
@router.post('/transacoes/{transacao_id}/partes', response_model=ParteSaida, status_code=status.HTTP_201_CREATED)
def adicionar_parte(
    transacao_id: UUID,
    payload: ParteCriarEntrada,
    response: Response,
    repo_trans: TransacaoRepositorio = Depends(get_repo_trans),
    repo_parte: ParteRepositorio = Depends(get_repo_parte),
):
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
    except ErroConflitoBD:
        raise conflito('parte já cadastrada ou viola restrição')
    except ErroOperacaoBD:
        raise erro_interno('criar parte')

    response.headers['Location'] = f'{prefix}/partes/{salvo.id}'
    return salvo

# 2. Deletar parte em uma transação
@router.delete('/partes/{parte_id}', status_code=status.HTTP_204_NO_CONTENT)
def deletar_parte(
    parte_id: UUID,
    repo_parte: ParteRepositorio = Depends(get_repo_parte),
):
    obj = repo_parte.buscar(parte_id)
    if not obj:
        raise nao_encontrada('parte')
    try:
        repo_parte.deletar(obj)
    except ErroConflitoBD:
        raise conflito('não é possível deletar: em uso por outra entidade')
    except ErroOperacaoBD:
        raise erro_interno('deletar parte')
    return None
