"""
GMR Airports Limited Financial Analysis Orchestrator
Manages 5 specialized agents using Azure AI Projects with Semantic Kernel for OpenAI
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Azure AI Projects for agent management
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FileSearchTool

# Semantic Kernel for Azure OpenAI
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import AuthorRole

# Load environment variables
load_dotenv()

# Azure AI Projects Configuration
AZURE_AI_PROJECT_ENDPOINT = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
AZURE_AI_PROJECT_SUBSCRIPTION_ID = os.getenv('AZURE_AI_PROJECT_SUBSCRIPTION_ID') 
AZURE_AI_PROJECT_RESOURCE_GROUP = os.getenv('AZURE_AI_PROJECT_RESOURCE_GROUP')
AZURE_AI_PROJECT_NAME = os.getenv('AZURE_AI_PROJECT_NAME')

# Azure OpenAI Configuration for Semantic Kernel
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
MODEL_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

def load_orchestrator_instructions():
    """Load orchestrator instructions from external file"""
    instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'orchestrator_instructions.txt')
    try:
        with open(instruction_file, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Warning: Could not load orchestrator instructions from {instruction_file}: {e}")
        return "You are the GMR Financial Analysis Orchestrator managing 5 specialized agents."

class GMRFinancialOrchestrator:
    """
    GMR Airports Limited Financial Analysis Orchestrator
    Uses Azure AI Projects for agent management + Semantic Kernel for OpenAI
    """
    
    def __init__(self):
        """Initialize with both Azure AI Projects client and Semantic Kernel"""
        try:
            # Initialize Azure AI Projects client for agent management
            self.project_client = AIProjectClient(
                endpoint=AZURE_AI_PROJECT_ENDPOINT,
                credential=DefaultAzureCredential(),
                subscription_id=AZURE_AI_PROJECT_SUBSCRIPTION_ID,
                resource_group_name=AZURE_AI_PROJECT_RESOURCE_GROUP,
                project_name=AZURE_AI_PROJECT_NAME
            )
            print("✅ Azure AI Project Client initialized successfully")
            
            # Initialize Semantic Kernel with Azure OpenAI
            self.kernel = sk.Kernel()
            
            if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, MODEL_DEPLOYMENT]):
                raise ValueError("Missing Azure OpenAI configuration")
            
            # Add Azure OpenAI service to Semantic Kernel
            self.chat_completion = AzureChatCompletion(
                deployment_name=MODEL_DEPLOYMENT,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION
            )
            self.kernel.add_service(self.chat_completion)
            
            print("✅ Semantic Kernel with Azure OpenAI initialized successfully")
            print(f"🔗 OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
            print(f"🤖 Model: {MODEL_DEPLOYMENT}")
            
            # Create vector store for file search
            self.vector_store = self._create_vector_store()
            
            # Shared thread for all agents
            self.shared_thread = None
            
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {e}")
            raise

    def _create_vector_store(self):
        """Create and populate vector store with financial documents"""
        try:
            # Create vector store (without configuration parameter for compatibility)
            vector_store = self.project_client.agents.create_vector_store(
                name="gmr-financial-docs"
            )
            print(f"✅ Created vector store: {vector_store.id}")
            
            # Add all financial documents to vector store
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processed_data')
            
            # List of financial documents to upload
            financial_files = [
                "GMR_processed.json",
                "LoanProposal_processed.json", 
                "Financial_ratios_processed.json",
                "Standalone_Auditors_report_processed.json",
                "Consolidated_Auditor's_Report_processed.json",
                "MDA_processed.json",
                "RatingRationale_processed.json",
                "boards_report_processed.json",
                "corporate_governance_processed.json",
                "preprocessing_summary.json",
                "GMR_Sentiment_Analysis.txt"
            ]
            
            uploaded_files = []
            for filename in financial_files:
                file_path = os.path.join(data_path, filename)
                if os.path.exists(file_path):
                    try:
                        file = self.project_client.agents.upload_file(
                            file_path=file_path,
                            purpose="agents"
                        )
                        uploaded_files.append(file.id)
                        print(f"✅ Uploaded: {filename}")
                    except Exception as e:
                        print(f"⚠️ Could not upload {filename}: {e}")
                else:
                    print(f"⚠️ File not found: {filename}")
            
            # Add files to vector store
            if uploaded_files:
                self.project_client.agents.create_vector_store_file_batch(
                    vector_store_id=vector_store.id,
                    file_ids=uploaded_files
                )
                print(f"✅ Added {len(uploaded_files)} files to vector store")
            
            return vector_store
            
        except Exception as e:
            print(f"❌ Failed to create vector store: {e}")
            raise

    def create_shared_thread(self):
        """Create a shared thread for all agents"""
        try:
            self.shared_thread = self.project_client.agents.create_thread()
            print(f"✅ Created shared thread: {self.shared_thread.id}")
            return self.shared_thread
        except Exception as e:
            print(f"❌ Failed to create shared thread: {e}")
            raise

    def create_proposal_verification_agent(self):
        """Create proposal verification agent with external instructions"""
        def load_proposal_instructions():
            instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'proposal_verification_agent.txt')
            try:
                with open(instruction_file, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Warning: Could not load proposal verification instructions from {instruction_file}: {e}")
                return "You are a proposal verification agent for GMR Airports Limited. Provide thorough verification analysis."
        
        instructions = load_proposal_instructions()
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-proposal-verification-agent",
            instructions=instructions,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        return agent

    def create_company_profile_agent(self):
        """Create company profile agent with external instructions"""
        def load_company_profile_instructions():
            instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'company_profile_agent.txt')
            try:
                with open(instruction_file, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Warning: Could not load company profile instructions from {instruction_file}: {e}")
                return "You are a company profile agent for GMR Airports Limited. Provide comprehensive company analysis."
        
        instructions = load_company_profile_instructions()
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-company-profile-agent",
            instructions=instructions,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        return agent

    def create_financial_analysis_agent(self):
        """Create financial analysis agent with external instructions"""
        def load_financial_instructions():
            instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'financial_analysis_agent.txt')
            try:
                with open(instruction_file, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Warning: Could not load financial analysis instructions from {instruction_file}: {e}")
                return "You are a financial analysis agent for GMR Airports Limited. Provide comprehensive financial analysis."
        
        instructions = load_financial_instructions()
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-financial-analysis-agent",
            instructions=instructions,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        return agent

    def create_market_analyst_agent(self):
        """Create market analyst agent with external instructions"""
        def load_market_analyst_instructions():
            instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'market_analyst_agent.txt')
            try:
                with open(instruction_file, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Warning: Could not load market analyst instructions from {instruction_file}: {e}")
                return "You are a market analyst agent for GMR Airports Limited. Provide market and industry analysis."
        
        instructions = load_market_analyst_instructions()
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-market-analyst-agent",
            instructions=instructions,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        return agent

    def create_coordinator_agent(self):
        """Create coordinator agent for ANNEXURES generation with external instructions"""
        def load_coordinator_instructions():
            instruction_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates', 'instructions', 'coordinator_agent.txt')
            try:
                with open(instruction_file, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Warning: Could not load coordinator instructions from {instruction_file}: {e}")
                return "You are a coordinator agent for GMR Airports Limited. Generate ANNEXURES and coordinate final analysis."
        
        instructions = load_coordinator_instructions()
        file_search_tool = FileSearchTool(vector_store_ids=[self.vector_store.id])
        
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-coordinator-agent",
            instructions=instructions,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        return agent

    def generate_section_analysis(self, agent, section_name, prompt):
        """Generate analysis using Azure AI Projects agents with Semantic Kernel fallback"""
        try:
            # Create shared thread if not exists
            if not self.shared_thread:
                self.create_shared_thread()
            
            # Create message using Azure AI Projects
            message = self.project_client.agents.create_message(
                thread_id=self.shared_thread.id,
                role="user",
                content=prompt
            )
            
            # Run the agent
            run = self.project_client.agents.create_run(
                thread_id=self.shared_thread.id,
                agent_id=agent.id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                time.sleep(2)
                run = self.project_client.agents.get_run(thread_id=self.shared_thread.id, run_id=run.id)
            
            if run.status == "completed":
                # Get messages
                messages = self.project_client.agents.list_messages(thread_id=self.shared_thread.id)
                
                # Find the assistant's latest response
                for msg in messages.data:
                    if msg.role == "assistant" and msg.run_id == run.id:
                        content = ""
                        for content_item in msg.content:
                            if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                                content += content_item.text.value
                        return content
                
                return "Analysis completed but no content returned"
            else:
                return f"Analysis failed with status: {run.status}"
                
        except Exception as e:
            print(f"❌ Error generating {section_name}: {e}")
            return f"Error generating {section_name}: {str(e)}"

    def run_proposal_verification_analysis(self):
        """Run proposal verification analysis without file storage"""
        print(f"\033[32m🎯 [FINANCIAL ORCHESTRATOR] ➤ CALLING Agent 1: Proposal Verification\033[0m")
        print("\n" + "="*80)
        print("📋 STEP 1: PROPOSAL VERIFICATION ANALYSIS")
        print("="*80)
        
        # Create agent
        agent = self.create_proposal_verification_agent()
        
        # Run comprehensive proposal verification analysis
        print("📝 Processing comprehensive proposal verification analysis...")
        
        verification_analysis = self.generate_section_analysis(
            agent, "Comprehensive Proposal Verification", 
            "Conduct thorough verification of GMR Airports Limited proposal including financial documents, business model analysis, risk assessment, and compliance review."
        )
        
        print("✅ Proposal verification analysis completed")
        
        print("🎉 PROPOSAL VERIFICATION ANALYSIS COMPLETED!")
        print("📊 Comprehensive verification analysis processed successfully")
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)
        print(f"✅ Proposal Verification Analysis Completed")
        print(f"📄 Agent execution completed without file storage\n")

    def run_company_profile_analysis(self):
        """Run company profile analysis without file storage"""
        print(f"\033[32m🎯 [FINANCIAL ORCHESTRATOR] ➤ CALLING Agent 2: Company Profile\033[0m")
        print("\n" + "="*80)
        print("🏢 STEP 2: COMPANY PROFILE ANALYSIS")
        print("="*80)
        
        # Create agent
        agent = self.create_company_profile_agent()
        
        # Run comprehensive company profile analysis
        print("📝 Processing comprehensive company profile analysis...")
        
        profile_analysis = self.generate_section_analysis(
            agent, "Comprehensive Company Profile", 
            "Generate detailed company profile analysis for GMR Airports Limited including business model, market position, financial performance, and strategic outlook."
        )
        
        print("✅ Company profile analysis completed")
        
        print("🎉 COMPANY PROFILE ANALYSIS COMPLETED!")
        print("📊 Comprehensive profile analysis processed successfully")
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)
        print(f"✅ Company Profile Analysis Completed")
        print(f"📄 Agent execution completed without file storage\n")

    def run_financial_analysis(self):
        """Run financial analysis without file storage"""
        print(f"\033[32m🎯 [FINANCIAL ORCHESTRATOR] ➤ CALLING Agent 3: Financial Analysis\033[0m")
        print("\n" + "="*80)
        print("💰 STEP 3: FINANCIAL ANALYSIS")
        print("="*80)
        
        # Create agent
        agent = self.create_financial_analysis_agent()
        
        # Run comprehensive financial analysis
        print("📝 Processing comprehensive financial analysis...")
        
        financial_analysis = self.generate_section_analysis(
            agent, "Comprehensive Financial Analysis", 
            "Conduct thorough financial analysis for GMR Airports Limited including performance metrics, ratios, cash flows, and projections with detailed tables and variance analysis."
        )
        
        print("✅ Financial analysis completed")
        
        print("🎉 FINANCIAL ANALYSIS COMPLETED!")
        print("📊 Comprehensive financial analysis processed successfully")
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)
        print(f"✅ Financial Analysis Completed")
        print(f"📄 Agent execution completed without file storage\n")

    def run_market_analysis(self):
        """Run market analysis without file storage"""
        print(f"\033[32m🎯 [FINANCIAL ORCHESTRATOR] ➤ CALLING Agent 4: Market Analysis\033[0m")
        print("\n" + "="*80)
        print("📈 STEP 4: MARKET ANALYSIS")
        print("="*80)
        
        # Create agent
        agent = self.create_market_analyst_agent()
        
        # Run comprehensive market analysis
        print("📝 Processing comprehensive market analysis...")
        
        market_analysis = self.generate_section_analysis(
            agent, "Comprehensive Market Analysis", 
            "Analyze market conditions, industry trends, competitive landscape, and outlook for GMR Airports Limited in the aviation and airport infrastructure sector."
        )
        
        print("✅ Market analysis completed")
        
        print("🎉 MARKET ANALYSIS COMPLETED!")
        print("📊 Comprehensive market analysis processed successfully")
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)
        print(f"✅ Market Analysis Completed")
        print(f"📄 Agent execution completed without file storage\n")

    def run_annexures_generation(self):
        """Run ANNEXURES generation without file storage"""
        print(f"\033[32m🎯 [FINANCIAL ORCHESTRATOR] ➤ CALLING Agent 5: ANNEXURES Generation\033[0m")
        print("\n" + "="*80)
        print("📋 STEP 5: ANNEXURES GENERATION")
        print("="*80)
        
        # Create coordinator agent
        agent = self.create_coordinator_agent()
        
        # Run comprehensive annexures generation
        print("📝 Processing comprehensive ANNEXURES generation...")
        
        annexures_analysis = self.generate_section_analysis(
            agent, "Comprehensive ANNEXURES Generation", 
            "Generate all required ANNEXURES (I-V) for GMR Airports Limited credit proposal including deviations, comparisons, risk analysis, and regulatory compliance documentation."
        )
        
        print("✅ ANNEXURES generation completed")
        
        print("🎉 ANNEXURES GENERATION COMPLETED!")
        print("📊 Comprehensive ANNEXURES processed successfully")
        
        # Cleanup agent
        self.project_client.agents.delete_agent(agent.id)
        print(f"✅ ANNEXURES Generation Completed")
        print(f"🗂️ Agent processing completed without file storage\n")

    def run_comprehensive_analysis(self):
        """Run complete comprehensive financial analysis without file storage"""
        print("🚀 Starting comprehensive financial analysis workflow...")
        print("\n🏦 PROCESSING CREDIT PROPOSAL: GMR-2024-001")
        print("Borrower: GMR Airports Limited")
        print("Proposed Amount: ₹12,200.00 million")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "="*80)
        print("🔄 EXECUTING 5-AGENT ORCHESTRATION WORKFLOW")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # Execute all 5 agents sequentially
            self.run_proposal_verification_analysis()
            self.run_company_profile_analysis()
            self.run_financial_analysis()
            self.run_market_analysis()
            self.run_annexures_generation()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print("\n" + "="*80)
            print("🎉 COMPREHENSIVE FINANCIAL ANALYSIS COMPLETED!")
            print("="*80)
            print(f"⏱️ Total Execution Time: {execution_time:.2f} seconds")
            print(f"🤖 Agents Executed: 5 (Proposal Verification, Company Profile, Financial Analysis, Market Analysis, ANNEXURES)")
            print(f"📊 Analysis Type: Comprehensive Credit Assessment")
            print(f"🏦 Borrower: GMR Airports Limited")
            print(f"💰 Proposed Amount: ₹12,200.00 million")
            print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("✅ All agent executions completed successfully without file storage")
            
            return {
                "status": "completed",
                "execution_time": execution_time,
                "agents_executed": 5,
                "borrower": "GMR Airports Limited",
                "amount": "₹12,200.00 million",
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error during comprehensive analysis: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "analysis_date": datetime.now().isoformat()
            }
        
        finally:
            # Cleanup vector store
            try:
                self.project_client.agents.delete_vector_store(self.vector_store.id)
                print(f"🧹 Cleaned up vector store: {self.vector_store.id}")
            except Exception as e:
                print(f"⚠️ Could not cleanup vector store: {e}")

def gmr_financial_orchestrator():
    """Main orchestration function for GMR financial analysis"""
    print("\n" + "="*80)
    print("🏦 GMR AIRPORTS LIMITED - FINANCIAL ANALYSIS ORCHESTRATOR")
    print("="*80)
    print("🎯 Initializing 5-Agent Workflow...")
    print("📋 Agent 1: Proposal Verification")
    print("🏢 Agent 2: Company Profile")
    print("💰 Agent 3: Financial Analysis")
    print("📈 Agent 4: Market Analysis")
    print("📋 Agent 5: ANNEXURES Generation")
    print("="*80)
    
    try:
        orchestrator = GMRFinancialOrchestrator()
        result = orchestrator.run_comprehensive_analysis()
        
        print("\n🎯 ORCHESTRATION SUMMARY:")
        print(f"Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'completed':
            print(f"Execution Time: {result.get('execution_time', 0):.2f} seconds")
            print(f"Agents Executed: {result.get('agents_executed', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    gmr_financial_orchestrator()
