"""
GMR Airports Limited Market Analyst Agent
Azure AI Agent for GMR infrastructure sentiment analysis
"""

import os
import sys
import time
import json
import datetime
import logging
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool
from azure.ai.projects.models import MessageRole

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import PROJECT_CONNECTION_STRING, MODEL_DEPLOYMENT, get_output_paths, ensure_frontend_output_dir
from orchestrator.news_customfunction import fetch_gmr_infrastructure_news, user_functions
from utils.template_loader import get_market_analyst_instruction, get_market_analyst_message

# Configure logging to suppress Azure SDK verbose logs
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
logging.getLogger('azure').setLevel(logging.WARNING)

def main():
    """GMR Infrastructure Sentiment Analysis using Azure AI Agent"""
    
    # Initialize project client
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=PROJECT_CONNECTION_STRING
    )
    
    # Load templates and create agent tools
    functions = FunctionTool(functions=user_functions)
    agent_instruction = get_market_analyst_instruction()
    user_message_content = get_market_analyst_message()
    
    # Create agent
    agent = project_client.agents.create_agent(
        model=MODEL_DEPLOYMENT,
        name="gmr-sentiment-agent", 
        instructions=agent_instruction,
        tools=functions.definitions,
    )
    
    # Create thread and send message
    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_message_content,
    )
    
    # Create run and poll for completion
    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(3)
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                if tool_call.function.name in ["fetch_gmr_infrastructure_news", "get_gmr_infrastructure_news"]:
                    output = fetch_gmr_infrastructure_news()
                    tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
            
            # Submit tool outputs
            project_client.agents.submit_tool_outputs_to_run(
                thread_id=thread.id, 
                run_id=run.id,
                tool_outputs=tool_outputs
            )
    
    # Fetch analysis results
    response_messages = project_client.agents.list_messages(thread_id=thread.id)
    agent_messages = [msg for msg in response_messages.data if msg.role == MessageRole.AGENT]
    
    if agent_messages:
        latest_response = agent_messages[0]
        analysis_text = ""
        
        for msg in latest_response.text_messages:
            analysis_text += msg.text.value + "\n"
        
        # Save analysis to both locations
        os.makedirs('processed_data', exist_ok=True)
        ensure_frontend_output_dir()
        output_paths = get_output_paths()
        
        # Define output file paths
        analysis_filename_processed = "processed_data/GMR_Sentiment_Analysis.txt"
        analysis_filename_frontend = output_paths["analysis_outputs_dir"] + "/GMR_Sentiment_Analysis.txt"
        
        # Create analysis content
        analysis_content = f"GMR Airports Infrastructure Sentiment Analysis Report\n"
        analysis_content += f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        analysis_content += "=" * 80 + "\n\n"
        analysis_content += analysis_text
        
        # Save to both locations
        for filepath in [analysis_filename_processed, analysis_filename_frontend]:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(analysis_content)
    
    # Cleanup agent
    try:
        project_client.agents.delete_agent(agent.id)
    except Exception:
        pass

def generate_gmr_sentiment_report():
    """Generate GMR sentiment analysis report"""
    main()
    return "GMR sentiment analysis completed. Check the generated report file."

if __name__ == "__main__":
    main()
