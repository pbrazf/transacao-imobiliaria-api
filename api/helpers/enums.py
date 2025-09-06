from enum import Enum

# Enum de Status da Transação
class StatusTransacao(str, Enum):
    CRIADA = 'CRIADA'
    EM_ANALISE = 'EM_ANALISE'
    APROVADA = 'APROVADA'
    REPROVADA = 'REPROVADA'
    FINALIZADA = 'FINALIZADA'
    CANCELADA = 'CANCELADA'

# Tabela de transições permitidas
TRANSICOES_PERMITIDAS = {
    StatusTransacao.CRIADA: {StatusTransacao.EM_ANALISE, StatusTransacao.CANCELADA},
    StatusTransacao.EM_ANALISE: {StatusTransacao.APROVADA, StatusTransacao.REPROVADA, StatusTransacao.CANCELADA},
    StatusTransacao.APROVADA: {StatusTransacao.FINALIZADA, StatusTransacao.CANCELADA},
    StatusTransacao.REPROVADA: {StatusTransacao.CANCELADA},
    StatusTransacao.FINALIZADA: set(),
    StatusTransacao.CANCELADA: set(),
}

# Função para verificar se a transição é permitida
def pode_transicionar(de: StatusTransacao, para: StatusTransacao) -> bool:
    return para in TRANSICOES_PERMITIDAS.get(de, set())

# ---------------------------------------------------------------------------
# Enum de Tipo Parte
class TipoParte(Enum):
	COMPRADOR = 'COMPRADOR'
	VENDEDOR = 'VENDEDOR'
	CORRETOR = 'CORRETOR'
