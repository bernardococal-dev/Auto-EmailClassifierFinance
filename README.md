# Auto-EmailClassifierFinance

📌 **Objetivo (MVP)**

Criar uma plataforma web para classificação e visualização de e-mails financeiros. O MVP engloba:

- Coletor de e-mails (IMAP/API) — salvar metadados e anexos
- Classificação automática (Nota Fiscal / Requisição de Compra / Outros)
- Extração de dados por regex (fornecedor, CNPJ, número, valor)
- Visualização do documento com preview de anexos
- Marcar item como **FEITO** e registrar histórico

---

## Arquitetura

- Backend: **Python + FastAPI**
- Banco de dados: **PostgreSQL**
- Frontend: **React (Vite)**
- Armazenamento de anexos: local (./storage) — preparado para S3
- OCR / PDF: **pdfplumber**, **Pillow** (usar OCR só quando necessário)

---

## Variáveis de ambiente (documentação) ⚙️

Copie `.env.example` → `.env` e preencha os valores. Nunca comite o `.env`.

- `DATABASE_URL` — string de conexão SQLAlchemy (ex: `postgresql+psycopg2://postgres:postgres@db:5432/postgres`)
- `STORAGE_DIR` — pasta onde anexos e previews serão armazenados (ex: `/data/storage`)

IMAP (coletor de e-mails):
- `IMAP_HOST` — host do servidor IMAP (ex: `imap.exemplo.com`)
- `IMAP_USER` — usuário/conta do e-mail
- `IMAP_PASS` — senha / app password
- `IMAP_FOLDER` — pasta a ser verificada (opcional, default `INBOX`)
- `IMAP_PORT` — porta IMAP (opcional, ex: `993`)
- `IMAP_USE_SSL` — `true/false` (opcional)

Outlook / Microsoft Graph (recomendado para caixas Exchange/Outlook online):
- `OUTLOOK_TENANT_ID` — Tenant ID do Azure AD
- `OUTLOOK_CLIENT_ID` — Client (Application) ID da app registrada no Azure
- `OUTLOOK_CLIENT_SECRET` — Client secret gerado para a app
- `OUTLOOK_USER` — e-mail do usuário/caixa que será lida (ex: `financeiro@empresa.com`)
- `OUTLOOK_FOLDER` — pasta a ser consultada (default `Inbox`)

> Para usar Outlook via Microsoft Graph você deve:
> 1. Registrar uma app no Azure AD (App registrations)
> 2. Conceder permissão **Application** `Mail.Read` (se acessar caixas de outros usuários) e executar **Admin consent**
> 3. Preencher `OUTLOOK_TENANT_ID`, `OUTLOOK_CLIENT_ID`, `OUTLOOK_CLIENT_SECRET` no `.env`
>
> Exemplo mínimo no `.env` para Outlook:
>
> OUTLOOK_TENANT_ID=<tenant_id>
> OUTLOOK_CLIENT_ID=<client_id>
> OUTLOOK_CLIENT_SECRET=<client_secret>
> OUTLOOK_USER=financeiro@empresa.com
> OUTLOOK_FOLDER=Inbox
> LOCAL_TZ=America/Sao_Paulo

> DICA: Se preferir não usar Microsoft Graph, o coletor também suporta IMAP como fallback.


---

## Como usar (local / Docker) ▶️

1. Copie e edite o `.env`:

```bash
cp .env.example .env
# edite o .env e preencha IMAP_*, DATABASE_URL, STORAGE_DIR
```

2. Suba serviços (Postgres + backend):

```bash
docker-compose up --build -d
```

3. Backend disponível em: `http://localhost:8000` (OpenAPI: `http://localhost:8000/docs`)

4. Frontend (dev):

```bash
cd frontend
npm install
npm run dev
# abre em http://localhost:5173
```

---

## Como configurar seu e-mail (onde colocar seu e-mail) 📧

- Coloque as credenciais do e-mail em `.env` nas variáveis `IMAP_USER`, `IMAP_PASS` e `IMAP_HOST`.
- Por segurança, use app password quando disponível (Office365).
- Para testar localmente, há um script de exemplo: `backend/app/scripts/fetch_emails_sample.py`.

Exemplo de execução do coletor (no container):

```bash
docker-compose exec backend python -m app.scripts.fetch_emails_sample
```

Ou localmente (após instalar dependências e ativar `.env`):

```bash
python -m app.scripts.fetch_emails_sample
```

> Nota: o coletor atual é um stub — implementa a conexão IMAP mínima e deve ser estendido para gravar e anexos e assegurar idempotência.

**Rodando o ingestor completo (Outlook)**

1. Configure a app no Azure AD e preencha as variáveis `OUTLOOK_TENANT_ID`, `OUTLOOK_CLIENT_ID`, `OUTLOOK_CLIENT_SECRET`, `OUTLOOK_USER` e `LOCAL_TZ` no `.env`.
2. Suba os serviços: `docker-compose up --build -d`.
3. Execute o ingestor de exemplo dentro do container: `docker-compose exec backend python -m app.scripts.fetch_emails_sample`.
4. Verifique `GET /documentos/` e abra o frontend (`http://localhost:5173`) para conferir classificação, extração, previews e link para o e-mail original.


---

## Endpoints principais (FastAPI)

- `GET /documentos` — lista documentos (filtros por tipo/status)
- `GET /documentos/{id}` — detalhes (+ histórico, anexos)
- `POST /documentos/{id}/confirmar?usuario=<usuario>` — marca como FEITO
- `GET /documentos/{id}/email-original` — retorna link para abrir o e-mail original

---

## Scripts úteis

- `backend/app/scripts/seed.py` — cria um exemplo no banco
- `backend/app/scripts/fetch_emails_sample.py` — exemplo de execução do coletor / ingestor (Outlook/IMAP)
- `backend/app/services/email_ingestor.py` — pipeline de ingestão para Outlook (idempotência, persistência, classificação, extração, preview, histórico)

---

## Recomendações para próximos passos

- Implementar coletor IMAP completo (idempotência, gravação de anexos, tratamento de XML NF-e)
- Adicionar migrações com Alembic e testes automatizados (pytest)
- Criar workers/filas (Redis + Celery/RQ) para processar anexos e gerar previews/OCR
- Implementar autenticação/ACL no backend e frontend

---

Se quiser, posso implementar o coletor completo (salvar anexos, gerar previews automaticamente) ou adicionar migrações com Alembic. Escolha uma tarefa e continuo.
📌 **Objetivo (MVP)**

Criar uma plataforma web para classificação e visualização de e-mails financeiros. O MVP engloba:

- Coletor de e-mails (IMAP/API) — salvar metadados e anexos
- Classificação automática (Nota Fiscal / Requisição de Compra / Outros)
- Extração de dados por regex (fornecedor, CNPJ, número, valor)
- Visualização do documento com preview de anexos
- Marcar item como **FEITO** e registrar histórico

---

## Arquitetura

- Backend: **Python + FastAPI**
- Banco de dados: **PostgreSQL**
- Frontend: **React (Vite)**
- Armazenamento de anexos: local (./storage) — preparado para S3
- OCR / PDF: **pdfplumber**, **Pillow** (usar OCR só quando necessário)

---

## Como rodar (local, via Docker)

1. Copie o `.env.example` para `.env` e ajuste se necessário.

2. Inicie os serviços:

```bash
docker-compose up --build
```

3. Backend estará em: `http://localhost:8000`
   - Docs OpenAPI: `http://localhost:8000/docs`

4. Frontend (dev):

```bash
cd frontend
npm install
npm run dev
```

> Se usar Docker, expomos a porta do frontend via `Dockerfile` e `docker-compose` quando desejado.

---

## Endpoints principais (FastAPI)

- GET `/documentos` — lista documentos (filtros por tipo/status)
- GET `/documentos/{id}` — detalhes (+ histórico, anexos)
- POST `/documentos/{id}/confirmar?usuario=<usuario>` — marca como FEITO
- GET `/documentos/{id}/email-original` — retorna link para abrir o e-mail original

---

## Estrutura inicial criada

- `backend/app` — código FastAPI
  - `db/` — modelos SQLAlchemy e sessão
  - `api/` — endpoints (documentos)
  - `services/` — stubs para coleta, classificação, extração, preview e histórico
- `frontend/` — app React (Vite) com telas `Inbox` e `Detail`
- `docker-compose.yml` — Postgres + backend (dev mount)

---

## Próximos passos recomendados

1. Implementar persistência completa do coletor IMAP (idempotência, anexos, message_id)
2. Testes automatizados (pytest) e pipelines CI
3. Mecanismo de filas (Redis) para processamento de anexos e pre-processamento OCR
4. Políticas de retenção e integração com S3
5. Role-based access e autenticação (ex: OAuth / JWT)

---

Se quiser, posso:
- Implementar coleta IMAP completa e gravação de anexos
- Adicionar migração com Alembic
- Criar testes de integração (pytest + docker-compose)

Escolha uma tarefa e eu continuo.