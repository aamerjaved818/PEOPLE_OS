import React, { useState, useEffect } from 'react';
import { Building2, Search, Plus, MoreVertical, Globe, MapPin, Activity } from 'lucide-react';
import { api } from '../../../services/api';
import { OrganizationProfile } from '../../../types';
import { Button } from '../../../components/ui/Button';
import ModuleSkeleton from '../../../components/ui/ModuleSkeleton';
import OrganizationFormModal from './OrganizationFormModal';
import { ConfirmationModal } from '../../../components/ui/ConfirmationModal';
import { useToast } from '../../../components/ui/Toast';

const OrganizationList: React.FC = () => {
  const [organizations, setOrganizations] = useState<OrganizationProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState<OrganizationProfile | undefined>(undefined);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  // Confirmation Modal State
  const [confirmModal, setConfirmModal] = useState({
    isOpen: false,
    orgId: '',
    orgName: '',
  });

  const { success, error: toastError } = useToast();

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
      fetchOrganizations();
    } catch (err) {
      console.error(err);
      toastError('Failed to delete organization');
    }
  };

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const data = await api.getOrganizations();
      setOrganizations(data);
    } catch (error) {
      console.error('Failed to fetch organizations', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedOrg(undefined);
    setIsModalOpen(true);
  };

  const handleEdit = (org: OrganizationProfile) => {
    setSelectedOrg(org);
    setIsModalOpen(true);
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
      fetchOrganizations();
      setIsModalOpen(false);
    } catch (err) {
      toastError('Failed to save organization');
      console.error(err);
    }
  };

  const filteredOrgs = organizations.filter(
    (org) =>
      org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      org.code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <ModuleSkeleton />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tight">
            Organization Registry
          </h2>
          <p className="text-slate-400 font-medium text-sm mt-1">
            Manage all registered organizations in the PeopleOS ecosystem
            <span className="ml-2 px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 text-xs font-bold">
              {organizations.length} Total
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search organizations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-900/50 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 w-64 transition-all"
            />
          </div>
          <Button
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl font-bold uppercase tracking-wider text-xs shadow-lg shadow-blue-600/20"
            onClick={handleCreate}
          >
            <Plus size={16} className="mr-2" />
            New Organization
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredOrgs.map((org) => (
          <div
            key={org.id}
            className="group relative bg-slate-800/40 border border-white/5 rounded-2xl p-6 hover:bg-slate-800/60 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-900/10 hover:-translate-y-1"
            onMouseLeave={() => setActiveMenu(null)}
          >
            <div className="absolute top-4 right-4 z-10">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveMenu(activeMenu === org.id ? null : org.id);
                }}
                className={`p-2 rounded-lg transition-colors ${
                  activeMenu === org.id
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                    : 'text-slate-400 hover:bg-white/10 hover:text-white opacity-0 group-hover:opacity-100'
                }`}
              >
                <MoreVertical size={16} />
              </button>

              {activeMenu === org.id && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(org);
                      setActiveMenu(null);
                    }}
                    className="w-full text-left px-4 py-3 text-sm font-medium text-slate-300 hover:bg-white/5 hover:text-white flex items-center gap-2 transition-colors"
                  >
                    Edit Organization
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      initiateDelete(org);
                    }}
                    className="w-full text-left px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-2 transition-colors border-t border-white/5"
                  >
                    Delete Organization
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
                  <Building2 className="text-blue-400" size={32} />
                )}
              </div>
              <div>
                <h3 className="font-bold text-lg text-white leading-tight mb-1">{org.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/5 text-[10px] font-black uppercase tracking-wider text-slate-400">
                    {org.code || 'N/A'}
                  </span>
                  {org.industry && (
                    <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-slate-600" />
                      {org.industry}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="space-y-1">
                <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                  Location
                </span>
                <div className="flex items-center gap-1.5 text-sm font-medium text-slate-300">
                  <MapPin size={14} className="text-indigo-400" />
                  {org.city || 'Unknown'}, {org.country || 'N/A'}
                </div>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                  Status
                </span>
                <div className="flex items-center gap-1.5 text-sm font-medium text-emerald-400">
                  <Activity size={14} />
                  Active
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                {org.website && (
                  <a
                    href={org.website}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors"
                  >
                    <Globe size={16} />
                  </a>
                )}
              </div>
              <Button
                variant="ghost"
                className="text-xs font-bold uppercase tracking-wider text-slate-400 hover:text-white"
                onClick={() => handleEdit(org)}
              >
                View Details
              </Button>
            </div>
          </div>
        ))}
      </div>

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

export default OrganizationList;
