"""
Cosmos DB Service - Backend with Managed Identity Support
Handles workflow persistence using Azure Managed Identity or connection string
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CosmosDBService:
    """Service for managing workflow data in Cosmos DB"""
    
    def __init__(self):
        """Initialize Cosmos DB client with Managed Identity or connection string"""
        
        # Load agents responses from JSON file
        self.agents_data = self._load_agents_responses()
        
        # Option 1: Use Managed Identity (production)
        if os.getenv('AZURE_COSMOS_ENDPOINT'):
            endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
            credential = DefaultAzureCredential()
            self.client = CosmosClient(endpoint, credential=credential)
            logger.info("✅ Cosmos DB connected using Managed Identity")
        
        # Option 2: Use connection string (fallback)
        elif os.getenv('COSMOS_CONNECTION_STRING'):
            connection_string = os.getenv('COSMOS_CONNECTION_STRING')
            self.client = CosmosClient.from_connection_string(connection_string)
            logger.info("✅ Cosmos DB connected using connection string")
        
        else:
            logger.warning("⚠️ No Cosmos DB credentials found in environment")
            self.client = None
            self.database = None
            self.container = None
            return
        
        # Database and container configuration from environment
        self.database_name = os.getenv('COSMOS_DATABASE_NAME', 'creditreport_d')
        self.container_name = os.getenv('COSMOS_CONTAINER_NAME', 'creditreport_c')
        
        try:
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            logger.info(f"✅ Cosmos DB service ready: {self.database_name}/{self.container_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
            self.database = None
            self.container = None
    
    def _load_agents_responses(self) -> Dict:
        """Load agent responses from JSON file"""
        try:
            json_path = Path(__file__).parent / "agents_responses.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("⚠️ agents_responses.json not found")
                return {"agents": {}, "messageCount": 0, "responseCount": 0}
        except Exception as e:
            logger.error(f"❌ Failed to load agents responses: {e}")
            return {"agents": {}, "messageCount": 0, "responseCount": 0}
    
    def is_enabled(self) -> bool:
        """Check if Cosmos DB is enabled and connected"""
        return self.container is not None
    
    def generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"workflow-{timestamp}-{random_str}"
    
    def create_workflow(self, company_name: str = "GMR Airports Limited", additional_data: Dict = None) -> Dict:
        """Create a new workflow document"""
        if not self.is_enabled():
            logger.warning("Cosmos DB not enabled")
            return {}
        
        workflow_id = self.generate_workflow_id()
        
        workflow = {
            "id": workflow_id,
            "workflowid": workflow_id,  # MUST match partition key /workflowid (lowercase)
            "workflowId": workflow_id,  # Keep camelCase for frontend compatibility
            "companyName": company_name,
            "status": "in_progress",
            "createdAt": datetime.now().astimezone().isoformat(),
            "updatedAt": datetime.now().astimezone().isoformat(),
        }
        
        # Add additional data from request if provided
        if additional_data:
            workflow.update(additional_data)
        
        try:
            created_workflow = self.container.create_item(body=workflow)
            # Merge with agents data before returning
            created_workflow.update(self.agents_data)
            logger.info(f"✅ Workflow created: {workflow_id}")
            return created_workflow
        except Exception as e:
            logger.error(f"❌ Failed to create workflow: {e}")
            return {}
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID and merge with agents data"""
        logger.info(f"🔍 get_workflow called with workflow_id: {workflow_id}")
        
        if not self.is_enabled():
            logger.warning("⚠️ Cosmos DB not enabled, returning None")
            return None
        
        try:
            logger.info(f"📡 Reading workflow from Cosmos DB: {workflow_id}")
            logger.info(f"📍 Container: {self.database_name}/{self.container_name}")
            logger.info(f"🔑 Partition key value: {workflow_id}")
            
            workflow = self.container.read_item(item=workflow_id, partition_key=workflow_id)
            logger.info(f"✅ Successfully retrieved workflow: {workflow_id}")
            logger.info(f"📦 Workflow fields: {list(workflow.keys())}")
            
            # Merge with agents data from JSON file
            workflow.update(self.agents_data)
            logger.info(f"✅ Merged agents data into workflow")
            
            return workflow
        except Exception as e:
            logger.error(f"❌ Error getting workflow {workflow_id}: {type(e).__name__} - {e}")
            import traceback
            logger.error(f"📋 Stack trace: {traceback.format_exc()}")
            return None
    
    def list_workflows(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict]:
        """List all workflows ordered by creation date"""
        logger.info(f"🔍 list_workflows called with limit={limit}, status_filter={status_filter}")
        
        if not self.is_enabled():
            logger.warning("⚠️ Cosmos DB not enabled, returning empty list")
            return []
        
        try:
            query = "SELECT * FROM c ORDER BY c.createdAt DESC"
            if status_filter:
                query = f"SELECT * FROM c WHERE c.status = '{status_filter}' ORDER BY c.createdAt DESC"
            
            logger.info(f"📡 Executing query: {query}")
            logger.info(f"📍 Container: {self.database_name}/{self.container_name}")
            logger.info(f"🔑 Partition key: /workflowid (lowercase)")
            
            workflows = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True,
                max_item_count=limit
            ))
            
            logger.info(f"✅ Query returned {len(workflows)} workflows")
            
            # Merge agents data into each workflow
            for idx, workflow in enumerate(workflows):
                workflow_id = workflow.get('id', workflow.get('workflowId', 'unknown'))
                logger.debug(f"📦 Workflow {idx+1}: {workflow_id}, status={workflow.get('status')}")
                workflow.update(self.agents_data)
            
            logger.info(f"📊 Retrieved and merged {len(workflows)} workflows")
            return workflows
        except Exception as e:
            logger.error(f"❌ Failed to list workflows: {type(e).__name__} - {e}")
            import traceback
            logger.error(f"📋 Stack trace: {traceback.format_exc()}")
            return []
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow by ID"""
        if not self.is_enabled():
            return False
        
        try:
            self.container.delete_item(item=workflow_id, partition_key=workflow_id)
            logger.info(f"✅ Deleted workflow: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            return False
    
    def update_workflow_status(self, workflow_id: str, status: str) -> Optional[Dict]:
        """Update workflow status"""
        if not self.is_enabled():
            return None
        
        try:
            workflow = self.container.read_item(item=workflow_id, partition_key=workflow_id)
            workflow['status'] = status
            workflow['updatedAt'] = datetime.now().astimezone().isoformat()
            
            if status == "completed":
                workflow['completedAt'] = datetime.now().astimezone().isoformat()
            
            updated = self.container.replace_item(item=workflow_id, body=workflow)
            logger.info(f"✅ Workflow {workflow_id} status updated to {status}")
            return updated
        except Exception as e:
            logger.error(f"❌ Failed to update workflow status: {e}")
            return None
    
    def update_agent_status(self, workflow_id: str, agent_key: str, status: str, output: str = None) -> Optional[Dict]:
        """Update agent status within a workflow"""
        if not self.is_enabled():
            return None
        
        try:
            workflow = self.container.read_item(item=workflow_id, partition_key=workflow_id)
            
            # Initialize agents dict if not exists
            if 'agents' not in workflow:
                workflow['agents'] = {}
            
            # Update agent status
            if agent_key not in workflow['agents']:
                workflow['agents'][agent_key] = {}
            
            workflow['agents'][agent_key]['status'] = status
            workflow['agents'][agent_key]['updatedAt'] = datetime.now().astimezone().isoformat()
            
            if output:
                workflow['agents'][agent_key]['output'] = output
            
            if status == "completed":
                workflow['agents'][agent_key]['completedAt'] = datetime.now().astimezone().isoformat()
            
            workflow['updatedAt'] = datetime.now().astimezone().isoformat()
            
            updated = self.container.replace_item(item=workflow_id, body=workflow)
            logger.info(f"✅ Agent {agent_key} status updated to {status} in workflow {workflow_id}")
            return updated
        except Exception as e:
            logger.error(f"❌ Failed to update agent status: {e}")
            return None


# Global instance
cosmos_service = CosmosDBService()
