// GMR Analysis API Service
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';

export interface StartAnalysisRequest {
  company_name: string;
  analyst_name?: string;
  priority_level?: 'low' | 'medium' | 'high' | 'urgent';
  description?: string;
  documents?: File[];
  jsonFile?: File | null;
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
      
      // Create FormData to send the JSON file
      const formData = new FormData();
      
      // If no JSON file provided, create one from the request data
      let jsonFile = request.jsonFile;
      if (!jsonFile) {
        const jsonData = {
          company_name: request.company_name,
          analyst_name: request.analyst_name || 'Credit Analyst',
          priority_level: request.priority_level || 'medium',
          description: request.description || 'Credit analysis',
          analysis_type: 'comprehensive_credit_analysis',
          timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
        jsonFile = new File([blob], 'analysis-config.json', { type: 'application/json' });
        console.log('📝 Created default JSON config:', jsonData);
      }
      
      formData.append('json_file', jsonFile);
      
      const response = await fetch(`${this.apiBaseUrl}/api/analysis/start`, {
        method: 'POST',
        body: formData
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