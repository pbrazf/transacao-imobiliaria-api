from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID

from api.helpers.enums import StatusTransacao


class TransacaoCriarEntrada(BaseModel):
    '''Dados de entrada para criar uma Transação'''

    imovel_codigo: str = Field(
        max_length=64,
        description='Código do imóvel'
    )
    valor_venda: Decimal = Field(
        gt=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description='Valor total de venda do imóvel (maior que zero, com 2 casas decimais)'
    )
    status = Field(
        default=StatusTransacao.CRIADA,
        description='Status da transação'
    )

class TransacaoAtualizarEntrada(BaseModel):
    '''Dados de entrada para atualizar uma Transação'''

    imovel_codigo: str = Field(
        max_length=64, description='Código do imóvel'
    )
    valor_venda: Decimal = Field(
        gt=Decimal('0'), max_digits=18, decimal_places=2,
        description='Valor total de venda (> 0, 2 casas decimais)'
    )


class TransacaoAtualizarStatusEntrada(BaseModel):
    '''Dados de entrada para atualizar o status de uma Transação'''
    
    status: StatusTransacao = Field(
        description='Novo status'
    )

class TransacaoSaida(BaseModel):
    '''Retorno de uma Transação'''

    id: UUID = Field(
        description='Identificador único (UUID) da transação'
    )
    valor_venda: Decimal = Field(
        gt=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description='Valor total de venda do imóvel'
    )
    status: StatusTransacao = Field(
        description='Status atual da transação'
    )
    data_criacao: datetime = Field(
        description='Data/hora de criação em UTC'
    )
    data_atualizacao: datetime = Field(
        description='Data/hora da última atualização em UTC'
    )

    model_config = {'from_attributes': True}
