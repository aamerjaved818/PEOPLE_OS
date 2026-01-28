import React, { useState, useEffect, useMemo } from 'react';
import {
  Building,
  Plus,
  Search,
  MoreVertical,
  Edit2,
  Trash2,
  Globe,
  MapPin,
  Activity,
  LayoutGrid,
  List,
  Filter,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  LayoutDashboard,
  X,
  Save,
  Hash,
  Phone,
  Mail,
  Calendar,
  Lock,
  User as UserIcon,
} from 'lucide-react';
import { api } from '@/services/api';
import { useOrgStore } from '@/store/orgStore';
import { OrganizationProfile } from '@/types';
import { Button } from '@/components/ui/Button';
import ModuleSkeleton from '@/components/ui/ModuleSkeleton';
import { ConfirmationModal } from '@/components/ui/ConfirmationModal';
import { useToast } from '@/components/ui/Toast';
import { Badge } from '@/components/ui/Badge';

// --- Internal Modal Component ---

interface OrganizationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  initialData?: OrganizationProfile;
}

import { useTheme } from '@/contexts/ThemeContext';

const OrganizationFormModal: React.FC<OrganizationFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
}) => {
  const [formData, setFormData] = useState<any>({
    name: '',
    code: '',
    industry: '',
    country: '',
    city: '',
    email: '',
    website: '',
    phone: '',
    taxId: '',
    registrationNumber: '',
    foundedDate: '',
    // Admin Fields
    adminUsername: '',
    adminPassword: '',
    adminEmail: '',
    adminName: '',
    ...initialData,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({ ...initialData });
    } else {
      setFormData({
        name: '',
        code: '',
        industry: '',
        country: '',
        city: '',
        email: '',
        website: '',
        phone: '',
        taxId: '',
        registrationNumber: '',
        foundedDate: '',
        adminUsername: '',
        adminPassword: '',
        adminEmail: '',
        adminName: '',
      });
    }
  }, [initialData, isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error: any) {
      console.error('Failed to save organization', error);
      alert(
        error.message ||
          'Failed to save organization. Please check admin credentials or org code uniqueness.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev: any) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-border bg-muted/20">
          <h2 className="text-xl font-black uppercase tracking-tight text-foreground flex items-center gap-3">
            <Building className="text-primary" size={24} />
            {initialData ? 'Edit Organization' : 'Register New Organization'}
          </h2>
          <Button
            onClick={onClose}
            variant="ghost"
            className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors h-auto"
          >
            <X size={20} />
          </Button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="p-6 space-y-6 max-h-[70vh] overflow-y-auto custom-scrollbar"
        >
          {/* Identity Section */}
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-2">
              Corporate Identity
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Organization Name <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Building
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="e.g. Acme Corp"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Organization Code <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Hash
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    size={16}
                  />
                  <input
                    type="text"
                    name="code"
                    required
                    pattern="^[A-Z]{3,7}[0-9]{2}$"
                    title="Organization code must be 3-7 uppercase letters followed by 2 digits (e.g., PEOPLE01)"
                    value={formData.code}
                    onChange={(e) => {
                      const val = e.target.value.toUpperCase();
                      if (val.length <= 9) {
                        setFormData((prev: any) => ({ ...prev, code: val }));
                      }
                    }}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all uppercase"
                    placeholder="e.g. PEOPLE01"
                  />
                  <p className="text-[10px] text-slate-500 mt-1 ml-1">
                    {' '}
                    Format: 3-7 letters + 2 digits (Uppercase){' '}
                  </p>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Industry / Sector
                </label>
                <div className="relative">
                  <Activity
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    size={16}
                  />
                  <input
                    type="text"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="e.g. Technology"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Establishment Date
                </label>
                <div className="relative">
                  <Calendar
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="date"
                    name="foundedDate"
                    value={formData.foundedDate}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all [&::-webkit-calendar-picker-indicator]:invert"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Location & Contact */}
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-emerald-400 mb-2">
              Location & Contact
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Country
                </label>
                <div className="relative">
                  <Globe
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="e.g. Pakistan"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  City
                </label>
                <div className="relative">
                  <MapPin
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="e.g. Lahore"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Email
                </label>
                <div className="relative">
                  <Mail
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="contact@company.com"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Phone
                </label>
                <div className="relative">
                  <Phone
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    size={16}
                  />
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                    placeholder="+92 300 1234567"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-1.5 mt-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                Website
              </label>
              <div className="relative">
                <Globe
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                  size={16}
                />
                <input
                  type="url"
                  name="website"
                  value={formData.website}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-xl text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
                  placeholder="https://example.com"
                />
              </div>
            </div>
          </div>

          {/* Super Admin Section - Only for New Registrations */}
          {!initialData && (
            <div className="space-y-4 p-4 bg-blue-500/5 rounded-2xl border border-blue-500/10">
              <h3 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-2 flex items-center gap-2">
                <Lock size={14} />
                Mandatory Super Admin Configuration
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Admin Username <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <UserIcon
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                      size={16}
                    />
                    <input
                      type="text"
                      name="adminUsername"
                      required
                      value={formData.adminUsername}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                      placeholder="e.g. admin_acme"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Admin Password <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <Lock
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                      size={16}
                    />
                    <input
                      type="password"
                      name="adminPassword"
                      required
                      minLength={8}
                      value={formData.adminPassword}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-slate-600 transition-all"
                      placeholder="Min 8 characters"
                    />
                  </div>
                </div>

                <div className="space-y-1.5 md:col-span-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Admin Full Name
                  </label>
                  <input
                    type="text"
                    name="adminName"
                    value={formData.adminName}
                    onChange={handleChange}
                    className="w-full px-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                    placeholder="e.g. System Administrator"
                  />
                </div>

                <div className="space-y-1.5 md:col-span-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Admin Email <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="email"
                    name="adminEmail"
                    required
                    value={formData.adminEmail}
                    onChange={handleChange}
                    className="w-full px-4 py-2 bg-slate-800 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                    placeholder="admin@company.com"
                  />
                </div>
              </div>
            </div>
          )}

          <div className="pt-6 border-t border-white/10 flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={isSubmitting}
              className="text-slate-400 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-500 text-white min-w-[120px] shadow-lg shadow-blue-600/20"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save size={16} />
                  Save Organization
                </span>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Main Component ---

const OrganizationManagement: React.FC = () => {
  const { theme } = useTheme();
  void theme;
  const {
    fetchProfile,
    currentOrganization,
    fetchOrganizations: storeFetchOrganizations,
    organizations: storeOrganizations,
  } = useOrgStore();
  const [organizations, setOrganizations] = useState<OrganizationProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState<OrganizationProfile | undefined>(undefined);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterIndustry, setFilterIndustry] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Confirmation Modal State
  const [confirmModal, setConfirmModal] = useState({
    isOpen: false,
    orgId: '',
    orgName: '',
  });

  const { success, error: toastError } = useToast();

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await storeFetchOrganizations?.();
        if (mounted) {
          setOrganizations(data || storeOrganizations || []);
        }
      } catch (e) {
        console.error('Failed to fetch organizations', e);
        const errorMsg = e instanceof Error ? e.message : 'Failed to fetch organizations';
        setError(`Error: ${errorMsg}`);
        setOrganizations([]);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    })();

    return () => {
      mounted = false;
    };
  }, [storeFetchOrganizations, storeOrganizations]);

  const handleCreate = () => {
    setSelectedOrg(undefined);
    setIsModalOpen(true);
  };

  const handleEdit = (org: OrganizationProfile) => {
    setSelectedOrg(org);
    setIsModalOpen(true);
  };

  const initiateDelete = (org: OrganizationProfile) => {
    setConfirmModal({
      isOpen: true,
      orgId: org.id,
      orgName: org.name,
    });
    setActiveMenu(null);
  };

  const handleConfirmDelete = async () => {
    try {
      await api.deleteOrganization(confirmModal.orgId);
      success('Organization deleted successfully');
      setConfirmModal({ ...confirmModal, isOpen: false });
      {
        const data = await storeFetchOrganizations?.(true);
        setOrganizations(data || storeOrganizations || []);
      }
    } catch (err) {
      console.error(err);
      toastError('Failed to delete organization');
    }
  };

  const handleSubmit = async (data: Partial<OrganizationProfile>) => {
    try {
      if (selectedOrg) {
        await api.updateOrganization(selectedOrg.id, data);
        success('Organization updated successfully');
      } else {
        await api.createOrganization(data);
        success('Organization created successfully');
      }
      {
        const data = await storeFetchOrganizations?.(true);
        setOrganizations(data || storeOrganizations || []);
      }
      setIsModalOpen(false);
    } catch (err) {
      toastError('Failed to save organization');
      console.error(err);
    }
  };

  const industries = useMemo(() => {
    const all = organizations.map((o) => o.industry).filter(Boolean);
    return Array.from(new Set(all));
  }, [organizations]);

  const filteredOrgs = useMemo(() => {
    return organizations.filter((org) => {
      const matchesSearch =
        org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        org.code?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesIndustry = filterIndustry === 'all' || org.industry === filterIndustry;
      const matchesStatus = filterStatus === 'all' || org.status === filterStatus;

      return matchesSearch && matchesIndustry && matchesStatus;
    });
  }, [organizations, searchTerm, filterIndustry, filterStatus]);

  const toggleSelectOrg = (org: OrganizationProfile) => {
    fetchProfile(org.id);
    success(`Switched context to ${org.name}`);
  };

  const stats = {
    total: organizations.length,
    active: organizations.filter((o) => o.status === 'Active').length,
    industries: industries.length,
  };

  if (loading) {
    return <ModuleSkeleton />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Dashboard Stats Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card/50 border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Building size={24} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground font-bold">
              Total Organizations
            </p>
            <p className="text-2xl font-black text-foreground">{stats.total}</p>
          </div>
        </div>
        <div className="bg-card/50 border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground font-bold">
              Active Tenants
            </p>
            <p className="text-2xl font-black text-foreground">{stats.active}</p>
          </div>
        </div>
        <div className="bg-card/50 border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
            <LayoutDashboard size={24} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground font-bold">
              Industries
            </p>
            <p className="text-2xl font-black text-foreground">{stats.industries}</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-4 rounded-2xl flex flex-col justify-center items-start shadow-xl shadow-blue-900/20">
          <p className="text-blue-100 text-xs font-bold uppercase tracking-wider mb-1">
            System Status
          </p>
          <div className="flex items-center gap-2">
            <ShieldCheck className="text-white" size={20} />
            <span className="text-white font-black text-lg">OPERATIONAL</span>
          </div>
        </div>
      </div>

      {/* Control Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-muted/50 p-4 rounded-2xl border border-border">
        <div className="flex items-center gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={16}
            />
            <input
              type="text"
              placeholder="Search organizations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-frost pl-10 pr-4 py-2.5 text-sm font-medium"
            />
          </div>
          <div className="relative">
            <select
              className="input-frost pl-9 p-2.5 text-sm"
              value={filterIndustry}
              onChange={(e) => setFilterIndustry(e.target.value)}
            >
              <option value="all">All Industries</option>
              {industries.map((i) => (
                <option key={i} value={i}>
                  {i}
                </option>
              ))}
            </select>
            <Filter
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={14}
            />
          </div>
          <div className="relative">
            <select
              className="input-frost pl-9 p-2.5 text-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
            <Activity
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={14}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-muted p-1 rounded-xl border border-border flex items-center">
            <Button
              variant={viewMode === 'grid' ? 'primary' : 'ghost'}
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-all h-auto ${viewMode === 'grid' ? 'bg-blue-600 text-white shadow-md' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <LayoutGrid size={16} />
            </Button>
            <Button
              variant={viewMode === 'table' ? 'primary' : 'ghost'}
              onClick={() => setViewMode('table')}
              className={`p-2 rounded-lg transition-all h-auto ${viewMode === 'table' ? 'bg-blue-600 text-white shadow-md' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <List size={16} />
            </Button>
          </div>
          <div className="h-6 w-px bg-border mx-1"></div>
          <Button
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl font-black uppercase tracking-wider text-xs shadow-lg shadow-blue-600/20"
            onClick={handleCreate}
          >
            <Plus size={16} className="mr-2" />
            New Organization
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 flex flex-col items-center text-center">
          <AlertCircle className="text-red-400 mb-2" size={32} />
          <p className="text-red-300 font-bold text-sm">{error}</p>
          <Button
            onClick={async () => {
              setLoading(true);
              const data = await storeFetchOrganizations?.();
              setOrganizations(data || storeOrganizations || []);
              setLoading(false);
            }}
            variant="outline"
            className="mt-4 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-300 rounded-lg text-sm font-medium transition-colors border-red-500/30 h-auto"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Content Area */}
      {filteredOrgs.length === 0 && !error ? (
        <div className="text-center py-20 bg-muted/20 rounded-3xl border border-border border-dashed">
          <Building className="mx-auto text-muted-foreground/50 mb-4 opacity-50" size={64} />
          <h3 className="text-xl font-bold text-foreground mb-2">No organizations found</h3>
          <p className="text-muted-foreground font-medium max-w-sm mx-auto mb-6">
            We couldn't find any organizations matching your search criteria.
          </p>
          <Button
            onClick={() => {
              setSearchTerm('');
              setFilterIndustry('all');
              setFilterStatus('all');
            }}
            variant="outline"
            className="flex h-auto"
          >
            Clear Filters
          </Button>
        </div>
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredOrgs.map((org) => (
                <div
                  key={org.id}
                  className={`group relative bg-card border rounded-2xl p-6 hover:bg-accent hover:opacity-100 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-900/10 hover:-translate-y-1 ${currentOrganization?.id === org.id ? 'border-emerald-500/50 shadow-emerald-900/20 bg-emerald-900/10' : 'border-border'}`}
                  onMouseLeave={() => setActiveMenu(null)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      toggleSelectOrg(org);
                    }
                  }}
                >
                  {currentOrganization?.id === org.id && (
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-emerald-500 text-emerald-950 font-black text-[10px] uppercase tracking-widest px-3 py-1 rounded-full shadow-lg border border-emerald-400 z-20 flex items-center gap-1">
                      <CheckCircle2 size={10} strokeWidth={4} /> Active Context
                    </div>
                  )}

                  <div className="absolute top-4 right-4 z-10">
                    <Button
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenu(activeMenu === org.id ? null : org.id);
                      }}
                      className={`p-2 rounded-lg transition-colors h-auto ${
                        activeMenu === org.id
                          ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                          : 'text-slate-400 hover:bg-white/10 hover:text-white opacity-0 group-hover:opacity-100'
                      }`}
                    >
                      <MoreVertical size={16} />
                    </Button>

                    {activeMenu === org.id && (
                      <div className="absolute right-0 top-full mt-2 w-48 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 z-50">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(org);
                            setActiveMenu(null);
                          }}
                          className="w-full text-left px-4 py-3 text-sm font-medium text-slate-300 hover:bg-white/5 hover:text-white flex items-center gap-2 transition-colors"
                        >
                          <Edit2 size={14} /> Edit Organization
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            initiateDelete(org);
                            setActiveMenu(null);
                          }}
                          className="w-full text-left px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-2 transition-colors border-t border-white/5"
                        >
                          <Trash2 size={14} /> Delete Organization
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="flex items-start gap-4 mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
                      {org.logo ? (
                        <img
                          src={org.logo}
                          alt={org.name}
                          className="w-full h-full object-cover rounded-2xl"
                        />
                      ) : (
                        <Building className="text-blue-400" size={32} />
                      )}
                    </div>
                    <div>
                      <h3 className="font-bold text-lg text-white leading-tight mb-1">
                        {org.name}
                      </h3>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="slate" className="text-[10px] bg-slate-900/50">
                          {org.code || 'N/A'}
                        </Badge>
                        {org.industry && (
                          <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-slate-600" />
                            {org.industry}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6 bg-black/20 p-4 rounded-xl">
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                        Location
                      </span>
                      <div className="flex items-center gap-1.5 text-sm font-medium text-slate-300">
                        <MapPin size={14} className="text-indigo-400" />
                        <span className="truncate">
                          {org.city || 'Unknown'}, {org.country || 'N/A'}
                        </span>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                        Status
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            const newStatus: 'Active' | 'Inactive' =
                              org.status === 'Inactive' ? 'Active' : 'Inactive';
                            try {
                              // Optimistic update
                              const updatedOrgs = organizations.map((o) =>
                                o.id === org.id ? { ...o, status: newStatus } : o
                              );
                              setOrganizations(updatedOrgs as OrganizationProfile[]);

                              await api.updateOrganization(org.id, { status: newStatus });
                              success(
                                `Organization ${newStatus === 'Active' ? 'activated' : 'deactivated'}`
                              );
                              storeFetchOrganizations?.(true); // Sync store
                            } catch (err) {
                              console.error(err);
                              toastError('Failed to update status');
                              storeFetchOrganizations?.(true); // Revert on error
                            }
                          }}
                          className={`
                            relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent focus:ring-blue-500
                            ${org.status === 'Inactive' ? 'bg-slate-700' : 'bg-emerald-500'}
                          `}
                        >
                          <span
                            className={`
                              inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                              ${org.status === 'Inactive' ? 'translate-x-0.5' : 'translate-x-4'}
                            `}
                          />
                        </button>
                        <span
                          className={`text-xs font-bold uppercase tracking-wider ${
                            org.status === 'Inactive' ? 'text-slate-500' : 'text-emerald-400'
                          }`}
                        >
                          {org.status === 'Inactive' ? 'Inactive' : 'Active'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-3">
                    <Button
                      variant={currentOrganization?.id === org.id ? 'secondary' : 'primary'}
                      className={`flex-1 text-xs font-bold uppercase tracking-wider ${currentOrganization?.id === org.id ? 'bg-emerald-500 text-emerald-950 hover:bg-emerald-400' : 'bg-blue-600 text-white hover:bg-blue-500'}`}
                      onClick={() => toggleSelectOrg(org)}
                    >
                      {currentOrganization?.id === org.id ? 'Currently Active' : 'Select Context'}
                    </Button>

                    {org.website && (
                      <a
                        href={org.website}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2.5 rounded-xl bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
                      >
                        <Globe size={18} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-800/40 border border-white/5 rounded-2xl overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-900/80 text-[0.65rem] uppercase text-slate-400 font-black tracking-widest border-b border-white/5">
                  <tr>
                    <th className="px-6 py-4">Organization</th>
                    <th className="px-6 py-4">Code</th>
                    <th className="px-6 py-4">Industry</th>
                    <th className="px-6 py-4">Location</th>
                    <th className="px-6 py-4 text-center">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredOrgs.map((org) => (
                    <tr
                      key={org.id}
                      className={`group hover:bg-slate-800/60 transition-colors ${currentOrganization?.id === org.id ? 'bg-emerald-900/5' : ''}`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center text-slate-400 shrink-0">
                            {org.logo ? (
                              <img
                                src={org.logo}
                                className="w-full h-full rounded-lg object-cover"
                              />
                            ) : (
                              <Building size={18} />
                            )}
                          </div>
                          <div>
                            <p
                              className={`text-sm font-bold ${currentOrganization?.id === org.id ? 'text-emerald-400' : 'text-white'}`}
                            >
                              {org.name}
                            </p>
                            {currentOrganization?.id === org.id && (
                              <span className="text-[10px] text-emerald-500/80 font-medium">
                                Active Context
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Badge
                          variant="slate"
                          className="font-mono text-xs text-slate-300 border-slate-700"
                        >
                          {org.code}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-300">{org.industry || '-'}</td>
                      <td className="px-6 py-4 text-sm text-slate-300">
                        <div className="flex items-center gap-1.5">
                          <MapPin size={14} className="text-slate-500" />
                          {org.city}, {org.country}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <Badge
                          variant="secondary"
                          className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        >
                          Active
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant={currentOrganization?.id === org.id ? 'secondary' : 'outline'}
                            className={`h-8 text-[10px] uppercase font-bold tracking-wider ${currentOrganization?.id === org.id ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' : 'border-slate-700 text-slate-300'}`}
                            onClick={() => toggleSelectOrg(org)}
                          >
                            {currentOrganization?.id === org.id ? 'Active' : 'Select'}
                          </Button>
                          <div className="h-4 w-px bg-slate-700 mx-1"></div>
                          <button
                            onClick={() => handleEdit(org)}
                            className="p-1.5 text-slate-400 hover:text-blue-400 transition-colors"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button
                            onClick={() => initiateDelete(org)}
                            className="p-1.5 text-slate-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      <OrganizationFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        initialData={selectedOrg}
      />

      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ ...confirmModal, isOpen: false })}
        onConfirm={handleConfirmDelete}
        title="Delete Organization"
        message={`Are you sure you want to delete ${confirmModal.orgName}? This action cannot be undone and will remove all associated data.`}
        confirmLabel="Delete Organization"
        variant="danger"
      />
    </div>
  );
};

export default OrganizationManagement;
