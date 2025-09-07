from uuid import UUID as PyUUID, uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import String, Numeric, DateTime, Enum, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infra.database import Base
from helpers.enums import StatusTransacao

# Modelo da Transação
class Transacao(Base):
    __tablename__ = 'transacao'

    id: Mapped[PyUUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid4
    )

    imovel_codigo: Mapped[str] = mapped_column(
		String(64),
		nullable=False
    )

    valor_venda: Mapped[Decimal] = mapped_column(
		Numeric(12, 2),
		nullable=False
    )

    status: Mapped[StatusTransacao] = mapped_column(
		Enum(StatusTransacao, name='status_transacao'),
		nullable=False,
		default=StatusTransacao.CRIADA,
    )

    data_criacao: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(), 
        nullable=False
    )
    
    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

	# Índices
    __table_args__ = (
        Index('ix_imovel_codigo', 'imovel_codigo'),
        Index('ix_transacao_status', 'status'),
        Index('ix_transacao_data_criacao', 'data_criacao')
    )
