import React, { useState } from 'react';
import {
  ShieldCheck,
  FileArchive,
  CheckCircle2,
  Download,
  Lock,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  ShieldAlert,
  Fingerprint,
  Zap,
} from 'lucide-react';
import { useToast } from '@/components/ui/Toast';

interface Control {
  id: string;
  name: string;
  status: 'pass' | 'warn' | 'fail';
  description: string;
  signals: string[];
}

export const ComplianceDashboard: React.FC = () => {
  const [standard, setStandard] = useState<'SOC2' | 'ISO27001'>('SOC2');
  const [isCollecting, setIsCollecting] = useState(false);
  const { success, error } = useToast();

  const controls: Record<string, Control[]> = {
    SOC2: [
      {
        id: 'CC6.1',
        name: 'Logical Access Control',
        status: 'pass',
        description:
          'Implementation of role-based access control (RBAC) and multi-factor authentication (MFA).',
        signals: ['auth_provider_config', 'rbac_policy_audit', 'session_timeout_check'],
      },
      {
        id: 'CC7.1',
        name: 'System Monitoring',
        status: 'pass',
        description:
          'Continuous monitoring of infrastructure, application health, and security events.',
        signals: ['uptime_kuma_sync', 'log_aggregation_active', 'vulnerability_scan_result'],
      },
      {
        id: 'CC2.1',
        name: 'Internal Communications',
        status: 'warn',
        description:
          'Dissemination of security policies and responsibilities to internal stakeholders.',
        signals: ['policy_acknowledgment_log', 'training_completion_rates'],
      },
    ],
    ISO27001: [
      {
        id: 'A.12.1.2',
        name: 'Change Management',
        status: 'pass',
        description:
          'Verification of change management processes, including CI/CD pipelines and peer reviews.',
        signals: ['github_action_logs', 'pr_review_compliance', 'deployment_freeze_checks'],
      },
      {
        id: 'A.9.2.2',
        name: 'User Provisioning',
        status: 'pass',
        description:
          'Formal user registration and de-registration process for granting and revoking access.',
        signals: ['ldap_connector_status', 'offboarding_workflow_audit'],
      },
    ],
  };

  const collectEvidence = async () => {
    setIsCollecting(true);
    try {
      // Simulate backend evidence extraction
      await new Promise((resolve) => setTimeout(resolve, 2500));
      success('Evidence vault sealed and certified. Hash: 0x82f...a12');
    } catch {
      error('Evidence collection interrupted');
    } finally {
      setIsCollecting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle2 size={16} className="text-success" />;
      case 'warn':
        return <AlertCircle size={16} className="text-warning" />;
      case 'fail':
        return <ShieldAlert size={16} className="text-danger" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      {/* Top Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-primary/10 via-surface/5 to-purple-500/10 border border-white/5 rounded-[2rem] p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl flex items-center justify-center shadow-2xl">
              <ShieldCheck size={32} className="text-primary" />
            </div>
            <div>
              <h3 className="text-3xl font-black text-text-primary uppercase tracking-tighter leading-none mb-1">
                Compliance Monitor
              </h3>
              <p className="text-sm text-text-muted font-medium">
                Real-time technical control validation & evidence orchestration
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 p-1.5 bg-background/50 backdrop-blur-md rounded-2xl border border-white/10 shadow-inner">
            {['SOC2', 'ISO27001'].map((s) => (
              <button
                key={s}
                onClick={() => setStandard(s as any)}
                className={`px-6 py-2.5 rounded-xl text-[0.65rem] font-black uppercase tracking-widest transition-all duration-300 ${standard === s ? 'bg-primary text-white shadow-xl shadow-primary/20 scale-105' : 'text-text-muted hover:text-text-primary hover:bg-white/5'}`}
              >
                {s === 'SOC2' ? 'SOC2 Type II' : 'ISO 27001:2022'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Controls List */}
        <div className="lg:col-span-3 space-y-5">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xs font-black text-text-muted uppercase tracking-[0.2em]">
              Active Control Matrix ({controls[standard].length} Controls)
            </h4>
            <div className="flex items-center gap-2 text-[0.65rem] font-bold text-success bg-success/10 px-3 py-1 rounded-full border border-success/20">
              <Zap size={12} fill="currentColor" />
              LIVE SYNC
            </div>
          </div>

          {controls[standard].map((control) => (
            <div
              key={control.id}
              className="bg-surface/30 backdrop-blur-md border border-white/5 rounded-3xl p-6 md:p-8 hover:bg-surface/50 hover:border-primary/30 transition-all duration-300 group relative overflow-hidden"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-lg text-[0.65rem] font-black text-primary tracking-widest">
                      {control.id}
                    </div>
                    <h4 className="text-xl font-bold text-text-primary group-hover:text-primary transition-colors">
                      {control.name}
                    </h4>
                  </div>
                  <p className="text-sm text-text-muted font-medium leading-relaxed max-w-2xl">
                    {control.description}
                  </p>

                  {/* Signal Pips */}
                  <div className="flex flex-wrap gap-2 pt-2">
                    {control.signals.map((signal) => (
                      <span
                        key={signal}
                        className="px-2 py-0.5 bg-background/50 border border-white/5 rounded-md text-[0.55rem] font-bold text-text-muted uppercase tracking-wider flex items-center gap-1.5 opacity-60 group-hover:opacity-100 transition-opacity"
                      >
                        <Fingerprint size={10} className="text-primary" />
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-start gap-4 flex-shrink-0">
                  <div
                    className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${control.status === 'pass' ? 'bg-success/10 border-success/20 text-success' : 'bg-warning/10 border-warning/20 text-warning'} text-[0.65rem] font-black uppercase tracking-widest`}
                  >
                    {getStatusIcon(control.status)}
                    {control.status === 'pass' ? 'Validated' : 'Attention'}
                  </div>
                  <button className="p-2 bg-white/5 border border-white/10 rounded-xl text-text-muted hover:text-primary hover:border-primary/50 transition-all group/info">
                    <ExternalLink
                      size={18}
                      className="group-hover/info:scale-110 transition-transform"
                    />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar Actions */}
        <div className="space-y-6">
          <div className="bg-surface/30 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-primary/20 transition-all duration-700" />
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-tr from-primary to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-xl shadow-primary/30">
                <FileArchive size={24} className="text-white" />
              </div>
              <h4 className="text-lg font-black text-text-primary uppercase tracking-tight mb-3">
                Evidence Vault
              </h4>
              <p className="text-xs text-text-muted mb-8 font-medium leading-relaxed">
                Generate cryptographically signed evidence packages for external audits. Includes
                system state, logs, and dimension scores.
              </p>
              <button
                onClick={collectEvidence}
                disabled={isCollecting}
                className={`w-full py-4 rounded-2xl font-black uppercase tracking-[0.15em] text-[0.65rem] flex items-center justify-center gap-3 transition-all relative overflow-hidden group/btn ${isCollecting ? 'bg-surface border border-white/10 text-text-muted cursor-not-allowed' : 'bg-text-primary text-background hover:bg-primary hover:text-white hover:shadow-2xl hover:shadow-primary/40 active:scale-95'}`}
              >
                {isCollecting ? (
                  <RefreshCw size={16} className="animate-spin" />
                ) : (
                  <Download
                    size={16}
                    className="group-hover/btn:-translate-y-0.5 transition-transform"
                  />
                )}
                <span>{isCollecting ? 'COLLECTING...' : 'PREPARE REPORT'}</span>
              </button>
              <div className="mt-6 flex items-center gap-3 py-3 px-4 bg-background/40 rounded-xl border border-white/5">
                <Lock size={14} className="text-success" />
                <span className="text-[0.6rem] font-black text-text-muted uppercase tracking-widest">
                  SECURE AES-256 AES-256
                </span>
              </div>
            </div>
          </div>

          <div className="bg-surface/30 backdrop-blur-lg border border-white/5 rounded-[2rem] p-8">
            <h4 className="text-[0.65rem] font-black text-text-muted uppercase tracking-[0.2em] mb-6">
              ORCHESTRATION RULES
            </h4>
            <div className="space-y-5">
              {[
                { label: 'Control Polling', status: 'Every 5m' },
                { label: 'Log Retention', status: '365 Days' },
                { label: 'Audit Trail', status: 'Immutable' },
                { label: 'Encryption', status: 'TLS 1.3' },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-primary">{item.label}</span>
                  <span className="text-[0.6rem] font-black text-primary bg-primary/10 px-2 py-0.5 rounded-md uppercase tracking-wider">
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
