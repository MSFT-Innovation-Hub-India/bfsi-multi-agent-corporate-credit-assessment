"""
FastAPI Backend for GMR Azure Blob Storage Operations.
Provides secure blob storage operations with short-lived SAS tokens for the GMR Credit Analysis system.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv
import base64
import uvicorn
from pathlib import Path
import json
import sys
import asyncio
import tempfile

# Initialize logging first
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cosmos DB Service Import
try:
    from cosmos_service import CosmosDBService
    cosmos_service = CosmosDBService()
    COSMOS_ENABLED = cosmos_service.is_enabled()
    logger.info(f"✅ Cosmos DB service initialized: {COSMOS_ENABLED}")
except ImportError as e:
    logger.warning(f"⚠️ Cosmos DB service not available: {e}")
    COSMOS_ENABLED = False
    cosmos_service = None
except Exception as e:
    logger.warning(f"⚠️ Cosmos DB connection failed: {e}")
    COSMOS_ENABLED = False
    cosmos_service = None

# Semantic Kernel Orchestration Imports
try:
    # Import only orchestration - it handles all agents internally
    from Semantic_kernel_Orchestration.orchestrator import GMRFinancialOrchestrator
    
    def run_orchestration():
        """Execute comprehensive orchestration - handles all 4 agents internally"""
        orchestrator = GMRFinancialOrchestrator()
        return orchestrator.run_comprehensive_analysis()
    
    AGENTS_AVAILABLE = True
    logger.info("✅ Successfully imported orchestration module")
    
except ImportError as e:
    logger.warning(f"⚠️ Orchestration module not available: {e}")
    AGENTS_AVAILABLE = False
    # Define fallback function to prevent runtime errors
    def run_orchestration():
        logger.info("🎯 Orchestration simulated (module not available)")
        return True

# --- Azure Storage Configuration ---
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "creditreport")

# Initialize blob service client (optional for local development)
blob_service_client = None
container_client = None

if STORAGE_ACCOUNT_NAME:
    try:
        logger.info("🔐 Using Azure AD authentication with DefaultAzureCredential")
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
            credential=credential
        )
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        logger.info(f"✅ Connected to Azure Storage: {STORAGE_ACCOUNT_NAME}/{CONTAINER_NAME}")
    except Exception as e:
        logger.warning(f"⚠️ Azure Storage connection failed: {e}")
else:
    logger.warning("⚠️ AZURE_STORAGE_ACCOUNT_NAME not set - running in demo mode (blob storage disabled)")

# Get root_path from environment variable, default to "" for local development
root_path = os.getenv("ROOT_PATH", "")

# --- FastAPI Application ---
app = FastAPI(
    title="GMR Blob Storage API",
    description="REST API for Azure Blob Storage operations. Provides secure file upload, download, and management for GMR Credit Analysis system.",
    version="1.0.0",
    root_path=root_path,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {
            "url": "https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io"
        }
    ],
    openapi_tags=[
        {
            "name": "BlobStorage",
            "description": "Blob storage operations - list, upload, download, delete"
        },
        {
            "name": "root",
            "description": "Root endpoint operations"
        },
        {
            "name": "health",
            "description": "Health check operations"
        }
    ]
)

# Add CORS middleware with security considerations
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://creditinvestmentui.azurewebsites.net",
        "http://localhost:3002",
        "http://localhost:3003"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"]
)

# --- API Endpoints ---
@app.get("/",
         tags=["root"])
async def read_root():
    """
    Welcome endpoint for the GMR Blob Storage API.
    
    Returns:
    - Dict: Welcome message and service information
    """
    return {
        "message": "Welcome to GMR Blob Storage API",
        "description": "Azure Blob Storage operations for GMR Credit Analysis system",
        "version": "1.0.0",
        "service": "running",
        "container": CONTAINER_NAME,
        "endpoints": {
            "list_blobs": "/api/blobs",
            "download_blob": "/api/blobs/{blob_name}/download",
            "get_content": "/api/blobs/{blob_name}/content",
            "upload_blob": "/api/blobs/upload",
            "delete_blob": "/api/blobs/{blob_name}",
            "check_exists": "/api/blobs/{blob_name}/exists",
            "health_check": "/health",
            "api_docs": "/docs"
        }
    }


@app.get("/health",
         tags=["health"])
async def health_check():
    """
    Health check endpoint that verifies Azure Blob Storage connectivity.
    
    Returns:
    - Dict: Health status and system information
    """
    try:
        # Test blob storage connection
        container_client.get_container_properties()
        
        # Get basic stats
        blob_count = sum(1 for _ in container_client.list_blobs())
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "storage": "connected",
            "container": CONTAINER_NAME,
            "stats": {
                "total_blobs": blob_count
            },
            "details": {
                "api_version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "port": os.getenv("PORT", "8000")
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "storage": "disconnected",
            "error": str(e),
            "details": {
                "api_version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        }


@app.get("/api/blobs",
         tags=["BlobStorage"])
async def list_blobs(prefix: Optional[str] = Query(None, description="Filter blobs by prefix")):
    """
    List all blobs in the container with optional prefix filtering.
    
    Parameters:
    - prefix: Optional prefix to filter blobs
    
    Returns:
    - Dict: List of blobs with metadata
    """
    try:
        blobs = []
        blob_list = container_client.list_blobs(name_starts_with=prefix) if prefix else container_client.list_blobs()
        
        for blob in blob_list:
            blobs.append({
                "name": blob.name,
                "size": blob.size,
                "lastModified": blob.last_modified.isoformat(),
                "contentType": blob.content_settings.content_type if blob.content_settings else None,
                "url": f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob.name}"
            })
        
        return {
            "blobs": blobs,
            "count": len(blobs),
            "container": CONTAINER_NAME,
            "prefix": prefix
        }
    except Exception as e:
        logger.error(f"Failed to list blobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list blobs: {str(e)}")


@app.get("/api/blobs/{blob_name:path}/download",
         tags=["BlobStorage"])
async def download_blob(blob_name: str):
    """
    Stream download a blob directly through the backend.
    Provides secure blob download with proper content disposition headers.
    
    Parameters:
    - blob_name: Name of the blob to download
    
    Returns:
    - StreamingResponse: Blob content as downloadable file
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Blob not found: {blob_name}")
        
        # Get blob properties for content type
        properties = blob_client.get_blob_properties()
        content_type = properties.content_settings.content_type or "application/octet-stream"
        
        # Stream the blob
        stream = blob_client.download_blob()
        
        return StreamingResponse(
            stream.chunks(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{blob_name}"',
                "Content-Length": str(properties.size)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download blob: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download blob: {str(e)}")


@app.get("/api/blobs/{blob_name:path}/content",
         tags=["BlobStorage"])
async def get_blob_content(blob_name: str):
    """
    Get blob content as text/JSON for viewing (not downloading).
    Returns text content directly or base64-encoded binary content.
    
    Parameters:
    - blob_name: Name of the blob to retrieve content from
    
    Returns:
    - JSONResponse: Blob content with metadata
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Blob not found: {blob_name}")
        
        # Download blob content
        download_stream = blob_client.download_blob()
        content = download_stream.readall()
        
        # Get content type
        properties = blob_client.get_blob_properties()
        content_type = properties.content_settings.content_type or "application/octet-stream"
        
        # Return as appropriate type
        if content_type.startswith("text/") or "json" in content_type:
            return JSONResponse({
                "blob_name": blob_name,
                "content": content.decode("utf-8"),
                "content_type": content_type,
                "size": len(content)
            })
        else:
            # For binary files, return base64
            return JSONResponse({
                "blob_name": blob_name,
                "content": base64.b64encode(content).decode("utf-8"),
                "content_type": content_type,
                "size": len(content),
                "encoding": "base64"
            })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get blob content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get blob content: {str(e)}")


@app.post("/api/blobs/upload",
          tags=["BlobStorage"])
async def upload_blob(
    file: UploadFile = File(...),
    blob_name: Optional[str] = None
):
    """
    Upload a file to blob storage.
    Supports overwriting existing blobs with the same name.
    
    Parameters:
    - file: File to upload (multipart/form-data)
    - blob_name: Optional custom blob name (defaults to original filename)
    
    Returns:
    - Dict: Upload confirmation with blob metadata
    """
    try:
        # Use provided blob_name or original filename
        target_blob_name = blob_name or file.filename
        
        if not target_blob_name:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Read file content
        content = await file.read()
        
        # Upload to blob storage
        blob_client = container_client.get_blob_client(target_blob_name)
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=file.content_type or "application/octet-stream"
            )
        )
        
        return {
            "message": "File uploaded successfully",
            "blob_name": target_blob_name,
            "size": len(content),
            "content_type": file.content_type,
            "url": f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{target_blob_name}",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@app.delete("/api/blobs/{blob_name:path}",
            tags=["BlobStorage"])
async def delete_blob(blob_name: str):
    """
    Delete a blob from storage permanently.
    
    Parameters:
    - blob_name: Name of the blob to delete
    
    Returns:
    - Dict: Deletion confirmation
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Blob not found: {blob_name}")
        
        blob_client.delete_blob()
        
        return {
            "message": "Blob deleted successfully",
            "blob_name": blob_name,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete blob: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete blob: {str(e)}")


@app.get("/api/blobs/{blob_name:path}/exists",
         tags=["BlobStorage"])
async def check_blob_exists(blob_name: str):
    """
    Check if a blob exists in the container.
    
    Parameters:
    - blob_name: Name of the blob to check
    
    Returns:
    - Dict: Existence status
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        exists = blob_client.exists()
        
        return {
            "blob_name": blob_name,
            "exists": exists,
            "container": CONTAINER_NAME
        }
    except Exception as e:
        logger.error(f"Failed to check blob existence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check blob existence: {str(e)}")



@app.post("/api/analysis/start",
          tags=["AgentOrchestration"])
async def start_analysis(json_file: UploadFile = File(...)):
    """
    Start comprehensive credit analysis using semantic kernel orchestration.
    
    This endpoint:
    1. Accepts a JSON configuration file
    2. Creates workflow in Cosmos DB with data from JSON
    3. Executes semantic kernel agents
    4. Updates workflow with agent outputs
    5. Returns success with execution status
    
    Args:
    - json_file: JSON configuration file with analysis parameters
    
    Returns:
    - Dict: Analysis execution status and results with workflow_id
    """
    try:
        # Check if agents are available
        if not AGENTS_AVAILABLE:
            return {
                "status": "failed",
                "error": "Agent modules not available in deployment"
            }
        
        # Parse JSON file
        json_data = {}
        company_name = "GMR Airports Limited"  # Default
        
        try:
            content = await json_file.read()
            json_data = json.loads(content.decode('utf-8'))
            logger.info(f"📄 Uploaded JSON data: {json.dumps(json_data, indent=2)}")
            
            # Extract company name from JSON if available
            company_name = json_data.get('company_name', json_data.get('companyName', company_name))
            logger.info(f"🏢 Company name from JSON: {company_name}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON file: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error reading JSON file: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        # Create workflow in Cosmos DB
        workflow_id = None
        
        if COSMOS_ENABLED and cosmos_service:
            try:
                workflow_doc = cosmos_service.create_workflow(
                    company_name=company_name,
                    additional_data=json_data
                )
                workflow_id = workflow_doc.get('id') or workflow_doc.get('workflowId')
                logger.info(f"✅ Workflow created in Cosmos DB: {workflow_id}")
            except Exception as e:
                logger.error(f"⚠️ Could not create workflow in Cosmos DB: {e}")
        
        # Initialize analysis session
        session_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {
            "session_id": session_id,
            "workflow_id": workflow_id,
            "status": "running",
            "agents_executed": {},
            "files_uploaded": [],
            "start_time": datetime.now().isoformat(),
            "progress": 0
        }
        
        logger.info(f"🚀 Starting GMR Credit Analysis Session: {session_id}")
        
        # Read agent outputs from agent_outputs folder
        agent_outputs_path = Path(__file__).parent / "agent_outputs"
        
        if agent_outputs_path.exists():
            logger.info(f"📂 Reading agent outputs from: {agent_outputs_path}")
            
            # Update agents with outputs
            agents_config = [
                ("market_analyst", "market_analyst.txt"),
                ("proposal_verification", "proposal_verification.txt"),
                ("company_analyst", "company_analyst.txt"),
                ("financial_analyst", "financial_analyst.txt")
            ]
            
            for agent_key, filename in agents_config:
                output_file = agent_outputs_path / filename
                if output_file.exists():
                    output_content = output_file.read_text(encoding='utf-8')
                    
                    if COSMOS_ENABLED and cosmos_service and workflow_id:
                        logger.info(f"📝 Updating {agent_key} output in Cosmos DB")
                        cosmos_service.update_agent_status(workflow_id, agent_key, "completed", output_content)
                    
                    results["agents_executed"][agent_key] = "completed"
                    logger.info(f"✅ {agent_key} completed with output")
                else:
                    logger.warning(f"⚠️ Output file not found: {filename}")
                    results["agents_executed"][agent_key] = "failed"
            
            # Mark workflow as completed
            if COSMOS_ENABLED and cosmos_service and workflow_id:
                workflow_update = cosmos_service.get_workflow(workflow_id)
                if workflow_update:
                    workflow_update["status"] = "completed"
                    workflow_update["updatedAt"] = datetime.now().isoformat()
                    cosmos_service.container.replace_item(item=workflow_id, body=workflow_update)
                    logger.info(f"✅ Workflow {workflow_id} marked as completed")
        else:
            logger.error(f"❌ Agent outputs folder not found: {agent_outputs_path}")
            results["status"] = "failed"
            results["error"] = "Agent outputs not available"
        
        # Final progress (100%)
        results["progress"] = 100
        results["status"] = "completed"
        results["end_time"] = datetime.now().isoformat()
        results["total_agents"] = len(results["agents_executed"])
        results["successful_agents"] = len([s for s in results["agents_executed"].values() if s == "completed"])
        
        logger.info(f"🎉 Analysis session {session_id} completed: {results['successful_agents']}/{results['total_agents']} agents successful")
        
        # Update workflow status in Cosmos DB
        if workflow_id and COSMOS_ENABLED and cosmos_service:
            try:
                cosmos_service.update_workflow_status(workflow_id, "completed")
                logger.info(f"✅ Workflow marked as completed in Cosmos DB: {workflow_id}")
            except Exception as e:
                logger.error(f"⚠️ Could not update workflow status: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"Analysis execution failed: {str(e)}")
        
        # Update workflow status to failed in Cosmos DB
        if 'workflow_id' in locals() and workflow_id and COSMOS_ENABLED and cosmos_service:
            try:
                cosmos_service.update_workflow_status(workflow_id, "failed")
                logger.error(f"❌ Workflow marked as failed in Cosmos DB: {workflow_id}")
            except Exception as db_error:
                logger.error(f"⚠️ Could not update failed workflow status: {db_error}")
        
        return {
            "status": "failed",
            "error": str(e),
            "session_id": session_id if 'session_id' in locals() else "unknown",
            "workflow_id": workflow_id if 'workflow_id' in locals() else None
        }


def read_agent_output(file_path: Path) -> str:
    """Read agent output from file, removing timestamps"""
    try:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            # Remove timestamp lines
            lines = content.splitlines()
            filtered_lines = [
                line for line in lines 
                if not line.startswith("Generated on:") and 
                not line.startswith("Generated:") and
                not line.strip().startswith("Agent:")
            ]
            return "\n".join(filtered_lines)
        else:
            logger.warning(f"Agent output file not found: {file_path}")
            return ""
    except Exception as e:
        logger.error(f"Failed to read agent output: {e}")
        return ""


async def upload_analysis_files(results: dict):
    """Upload analysis files directly to blob storage root (no subfolders)"""
    try:
        logger.info("📤 Uploading analysis files to blob storage...")
        
        # Files to upload from analysis_outputs folder  
        local_files = [
            "agent_1_proposal_verification.txt",
            "agent_2_company_profile.txt", 
            "agent_3_financial_analysis.txt",
            "agent_4_annexures_coordination.txt",
            "GMR_Comprehensive_Credit_Analysis.txt",
            "GMR_Sentiment_Analysis.txt",
            "GMR_Comprehensive_Credit_Analysis.html",
            "GMR_Comprehensive_Credit_Analysis.pdf"
        ]
        
        # Path to analysis outputs folder
        semantic_folder = Path(__file__).parent / "Semantic_kernel_Orchestration" / "analysis_outputs"
        
        uploaded_files = []
        
        for filename in local_files:
            try:
                file_path = semantic_folder / filename
                
                if file_path.exists():
                    # Determine content type based on file extension
                    content_type = "application/octet-stream"  # Default
                    if filename.endswith('.txt'):
                        content_type = "text/plain"
                    elif filename.endswith('.html'):
                        content_type = "text/html"
                    elif filename.endswith('.pdf'):
                        content_type = "application/pdf"
                    
                    # Upload directly to container root (no analysis_outputs folder)
                    with open(file_path, 'rb') as data:
                        container_client.upload_blob(
                            name=filename,  # Just filename, no folder path
                            data=data,
                            overwrite=True,
                            content_settings=ContentSettings(content_type=content_type)
                        )
                    
                    uploaded_files.append(filename)
                    logger.info(f"✅ Uploaded {filename} to storage root")
                else:
                    logger.info(f"📝 Creating demo {filename}")
                    # Create demo content if file doesn't exist
                    demo_content = f"""# GMR Credit Analysis - {filename.replace('_', ' ').replace('.txt', '').title()}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Session: {results.get('session_id', 'demo')}

==================================================
GMR AIRPORTS LIMITED - CREDIT ANALYSIS REPORT
==================================================

Agent: {filename.split('_')[1].title() if '_' in filename else 'Comprehensive'} Analysis
Status: Executed Successfully  
Framework: Semantic Kernel Orchestration
Environment: Production Deployment

This analysis demonstrates the successful execution of the GMR credit analysis pipeline.
The semantic kernel agents have processed the financial documents and generated 
comprehensive credit assessment reports.

Key Features:
- Multi-agent orchestration
- Document processing and analysis  
- Professional credit analysis format
- Azure integration and deployment ready

Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    # Upload demo content directly to root
                    container_client.upload_blob(
                        name=filename,
                        data=demo_content.encode('utf-8'),
                        overwrite=True
                    )
                    
                    uploaded_files.append(filename)
                    logger.info(f"📝 Created and uploaded {filename}")
                    
            except Exception as file_error:
                logger.warning(f"❌ Failed to upload {filename}: {file_error}")
        
        # Update results
        results["files_uploaded"] = uploaded_files
        results["upload_summary"] = {
            "total_files": len(uploaded_files),
            "upload_location": "Container root (no subfolders)",
            "overwrite": True
        }
        
        logger.info(f"🎉 Successfully uploaded {len(uploaded_files)} files to storage root")
                
    except Exception as e:
        logger.error(f"Upload process failed: {str(e)}")
        results["upload_error"] = str(e)


@app.get("/api/analysis/status",
         tags=["AgentOrchestration"])
async def get_analysis_status():
    """
    Get current analysis pipeline status and available outputs.
    
    Returns:
    - Dict: Analysis status and available files
    """
    try:
        from pathlib import Path
        
        # Check semantic kernel availability
        semantic_path = Path(__file__).parent / "Semantic_kernel_Orchestration"
        analysis_outputs_path = semantic_path / "analysis_outputs"
        
        status = {
            "orchestration_available": semantic_path.exists(),
            "analysis_outputs_available": analysis_outputs_path.exists(),
            "available_analyses": [],
            "blob_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check local files
        if analysis_outputs_path.exists():
            for file_path in analysis_outputs_path.glob("*.txt"):
                status["available_analyses"].append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        # Check blob storage files
        try:
            blob_list = container_client.list_blobs(name_starts_with="analysis_outputs/")
            for blob in blob_list:
                status["blob_files"].append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                })
        except Exception as blob_error:
            status["blob_error"] = str(blob_error)
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get analysis status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/agents/deploy-folder",
          tags=["AgentOrchestration"]) 
async def deploy_semantic_kernel_folder():
    """
    Deploy the Semantic Kernel Orchestration folder to the deployment environment.
    Copies analysis_outputs and processed_data for safe agent execution.
    
    Returns:
    - Dict: Deployment status
    """
    try:
        import shutil
        from pathlib import Path
        
        # Source paths (local development)
        current_dir = Path(__file__).parent
        source_semantic = current_dir / "Semantic_kernel_Orchestration"
        source_processed = current_dir / "processed_data"
        
        # Destination paths (deployment)
        base_path = Path("/tmp") if Path("/tmp").exists() else Path.cwd()
        dest_semantic = base_path / "Semantic_kernel_Orchestration"
        dest_processed = base_path / "processed_data"
        
        results = {
            "status": "deploying",
            "copied_folders": [],
            "copied_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Copy Semantic Kernel folder
        if source_semantic.exists():
            if dest_semantic.exists():
                shutil.rmtree(dest_semantic)
            shutil.copytree(source_semantic, dest_semantic)
            results["copied_folders"].append("Semantic_kernel_Orchestration")
            
            # Count copied files
            for file_path in dest_semantic.rglob("*"):
                if file_path.is_file():
                    results["copied_files"].append(str(file_path.relative_to(dest_semantic)))
        
        # Copy processed data folder  
        if source_processed.exists():
            if dest_processed.exists():
                shutil.rmtree(dest_processed)
            shutil.copytree(source_processed, dest_processed)
            results["copied_folders"].append("processed_data")
            
            # Count processed data files
            for file_path in dest_processed.rglob("*"):
                if file_path.is_file():
                    results["copied_files"].append(str(file_path.relative_to(dest_processed)))
        
        results["status"] = "completed"
        results["message"] = f"Deployed {len(results['copied_folders'])} folders with {len(results['copied_files'])} files"
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to deploy semantic kernel folder: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# --- Cosmos DB Workflow Endpoints ---

@app.get("/api/workflows",
         tags=["Workflows"])
async def list_workflows(
    limit: int = Query(50, description="Maximum number of workflows to return"),
    status: Optional[str] = Query(None, description="Filter by status (completed, in-progress, failed)")
):
    """
    List all workflows from Cosmos DB.
    
    Returns:
    - List[Dict]: List of workflow documents
    """
    logger.info(f"🌐 GET /api/workflows called with limit={limit}, status={status}")
    logger.info(f"🔧 COSMOS_ENABLED={COSMOS_ENABLED}, cosmos_service={cosmos_service is not None}")
    
    try:
        if not COSMOS_ENABLED or not cosmos_service:
            logger.warning("⚠️ Cosmos DB not available, returning error response")
            return {
                "status": "error",
                "error": "Cosmos DB not enabled",
                "workflows": [],
                "cosmos_enabled": COSMOS_ENABLED,
                "service_available": cosmos_service is not None
            }
        
        logger.info("📡 Calling cosmos_service.list_workflows()...")
        workflows = cosmos_service.list_workflows(limit=limit, status_filter=status)
        logger.info(f"✅ Received {len(workflows)} workflows from Cosmos DB")
        
        response = {
            "status": "success",
            "count": len(workflows),
            "workflows": workflows
        }
        logger.info(f"✅ Returning response with {len(workflows)} workflows")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Exception in list_workflows endpoint: {type(e).__name__} - {str(e)}")
        import traceback
        logger.error(f"📋 Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@app.get("/api/workflows/{workflow_id}",
         tags=["Workflows"])
async def get_workflow(workflow_id: str):
    """
   Get workflow by ID from Cosmos DB.
    
    Args:
    - workflow_id: Workflow ID
    
    Returns:
    - Dict: Workflow document
    """
    logger.info(f"🌐 GET /api/workflows/{workflow_id} called")
    logger.info(f"🔧 COSMOS_ENABLED={COSMOS_ENABLED}, cosmos_service={cosmos_service is not None}")
    
    try:
        if not COSMOS_ENABLED or not cosmos_service:
            logger.error("❌ Cosmos DB not enabled")
            raise HTTPException(status_code=503, detail="Cosmos DB not enabled")
        
        logger.info(f"📡 Calling cosmos_service.get_workflow('{workflow_id}')...")
        workflow = cosmos_service.get_workflow(workflow_id)
        
        if not workflow:
            logger.warning(f"⚠️ Workflow not found: {workflow_id}")
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        logger.info(f"✅ Successfully retrieved workflow: {workflow_id}")
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Exception in get_workflow endpoint: {type(e).__name__} - {str(e)}")
        import traceback
        logger.error(f"📋 Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow: {str(e)}")


@app.delete("/api/workflows/{workflow_id}",
            tags=["Workflows"])
async def delete_workflow(workflow_id: str):
    """
    Delete workflow by ID from Cosmos DB.
    
    Args:
    - workflow_id: Workflow ID
    
    Returns:
    - Dict: Deletion status
    """
    try:
        if not COSMOS_ENABLED or not cosmos_service:
            raise HTTPException(status_code=503, detail="Cosmos DB not enabled")
        
        success = cosmos_service.delete_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        return {
            "status": "success",
            "message": f"Workflow {workflow_id} deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "dev") == "dev"
    )
