from fastapi import HTTPException, status

def erro_http(codigo: str, http_status: int, mensagem: str | None = None) -> HTTPException:
    return HTTPException(status_code=http_status, detail={'codigo': codigo, 'mensagem': mensagem or codigo})

def nao_encontrada(recurso: str = 'recurso') -> HTTPException:
    return erro_http(f'{recurso}_nao_encontrada', status.HTTP_404_NOT_FOUND, f'{recurso} não encontrada')

def erro_interno(acao: str = 'operacao') -> HTTPException:
    return erro_http('erro_interno', status.HTTP_500_INTERNAL_SERVER_ERROR, f'erro ao {acao}')

def transicao_invalida() -> HTTPException:
    return erro_http('transicao_invalida', status.HTTP_422_UNPROCESSABLE_ENTITY, 'transição inválida')

def requisito_partes_nao_atendido() -> HTTPException:
    return erro_http('requisito_partes_nao_atendido', status.HTTP_422_UNPROCESSABLE_ENTITY, 'requisito de partes não atendido')

def requisicao_invalida(msg: str = 'requisição inválida') -> HTTPException:
    return erro_http('requisicao_invalida', status.HTTP_400_BAD_REQUEST, msg)

def conflito(msg: str = 'conflito') -> HTTPException:
    return erro_http('conflito', status.HTTP_409_CONFLICT, msg)

def nao_autorizado(msg: str = 'não autorizado') -> HTTPException:
	return erro_http('nao_autorizado', status.HTTP_401_UNAUTHORIZED, msg)
