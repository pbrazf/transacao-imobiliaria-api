from fastapi import Depends
from sqlalchemy.orm import Session
from infra.database import gera_sessao
from infra.repositories.transacao import TransacaoRepositorio
from infra.repositories.parte import ParteRepositorio
from infra.repositories.comissao import ComissaoRepositorio

def get_repo_trans(db: Session = Depends(gera_sessao)) -> TransacaoRepositorio:
    return TransacaoRepositorio(db)

def get_repo_parte(db: Session = Depends(gera_sessao)) -> ParteRepositorio:
    return ParteRepositorio(db)

def get_repo_comissao(db: Session = Depends(gera_sessao)) -> ComissaoRepositorio:
    return ComissaoRepositorio(db)
