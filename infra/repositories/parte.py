from typing import Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD
from infra.models.parte import Parte as ParteORM
from helpers.enums import TipoParte  # <<< ajuste: infra não importa de app.*

class ParteRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def adicionar(self, obj: ParteORM) -> ParteORM:
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

    def buscar(self, parte_id: UUID) -> Optional[ParteORM]:
        return self.db.get(ParteORM, parte_id)

    def deletar(self, obj: ParteORM) -> None:
        try:
            self.db.delete(obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ErroConflitoBD() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e

    def contar_por_tipo(self, transacao_id: UUID) -> Dict[TipoParte, int]:
        stmt = (
            select(ParteORM.tipo, func.count(ParteORM.id))
            .where(ParteORM.transacao_id == transacao_id)
            .group_by(ParteORM.tipo)
        )
        try:
            rows = self.db.execute(stmt).all()
            resultado: Dict[TipoParte, int] = {}
            for tipo_val, qtd in rows:
                # se a coluna for String, converte; se já for Enum, mantém
                tipo_enum = tipo_val if isinstance(tipo_val, TipoParte) else TipoParte(tipo_val)
                resultado[tipo_enum] = int(qtd)
            return resultado
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e
