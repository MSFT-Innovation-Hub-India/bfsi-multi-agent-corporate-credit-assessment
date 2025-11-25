import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowDown,
  TrendingUp,
  FileCheck,
  Building,
  Calculator,
  FileText,
  Download,
  CheckCircle,
  Loader2,
  Eye,
  Bot,
  MessageSquare,
  Play,
  RotateCcw,
  X,
  Maximize2,
  Minimize2
} from 'lucide-react';

interface ChatMessage {
  id: string;
  timestamp: string;
  agent: string;
  stage: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
}

interface WorkflowVisualizationProps {
  session: any;
  onBack: () => void;
}

// Agent processing steps based on actual semantic kernel orchestration
const marketAnalystSteps = [
  { text: "📰 Fetching latest GMR infrastructure news from all major sources...", delay: 2000 },
  { text: " GMR Group Official Media", delay: 1500 },
  { text: " Economic Times Markets", delay: 1500 },
  { text: " Business Standard Infrastructure", delay: 1500 },
  { text: " Financial Express Infrastructure", delay: 1500 },
  { text: " Live Mint Markets", delay: 1500 },
  { text: " Moneycontrol Markets", delay: 1500 },
  { text: " NDTV Business", delay: 1500 },
  { text: " NDTV Profit", delay: 1500 },
  { text: " Business Today Markets", delay: 1500 },
  { text: " BSE Corporate Announcements", delay: 1500 },
  { text: " Infrastructure Sector Updates", delay: 1500 },
  { text: " Devdiscourse Business", delay: 1500 },
  { text: "📊 TOTAL: 52 unique articles collected", delay: 2000 },
  { text: "✅ GMR news scraping completed!", delay: 2000, isComplete: true }
];

const proposalVerificationSteps = [
  { text: "📝 Processing section: Proposal Details", delay: 2000 },
  { text: "🔍 Processing Section: Assistance Details", delay: 2000 },
  { text: "🔍 Processing Section: Credit Appraisal Note", delay: 2000 },
  { text: "🔍 Processing Section: Assistance Details (Borrower)", delay: 2000 },
  { text: "🔍 Processing Section: Exposure Remarks", delay: 2000 },
  { text: "🔍 Processing Section: Account Conduct", delay: 2000 },
  { text: "🔍 Processing Section: Auditor & Guidelines", delay: 2000 },
  { text: "🔍 Processing Section: RFA & ERM Details", delay: 2000 },
  { text: "🔍 Processing Section: Income & ROE Details", delay: 2000 },
  { text: "🔍 Processing Section: Overall Verification Analysis", delay: 2000 },
  { text: "✅ Proposal verification completed!", delay: 2000, isComplete: true }
];

const companyProfileSteps = [
  { text: "📝 Processing section : Company Profile & Business Overview", delay: 2000 },
  { text: "📝 Processing section : Financial Performance & Key Metrics", delay: 2000 },
  { text: "📝 Processing section : Business Segments & Revenue Streams", delay: 2000 },
  { text: "📝 Processing section : Airport Portfolio & Infrastructure Details", delay: 2000 },
  { text: "📝 Processing section : Corporate Governance & Management", delay: 2000 },
  { text: "📝 Processing section : Regulatory Framework & Compliance", delay: 2000 },
  { text: "📝 Processing section : Group Structure & Related Entities", delay: 2000 },
  { text: "📝 Processing section : Recent Developments & Strategic Initiatives", delay: 2000 },
  { text: "📝 Processing section : Risk Assessment & Mitigation Strategies", delay: 2000 },
  { text: "✅ Company profile analysis completed!", delay: 2000, isComplete: true }
];

const financialAnalysisSteps = [
  { text: "📝 Processing section : Physical Performance Analysis", delay: 2000 },
  { text: "📝 Processing section : Financial Tables & Analysis", delay: 2000 },
  { text: "📝 Processing section : Current Year Performance", delay: 2000 },
  { text: "📝 Processing section : Detailed Financial Analysis", delay: 2000 },
  { text: "📝 Processing section : Asset & Liability Breakdown", delay: 2000 },
  { text: "📝 Processing section : Cash Flow Analysis", delay: 2000 },
  { text: "📝 Processing section : Projections & Major Developments", delay: 2000 },
  { text: "📝 Processing section : Contingent Liabilities & Group Information", delay: 2000 },
  { text: "✅ Financial analysis completed!", delay: 2000, isComplete: true }
];

const pdfGenerationSteps = [
  { text: "📑 Generating comprehensive credit analysis report...", delay: 4000 },
  { text: "✅ Report generation completed!", delay: 4000, isComplete: true }
];

// Agent Modal Component
const AgentProcessingModal: React.FC<{
  agentName: string;
  isOpen: boolean;
  onClose: () => void;
  steps: Array<{ text: string; delay: number; isComplete?: boolean }>;
  agentProgress?: { currentStep: number; completedSteps: string[]; isProcessing: boolean };
}> = ({ agentName, isOpen, onClose, steps, agentProgress }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Use progress from parent if available
  const currentStep = agentProgress?.currentStep || 0;
  const completedSteps = agentProgress?.completedSteps || [];
  const isProcessing = agentProgress?.isProcessing ?? false;

  if (!isOpen) return null;

  const getAgentIcon = (name: string) => {
    switch (name) {
      case 'Market Analyst': return <TrendingUp className="h-6 w-6" />;
      case 'Proposal Verification': return <FileCheck className="h-6 w-6" />;
      case 'Company Profile': return <Building className="h-6 w-6" />;
      case 'Financial Analyst': return <Calculator className="h-6 w-6" />;
      case 'Credit Report Generator': return <Download className="h-6 w-6" />;
      default: return <Bot className="h-6 w-6" />;
    }
  };

  const getAgentColor = (name: string) => {
    switch (name) {
      case 'Market Analyst': return 'from-blue-500 to-blue-600';
      case 'Proposal Verification': return 'from-blue-500 to-blue-600';
      case 'Company Profile': return 'from-blue-500 to-blue-600';
      case 'Financial Analyst': return 'from-blue-500 to-blue-600';
      case 'Credit Report Generator': return 'from-blue-500 to-blue-600';
      default: return 'from-blue-500 to-blue-600';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className={`bg-white rounded-2xl shadow-2xl w-full overflow-hidden transition-all duration-300 ${
        isExpanded ? 'max-w-7xl max-h-[90vh]' : 'max-w-2xl'
      }`}>
        <div className={`p-6 border-b bg-gradient-to-r ${getAgentColor(agentName)} text-white`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                {getAgentIcon(agentName)}
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold">{agentName}</h2>
                <p className="text-white text-opacity-90">
                  {isProcessing ? 'Processing...' : 'Completed'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-white hover:bg-white hover:bg-opacity-20"
                title={isExpanded ? "Minimize" : "Expand"}
              >
                {isExpanded ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
              </Button>
              <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white hover:bg-opacity-20">
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <h3 className="font-semibold text-gray-900">Processing Timeline</h3>
                <Badge variant="outline" className="text-xs">
                  Live Updates
                </Badge>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-sm text-gray-600">
                  {currentStep} / {steps.length} steps
                </div>
                <div className="text-xs text-gray-500 font-mono">
                  {isProcessing ? 'Active' : 'Completed'}
                </div>
              </div>
            </div>
            <Progress value={(currentStep / steps.length) * 100} className="h-3" />
          </div>

          <div className={`overflow-hidden ${isExpanded ? 'h-[500px]' : 'h-auto'}`}>
            <div className={`space-y-2 pr-2 ${isExpanded ? 'overflow-y-auto h-full' : ''}`}>
              {(isExpanded ? completedSteps : completedSteps.slice(-2)).map((step, index) => (
                <div key={index} className="flex items-start gap-3 animate-fade-in">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    {index < (isExpanded ? completedSteps : completedSteps.slice(-2)).length - 1 && (
                      <div className="w-px h-6 bg-gray-200 ml-0.5 mt-1"></div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0 pb-2">
                    <p className="text-sm text-gray-700 font-mono leading-relaxed">
                      {step}
                    </p>
                  </div>
                </div>
              ))}
              
              {isProcessing && currentStep < steps.length && (
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                  </div>
                  <div className="flex-1 min-w-0 pb-2">
                    <p className="text-sm text-gray-500 font-mono leading-relaxed">
                      Processing next step...
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {!isExpanded && completedSteps.length > 2 && (
            <div className="mt-3 text-center">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setIsExpanded(true)}
                className="text-blue-600 hover:text-blue-800 text-xs"
              >
                Show {completedSteps.length - 2} more steps
              </Button>
            </div>
          )}

          <div className="mt-6 pt-6 border-t">
            <div className="flex items-center justify-between">
              {!isProcessing ? (
                <>
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Processing completed successfully</span>
                  </div>
                  <Button onClick={onClose}>
                    Continue
                  </Button>
                </>
              ) : (
                <>
                  <div></div>
                  <Button variant="outline" onClick={onClose}>
                    Close
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Full Response Modal
const FullResponseModal: React.FC<{
  agentName: string;
  isOpen: boolean;
  onClose: () => void;
  content: string;
}> = ({ agentName, isOpen, onClose, content }) => {
  const [fileContent, setFileContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (agentName === 'Credit Report Generator') {
        // For PDF, we don't need to load content, just verify it exists
        verifyPdfExists();
      } else {
        // For other agents, load their text files
        loadFileContent();
      }
    }
  }, [isOpen, content, agentName]);

  const verifyPdfExists = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`📁 Checking if PDF exists: ${content}`);
      const response = await fetch(content, { method: 'HEAD' });
      
      if (response.ok) {
        setFileContent('PDF_READY'); // Flag to indicate PDF is ready
        console.log(`✅ PDF file exists: ${content}`);
      } else {
        setError(`PDF file not found at: ${content}. Please ensure the MCP PDF generator has been run.`);
      }
    } catch (err) {
      console.error('Error checking PDF:', err);
      setError(`Failed to verify PDF file. Please ensure the MCP PDF generator has been run.`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFileContent = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Use the content path directly (it already starts with /)
      console.log(`📁 Attempting to load file: ${content}`);
      const response = await fetch(content);
      
      if (response.ok) {
        const data = await response.text();
        setFileContent(data);
        console.log(`✅ Successfully loaded file: ${content} (${data.length} characters)`);
      } else {
        // Try alternative paths if the main path fails
        const alternativePaths = [
          `/processed_data/${content.split('/').pop()}`,
          `/analysis_outputs/${content.split('/').pop()}`,
          `/${content.replace('/analysis_outputs/', '')}`
        ];
        
        let loaded = false;
        for (const altPath of alternativePaths) {
          try {
            console.log(`Trying alternative path: ${altPath}`);
            const altResponse = await fetch(altPath);
            if (altResponse.ok) {
              const data = await altResponse.text();
              setFileContent(data);
              console.log(`✅ Loaded from alternative path: ${altPath}`);
              loaded = true;
              break;
            }
          } catch (e) {
            console.log(`❌ Failed to load from: ${altPath}`);
            continue;
          }
        }
        
        if (!loaded) {
          setError(`Unable to load file: ${content}. Status: ${response.status}. Please ensure the semantic kernel orchestrator has generated the analysis files.`);
        }
      }
    } catch (err) {
      console.error('Error reading file:', err);
      setError(`Failed to fetch analysis file for ${agentName}. Please ensure the semantic kernel orchestrator has been run and generated the output files.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      if (agentName === 'Credit Report Generator') {
        // For Credit Report Generator, download the PDF file directly
        if (!fileContent || fileContent !== 'PDF_READY') {
          alert('PDF report not available. Please ensure the MCP PDF generator has been run.');
          return;
        }
        
        // Fetch the PDF file as a blob
        console.log(`📥 Downloading PDF from: ${content}`);
        const response = await fetch(content);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch PDF: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Create a link and trigger download
        const link = document.createElement("a");
        link.download = "GMR_Comprehensive_Credit_Analysis.pdf";
        link.href = url;
        link.click();
        
        // Clean up
        URL.revokeObjectURL(url);
        console.log(`✅ PDF download initiated`);
      } else {
        // For text files, use the same blob approach
        if (!fileContent) {
          alert('File content not available. Please ensure the file is loaded.');
          return;
        }
        
        // 1. Stringify the data (text content is already a string)
        const fileData = fileContent;
        
        // 2. Blobify the data with text MIME type
        const blob = new Blob([fileData], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        
        // 3. Create a link in the DOM and click it
        const link = document.createElement("a");
        link.download = content.split('/').pop() || `${agentName.replace(/\s+/g, '_')}_Analysis.txt`;
        link.href = url;
        
        // 4. Download the file
        link.click();
        
        // Clean up the URL object
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Download failed:', error);
      if (error instanceof Error) {
        alert(`Download failed: ${error.message}`);
      } else {
        alert('Download failed: An unknown error occurred.');
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6 border-b bg-gradient-to-r from-gray-50 to-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center">
                <FileText className="h-6 w-6 text-gray-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{agentName} - Analysis Output</h2>
                <p className="text-sm text-gray-600">
                  {agentName === 'Credit Report Generator' ? 'Comprehensive report ready for download' : 'Analysis file available'}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        <div className="p-6">
          {agentName === 'Credit Report Generator' ? (
            // Special handling for Credit Report Generator - show PDF file info and download
            isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 text-gray-600 animate-spin" />
                <span className="ml-3 text-gray-600">Verifying PDF report...</span>
              </div>
            ) : error ? (
              <div className="bg-red-50 rounded-xl p-6 border border-red-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <X className="h-5 w-5 text-red-600" />
                  </div>
                  <h4 className="font-semibold text-red-900">PDF Report Not Found</h4>
                </div>
                <p className="text-sm text-red-800 ml-13">{error}</p>
                <div className="mt-4 ml-13">
                  <p className="text-xs text-red-700 mb-3">
                    To generate the PDF report, run:
                    <code className="block mt-2 p-2 bg-red-100 rounded text-xs">
                      python mcp/pdf-mcp-server/generate_pdf_from_custom_format.py
                    </code>
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Professional PDF Credit Analysis Report
                </h3>
                
                <Button onClick={handleDownload} size="lg" className="px-8">
                  <Download className="h-5 w-5 mr-2" />
                  Download PDF Report
                </Button>
                <p className="text-xs text-gray-500 mt-4">
                  File: GMR_Comprehensive_Credit_Analysis.pdf
                </p>
              </div>
            )
          ) : (
            // For other agents, show file content
            <div className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                  <span className="ml-3 text-gray-600">Loading file content...</span>
                </div>
              ) : error ? (
                <div className="bg-red-50 rounded-xl p-6 border border-red-200">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                      <X className="h-5 w-5 text-red-600" />
                    </div>
                    <h4 className="font-semibold text-red-900">Error Loading File</h4>
                  </div>
                  <p className="text-sm text-red-800 ml-13">{error}</p>
                  <p className="text-sm text-red-700 mt-2 ml-13">File path: {content}</p>
                </div>
              ) : (
                <>
                  <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-gray-600" />
                        <span className="font-medium text-gray-900">Analysis Output</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {fileContent.length.toLocaleString()} characters
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 max-h-96 overflow-y-auto">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">
                      {fileContent}
                    </pre>
                  </div>
                </>
              )}
            </div>
          )}
          
          <div className="mt-6 flex justify-end gap-3">
            {!isLoading && !error && (
              <Button variant="outline" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                {agentName === 'Credit Report Generator' ? 'Download Report' : 'Download File'}
              </Button>
            )}
            <Button onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const WorkflowVisualization: React.FC<WorkflowVisualizationProps> = ({ session: _session }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [selectedAgentModal, setSelectedAgentModal] = useState<string | null>(null);
  const [selectedAgentForResponse, setSelectedAgentForResponse] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState<Set<string>>(new Set());
  const [processingAgents, setProcessingAgents] = useState<Set<string>>(new Set());
  const [currentStage, setCurrentStage] = useState(0);
  const [currentAgentInStage, setCurrentAgentInStage] = useState(0);
  const [showArrow, setShowArrow] = useState<string | null>(null);
  const [agentResponses, setAgentResponses] = useState<Record<string, string>>({});
  const [agentProgress, setAgentProgress] = useState<Record<string, { currentStep: number; completedSteps: string[]; isProcessing: boolean }>>({});
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      timestamp: new Date().toISOString(),
      agent: 'System',
      stage: 'initialization',
      message: 'Workflow initialization completed. Ready to start analysis...',
      type: 'info'
    }
  ]);
  
  // Simple state for static workflow
  const [, setSessionId] = useState<string>('');

  // Mark agent as processing when modal opens
  useEffect(() => {
    if (selectedAgentModal) {
      setProcessingAgents(prev => new Set([...prev, selectedAgentModal]));
    }
  }, [selectedAgentModal]);

  const stages = [
    {
      id: 'market',
      name: 'Market Analysis',
      description: 'Comprehensive market intelligence and sentiment analysis',
      agents: ['Market Analyst'],
      layout: 'vertical'
    },
    {
      id: 'financial',
      name: 'Credit Analysis',
      description: 'Multi-agent financial assessment and verification',
      agents: ['Proposal Verification', 'Company Profile', 'Financial Analyst'],
      layout: 'horizontal'
    },
    {
      id: 'report',
      name: 'Report Generation',
      description: 'Final report compilation and document generation',
      agents: ['Credit Report Generator'],
      layout: 'vertical'
    }
  ];

  const getAgentSteps = (agentName: string) => {
    switch (agentName) {
      case 'Market Analyst': return marketAnalystSteps;
      case 'Proposal Verification': return proposalVerificationSteps;
      case 'Company Profile': return companyProfileSteps;
      case 'Financial Analyst': return financialAnalysisSteps;
      case 'Credit Report Generator': return pdfGenerationSteps;
      default: return [];
    }
  };

  const getAgentResponse = (agentName: string): string => {
    // Return file paths accessible from the public folder via HTTP
    // These paths correspond to files created by semantic kernel orchestrator
    const responseMap: Record<string, string> = {
      'Market Analyst': '/analysis_outputs/GMR_Sentiment_Analysis.txt',
      'Proposal Verification': '/analysis_outputs/agent_1_proposal_verification.txt',
      'Company Profile': '/analysis_outputs/agent_2_company_profile.txt', 
      'Financial Analyst': '/analysis_outputs/agent_3_financial_analysis.txt',
      'Credit Report Generator': '/analysis_outputs/GMR_Comprehensive_Credit_Analysis.pdf'
    };

    return responseMap[agentName] || 'Analysis completed successfully.';
  };

  const handleStepUpdate = (step: string, agentName: string) => {
    const newMessage: ChatMessage = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      agent: agentName,
      stage: agentName.toLowerCase().replace(/\s+/g, '_'),
      message: step,
      type: 'info'
    };
    setChatMessages(prev => [...prev, newMessage]);
    
    // Update agent progress
    setAgentProgress(prev => {
      const current = prev[agentName] || { currentStep: 0, completedSteps: [], isProcessing: true };
      return {
        ...prev,
        [agentName]: {
          currentStep: current.currentStep + 1,
          completedSteps: [...current.completedSteps, step],
          isProcessing: true
        }
      };
    });
  };

  const simulateAgentProcessing = async (agentName: string) => {
    const steps = getAgentSteps(agentName);
    
    // Check if already completed
    setAgentProgress(prev => {
      if (prev[agentName]?.isProcessing === false) {
        return prev; // Already completed, don't restart
      }
      return {
        ...prev,
        [agentName]: prev[agentName] || { currentStep: 0, completedSteps: [], isProcessing: true }
      };
    });
    
    // Process steps for this specific agent
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, steps[i].delay));
      handleStepUpdate(steps[i].text, agentName);
      
      if (steps[i].isComplete) {
        // Mark this specific agent as completed
        setAgentProgress(prev => ({
          ...prev,
          [agentName]: { ...prev[agentName], isProcessing: false }
        }));
        
        setCompletedAgents(prev => new Set([...prev, agentName]));
        setProcessingAgents(prev => {
          const newSet = new Set(prev);
          newSet.delete(agentName);
          return newSet;
        });

        // Load agent response from file
        const response = getAgentResponse(agentName);
        setAgentResponses(prev => ({ ...prev, [agentName]: response }));

        const completionMessage: ChatMessage = {
          id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
          agent: agentName,
          stage: agentName.toLowerCase().replace(/\s+/g, '_'),
          message: `✅ ${agentName} processing completed successfully!`,
          type: 'success'
        };
        setChatMessages(prev => [...prev, completionMessage]);
        
        // Continue to next agent in workflow - pass the completed agent
        continueWorkflow(agentName);
        break;
      }
    }
  };

  const continueWorkflow = (completedAgentName: string) => {
    // Find which stage and position this agent is in
    let agentStageIndex = -1;
    let agentPositionInStage = -1;
    
    for (let i = 0; i < stages.length; i++) {
      const pos = stages[i].agents.indexOf(completedAgentName);
      if (pos !== -1) {
        agentStageIndex = i;
        agentPositionInStage = pos;
        break;
      }
    }
    
    if (agentStageIndex === -1) return; // Agent not found
    
    const stage = stages[agentStageIndex];
    
    if (agentPositionInStage + 1 < stage.agents.length) {
      // Next agent in same stage
      const nextAgentIndex = agentPositionInStage + 1;
      const nextAgent = stage.agents[nextAgentIndex];
      
      setCurrentStage(agentStageIndex);
      setCurrentAgentInStage(nextAgentIndex);
      setShowArrow(`arrow-to-${nextAgent}`);
      
      setTimeout(() => {
        setShowArrow(null);
        // Start processing in background without opening modal
        setProcessingAgents(prev => new Set(prev).add(nextAgent));
        simulateAgentProcessing(nextAgent);
      }, 8000);
    } else if (agentStageIndex + 1 < stages.length) {
      // Next stage
      const nextStageIndex = agentStageIndex + 1;
      const nextAgent = stages[nextStageIndex].agents[0];
      
      setCurrentStage(nextStageIndex);
      setCurrentAgentInStage(0);
      setShowArrow(`arrow-stage-${nextStageIndex}`);
      
      setTimeout(() => {
        setShowArrow(null);
        // Start processing in background without opening modal
        setProcessingAgents(prev => new Set(prev).add(nextAgent));
        simulateAgentProcessing(nextAgent);
      }, 8000);
    } else {
      // All done
      setIsRunning(false);
      const finalMessage: ChatMessage = {
        id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        agent: 'System',
        stage: 'completion',
        message: '🎉 Complete workflow finished successfully! All analysis reports are ready.',
        type: 'success'
      };
      setChatMessages(prev => [...prev, finalMessage]);
    }
  };

  const startWorkflow = () => {
    setIsRunning(true);
    setCompletedAgents(new Set());
    setProcessingAgents(new Set());
    setCurrentStage(0);
    setCurrentAgentInStage(0);
    setAgentResponses({});
    
    // Generate session ID
    const newSessionId = `gmr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    
    const startMsg: ChatMessage = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      agent: 'System',
      stage: 'workflow_start',
      message: `Starting comprehensive credit analysis for GMR Infrastructure... (Session: ${newSessionId})`,
      type: 'info'
    };
    setChatMessages([startMsg]);

    console.log('Starting workflow with session:', newSessionId);
    
    // Start processing the first agent in the background (no modal)
    setTimeout(() => {
      const firstAgent = stages[0].agents[0];
      setProcessingAgents(prev => new Set(prev).add(firstAgent));
      // Simulate processing in background
      simulateAgentProcessing(firstAgent);
    }, 1000);
  };

  const resetWorkflow = () => {
    setIsRunning(false);
    setSelectedAgentModal(null);
    setCompletedAgents(new Set());
    setProcessingAgents(new Set());
    setCurrentStage(0);
    setCurrentAgentInStage(0);
    setShowArrow(null);
    setAgentResponses({});
    
    setChatMessages([{
      id: '1',
      timestamp: new Date().toISOString(),
      agent: 'System',
      stage: 'ready',
      message: 'Workflow reset. Ready to start comprehensive credit analysis.',
      type: 'info'
    }]);
  };

  const totalProgress = (completedAgents.size / 5) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Analysis Workflow
                </h1>
                <p className="text-gray-600">
                  Generating comprehensive credit analysis for GMR Airport Limited
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                {!isRunning ? (
                  <Button onClick={startWorkflow} className="flex items-center gap-2">
                    <Play className="h-4 w-4" />
                    Start Analysis
                  </Button>
                ) : (
                  <Button variant="outline" onClick={resetWorkflow} className="flex items-center gap-2">
                    <RotateCcw className="h-4 w-4" />
                    Reset Workflow
                  </Button>
                )}
              </div>
            </div>
            
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm text-gray-600">{Math.round(totalProgress)}%</span>
              </div>
              <Progress value={totalProgress} className="h-3" />
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                <span>Pending</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                <span>Processing</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Completed</span>
              </div>
            </div>
          </div>
        </div>

        {/* Vertical Workflow */}
        <div className="space-y-6">
          {stages.map((stage, stageIndex) => (
            <div key={stage.id} className="flex flex-col items-center">
              {/* Stage Header */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-full font-semibold text-lg mb-6 shadow-lg">
                Stage {stageIndex + 1}: {stage.name}
              </div>

              {/* Agents - Conditional Layout */}
              {stage.layout === 'horizontal' ? (
                /* Horizontal Layout for Credit Analysis */
                <div className="flex flex-row gap-6 w-full justify-center items-start">
                  {stage.agents.map((agentName) => {
                    const isCompleted = completedAgents.has(agentName);
                    const isProcessing = processingAgents.has(agentName);
                    const getIcon = () => {
                      switch (agentName) {
                        case 'Market Analyst': return TrendingUp;
                        case 'Proposal Verification': return FileCheck;
                        case 'Company Profile': return Building;
                        case 'Financial Analyst': return Calculator;
                        case 'Credit Report Generator': return Download;
                        default: return Bot;
                      }
                    };
                    const Icon = getIcon();

                    return (
                      <div key={agentName} className="flex flex-col items-center">
                        {/* Arrow pointing to agent */}
                        {showArrow === `arrow-to-${agentName}` && (
                          <div className="animate-bounce mb-3">
                            <ArrowDown className="h-8 w-8 text-blue-500" />
                          </div>
                        )}

                        {/* Agent Card */}
                        <div 
                          className={`w-80 p-6 rounded-2xl border-2 transition-all duration-300 shadow-lg ${
                            isCompleted ? 'border-green-200 bg-green-50' : 
                            isProcessing ? 'border-blue-200 bg-blue-50 cursor-pointer hover:border-blue-300 hover:shadow-xl' : 
                            'border-gray-200 bg-white'
                          }`}
                          onClick={() => isProcessing && setSelectedAgentModal(agentName)}
                        >
                          <div className="flex items-center gap-4 mb-4">
                            <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${
                              isCompleted ? 'bg-green-100' : 
                              isProcessing ? 'bg-blue-100' : 
                              'bg-gray-100'
                            }`}>
                              <Icon className={`h-8 w-8 ${
                                isCompleted ? 'text-green-600' : 
                                isProcessing ? 'text-blue-600' : 
                                'text-gray-400'
                              }`} />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-bold text-lg text-gray-900">{agentName}</h3>
                              <Badge variant="outline" className={`mt-1 ${
                                isCompleted ? 'border-green-200 text-green-700' : 
                                isProcessing ? 'border-blue-200 text-blue-700' : 
                                'border-gray-200 text-gray-600'
                              }`}>
                                {isCompleted ? '✓ Completed' : isProcessing ? 'Processing...' : 'Pending'}
                              </Badge>
                            </div>
                          </div>
                          {isCompleted && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedAgentForResponse(agentName)}
                              className="w-full"
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View Analysis
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* Vertical Layout for other stages */
                <div className="space-y-6 w-full">
                  {stage.agents.map((agentName) => {
                    const isCompleted = completedAgents.has(agentName);
                    const isProcessing = processingAgents.has(agentName);
                    const getIcon = () => {
                      switch (agentName) {
                        case 'Market Analyst': return TrendingUp;
                        case 'Proposal Verification': return FileCheck;
                        case 'Company Profile': return Building;
                        case 'Financial Analyst': return Calculator;
                        case 'Credit Report Generator': return Download;
                        default: return Bot;
                      }
                    };
                    const Icon = getIcon();

                    return (
                      <div key={agentName} className="flex flex-col items-center">
                        {/* Arrow pointing to agent */}
                        {showArrow === `arrow-to-${agentName}` && (
                          <div className="animate-bounce mb-3">
                            <ArrowDown className="h-8 w-8 text-blue-500" />
                          </div>
                        )}

                        {/* Agent Card */}
                        <div 
                          className={`w-80 p-6 rounded-2xl border-2 transition-all duration-300 shadow-lg ${
                            isCompleted ? 'border-green-200 bg-green-50' : 
                            isProcessing ? 'border-blue-200 bg-blue-50 cursor-pointer hover:border-blue-300 hover:shadow-xl' : 
                            'border-gray-200 bg-white'
                          }`}
                          onClick={() => isProcessing && setSelectedAgentModal(agentName)}
                        >
                          <div className="flex items-center gap-4 mb-4">
                            <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${
                              isCompleted ? 'bg-green-100' : 
                              isProcessing ? 'bg-blue-100' : 
                              'bg-gray-100'
                            }`}>
                              <Icon className={`h-8 w-8 ${
                                isCompleted ? 'text-green-600' : 
                                isProcessing ? 'text-blue-600' : 
                                'text-gray-400'
                              }`} />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-bold text-lg text-gray-900">{agentName}</h3>
                              <Badge variant="outline" className={`mt-1 ${
                                isCompleted ? 'border-green-200 text-green-700' : 
                                isProcessing ? 'border-blue-200 text-blue-700' : 
                                'border-gray-200 text-gray-600'
                              }`}>
                                {isCompleted ? '✓ Completed' : isProcessing ? 'Processing...' : 'Pending'}
                              </Badge>
                            </div>
                          </div>
                          {isCompleted && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedAgentForResponse(agentName)}
                              className="w-full"
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View Analysis
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Arrow to next stage */}
              {stageIndex < stages.length - 1 && (
                <div className="my-8">
                  {showArrow === `arrow-stage-${stageIndex + 1}` ? (
                    <div className="animate-bounce">
                      <ArrowDown className="h-12 w-12 text-blue-500" />
                    </div>
                  ) : (
                    <ArrowDown className="h-8 w-8 text-gray-300" />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Chat Log Panel */}
        <div className="mt-8">
          <Card className="h-96">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Real-time Process Log
                </CardTitle>
                <Badge variant="outline">
                  {chatMessages.length} events
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <div className="h-80 overflow-y-auto space-y-2">
                {chatMessages.map((message) => (
                  <div key={message.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      message.type === 'success' ? 'bg-green-500' :
                      message.type === 'error' ? 'bg-red-500' :
                      message.type === 'warning' ? 'bg-yellow-500' :
                      'bg-blue-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-900">{message.agent}</span>
                        <Badge variant="secondary" className="text-xs">{message.stage}</Badge>
                        <span className="text-xs text-gray-500">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 font-mono leading-relaxed">{message.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modals */}
      {selectedAgentModal && (
        <AgentProcessingModal
          agentName={selectedAgentModal}
          isOpen={!!selectedAgentModal}
          onClose={() => setSelectedAgentModal(null)}
          steps={getAgentSteps(selectedAgentModal)}
          agentProgress={agentProgress[selectedAgentModal]}
        />
      )}

      {selectedAgentForResponse && (
        <FullResponseModal
          agentName={selectedAgentForResponse}
          isOpen={!!selectedAgentForResponse}
          onClose={() => setSelectedAgentForResponse(null)}
          content={agentResponses[selectedAgentForResponse] || 'Analysis content not available.'}
        />
      )}
    </div>
  );
};