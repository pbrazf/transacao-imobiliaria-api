from uuid import UUID as PyUUID, uuid4

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.database import Base
from helpers.enums import TipoParte

# Modelo da Parte
class Parte(Base):
	__tablename__ = 'parte'

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

	tipo: Mapped[TipoParte] = mapped_column(
		Enum(TipoParte, name='tipo_parte'),
		nullable=False
	)

	nome: Mapped[str] = mapped_column(
		String(100),
		nullable=False
	)

	# 11 (CPF) ou 14 (CNPJ)
	cpf_cnpj: Mapped[str] = mapped_column(
		String(14),
		nullable=False
	)

	email: Mapped[str | None] = mapped_column(
		String(100),
		nullable=True
	)

	transacao = relationship('Transacao', backref='partes', passive_deletes=True)
