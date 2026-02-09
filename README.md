# BFSI Multi-Agent Corporate Credit Assessment
AI-powered corporate credit analysis platform using Azure AI services for automated loan proposal verification, financial analysis, and comprehensive credit report generation.

## 🚀 Features

- **Multi-Agent Architecture** — 4 specialized AI agents for comprehensive credit assessment
- **Real-Time Processing** — Live agent progress tracking and updates
- **Azure Integration** — Leverages Azure AI, OpenAI, Azure AI Projects, and Semantic Kernel
- **Container-Ready** — Docker support with Azure Container Apps deployment
- **Automated Credit Reports** — Generate comprehensive PDF credit analysis reports

## 🤖 AI Agents

| Agent | Description | Output |
|-------|-------------|--------|
| **Proposal Verification Agent** | Validates loan proposal details, checks completeness, and verifies alignment with credit policies | Proposal validation report with compliance status |
| **Company Profile Agent** | Analyzes company background, management, business model, market position, and governance | Detailed company profile and risk assessment |
| **Financial Analysis Agent** | Performs comprehensive financial analysis including ratios, trends, cash flows, and creditworthiness evaluation | Financial health report with credit metrics |
| **PDF Generator Agent** | Synthesizes all agent outputs into comprehensive credit assessment report with recommendations | Final credit report in PDF format |

## 🛠️ Tech Stack

**Backend:** Python 3.10+, FastAPI, Uvicorn, Azure AI Projects SDK, Semantic Kernel

**Frontend:** React 18, TypeScript, Vite, TailwindCSS

**AI:** Azure OpenAI, Azure AI Projects, Semantic Kernel

**Infrastructure:** Docker, Azure Container Apps, Azure Container Registry, Azure Blob Storage

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Azure subscription with required services
- Azure CLI installed

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/bfsi-multi-agent-corporate-credit-assessment.git
   cd bfsi-multi-agent-corporate-credit-assessment
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cd backend
   copy .env.example .env
   # Edit .env with your Azure credentials
   
   # Frontend
   cd ../frontend
   copy .env.example .env
   # Edit .env with backend URL
   ```

3. **Install and run backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Install and run frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`


## ☁️ Deployment

### Azure Container Apps

#### Prerequisites
- Azure CLI installed (`az --version`)
- Azure subscription with required services

#### Deploy Backend and Frontend

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name bfsi-credit-assessment-rg --location eastus

# 3. Create container registry
az acr create --resource-group bfsi-credit-assessment-rg \
  --name bfsicreditacr --sku Basic --admin-enabled true

# 4. Create Container Apps environment
az containerapp env create \
  --name bfsi-credit-env \
  --resource-group bfsi-credit-assessment-rg \
  --location eastus

# 5. Build and deploy backend
az acr build --registry bfsicreditacr --image bfsi-backend:latest ./backend

az containerapp create \
  --name bfsi-backend \
  --resource-group bfsi-credit-assessment-rg \
  --environment bfsi-credit-env \
  --image bfsicreditacr.azurecr.io/bfsi-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server bfsicreditacr.azurecr.io \
  --cpu 1.0 --memory 2.0Gi \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-api-key" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
    AZURE_AI_PROJECT_ENDPOINT="https://your-ai-project.openai.azure.com/" \
    AZURE_AI_PROJECT_SUBSCRIPTION_ID="your-sub-id" \
    AZURE_AI_PROJECT_RESOURCE_GROUP="your-rg" \
    AZURE_AI_PROJECT_NAME="your-project" \
    AZURE_STORAGE_ACCOUNT_NAME="yourstorageaccount" \
    AZURE_STORAGE_CONTAINER_NAME="credit-reports"

# 6. Get backend URL
BACKEND_URL=$(az containerapp show --name bfsi-backend \
  --resource-group bfsi-credit-assessment-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Backend URL: https://$BACKEND_URL"

# 7. Build and deploy frontend
az acr build --registry bfsicreditacr \
  --image bfsi-frontend:latest \
  --build-arg VITE_API_BASE_URL=https://$BACKEND_URL \
  ./frontend

az containerapp create \
  --name bfsi-frontend \
  --resource-group bfsi-credit-assessment-rg \
  --environment bfsi-credit-env \
  --image bfsicreditacr.azurecr.io/bfsi-frontend:latest \
  --target-port 80 \
  --ingress external \
  --registry-server bfsicreditacr.azurecr.io \
  --cpu 0.5 --memory 1.0Gi

# 8. Get frontend URL
FRONTEND_URL=$(az containerapp show --name bfsi-frontend \
  --resource-group bfsi-credit-assessment-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Frontend URL: https://$FRONTEND_URL"
echo "Deployment complete!"
```

#### Useful Commands

```bash
# View logs
az containerapp logs show --name bfsi-backend --resource-group bfsi-credit-assessment-rg --follow

# Update backend after code changes
az acr build --registry bfsicreditacr --image bfsi-backend:latest ./backend
az containerapp update --name bfsi-backend --resource-group bfsi-credit-assessment-rg \
  --image bfsicreditacr.azurecr.io/bfsi-backend:latest

# Delete all resources
az group delete --name bfsi-credit-assessment-rg --yes
```

## 🔧 Configuration

### Required Azure Resources

| Resource | Purpose | Setup |
|----------|---------|-------|
| **Azure AI Project** | AI agent orchestration and management | Create in Azure AI Studio |
| **Azure OpenAI** | GPT model deployment | Deploy GPT-4o or GPT-4o-mini |
| **Azure Storage Account** | Store credit reports and analysis outputs | Create storage account with blob container |
| **Azure Container Registry** | Docker image storage | Create ACR with admin enabled |
| **Azure Container Apps** | Application hosting | Create environment for apps |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI service endpoint |
| `AZURE_OPENAI_API_KEY` | ✅ | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | ✅ | Model deployment name (e.g., `gpt-4o`) |
| `AZURE_AI_PROJECT_ENDPOINT` | ✅ | Azure AI Project endpoint |
| `AZURE_AI_PROJECT_SUBSCRIPTION_ID` | ✅ | Azure subscription ID |
| `AZURE_AI_PROJECT_RESOURCE_GROUP` | ✅ | Azure resource group name |
| `AZURE_AI_PROJECT_NAME` | ✅ | Azure AI project name |
| `AZURE_STORAGE_ACCOUNT_NAME` | ✅ | Azure Storage account for credit reports |
| `AZURE_STORAGE_CONTAINER_NAME` | ✅ | Container name for report storage |
| `PORT` | ⬜ | API server port (default: `8000`) |
| `ENVIRONMENT` | ⬜ | Environment mode (`development`/`production`) |
| `VITE_API_BASE_URL` | ✅ | Frontend: Backend API URL |

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/fetchjson?file=<name>` | Fetch processed credit data and analysis outputs |
| `POST` | `/api/orchestrate` | Trigger multi-agent credit analysis workflow |
| `POST` | `/api/upload` | Upload loan proposal and financial documents |
| `GET` | `/docs` | Interactive Swagger UI |

Interactive documentation available at: `/docs` (Swagger UI)

## 🏗️ Project Structure

```
bfsi-multi-agent-corporate-credit-assessment/
├── backend/                    # FastAPI backend
│   ├── Semantic_kernel_Orchestration/  # AI orchestration
│   │   ├── orchestrator.py     #   Main orchestration engine
│   │   ├── companyprofileagent.py #   Company analysis agent
│   │   ├── FinDocAgent.py      #   Financial document agent
│   │   ├── PropslVerficationAgent.py # Proposal verification agent
│   │   ├── pdf_generator_agent.py #   Report generation agent
│   │   ├── analysis_outputs/   #   Generated credit reports
│   │   └── Templates/          #   Agent prompt templates
│   ├── processed_data/         # Preprocessed financial data
│   │   ├── LoanProposal_processed.json
│   │   ├── Financial_ratios_processed.json
│   │   ├── GMR_processed.json
│   │   └── RatingRationale_processed.json
│   ├── main.py                 # API entry point
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container image
│   └── .env.example            # Environment template
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Application pages
│   │   │   ├── WorkflowPage/   #   Workflow monitor
│   │   │   └── AgentsPage/     #   Agent outputs
│   │   ├── hooks/              # Custom React hooks
│   │   └── types/              # TypeScript types
│   ├── public/                 # Static assets
│   │   └── processed_data/     # Sample credit data
│   ├── Dockerfile              # Frontend container image
│   ├── package.json            # Node dependencies
│   └── .env.example            # Environment template
├── docker-compose.yml          # Local development
├── DEPLOYMENT.md               # Deployment documentation
└── README.md                   # This file
```

## 🔒 Security

- **Environment Variables** — Credentials stored in Azure Container Apps configuration (never in code)
- **Azure Key Vault** — Use for production secrets management
- **CORS** — Properly configured for frontend access only
- **HTTPS** — Enforced on all Azure deployments
- **.gitignore** — Sensitive files and credentials excluded from source control

## 📊 Monitoring

- **Health Check** — `GET /` endpoint for availability monitoring
- **Structured Logging** — Console logs with detailed agent execution tracking
- **Azure Monitor** — Container Apps built-in metrics and log streaming
- **Real-time Logs** — `az containerapp logs show --follow`
- **Credit Report Tracking** — All generated reports stored in Azure Blob Storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure AI Studio Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
- [Azure AI Projects SDK](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
