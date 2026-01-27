"""
Output Configuration Module for GMR Credit Analysis
Centralizes output path configuration for all agents
"""

import os
from pathlib import Path

# Base directory configuration
BASE_DIR = Path(__file__).parent.parent  # Goes up to GMR directory

# Frontend output directory where UI can access files
FRONTEND_OUTPUT_DIR = BASE_DIR / "frontend" / "creditreportautomationUI" / "public" / "analysis_outputs"

# Ensure frontend output directory exists
def ensure_frontend_output_dir():
    """Create frontend output directory if it doesn't exist"""
    FRONTEND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return str(FRONTEND_OUTPUT_DIR)

# Output file paths for agents
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

# Legacy analysis_outputs directory for backward compatibility
LEGACY_OUTPUT_DIR = Path(__file__).parent / "analysis_outputs"

def get_legacy_paths():
    """Get legacy output paths for backward compatibility"""
    LEGACY_OUTPUT_DIR.mkdir(exist_ok=True)
    
    return {
        "analysis_outputs_dir": str(LEGACY_OUTPUT_DIR),
        "comprehensive_analysis": str(LEGACY_OUTPUT_DIR / "GMR_Comprehensive_Credit_Analysis.txt"),
        "comprehensive_html": str(LEGACY_OUTPUT_DIR / "GMR_Comprehensive_Credit_Analysis.html"),
        "agent_1_verification": str(LEGACY_OUTPUT_DIR / "agent_1_proposal_verification.txt"),
        "agent_2_profile": str(LEGACY_OUTPUT_DIR / "agent_2_company_profile.txt"),
        "agent_3_financial": str(LEGACY_OUTPUT_DIR / "agent_3_financial_analysis.txt"),
        "agent_4_annexures": str(LEGACY_OUTPUT_DIR / "agent_4_annexures_coordination.txt"),
        "orchestration_complete": str(LEGACY_OUTPUT_DIR / "gmr_orchestration_complete.txt")
    }

# Dual output - save to both frontend and legacy locations
def save_to_both_locations(content, filename_key):
    """Save content to both frontend and legacy locations"""
    frontend_paths = get_output_paths()
    legacy_paths = get_legacy_paths()
    
    # Save to frontend location (primary)
    frontend_file = frontend_paths[filename_key]
    with open(frontend_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Save to legacy location (backup)
    legacy_file = legacy_paths[filename_key]
    with open(legacy_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return frontend_file, legacy_file

if __name__ == "__main__":
    # Test the configuration
    paths = get_output_paths()
    print("Frontend Output Paths:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
    
    print(f"\nFrontend directory: {FRONTEND_OUTPUT_DIR}")
    print(f"Directory exists: {FRONTEND_OUTPUT_DIR.exists()}")