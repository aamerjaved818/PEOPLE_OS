import React, { useState } from 'react';
import { SelfServiceDashboard } from './Dashboard';
import { ProfileView } from './ProfileView';
import { DocumentCenter } from './DocumentCenter';
import { PayslipViewer } from './PayslipViewer';
import { TeamDirectory } from './TeamDirectory';
import AssistanceModule from '../assistance';
import { Button } from '@/components/ui/Button';
import { useTheme } from '@/contexts/ThemeContext';

import { Layout as LayoutIcon, User, FileText, CreditCard, Users, HelpCircle } from 'lucide-react';

type SelfServiceView = 'dashboard' | 'profile' | 'documents' | 'payslips' | 'team' | 'help-desk';

const SelfService: React.FC = () => {
  const [currentView, setCurrentView] = useState<SelfServiceView>('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'profile':
        return <ProfileView />;
      case 'documents':
        return <DocumentCenter />;
      case 'payslips':
        return <PayslipViewer />;
      case 'team':
        return <TeamDirectory />;
      case 'help-desk':
        return <AssistanceModule />;
      case 'dashboard':
      default:
        return <SelfServiceDashboard />;
    }
  };

  const navItems: { id: SelfServiceView; label: string; icon: React.ElementType }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutIcon },
    { id: 'profile', label: 'My Profile', icon: User },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'payslips', label: 'Payslips', icon: CreditCard },
    { id: 'team', label: 'Team', icon: Users },
    { id: 'help-desk', label: 'Help Desk', icon: HelpCircle },
  ];

  return (
    <div className="min-h-screen bg-bg transition-colors duration-500">
      <div className="container mx-auto px-6 py-8">
        {/* Standard Module Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-black text-text-primary tracking-tighter leading-none uppercase">
              Self Service
            </h1>
            <p className="text-text-muted mt-2 font-black uppercase tracking-[0.3em] text-[0.6rem] flex items-center gap-3">
              <span className="w-8 h-[0.125rem] bg-primary"></span>
              Employee Hub
            </p>
          </div>
        </div>

        {/* Internal Navigation Bar */}
        <div className="bg-surface border border-border/50 px-3 py-2 flex items-center space-x-2 rounded-2xl shadow-xl backdrop-blur-xl mb-8">
          {navItems.map((item) => (
            <Button
              key={item.id}
              variant={currentView === item.id ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setCurrentView(item.id)}
              className={`flex items-center gap-2.5 px-4 h-9 rounded-xl font-bold uppercase tracking-widest text-[0.65rem] transition-all ${
                currentView === item.id
                  ? 'shadow-lg shadow-primary/20 scale-105'
                  : 'text-text-muted'
              }`}
            >
              <item.icon
                size={14}
                className={currentView === item.id ? 'text-white' : 'text-primary'}
              />
              <span>{item.label}</span>
            </Button>
          ))}
        </div>

        <main className="animate-in fade-in slide-in-from-bottom-4 duration-700">
          {renderView()}
        </main>
      </div>
    </div>
  );
};

export default SelfService;
