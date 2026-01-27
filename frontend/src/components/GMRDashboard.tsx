import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Building2, 
  FileText, 
  Activity,
  Plus,
  RefreshCw,
  BarChart3,
  PieChart,
  Clock,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { formatNumber, getStatusColor, getCreditRatingColor } from '@/lib/utils';
import { GMRAnalysisSession, SystemStatistics, AgentPerformanceMetrics } from '@/types/gmr';
import { gmrApiService, StartAnalysisRequest, AnalysisStatusResponse } from '@/lib/gmrApiService';

// Import components
import { WorkflowVisualization } from './WorkflowVisualization.js';
import { AnalyticsView } from './AnalyticsView.js';
import { NewSessionModal } from './NewSessionModal.js';

interface GMRDashboardProps {
  onSessionSelect?: (sessionId: string) => void;
}

// Mock data - in real app this would come from API
const mockSessions: GMRAnalysisSession[] = [
  {
    session_metadata: {
      session_id: "CCRA-2025101501",
      company_name: "GMR Airports Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-15T10:30:00Z",
      processing_time_seconds: 21600, // 6 hours
      submission_date: "2025-10-15T04:30:00Z",
      status: "pending",
      system_version: "2.0.0",
      analyst_name: "Senior Credit Analyst",
      priority_level: "high"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101502",
      company_name: "Tata Consultancy Services",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-15T16:45:00Z",
      processing_time_seconds: 24300, // 6.75 hours
      submission_date: "2025-10-15T10:00:00Z",
      status: "processing",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101503",
      company_name: "HDFC Bank Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-15T22:15:00Z",
      processing_time_seconds: 27000, // 7.5 hours
      submission_date: "2025-10-15T14:45:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Rajesh Kumar",
      priority_level: "high"
    },
    comprehensive_results: {
      final_credit_rating: "AAA",
      risk_assessment: "LOW",
      recommendation: "APPROVE",
      confidence_score: 89.5,
      key_decision_factors: [
        "Leading private sector bank with strong market share",
        "Robust asset quality and provisioning coverage",
        "Digital banking initiatives driving customer growth"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 95,
      analysis_confidence: 89.5,
      system_performance_score: 92,
      processing_efficiency: 88,
      error_rate: 0.02
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101504",
      company_name: "Infosys Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-16T06:30:00Z",
      processing_time_seconds: 25200, // 7 hours
      submission_date: "2025-10-15T23:30:00Z",
      status: "pending",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101505",
      company_name: "Bharti Airtel Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-16T14:20:00Z",
      processing_time_seconds: 28800, // 8 hours
      submission_date: "2025-10-16T06:20:00Z",
      status: "failed",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 1.0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101506",
      company_name: "ITC Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-16T21:45:00Z",
      processing_time_seconds: 26100, // 7.25 hours
      submission_date: "2025-10-16T14:30:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Meera Gupta",
      priority_level: "low"
    },
    comprehensive_results: {
      final_credit_rating: "A",
      risk_assessment: "LOW",
      recommendation: "APPROVE",
      confidence_score: 88.9,
      key_decision_factors: [
        "Diversified FMCG portfolio with strong brands",
        "Sustainable business practices and ESG compliance",
        "Consistent dividend payments and cash generation"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 94,
      analysis_confidence: 88.9,
      system_performance_score: 91,
      processing_efficiency: 87,
      error_rate: 0.02
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101507",
      company_name: "Asian Paints Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-17T05:15:00Z",
      processing_time_seconds: 27600, // 7.67 hours
      submission_date: "2025-10-16T21:30:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Arjun Reddy",
      priority_level: "medium"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 87.6,
      key_decision_factors: [
        "Market leader in decorative paints segment",
        "Strong distribution network and brand equity",
        "Healthy margins and return on capital employed"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 92,
      analysis_confidence: 87.6,
      system_performance_score: 89,
      processing_efficiency: 85,
      error_rate: 0.03
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101508",
      company_name: "Larsen & Toubro Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-17T13:30:00Z",
      processing_time_seconds: 29700, // 8.25 hours
      submission_date: "2025-10-17T05:15:00Z",
      status: "processing",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "high"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101509",
      company_name: "Hindustan Unilever Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-17T20:45:00Z",
      processing_time_seconds: 26400, // 7.33 hours
      submission_date: "2025-10-17T13:30:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Rohit Jain",
      priority_level: "low"
    },
    comprehensive_results: {
      final_credit_rating: "AA",
      risk_assessment: "LOW",
      recommendation: "APPROVE",
      confidence_score: 92.1,
      key_decision_factors: [
        "Leading FMCG company with diverse product portfolio",
        "Strong rural and urban market penetration",
        "Consistent profitability and market share gains"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 96,
      analysis_confidence: 92.1,
      system_performance_score: 94,
      processing_efficiency: 91,
      error_rate: 0.015
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101510",
      company_name: "ICICI Bank Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-18T04:00:00Z",
      processing_time_seconds: 25800, // 7.17 hours
      submission_date: "2025-10-17T20:45:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Neha Agarwal",
      priority_level: "high"
    },
    comprehensive_results: {
      final_credit_rating: "A",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 86.8,
      key_decision_factors: [
        "Strong retail banking franchise and digital capabilities",
        "Improving asset quality metrics",
        "Diversified revenue streams across banking segments"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 93,
      analysis_confidence: 86.8,
      system_performance_score: 90,
      processing_efficiency: 88,
      error_rate: 0.02
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101511",
      company_name: "Wipro Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-18T11:15:00Z",
      processing_time_seconds: 26700, // 7.42 hours
      submission_date: "2025-10-18T04:00:00Z",
      status: "pending",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101512",
      company_name: "Maruti Suzuki India Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-18T19:30:00Z",
      processing_time_seconds: 29400, // 8.17 hours
      submission_date: "2025-10-18T11:15:00Z",
      status: "processing",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101513",
      company_name: "Bajaj Finance Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-19T02:45:00Z",
      processing_time_seconds: 26100, // 7.25 hours
      submission_date: "2025-10-18T19:30:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Pooja Agrawal",
      priority_level: "high"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 80.7,
      key_decision_factors: [
        "Leading NBFC with diversified lending portfolio",
        "Strong digital platform and customer acquisition",
        "Credit risk concentration in consumer finance"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 87,
      analysis_confidence: 80.7,
      system_performance_score: 84,
      processing_efficiency: 81,
      error_rate: 0.045
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101514",
      company_name: "UltraTech Cement Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-19T10:00:00Z",
      processing_time_seconds: 25500, // 7.08 hours
      submission_date: "2025-10-19T02:45:00Z",
      status: "failed",
      system_version: "2.0.0",
      analyst_name: "Credit Analyst",
      priority_level: "medium"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 1.0
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101515",
      company_name: "Mahindra & Mahindra Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-19T17:15:00Z",
      processing_time_seconds: 26400, // 7.33 hours
      submission_date: "2025-10-19T10:00:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Sunita Rao",
      priority_level: "low"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 79.2,
      key_decision_factors: [
        "Diversified automotive and farm equipment manufacturer",
        "Strong presence in utility vehicle segment",
        "Rural market dependency and cyclical nature"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 86,
      analysis_confidence: 79.2,
      system_performance_score: 83,
      processing_efficiency: 80,
      error_rate: 0.05
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101516",
      company_name: "Tech Mahindra Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-20T00:30:00Z",
      processing_time_seconds: 26100, // 7.25 hours
      submission_date: "2025-10-19T17:15:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Amit Joshi",
      priority_level: "medium"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 81.4,
      key_decision_factors: [
        "IT services provider with telecom sector focus",
        "Digital transformation and 5G opportunities",
        "Client concentration and margin pressures"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 88,
      analysis_confidence: 81.4,
      system_performance_score: 85,
      processing_efficiency: 82,
      error_rate: 0.04
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101517",
      company_name: "Axis Bank Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-20T07:45:00Z",
      processing_time_seconds: 25800, // 7.17 hours
      submission_date: "2025-10-20T00:30:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Divya Singh",
      priority_level: "high"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 84.1,
      key_decision_factors: [
        "Private sector bank with improving metrics",
        "Strong corporate banking and retail presence",
        "Asset quality concerns in certain segments"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 91,
      analysis_confidence: 84.1,
      system_performance_score: 88,
      processing_efficiency: 86,
      error_rate: 0.03
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101518",
      company_name: "JSW Steel Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-20T15:00:00Z",
      processing_time_seconds: 25200, // 7 hours
      submission_date: "2025-10-20T08:00:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Kiran Kumar",
      priority_level: "medium"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "HIGH",
      recommendation: "REVIEW_REQUIRED",
      confidence_score: 76.8,
      key_decision_factors: [
        "Leading steel manufacturer with integrated operations",
        "Cyclical steel industry with commodity price volatility",
        "High capital intensity and debt levels"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 85,
      analysis_confidence: 76.8,
      system_performance_score: 82,
      processing_efficiency: 79,
      error_rate: 0.055
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101519",
      company_name: "Kotak Mahindra Bank Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-20T22:15:00Z",
      processing_time_seconds: 26400, // 7.33 hours
      submission_date: "2025-10-20T15:00:00Z",
      status: "completed",
      system_version: "2.0.0",
      analyst_name: "Rashmi Verma",
      priority_level: "high"
    },
    comprehensive_results: {
      final_credit_rating: "BBB",
      risk_assessment: "MEDIUM",
      recommendation: "CONDITIONAL_APPROVAL",
      confidence_score: 85.6,
      key_decision_factors: [
        "Private sector bank with diversified services",
        "Strong capital adequacy and asset quality",
        "Growing retail and corporate banking segments"
      ]
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 92,
      analysis_confidence: 85.6,
      system_performance_score: 89,
      processing_efficiency: 87,
      error_rate: 0.025
    }
  },
  {
    session_metadata: {
      session_id: "CCRA-2025101520",
      company_name: "Adani Enterprises Limited",
      analysis_type: "comprehensive_credit_analysis",
      processing_date: "2025-10-21T05:30:00Z",
      processing_time_seconds: 27900, // 7.75 hours
      submission_date: "2025-10-20T22:15:00Z",
      status: "processing",
      system_version: "2.0.0",
      analyst_name: "Rahul Sharma",
      priority_level: "urgent"
    },
    detailed_agent_responses: {},
    processing_timeline: [],
    quality_metrics: {
      data_completeness_score: 0,
      analysis_confidence: 0,
      system_performance_score: 0,
      processing_efficiency: 0,
      error_rate: 0
    }
  }
];

const mockSystemStats: SystemStatistics = {
  total_analyses_completed: 15847,
  total_processing_time_hours: 3842.7,
  average_session_duration_minutes: 435.2, // ~7.25 hours average
  success_rate: 94.8, // Adjusted for some failed sessions
  active_sessions: 12, // More active sessions with processing/pending
  queue_length: 18
};

const mockAgentPerformance: AgentPerformanceMetrics[] = [
  {
    agent_type: "market_analyst",
    agent_name: "Market Analyst",
    total_executions: 15847,
    success_rate: 98.7,
    average_processing_time_seconds: 8640, // ~2.4 hours
    efficiency_score: 95,
    recent_performance_trend: "improving",
    last_execution: "2025-10-21T05:30:00Z"
  },
  {
    agent_type: "financial_analyst",
    agent_name: "Financial Analyst",
    total_executions: 15847,
    success_rate: 97.1,
    average_processing_time_seconds: 9720, // ~2.7 hours
    efficiency_score: 93,
    recent_performance_trend: "stable",
    last_execution: "2025-10-21T05:28:00Z"
  },
  {
    agent_type: "proposal_verification",
    agent_name: "Proposal Verification",
    total_executions: 15847,
    success_rate: 96.8,
    average_processing_time_seconds: 7200, // ~2 hours
    efficiency_score: 94,
    recent_performance_trend: "improving",
    last_execution: "2025-10-21T05:26:00Z"
  },
  {
    agent_type: "company_profile",
    agent_name: "Company Profile",
    total_executions: 15847,
    success_rate: 95.2,
    average_processing_time_seconds: 6300, // ~1.75 hours
    efficiency_score: 92,
    recent_performance_trend: "stable",
    last_execution: "2025-10-21T05:25:00Z"
  },
  {
    agent_type: "credit_report_generator",
    agent_name: "Credit Report Generator",
    total_executions: 15847,
    success_rate: 99.1,
    average_processing_time_seconds: 3600, // ~1 hour
    efficiency_score: 98,
    recent_performance_trend: "improving",
    last_execution: "2025-10-21T05:32:00Z"
  }
];

export const GMRDashboard: React.FC<GMRDashboardProps> = ({ onSessionSelect }) => {
  const [currentView, setCurrentView] = useState<'overview' | 'workflow' | 'analytics'>('overview');
  const [sessions, setSessions] = useState<GMRAnalysisSession[]>(mockSessions);
  const [systemStats] = useState<SystemStatistics>(mockSystemStats);
  const [isNewSessionModalOpen, setIsNewSessionModalOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedSession, setSelectedSession] = useState<GMRAnalysisSession | null>(null);
  const [isStartingAnalysis, setIsStartingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatusResponse | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  const fetchAnalysisStatus = useCallback(async () => {
    try {
      const status = await gmrApiService.getAnalysisStatus();
      setAnalysisStatus(status);
      setStatusError(null);
      console.log('🔄 Analysis status updated:', status);
    } catch (error) {
      console.error('Failed to fetch analysis status:', error);
      setStatusError(error instanceof Error ? error.message : 'Failed to fetch analysis status');
    }
  }, []);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await fetchAnalysisStatus();
    } finally {
      setIsRefreshing(false);
    }
  }, [fetchAnalysisStatus]);

  useEffect(() => {
    fetchAnalysisStatus();
    const interval = setInterval(fetchAnalysisStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchAnalysisStatus]);

  const handleNewSession = () => {
    setIsNewSessionModalOpen(true);
  };

  const handleSessionClick = (session: GMRAnalysisSession) => {
    setSelectedSession(session);
    setCurrentView('workflow');
    onSessionSelect?.(session.session_metadata.session_id);
  };

  // Quick stats cards data
  const quickStats = [
    {
      title: "Total Analyses",
      value: formatNumber(systemStats.total_analyses_completed),
      icon: <FileText className="h-5 w-5" />,
      trend: "+12.5%",
      trendUp: true
    },
    {
      title: "Success Rate",
      value: `${systemStats.success_rate}%`,
      icon: <CheckCircle className="h-5 w-5" />,
      trend: "+0.3%",
      trendUp: true
    },
    {
      title: "Active Sessions",
      value: systemStats.active_sessions.toString(),
      icon: <Activity className="h-5 w-5" />,
      trend: "Real-time",
      trendUp: null
    },
    {
      title: "Avg Duration",
      value: `${systemStats.average_session_duration_minutes}m`,
      icon: <Clock className="h-5 w-5" />,
      trend: "-2.1%",
      trendUp: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Corporate Credit Risk Analysis</h1>
                <p className="text-sm text-gray-600">AI-Powered Financial Analytics Platform</p>
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
            <Button size="sm" onClick={handleNewSession}>
              <Plus className="h-4 w-4 mr-2" />
              New Analysis
            </Button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <Tabs value={currentView} onValueChange={(value: any) => setCurrentView(value)}>
          <TabsList className="grid w-full grid-cols-3 lg:w-fit">
            <TabsTrigger value="overview" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="workflow" className="gap-2">
              <Activity className="h-4 w-4" />
              Workflow
            </TabsTrigger>
            <TabsTrigger value="analytics" className="gap-2">
              <PieChart className="h-4 w-4" />
              Analytics
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Main Content */}
      <main className="px-6 py-6">
        <Tabs value={currentView} onValueChange={(value: any) => setCurrentView(value)}>
          <TabsContent value="overview" className="space-y-6">
            {/* Recent Sessions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Analysis Sessions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sessions.slice(0, 4).map((session) => (
                    <div 
                      key={session.session_metadata.session_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleSessionClick(session)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Building2 className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{session.session_metadata.company_name}</h4>
                          <p className="text-sm text-gray-600">{session.session_metadata.session_id}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        {session.comprehensive_results?.final_credit_rating && (
                          <Badge className={getCreditRatingColor(session.comprehensive_results.final_credit_rating)}>
                            {session.comprehensive_results.final_credit_rating}
                          </Badge>
                        )}
                        <Badge className={getStatusColor(session.session_metadata.status)}>
                          {session.session_metadata.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(session.session_metadata.processing_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="workflow">
            {selectedSession ? (
              <WorkflowVisualization 
                session={selectedSession}
                onBack={() => setCurrentView('overview')}
              />
            ) : (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Session Selected</h3>
                <p className="text-gray-600 mb-4">Select a session from the overview to view its workflow visualization</p>
                <Button onClick={() => setCurrentView('overview')}>
                  Go to Overview
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsView 
              sessions={sessions}
              systemStats={systemStats}
              agentPerformance={mockAgentPerformance}
            />
          </TabsContent>
        </Tabs>
      </main>

      {/* New Session Modal */}
      {isNewSessionModalOpen && (
        <NewSessionModal 
          isOpen={isNewSessionModalOpen}
          onClose={() => {
            setIsNewSessionModalOpen(false);
            setAnalysisError(null);
          }}
          onSubmit={async (sessionData: StartAnalysisRequest) => {
            try {
              setIsStartingAnalysis(true);
              setAnalysisError(null);
              
              console.log('Starting analysis with data:', sessionData);
              
              // Call the API to start analysis
              const response = await gmrApiService.startAnalysis(sessionData);
              
              console.log('Analysis started successfully:', response);

              const processingTimestamp = response.start_time || response.timestamp || new Date().toISOString();

              const newSession: GMRAnalysisSession = {
                session_metadata: {
                  session_id: response.session_id,
                  company_name: response.company_name || sessionData.company_name,
                  analysis_type: 'comprehensive_credit_analysis',
                  processing_date: processingTimestamp,
                  processing_time_seconds: 0,
                  submission_date: processingTimestamp,
                  status: (response.status as 'pending' | 'processing' | 'completed' | 'failed') || 'pending',
                  system_version: '2.0.0',
                  analyst_name: response.analyst_name || sessionData.analyst_name || 'Unknown Analyst',
                  priority_level: (response.priority_level as 'low' | 'medium' | 'high' | 'urgent') || sessionData.priority_level || 'medium'
                },
                detailed_agent_responses: {},
                processing_timeline: [],
                quality_metrics: {
                  data_completeness_score: 0,
                  analysis_confidence: 0,
                  system_performance_score: 0,
                  processing_efficiency: 0,
                  error_rate: 0
                }
              };

              setSessions(prev => [newSession, ...prev]);
              setSelectedSession(newSession);
              await fetchAnalysisStatus();
              setCurrentView('workflow');
              
              // Close modal and show success
              setIsNewSessionModalOpen(false);
              
              // Simple success notice for the analyst
              alert('Analysis has been kicked off. You can monitor progress from the dashboard.');
              
            } catch (error) {
              console.error('Failed to start analysis:', error);
              setAnalysisError(error instanceof Error ? error.message : 'Failed to start analysis');
            } finally {
              setIsStartingAnalysis(false);
            }
          }}
          isLoading={isStartingAnalysis}
          error={analysisError}
        />
      )}
    </div>
  );
};

export default GMRDashboard;