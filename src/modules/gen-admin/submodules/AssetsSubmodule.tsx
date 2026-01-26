import { useState, useMemo, useEffect, useCallback } from 'react';
import { Package, Plus, RefreshCw, Search } from 'lucide-react';
import { Asset } from '@/types';
import api from '@/services/api';

import { useSystemStore } from '@/system/systemStore';

const AssetsSubmodule = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const orgId = useSystemStore((state) => state.organization?.id);

  const [showModal, setShowModal] = useState(false);
  const [newAsset, setNewAsset] = useState<Partial<Asset>>({
    name: '',
    serialNumber: '',
    category: 'IT Equipment',
    status: 'Active',
  });

  const loadData = useCallback(async () => {
    if (!orgId) {
      return;
    }
    setIsLoading(true);
    try {
      const data = await api.getAssets(orgId);
      setAssets(data);
    } catch (error) {
      console.error('Failed to load assets', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSave = async () => {
    if (!newAsset.name || !newAsset.serialNumber || !orgId) {
      return;
    }
    try {
      await api.createAsset(newAsset, orgId);
      setShowModal(false);
      setNewAsset({ name: '', serialNumber: '', category: 'IT Equipment', status: 'Active' });
      loadData();
    } catch (error) {
      console.error('Failed to create asset', error);
    }
  };

  const filteredAssets = useMemo(() => {
    return assets.filter(
      (a) =>
        a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.serialNumber.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [assets, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Search & Actions */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input
            type="text"
            placeholder="Search items by name or S/N..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 outline-none focus:border-blue-500 transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
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
            <Plus size={20} />
            Add Item
          </button>
        </div>
      </div>

      {/* Asset Table */}
      <div className="bg-slate-800 border border-slate-700 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 border-b border-slate-700">
                <th className="px-6 py-5 text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Item Details
                </th>
                <th className="px-6 py-5 text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Category
                </th>
                <th className="px-6 py-5 text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Status
                </th>
                <th className="px-6 py-5 text-sm font-bold text-slate-400 uppercase tracking-widest">
                  Holder
                </th>
                <th className="px-6 py-5 text-sm font-bold text-slate-400 uppercase tracking-widest text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-20 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-3">
                      <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                      <p className="font-medium">Loading inventory...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredAssets.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-20 text-center text-slate-500">
                    <Package className="w-12 h-12 mx-auto mb-4 opacity-20" />
                    <p className="text-xl font-bold">No items found</p>
                    <p className="text-slate-600">Try adjusting your search or add a new item.</p>
                  </td>
                </tr>
              ) : (
                filteredAssets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-slate-700/30 transition-colors group">
                    <td className="px-6 py-6" title={asset.specifications || ''}>
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-500 border border-blue-500/20">
                          <Package size={24} />
                        </div>
                        <div>
                          <p className="text-white font-bold tracking-tight">{asset.name}</p>
                          <p className="text-slate-500 text-xs font-mono uppercase mt-1">
                            {asset.serialNumber}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-6 font-medium text-slate-400">{asset.category}</td>
                    <td className="px-6 py-6">
                      <span
                        className={`
                        px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest border
                        ${
                          asset.status === 'Active'
                            ? 'bg-green-500/10 text-green-500 border-green-500/20'
                            : asset.status === 'Maintenance'
                              ? 'bg-orange-500/10 text-orange-500 border-orange-500/20'
                              : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                        }
                      `}
                      >
                        {asset.status}
                      </span>
                    </td>
                    <td className="px-6 py-6">
                      <div className="flex items-center gap-2 text-slate-300 font-medium">
                        {asset.employeeId || 'Unassigned'}
                      </div>
                    </td>
                    <td className="px-6 py-6 text-right">
                      <button className="text-blue-400 hover:text-blue-300 font-bold text-sm tracking-widest uppercase py-2 px-4 rounded-lg bg-blue-500/5 hover:bg-blue-500/10 transition-all">
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Basic Modal Implementation */}
      {showModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">Add New Item</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Item Name
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newAsset.name}
                  onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Serial Number / Asset ID
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newAsset.serialNumber}
                  onChange={(e) => setNewAsset({ ...newAsset, serialNumber: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Category
                  </label>
                  <select
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newAsset.category}
                    onChange={(e) => setNewAsset({ ...newAsset, category: e.target.value })}
                  >
                    <option>IT Equipment</option>
                    <option>Office Furniture</option>
                    <option>Laboratory Tools</option>
                    <option>Generic Fixed Asset</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Initial Status
                  </label>
                  <select
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newAsset.status}
                    onChange={(e) =>
                      setNewAsset({
                        ...newAsset,
                        status: e.target.value as 'Active' | 'Maintenance' | 'Retired' | 'Disposed',
                      })
                    }
                  >
                    <option>Active</option>
                    <option>Maintenance</option>
                    <option>Retired</option>
                    <option>Disposed</option>
                  </select>
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
                Save Item
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetsSubmodule;
