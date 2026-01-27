// GMR Analysis API Service
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export interface StartAnalysisRequest {
  company_name: string;
  analyst_name?: string;
  priority_level?: 'low' | 'medium' | 'high' | 'urgent';
  description?: string;
  documents?: File[];
}

export interface StartAnalysisResponse {
  session_id: string;
  status: string;
  agents_executed?: Record<string, string>;
  files_uploaded?: string[];
  start_time?: string;
  end_time?: string;
  progress?: number;
  upload_summary?: Record<string, unknown>;
  [key: string]: any;
}

export interface AvailableAnalysisFile {
  filename: string;
  size: number;
  modified: string;
}

export interface BlobAnalysisFile {
  name: string;
  size: number;
  last_modified?: string;
}

export interface AnalysisStatusResponse {
  orchestration_available: boolean;
  analysis_outputs_available: boolean;
  available_analyses: AvailableAnalysisFile[];
  blob_files: BlobAnalysisFile[];
  timestamp: string;
  blob_error?: string;
  [key: string]: any;
}

/**
 * GMR Analysis API Service
 * Handles communication with the GMR analysis backend
 */
export class GMRApiService {
  private apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = API_BASE_URL;
    console.log('✅ GMR API Service initialized');
    console.log(`   API URL: ${this.apiBaseUrl}`);
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Start a new GMR analysis session
   */
  async startAnalysis(request: StartAnalysisRequest): Promise<StartAnalysisResponse> {
    try {
      console.log('🚀 Starting analysis for:', request.company_name);
      
      const response = await fetch(`${this.apiBaseUrl}/api/analysis/start`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json'
        }
      });

      const result = await this.handleResponse<StartAnalysisResponse>(response);
      console.log('✅ Analysis started successfully:', result);
      return result;
      
    } catch (error) {
      console.error('❌ Failed to start analysis:', error);
      throw error;
    }
  }

  /**
   * Get analysis status
   */
  async getAnalysisStatus(): Promise<AnalysisStatusResponse> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/analysis/status`);
      return this.handleResponse<AnalysisStatusResponse>(response);
    } catch (error) {
      console.error('❌ Failed to get analysis status:', error);
      throw error;
    }
  }

  /**
   * Get analysis results
   */
  async getAnalysisResults(sessionId: string): Promise<any> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/analysis/results/${sessionId}`);
      return this.handleResponse<any>(response);
    } catch (error) {
      console.error('❌ Failed to get analysis results:', error);
      throw error;
    }
  }

  /**
   * List all analysis sessions
   */
  async listAnalysisSessions(): Promise<any[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/analysis/sessions`);
      return this.handleResponse<any[]>(response);
    } catch (error) {
      console.error('❌ Failed to list analysis sessions:', error);
      throw error;
    }
  }

  /**
   * Check if service is available
   */
  isConfigured(): boolean {
    return !!this.apiBaseUrl;
  }
}

// Export singleton instance
export const gmrApiService = new GMRApiService();