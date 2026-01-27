import React from 'react';

// GMR Credit Analysis Data Types
export interface GMRAnalysisSession {
  session_metadata: SessionMetadata;
  market_analysis?: MarketAnalysis;
  financial_analysis?: FinancialAnalysis;
  report_generation?: ReportGeneration;
  comprehensive_results?: ComprehensiveResults;
  detailed_agent_responses: Record<string, AgentResponse>;
  processing_timeline: ProcessingTimeline[];
  quality_metrics: QualityMetrics;
}

export interface SessionMetadata {
  session_id: string;
  company_name: string;
  analysis_type: "comprehensive_credit_analysis";
  processing_date: string;
  processing_time_seconds?: number;
  submission_date: string;
  status: "pending" | "processing" | "completed" | "failed";
  system_version: string;
  analyst_name?: string;
  priority_level: "low" | "medium" | "high" | "urgent";
}

export interface MarketAnalysis {
  sentiment_score: number;
  articles_processed: number;
  processing_time_seconds: number;
  sentiment_breakdown: {
    positive: number;
    negative: number;
    neutral: number;
  };
  key_insights: string[];
  news_coverage_score: number;
  market_trends: MarketTrend[];
  risk_indicators: RiskIndicator[];
  output_files: string[];
}

export interface MarketTrend {
  category: string;
  trend_direction: "up" | "down" | "stable";
  confidence: number;
  impact_level: "low" | "medium" | "high";
  description: string;
}

export interface RiskIndicator {
  type: "regulatory" | "market" | "operational" | "financial";
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  source: string;
  confidence: number;
}

export interface FinancialAnalysis {
  agents_completed: number;
  total_agents: 4;
  completion_rate: number;
  total_processing_time_seconds: number;
  individual_agent_responses: {
    proposal_verification: AgentAnalysis;
    company_profile: AgentAnalysis;
    financial_analysis: AgentAnalysis;
    annexures_coordination: AgentAnalysis;
  };
  consolidated_findings: ConsolidatedFindings;
}

export interface AgentAnalysis {
  agent_name: string;
  processing_time_seconds: number;
  status: "completed" | "failed" | "processing";
  key_findings: string[];
  risk_factors: string[];
  recommendations: string[];
  confidence_score: number;
  output_files: string[];
}

export interface ConsolidatedFindings {
  overall_financial_health: "excellent" | "good" | "fair" | "poor" | "critical";
  credit_worthiness_score: number;
  debt_to_equity_ratio: number;
  liquidity_ratio: number;
  profitability_metrics: {
    roa: number;
    roe: number;
    profit_margin: number;
  };
  growth_indicators: {
    revenue_growth: number;
    asset_growth: number;
    market_share_trend: "increasing" | "stable" | "decreasing";
  };
}

export interface ReportGeneration {
  html_generated: boolean;
  pdf_generated: boolean;
  processing_time_seconds: number;
  file_sizes: {
    html_bytes: number;
    pdf_bytes: number;
  };
  generation_timestamp: string;
  output_files: string[];
  generation_quality_score: number;
}

export interface ComprehensiveResults {
  final_credit_rating: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC" | "CC" | "C" | "D";
  risk_assessment: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  recommendation: "APPROVE" | "CONDITIONAL_APPROVAL" | "REVIEW_REQUIRED" | "DECLINE";
  confidence_score: number;
  key_decision_factors: string[];
  conditions_required?: string[];
  monitoring_requirements?: string[];
}

export interface AgentResponse {
  agent_name: string;
  agent_type: "market_analyst" | "proposal_verification" | "company_profile" | "financial_analysis" | "annexures_coordination" | "pdf_generator";
  analysis: string;
  timestamp: string;
  processing_time_seconds: number;
  status: "completed" | "failed" | "processing" | "pending";
  output_files: string[];
  key_metrics?: Record<string, number | string>;
  error_message?: string;
}

export interface ProcessingTimeline {
  timestamp: string;
  stage: "market_analysis" | "financial_orchestration" | "report_generation";
  agent: string;
  event: "started" | "progress" | "completed" | "failed";
  message: string;
  progress_percentage?: number;
  details?: Record<string, any>;
}

export interface QualityMetrics {
  data_completeness_score: number;
  analysis_confidence: number;
  system_performance_score: number;
  processing_efficiency: number;
  error_rate: number;
  user_satisfaction_score?: number;
}

// Dashboard specific types
export interface GMRDashboardData {
  recent_sessions: GMRAnalysisSession[];
  system_statistics: SystemStatistics;
  agent_performance: AgentPerformanceMetrics[];
  trending_companies: TrendingCompany[];
}

export interface SystemStatistics {
  total_analyses_completed: number;
  total_processing_time_hours: number;
  average_session_duration_minutes: number;
  success_rate: number;
  active_sessions: number;
  queue_length: number;
}

export interface AgentPerformanceMetrics {
  agent_type: string;
  agent_name: string;
  total_executions: number;
  success_rate: number;
  average_processing_time_seconds: number;
  efficiency_score: number;
  recent_performance_trend: "improving" | "stable" | "declining";
  last_execution: string;
}

export interface TrendingCompany {
  company_name: string;
  analysis_count: number;
  latest_rating: string;
  rating_trend: "upgraded" | "stable" | "downgraded";
  last_analysis_date: string;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
}

// UI Component Types
export interface WorkflowStage {
  id: string;
  name: string;
  description: string;
  agents: Agent[];
  estimatedTime: string;
  status: "pending" | "running" | "completed" | "failed";
}

export interface Agent {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  icon: React.ComponentType<{ className?: string }>;
}

export interface ChatMessage {
  id: string;
  timestamp: string;
  agent: string;
  stage: string;
  message: string;
  type: "info" | "success" | "warning" | "error" | "progress";
  progress?: number;
  attachments?: string[];
  metadata?: Record<string, any>;
}

// Filter and Search Types
export interface SessionFilter {
  status?: ("pending" | "processing" | "completed" | "failed")[];
  date_range?: {
    start: string;
    end: string;
  };
  company_name?: string;
  analyst_name?: string;
  priority_level?: ("low" | "medium" | "high" | "urgent")[];
  credit_rating?: string[];
}

export interface SearchCriteria {
  query: string;
  filters: SessionFilter;
  sort_by: "date" | "company" | "status" | "rating" | "processing_time";
  sort_order: "asc" | "desc";
  page: number;
  limit: number;
}

// Export alias for easy importing
export type AnalysisSession = GMRAnalysisSession;