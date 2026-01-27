import traceback
import os
import sys
from datetime import datetime, timezone

# Add the parent directory to the path so we can import from Azure_AI_Agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sentiment_agent_pipeline():
    """
    Pipeline for GMR Market Analyst Agent (formerly Sentiment Analysis)
    Returns structured output for semantic kernel integration
    """
    try:
        from Semantic_kernel_Orchestration.market_analyst_agent import generate_gmr_sentiment_report
        
        # Run the sentiment analysis agent
        agent_result = generate_gmr_sentiment_report()
        
        # Get the actual agent response directly (dynamic)
        sentiment_file = "processed_data/GMR_Sentiment_Analysis.txt"
        
        # Use the agent's actual result or read the generated content
        if agent_result and agent_result != "GMR sentiment analysis completed. Check the generated report file.":
            # Agent returned actual analysis content
            response = f"📊 AGENT RESPONSE: {agent_result} | 📄 Full report saved to: {sentiment_file}"
        elif os.path.exists(sentiment_file):
            # Read the actual generated analysis content
            try:
                with open(sentiment_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Return first 500 characters as overview + file reference
                content_preview = content.replace('\n', ' ').strip()[:500]
                if len(content) > 500:
                    content_preview += "..."
                
                response = f"📊 MARKET ANALYSIS COMPLETED: {content_preview} | 📄 Complete analysis available in: {sentiment_file}"
                
            except Exception as e:
                response = f"📊 MARKET ANALYSIS COMPLETED | 📄 Full report available in: {sentiment_file} | ⚠️ Could not read preview: {str(e)}"
        else:
            response = f"📊 MARKET ANALYSIS EXECUTED | ⚠️ Report file not found at: {sentiment_file}"
        
        status = "AgentStatus.complete"
        error = None
        
    except Exception as e:
        response = None
        status = "AgentStatus.failed"
        error = str(e) + "\n" + traceback.format_exc()
    
    return {
        "agentName": "GMR Market Analyst Agent",
        "agentDescription": "Analyzes GMR Airports market sentiment and generates detailed market analysis report.",
        "response": response,
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "errorMessage": error
    }

if __name__ == "__main__":
    import json
    print(json.dumps(sentiment_agent_pipeline(), indent=2))
