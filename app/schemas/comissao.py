from __future__ import annotations 

from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class ComissaoCriarEntrada(BaseModel):
    '''Dados de entrada para criar uma Comissão'''

    percentual: Decimal = Field(
        ge=Decimal('0'),
        le=Decimal('1'),
        max_digits=5,
        decimal_places=3,
        description='Percentual da comissão em formato decimal (ex.: 0.05 = 5%)'
    )


class ComissaoSaida(BaseModel):
    '''Retorno de uma Comissão'''

    id: UUID = Field(description='Identificador único (UUID) da comissão')
    transacao_id: UUID = Field(description='Identificador único (UUID) da transação associada')
    percentual: Decimal = Field(description='Percentual aplicado à comissão (0–1, ex.: 0.10 = 10%)')
    valor_calculado: Decimal = Field(
        ge=Decimal('0'),
        max_digits=5,
        decimal_places=3,
        description='Valor da comissão calculado a partir do valor de venda'
    )
    paga: bool = Field(description='Indica se a comissão já foi paga')

    model_config = {'from_attributes': True}
