from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field
from .status import StatusTransacao

Tipo = Literal['comprador', 'vendedor', 'corretor']


class ParteEntrada(BaseModel):
    '''Dados de entrada para adicionar uma Parte na Transação'''

    nome: str = Field(
        min_length=1,
        strip_whitespace=True,
        description='Nome completo da parte (comprador, vendedor ou corretor)'
    )
    documento: str = Field(
        min_length=3,
        strip_whitespace=True,
        description='CPF ou CNPJ da parte'
    )
    tipo: Tipo = Field(
        description='Tipo da parte: comprador, vendedor ou corretor'
    )


class ParteSaida(ParteEntrada):
    '''Retorno de uma Parte cadastrada'''

    id: str = Field(description='Identificador único (UUID) da parte')

    model_config = {'from_attributes': True}


class TransacaoCriarEntrada(BaseModel):
    '''Dados de entrada para criar uma Transação'''

    valor_venda: Decimal = Field(
        gt=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description='Valor total de venda do imóvel (maior que zero, com 2 casas decimais)'
    )


class TransacaoSaida(BaseModel):
    '''Retorno de uma Transação'''

    id: str = Field(description='Identificador único (UUID) da transação')
    valor_venda: Decimal = Field(
        gt=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description='Valor total de venda do imóvel'
    )
    status: StatusTransacao = Field(description='Status atual da transação')
    criado_em: datetime = Field(description='Data/hora de criação em UTC')
    atualizado_em: datetime = Field(description='Data/hora da última atualização em UTC')

    model_config = {'from_attributes': True}


class ComissaoCriarEntrada(BaseModel):
    '''Dados de entrada para criar uma Comissão'''

    percentual: Decimal = Field(
        ge=Decimal('0'),
        le=Decimal('1'),
        max_digits=5,
        decimal_places=4,
        description='Percentual da comissão em formato decimal (ex.: 0.05 = 5%)'
    )


class ComissaoSaida(BaseModel):
    '''Retorno de uma Comissão'''

    id: str = Field(description='Identificador único (UUID) da comissão')
    percentual: Decimal = Field(
        ge=Decimal('0'),
        le=Decimal('1'),
        max_digits=5,
        decimal_places=4,
        description='Percentual aplicado à comissão (0–1, ex.: 0.10 = 10%)'
    )
    valor_calculado: Decimal = Field(
        ge=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description='Valor da comissão calculado a partir do valor de venda'
    )
    paga: bool = Field(description='Indica se a comissão já foi paga (true/false)')

    model_config = {'from_attributes': True}
