import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { selfServiceApi } from '@/services/selfServiceApi';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { toast } from '@/components/ui/Toast';
import {
  User,
  Camera,
  Mail,
  Phone,
  Calendar,
  Zap,
  Heart,
  Activity,
  Droplets,
  MapPin,
  ShieldCheck,
  Edit3,
  X,
  Save,
} from 'lucide-react';

export const ProfileView: React.FC = () => {
  const queryClient = useQueryClient();
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [bio, setBio] = useState('');
  const [isEditingContact, setIsEditingContact] = useState(false);
  const [emergencyContact, setEmergencyContact] = useState({
    emergencyContactName: '',
    emergencyContactPhone: '',
    emergencyContactRelation: '',
  });

  const { data: profile, isPending: isLoading } = useQuery({
    queryKey: ['myProfile'],
    queryFn: selfServiceApi.getMyProfile,
  });

  const updateProfileMutation = useMutation({
    mutationFn: selfServiceApi.updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      toast.success('Profile updated successfully');
      setIsEditingBio(false);
      setBio((profile as any)?.bio || '');
    },
  });

  const updateEmergencyContactMutation = useMutation({
    mutationFn: selfServiceApi.updateEmergencyContact,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      toast.success('Emergency contact updated');
      setIsEditingContact(false);
    },
  });

  const uploadPhotoMutation = useMutation({
    mutationFn: selfServiceApi.uploadProfilePhoto,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      toast.success('Profile photo updated');
    },
  });

  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File too large. Maximum size is 5MB');
        return;
      }
      uploadPhotoMutation.mutate(file);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-20">
      {/* Profile Header Card */}
      <div className="bg-surface border border-border/50 rounded-[3rem] p-10 shadow-2xl relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start gap-10">
          <div className="relative group/photo">
            {profile?.profilePhotoUrl ? (
              <img
                src={profile.profilePhotoUrl}
                alt={profile.name}
                className="w-40 h-40 rounded-[2.5rem] object-cover border-4 border-surface shadow-2xl transition-transform duration-500 group-hover/photo:scale-105"
              />
            ) : (
              <div className="w-40 h-40 rounded-[2.5rem] bg-primary text-white flex items-center justify-center text-6xl font-black shadow-2xl transition-transform duration-500 group-hover/photo:scale-105">
                {profile?.name?.charAt(0)}
              </div>
            )}
            <label className="absolute -bottom-2 -right-2 bg-primary text-white p-4 rounded-2xl cursor-pointer hover:bg-primary-hover shadow-xl transition-all hover:scale-110 active:scale-95 border-4 border-surface">
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handlePhotoUpload}
                disabled={uploadPhotoMutation.isPending}
              />
              <Camera size={20} />
            </label>
          </div>

          <div className="flex-1 text-center md:text-left">
            <h1 className="text-5xl font-black text-text-primary tracking-tighter leading-none mb-3">
              {profile?.name}
            </h1>
            <p className="text-text-muted font-black uppercase tracking-[0.4em] text-[0.625rem] flex items-center justify-center md:justify-start gap-3 mb-8">
              <span className="w-8 h-[0.125rem] bg-primary"></span>
              {profile?.designation} • {profile?.department}
            </p>

            <div className="bg-muted-bg/30 rounded-3xl p-8 border border-border/50 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-text-muted">
                  Professional Manifesto
                </h3>
                <button
                  onClick={() => setIsEditingBio(!isEditingBio)}
                  className="text-primary hover:text-primary-hover transition-colors font-black uppercase tracking-widest text-[0.6rem] flex items-center gap-2"
                >
                  {isEditingBio ? (
                    <>
                      <X size={14} /> Cancel
                    </>
                  ) : (
                    <>
                      <Edit3 size={14} /> Refactor
                    </>
                  )}
                </button>
              </div>
              {isEditingBio ? (
                <div className="space-y-4">
                  <textarea
                    className="w-full bg-surface border border-primary/20 rounded-2xl p-6 min-h-[140px] text-text-primary font-bold placeholder:text-text-muted/50 focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all"
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder="Distill your professional essence..."
                    maxLength={500}
                  />
                  <div className="flex justify-between items-center">
                    <span className="text-[0.65rem] font-black text-text-muted tracking-widest">
                      {bio.length}/500 CHARS
                    </span>
                    <Button
                      onClick={() => updateProfileMutation.mutate({ bio })}
                      disabled={updateProfileMutation.isPending}
                      className="rounded-xl px-8 h-10 font-black uppercase tracking-widest text-[0.6rem] shadow-lg shadow-primary/20"
                    >
                      <Save size={14} className="mr-2" /> Commit Changes
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-text-primary font-bold leading-relaxed italic opacity-80">
                  "{profile?.bio || 'No manifesto initialized for this node yet...'}"
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Identity Clusters */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Core Intelligence */}
        <div className="bg-surface border border-border/50 rounded-[3rem] p-10 shadow-xl">
          <h3 className="text-2xl font-black text-text-primary tracking-tight uppercase mb-8 flex items-center gap-4">
            <div className="p-3 bg-primary/10 rounded-2xl border border-primary/20">
              <ShieldCheck size={24} className="text-primary" />
            </div>
            Core Intelligence
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            <InfoField label="Node Hash" value={profile?.employeeCode} icon={Activity} />
            <InfoField label="Corporate Sync" value={profile?.email} icon={Mail} />
            <InfoField label="Voice Link" value={profile?.phone} icon={Phone} />
            <InfoField label="Private Alias" value={profile?.personalEmail} icon={Mail} />
            <InfoField label="Field Comms" value={profile?.personalPhone} icon={Phone} />
            <InfoField label="Activation" value={profile?.joinDate} icon={Calendar} />
          </div>
        </div>

        {/* Biological Data */}
        <div className="bg-surface border border-border/50 rounded-[3rem] p-10 shadow-xl">
          <h3 className="text-2xl font-black text-text-primary tracking-tight uppercase mb-8 flex items-center gap-4">
            <div className="p-3 bg-vibrant-pink/10 rounded-2xl border border-vibrant-pink/20">
              <Heart size={24} className="text-vibrant-pink" />
            </div>
            Biological Cluster
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            <InfoField label="Origins" value={profile?.dateOfBirth} icon={Calendar} />
            <InfoField label="Gender Node" value={profile?.gender} icon={User} />
            <InfoField label="Status Link" value={profile?.maritalStatus} icon={Activity} />
            <InfoField label="Blood Marker" value={profile?.bloodGroup} icon={Droplets} />
            <InfoField label="Entity Status" value={profile?.status} icon={ShieldCheck} />
          </div>
        </div>
      </div>

      {/* Geospatial Mapping */}
      <div className="bg-surface border border-border/50 rounded-[3rem] p-10 shadow-xl">
        <h3 className="text-2xl font-black text-text-primary tracking-tight uppercase mb-8 flex items-center gap-4">
          <div className="p-3 bg-vibrant-cyan/10 rounded-2xl border border-vibrant-cyan/20">
            <MapPin size={24} className="text-vibrant-cyan" />
          </div>
          Geospatial Mapping
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          <InfoField label="Deployment Address" value={profile?.presentAddress} multiline />
          <InfoField label="Origin Core" value={profile?.permanentAddress} multiline />
        </div>
      </div>

      {/* Emergency Protocols */}
      <div className="bg-danger/5 border border-danger/10 rounded-[3rem] p-10 shadow-xl">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-2xl font-black text-danger tracking-tight uppercase flex items-center gap-4">
            <div className="p-3 bg-danger/10 rounded-2xl border border-danger/20">
              <Zap size={24} className="text-danger" />
            </div>
            Emergency Protocols
          </h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEditingContact(!isEditingContact)}
            className="rounded-xl font-black uppercase tracking-widest text-[0.6rem] border-danger/20 text-danger hover:bg-danger hover:text-white transition-all h-10 px-6"
          >
            {isEditingContact ? 'Abort Edit' : 'Modify Protocol'}
          </Button>
        </div>

        {isEditingContact ? (
          <div className="space-y-6 max-w-2xl">
            <Input
              label="Contact Signature"
              value={emergencyContact.emergencyContactName}
              onChange={(e) =>
                setEmergencyContact((prev) => ({ ...prev, emergencyContactName: e.target.value }))
              }
            />
            <Input
              label="Priority Line"
              value={emergencyContact.emergencyContactPhone}
              onChange={(e) =>
                setEmergencyContact((prev) => ({
                  ...prev,
                  emergencyContactPhone: e.target.value,
                }))
              }
            />
            <Input
              label="Relational Bond"
              value={emergencyContact.emergencyContactRelation}
              onChange={(e) =>
                setEmergencyContact((prev) => ({
                  ...prev,
                  emergencyContactRelation: e.target.value,
                }))
              }
            />
            <Button
              onClick={() => updateEmergencyContactMutation.mutate(emergencyContact)}
              disabled={updateEmergencyContactMutation.isPending}
              className="w-full bg-danger hover:bg-danger/80 text-white rounded-xl h-12 font-black uppercase tracking-widest text-[0.7rem] shadow-xl shadow-danger/20"
            >
              Commit Protocol Change
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <InfoField label="Contact Identifier" value={profile?.emergencyContactName} />
            <InfoField label="Secure Line" value={profile?.emergencyContactPhone} />
            <InfoField label="Relational Tag" value={profile?.emergencyContactRelation} />
          </div>
        )}
      </div>
    </div>
  );
};

const InfoField: React.FC<{
  label: string;
  value?: string;
  multiline?: boolean;
  icon?: React.ElementType;
}> = ({ label, value, multiline, icon: Icon }) => (
  <div className={`${multiline ? 'col-span-full' : ''} group/field`}>
    <div className="flex items-center gap-3 mb-2">
      {Icon && (
        <Icon
          size={12}
          className="text-primary/60 group-hover/field:text-primary transition-colors"
        />
      )}
      <label className="block text-[0.6rem] font-black text-text-muted uppercase tracking-widest">
        {label}
      </label>
    </div>
    <p
      className={`text-text-primary font-bold ${multiline ? 'text-sm leading-relaxed' : 'text-lg tracking-tight'}`}
    >
      {value || '—'}
    </p>
  </div>
);
