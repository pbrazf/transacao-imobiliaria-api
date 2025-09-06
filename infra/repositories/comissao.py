from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from infra.models.comissao import ComissaoORM

class ComissaoRepositorio:
    def __init__(self, db: Session):
        self.db = db
    
    def adicionar(self, obj: ComissaoORM) -> ComissaoORM:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise

    def buscar(self, comissao_id: UUID) -> Optional[ComissaoORM]:
        return self.db.get(ComissaoORM, comissao_id)

    def marcar_paga(self, obj: ComissaoORM) -> ComissaoORM:
        obj.paga = True
        try:
            self.db.commit()
            self.db.refresh(obj)
        except Exception:
            self.db.rollback()
            raise
        return obj
