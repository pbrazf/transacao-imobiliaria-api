from decimal import Decimal
from typing import Optional, List, Dict, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from uuid import UUID

from infra.models.transacao import Transacao as TransacaoORM
from infra.models.parte import Parte as ParteORM  # Para validação de STATUS

from api.helpers.enums import StatusTransacao, TipoParte

class TransacaoRepositorio:
    def __init__(self, db: Session):
        self.db = db
        
    def adicionar(self, obj: TransacaoORM) -> TransacaoORM:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        except Exception:
            self.db.rollback()
            raise
        return obj

    def buscar(self, transacao_id: str) -> TransacaoORM | None:
        return self.db.get(TransacaoORM, transacao_id)

    def listar(self, *, status_filtro, imovel_codigo, data_ini, data_fim, limit, offset):
        stmt = select(TransacaoORM)
        if status_filtro is not None:
            stmt = stmt.where(TransacaoORM.status == status_filtro)
        if imovel_codigo:
            stmt = stmt.where(TransacaoORM.imovel_codigo == imovel_codigo)
        if data_ini:
            stmt = stmt.where(TransacaoORM.data_criacao >= data_ini)
        if data_fim:
            stmt = stmt.where(TransacaoORM.data_criacao < data_fim)

        try:
            total = self.db.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar_one()

            stmt = stmt.order_by(TransacaoORM.data_criacao.desc()).offset(offset).limit(limit)
            itens = self.db.execute(stmt).scalars().all()
            return itens, total
        except Exception:
            self.db.rollback()
            raise

    def atualizar_tudo(
        self, obj: TransacaoORM, *, imovel_codigo: Optional[str] = None, valor_venda: Optional[Decimal] = None
    ) -> TransacaoORM:
        if imovel_codigo is not None:
            obj.imovel_codigo = imovel_codigo
        if valor_venda is not None:
            obj.valor_venda = valor_venda
        try:
            self.db.commit()
            self.db.refresh(obj)
        except Exception:
            self.db.rollback()
            raise
        return obj
    
    def deletar(self, obj: TransacaoORM) -> None:
        try:
            self.db.delete(obj)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        
    def atualizar_status(self, obj: TransacaoORM, novo_status: StatusTransacao) -> TransacaoORM:
        obj.status = novo_status
        try:
            self.db.commit()
            self.db.refresh(obj)
        except Exception:
            self.db.rollback()
            raise
        return obj

    def listar_partes(self, transacao_id: UUID) -> List[ParteORM]:
        stmt = select(ParteORM).where(ParteORM.transacao_id == transacao_id)
        return self.db.execute(stmt).scalars().all()

    def contar_partes_por_tipo(self, transacao_id: UUID) -> Dict[TipoParte, int]:
        """
        Retorna um dicionário {TipoParte: quantidade} para as Partes da transação.
        Garante que a chave seja o Enum TipoParte (mesmo que a coluna esteja como string no banco).
        """
        stmt = (
            select(ParteORM.tipo, func.count(ParteORM.id))
            .where(ParteORM.transacao_id == transacao_id)
            .group_by(ParteORM.tipo)
        )
        try:
            linhas = self.db.execute(stmt).all()
        except Exception:
            self.db.rollback()
            raise

        return {tipo: qtd for tipo, qtd in linhas}
