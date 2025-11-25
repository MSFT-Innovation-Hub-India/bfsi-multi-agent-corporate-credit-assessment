# === GMR AIRPORTS LIMITED - COMPREHENSIVE FINANCIAL ANALYSIS ORCHESTRATOR ===
"""
Multi-Agent Financial Analysis Orchestrator for GMR Airports Limited
Features:
- Shared thread approach for 4 specialized agents
- Exact same templates and instructions from individual agents
- Single comprehensive report file with all analyses
- Real-time terminal output with detailed section-by-section analysis
- Ambuja Cements style format throughout
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Suppress Azure SDK logging to remove RunStatus messages
logging.getLogger("azure").setLevel(logging.CRITICAL)
logging.getLogger("azure.ai").setLevel(logging.CRITICAL)
logging.getLogger("azure.ai.projects").setLevel(logging.CRITICAL)
logging.getLogger("azure.identity").setLevel(logging.CRITICAL)

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FilePurpose

# Add parent directory to path for imports
import sys
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import configuration from centralized config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import PROJECT_CONNECTION_STRING, MODEL_DEPLOYMENT

# Get project root for file paths
PROJECT_ROOT = project_root.parent  # Go up from Semantic_kernel_Orchestration to project root

# Financial document files for all agents (relative to project root)
FINANCIAL_DOCUMENTS = [
    PROJECT_ROOT / "processed_data" / "Financial_ratios_processed.json",
    PROJECT_ROOT / "processed_data" / "Standalone_Auditors_report_processed.json",
    PROJECT_ROOT / "processed_data" / "Consolidated_Auditor's_Report_processed.json",
    PROJECT_ROOT / "processed_data" / "MDA_processed.json",
    PROJECT_ROOT / "processed_data" / "RatingRationale_processed.json",
    PROJECT_ROOT / "processed_data" / "boards_report_processed.json",
    PROJECT_ROOT / "processed_data" / "corporate_governance_processed.json",
    PROJECT_ROOT / "processed_data" / "GMR_processed.json",
    PROJECT_ROOT / "processed_data" / "LoanProposal_processed.json",
    PROJECT_ROOT / "processed_data" / "GMR_Sentiment_Analysis.txt"
]

# Import templates from utils.template_loader
from utils.template_loader import (
    get_proposal_verification_sections,
    get_proposal_verification_instruction,
    get_company_profile_sections,
    get_company_profile_instruction,
    get_financial_analysis_sections,
    get_financial_analysis_instruction,
    get_coordinator_instruction,
    get_annexures_sections,
    get_verification_analysis_prompt
)

# Load all templates from files
PROPOSAL_VERIFICATION_SECTIONS = get_proposal_verification_sections()
VERIFICATION_ANALYSIS_PROMPT = get_verification_analysis_prompt()
COMPANY_PROFILE_SECTIONS = get_company_profile_sections()
ANALYSIS_SECTIONS = get_financial_analysis_sections()
ANNEXURES_SECTIONS = get_annexures_sections()

# Load agent instructions
PROPOSAL_VERIFICATION_INSTRUCTION = get_proposal_verification_instruction()
COMPANY_PROFILE_INSTRUCTION = get_company_profile_instruction()
FINANCIAL_ANALYSIS_INSTRUCTION = get_financial_analysis_instruction()
COORDINATOR_INSTRUCTION = get_coordinator_instruction()

# ANNEXURES_SECTIONS loaded from template files above

class GMRFinancialOrchestrator:
    """
    GMR Airports Limited Financial Analysis Orchestrator
    Manages 4 specialized agents using shared thread approach
    """
    
    def __init__(self):
        """Initialize the orchestrator with Azure AI project client"""
        
        try:
            # Import output configuration
            from config import get_output_paths, ensure_frontend_output_dir
            
            credential = DefaultAzureCredential()
            self.project_client = AIProjectClient.from_connection_string(
                credential=credential,
                conn_str=PROJECT_CONNECTION_STRING
            )
            
            # Setup output paths using configuration
            self.output_paths = get_output_paths()
            self.output_file = self.output_paths["comprehensive_analysis"]
            
            # Ensure frontend output directory exists
            ensure_frontend_output_dir()
            
            self.vector_store = None
            self.shared_thread = None
            
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {str(e)}")
            raise

    def setup_vector_store(self):
        """Setup vector store with all financial documents"""
        
        try:
            # Upload all financial documents
            uploaded_files = []
            
            for doc_path in FINANCIAL_DOCUMENTS:
                if Path(doc_path).exists():
                    with open(doc_path, 'rb') as file:
                        uploaded_file = self.project_client.agents.upload_file_and_poll(
                            file=file, 
                            purpose=FilePurpose.AGENTS
                        )
                        uploaded_files.append(uploaded_file)
            
            # Create vector store with uploaded files
            self.vector_store = self.project_client.agents.create_vector_store_and_poll(
                file_ids=[file.id for file in uploaded_files],
                name="GMR_Financial_Documents"
            )
            
        except Exception as e:
            print(f"❌ Error setting up vector store: {str(e)}")
            raise

    def create_shared_thread(self):
        """Create shared thread for all agents"""
        
        try:
            self.shared_thread = self.project_client.agents.create_thread()
            
        except Exception as e:
            print(f"❌ Error creating shared thread: {str(e)}")
            raise

    def create_proposal_verification_agent(self):
        """Create proposal verification agent with comprehensive instructions loaded from template file"""
        from azure.ai.projects.models import FileSearchTool
        
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-proposal-verification-agent",
            instructions=PROPOSAL_VERIFICATION_INSTRUCTION,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        
        return agent

    def create_company_profile_agent(self):
        """Create company profile agent with comprehensive instructions loaded from template file"""
        from azure.ai.projects.models import FileSearchTool
        
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-company-profile-agent",
            instructions=COMPANY_PROFILE_INSTRUCTION,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        
        return agent

    def create_financial_analysis_agent(self):
        """Create financial analysis agent with comprehensive instructions loaded from template file"""
        from azure.ai.projects.models import FileSearchTool
        
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-financial-documents-agent",
            instructions=FINANCIAL_ANALYSIS_INSTRUCTION,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        
        return agent

    def create_coordinator_agent(self):
        """Create coordinator agent for ANNEXURES generation with comprehensive instructions loaded from template file"""
        from azure.ai.projects.models import FileSearchTool
        
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-coordination-specialist",
            instructions=COORDINATOR_INSTRUCTION,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        
        return agent

    def generate_section_analysis(self, agent, section_name, section_prompt):
        """Generate analysis for a specific section using shared thread with rate limiting and retry logic"""

        
        max_retries = 3
        retry_delay = 10  # Start with 10 seconds delay (reduced from 60)
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:

                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
                # Create message in shared thread
                message = self.project_client.agents.create_message(
                    thread_id=self.shared_thread.id,
                    role="user",
                    content=section_prompt
                )
                
                # Add small delay before running to avoid rate limits
                time.sleep(1)  # Reduced from 5 seconds to 1 second
                
                # Run analysis with proper waiting
                run = self.project_client.agents.create_and_process_run(
                    thread_id=self.shared_thread.id,
                    agent_id=agent.id
                )
                
                if run.status == "completed":
                    # Get response messages using the proper method from individual agents
                    messages = self.project_client.agents.list_messages(thread_id=self.shared_thread.id)
                    
                    # Extract the response text (get the latest assistant message)
                    section_result = ""
                    for message in messages.data:
                        if message.role == "assistant":
                            # Handle different message content formats from Azure AI (same as individual agents)
                            if hasattr(message, 'content') and message.content:
                                # Handle simple content format
                                for content_item in message.content:
                                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                                        section_result = content_item.text.value
                                        break
                                    elif hasattr(content_item, 'value'):
                                        section_result = str(content_item.value)
                                    else:
                                        section_result = str(content_item)
                            else:
                                # Fallback for other formats
                                section_result = str(message)
                            break  # Get only the latest response
                    
                    if section_result:
                        # Add delay after successful processing to avoid rate limits
                        time.sleep(1)  # Reduced from 3 seconds to 1 second
                        
                        return section_result
                    else:
                        return f"No response content generated for {section_name}"
                        
                elif run.status == "failed":
                    print(f"❌ Run failed for {section_name} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        continue  # Retry
                    else:
                        return f"Failed to generate analysis for {section_name} after {max_retries} attempts - Status: {run.status}"
                else:
                    print(f"❌ Unexpected run status for {section_name}: {run.status}")
                    if attempt < max_retries - 1:
                        continue  # Retry
                    else:
                        return f"Failed to generate analysis for {section_name} - Status: {run.status}"
                        
            except Exception as e:
                print(f"❌ Error processing {section_name} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if "rate limit" in str(e).lower() or "throttle" in str(e).lower():
                    if attempt < max_retries - 1:
                        continue  # Retry for rate limit errors
                
                if attempt == max_retries - 1:
                    import traceback
                    traceback.print_exc()
                    return f"Error generating {section_name} after {max_retries} attempts: {str(e)}"
        
        return f"Failed to generate {section_name} after all retry attempts"

    def run_proposal_verification_analysis(self):
        """Run complete proposal verification analysis"""
        
        # Create agent
        agent = self.create_proposal_verification_agent()
        
        # Initialize individual agent file using output configuration
        agent_file = self.output_paths["agent_1_verification"]
        os.makedirs(os.path.dirname(agent_file), exist_ok=True)
        
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write("# GMR AIRPORTS LIMITED - PROPOSAL VERIFICATION AGENT RESPONSE\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Agent: Proposal Verification Agent\n\n")
        
        # Initialize comprehensive file section
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("## GMR AIRPORTS LIMITED - PROPOSAL VERIFICATION\n\n")
        
        # Collect all content for individual file
        agent_content = ""
        
        # Process each verification section with rate limiting
        section_count = len(PROPOSAL_VERIFICATION_SECTIONS)
        for i, (section_key, section_info) in enumerate(PROPOSAL_VERIFICATION_SECTIONS.items(), 1):
            section_analysis = self.generate_section_analysis(
                agent, section_info['name'], section_info['prompt']
            )
            
            # Append to both files
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(section_analysis)
                f.write("\n\n")
            
            agent_content += section_analysis + "\n\n"
            
            # Add delay between sections to avoid rate limits (except for last section)
            if i < section_count:
                time.sleep(3)
        
        # Generate verification analysis
        verification_analysis = self.generate_section_analysis(
            agent, "Overall Verification Analysis", VERIFICATION_ANALYSIS_PROMPT
        )
        
        # Append verification analysis to both files
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(verification_analysis)
            f.write("\n\n")
        
        agent_content += verification_analysis + "\n\n"
        
        # Save complete agent response to individual file
        with open(agent_file, 'a', encoding='utf-8') as f:
            f.write(agent_content)
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)

    def run_company_profile_analysis(self):
        """Run complete company profile analysis"""
        
        # Create agent
        agent = self.create_company_profile_agent()
        
        # Initialize individual agent file using output configuration
        agent_file = self.output_paths["agent_2_profile"]
        os.makedirs(os.path.dirname(agent_file), exist_ok=True)
        
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write("# GMR AIRPORTS LIMITED - COMPANY PROFILE AGENT RESPONSE\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Agent: Company Profile Agent\n\n")
        
        # Initialize comprehensive file section
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("## GMR AIRPORTS LIMITED - COMPANY PROFILE\n\n")
        
        # Collect all content for individual file
        agent_content = ""
        
        # Process each company profile section with rate limiting
        section_count = len(COMPANY_PROFILE_SECTIONS)
        for i, (section_key, section_info) in enumerate(COMPANY_PROFILE_SECTIONS.items(), 1):
            section_analysis = self.generate_section_analysis(
                agent, section_info['name'], section_info['prompt']
            )
            
            # Append to both files
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(section_analysis)
                f.write("\n\n")
            
            agent_content += section_analysis + "\n\n"
            
            # Add delay between sections to avoid rate limits (except for last section)
            if i < section_count:
                time.sleep(3)
        
        # Save complete agent response to individual file
        with open(agent_file, 'a', encoding='utf-8') as f:
            f.write(agent_content)
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)

    def run_financial_analysis(self):
        """Run complete financial analysis"""
        
        # Create agent
        agent = self.create_financial_analysis_agent()
        
        # Initialize individual agent file using output configuration
        agent_file = self.output_paths["agent_3_financial"]
        os.makedirs(os.path.dirname(agent_file), exist_ok=True)
        
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write("# GMR AIRPORTS LIMITED - FINANCIAL ANALYSIS AGENT RESPONSE\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Agent: Financial Analysis Agent\n\n")
        
        # Initialize comprehensive file section
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("## GMR AIRPORTS LIMITED - FINANCIAL ANALYSIS\n\n")
        
        # Collect all content for individual file
        agent_content = ""
        
        # Process each financial analysis section with rate limiting
        section_count = len(ANALYSIS_SECTIONS)
        for i, (section_key, section_info) in enumerate(ANALYSIS_SECTIONS.items(), 1):
            
            section_analysis = self.generate_section_analysis(
                agent, section_info['name'], section_info['prompt']
            )
            
            # Append to both files
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(section_analysis)
                f.write("\n\n")
            
            agent_content += section_analysis + "\n\n"
            
            # Add delay between sections to avoid rate limits (except for last section)
            if i < section_count:
                time.sleep(3)
        
        # Save complete agent response to individual file
        with open(agent_file, 'a', encoding='utf-8') as f:
            f.write(agent_content)
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)

    def run_annexures_generation(self):
        """Run ANNEXURES generation using coordinator agent"""
        
        # Create coordinator agent
        agent = self.create_coordinator_agent()
        
        # Initialize individual agent file using output configuration
        agent_file = self.output_paths["agent_4_annexures"]
        os.makedirs(os.path.dirname(agent_file), exist_ok=True)
        
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write("# GMR AIRPORTS LIMITED - ANNEXURES COORDINATION AGENT RESPONSE\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Agent: ANNEXURES Coordination Agent\n\n")
        
        # Initialize comprehensive file section
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("## ANNEXURES\n\n")
        
        # Collect all content for individual file
        agent_content = ""
        
        # Process each ANNEXURE with rate limiting
        section_count = len(ANNEXURES_SECTIONS)
        for i, (section_key, section_info) in enumerate(ANNEXURES_SECTIONS.items(), 1):
            section_analysis = self.generate_section_analysis(
                agent, section_info['name'], section_info['prompt']
            )
            
            # Append to both files
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"### {section_info['name'].upper()}\n")
                f.write(section_analysis)
                f.write("\n\n")
            
            agent_content += f"### {section_info['name'].upper()}\n"
            agent_content += section_analysis + "\n\n"
            
            # Add delay between sections to avoid rate limits (except for last section)
            if i < section_count:
                time.sleep(3)
        
        # Save complete agent response to individual file
        with open(agent_file, 'a', encoding='utf-8') as f:
            f.write(agent_content)
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)

    def cleanup_resources(self):
        """Clean up Azure resources"""
        try:
            if self.vector_store:
                self.project_client.agents.delete_vector_store(self.vector_store.id)
        except Exception as e:
            print(f"❌ Error cleaning up resources: {str(e)}")

    def run_comprehensive_analysis(self):
        """Run complete comprehensive financial analysis"""
        start_time = datetime.now()
        
        try:
            # Initialize comprehensive output file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# GMR AIRPORTS LIMITED - COMPREHENSIVE CREDIT ASSESSMENT REPORT\n")
                f.write(f"Generated: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Proposal ID: GMR-2024-001\n")
                f.write("Borrower: GMR Airports Limited\n\n")
            
            # Setup infrastructure
            self.setup_vector_store()
            self.create_shared_thread()
            
            # Run all 4 analysis steps with rate limiting between major steps
            self.run_proposal_verification_analysis()
            time.sleep(10)  # Reduced from 30 seconds to 10 seconds
            
            self.run_company_profile_analysis() 
            time.sleep(10)  # Reduced from 30 seconds to 10 seconds
            
            self.run_financial_analysis()
            time.sleep(10)  # Reduced from 30 seconds to 10 seconds
            
            self.run_annexures_generation()
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {str(e)}")
            raise
        finally:
            self.cleanup_resources()

def main():
    """Main execution function"""
    try:
        orchestrator = GMRFinancialOrchestrator()
        orchestrator.run_comprehensive_analysis()
        
    except Exception as e:
        print(f"❌ Orchestrator failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
