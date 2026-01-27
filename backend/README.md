# Backend

FastAPI service that brokers Azure Blob Storage access and kicks off the multi-agent credit analysis workflow. It backs the investment-analysis UI and is designed to run in Azure App Service with managed identity.

## Layout

```
backend/
├─ main.py
├─ requirements.txt
├─ startup.sh
├─ Semantic_kernel_Orchestration/
├─ processed_data/
├─ .env          # developer secrets (not checked in)
└─ .env.example  # template with required settings
```

## Configure

1. Copy `.env.example` to `.env` and fill in Azure resource values (storage account, container, Semantic Kernel project, OpenAI deployment).
2. Make sure the identity you use locally or in Azure has **Storage Blob Data Contributor** on the storage account.
3. Optional overrides: `PORT`, `ROOT_PATH`, `ENVIRONMENT`.

## Run Locally

```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # use .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Smoke tests:
- `GET /health` – confirms Blob Storage connectivity
- `GET /api/blobs` – lists container contents
- `POST /api/analysis/start` – triggers the orchestration demo

## Deploy (Portal Outline)

1. Create or reuse an App Service plan (Linux, Python 3.10).
2. Provision a Web App, enable the system-assigned managed identity, and grant it **Storage Blob Data Contributor** on the storage account.
3. Add the `.env` values under **Configuration → Application settings** (use Key Vault for secrets when possible).
4. Deploy the folder (zip deploy, GitHub Actions, or other pipeline). `startup.sh` illustrates the launch command.
5. Validate at `https://<app-name>.azurewebsites.net/health`.

## Essential Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Storage + service status |
| GET | `/api/blobs` | List blobs in the configured container |
| POST | `/api/blobs/upload` | Upload or overwrite a blob |
| POST | `/api/analysis/start` | Run the Semantic Kernel analysis workflow |

For frontend notes, see `frontend/README.md`.

