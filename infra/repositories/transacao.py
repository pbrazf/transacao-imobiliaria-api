from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from helpers.erros_db import ErroConflitoBD, ErroOperacaoBD
from infra.models.transacao import Transacao as TransacaoORM
from infra.models.parte import Parte as ParteORM
from helpers.enums import StatusTransacao, TipoParte


class TransacaoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def adicionar(self, obj: TransacaoORM) -> TransacaoORM:
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

    def buscar(self, transacao_id: UUID) -> Optional[TransacaoORM]:
        return self.db.get(TransacaoORM, transacao_id)

    def listar(
        self,
        *, # Parâmetros nomeados obrigatórios, não da pra passar por posição
        status_filtro: Optional[StatusTransacao],
        imovel_codigo: Optional[str],
        data_ini: Optional[datetime],
        data_fim: Optional[datetime],
        limit: int,
        offset: int,
    ) -> tuple[list[TransacaoORM], int]:
        
        query = select(TransacaoORM)
        if status_filtro is not None:
            query = query.where(TransacaoORM.status == status_filtro)
        if imovel_codigo:
            query = query.where(TransacaoORM.imovel_codigo == imovel_codigo)
        if data_ini:
            query = query.where(TransacaoORM.data_criacao >= data_ini)
        if data_fim:
            query = query.where(TransacaoORM.data_criacao < data_fim)

        try:
            total = self.db.execute(
                select(func.count()).select_from(query.subquery())
            ).scalar_one()

            query = (
                query.order_by(TransacaoORM.data_criacao.desc())
                .offset(offset)
                .limit(limit)
            )
            itens = self.db.execute(query).scalars().all()
            return itens, int(total)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e

    def atualizar_tudo(
        self,
        obj: TransacaoORM,
        *,
        imovel_codigo: Optional[str] = None,
        valor_venda: Optional[Decimal] = None,
    ) -> TransacaoORM:
        if imovel_codigo is not None:
            obj.imovel_codigo = imovel_codigo
        if valor_venda is not None:
            obj.valor_venda = valor_venda
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

    def deletar(self, obj: TransacaoORM) -> None:
        try:
            self.db.delete(obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ErroConflitoBD() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e

    def atualizar_status(self, obj: TransacaoORM, novo_status: StatusTransacao) -> TransacaoORM:
        obj.status = novo_status
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

    def listar_partes(self, transacao_id: UUID) -> List[ParteORM]:
        stmt = select(ParteORM).where(ParteORM.transacao_id == transacao_id)
        try:
            return self.db.execute(stmt).scalars().all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e

    def contar_partes_por_tipo(self, transacao_id: UUID) -> Dict[TipoParte, int]:
        stmt = (
            select(ParteORM.tipo, func.count(ParteORM.id))
            .where(ParteORM.transacao_id == transacao_id)
            .group_by(ParteORM.tipo)
        )
        try:
            linhas = self.db.execute(stmt).all()
            resultado: Dict[TipoParte, int] = {}
            for tipo_val, qtd in linhas:
                tipo_enum = tipo_val if isinstance(tipo_val, TipoParte) else TipoParte(tipo_val)
                resultado[tipo_enum] = int(qtd)
            return resultado
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ErroOperacaoBD() from e
