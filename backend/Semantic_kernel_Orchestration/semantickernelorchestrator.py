import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import AuthorRole
from gmr_plugin import GMRAnalysisPlugin
import logging
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def setup_kernel_logger():
    """Suppress all internal logging for clean output"""
    for name in logging.root.manager.loggerDict:
        if "semantic_kernel" in name or "azure" in name or "openai" in name:
            logging.getLogger(name).setLevel(logging.CRITICAL)
        else:
            logging.getLogger(name).setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.CRITICAL)

setup_kernel_logger()

class GMRSemanticKernelOrchestrator:
    """
    GMR Airports Limited AI Orchestrator using Microsoft Semantic Kernel
    
    Provides intelligent sequential orchestration of:
    1. Sentiment Analysis - News and market sentiment evaluation  
    2. Financial Analysis - 4-agent comprehensive financial review
    3. PDF Generation - Professional report compilation
    
    Features:
    - Pure AI-driven function calling via Azure OpenAI
    - Clean agent calling logs with green indicators
    - Automatic file saving to both orchestration_outputs/ and frontend/
    - Silent completion for professional workflow
    """
    
    def __init__(self):
        """Initialize the orchestrator with Azure OpenAI and GMR plugin"""
        print("🟢 Initializing GMR Semantic Kernel Orchestrator...")
        
        self.kernel = sk.Kernel()
        load_dotenv()
        
        # Load Azure OpenAI configuration
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not all([deployment_name, endpoint, api_key]):
            raise ValueError("Missing Azure OpenAI configuration in .env file")
        
        # Initialize Azure OpenAI service for Semantic Kernel
        self.chat_completion = AzureChatCompletion(
            deployment_name=deployment_name,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.kernel.add_service(self.chat_completion)
        self.kernel.add_plugin(GMRAnalysisPlugin(), plugin_name="GMRAnalysis")
        
        print("✅ Orchestrator ready with Azure OpenAI + Semantic Kernel")

    def save_results_to_files(self, result: dict) -> dict:
        """Save orchestration results to organized output files"""
        try:
            # Import output configuration for frontend saving
            from output_config import get_output_paths, ensure_frontend_output_dir
            output_paths = get_output_paths()
            ensure_frontend_output_dir()
            
            # Save to both legacy and frontend locations
            legacy_output_dir = "orchestration_outputs"
            frontend_output_dir = output_paths["analysis_outputs_dir"]
            
            os.makedirs(legacy_output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save individual agent results to both locations
            files_created = 0
            for key, value in result.items():
                if value and isinstance(value, dict) and key != "orchestration_log":
                    # Legacy location
                    legacy_filename = f"{legacy_output_dir}/gmr_{key}_{timestamp}.txt"
                    # Frontend location  
                    frontend_filename = f"{frontend_output_dir}/gmr_{key}_{timestamp}.txt"
                    
                    content = f"# GMR {key.replace('_', ' ').title()}\n"
                    content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    content += f"Orchestrator: GMR Semantic Kernel\n\n"
                    content += json.dumps(value, indent=2)
                    
                    # Save to both locations
                    with open(legacy_filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    with open(frontend_filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_created += 1
            
            # Save combined results to both locations
            legacy_combined = f"{legacy_output_dir}/gmr_orchestration_complete_{timestamp}.txt"
            frontend_combined = f"{frontend_output_dir}/gmr_orchestration_complete_{timestamp}.txt"
            
            combined_content = "# GMR COMPREHENSIVE ORCHESTRATION RESULTS\n"
            combined_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            combined_content += "Orchestrator: GMR Semantic Kernel\n\n"
            combined_content += json.dumps(result, indent=2)
            
            # Save combined to both locations
            with open(legacy_combined, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            with open(frontend_combined, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            return {
                "legacy_output_directory": legacy_output_dir,
                "frontend_output_directory": frontend_output_dir,
                "files_created": files_created + 1,
                "legacy_combined_file": legacy_combined,
                "frontend_combined_file": frontend_combined
            }
        except Exception as e:
            return {"error": str(e)}

    async def run_smart_gmr_analysis(self, requirements: list = None) -> dict:
        """
        Execute AI-driven sequential GMR analysis
        
        Returns:
            dict: Orchestration results with agent outputs and file save information
        """
        print("🤖 Starting AI-Driven Sequential GMR Analysis...")
        
        # Initialize result structure
        result = {
            "sentiment_analysis": None,
            "financial_orchestrator": None, 
            "pdf_generator": None,
            "orchestration_log": []
        }
        
        # AI orchestration instructions
        system_instruction = """
You are an intelligent GMR Airports Limited analysis orchestrator with full AI decision-making capabilities.

ORCHESTRATION MISSION: Execute ALL 3 functions sequentially in this exact order:
1. gmr_sentiment_analysis() - Analyze GMR market sentiment from news and infrastructure data
2. gmr_financial_orchestrator() - Run comprehensive 4-agent financial analysis  
3. gmr_pdf_generator() - Generate comprehensive PDF reports

ORCHESTRATION INTELLIGENCE RULES:
- Execute functions sequentially, not based on file checks
- Call ALL 3 functions regardless of existing files
- Use logical dependency order: market analysis → financial → PDF

You MUST call ALL 3 functions in sequence. After calling all functions, respond with "GMR Sequential Orchestration Complete."
"""
        
        # Setup conversation
        history = ChatHistory()
        history.add_system_message(system_instruction)
        history.add_user_message("""Execute complete sequential GMR analysis with full orchestration intelligence:

ORCHESTRATION PLAN:
1. Call gmr_sentiment_analysis() - Market sentiment and infrastructure analysis
2. Call gmr_financial_orchestrator() - Multi-agent financial analysis
3. Call gmr_pdf_generator() - Professional report generation

Execute ALL 3 functions in sequence. Show your orchestration intelligence at each step.""")

        # Execute AI orchestration
        execution_settings = OpenAIPromptExecutionSettings(
            max_tokens=4000,
            temperature=0.1,
            function_choice_behavior="auto"
        )
        
        chat_service = self.kernel.get_service(type=AzureChatCompletion)
        await chat_service.get_chat_message_contents(
            chat_history=history,
            settings=execution_settings,
            kernel=self.kernel
        )
        # Process chat history to extract results and show progress  
        for i, message in enumerate(history.messages):
            # Detect AI function calls
            if hasattr(message, 'role') and message.role == AuthorRole.ASSISTANT:
                if hasattr(message, 'items') and message.items:
                    for item in message.items:
                        if hasattr(item, 'function_call') or (hasattr(item, 'metadata') and 'function_call' in str(item.metadata)):
                            # Extract function name
                            function_name = "unknown_function"
                            if hasattr(item, 'function_call') and item.function_call:
                                function_name = getattr(item.function_call, 'name', 'unknown_function')
                            elif hasattr(item, 'metadata'):
                                metadata_str = str(item.metadata)
                                if 'gmr_sentiment_analysis' in metadata_str:
                                    function_name = 'gmr_sentiment_analysis'
                                elif 'gmr_financial_orchestrator' in metadata_str:
                                    function_name = 'gmr_financial_orchestrator'
                                elif 'gmr_pdf_generator' in metadata_str:
                                    function_name = 'gmr_pdf_generator'
                            
                            # Display clean calling logs
                            if 'sentiment' in function_name:
                                print("\033[32m🎯 [SEMANTIC KERNEL ORCHESTRATOR] ➤ CALLING GMR Sentiment Analysis Agent\033[0m")
                            elif 'financial' in function_name:
                                print("\033[32m🎯 [SEMANTIC KERNEL ORCHESTRATOR] ➤ CALLING GMR Financial Orchestrator Agent\033[0m")
                            elif 'pdf' in function_name:
                                print("\033[32m🎯 [SEMANTIC KERNEL ORCHESTRATOR] ➤ CALLING GMR PDF Generator Agent\033[0m")

            # Capture function results
            elif hasattr(message, 'role') and message.role == AuthorRole.TOOL:
                function_result = None
                if hasattr(message, 'content') and message.content:
                    function_result = str(message.content)
                elif hasattr(message, 'items') and message.items:
                    for item in message.items:
                        if hasattr(item, 'text') and item.text:
                            function_result = str(item.text)
                            break
                elif hasattr(message, 'inner_content') and message.inner_content:
                    function_result = str(message.inner_content)
                
                if function_result:
                    try:
                        # Parse JSON result
                        try:
                            parsed_result = json.loads(function_result)
                            agent_name = parsed_result.get("agentName", "Unknown Agent")
                            status = parsed_result.get("status", "Unknown Status")
                        except json.JSONDecodeError:
                            parsed_result = {"summary": function_result, "status": "completed"}
                            agent_name = "Unknown Agent"  
                            status = "completed"
                        
                        # Categorize and log results
                        success_indicator = "✅" if "complete" in str(status).lower() else "⚠️"
                        
                        if "sentiment" in function_result.lower() or i == 3:
                            print(f"🤖 [ORCHESTRATOR STEP 1/3] SENTIMENT ANALYSIS {success_indicator}")
                            print(f"📊 Agent: {agent_name}")
                            print(f"📄 Output Length: {len(str(parsed_result))} characters\n")
                            result["sentiment_analysis"] = parsed_result
                            result["orchestration_log"].append(f"{success_indicator} Step 1: Sentiment Analysis - {status}")
                            
                        elif "financial" in function_result.lower() or i == 5:
                            print(f"🤖 [ORCHESTRATOR STEP 2/3] FINANCIAL ORCHESTRATION {success_indicator}")
                            print(f"🏦 Agent: {agent_name}")
                            print(f"📄 Output Length: {len(str(parsed_result))} characters\n")
                            result["financial_orchestrator"] = parsed_result
                            result["orchestration_log"].append(f"{success_indicator} Step 2: Financial Analysis - {status}")
                            
                        elif "pdf" in function_result.lower() or i == 7:
                            print(f"🤖 [ORCHESTRATOR STEP 3/3] PDF GENERATION {success_indicator}")
                            print(f"📄 Agent: {agent_name}")
                            print(f"📄 Output Length: {len(str(parsed_result))} characters\n")
                            result["pdf_generator"] = parsed_result
                            result["orchestration_log"].append(f"{success_indicator} Step 3: PDF Generation - {status}")
                            
                    except Exception as e:
                        result["orchestration_log"].append(f"❌ Processing Error: {str(e)}")

        # Save results and return
        save_info = self.save_results_to_files(result)
        result["file_save_info"] = save_info
        return result

async def main_example():
    """
    GMR Semantic Kernel Orchestrator - Production Usage
    
    Executes complete AI-driven workflow:
    1. Sentiment Analysis - News and market evaluation
    2. Financial Orchestration - 4-agent comprehensive analysis  
    3. PDF Generation - Professional report compilation
    
    Features:
    - Pure semantic kernel intelligence
    - Clean green calling logs only
    - Silent completion with automatic file saving
    """
    print("🏢 GMR AIRPORTS LIMITED - AI ORCHESTRATION")
    print("=" * 60)
    print("🤖 Pure Semantic Kernel Intelligence")
    print("📊 Sequential: Sentiment → Financial → PDF")
    print("=" * 60)
    
    try:
        print("\n⚙️ Initializing AI Orchestrator...")
        orchestrator = GMRSemanticKernelOrchestrator()
        
        print("\n🚀 Starting AI-driven sequential analysis...")
        print("⏱️ Estimated time: 10-15 minutes")
        
        # Execute pure AI orchestration
        await orchestrator.run_smart_gmr_analysis()
        
        # Completes silently with automatic file saving
            
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main_example())