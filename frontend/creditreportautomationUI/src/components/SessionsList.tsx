import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  Filter, 
  Calendar,
  Building2,
  User,
  Clock,
  TrendingUp,
  FileText,
  Plus
} from 'lucide-react';
import { GMRAnalysisSession } from '@/types/gmr';
import { formatDuration, getStatusColor, getCreditRatingColor } from '@/lib/utils';

interface SessionsListProps {
  sessions: GMRAnalysisSession[];
  onSessionClick: (session: GMRAnalysisSession) => void;
  onNewSession: () => void;
}

export const SessionsList: React.FC<SessionsListProps> = ({ 
  sessions, 
  onSessionClick, 
  onNewSession 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'company' | 'status'>('date');

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = session.session_metadata.company_name
      .toLowerCase()
      .includes(searchQuery.toLowerCase()) ||
      session.session_metadata.session_id
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
      session.session_metadata.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const sortedSessions = [...filteredSessions].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.session_metadata.processing_date).getTime() - 
               new Date(a.session_metadata.processing_date).getTime();
      case 'company':
        return a.session_metadata.company_name.localeCompare(b.session_metadata.company_name);
      case 'status':
        return a.session_metadata.status.localeCompare(b.session_metadata.status);
      default:
        return 0;
    }
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analysis Sessions</h2>
          <p className="text-gray-600">Manage and monitor credit analysis sessions</p>
        </div>
        <Button onClick={onNewSession}>
          <Plus className="h-4 w-4 mr-2" />
          New Analysis
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search sessions..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Status Filter */}
            <select
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>

            {/* Sort By */}
            <select
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'company' | 'status')}
            >
              <option value="date">Sort by Date</option>
              <option value="company">Sort by Company</option>
              <option value="status">Sort by Status</option>
            </select>

            {/* Results Count */}
            <div className="flex items-center text-sm text-gray-600">
              <Filter className="h-4 w-4 mr-2" />
              {sortedSessions.length} of {sessions.length} sessions
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {sortedSessions.map((session) => (
          <Card 
            key={session.session_metadata.session_id}
            className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-blue-500"
            onClick={() => onSessionClick(session)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Building2 className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg leading-tight">
                      {session.session_metadata.company_name}
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-1">
                      {session.session_metadata.session_id}
                    </p>
                  </div>
                </div>
                <Badge 
                  className={`${getStatusColor(session.session_metadata.status)} text-xs`}
                >
                  {session.session_metadata.status}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4">
                {session.comprehensive_results?.final_credit_rating && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Credit Rating</p>
                    <Badge className={getCreditRatingColor(session.comprehensive_results.final_credit_rating)}>
                      {session.comprehensive_results.final_credit_rating}
                    </Badge>
                  </div>
                )}
                
                {session.comprehensive_results?.confidence_score && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">Confidence</p>
                    <p className="font-semibold text-gray-900">
                      {session.comprehensive_results.confidence_score}%
                    </p>
                  </div>
                )}
              </div>

              {/* Session Details */}
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <User className="h-4 w-4" />
                  <span>{session.session_metadata.analyst_name || 'System'}</span>
                </div>
                
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <span>{new Date(session.session_metadata.processing_date).toLocaleDateString()}</span>
                </div>
                
                {session.session_metadata.processing_time_seconds && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>{formatDuration(session.session_metadata.processing_time_seconds)}</span>
                  </div>
                )}

                {session.session_metadata.priority_level && (
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-gray-600" />
                    <Badge variant={
                      session.session_metadata.priority_level === 'urgent' ? 'danger' :
                      session.session_metadata.priority_level === 'high' ? 'warning' :
                      'secondary'
                    }>
                      {session.session_metadata.priority_level} priority
                    </Badge>
                  </div>
                )}
              </div>

              {/* Risk Assessment */}
              {session.comprehensive_results?.risk_assessment && (
                <div className="pt-3 border-t">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Risk Level</span>
                    <Badge className={
                      session.comprehensive_results.risk_assessment === 'LOW' ? 'bg-green-100 text-green-700' :
                      session.comprehensive_results.risk_assessment === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                      session.comprehensive_results.risk_assessment === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }>
                      {session.comprehensive_results.risk_assessment}
                    </Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {sortedSessions.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Sessions Found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || statusFilter !== 'all' 
                ? 'Try adjusting your search or filters' 
                : 'Get started by creating your first analysis session'
              }
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <Button onClick={onNewSession}>
                <Plus className="h-4 w-4 mr-2" />
                Create First Analysis
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};