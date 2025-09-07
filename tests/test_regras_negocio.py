from decimal import Decimal
from datetime import datetime, timedelta
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- imports da sua app ---
from main import app  # sua FastAPI principal
from infra.database import Base, get_db  # ajuste se seu get_db tiver outro nome
from helpers.enums import StatusTransacao, TipoParte  # ajuste caminho se necessário

# ---------- FIXTURES DE BANCO E CLIENTE ----------
@pytest.fixture(scope='function')
def engine_memoria():
    engine = create_engine('sqlite+pysqlite:///:memory:', echo=False, future=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope='function')
def db_sessao(engine_memoria):
    TestingSessionLocal = sessionmaker(bind=engine_memoria, autoflush=False, autocommit=False, future=True)
    sess = TestingSessionLocal()
    try:
        yield sess
    finally:
        sess.close()

@pytest.fixture(scope='function')
def client(db_sessao, monkeypatch):
    def override_get_db():
        try:
            yield db_sessao
            db_sessao.commit()
        except Exception:
            db_sessao.rollback()
            raise

    monkeypatch.setattr('infra.database.get_db', override_get_db)
    return TestClient(app)

# =========================================================
#                REGRAS DE NEGÓCIO: TRANSAÇÃO
# =========================================================

def criar_transacao(client, imovel_codigo='IMO-001', valor='100000.00', status=StatusTransacao.CRIADA.value):
    payload = {
        'imovel_codigo': imovel_codigo,
        'valor_venda': valor,
        'status': status
    }
    r = client.post('/api/v1/transacoes', json=payload)
    assert r.status_code == 201, r.text
    return r.json()

def test_criar_transacao_valida(client):
    dado = criar_transacao(client)
    assert dado['imovel_codigo'] == 'IMO-001'
    assert Decimal(dado['valor_venda']) == Decimal('100000.00')
    assert dado['status'] == StatusTransacao.CRIADA.value

def test_nao_permite_valor_venda_zero_ou_negativo(client):
    r = client.post('/api/v1/transacoes', json={'imovel_codigo': 'A', 'valor_venda': '0.00'})
    assert r.status_code in (400, 422)

    r = client.post('/api/v1/transacoes', json={'imovel_codigo': 'A', 'valor_venda': '-10.00'})
    assert r.status_code in (400, 422)

def test_atualizar_transacao_status_transicao_valida(client):
    dado = criar_transacao(client)
    tid = dado['id']
    # supondo que a transição válida CRIADA -> APROVADA exista no seu enum/regra
    r = client.patch(f'/api/v1/transacoes/{tid}/status', json={'status': StatusTransacao.APROVADA.value})
    assert r.status_code == 200, r.text
    assert r.json()['status'] == StatusTransacao.APROVADA.value

def test_bloqueia_transicao_invalida(client):
    dado = criar_transacao(client)
    tid = dado['id']
    # exemplo: transição proibida CRIADA -> CONCLUIDA (ajuste conforme sua regra pode_transicionar)
    r = client.patch(f'/api/v1/transacoes/{tid}/status', json={'status': StatusTransacao.CONCLUIDA.value})
    assert r.status_code in (400, 409)

def test_listagem_com_filtros_e_paginacao(client):
    base = datetime.utcnow()
    # cria 3 transações em datas diferentes
    t1 = criar_transacao(client, imovel_codigo='X1', valor='100.00')
    t2 = criar_transacao(client, imovel_codigo='X2', valor='200.00')
    t3 = criar_transacao(client, imovel_codigo='X2', valor='300.00')

    # lista filtrando por imovel_codigo e paginando
    r = client.get('/api/v1/transacoes', params={'imovel_codigo': 'X2', 'limit': 1, 'offset': 0})
    assert r.status_code == 200
    corpo = r.json()
    assert 'total' in corpo and corpo['total'] >= 2
    assert len(corpo['itens']) == 1  # paginação aplicada
    # ordenação desc por data_criacao esperada
    primeiro = corpo['itens'][0]
    assert primeiro['imovel_codigo'] == 'X2'

# =========================================================
#                REGRAS DE NEGÓCIO: PARTES
# =========================================================

def adicionar_parte(client, transacao_id: str, nome='Fulano', doc='11122233344', tipo=TipoParte.COMPRADOR.value):
    payload = {'nome': nome, 'cpf_cnpj': doc, 'tipo': tipo}
    r = client.post(f'/api/v1/transacoes/{transacao_id}/partes', json=payload)
    return r

def test_adicionar_parte_compra(client):
    t = criar_transacao(client)
    r = adicionar_parte(client, t['id'], nome='Comprador A', tipo=TipoParte.COMPRADOR.value)
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo['nome'] == 'Comprador A'
    assert corpo['tipo'] == TipoParte.COMPRADOR.value

def test_nao_permite_tipo_invalido_em_parte(client):
    t = criar_transacao(client)
    r = client.post(f'/api/v1/transacoes/{t["id"]}/partes', json={'nome': 'X', 'cpf_cnpj': '1', 'tipo': 'qualquer'})
    assert r.status_code in (400, 422)

def test_deletar_parte(client):
    t = criar_transacao(client)
    r = adicionar_parte(client, t['id'], nome='Corretor A', tipo=TipoParte.CORRETOR.value)
    assert r.status_code == 201
    pid = r.json()['id']

    d = client.delete(f'/api/v1/partes/{pid}')
    assert d.status_code in (204, 200)

    # garantir que não existe mais
    g = client.get(f'/api/v1/partes/{pid}')
    assert g.status_code in (404, 400, 422)

# =========================================================
#                REGRAS DE NEGÓCIO: COMISSÕES
# =========================================================

def criar_comissao(client, transacao_id: str, percentual='0.06'):
    payload = {'percentual': percentual}
    r = client.post(f'/api/v1/transacoes/{transacao_id}/comissoes', json=payload)
    return r

def test_calcular_comissao_valor(client):
    t = criar_transacao(client, valor='500000.00')
    r = criar_comissao(client, t['id'], percentual='0.05')  # 5%
    assert r.status_code == 201, r.text
    corpo = r.json()
    # 5% de 500000.00 = 25000.00
    assert Decimal(corpo['valor_calculado']) == Decimal('25000.00')
    assert corpo['paga'] is False

def test_percentual_invalido_em_comissao(client):
    t = criar_transacao(client)
    r = criar_comissao(client, t['id'], percentual='-0.1')
    assert r.status_code in (400, 422)

    r = criar_comissao(client, t['id'], percentual='1.5')
    assert r.status_code in (400, 422)

def test_pagar_comissao(client):
    t = criar_transacao(client, valor='1000.00')
    c = criar_comissao(client, t['id'], '0.10').json()  # 10%
    cid = c['id']

    p = client.post(f'/api/v1/comissoes/{cid}/pagar')
    assert p.status_code == 200, p.text
    assert p.json()['paga'] is True

def test_nao_paga_comissao_ja_paga(client):
    t = criar_transacao(client, valor='1000.00')
    c = criar_comissao(client, t['id'], '0.10').json()
    cid = c['id']

    p1 = client.post(f'/api/v1/comissoes/{cid}/pagar')
    assert p1.status_code == 200
    p2 = client.post(f'/api/v1/comissoes/{cid}/pagar')
    assert p2.status_code in (400, 409)  # esperado: idempotência/erro de negócio

# =========================================================
#        LISTAGEM / FILTROS DE DATA (BORDA DE REGRA)
# =========================================================

def test_filtro_intervalo_datas_exclusivo_no_fim(client, monkeypatch):
    # cria duas transações em sequência para testar janela [ini, fim)
    t1 = criar_transacao(client, imovel_codigo='D1', valor='10.00')
    t2 = criar_transacao(client, imovel_codigo='D2', valor='20.00')

    # supondo que sua API aceite filtros 'data_ini' e 'data_fim' em ISO8601
    r_all = client.get('/api/v1/transacoes', params={'limit': 50, 'offset': 0})
    assert r_all.status_code == 200
    itens = r_all.json()['itens']
    assert len(itens) >= 2

    # pega a data do segundo para construir o corte exclusivo < data_fim
    data_fim = itens[0]['data_criacao']  # ordenado desc
    r_filtro = client.get('/api/v1/transacoes', params={'data_fim': data_fim, 'limit': 50, 'offset': 0})
    assert r_filtro.status_code == 200
    # espera trazer registros ESTRITAMENTE menores que data_fim
    for it in r_filtro.json()['itens']:
        assert it['data_criacao'] < data_fim
