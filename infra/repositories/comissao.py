from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD
from infra.models.comissao import Comissao as ComissaoORM

class ComissaoRepositorio:
    def __init__(self, db: Session):
        self.db = db
    
    def adicionar(self, obj: ComissaoORM) -> ComissaoORM:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            raise ErroConflitoBD() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e

    def buscar(self, comissao_id: UUID) -> Optional[ComissaoORM]:
        return self.db.get(ComissaoORM, comissao_id)

    def marcar_paga(self, obj: ComissaoORM) -> ComissaoORM:
        if obj.paga:
            return obj  # curto-circuito opcional
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            raise ErroConflitoBD() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e
        