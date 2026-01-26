import { useState, useMemo, useEffect, useCallback } from 'react';
import {
  Users,
  Search,
  UserPlus,
  RefreshCw,
  Clock,
  LogOut,
  Building,
  Check,
  BellRing,
  IdCard,
} from 'lucide-react';
import { VisitorNode } from '@/types';
import api from '@/services/api';
import { HorizontalTabs } from '@/components/ui/HorizontalTabs';
import { useSystemStore } from '@/system/systemStore';

const VisitorsSubmodule = () => {
  const [activeTab, setActiveTab] = useState<'log' | 'requests'>('log');
  const [visitors, setVisitors] = useState<VisitorNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const orgId = useSystemStore((state) => state.organization?.id);

  const [showModal, setShowModal] = useState(false);
  const [newVisitor, setNewVisitor] = useState<Partial<VisitorNode>>({
    name: '',
    organization: '',
    purpose: '',
    identificationNumber: '',
    badgeNumber: '',
    checkIn: new Date().toISOString(),
    status: 'Checked-In', // Default
  });

  const loadData = useCallback(async () => {
    if (!orgId) {
      return;
    }
    setIsLoading(true);
    try {
      const data = await api.getVisitors(orgId);
      setVisitors(data);
    } catch (error) {
      console.error('Failed to load visitors', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCheckout = async (visitorId: string) => {
    try {
      await api.checkoutVisitor(visitorId);
      await loadData();
    } catch (error) {
      console.error('Checkout failed', error);
    }
  };

  const handleSave = async () => {
    if (!newVisitor.name || !newVisitor.purpose || !orgId) {
      return;
    }
    try {
      // If we are in 'requests' tab, let's create it as 'Pending' or 'Expected'
      const status = activeTab === 'requests' ? 'Expected' : 'Checked-In';
      await api.createVisitor({ ...newVisitor, status }, orgId);
      setShowModal(false);
      setNewVisitor({
        name: '',
        organization: '',
        purpose: '',
        identificationNumber: '',
        badgeNumber: '',
        checkIn: new Date().toISOString(),
        status: 'Checked-In',
      });
      loadData();
    } catch (error) {
      console.error('Failed to register visitor', error);
    }
  };

  const filteredVisitors = useMemo(() => {
    return visitors.filter((v) => {
      const matchesSearch =
        v.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.organization?.toLowerCase().includes(searchTerm.toLowerCase());

      const isRequest = v.status === 'Expected';
      const matchesTab = activeTab === 'log' ? !isRequest : isRequest;

      return matchesSearch && matchesTab;
    });
  }, [visitors, searchTerm, activeTab]);

  const stats = [
    {
      label: 'Guests On-Site',
      value: visitors.filter((v) => v.status === 'Checked-In').length,
      icon: Users,
      color: 'text-blue-500 bg-blue-500/10',
    },
    {
      label: 'Expected / Pending',
      value: visitors.filter((v) => v.status === 'Expected').length,
      icon: BellRing,
      color: 'text-orange-500 bg-orange-500/10',
    },
    {
      label: 'Total Today',
      value: visitors.filter(
        (v) => new Date(v.checkIn).toDateString() === new Date().toDateString()
      ).length,
      icon: IdCard,
      color: 'text-green-500 bg-green-500/10',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((s, i) => (
          <div
            key={i}
            className="bg-slate-800 border border-slate-700 p-6 rounded-3xl flex items-center justify-between"
          >
            <div>
              <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">
                {s.label}
              </p>
              <h3 className="text-3xl font-bold text-white">{s.value}</h3>
            </div>
            <div className={`p-4 rounded-2xl ${s.color}`}>
              <s.icon size={24} />
            </div>
          </div>
        ))}
      </div>

      {/* Tabs & Actions */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-800/50 p-4 rounded-2xl border border-slate-700">
        <div className="flex flex-col md:flex-row items-center gap-6 w-full md:w-auto">
          <HorizontalTabs
            tabs={[
              { id: 'log', label: 'Visitor Log' },
              { id: 'requests', label: 'Requests' },
            ]}
            activeTabId={activeTab}
            onTabChange={(id) => setActiveTab(id as 'log' | 'requests')}
          />
          <div className="relative w-full md:w-72">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input
              type="text"
              placeholder="Search guests..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-200 outline-none focus:border-blue-500 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <button
            onClick={loadData}
            className="p-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-all"
          >
            <RefreshCw size={20} className={isLoading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/20"
          >
            <UserPlus size={20} />
            {activeTab === 'requests' ? 'New Request' : 'Register Guest'}
          </button>
        </div>
      </div>

      {/* Visitors List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isLoading ? (
          <div className="lg:col-span-2 p-20 text-center text-slate-500 bg-slate-800/50 rounded-3xl border border-slate-700 text-xl font-bold">
            <RefreshCw className="w-10 h-10 animate-spin text-blue-500 mx-auto mb-4" />
            Retrieving data...
          </div>
        ) : filteredVisitors.length === 0 ? (
          <div className="lg:col-span-2 p-20 text-center text-slate-500 bg-slate-800/50 rounded-3xl border border-slate-700">
            <Users className="w-16 h-16 opacity-20 mx-auto mb-4" />
            <p className="text-2xl font-bold text-slate-400">No entries found</p>
            <p className="text-slate-600 mt-2">No visitors match the current filter.</p>
          </div>
        ) : (
          filteredVisitors.map((v) => (
            <div
              key={v.id}
              className="bg-slate-800 border border-slate-700 p-6 rounded-3xl group hover:border-blue-500/50 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-slate-700 flex items-center justify-center text-2xl font-bold text-blue-400 border border-slate-600 group-hover:bg-blue-600 group-hover:text-white transition-all">
                    {v.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="text-xl font-bold text-white tracking-tight">{v.name}</h4>
                    <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-widest mt-1">
                      <Building size={12} />
                      {v.organization || 'Individual'}
                    </div>
                  </div>
                </div>
                <span
                  className={`
                    px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border
                    ${
                      v.status === 'Checked-In'
                        ? 'bg-green-500/10 text-green-500 border-green-500/20'
                        : v.status === 'Expected'
                          ? 'bg-orange-500/10 text-orange-500 border-orange-500/20'
                          : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                    }
                  `}
                >
                  {v.status}
                </span>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-700/50">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                    Host & ID
                  </p>
                  <p className="text-slate-200 text-sm font-medium mt-1 truncate">
                    ID: {v.identificationNumber || 'N/A'}
                  </p>
                </div>
                <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-700/50">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                    {v.status === 'Expected' ? 'Expected At' : 'Checked-In At'}
                  </p>
                  <p className="text-slate-200 text-sm font-medium mt-1">
                    {new Date(v.checkIn).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between border-t border-slate-700 pt-6">
                <div className="flex items-center gap-2 text-slate-500 text-sm">
                  <Clock size={16} />
                  Purpose:{' '}
                  <span className="text-slate-300 font-medium truncate max-w-[150px]">
                    {v.purpose}
                  </span>
                </div>
                {v.status === 'Checked-In' && (
                  <button
                    onClick={() => handleCheckout(v.id)}
                    className="flex items-center gap-2 bg-slate-900 hover:bg-red-500/10 text-slate-400 hover:text-red-400 px-4 py-2 rounded-xl border border-slate-700 hover:border-red-500/20 transition-all font-bold text-xs uppercase"
                  >
                    <LogOut size={14} />
                    Sign Out
                  </button>
                )}
                {v.status === 'Expected' && (
                  <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl  transition-all font-bold text-xs uppercase shadow-lg shadow-blue-900/20">
                    <Check size={14} />
                    Check In
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Register Visit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">
              {activeTab === 'requests' ? 'New Entry Request' : 'Register New Guest'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Guest Full Name
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newVisitor.name}
                  onChange={(e) => setNewVisitor({ ...newVisitor, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Company / Organization
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newVisitor.organization}
                  onChange={(e) => setNewVisitor({ ...newVisitor, organization: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Purpose of Visit
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  placeholder="e.g. Sales Meeting, Interview"
                  value={newVisitor.purpose}
                  onChange={(e) => setNewVisitor({ ...newVisitor, purpose: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    ID Number
                  </label>
                  <input
                    type="text"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newVisitor.identificationNumber}
                    onChange={(e) =>
                      setNewVisitor({ ...newVisitor, identificationNumber: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Badge No.
                  </label>
                  <input
                    type="text"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newVisitor.badgeNumber}
                    onChange={(e) => setNewVisitor({ ...newVisitor, badgeNumber: e.target.value })}
                  />
                </div>
              </div>
            </div>
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 rounded-xl transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-900/40"
              >
                {activeTab === 'requests' ? 'Submit Request' : 'Check-In Guest'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisitorsSubmodule;
