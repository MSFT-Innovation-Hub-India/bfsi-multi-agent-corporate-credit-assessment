import traceback
import os
import sys
import logging
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger(__name__)

def financial_orchestrator_pipeline():
    """
    Pipeline for GMR Financial Orchestrator (multi-agent)
    Returns structured output for semantic kernel integration
    """
    try:
        # Direct import since orchestrator.py is now in the same directory
        from orchestrator import main as financial_main
        
        # Import output configuration
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config import get_output_paths
        output_paths = get_output_paths()
        
        # Run the financial orchestrator
        orchestrator_result = financial_main()
        
        # Get dynamic response - check 4 agents status and content
        # Files will be created in frontend output directory
        financial_file = output_paths["comprehensive_analysis"]
        
        # Track 4 specialized agents completion
        agent_statuses = {
            "Agent 1 - Proposal Verification": "❌ Not Found",
            "Agent 2 - Company Profile": "❌ Not Found", 
            "Agent 3 - Financial Analysis": "❌ Not Found",
            "Agent 4 - ANNEXURES Coordination": "❌ Not Found"
        }
        
        if orchestrator_result:
            # Use orchestrator's actual return value
            if orchestrator_result == True:
                agent_statuses = {k: "✅ Completed" for k in agent_statuses.keys()}
        
        # Check individual agent files for detailed responses using new paths
        individual_agent_files = [
            ("Agent 1 - Proposal Verification", output_paths["agent_1_verification"]),
            ("Agent 2 - Company Profile", output_paths["agent_2_profile"]),
            ("Agent 3 - Financial Analysis", output_paths["agent_3_financial"]),
            ("Agent 4 - ANNEXURES Coordination", output_paths["agent_4_annexures"])
        ]
        
        agent_responses = {}
        
        # Read each individual agent file
        for agent_name, agent_file in individual_agent_files:
            if os.path.exists(agent_file):
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        agent_content = f.read()
                        # Get preview of agent response (first 200 chars)
                        agent_preview = agent_content.replace('\n', ' ').strip()[:200]
                        if len(agent_content) > 200:
                            agent_preview += "..."
                        
                        agent_responses[agent_name] = {
                            "status": "✅ Completed",
                            "file_size": len(agent_content),
                            "preview": agent_preview,
                            "file_path": agent_file
                        }
                        agent_statuses[agent_name] = "✅ Completed"
                        
                except Exception as e:
                    agent_responses[agent_name] = {
                        "status": "❌ File Error",
                        "error": str(e),
                        "file_path": agent_file
                    }
                    agent_statuses[agent_name] = "❌ File Error"
            else:
                logger.warning(f"    🏦 [FINANCIAL ORCHESTRATOR] ⚠️ {agent_name} - Output file missing")
                agent_responses[agent_name] = {
                    "status": "❌ Not Found",
                    "file_path": agent_file
                }
                agent_statuses[agent_name] = "❌ Not Found"
        
        # Check main comprehensive file
        main_file_info = ""
        if os.path.exists(financial_file):
            try:
                with open(financial_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_size = len(content)
                    main_file_info = f" | 📄 Complete report ({file_size:,} chars): {financial_file}"
            except Exception as e:
                main_file_info = f" | ⚠️ Main file error: {financial_file}"
        else:
            main_file_info = f" | ⚠️ Main file not found: {financial_file}"
        
        # Create detailed response with all 4 individual agent responses
        response_parts = []
        response_parts.append("🏦 FINANCIAL ORCHESTRATOR - 4 AGENTS RESPONSES:")
        
        for agent_name, agent_info in agent_responses.items():
            if "preview" in agent_info:
                response_parts.append(f"\n📋 {agent_name}: {agent_info['status']} | 📊 PREVIEW ({agent_info['file_size']:,} chars): {agent_info['preview']}")
            else:
                response_parts.append(f"\n📋 {agent_name}: {agent_info['status']}")
        
        response_parts.append(main_file_info)
        response = "".join(response_parts)
        
        status = "AgentStatus.complete"
        error = None
        
    except Exception as e:
        response = None
        status = "AgentStatus.failed"
        error = str(e) + "\n" + traceback.format_exc()
    
    return {
        "agentName": "GMR Financial Orchestrator",
        "agentDescription": "Runs multi-agent financial analysis and generates comprehensive credit report.",
        "response": response,
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "errorMessage": error
    }

if __name__ == "__main__":
    import json
    financial_orchestrator_pipeline()
