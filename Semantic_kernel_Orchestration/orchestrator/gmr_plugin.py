"""
GMR Analysis Plugin for Semantic Kernel
========================================

This plugin provides 4 kernel functions for GMR Airports Limited analysis:

1. gmr_sentiment_analysis() - Market sentiment analysis
2. gmr_financial_orchestrator() - 4-agent financial analysis  
3. gmr_pdf_generator() - PDF report generation
4. gmr_analysis_status() - File status checking

Usage:
    from gmr_plugin import GMRAnalysisPlugin
    plugin = GMRAnalysisPlugin()
    
    # These functions are automatically registered as semantic kernel functions
    # Use with GMRSemanticKernelOrchestrator for AI-driven orchestration

Note: This plugin should be used with gmr_semantic_orchestrator.py for 
      complete AI-driven workflow orchestration.
"""

from semantic_kernel.functions import kernel_function
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline modules from same orchestrator directory
from market_analyst_pipeline import sentiment_agent_pipeline
from financial_orchestrator_pipeline import financial_orchestrator_pipeline
from pdf_generator_pipeline import pdf_generator_pipeline
import logging
import json

# Set up logging with enhanced orchestration visibility
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class GMRAnalysisPlugin:
    """
    GMR Airports Limited - Comprehensive Analysis Plugin
    Provides sentiment analysis, financial orchestration, and PDF generation capabilities
    """
    
    @kernel_function(
        description="Analyzes GMR market sentiment from news and infrastructure data, generates comprehensive sentiment report",
        name="gmr_sentiment_analysis"
    )
    def gmr_sentiment_analysis(self) -> str:
        """Runs GMR market analyst pipeline (formerly sentiment analysis) and returns JSON result."""
        try:
            result = sentiment_agent_pipeline()
            
            if result.get("status") != "AgentStatus.complete":
                error_msg = f"Market analyst agent failed: {result.get('errorMessage')}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({"error": str(e)})

    @kernel_function(
        description="Runs multi-agent financial analysis orchestrator (4 agents: Proposal Verification, Company Profile, Financial Analysis, ANNEXURES)",
        name="gmr_financial_orchestrator"
    )
    def gmr_financial_orchestrator(self) -> str:
        """Performs comprehensive financial analysis using 4 specialized agents and returns JSON result."""
        try:
            result = financial_orchestrator_pipeline()
            
            if result.get("status") != "AgentStatus.complete":
                error_msg = f"Financial orchestrator failed: {result.get('errorMessage')}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(result)
            
        except Exception as e:
            return json.dumps({"error": str(e)})

    @kernel_function(
        description="Generates PDF reports from comprehensive credit analysis text files",
        name="gmr_pdf_generator"
    )
    def gmr_pdf_generator(self) -> str:
        """Generates PDF reports from analysis files and returns JSON result."""
        try:
            result = pdf_generator_pipeline()
            
            if result.get("status") != "AgentStatus.complete":
                error_msg = f"PDF generator failed: {result.get('errorMessage')}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error in gmr_pdf_generator: {str(e)}")
            return json.dumps({"error": str(e)})

    @kernel_function(
        description="Gets status and file information for all GMR analysis outputs",
        name="gmr_analysis_status"
    )
    def gmr_analysis_status(self) -> str:
        """Returns status of all GMR analysis files and outputs."""
        try:
            import os
            from datetime import datetime
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from config import get_output_paths
            
            # Get current output paths configuration
            output_paths = get_output_paths()
            
            files_to_check = {
                "sentiment_analysis": "processed_data/GMR_Sentiment_Analysis.txt",
                "comprehensive_analysis": output_paths["comprehensive_analysis"],
                "comprehensive_html": output_paths["comprehensive_html"],
                "agent_1_verification": output_paths["agent_1_verification"],
                "agent_2_profile": output_paths["agent_2_profile"], 
                "agent_3_financial": output_paths["agent_3_financial"],
                "agent_4_annexures": output_paths["agent_4_annexures"]
            }
            
            status_info = {}
            
            for file_type, file_path in files_to_check.items():
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    status_info[file_type] = {
                        "status": "✅ Available",
                        "file_path": file_path,
                        "file_size": file_size,
                        "last_modified": file_modified.isoformat(),
                        "size_readable": f"{file_size:,} bytes"
                    }
                else:
                    status_info[file_type] = {
                        "status": "❌ Not Found",
                        "file_path": file_path
                    }
            
            result = {
                "agentName": "GMR Analysis Status Checker",
                "agentDescription": "Checks status of all GMR analysis files and outputs",
                "files_status": status_info,
                "completedAt": datetime.now().isoformat(),
                "total_files_found": sum(1 for info in status_info.values() if info["status"] == "✅ Available"),
                "total_files_expected": len(files_to_check)
            }
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error in gmr_analysis_status: {str(e)}")
            return json.dumps({"error": str(e)})