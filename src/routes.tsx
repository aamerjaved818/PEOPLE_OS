import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { RoleGuard } from './components/auth/RoleGuard';

// Lazy Load Core Components
const Dashboard = React.lazy(() => import('./modules/dashboard'));
const GeneralAdministration = React.lazy(() => import('./modules/gen-admin'));
const HCMModule = React.lazy(() => import('./modules/hcm'));
const OrganizationSetup = React.lazy(() => import('./modules/org-setup'));
const SystemSettings = React.lazy(() => import('./modules/system-settings'));
const SystemAudit = React.lazy(() => import('./modules/system-audit'));
const OrgAudit = React.lazy(() => import('./modules/org-audit'));

// Lazy Load Functional Modules
const PayrollEngine = React.lazy(() => import('./modules/payroll'));
const ExpensesTravel = React.lazy(() => import('./modules/expenses'));
const AnalyticsInsights = React.lazy(() => import('./modules/analytics'));
const SelfService = React.lazy(() => import('./modules/self-service'));
const LearningModule = React.lazy(() => import('./modules/learning'));
const PerformanceModule = React.lazy(() => import('./modules/performance'));
const PromotionsModule = React.lazy(() => import('./modules/promotions'));
const Benefits = React.lazy(() => import('./modules/benefits'));
const RewardsModule = React.lazy(() => import('./modules/rewards'));

// Placeholder Wrapper for unfinished modules
const PlaceholderModule: React.FC<{ title: string }> = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-center p-10">
    <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
      <div className="w-12 h-12 text-primary" /> {/* Icon would go here */}
    </div>
    <h2 className="text-3xl font-black text-text-primary uppercase tracking-tight">{title}</h2>
    <p className="text-text-muted mt-2 font-medium max-w-md">
      This module is currently under development. Check back soon for updates!
    </p>
  </div>
);

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Core Modules */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/admin" element={<GeneralAdministration />} />

      <Route
        path="/hcm/*"
        element={
          <RoleGuard permission="view_employees">
            <HCMModule />
          </RoleGuard>
        }
      />

      <Route
        path="/org-settings"
        element={
          <RoleGuard permission="manage_master_data">
            <OrganizationSetup />
          </RoleGuard>
        }
      />

      <Route
        path="/system-settings"
        element={
          <RoleGuard permission="system_config">
            <SystemSettings />
          </RoleGuard>
        }
      />

      <Route
        path="/system-audit"
        element={
          <RoleGuard permission="system_config">
            <SystemAudit />
          </RoleGuard>
        }
      />

      <Route
        path="/org-audit"
        element={
          <RoleGuard permission="manage_master_data">
            <OrgAudit />
          </RoleGuard>
        }
      />

      {/* Functional Modules */}
      <Route path="/payroll" element={<PayrollEngine />} />
      <Route path="/expenses" element={<ExpensesTravel />} />
      <Route path="/analytics" element={<AnalyticsInsights />} />
      <Route path="/self-service" element={<SelfService />} />
      <Route path="/learning" element={<LearningModule />} />
      <Route path="/performance" element={<PerformanceModule />} />
      <Route path="/promotions" element={<PromotionsModule />} />
      <Route path="/benefits" element={<Benefits />} />
      <Route path="/rewards" element={<RewardsModule />} />

      {/* Placeholders */}
      <Route path="/tax-compliance" element={<PlaceholderModule title="Tax & Compliance" />} />
      <Route path="/compensation" element={<PlaceholderModule title="Compensation" />} />
      <Route path="/skills" element={<PlaceholderModule title="Skills & Competency" />} />
      <Route path="/succession" element={<PlaceholderModule title="Talent & Succession" />} />
      <Route path="/engagement" element={<PlaceholderModule title="Engagement" />} />
      <Route path="/relations" element={<PlaceholderModule title="Employee Relations" />} />
      <Route path="/health-safety" element={<PlaceholderModule title="Health & Safety" />} />
      <Route path="/alumni" element={<PlaceholderModule title="Alumni Mgmt" />} />
      <Route path="/workflow" element={<PlaceholderModule title="Workflow" />} />
      <Route path="/integration" element={<PlaceholderModule title="Integrations" />} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes;
