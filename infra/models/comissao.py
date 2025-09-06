from uuid import UUID as PyUUID, uuid4
from decimal import Decimal

from sqlalchemy import Boolean, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.database import Base


class Comissao(Base):
    __tablename__ = 'comissao'

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    transacao_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('transacao.id', ondelete='CASCADE'),
        nullable=False
    )

    # percentual como fração: ex. 0.05 = 5%
    percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False
    )

    valor_calculado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),   # mesma precisão de valor_venda
        nullable=False
    )

    paga: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=text('false')
    )

    transacao = relationship('Transacao', backref='comissoes', passive_deletes=True)
