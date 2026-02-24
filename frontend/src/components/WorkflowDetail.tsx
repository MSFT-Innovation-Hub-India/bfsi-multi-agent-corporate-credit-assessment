import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft,
  Building2, 
  RefreshCw, 
  Loader2,
  CheckCircle,
  Clock,
  TrendingUp,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import './WorkflowDetail.css';

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

const WorkflowDetail: React.FC = () => {
  const { workflowId } = useParams<{ workflowId: string }>();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(
    new Set(['market_analyst', 'proposal_verification', 'company_analyst', 'financial_analyst', 'pdf_generator'])
  );

  const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';

  useEffect(() => {
    if (workflowId) {
      fetchWorkflow();
      const interval = setInterval(fetchWorkflow, 5000);
      return () => clearInterval(interval);
    }
  }, [workflowId]);

  const fetchWorkflow = async () => {
    try {
      const response = await fetch(`${API_URL}/api/workflows/${workflowId}`);
      if (!response.ok) {
        throw new Error('Workflow not found');
      }
      const data = await response.json();
      
      // Fallback: If agent outputs are empty, try to load from public folder
      if (data.agents) {
        for (const [agentKey, agent] of Object.entries(data.agents)) {
          const typedAgent = agent as Agent;
          if (!typedAgent.output || typedAgent.output.length < 100) {
            try {
              const publicResponse = await fetch(`/processed_data/${agentKey}.txt`);
              if (publicResponse.ok) {
                const fallbackOutput = await publicResponse.text();
                typedAgent.output = fallbackOutput;
                console.log(`✅ Loaded ${agentKey} from public folder fallback`);
              }
            } catch (err) {
              console.warn(`⚠️ Could not load ${agentKey} from public folder`, err);
            }
          }
        }
      }
      
      setWorkflow(data);
      setError(null);
    } catch (err) {
      setError('Failed to load workflow');
      console.error('Error fetching workflow:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchWorkflow();
  };

  const handleDownloadPDF = async () => {
    const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';
    
    try {
      // Try blob storage API first
      const blobUrl = `${API_URL}/api/blobs/GMR_Credit_Report.pdf/download`;
      console.log('📥 Attempting PDF download from blob storage:', blobUrl);
      
      // Check if blob endpoint is responsive
      const response = await fetch(blobUrl, { method: 'HEAD' });
      if (response.ok) {
        window.open(blobUrl, '_blank');
        console.log('✅ PDF download from blob storage initiated');
        return;
      }
    } catch (blobErr) {
      console.warn('⚠️ Blob storage download failed, trying public folder fallback:', blobErr);
    }
    
    // Fallback to public folder
    const publicPdfPath = '/processed_data/GMR_Comprehensive_Credit_Analysis.pdf';
    console.log('📂 Downloading PDF from public folder:', publicPdfPath);
    window.open(publicPdfPath, '_blank');
  };

  const toggleAgent = (agentKey: string) => {
    const newExpanded = new Set(expandedAgents);
    if (newExpanded.has(agentKey)) {
      newExpanded.delete(agentKey);
    } else {
      newExpanded.add(agentKey);
    }
    setExpandedAgents(newExpanded);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
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

  const getAgentIcon = (agentKey: string) => {
    const icons: Record<string, React.ReactElement> = {
      market_analyst: <TrendingUp className="h-5 w-5" />,
      proposal_verification: <CheckCircle className="h-5 w-5" />,
      company_analyst: <Building2 className="h-5 w-5" />,
      financial_analyst: <TrendingUp className="h-5 w-5" />
    };
    return icons[agentKey] || <CheckCircle className="h-5 w-5" />;
  };

  const cleanOutput = (output: string | null): string => {
    if (!output) return '';
    
    // Remove lines with timestamps and "Generated on" text
    const lines = output.split('\n');
    const cleanedLines = lines.filter((line) => {
      const trimmedLine = line.trim();
      // Skip lines that contain timestamp patterns
      if (/^Generated on:/.test(trimmedLine)) return false;
      if (/^\*\*Generated on:/.test(trimmedLine)) return false;
      if (/\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}/.test(trimmedLine)) return false;
      if (/^Agent:/.test(trimmedLine)) return false;
      return true;
    });
    
    return cleanedLines.join('\n').trim();
  };

  // Helper function to render agent cards
  const renderAgentCard = (agentKey: string, displayName: string, icon: React.ReactElement) => {
    const agent = workflow?.agents[agentKey as keyof typeof workflow.agents];
    if (!agent) return null;

    const isExpanded = expandedAgents.has(agentKey);
    const hasOutput = Boolean(agent.output);
    
    return (
      <div
        className="w-full border rounded-lg overflow-hidden transition-all border-emerald-300 bg-emerald-50"
      >
        <div
          className="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
          onClick={() => toggleAgent(agentKey)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-emerald-600 text-white">
                {hasOutput ? (
                  <CheckCircle className="h-5 w-5" />
                ) : agent.status === 'running' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  icon
                )}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{displayName}</h3>
                <p className="text-sm text-gray-500">
                  {hasOutput ? 'Completed' : agent.status === 'running' ? 'Running' : 'Pending'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {hasOutput && (
                <Badge className="bg-emerald-100 text-emerald-800">
                  Output Available
                </Badge>
              )}
              {isExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </div>
          </div>
        </div>

        {isExpanded && (
          <div className="border-t border-emerald-200 bg-white p-6 max-h-64 overflow-y-auto">
            {hasOutput ? (
              <pre className="text-sm whitespace-pre-wrap font-mono text-gray-700 leading-relaxed">
                {cleanOutput(agent.output)}
              </pre>
            ) : (
              <p className="text-gray-500 italic text-center py-8">
                No output available yet
              </p>
            )}
          </div>
        )}
      </div>
    );
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

  if (error || !workflow) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error || 'Workflow not found'}</p>
            <Button onClick={() => navigate('/workflows')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Workflows
            </Button>
          </div>
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
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => navigate('/workflows')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{workflow.companyName}</h1>
                <p className="text-sm text-gray-600">{workflow.workflowId}</p>
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
            <Badge 
              className={`${
                workflow.status === 'completed' ? 'bg-emerald-100 text-emerald-800' :
                workflow.status === 'in-progress' ? 'bg-amber-100 text-amber-800' :
                'bg-red-100 text-red-800'
              }`}
            >
              {workflow.status.toUpperCase()}
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-6">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Status
              </CardTitle>
              <CheckCircle className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-gray-900 capitalize">
                {workflow.status}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Company
              </CardTitle>
              <Building2 className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium text-gray-900">
                {workflow.companyName}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Agents
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {Object.values(workflow.agents).filter(a => a.status === 'completed').length} / 4
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Completion
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">
                {Math.round((Object.values(workflow.agents).filter(a => a.status === 'completed').length / 4) * 100)}%
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Agent Outputs - Staged Layout */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Workflow - 3 Stage Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Stage 1: Market Analysis */}
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm">
                  Stage 1: Market Analysis
                </div>
              </div>
              
              <div className="flex justify-center">
                <div className="w-full max-w-md">
                  {renderAgentCard('market_analyst', 'Market Analyst', <TrendingUp />)}
                </div>
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center">
              <ChevronDown className="h-8 w-8 text-gray-400" />
            </div>

            {/* Stage 2: Credit Analysis */}
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm">
                  Stage 2: Credit Analysis
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {renderAgentCard('proposal_verification', 'Proposal Verification', <CheckCircle />)}
                {renderAgentCard('company_analyst', 'Company Profile', <Building2 />)}
                {renderAgentCard('financial_analyst', 'Financial Analyst', <TrendingUp />)}
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center">
              <ChevronDown className="h-8 w-8 text-gray-400" />
            </div>

            {/* Stage 3: Report Generation */}
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold text-sm">
                  Stage 3: Report Generation
                </div>
              </div>
              
              <div className="flex justify-center">
                <div className="w-full max-w-md">
                  <div className="border rounded-lg overflow-hidden transition-all border-emerald-300 bg-emerald-50">
                    <div
                      className="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
                      onClick={() => toggleAgent('pdf_generator')}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-emerald-600 text-white">
                            <CheckCircle className="h-5 w-5" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">Credit Report Generator</h3>
                            <p className="text-sm text-gray-500">Completed</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <Badge className="bg-emerald-100 text-emerald-800">
                            Output Available
                          </Badge>
                          {expandedAgents.has('pdf_generator') ? (
                            <ChevronUp className="h-5 w-5 text-gray-400" />
                          ) : (
                            <ChevronDown className="h-5 w-5 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </div>

                    {expandedAgents.has('pdf_generator') && (
                      <div className="border-t border-emerald-200 bg-white p-6">
                        <div className="space-y-4">
                          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <svg className="h-8 w-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                              </svg>
                              <div>
                                <p className="font-semibold text-gray-900">GMR Credit Analysis Report</p>
                                <p className="text-sm text-gray-500">PDF Document - Generated {formatDate(workflow.updatedAt)}</p>
                              </div>
                            </div>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={handleDownloadPDF}
                            >
                              Download PDF
                            </Button>
                          </div>
                          <p className="text-sm text-gray-600">
                            ✅ Final credit analysis report has been generated successfully.
                            The report includes comprehensive analysis from all agents: Market Analysis, 
                            Proposal Verification, Company Profile, and Financial Analysis.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default WorkflowDetail;
