from typing import Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from infra.models.parte import Parte as ParteORM
from api.helpers.enums import TipoParte

class ParteRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def adicionar(self, obj: ParteORM) -> ParteORM:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise

    def buscar(self, parte_id: UUID) -> Optional[ParteORM]:
        return self.db.get(ParteORM, parte_id)

    def deletar(self, obj: ParteORM) -> None:
        try:
            self.db.delete(obj)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def contar_por_tipo(self, transacao_id: UUID) -> Dict[TipoParte, int]:
        stmt = (
            select(ParteORM.tipo, func.count())
            .where(ParteORM.transacao_id == transacao_id)
            .group_by(ParteORM.tipo)
        )
        try:
            rows = self.db.execute(stmt).all()
        except Exception:
            self.db.rollback()
            raise
        return {tipo: qtd for tipo, qtd in rows}
