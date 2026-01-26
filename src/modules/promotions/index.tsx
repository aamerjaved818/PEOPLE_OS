import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Calendar,
  Clock,
  FileText,
  Plus,
  Filter,
  ArrowUpRight,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';
import api from '@/services/api';
import { PromotionCycle, PromotionRequest } from '@/types';
import CreateCycleModal from './CreateCycleModal';
import CreateRequestModal from './CreateRequestModal';
import ActionModal from './ActionModal';

const PromotionModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cycles' | 'requests' | 'approvals'>('requests');
  const [cycles, setCycles] = useState<PromotionCycle[]>([]);
  const [requests, setRequests] = useState<PromotionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCycleModal, setShowCycleModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<PromotionRequest | null>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [cycleData, requestData] = await Promise.all([
        api.getPromotionCycles(),
        api.getPromotionRequests(),
      ]);
      setCycles(cycleData);
      setRequests(requestData);
    } catch (error) {
      console.error('Failed to fetch promotion data', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Implemented':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'Rejected':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      case 'Pending':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-blue-100 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden relative group">
        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-600 rounded-2xl shadow-indigo-200 shadow-lg">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-slate-800 tracking-tight">
                Performance Rewards
              </h1>
              <p className="text-slate-500 font-medium">
                Manage annual increments and career advancements.
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-4 relative z-10">
          <button
            onClick={() => setShowCycleModal(true)}
            className="flex items-center gap-2 bg-white text-indigo-600 px-6 py-4 rounded-2xl font-bold hover:bg-indigo-50 transition-all shadow-sm border border-indigo-100 hover:scale-105 active:scale-95"
          >
            <Calendar className="w-5 h-5" />
            New Cycle
          </button>
          <button
            onClick={() => setShowRequestModal(true)}
            className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-4 rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100 hover:scale-105 active:scale-95"
          >
            <Plus className="w-5 h-5" />
            New Request
          </button>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50 group-hover:opacity-80 transition-opacity"></div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex p-1.5 bg-slate-100/80 backdrop-blur-sm rounded-2xl w-fit border border-slate-200/50">
        {[
          { id: 'requests', label: 'Proposals', icon: FileText },
          { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
          { id: 'cycles', label: 'Review Cycles', icon: Calendar },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-8 py-3.5 rounded-xl font-bold transition-all flex items-center gap-2.5 ${
              activeTab === tab.id
                ? 'bg-white text-indigo-600 shadow-sm border border-slate-200/30'
                : 'text-slate-500 hover:text-slate-800 hover:bg-white/50'
            }`}
          >
            <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? 'animate-bounce' : ''}`} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="min-h-[600px]">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-500 font-bold animate-pulse">Syncing promotion records...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-8">
            {activeTab === 'requests' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between px-2">
                  <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <FileText className="w-6 h-6 text-slate-400" />
                    Pending Proposals
                  </h3>
                  <div className="flex gap-2">
                    <button className="p-2.5 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors shadow-sm">
                      <Filter className="w-5 h-5 text-slate-500" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {requests.length === 0 ? (
                    <div className="col-span-full py-20 bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-center">
                      <div className="p-4 bg-white rounded-2xl shadow-sm mb-4">
                        <FileText className="w-10 h-10 text-slate-300" />
                      </div>
                      <h4 className="text-lg font-bold text-slate-800">No proposals found</h4>
                      <p className="text-slate-500 mt-1 max-w-xs">
                        Start by creating a new increment or promotion request for your team.
                      </p>
                    </div>
                  ) : (
                    requests.map((req) => (
                      <div
                        key={req.id}
                        className="bg-white border border-slate-100 p-6 rounded-[2rem] shadow-sm hover:shadow-xl transition-all group border-b-4 border-b-transparent hover:border-b-indigo-500"
                      >
                        <div className="flex justify-between items-start mb-6">
                          <span
                            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest border ${getStatusColor(req.status)}`}
                          >
                            {req.status}
                          </span>
                          <span className="text-slate-400 text-xs font-bold">{req.type}</span>
                        </div>

                        <div className="flex items-center gap-4 mb-6">
                          <div className="h-14 w-14 bg-slate-100 rounded-2xl flex items-center justify-center font-black text-slate-400 text-xl border border-slate-200 overflow-hidden">
                            {req.employee?.avatar ? (
                              <img
                                src={req.employee.avatar}
                                alt=""
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              req.employee?.name?.[0] || 'E'
                            )}
                          </div>
                          <div>
                            <h4 className="font-black text-slate-800 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">
                              {req.employee?.name || 'Unknown Employee'}
                            </h4>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                              {req.currentDesignation?.name || 'Staff'}
                            </p>
                          </div>
                        </div>

                        <div className="space-y-4 pt-4 border-t border-slate-50">
                          <div className="flex justify-between items-center bg-slate-50 p-3 rounded-2xl">
                            <div className="text-center flex-1">
                              <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter mb-1">
                                Current
                              </p>
                              <p className="text-sm font-black text-slate-600">
                                ${req.currentSalary.toLocaleString()}
                              </p>
                            </div>
                            <div className="p-1 px-2">
                              <ArrowUpRight className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div className="text-center flex-1">
                              <p className="text-[10px] font-black text-indigo-400 uppercase tracking-tighter mb-1">
                                Proposed
                              </p>
                              <p className="text-sm font-black text-indigo-600">
                                ${req.proposedSalary.toLocaleString()}
                              </p>
                            </div>
                          </div>

                          {req.proposedDesignationId && (
                            <div className="flex items-center gap-3 p-3 bg-white border border-slate-100 rounded-2xl">
                              <div className="p-2 bg-purple-50 rounded-xl">
                                <ArrowUpRight className="w-4 h-4 text-purple-600" />
                              </div>
                              <div>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                                  New Role
                                </p>
                                <p className="text-xs font-black text-slate-700">
                                  {req.proposedDesignation?.name}
                                </p>
                              </div>
                            </div>
                          )}

                          <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 px-1">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" /> Effective: {req.effectiveDate}
                            </span>
                            <span className="flex items-center gap-1 group-hover:text-indigo-600">
                              Details <ChevronRight className="w-3 h-3" />
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {activeTab === 'cycles' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between px-2">
                  <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <Calendar className="w-6 h-6 text-slate-400" />
                    Active Review Cycles
                  </h3>
                </div>

                <div className="bg-white border border-slate-100 rounded-[2.5rem] overflow-hidden shadow-sm">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-slate-50/50">
                        <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-100">
                          Cycle Title
                        </th>
                        <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-100">
                          Status
                        </th>
                        <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-100">
                          Range
                        </th>
                        <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-100">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {cycles.length === 0 ? (
                        <tr>
                          <td
                            colSpan={4}
                            className="px-8 py-20 text-center text-slate-500 font-bold"
                          >
                            No review cycles defined.
                          </td>
                        </tr>
                      ) : (
                        cycles.map((cycle) => (
                          <tr
                            key={cycle.id}
                            className="hover:bg-slate-50/50 transition-colors group"
                          >
                            <td className="px-8 py-6">
                              <p className="font-black text-slate-800 group-hover:text-indigo-600 transition-colors tracking-tight">
                                {cycle.title}
                              </p>
                              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                Modified: {new Date(cycle.createdAt).toLocaleDateString()}
                              </p>
                            </td>
                            <td className="px-8 py-6">
                              <span
                                className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${
                                  cycle.status === 'Open'
                                    ? 'bg-indigo-50 text-indigo-600 border-indigo-100'
                                    : 'bg-slate-100 text-slate-500 border-slate-200'
                                }`}
                              >
                                {cycle.status}
                              </span>
                            </td>
                            <td className="px-8 py-6 text-sm font-bold text-slate-600">
                              {cycle.startDate} — {cycle.endDate || 'Ongoing'}
                            </td>
                            <td className="px-8 py-6">
                              <button className="text-indigo-600 font-black text-xs uppercase tracking-widest hover:underline">
                                Manage
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'approvals' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between px-2">
                  <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <ShieldCheck className="w-6 h-6 text-slate-400" />
                    Pending Approvals
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {requests.filter((r) =>
                    ['Pending', 'HR_Approved', 'Finance_Approved'].includes(r.status)
                  ).length === 0 ? (
                    <div className="col-span-full flex flex-col items-center justify-center py-32 space-y-4 bg-white rounded-[3rem] border border-slate-100 shadow-sm">
                      <div className="p-6 bg-slate-50 rounded-full">
                        <ShieldCheck className="w-16 h-16 text-slate-200" />
                      </div>
                      <h3 className="text-2xl font-black text-slate-800 tracking-tight">
                        Approval Queue Empty
                      </h3>
                      <p className="text-slate-500 font-medium text-center max-w-sm">
                        You have no pending approvals in your queue at the moment.
                      </p>
                    </div>
                  ) : (
                    requests
                      .filter((r) =>
                        ['Pending', 'HR_Approved', 'Finance_Approved'].includes(r.status)
                      )
                      .map((req) => (
                        <div
                          key={req.id}
                          className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex flex-col gap-4"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex items-center gap-3">
                              <div className="h-12 w-12 bg-indigo-50 rounded-xl flex items-center justify-center font-black text-indigo-600 border border-indigo-100 overflow-hidden">
                                {req.employee?.avatar ? (
                                  <img
                                    src={req.employee.avatar}
                                    alt=""
                                    className="w-full h-full object-cover"
                                  />
                                ) : (
                                  req.employee?.name?.[0] || 'U'
                                )}
                              </div>
                              <div>
                                <h4 className="font-bold text-slate-800">{req.employee?.name}</h4>
                                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                                  {req.type}
                                </p>
                              </div>
                            </div>
                            <span
                              className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${getStatusColor(req.status)}`}
                            >
                              {req.status}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-100">
                            <div>
                              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                Current
                              </p>
                              <p className="font-bold text-slate-700">
                                ${req.currentSalary.toLocaleString()}
                              </p>
                            </div>
                            <div>
                              <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                                Proposed
                              </p>
                              <p className="font-bold text-indigo-600">
                                ${req.proposedSalary.toLocaleString()}
                              </p>
                            </div>
                          </div>

                          <button
                            onClick={() => setSelectedRequest(req)}
                            className="w-full py-3 bg-slate-800 text-white rounded-xl font-bold hover:bg-slate-900 transition-all shadow-lg shadow-slate-200 active:scale-95"
                          >
                            Review Proposal
                          </button>
                        </div>
                      ))
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <ActionModal
        isOpen={!!selectedRequest}
        onClose={() => setSelectedRequest(null)}
        request={selectedRequest}
        onSuccess={(updated) => {
          setRequests(requests.map((r) => (r.id === updated.id ? updated : r)));
          setSelectedRequest(null);
        }}
      />

      <CreateCycleModal
        isOpen={showCycleModal}
        onClose={() => setShowCycleModal(false)}
        onSuccess={(cycle) => {
          setCycles([cycle, ...cycles]);
          setShowCycleModal(false);
        }}
      />

      <CreateRequestModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        cycles={cycles}
        onSuccess={(req) => {
          setRequests([req, ...requests]);
          setShowRequestModal(false);
        }}
      />
    </div>
  );
};

export default PromotionModule;
