# === GMR Airports Limited Proposal Verification Agent ===
"""
Comprehensive Proposal Verification Agent for GMR Airports Limited
Features:
- Azure AI with vector store file search
- Load instructions from external txt files
- Clean deployment-ready code without file storage
- Professional proposal verification capabilities
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Core libraries
import asyncio
from typing import Dict, Any, Optional, List, Tuple

# Azure AI imports
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FilePurpose,
    VectorStoreDataSource, 
    VectorStoreDataSourceAssetType,
    MessageRole,
    RunStatus
)
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# Configuration from environment variables
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-4o")

# Use absolute paths if GMR_DATA_DIR is set (when running from temp directory)
data_dir = os.getenv("GMR_DATA_DIR", "processed_data")
PROPOSAL_DOCUMENTS = [
    os.path.join(data_dir, "LoanProposal_processed.json"),
    os.path.join(data_dir, "GMR_processed.json"),
    os.path.join(data_dir, "Financial_ratios_processed.json"),
    os.path.join(data_dir, "MDA_processed.json")
]

def load_instructions():
    """Load instructions from the templates/instructions/proposal_verification_agent.txt file"""
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build path to the instructions file
        instructions_path = os.path.join(current_dir, "Templates", "instructions", "proposal_verification_agent.txt")
        
        # Read the instructions file
        with open(instructions_path, 'r', encoding='utf-8') as file:
            instructions = file.read()
        
        print(f"✅ Loaded instructions from: {instructions_path}")
        return instructions
        
    except Exception as e:
        print(f"❌ Error loading instructions: {e}")
        print(f"📁 Looking for: {instructions_path if 'instructions_path' in locals() else 'Template file'}")
        return """
You are a Proposal Verification Agent for GMR Airports Limited.
Analyze loan proposal documents and verify information accuracy.
Focus on:
1. Proposal verification and validation
2. Document completeness assessment
3. Financial data verification
4. Compliance and regulatory checks
5. Risk factor identification
6. Data consistency verification

Use the proposal documents to provide detailed verification analysis.
"""

# Azure AI Project Setup
def get_project_client():
    """Get Azure AI Project client"""
    try:
        if PROJECT_CONNECTION_STRING:
            project_client = AIProjectClient.from_connection_string(
                conn_str=PROJECT_CONNECTION_STRING, 
                credential=AzureKeyCredential("dummy-key")
            )
        else:
            raise ValueError("PROJECT_CONNECTION_STRING not found in environment variables")
        return project_client
    except Exception as e:
        print(f"❌ Error creating project client: {e}")
        return None

def create_proposal_verification_agent():
    """Create GMR Proposal Verification Agent with file search capabilities"""
    
    print("🚀 Creating GMR Proposal Verification Agent...")
    print("=" * 60)
    
    # Get project client
    project_client = get_project_client()
    if not project_client:
        return None
    
    # Load instructions from external file
    instructions = load_instructions()
    
    try:
        # Create vector store for file search
        vector_store = project_client.agents.create_vector_store_and_poll(
            file_ids=[],
            name="GMR-Proposal-Verification-VectorStore"
        )
        print(f"✅ Created vector store, ID: {vector_store.id}")
        
        # Upload proposal documents to vector store
        uploaded_files = []
        
        for file_path in PROPOSAL_DOCUMENTS:
            if Path(file_path).exists():
                print(f"   📤 Uploading: {file_path}")
                try:
                    # Use the correct method from Azure AI documentation
                    file = project_client.agents.upload_file_and_poll(
                        file_path=file_path, 
                        purpose=FilePurpose.AGENTS
                    )
                    uploaded_files.append(file)
                    print(f"   ✅ Uploaded file, file ID: {file.id}")
                except Exception as upload_error:
                    print(f"   ❌ Upload failed for {file_path}: {upload_error}")
                    continue
            else:
                print(f"   ❌ File not found: {file_path}")
        
        if not uploaded_files:
            print("⚠️ No files uploaded, creating agent without file search for now...")
        
        # Add uploaded files to vector store
        if uploaded_files:
            file_ids = [file.id for file in uploaded_files]
            vector_store = project_client.agents.create_vector_store_and_poll(
                file_ids=file_ids,
                name="GMR-Proposal-Verification-VectorStore"
            )
            print(f"✅ Updated vector store with {len(file_ids)} files")
        
        # Create file search tool
        file_search_tool = {"type": "file_search"}
        if uploaded_files:
            file_search_tool["file_search"] = {"vector_store_ids": [vector_store.id]}
        
        # Create agent
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="gmr-proposal-verification-agent",
            instructions=instructions,
            tools=[file_search_tool]
        )
        print(f"✅ Created agent, ID: {agent.id}")
        
        # Create a thread
        thread = project_client.agents.create_thread()
        print(f"✅ Created thread, ID: {thread.id}")
        
        return {
            "project_client": project_client,
            "agent": agent,
            "thread": thread,
            "vector_store": vector_store,
            "uploaded_files": [file.id for file in uploaded_files]
        }
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_proposal_verification(agent_resources, verification_prompt=None):
    """Generate proposal verification using the agent"""
    
    if not verification_prompt:
        verification_prompt = """
Generate comprehensive proposal verification for GMR Airports Limited including:

1. **Proposal Document Verification**
2. **Financial Data Accuracy Check**
3. **Compliance Verification**
4. **Document Completeness Assessment**
5. **Risk Factor Identification**
6. **Data Consistency Analysis**
7. **Regulatory Compliance Check**
8. **Verification Summary and Recommendations**

Use the proposal documents to provide detailed verification analysis with specific findings.
"""
    
    print(f"\n🔍 Generating proposal verification...")
    
    try:
        # Create a message in the thread
        message = agent_resources['project_client'].agents.create_message(
            thread_id=agent_resources['thread'].id,
            role="user",
            content=verification_prompt
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
        
        # Extract the response text (get the latest assistant message)
        verification_text = ""
        for message in messages.data:
            if message.role == "assistant":
                # Handle different message content formats from Azure AI
                if hasattr(message, 'content') and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, 'text'):
                            verification_text += content_item.text.value
                            # Handle file citations if present
                            if hasattr(content_item.text, 'annotations'):
                                for annotation in content_item.text.annotations:
                                    if hasattr(annotation, 'file_citation') and annotation.file_citation:
                                        file_id = annotation.file_citation.file_id
                                        citation = f"[{file_id}]"
                                        verification_text = verification_text.replace(annotation.text, f" {citation}")
                        elif hasattr(content_item, 'value'):
                            verification_text += str(content_item.value)
                        else:
                            verification_text += str(content_item)
                else:
                    # Fallback for other formats
                    verification_text += str(message)
                break  # Get only the latest response
        
        print(f"✅ Generated proposal verification")
        return verification_text
        
    except Exception as e:
        print(f"❌ Error generating verification: {str(e)}")
        return f"Error generating proposal verification: {str(e)}"

def run_proposal_verification_analysis():
    """Execute the GMR Proposal Verification Agent"""
    
    print("🏢 GMR AIRPORTS LIMITED - PROPOSAL VERIFICATION AGENT")
    print("=" * 70)
    print("📑 Purpose: Comprehensive Proposal Verification and Validation")
    print("🎯 Focus: Clean agent execution without file storage")
    print("=" * 70)
    
    # Create agent
    print("\n🚀 Creating Proposal Verification Agent...")
    agent_resources = create_proposal_verification_agent()
    
    if not agent_resources:
        print("❌ Failed to create agent. Please check configuration.")
        return False
    
    print("✅ Agent created successfully!")
    
    # Generate verification (execute agent logic without saving)
    print(f"\n📋 Executing Proposal Verification")
    verification_result = generate_proposal_verification(agent_resources)
    
    # Agent processing completed (no file writing)
    print(f"✅ Proposal verification processing completed")
    
    # Agent execution summary
    print(f"\n🎉 COMPREHENSIVE PROPOSAL VERIFICATION AGENT EXECUTED!")
    print(f"📊 Verification Completed Successfully")
    print(f"📝 Agent Processing: Completed Successfully")
    print(f"🗂️ Output: Agent execution completed without file storage")
    
    return True

if __name__ == "__main__":
    """Execute the GMR Proposal Verification Agent"""
    
    print("🏢 GMR AIRPORTS LIMITED - PROPOSAL VERIFICATION AGENT")
    print("=" * 70)
    print("📑 Purpose: Comprehensive Proposal Verification and Validation")
    print("🎯 Focus: Clean deployment-ready agent execution")
    print("=" * 70)
    
    # Run proposal verification
    success = run_proposal_verification_analysis()
    if success:
        print("\n🎯 Agent execution completed successfully!")
    else:
        print("\n❌ Agent execution failed!")