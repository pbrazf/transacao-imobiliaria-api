import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.database import Base

# Enum de Tipo Parte
class TipoEnum(PyEnum):
	COMPRADOR = 'COMPRADOR'
	VENDEDOR = 'VENDEDOR'
	CORRETOR = 'CORRETOR'

# Modelo da Parte
class Parte(Base):
	__tablename__ = 'parte'

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4
	)

	transacao_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey('transacao.id', ondelete='CASCADE'),
		nullable=False
	)

	tipo: Mapped[TipoEnum] = mapped_column(
		Enum(TipoEnum, name='tipo_parte'),
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

	# Faz a relação com a transação
	transacao = relationship('Transacao', backref='partes', passive_deletes=True)
