"""
Root Configuration Module for GMR Credit Risk Analysis
======================================================
Centralized configuration loader for all Python scripts in the project.
Loads environment variables from root .env file.

Usage:
    from config import (
        PROJECT_CONNECTION_STRING, 
        MODEL_DEPLOYMENT,
        AZURE_OPENAI_ENDPOINT,
        STORAGE_ACCOUNT_NAME,
        DOC_INTEL_ENDPOINT
    )
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# ===================================================================
# Azure AI Project Configuration (Semantic Kernel Orchestration)
# ===================================================================
PROJECT_CONNECTION_STRING = os.getenv('PROJECT_CONNECTION_STRING')
MODEL_DEPLOYMENT = os.getenv('MODEL_DEPLOYMENT', 'gpt-4o-mini')

# ===================================================================
# Azure OpenAI Configuration (for Semantic Kernel)
# ===================================================================
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')

# ===================================================================
# Azure Cognitive Search Configuration
# ===================================================================
SEARCH_SERVICE_KEY = os.getenv('SEARCH_SERVICE_KEY')
SEARCH_SERVICE_ENDPOINT = os.getenv('SEARCH_SERVICE_ENDPOINT')
SEARCH_INDEX_NAME = os.getenv('SEARCH_INDEX_NAME', 'policy')

# ===================================================================
# Azure Blob Storage Configuration
# ===================================================================
STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME')
STORAGE_ACCOUNT_KEY = os.getenv('STORAGE_ACCOUNT_KEY')
BLOB_CONTAINER_NAME = os.getenv('BLOB_CONTAINER_NAME', 'gmrdata')

# ===================================================================
# Azure Document Intelligence Configuration
# ===================================================================
DOC_INTEL_ENDPOINT = os.getenv('DOC_INTEL_ENDPOINT')
DOC_INTEL_KEY = os.getenv('DOC_INTEL_KEY')

# ===================================================================
# OpenAI Embedding Configuration (for Document Processing)
# ===================================================================
OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')
OPENAI_SUBSCRIPTION_KEY = os.getenv('OPENAI_SUBSCRIPTION_KEY')
OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION', '2024-02-01')
OPENAI_DEPLOYMENT_NAME = os.getenv('OPENAI_DEPLOYMENT_NAME', 'text-embedding-3-small')
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small')

# ===================================================================
# Validation Functions
# ===================================================================

def validate_azure_ai_config():
    """Validate Azure AI Project configuration"""
    if not PROJECT_CONNECTION_STRING:
        raise ValueError(
            "PROJECT_CONNECTION_STRING not found in environment variables. "
            "Please ensure it's set in root .env file"
        )
    return True

def validate_openai_config():
    """Validate Azure OpenAI configuration"""
    required_vars = {
        "AZURE_OPENAI_DEPLOYMENT_NAME": AZURE_OPENAI_DEPLOYMENT_NAME,
        "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
        "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY
    }
    missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
    if missing_vars:
        raise ValueError(
            f"Missing required OpenAI environment variables: {', '.join(missing_vars)}\n"
            f"Please ensure all variables are set in root .env file"
        )
    return True

def validate_storage_config():
    """Validate Azure Storage configuration"""
    required_vars = {
        "STORAGE_ACCOUNT_NAME": STORAGE_ACCOUNT_NAME,
        "STORAGE_ACCOUNT_KEY": STORAGE_ACCOUNT_KEY
    }
    missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
    if missing_vars:
        raise ValueError(
            f"Missing required Storage environment variables: {', '.join(missing_vars)}\n"
            f"Please ensure all variables are set in root .env file"
        )
    return True

def validate_doc_intelligence_config():
    """Validate Document Intelligence configuration"""
    required_vars = {
        "DOC_INTEL_ENDPOINT": DOC_INTEL_ENDPOINT,
        "DOC_INTEL_KEY": DOC_INTEL_KEY
    }
    missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
    if missing_vars:
        raise ValueError(
            f"Missing required Document Intelligence environment variables: {', '.join(missing_vars)}\n"
            f"Please ensure all variables are set in root .env file"
        )
    return True

def get_all_config():
    """Get all configuration as a dictionary"""
    return {
        'azure_ai': {
            'connection_string': PROJECT_CONNECTION_STRING,
            'model_deployment': MODEL_DEPLOYMENT
        },
        'azure_openai': {
            'deployment_name': AZURE_OPENAI_DEPLOYMENT_NAME,
            'endpoint': AZURE_OPENAI_ENDPOINT,
            'api_key': AZURE_OPENAI_API_KEY,
            'api_version': AZURE_OPENAI_API_VERSION
        },
        'search': {
            'key': SEARCH_SERVICE_KEY,
            'endpoint': SEARCH_SERVICE_ENDPOINT,
            'index_name': SEARCH_INDEX_NAME
        },
        'storage': {
            'account_name': STORAGE_ACCOUNT_NAME,
            'account_key': STORAGE_ACCOUNT_KEY,
            'container_name': BLOB_CONTAINER_NAME
        },
        'doc_intelligence': {
            'endpoint': DOC_INTEL_ENDPOINT,
            'key': DOC_INTEL_KEY
        },
        'embeddings': {
            'endpoint': OPENAI_ENDPOINT,
            'subscription_key': OPENAI_SUBSCRIPTION_KEY,
            'api_version': OPENAI_API_VERSION,
            'deployment_name': OPENAI_DEPLOYMENT_NAME,
            'model_name': EMBEDDING_MODEL_NAME
        }
    }

# ===================================================================
# Output Path Configuration (for agents and pipelines)
# ===================================================================

# Base directory configuration
BASE_DIR = Path(__file__).parent  # Project root (GMR_credit_risk)

# Frontend output directory where UI can access files
FRONTEND_OUTPUT_DIR = BASE_DIR / "frontend" / "creditreportautomationUI" / "public" / "analysis_outputs"

def ensure_frontend_output_dir():
    """Create frontend output directory if it doesn't exist"""
    FRONTEND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return str(FRONTEND_OUTPUT_DIR)

def get_output_paths():
    """Get all output file paths for agents"""
    ensure_frontend_output_dir()
    
    return {
        "analysis_outputs_dir": str(FRONTEND_OUTPUT_DIR),
        "comprehensive_analysis": str(FRONTEND_OUTPUT_DIR / "GMR_Comprehensive_Credit_Analysis.txt"),
        "comprehensive_html": str(FRONTEND_OUTPUT_DIR / "GMR_Comprehensive_Credit_Analysis.html"),
        "agent_1_verification": str(FRONTEND_OUTPUT_DIR / "agent_1_proposal_verification.txt"),
        "agent_2_profile": str(FRONTEND_OUTPUT_DIR / "agent_2_company_profile.txt"),
        "agent_3_financial": str(FRONTEND_OUTPUT_DIR / "agent_3_financial_analysis.txt"),
        "agent_4_annexures": str(FRONTEND_OUTPUT_DIR / "agent_4_annexures_coordination.txt"),
        "orchestration_complete": str(FRONTEND_OUTPUT_DIR / "gmr_orchestration_complete.txt")
    }

def save_to_both_locations(content, filename_key):
    """Save content to both frontend and backup locations"""
    frontend_paths = get_output_paths()
    
    # Save to frontend location
    frontend_file = frontend_paths[filename_key]
    with open(frontend_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return frontend_file
