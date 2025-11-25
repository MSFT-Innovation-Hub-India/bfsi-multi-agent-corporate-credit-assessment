
"""GMR Airports Limited HTML/PDF Generator Agent
Converts text analysis reports to HTML and PDF format
"""

import os
import sys
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FilePurpose, CodeInterpreterTool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import PROJECT_CONNECTION_STRING, MODEL_DEPLOYMENT, get_output_paths, ensure_frontend_output_dir
from utils.template_loader import get_pdf_generator_instruction

def convert_txt_to_html():
    """Convert text analysis to HTML and PDF format"""
    
    output_paths = get_output_paths()
    ensure_frontend_output_dir()
    
    txt_file_path = output_paths["comprehensive_analysis"]
    if not Path(txt_file_path).exists():
        return
    
    try:
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        
        uploaded_file = project_client.agents.upload_file_and_poll(
            file_path=txt_file_path,
            purpose=FilePurpose.AGENTS
        )
        
        code_interpreter_tool = CodeInterpreterTool(file_ids=[uploaded_file.id])
        
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-html-generator",
            instructions=get_pdf_generator_instruction(),
            tools=code_interpreter_tool.definitions,
            tool_resources=code_interpreter_tool.resources
        )
        
        thread = project_client.agents.create_thread()
        
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=get_pdf_generator_instruction()
        )
        
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        if run.status == "completed":
            messages = project_client.agents.list_messages(thread_id=thread.id)
            
            html_file_id = None
            for message in messages.data:
                if message.role == "assistant" and hasattr(message, 'content'):
                    for content_item in message.content:
                        if hasattr(content_item, 'text') and hasattr(content_item.text, 'annotations'):
                            for annotation in content_item.text.annotations:
                                if hasattr(annotation, 'file_path') and annotation.file_path:
                                    html_file_id = annotation.file_path.file_id
                    break
            
            # Download HTML file
            if html_file_id:
                try:
                    frontend_dir = output_paths["analysis_outputs_dir"]
                    project_client.agents.save_file(
                        file_id=html_file_id,
                        file_name="GMR_Comprehensive_Credit_Analysis.html",
                        target_dir=frontend_dir
                    )
                    
                    # Convert HTML to PDF
                    pdf_message = project_client.agents.create_message(
                        thread_id=thread.id,
                        role="user",
                        content="Convert the HTML file to PDF named GMR_Comprehensive_Credit_Analysis.pdf. Maintain all formatting and styling."
                    )
                    
                    pdf_run = project_client.agents.create_and_process_run(
                        thread_id=thread.id,
                        agent_id=agent.id
                    )
                    
                    if pdf_run.status == "completed":
                        pdf_messages = project_client.agents.list_messages(thread_id=thread.id)
                        
                        pdf_file_id = None
                        for message in pdf_messages.data:
                            if message.role == "assistant" and hasattr(message, 'content'):
                                for content_item in message.content:
                                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'annotations'):
                                        for annotation in content_item.text.annotations:
                                            if hasattr(annotation, 'file_path') and annotation.file_path:
                                                if annotation.file_path.file_id != html_file_id:
                                                    pdf_file_id = annotation.file_path.file_id
                                break
                        
                        # Download PDF file
                        if pdf_file_id:
                            try:
                                project_client.agents.save_file(
                                    file_id=pdf_file_id,
                                    file_name="GMR_Comprehensive_Credit_Analysis.pdf",
                                    target_dir=frontend_dir
                                )
                            except Exception:
                                pass
                        
                except Exception:
                    pass
            
    except Exception:
        pass

if __name__ == "__main__":
    convert_txt_to_html()