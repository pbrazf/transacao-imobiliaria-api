from decimal import Decimal, ROUND_HALF_UP

def dinheiro(valor: Decimal) -> Decimal:
    # 2 casas, arredondamento de mercado
    return valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calcular_comissao(valor_venda: Decimal, percentual: Decimal) -> Decimal:
    # assume 0 < percentual <= 1 (validado no schema)
    return dinheiro(valor_venda * percentual)
