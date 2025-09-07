# infra/excecoes.py

class ErroBanco(Exception):
    '''Erro genérico de acesso ao banco de dados.'''
    pass


class ErroConflitoBD(ErroBanco):
    '''Violação de restrição de unicidade, FK ou regra de integridade.'''
    pass


class ErroNaoEncontrado(ErroBanco):
    '''Registro não encontrado no banco de dados.'''
    pass


class ErroOperacaoBD(ErroBanco):
    '''Erro inesperado em operação de banco (INSERT/UPDATE/DELETE).'''
    pass
