
"""GMR Airports Limited Financial Documentation Agent
Azure AI agent for comprehensive financial analysis
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FilePurpose, FileSearchTool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import PROJECT_CONNECTION_STRING, MODEL_DEPLOYMENT, get_output_paths, ensure_frontend_output_dir
from utils.template_loader import get_financial_analysis_sections, get_financial_analysis_instruction

# Financial document files for analysis - All 9 processed documents
FINANCIAL_DOCUMENTS = [
    "processed_data/Financial_ratios_processed.json",
    "processed_data/Standalone_Auditors_report_processed.json", 
    "processed_data/Consolidated_Auditor's_Report_processed.json",
    "processed_data/MDA_processed.json",
    "processed_data/RatingRationale_processed.json", 
    "processed_data/boards_report_processed.json",
    "processed_data/corporate_governance_processed.json",
    "processed_data/GMR_processed.json",
    "processed_data/LoanProposal_processed.json"
]

# Load sections from template files
ANALYSIS_SECTIONS = get_financial_analysis_sections()

def create_financial_documents_agent():
    """Create GMR Financial Documents Agent with file search capabilities"""
    
    try:
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        
        # Upload files and create vector store
        uploaded_files = []
        
        for file_path in FINANCIAL_DOCUMENTS:
            if Path(file_path).exists():
                try:
                    file = project_client.agents.upload_file_and_poll(
                        file_path=file_path, 
                        purpose=FilePurpose.AGENTS
                    )
                    uploaded_files.append(file)
                except Exception as upload_error:
                    continue
        
        if not uploaded_files:
            # Create basic agent without file search
            agent = project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT,
                name="gmr-financial-documents-agent",
                instructions=agent_instruction
            )
            
            # Create a thread
            thread = project_client.agents.create_thread()
            
            return {
                "project_client": project_client,
                "agent": agent,
                "thread": thread,
                "vector_store": None,
                "uploaded_files": []
            }
        
        # Create vector store and file search tool
        vector_store = project_client.agents.create_vector_store_and_poll(
            file_ids=[file.id for file in uploaded_files], 
            name="GMR_Financial_Documents_Vector_Store"
        )
        
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
        agent_instruction = get_financial_analysis_instruction()
        
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-financial-documents-agent",
            instructions=agent_instruction,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources
        )
        
        thread = project_client.agents.create_thread()
        
        return {
            "project_client": project_client,
            "agent": agent,
            "thread": thread,
            "vector_store": vector_store,
            "uploaded_files": [file.id for file in uploaded_files]
        }
        
    except Exception as e:
        return None

def generate_section_analysis(agent_resources, section_key):
    """Generate analysis for a specific section"""
    section = ANALYSIS_SECTIONS[section_key]
    
    try:
        # Create a message in the thread
        message = agent_resources['project_client'].agents.create_message(
            thread_id=agent_resources['thread'].id,
            role="user",
            content=section["prompt"]
        )
        
        # Run the agent
        run = agent_resources['project_client'].agents.create_and_process_run(
            thread_id=agent_resources['thread'].id,
            agent_id=agent_resources['agent'].id
        )
        
        # Get the response messages
        messages = agent_resources['project_client'].agents.list_messages(
            thread_id=agent_resources['thread'].id
        )
        
        # Extract response text from latest assistant message
        analysis_text = ""
        for message in messages.data:
            if message.role == "assistant":
                if hasattr(message, 'text_messages') and message.text_messages:
                    for text_msg in message.text_messages:
                        analysis_text += text_msg.text.value
                elif hasattr(message, 'content') and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, 'text'):
                            analysis_text += content_item.text.value
                break
        
        return analysis_text
        
    except Exception as e:
        return f"Error generating {section['name']}: {str(e)}"

def generate_comprehensive_report():
    """Generate comprehensive credit analysis report"""
    
    agent_resources = create_financial_documents_agent()
    if not agent_resources:
        return False
    
    output_paths = get_output_paths()
    output_filename = output_paths["agent_3_financial"]
    ensure_frontend_output_dir()
    
    # Initialize the file with header
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("# GMR AIRPORTS LIMITED - COMPREHENSIVE CREDIT ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Format: Ambuja Cements Style - Complete Credit Analysis\n")
        f.write("=" * 100 + "\n\n")
    
    
    # Generate all sections sequentially
    total_sections = len(ANALYSIS_SECTIONS)
    
    for i, (section_key, section_info) in enumerate(ANALYSIS_SECTIONS.items(), 1):
        section_analysis = generate_section_analysis(agent_resources, section_key)
        
        # Append section to the main file
        with open(output_filename, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"SECTION {i}: {section_info['name'].upper()}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(section_analysis)
            f.write("\n\n")
        
    
    # Add final footer
    with open(output_filename, 'a', encoding='utf-8') as f:
        f.write(f"\n{'=' * 100}\n")
        f.write("REPORT COMPLETED\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Sections: {total_sections}\n")
        f.write(f"{'=' * 100}\n")
    
    return True

if __name__ == "__main__":
    generate_comprehensive_report()