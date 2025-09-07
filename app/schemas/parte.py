from __future__ import annotations # permite referências a tipos dentro da própria classe

from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from helpers.enums import TipoParte


class ParteCriarEntrada(BaseModel):
    '''Dados para criação de uma nova parte'''

    nome: str = Field(
        min_length=1,
        max_length=100,
        description='Nome da pessoa'
    )
    cpf_cnpj: str = Field(
        pattern=r'^(?:\d{11}|\d{14})$',
        description='CPF (11 dígitos) ou CNPJ (14 dígitos) da pessoa (apenas números)'
    )
    tipo: TipoParte = Field(
        description='Tipo da parte (COMPRADOR, VENDEDOR, CORRETOR)'
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=100,
        description='E-mail da parte (opcional)'
    )


class ParteSaida(BaseModel):
    '''Dados de saída de uma parte'''

    id: UUID = Field(description='Identificador da parte')
    transacao_id: UUID = Field(description='Transação à qual a parte pertence')
    nome: str
    tipo: TipoParte
    cpf_cnpj: str
    email: EmailStr | None = None

    model_config = {'from_attributes': True}
