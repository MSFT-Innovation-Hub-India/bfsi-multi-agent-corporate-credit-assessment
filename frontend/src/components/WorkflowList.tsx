import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  RefreshCw, 
  Loader2,
  TrendingUp,
  CheckCircle,
  Clock
} from 'lucide-react';
import './WorkflowList.css';

interface Agent {
  status: string;
  output: string | null;
  startedAt: string | null;
  completedAt: string | null;
}

interface Workflow {
  id: string;
  workflowId: string;
  companyName: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  agents: {
    market_analyst: Agent;
    proposal_verification: Agent;
    company_analyst: Agent;
    financial_analyst: Agent;
  };
  messageCount: number;
  responseCount: number;
}

const WorkflowList: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';

  useEffect(() => {
    fetchWorkflows();
    const interval = setInterval(fetchWorkflows, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_URL}/api/workflows`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setWorkflows(data.workflows || []);
        setError(null);
      } else {
        setError(data.error || 'Failed to fetch workflows');
      }
    } catch (err) {
      setError('Failed to connect to backend');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchWorkflows();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getAgentDisplayName = (agentKey: string) => {
    const names: Record<string, string> = {
      market_analyst: 'Market Analyst',
      proposal_verification: 'Proposal Verification',
      company_analyst: 'Company Analyst',
      financial_analyst: 'Financial Analyst'
    };
    return names[agentKey] || agentKey;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Workflow History</h1>
                <p className="text-sm text-gray-600">Corporate Credit Assessment Workflows</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              {isRefreshing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
            <Button 
              size="sm" 
              onClick={() => navigate('/dashboard')}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-6">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Workflows
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{workflows.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Completed
              </CardTitle>
              <CheckCircle className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">
                {workflows.filter(w => w.status === 'completed').length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                In Progress
              </CardTitle>
              <Clock className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-600">
                {workflows.filter(w => w.status === 'in-progress').length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Messages
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {workflows.reduce((sum, w) => sum + w.messageCount, 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflows List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Workflow Sessions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {workflows.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <p>No workflows found. Start an analysis to create one.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {workflows.map((workflow) => (
                  <div 
                    key={workflow.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/workflows/${workflow.workflowId}`)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                        <Building2 className="h-5 w-5 text-emerald-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{workflow.companyName}</h3>
                        <p className="text-sm text-gray-500">{workflow.workflowId}</p>
                        <p className="text-xs text-gray-400 mt-1">{formatDate(workflow.createdAt)}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      {/* Agent Status Indicators */}
                      <div className="flex gap-2">
                        {Object.entries(workflow.agents).map(([agentKey, agent]) => (
                          <div
                            key={agentKey}
                            className="flex flex-col items-center gap-1"
                            title={getAgentDisplayName(agentKey)}
                          >
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                agent.output ? 'bg-emerald-100' : 
                                agent.status === 'running' ? 'bg-amber-100' : 
                                'bg-gray-100'
                              }`}
                            >
                              {agent.output ? (
                                <CheckCircle className="h-4 w-4 text-emerald-600" />
                              ) : agent.status === 'running' ? (
                                <Loader2 className="h-4 w-4 animate-spin text-amber-600" />
                              ) : (
                                <Clock className="h-4 w-4 text-gray-400" />
                              )}
                            </div>
                            <span className="text-xs text-gray-500">
                              {agentKey.split('_')[0]}
                            </span>
                          </div>
                        ))}
                      </div>

                      <div className="text-right">
                        <Badge 
                          className={`${
                            workflow.status === 'completed' ? 'bg-emerald-100 text-emerald-800' :
                            workflow.status === 'in-progress' ? 'bg-amber-100 text-amber-800' :
                            'bg-red-100 text-red-800'
                          }`}
                        >
                          {workflow.status.toUpperCase()}
                        </Badge>
                        <p className="text-sm text-gray-500 mt-1">
                          {workflow.messageCount} messages | {workflow.responseCount} responses
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default WorkflowList;
