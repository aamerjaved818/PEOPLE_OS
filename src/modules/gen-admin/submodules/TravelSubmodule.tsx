import React, { useState, useEffect, useCallback } from 'react';
import { Plane, Map, Globe, Calendar, FileText, CheckCircle, XCircle } from 'lucide-react';
import api from '@/services/api';
import { useSystemStore } from '@/system/systemStore';
import { useOrgStore } from '@/store/orgStore';
import { TravelRequest } from '@/types';

const TravelSubmodule: React.FC = () => {
  const [requests, setRequests] = useState<TravelRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newTrip, setNewTrip] = useState<Partial<TravelRequest>>({
    destination: '',
    departureDate: '',
    returnDate: '',
    reason: '',
    budget: 0,
  });

  const orgId = useSystemStore((state) => state.organization?.id);
  const user = useOrgStore((state) => state.currentUser);

  const loadTravelRequests = useCallback(async () => {
    if (!orgId) {
      return;
    }
    setIsLoading(true);
    try {
      const data = await api.getTravelRequests(orgId);
      setRequests(data);
    } catch (error) {
      console.error('Failed to load travel requests', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId) {
      loadTravelRequests();
    }
  }, [orgId, loadTravelRequests]);

  const handleSave = async () => {
    if (!orgId || !newTrip.destination || !newTrip.departureDate) {
      return;
    }
    try {
      await api.createTravelRequest(
        {
          ...newTrip,
          employeeId: user?.employeeId || 'EMP-000', // Fallback if not linked
          employeeName: user?.name,
          status: 'Pending',
        },
        orgId
      );
      setShowModal(false);
      setNewTrip({ destination: '', departureDate: '', returnDate: '', reason: '', budget: 0 });
      loadTravelRequests();
    } catch (error) {
      console.error('Failed to create travel request', error);
    }
  };

  const updateStatus = async (id: string, status: string) => {
    if (!orgId) {
      return;
    }
    try {
      await api.updateTravelRequestStatus(id, status, orgId);
      loadTravelRequests();
    } catch (error) {
      console.error('Failed to update status', error);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 animate-in slide-in-from-bottom-8 duration-700">
      <div className="lg:col-span-8 bg-card bg-slate-800 rounded-[2rem] border border-slate-700 shadow-2xl overflow-hidden min-h-[37.5rem] flex flex-col">
        <div className="p-12 border-b border-slate-700 flex items-center justify-between mb-12">
          <div>
            <h3 className="text-3xl font-black text-white tracking-tight uppercase leading-none">
              Global Mobility Ledger
            </h3>
            <p className="text-slate-400 mt-2 font-medium">
              Manage and track employee travel requisitions
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 text-white px-10 py-4 rounded-[1.375rem] font-black uppercase text-[0.625rem] tracking-widest flex items-center gap-4 shadow-xl hover:scale-105 transition-all"
          >
            <Plane size={18} /> Plan New Route
          </button>
        </div>

        <div className="space-y-6 px-10 pb-10 flex-1 overflow-y-auto custom-scrollbar">
          {isLoading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : requests.length === 0 ? (
            <div className="text-center py-20 text-slate-500">
              <Globe size={48} className="mx-auto mb-4 opacity-20" />
              <p>No active travel protocols initiated.</p>
            </div>
          ) : (
            requests.map((trip) => (
              <div
                key={trip.id}
                className="p-10 bg-slate-900 rounded-[3rem] border border-slate-700 flex flex-col md:flex-row items-center justify-between group hover:border-blue-500/30 transition-all gap-8"
              >
                <div className="flex items-center gap-8">
                  <div className="w-20 h-20 bg-slate-800 rounded-[2rem] flex items-center justify-center text-blue-400 shadow-inner group-hover:scale-110 transition-transform">
                    <Map size={32} />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-2xl font-black text-white">{trip.destination}</h4>
                      <span
                        className={`px-3 py-1 rounded-lg text-[0.5625rem] font-black uppercase tracking-widest ${
                          trip.status === 'Approved'
                            ? 'bg-green-500 text-white'
                            : trip.status === 'Rejected'
                              ? 'bg-red-500 text-white'
                              : 'bg-yellow-500 text-white'
                        }`}
                      >
                        {trip.status}
                      </span>
                    </div>
                    <p className="text-[0.6875rem] font-black text-slate-400 uppercase tracking-widest">
                      {trip.employeeName} • {trip.reason}
                    </p>
                  </div>
                </div>
                <div className="text-right flex flex-col items-end gap-2">
                  <div>
                    <p className="text-sm font-black text-white uppercase tracking-widest">
                      {trip.departureDate}
                    </p>
                    <p className="text-[0.5625rem] font-black text-slate-400 uppercase mt-1 tracking-widest">
                      Departure
                    </p>
                  </div>

                  {trip.status === 'Pending' && (
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => updateStatus(trip.id, 'Approved')}
                        className="p-2 hover:bg-green-500/20 text-green-500 rounded-full transition-colors"
                        title="Approve"
                      >
                        <CheckCircle size={18} />
                      </button>
                      <button
                        onClick={() => updateStatus(trip.id, 'Rejected')}
                        className="p-2 hover:bg-red-500/20 text-red-500 rounded-full transition-colors"
                        title="Reject"
                      >
                        <XCircle size={18} />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="lg:col-span-4 space-y-10">
        <div className="bg-slate-950 p-12 rounded-[3.5rem] text-white shadow-2xl relative overflow-hidden group border border-white/5">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-1000">
            <Globe size={240} />
          </div>
          <h4 className="text-[0.625rem] font-black uppercase tracking-[0.4em] text-blue-400 mb-8">
            Mobility Intelligence
          </h4>
          <p className="text-xl font-black leading-tight antialiased mb-10 uppercase">
            Travel Spend{' '}
            <span className="text-blue-400 underline decoration-blue-500/30 underline-offset-8">
              Optimizer
            </span>{' '}
            Active.
          </p>
          <div className="space-y-6">
            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 flex items-center justify-between">
              <div>
                <p className="text-[0.625rem] font-black uppercase tracking-widest text-slate-500">
                  Pending Approvals
                </p>
                <p className="font-black text-xl text-yellow-500 mt-1">
                  {requests.filter((r) => r.status === 'Pending').length}
                </p>
              </div>
              <FileText className="text-yellow-500" />
            </div>
            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 flex items-center justify-between">
              <div>
                <p className="text-[0.625rem] font-black uppercase tracking-widest text-slate-500">
                  Active Trips
                </p>
                <p className="font-black text-xl text-green-500 mt-1">
                  {requests.filter((r) => r.status === 'Approved').length}
                </p>
              </div>
              <Plane className="text-green-500" />
            </div>
          </div>
        </div>
      </div>

      {/* New Trip Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-slate-900 border border-slate-700 p-10 rounded-[2.5rem] w-full max-w-xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
              <Plane size={200} />
            </div>

            <h2 className="text-3xl font-black text-white mb-8 tracking-tight uppercase">
              Initiate Travel Protocol
            </h2>

            <div className="space-y-6 relative z-10">
              <div>
                <label className="text-[0.625rem] font-black text-slate-500 uppercase tracking-widest mb-2 block">
                  Destination Node
                </label>
                <div className="bg-slate-800 rounded-2xl p-1 flex items-center border border-slate-700">
                  <div className="p-3 text-slate-400">
                    <Map size={20} />
                  </div>
                  <input
                    className="bg-transparent w-full text-white font-bold outline-none placeholder:text-slate-600"
                    placeholder="e.g. San Francisco, US"
                    value={newTrip.destination}
                    onChange={(e) => setNewTrip({ ...newTrip, destination: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="text-[0.625rem] font-black text-slate-500 uppercase tracking-widest mb-2 block">
                    Extraction Date
                  </label>
                  <div className="bg-slate-800 rounded-2xl p-1 flex items-center border border-slate-700">
                    <div className="p-3 text-slate-400">
                      <Calendar size={20} />
                    </div>
                    <input
                      type="date"
                      className="bg-transparent w-full text-white font-bold outline-none placeholder:text-slate-600"
                      value={newTrip.departureDate}
                      onChange={(e) => setNewTrip({ ...newTrip, departureDate: e.target.value })}
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[0.625rem] font-black text-slate-500 uppercase tracking-widest mb-2 block">
                    Return Date
                  </label>
                  <div className="bg-slate-800 rounded-2xl p-1 flex items-center border border-slate-700">
                    <div className="p-3 text-slate-400">
                      <Calendar size={20} />
                    </div>
                    <input
                      type="date"
                      className="bg-transparent w-full text-white font-bold outline-none placeholder:text-slate-600"
                      value={newTrip.returnDate}
                      onChange={(e) => setNewTrip({ ...newTrip, returnDate: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[0.625rem] font-black text-slate-500 uppercase tracking-widest mb-2 block">
                  Mission Objective
                </label>
                <textarea
                  className="w-full bg-slate-800 border border-slate-700 rounded-2xl p-4 text-white font-bold outline-none placeholder:text-slate-600 min-h-[100px]"
                  placeholder="State the primary reason for this travel request..."
                  value={newTrip.reason}
                  onChange={(e) => setNewTrip({ ...newTrip, reason: e.target.value })}
                />
              </div>
            </div>

            <div className="mt-10 flex gap-4">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 bg-slate-800 hover:bg-slate-700 text-white py-4 rounded-2xl font-bold uppercase text-xs tracking-widest transition-all"
              >
                Abort
              </button>
              <button
                onClick={handleSave}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-2xl font-bold uppercase text-xs tracking-widest transition-all shadow-lg shadow-blue-900/40"
              >
                Confirm Vector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelSubmodule;
