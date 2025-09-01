class RegraNegocioError(Exception):
    pass

class TransicaoInvalida(RegraNegocioError):
    pass

class ParticipantesInvalidos(RegraNegocioError):
    pass

class OperacaoBloqueada(RegraNegocioError):
    pass

class ValidacaoError(RegraNegocioError):
    pass
