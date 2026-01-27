import { useState, useCallback } from 'react';
import { azureBlobService, type UploadProgress, type BlobFile } from '../lib/azureBlobService';

interface UseAzureBlobReturn {
  uploading: boolean;
  uploadProgress: UploadProgress | null;
  uploadFile: (file: File, blobName?: string) => Promise<string>;
  downloadFile: (blobName: string) => Promise<Blob>;
  getBlobText: (blobName: string) => Promise<string>;
  deleteFile: (blobName: string) => Promise<void>;
  listFiles: (prefix?: string) => Promise<BlobFile[]>;
  error: string | null;
  isConfigured: boolean;
}

/**
 * React hook for interacting with Azure Blob Storage
 */
export const useAzureBlob = (): UseAzureBlobReturn => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = useCallback(async (file: File, blobName?: string): Promise<string> => {
    setUploading(true);
    setError(null);
    setUploadProgress(null);

    try {
      const url = await azureBlobService.uploadFile(file, blobName, (progress: UploadProgress) => {
        setUploadProgress(progress);
      });
      return url;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload file';
      setError(errorMessage);
      throw err;
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  }, []);

  const downloadFile = useCallback(async (blobName: string): Promise<Blob> => {
    setError(null);
    try {
      return await azureBlobService.downloadFile(blobName);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to download file';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const getBlobText = useCallback(async (blobName: string): Promise<string> => {
    setError(null);
    try {
      return await azureBlobService.getBlobText(blobName);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get blob text';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const deleteFile = useCallback(async (blobName: string): Promise<void> => {
    setError(null);
    try {
      await azureBlobService.deleteFile(blobName);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete file';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const listFiles = useCallback(async (prefix?: string): Promise<BlobFile[]> => {
    setError(null);
    try {
      return await azureBlobService.listFiles(prefix);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to list files';
      setError(errorMessage);
      throw err;
    }
  }, []);

  return {
    uploading,
    uploadProgress,
    uploadFile,
    downloadFile,
    getBlobText,
    deleteFile,
    listFiles,
    error,
    isConfigured: azureBlobService.isConfigured(),
  };
};
