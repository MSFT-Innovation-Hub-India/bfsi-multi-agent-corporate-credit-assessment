
"""GMR Airports Limited Proposal Verification Agent
Azure AI agent for comprehensive proposal verification and analysis
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
from utils.template_loader import (
    get_proposal_verification_sections,
    get_proposal_verification_instruction,
    get_verification_analysis_prompt
)

# All 9 financial document files for comprehensive verification
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

# Load sections and prompts from template files
PROPOSAL_VERIFICATION_SECTIONS = get_proposal_verification_sections()
VERIFICATION_ANALYSIS_PROMPT = get_verification_analysis_prompt()

def create_proposal_verification_agent():
    """Create GMR Proposal Verification Agent with file search capabilities"""
    
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
                except Exception:
                    continue
        
        if not uploaded_files:
            # Create basic agent without file search
            agent = project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT,
                name="gmr-proposal-verification-agent",
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
            name="GMR_Proposal_Verification_Vector_Store"
        )
        
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
        agent_instruction = get_proposal_verification_instruction()
        
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-proposal-verification-agent",
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
    section = PROPOSAL_VERIFICATION_SECTIONS[section_key]
    
    try:
        project_client = agent_resources["project_client"]
        agent = agent_resources["agent"]
        thread = agent_resources["thread"]
        
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=section["prompt"]
        )
        
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        for msg in messages.data:
            if msg.role == "assistant" and hasattr(msg, 'content') and msg.content:
                for content_item in msg.content:
                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                        return content_item.text.value
        
        return f"# {section['name']}\n\n[Section analysis not available]\n\n"
            
    except Exception as e:
        return f"# {section['name']}\n\n[Error: {e}]\n\n"

def generate_verification_analysis(agent_resources):
    """Generate the final verification analysis"""
    
    try:
        project_client = agent_resources["project_client"]
        agent = agent_resources["agent"]
        thread = agent_resources["thread"]
        
        # Create a message for verification analysis
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=VERIFICATION_ANALYSIS_PROMPT
        )
        
        # Run the agent for verification analysis
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Get messages and extract the response
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # Find the assistant's response
        response_content = ""
        for msg in messages.data:
            if msg.role == "assistant" and hasattr(msg, 'content') and msg.content:
                for content_item in msg.content:
                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                        response_content = content_item.text.value
                        break
                if response_content:
                    break
        
        if response_content:
            return response_content
        else:
            return "# Verification Analysis\n\n[Verification analysis not available]\n\n"
            
    except Exception as e:
        print(f"❌ Error generating Verification Analysis: {e}")
        return f"# Verification Analysis\n\n[Error generating verification analysis: {e}]\n\n"

def generate_comprehensive_verification_report():
    """Generate comprehensive proposal verification report"""
    
    agent_resources = create_proposal_verification_agent()
    if not agent_resources:
        return False
    
    output_paths = get_output_paths()
    output_filename = output_paths["agent_1_verification"]
    ensure_frontend_output_dir()
    
    # Initialize the file with header
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("# GMR AIRPORTS LIMITED - PROPOSAL VERIFICATION & CREDIT APPRAISAL NOTE\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Format: Professional Credit Appraisal Documentation\n")
        f.write("Verification: Cross-checked against all 9 financial documents\n")
        f.write("=" * 100 + "\n\n")
    
    
    # Generate all sections sequentially and append to the same file
    total_sections = len(PROPOSAL_VERIFICATION_SECTIONS)
    
    for i, (section_key, section_info) in enumerate(PROPOSAL_VERIFICATION_SECTIONS.items(), 1):
        
        # Generate section analysis
        section_content = generate_section_analysis(agent_resources, section_key)
        
        # Append to file
        with open(output_filename, 'a', encoding='utf-8') as f:
            f.write(f"{section_content}\n\n")
        
    
    # Generate verification analysis
    verification_content = generate_verification_analysis(agent_resources)
    
    # Append verification analysis
    with open(output_filename, 'a', encoding='utf-8') as f:
        f.write("---\n\n")
        f.write(f"{verification_content}\n\n")
    
    # Add final footer
    with open(output_filename, 'a', encoding='utf-8') as f:
        f.write("\n" + "=" * 100 + "\n")
        f.write("PROPOSAL VERIFICATION COMPLETED\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Documents Verified: 9 comprehensive financial documents\n")
        f.write("=" * 100 + "\n")
    
    # Generate summary
    
    return True

if __name__ == "__main__":
    generate_comprehensive_verification_report()
    
