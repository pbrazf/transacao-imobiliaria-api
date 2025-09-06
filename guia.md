# Teste Técnico — Backend Python (Pleno)

## 🎯 Objetivo

Construir uma API REST que gerencie o ciclo básico de uma **transação imobiliária** (da criação ao pagamento de comissão), com **CRUD** completo, algumas **regras de negócio** e **proposta de deploy na AWS**.

---

## 📦 Escopo Funcional

### Entidades

- **Transacao**

  - `id` (UUID)
  - `imovel_codigo` (string)
  - `valor_venda` (decimal)
  - `status` (enum: `CRIADA`, `EM_ANALISE`, `APROVADA`, `FINALIZADA`, `CANCELADA`)
  - `data_criacao` (datetime)
  - `data_atualizacao` (datetime)

- **Parte**

  - `id` (UUID)
  - `transacao_id` (FK)
  - `tipo` (enum: `COMPRADOR`, `VENDEDOR`, `CORRETOR`)
  - `nome` (string)
  - `cpf_cnpj` (string)
  - `email` (string opcional)

- **Comissao**
  - `id` (UUID)
  - `transacao_id` (FK)
  - `percentual` (decimal, ex.: 0.05 = 5%)
  - `valor_calculado` (decimal) — calculado a partir de `valor_venda * percentual`
  - `paga` (bool)

> **Regras de negócio**
>
> - Uma **Transação** deve ter pelo menos 1 `COMPRADOR`, 1 `VENDEDOR` e 1 `CORRETOR` para ser **APROVADA**.
> - `valor_calculado` é **derivado** e não deve ser enviado no POST.

---

### Endpoints mínimos (REST)

#### Transações

- `POST /api/v1/transacoes` — cria transação
- `GET /api/v1/transacoes` — lista com **filtros** (`status`, `imovel_codigo`, intervalo de `data_criacao`) e **paginação**
- `GET /api/v1/transacoes/{id}`
- `PUT /api/v1/transacoes/{id}` — atualização total
- `PATCH /api/v1/transacoes/{id}/status`  
  Transições válidas:
  - `CRIADA -> EM_ANALISE -> APROVADA -> FINALIZADA`
  - `* -> CANCELADA` (motivo opcional)  
    ➝ Transições inválidas devem retornar **422**
- `DELETE /api/v1/transacoes/{id}`

#### Partes

- `POST /api/v1/transacoes/{id}/partes` (adiciona parte)
- `DELETE /api/v1/partes/{id}`

#### Comissões

- `POST /api/v1/transacoes/{id}/comissoes` (cria registro de comissão com `percentual`; calcule `valor_calculado`)
- `POST /api/v1/comissoes/{id}/pagar` (marca `paga=true`)

#### Autenticação

- Pode ser **Bearer token** simples (chave fixa via env) ou JWT.

---

## 🛠️ Requisitos Técnicos

- **Stack sugerida**:

  - Python 3.10+ | **FastAPI** ou **Flask**
  - **PostgreSQL**
  - **Docker** + `docker-compose`

- **Boas práticas**:
  - Tratamento de erros e **validação** (pydantic se FastAPI)
  - Logs estruturados
  - **Paginação** consistente (`limit`, `offset`, `X-Total-Count`)

---

## 📂 O que Entregar

1. **Repositório** (GitHub/Bitbucket):
   - `README.md` com:
     - Como rodar (local e Docker)
     - Variáveis de ambiente
   - Breve explicação de **arquitetura** e decisões técnicas

2. **Proposta de Deploy na AWS**
   - Aqui é só como você colocaria na AWS e não precisa fazer o deploy de fato. Somente a ideia e as ferramentas utilizadas.
