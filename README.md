# GMR Investment Analysis Backend

FastAPI service that exposes blob storage utilities, Semantic Kernel orchestration hooks, and health endpoints for the GMR research environment. The API delivers JSON responses compatible with the Vite frontend and can initiate multi-agent workflows on demand.

## Project Structure

```
deploymentdemogmr/
├─ main.py                          # FastAPI application entry point
├─ requirements.txt                 # Python dependencies
├─ startup.sh                       # Sample launch script for hosted environments
├─ Semantic_kernel_Orchestration/   # Agent orchestrators, prompts, and outputs
│  ├─ analysis_outputs/             # Generated reports uploaded to Blob Storage
│  ├─ Templates/                    # Instruction assets for each agent
│  └─ *.py                          # Semantic Kernel pipelines and helpers
├─ processed_data/                  # Preprocessed artefacts consumed by the agents
├─ frontend/creditreportautomationUI/ # Legacy UI snapshot (reference only)
├─ .env / .env.example              # Environment configuration (gitignored)
└─ .github/workflows/               # CI pipeline for backend deployment
```

## Prerequisites

- Python 3.10 or newer
- pip (or pipx) with virtual environment capability
- Azure CLI authenticated against the target subscription
- Optional: curl or Postman for exercising endpoints

## Configuration

1. Copy the sample environment file and create your local configuration:
	```bash
	cd deploymentdemogmr
	copy .env.example .env       # Windows
	# or
	cp .env.example .env         # macOS/Linux
	```
2. Populate `.env` with values that match your Azure resources:
	- Storage account and container (`AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME`)
	- Azure AI project identifiers (endpoint, subscription ID, resource group, project name)
	- Azure OpenAI deployment information (or remove if unused)
	- Optional overrides such as `PORT`, `ROOT_PATH`, or `ENVIRONMENT`
3. Ensure the identity running the service (developer account, service principal, or managed identity) has **Storage Blob Data Contributor** on the storage account.

The refreshed `.env.example` lists every required variable so new clones can configure the backend without hidden assumptions.

## Getting Started (Local Development)

```bash
cd deploymentdemogmr
python -m venv .venv
.venv\Scripts\activate    # PowerShell (use: source .venv/bin/activate on macOS/Linux)
pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Default base URL: http://localhost:8000
- Interactive docs: http://localhost:8000/docs and http://localhost:8000/redoc

## Local Verification Checklist

1. **Health check**
	```bash
	curl http://localhost:8000/health
	```
	Expect `"status": "healthy"` once Azure credentials resolve.
2. **Blob listing**
	```bash
	curl http://localhost:8000/api/blobs
	```
	Confirms access to the configured container.
3. **Agent orchestration demo (optional)**
	```bash
	curl -X POST http://localhost:8000/api/analysis/start
	```
	Produces a session payload and uploads demo artefacts to Blob Storage.

## Key Endpoints

- `GET /` — Welcome payload with available routes
- `GET /health` — Storage connectivity and service status report
- `GET /api/blobs` — List blobs (supports optional prefix filtering)
- `GET /api/blobs/{blob_name}/download` — Stream blob content as a file response
- `GET /api/blobs/{blob_name}/content` — Inspect blob content as JSON or text
- `GET /api/blobs/{blob_name}/exists` — Check if a blob is present
- `POST /api/blobs/upload` — Upload or overwrite a blob (multipart/form-data)
- `DELETE /api/blobs/{blob_name}` — Remove a blob from the container
- `POST /api/analysis/start` — Kick off the Semantic Kernel orchestration pipeline
- `GET /api/analysis/status` — Inspect orchestration outputs and blob artefacts
- `POST /api/agents/deploy-folder` — Copy Semantic Kernel assets to a temporary workspace for execution

## Azure App Service Deployment

1. **Create the App Service plan**
	- In the Azure portal, select **Create a resource** → **App Service plan**.
	- Choose the subscription, set **Resource group** (for example, `fsi-demos`), pick a region, select a Linux plan (B1 or higher), and create the plan.
2. **Provision the Web App**
	- From the plan, create a new **Web App**.
	- Select the same subscription/resource group, enter a globally unique name (for example, `gmr-backend-app`), choose **Code** → **Python 3.10**, and finish the wizard.
3. **Enable managed identity**
	- Open the Web App, navigate to **Identity**, and switch the **System assigned** identity to **On**. Save to provision the identity.
4. **Grant Blob Storage permissions to the managed identity**
	- In the storage account (`fsidemo`), go to **Access control (IAM)** → **Add role assignment**.
	- Assign **Storage Blob Data Contributor** to the Web App’s managed identity.
5. **Configure application settings**
	- In the Web App, open **Configuration** → **Application settings**.
	- Add the variables from `.env` (storage, AI project, OpenAI). Use Key Vault references or deployment slots for secrets where possible. Save and restart.
6. **Deploy code**
	- Package the backend (zip deploy, GitHub Actions, or Azure DevOps). The included `startup.sh` demonstrates how the runtime activates the environment and launches `uvicorn`.
7. **Verify deployment**
	- Browse to `https://<web-app-name>.azurewebsites.net/health` to confirm the service reports `"status": "healthy"`.

## Additional Tips

- Keep `processed_data/` synced with the documents expected by the orchestration pipeline; agents resolve the directory via the `GMR_DATA_DIR` variable.
- For large files, consider chunked uploads or generating SAS URLs as a future enhancement.
- The orchestration flow writes to temporary directories; ensure the hosting platform permits write access to `/tmp` or override the path through environment variables.

## Related Resources

- Frontend deployment instructions live in deploymentfrontendgmr/README.md.
- CI configuration for production deployment resides in .github/workflows/main_creditbackend.yml.

