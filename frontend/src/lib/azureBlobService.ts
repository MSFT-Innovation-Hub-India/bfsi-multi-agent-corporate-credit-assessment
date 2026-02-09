// Backend API URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://creditreport-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface BlobFile {
  name: string;
  url: string;
  size: number;
  lastModified: string;
  contentType?: string;
}

/**
 * Production-ready Azure Blob Storage Service
 * - Uses FastAPI backend for secure operations
 * - Short-lived SAS tokens (generated server-side)
 * - Streaming support for large files
 * - No credentials in frontend
 * - Comprehensive error handling
 */
export class AzureBlobService {
  private apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = API_BASE_URL;
    console.log('✅ Azure Blob Storage Service initialized');
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
   * Check if service is available
   */
  isConfigured(): boolean {
    return !!this.apiBaseUrl;
  }

  /**
   * List all files in the container
   * @param prefix - Optional prefix to filter files
   * @returns Array of blob metadata
   */
  async listFiles(prefix?: string): Promise<BlobFile[]> {
    try {
      console.log(`📋 Listing files${prefix ? ` with prefix: ${prefix}` : ''}...`);
      
      const url = new URL(`${this.apiBaseUrl}/api/blobs`);
      if (prefix) url.searchParams.set('prefix', prefix);
      
      const response = await fetch(url.toString());
      const data = await this.handleResponse<{ blobs: BlobFile[]; count: number }>(response);
      
      console.log(`✅ Listed ${data.count} file(s)`);
      return data.blobs;
    } catch (error) {
      console.error('❌ List files failed:', error);
      throw new Error(`Failed to list files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Upload a file to blob storage
   * @param file - File to upload
   * @param blobName - Optional custom blob name
   * @param onProgress - Optional progress callback
   * @returns URL of uploaded blob
   */
  async uploadFile(
    file: File,
    blobName?: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<string> {
    try {
      const fileName = blobName || file.name;
      console.log(`📤 Uploading: ${fileName} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
      
      const formData = new FormData();
      formData.append('file', file);
      if (blobName) formData.append('blob_name', blobName);
      
      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable && onProgress) {
            onProgress({
              loaded: e.loaded,
              total: e.total,
              percentage: Math.round((e.loaded / e.total) * 100)
            });
          }
        });
        
        xhr.addEventListener('load', async () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const data = JSON.parse(xhr.responseText);
            console.log(`✅ Upload complete: ${fileName}`);
            resolve(data.url);
          } else {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || 'Upload failed'));
          }
        });
        
        xhr.addEventListener('error', () => reject(new Error('Upload failed: Network error')));
        
        xhr.open('POST', `${this.apiBaseUrl}/api/blobs/upload`);
        xhr.send(formData);
      });
    } catch (error) {
      console.error('❌ Upload failed:', error);
      throw new Error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Download a file from blob storage
   * Uses backend streaming for efficient large file handling
   * @param blobName - Name of the blob to download
   * @returns Blob containing the file data
   */
  async downloadFile(blobName: string): Promise<Blob> {
    try {
      console.log(`📥 Downloading: ${blobName}`);
      
      // Use the /download endpoint which returns the actual file as blob
      const response = await fetch(`${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/download`);
      
      if (!response.ok) {
        // Try to get error details, but download endpoint doesn't return JSON errors
        if (response.status === 404) {
          throw new Error(`File not found: ${blobName}`);
        }
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      console.log(`✅ Download complete: ${blobName} (${(blob.size / 1024 / 1024).toFixed(2)} MB)`);
      return blob;
    } catch (error) {
      console.error(`❌ Download failed: ${blobName}`, error);
      throw new Error(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get blob content as text (for viewing in UI)
   * @param blobName - Name of the blob
   * @returns Text content of the blob
   */
  async getBlobText(blobName: string): Promise<string> {
    try {
      console.log(`📄 Getting text content: ${blobName}`);
      
      const response = await fetch(`${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/content`);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        if (response.status === 404) {
          throw new Error(`File not found: ${blobName}`);
        }
        throw new Error(error.detail || 'Failed to get content');
      }
      
      const data = await response.json();
      
      // Return text content directly
      if (data.encoding === 'base64') {
        // Decode base64 for binary files (though this may not be readable text)
        return atob(data.content);
      }
      
      return data.content;
    } catch (error) {
      console.error(`❌ Failed to get text content: ${blobName}`, error);
      throw new Error(`Failed to get content: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Trigger browser download for a blob
   * Uses direct streaming from backend for large files
   * @param blobName - Name of the blob to download
   * @param fileName - Optional custom filename for download
   */
  async triggerDownload(blobName: string, fileName?: string): Promise<void> {
    try {
      console.log(`📥 Triggering download: ${blobName}`);
      
      // Use backend streaming endpoint for efficient downloads
      const url = `${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/download`;
      
      const response = await fetch(url);
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || 'Download failed');
      }
      
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = fileName || blobName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
      
      console.log(`✅ Download triggered: ${blobName}`);
    } catch (error) {
      console.error(`❌ Download trigger failed: ${blobName}`, error);
      throw new Error(`Failed to trigger download: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Delete a file from blob storage
   * @param blobName - Name of the blob to delete
   */
  async deleteFile(blobName: string): Promise<void> {
    try {
      console.log(`🗑️ Deleting: ${blobName}`);
      
      const response = await fetch(`${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}`, {
        method: 'DELETE'
      });
      
      await this.handleResponse<{ message: string; blob_name: string }>(response);
      console.log(`✅ Deleted: ${blobName}`);
    } catch (error) {
      console.error(`❌ Delete failed: ${blobName}`, error);
      if (error instanceof Error && error.message.includes('404')) {
        throw new Error(`File not found: ${blobName}`);
      }
      throw new Error(`Delete failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check if a blob exists
   * @param blobName - Name of the blob to check
   * @returns True if exists, false otherwise
   */
  async blobExists(blobName: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/exists`);
      const data = await this.handleResponse<{ blob_name: string; exists: boolean }>(response);
      return data.exists;
    } catch (error) {
      console.error(`Error checking blob existence: ${blobName}`, error);
      return false;
    }
  }

  /**
   * Get the public URL for a blob
   * @param blobName - Name of the blob
   * @returns Public URL
   */
  getFileUrl(blobName: string): string {
    // This returns the blob URL without SAS token - backend will generate SAS when needed
    return `${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/download`;
  }

  /**
   * Get a short-lived SAS URL for direct blob access
   * Useful for embedding in <img> or <video> tags
   * @param blobName - Name of the blob
   * @param expiryMinutes - SAS token expiry time (default: 60 minutes)
   * @returns SAS URL with short-lived token
   */
  async getSasUrl(blobName: string, expiryMinutes: number = 60): Promise<string> {
    try {
      const url = new URL(`${this.apiBaseUrl}/api/blobs/${encodeURIComponent(blobName)}/sas`);
      url.searchParams.set('expiry_minutes', expiryMinutes.toString());
      
      const response = await fetch(url.toString());
      const data = await this.handleResponse<{ sas_url: string; expires_at: string }>(response);
      
      console.log(`✅ Generated SAS URL for: ${blobName} (expires: ${data.expires_at})`);
      return data.sas_url;
    } catch (error) {
      console.error(`❌ Failed to generate SAS URL: ${blobName}`, error);
      throw new Error(`Failed to generate SAS URL: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

// Export singleton instance
export const azureBlobService = new AzureBlobService();
