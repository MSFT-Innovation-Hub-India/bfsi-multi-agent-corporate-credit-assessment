import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GMRDashboard from './components/GMRDashboard';
import WorkflowList from './components/WorkflowList';
import WorkflowDetail from './components/WorkflowDetail';
import './index.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<GMRDashboard />} />
          <Route path="/dashboard/:sessionId" element={<GMRDashboard />} />
          <Route path="/workflows" element={<WorkflowList />} />
          <Route path="/workflows/:workflowId" element={<WorkflowDetail />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;