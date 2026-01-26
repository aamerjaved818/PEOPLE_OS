import { useState, useEffect, useCallback } from 'react';
import { Shield, Search, Plus, Calendar } from 'lucide-react';
import api from '@/services/api';
import { useSystemStore } from '@/system/systemStore';

const ComplianceSubmodule = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const orgId = useSystemStore((state) => state.organization?.id);

  const [showModal, setShowModal] = useState(false);
  const [newRecord, setNewRecord] = useState<any>({
    license_name: '',
    provider: '',
    expiry_date: new Date().toISOString(),
    status: 'Active',
    reminder_days_before: 30,
  });

  const loadCompliance = useCallback(async () => {
    try {
      if (!orgId) {
        return;
      }
      setIsLoading(true);
      const data = await api.getComplianceRecords(orgId);
      setRecords(data);
    } catch (error) {
      console.error('Failed to load compliance records', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId) {
      loadCompliance();
    }
  }, [orgId, loadCompliance]);

  const handleSave = async () => {
    if (!newRecord.license_name || !newRecord.expiry_date || !orgId) {
      return;
    }
    try {
      await api.createComplianceRecord(newRecord, orgId);
      setShowModal(false);
      setNewRecord({
        license_name: '',
        provider: '',
        expiry_date: new Date().toISOString(),
        status: 'Active',
        reminder_days_before: 30,
      });
      loadCompliance();
    } catch (error) {
      console.error('Failed to add compliance record', error);
    }
  };

  const filteredRecords = records.filter(
    (r) =>
      r.license_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.provider?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (expiryDate: string) => {
    const days = Math.ceil(
      (new Date(expiryDate).getTime() - new Date().getTime()) / (1000 * 3600 * 24)
    );
    if (days < 0) {
      return 'text-red-500 bg-red-500/10';
    }
    if (days < 30) {
      return 'text-yellow-500 bg-yellow-500/10';
    }
    return 'text-green-500 bg-green-500/10';
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/40"
        >
          <Plus size={18} />
          Add Document
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/50 border-b border-slate-700">
                  <th className="px-6 py-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
                    Document Name
                  </th>
                  <th className="px-6 py-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
                    Provider
                  </th>
                  <th className="px-6 py-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
                    Expiry Date
                  </th>
                  <th className="px-6 py-4 text-slate-400 font-bold text-xs uppercase tracking-widest">
                    Status
                  </th>
                  <th className="px-6 py-4 text-slate-400 font-bold text-xs uppercase tracking-widest text-right">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                          <Shield size={16} className="text-blue-400" />
                        </div>
                        <span className="text-white font-medium">{record.license_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400">{record.provider || 'N/A'}</td>
                    <td className="px-6 py-4 text-slate-400">
                      <div className="flex items-center gap-2">
                        <Calendar size={14} />
                        {new Date(record.expiry_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${getStatusColor(record.expiry_date)}`}
                      >
                        {new Date(record.expiry_date) < new Date() ? 'Expired' : 'Active'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-blue-500 hover:text-blue-400 font-bold text-xs uppercase tracking-widest">
                        Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredRecords.length === 0 && (
            <div className="py-20 text-center">
              <Shield size={48} className="mx-auto text-slate-700 mb-4" />
              <p className="text-slate-500 font-medium">No documents found</p>
            </div>
          )}
        </div>
      )}

      {/* Add Compliance Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">New Document</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Document Name
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  placeholder="e.g. Fire Safety Certificate"
                  value={newRecord.license_name}
                  onChange={(e) => setNewRecord({ ...newRecord, license_name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Provider / Issuer
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newRecord.provider}
                  onChange={(e) => setNewRecord({ ...newRecord, provider: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Expiry Date
                  </label>
                  <input
                    type="date"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newRecord.expiry_date.split('T')[0]}
                    onChange={(e) =>
                      setNewRecord({
                        ...newRecord,
                        expiry_date: new Date(e.target.value).toISOString(),
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Reminder (Days Before)
                  </label>
                  <input
                    type="number"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newRecord.reminder_days_before}
                    onChange={(e) =>
                      setNewRecord({ ...newRecord, reminder_days_before: parseInt(e.target.value) })
                    }
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
                Save Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceSubmodule;
