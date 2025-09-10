# API Imobiliária

## 🎯 Visão Geral
API REST desenvolvida em **Python + FastAPI** para gerenciar o ciclo completo de uma **transação imobiliária**, incluindo cadastro de transações, partes envolvidas e cálculo/pagamento de comissões.  

O projeto segue boas práticas de arquitetura, versionamento de banco de dados e organização em camadas, rodando de forma simples via Docker.

---

## 🚀 Tecnologias
- **Python 3.12**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy + Alembic**
- **Docker + Docker Compose**
- **Pydantic** (validação)

---

## 📦 Funcionalidades

### Entidades
- **Transação**  
  - Campos: `id`, `imovel_codigo`, `valor_venda`, `status`, `data_criacao`, `data_atualizacao`  
  - Controle de status com transições válidas:
    - `CRIADA -> EM_ANALISE -> APROVADA -> FINALIZADA`
    - `* -> CANCELADA`  

- **Parte**  
  - Vínculo com uma transação (`transacao_id`)  
  - Tipos: `COMPRADOR`, `VENDEDOR`, `CORRETOR`  

- **Comissão**  
  - Calculada automaticamente: `valor_venda * percentual`  
  - Campo `paga` para indicar quitação  

### Regras de Negócio
- Uma transação só pode ser **aprovada** se possuir ao menos:
  - 1 comprador
  - 1 vendedor
  - 1 corretor  

### Endpoints
- **Transações**  
  - `POST /api/v1/transacoes`  
  - `GET /api/v1/transacoes` (filtros + paginação)  
  - `GET /api/v1/transacoes/{id}`  
  - `PATCH /api/v1/transacoes/{id}/status`  
  - `DELETE /api/v1/transacoes/{id}`  

- **Partes**  
  - `POST /api/v1/transacoes/{id}/partes`  
  - `DELETE /api/v1/partes/{id}`  

- **Comissões**  
  - `POST /api/v1/transacoes/{id}/comissoes`  
  - `POST /api/v1/comissoes/{id}/pagar`  

---

## ⚙️ Como Rodar

### Pré-requisitos
- [Docker](https://www.docker.com/)  
- [Docker Compose](https://docs.docker.com/compose/)  

### Passos
1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/api-imobiliaria.git
   cd api-imobiliaria
   ```

2. Crie o arquivo `.env` na raiz do projeto com o conteúdo:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/imobiliaria
   AUTH_BEARER_TOKEN=seu_token_aqui
   API_PREFIX=/api/v1
   ```

3. Suba os containers:
   ```bash
   docker compose up -d --build
   ```

4. Rode as migrations:
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. Acesse a documentação da API em:  
   👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ✅ Próximos Passos
- Melhorar logs (estruturados em JSON).  
- Autenticação JWT.  
- Métricas e observabilidade (Prometheus + OpenTelemetry).  
- Testes mais abrangentes e CI/CD.  

---
