import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { selfServiceApi } from '@/services/selfServiceApi';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useNavigate } from 'react-router-dom';
import {
  User,
  FileText,
  CreditCard,
  Users,
  Timer,
  ChevronRight,
  ShieldCheck,
  Mail,
  Phone,
  Calendar,
  Activity,
  Droplets,
  Zap,
} from 'lucide-react';

export const SelfServiceDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: profile, isLoading } = useQuery({
    queryKey: ['myProfile'],
    queryFn: selfServiceApi.getMyProfile,
  });

  const { data: documentRequests } = useQuery({
    queryKey: ['myDocumentRequests'],
    queryFn: selfServiceApi.getMyDocumentRequests,
  });

  const pendingRequests = documentRequests?.filter((r) => r.status === 'Pending').length || 0;

  const quickActions = [
    { label: 'View My Profile', icon: User, path: '/self-service/profile' },
    { label: 'Request Document', icon: FileText, path: '/self-service/documents' },
    { label: 'View Payslips', icon: CreditCard, path: '/self-service/payslips' },
    { label: 'Team Directory', icon: Users, path: '/self-service/team' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Welcome Header */}
      <div className="flex items-center justify-between p-8 bg-surface border border-border/50 rounded-[2.5rem] shadow-xl relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent pointer-events-none"></div>
        <div className="relative z-10">
          <h1 className="text-5xl font-black text-text-primary tracking-tighter leading-none mb-4">
            Welcome back, <span className="text-primary">{profile?.name?.split(' ')[0]}!</span>
          </h1>
          <p className="text-text-muted font-black uppercase tracking-[0.4em] text-[0.625rem] flex items-center gap-3">
            <span className="w-8 h-[0.125rem] bg-primary"></span>
            {profile?.designation} • {profile?.department}
          </p>
        </div>
        <div className="relative z-10 shrink-0">
          {profile?.profilePhotoUrl ? (
            <img
              src={profile.profilePhotoUrl}
              alt={profile.name}
              className="w-24 h-24 rounded-2xl object-cover border-2 border-primary/20 shadow-2xl group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <div className="w-24 h-24 rounded-2xl bg-primary text-white flex items-center justify-center text-4xl font-black shadow-2xl group-hover:scale-105 transition-transform duration-500">
              {profile?.name?.charAt(0)}
            </div>
          )}
        </div>
      </div>

      {/* Pending Requests Alert */}
      {pendingRequests > 0 && (
        <div className="p-6 bg-warning/10 border border-warning/20 rounded-[2rem] backdrop-blur-3xl animate-in slide-in-from-top duration-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="p-4 bg-warning/20 backdrop-blur-xl rounded-2xl border border-warning/30">
                <Timer size={24} className="text-warning animate-pulse" />
              </div>
              <div>
                <h3 className="font-black text-xl text-text-primary tracking-tight">
                  Pending Approval
                </h3>
                <p className="text-[0.625rem] font-black uppercase text-warning tracking-widest mt-1">
                  You have {pendingRequests} document request{pendingRequests > 1 ? 's' : ''} in
                  queue
                </p>
              </div>
            </div>
            <Button
              onClick={() => navigate('/self-service/documents')}
              variant="outline"
              className="rounded-xl font-black uppercase tracking-widest text-[0.625rem] px-6 h-10 hover:bg-warning hover:text-white border-warning/30 text-warning transition-all"
            >
              Verify Queue <ChevronRight size={14} className="ml-2" />
            </Button>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {quickActions.map((action) => (
          <button
            key={action.path}
            onClick={() => navigate(action.path)}
            className="p-8 bg-surface border border-border/50 rounded-[2.5rem] hover:bg-primary/5 hover:border-primary/30 transition-all group relative overflow-hidden text-center shadow-lg"
          >
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:scale-110 group-hover:bg-primary group-hover:text-white transition-all duration-500 shadow-inner">
                <action.icon size={28} />
              </div>
              <p className="text-[0.65rem] font-black text-text-muted uppercase tracking-[0.2em] group-hover:text-primary transition-colors">
                {action.label}
              </p>
            </div>
          </button>
        ))}
      </div>

      {/* Profile & Info Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 p-10 bg-surface border border-border/50 rounded-[3rem] shadow-xl relative overflow-hidden group">
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-primary/10 backdrop-blur-xl rounded-2xl border border-primary/20">
                  <User size={24} className="text-primary" />
                </div>
                <div>
                  <h3 className="font-black text-2xl text-text-primary tracking-tight uppercase">
                    Personal Intelligence
                  </h3>
                  <p className="text-[0.625rem] font-black uppercase text-text-muted tracking-widest mt-1">
                    System-Verified Employee Data
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                onClick={() => navigate('/self-service/profile')}
                className="rounded-xl font-black uppercase tracking-widest text-[0.625rem] px-6 h-10 border-border/50 hover:bg-primary hover:text-white transition-all"
              >
                Access Profile
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-x-12 gap-y-8">
              <InfoItem label="Employee Code" value={profile?.employeeCode} icon={ShieldCheck} />
              <InfoItem label="Corporate Email" value={profile?.email} icon={Mail} />
              <InfoItem label="Active Phone" value={profile?.phone} icon={Phone} />
              <InfoItem label="Commissioning Date" value={profile?.joinDate} icon={Calendar} />
              <InfoItem label="Node Status" value={profile?.status} icon={Activity} />
              <InfoItem label="Biological Marker" value={profile?.bloodGroup} icon={Droplets} />
            </div>
          </div>
        </div>

        <div className="p-10 bg-surface border border-border/50 rounded-[3rem] shadow-xl relative overflow-hidden flex flex-col justify-between">
          <div className="relative z-10">
            <h3 className="font-black text-2xl text-text-primary tracking-tight uppercase mb-8 flex items-center gap-4">
              <div className="p-3 bg-danger/10 backdrop-blur-xl rounded-2xl border border-danger/20">
                <Zap size={24} className="text-danger" />
              </div>
              Emergency
            </h3>

            {profile?.emergencyContactName ? (
              <div className="space-y-6">
                <InfoItem label="Contact Name" value={profile.emergencyContactName} />
                <InfoItem label="Emergency Line" value={profile.emergencyContactPhone} />
                <InfoItem label="Relation Node" value={profile.emergencyContactRelation} />
                <Button
                  className="mt-6 w-full rounded-xl font-black uppercase tracking-widest text-[0.625rem] h-12 border-danger/20 text-danger hover:bg-danger hover:text-white transition-all"
                  onClick={() => navigate('/self-service/profile')}
                  variant="outline"
                >
                  Update Protocols
                </Button>
              </div>
            ) : (
              <div className="text-center py-12 flex flex-col items-center">
                <div className="w-16 h-16 bg-muted-bg rounded-2xl flex items-center justify-center mb-6 opacity-20">
                  <User size={32} />
                </div>
                <p className="text-[0.7rem] font-black text-text-muted uppercase tracking-widest mb-6">
                  No emergency protocols set
                </p>
                <Button
                  onClick={() => navigate('/self-service/profile')}
                  className="w-full h-11 rounded-xl font-black uppercase tracking-widest text-[0.625rem]"
                >
                  Configure Now
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoItem: React.FC<{ label: string; value?: string; icon?: React.ElementType }> = ({
  label,
  value,
  icon: Icon,
}) => (
  <div className="group/item">
    <div className="flex items-center gap-3 mb-2">
      {Icon && <Icon size={12} className="text-primary/60" />}
      <p className="text-[0.6rem] font-black text-text-muted uppercase tracking-widest">{label}</p>
    </div>
    <p className="text-lg font-black text-text-primary tracking-tight leading-none truncate">
      {value || '—'}
    </p>
  </div>
);
