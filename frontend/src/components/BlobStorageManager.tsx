import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAzureBlob } from '@/hooks/useAzureBlob';
import { type BlobFile } from '@/lib/azureBlobService';
import { 
  Upload, 
  Download, 
  Trash2, 
  RefreshCw,
  FileText,
  File,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

export const BlobStorageManager: React.FC = () => {
  const { listFiles, uploadFile, deleteFile, uploading, uploadProgress, error, isConfigured } = useAzureBlob();
  const [files, setFiles] = useState<BlobFile[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isConfigured) {
      loadFiles();
    }
  }, [isConfigured]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const fileList = await listFiles();
      setFiles(fileList);
    } catch (err) {
      console.error('Failed to load files:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await uploadFile(file);
      alert(`File "${file.name}" uploaded successfully!`);
      await loadFiles();
    } catch (err) {
      alert(`Failed to upload file: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const handleDelete = async (fileName: string) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) return;

    try {
      await deleteFile(fileName);
      alert(`File "${fileName}" deleted successfully!`);
      await loadFiles();
    } catch (err) {
      alert(`Failed to delete file: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (date?: Date): string => {
    if (!date) return 'Unknown';
    return new Date(date).toLocaleString();
  };

  if (!isConfigured) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-600" />
            Azure Blob Storage Not Configured
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-4">
            Azure Blob Storage is not configured. Please check your environment variables:
          </p>
          <ul className="list-disc list-inside space-y-2 text-sm text-gray-600">
            <li>VITE_AZURE_STORAGE_ACCOUNT_NAME</li>
            <li>VITE_AZURE_STORAGE_ACCOUNT_KEY</li>
            <li>VITE_AZURE_STORAGE_CONTAINER_NAME</li>
          </ul>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Azure Blob Storage Files
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadFiles}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="default" 
              size="sm" 
              disabled={uploading}
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <Upload className="h-4 w-4 mr-2" />
              {uploading ? `Uploading ${uploadProgress?.percentage || 0}%` : 'Upload File'}
            </Button>
            <input
              id="file-upload"
              type="file"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p>No files found in blob storage</p>
            <p className="text-sm">Upload files to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.name}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <File className="h-5 w-5 text-gray-400" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{file.name}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{formatFileSize(file.size)}</span>
                      <span>{formatDate(new Date(file.lastModified))}</span>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {file.name.endsWith('.pdf') ? 'PDF' : 
                     file.name.endsWith('.txt') ? 'TEXT' : 'FILE'}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(file.url, '_blank')}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(file.name)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
