from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import List, Optional
from .status import StatusTransacao, pode_transicionar
from .errors import *
from uuid import uuid4

def dinheiro(val: Decimal) -> Decimal:
    # padroniza 2 casas, arredondamento de mercado
    return val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@dataclass
class Parte:
    nome: str
    documento: str
    papel: str   # 'comprador' | 'vendedor' | 'corretor'
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class Comissao:
    percentual: Decimal  # 0–1
    valor_calculado: Decimal
    paga: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))

    @staticmethod
    def criar(percentual: Decimal, valor_venda: Decimal) -> 'Comissao':
        if not (Decimal('0') <= percentual <= Decimal('1')):
            raise ValidacaoError('percentual deve estar entre 0 e 1')
        valor = dinheiro(valor_venda * percentual)
        return Comissao(percentual=percentual, valor_calculado=valor)

    def pagar(self) -> None:
        if self.paga:
            # idempotente: não falha, apenas ignora
            return
        self.paga = True

@dataclass
class Transacao:
    valor_venda: Decimal
    status: StatusTransacao = StatusTransacao.CRIADA
    partes: List[Parte] = field(default_factory=list)
    comissoes: List[Comissao] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    # ---- Regras de status (Item 1)
    def transicionar(self, novo_status: StatusTransacao) -> None:
        if not pode_transicionar(self.status, novo_status):
            raise TransicaoInvalida(f'Transição {self.status.value} -> {novo_status.value} não permitida')
        # trava campos após aprovada
        if self.status == StatusTransacao.APROVADA and novo_status not in (StatusTransacao.CONCLUIDA, StatusTransacao.CANCELADA):
            raise OperacaoBloqueada('Transação aprovada: alterações não permitidas')
        self.status = novo_status

    # ---- Participantes mínimos para aprovar (Item 2)
    def aprovar(self) -> None:
        comp = len([p for p in self.partes if p.papel == 'comprador'])
        vend = len([p for p in self.partes if p.papel == 'vendedor'])
        corr = len([p for p in self.partes if p.papel == 'corretor'])
        if comp != 1 or vend != 1 or corr != 1:
            raise ParticipantesInvalidos('Aprovação requer exatamente 1 comprador, 1 vendedor e 1 corretor')
        self.transicionar(StatusTransacao.APROVADA)

    # ---- Gerir Partes (validators simples)
    def adicionar_parte(self, parte: Parte) -> None:
        if self.status in (StatusTransacao.APROVADA, StatusTransacao.CONCLUIDA, StatusTransacao.CANCELADA):
            raise OperacaoBloqueada('Não é permitido editar partes após aprovação')
        self.partes.append(parte)

    def remover_parte(self, parte_id: str) -> None:
        if self.status in (StatusTransacao.APROVADA, StatusTransacao.CONCLUIDA, StatusTransacao.CANCELADA):
            raise OperacaoBloqueada('Não é permitido editar partes após aprovação')
        self.partes = [p for p in self.partes if p.id != parte_id]

    # ---- Comissão (Item 3)
    def criar_comissao(self, percentual: Decimal) -> Comissao:
        com = Comissao.criar(percentual=percentual, valor_venda=self.valor_venda)
        self.comissoes.append(com)
        return com

    def pagar_comissao(self, comissao_id: str) -> None:
        com = next((c for c in self.comissoes if c.id == comissao_id), None)
        if not com:
            raise ValidacaoError('Comissão não encontrada')
        com.pagar()

    # ---- Guardas úteis (Item 1/2/3)
    def atualizar_valor_venda(self, novo_valor: Decimal) -> None:
        if self.status in (StatusTransacao.APROVADA, StatusTransacao.CONCLUIDA, StatusTransacao.CANCELADA):
            raise OperacaoBloqueada('Valor de venda não pode ser alterado após aprovação')
        if novo_valor <= 0:
            raise ValidacaoError('valor_venda deve ser > 0')
        self.valor_venda = dinheiro(novo_valor)
