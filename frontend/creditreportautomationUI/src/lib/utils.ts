import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = "INR"): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatNumber(num: number): string {
  if (num >= 10000000) {
    return (num / 10000000).toFixed(1) + 'Cr';
  } else if (num >= 100000) {
    return (num / 100000).toFixed(1) + 'L';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    return `${Math.round(seconds / 60)}m`;
  } else {
    return `${Math.round(seconds / 3600)}h`;
  }
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function getStatusColor(status: string): string {
  const colors = {
    completed: 'text-green-600 bg-green-50 border-green-200',
    processing: 'text-blue-600 bg-blue-50 border-blue-200',
    pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    failed: 'text-red-600 bg-red-50 border-red-200',
    error: 'text-red-600 bg-red-50 border-red-200'
  };
  return colors[status as keyof typeof colors] || colors.pending;
}

export function getRiskColor(risk: string): string {
  const colors = {
    LOW: 'text-green-600 bg-green-50 border-green-200',
    MEDIUM: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
    CRITICAL: 'text-red-600 bg-red-50 border-red-200'
  };
  return colors[risk as keyof typeof colors] || colors.MEDIUM;
}

export function getCreditRatingColor(rating: string): string {
  const colors = {
    AAA: 'text-green-700 bg-green-100 border-green-300',
    AA: 'text-green-600 bg-green-50 border-green-200',
    A: 'text-blue-600 bg-blue-50 border-blue-200',
    BBB: 'text-blue-500 bg-blue-50 border-blue-200',
    BB: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    B: 'text-orange-600 bg-orange-50 border-orange-200',
    CCC: 'text-red-500 bg-red-50 border-red-200',
    CC: 'text-red-600 bg-red-50 border-red-200',
    C: 'text-red-700 bg-red-100 border-red-300',
    D: 'text-red-800 bg-red-100 border-red-400'
  };
  return colors[rating as keyof typeof colors] || colors.BBB;
}

export function getAgentIcon(agentType: string): string {
  const icons = {
    market_analyst: '📈',
    proposal_verification: '✅',
    company_profile: '🏢',
    financial_analysis: '💰',
    annexures_coordination: '📋',
    pdf_generator: '📄'
  };
  return icons[agentType as keyof typeof icons] || '🤖';
}

export function getAgentColor(agentType: string): string {
  const colors = {
    market_analyst: 'border-blue-200 bg-blue-50 text-blue-700',
    proposal_verification: 'border-green-200 bg-green-50 text-green-700',
    company_profile: 'border-purple-200 bg-purple-50 text-purple-700',
    financial_analysis: 'border-orange-200 bg-orange-50 text-orange-700',
    annexures_coordination: 'border-red-200 bg-red-50 text-red-700',
    pdf_generator: 'border-gray-200 bg-gray-50 text-gray-700'
  };
  return colors[agentType as keyof typeof colors] || 'border-gray-200 bg-gray-50 text-gray-700';
}

export function calculateProgress(stages: any[]): number {
  if (!stages || stages.length === 0) return 0;
  
  const totalProgress = stages.reduce((sum, stage) => sum + (stage.progress_percentage || 0), 0);
  return Math.round(totalProgress / stages.length);
}

export function generateSessionId(): string {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substr(2, 5);
  return `GMR-${timestamp}-${randomPart}`.toUpperCase();
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function downloadFile(content: string, filename: string, type: string = 'text/plain'): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  } else {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'absolute';
    textArea.style.left = '-999999px';
    document.body.prepend(textArea);
    textArea.select();
    
    try {
      document.execCommand('copy');
    } catch (error) {
      console.error('Failed to copy text: ', error);
    } finally {
      textArea.remove();
    }
    
    return Promise.resolve();
  }
}