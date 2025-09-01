from enum import Enum

class StatusTransacao(str, Enum):
    CRIADA = 'criada'
    EM_ANALISE = 'em_analise'
    APROVADA = 'aprovada'
    REPROVADA = 'reprovada'
    CONCLUIDA = 'concluida'
    CANCELADA = 'cancelada'

# Tabela de transições permitidas
TRANSICOES_PERMITIDAS = {
    StatusTransacao.CRIADA: {StatusTransacao.EM_ANALISE, StatusTransacao.CANCELADA},
    StatusTransacao.EM_ANALISE: {StatusTransacao.APROVADA, StatusTransacao.REPROVADA, StatusTransacao.CANCELADA},
    StatusTransacao.APROVADA: {StatusTransacao.CONCLUIDA, StatusTransacao.CANCELADA},
    StatusTransacao.REPROVADA: {StatusTransacao.CANCELADA},
    StatusTransacao.CONCLUIDA: set(),
    StatusTransacao.CANCELADA: set(),
}

# Função para verificar se a transição é permitida
def pode_transicionar(de: StatusTransacao, para: StatusTransacao) -> bool:
    return para in TRANSICOES_PERMITIDAS.get(de, set())
