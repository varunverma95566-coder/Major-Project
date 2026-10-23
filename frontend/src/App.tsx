import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

// Pages
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { TrafficAnalysisPage } from './pages/TrafficAnalysisPage';
import { DatasetManagementPage } from './pages/DatasetManagementPage';
import { ModelTrainingPage } from './pages/ModelTrainingPage';
import { FlowInvestigationPage } from './pages/FlowInvestigationPage';
import { AlertsPage } from './pages/AlertsPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { IOCExplorerPage } from './pages/IOCExplorerPage';
import { CorrelationGraphPage } from './pages/CorrelationGraphPage';
import { MitreMappingPage } from './pages/MitreMappingPage';
import { FederatedLearningPage } from './pages/FederatedLearningPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

const ProtectedLayout: React.FC = () => {
  const { user, token } = useAuth();

  if (!token && !user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col selection:bg-cyan-500 selection:text-slate-950">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-4rem)] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(6,182,212,0.06),rgba(15,23,42,0))]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            {/* Protected SOC Dashboard Routes */}
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/traffic" element={<TrafficAnalysisPage />} />
              <Route path="/investigation" element={<FlowInvestigationPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/iocs" element={<IOCExplorerPage />} />
              <Route path="/graph" element={<CorrelationGraphPage />} />
              <Route path="/mitre" element={<MitreMappingPage />} />
              <Route path="/datasets" element={<DatasetManagementPage />} />
              <Route path="/models" element={<ModelTrainingPage />} />
              <Route path="/federated" element={<FederatedLearningPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
};

export default App;
