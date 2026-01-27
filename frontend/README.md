# GMR Investment Analysis Frontend

React + TypeScript interface for the investment analysis platform. This client mirrors the production layout while pointing to the research backend by default, surfacing multi-agent reports, workflow status, and Azure Blob documents in a single dashboard.

## Prerequisites

- Node.js 20+
- npm 9+

## Getting Started

1. Install dependencies
   ```bash
   npm install
   ```
2. Start the development server (Vite on http://localhost:3002)
   ```bash
   npm run dev
   ```
3. Create a production build
   ```bash
   npm run build
   ```
4. Preview the built bundle locally
   ```bash
   npm run preview
   ```

## Folder Structure

```
 frontend/
 ├── src/
 │   ├── components/            # UI widgets, dashboard views, and shadcn/ui primitives
 │   ├── hooks/                 # Custom hooks for SSE streams and Azure Blob access
 │   ├── lib/                   # API clients, blob services, and shared utilities
 │   ├── types/                 # TypeScript definitions for GMR domain objects
 │   ├── App.tsx                # Root application layout
 │   └── main.tsx               # Vite bootstrap entry point
 ├── public/                    # Static assets and processed data samples
 ├── package.json
 └── vite.config.ts
```

## Environment Configuration

Provide runtime settings through `.env` (copy from `.env.example`). Common values:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=your_openai_api_key
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
VITE_AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Adjust `VITE_API_BASE_URL` when pointing at deployed FastAPI instances.

## Deployment Notes

- Ensure the backend exposes the routes expected by `VITE_API_BASE_URL` (blob CRUD and orchestration endpoints).
- `npm run build` emits static assets in `dist/`; publish to Azure Static Web Apps, Storage static websites, or any static host.
- Synchronize the `public/processed_data` examples with your Blob Storage container if you want the dashboard to ship with reference content.
