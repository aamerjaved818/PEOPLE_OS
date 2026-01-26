import { useState, useEffect, useCallback } from 'react';
import ErrorBoundary from '@/components/ErrorBoundary';
import { Shield, Package, Users, Building, Truck, LayoutDashboard, Plane } from 'lucide-react';
import { useSystemStore } from '@/system/systemStore';
import AssetsSubmodule from './submodules/AssetsSubmodule';
import VisitorsSubmodule from './submodules/VisitorsSubmodule';
import FacilitiesSubmodule from './submodules/FacilitiesSubmodule';
import FleetSubmodule from './submodules/FleetSubmodule';
import ComplianceSubmodule from './submodules/ComplianceSubmodule';
import TravelSubmodule from './submodules/TravelSubmodule';
import api from '@/services/api'; // Assuming default export based on usage

const GenAdminWrapper: React.FC = () => (
  <ErrorBoundary>
    <div className="h-full w-full overflow-y-auto overscroll-contain custom-scrollbar px-6 md:px-10 pb-10">
      <div className="w-full pb-20">
        <GenAdminComponent />
      </div>
    </div>
  </ErrorBoundary>
);

const GenAdminComponent = () => {
  const tabs = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'assets', label: 'Inventory', icon: Package },
    { id: 'visitors', label: 'Reception', icon: Users },
    { id: 'facilities', label: 'Office Spaces', icon: Building },
    { id: 'fleet', label: 'Vehicles', icon: Truck },
    { id: 'travel', label: 'Travel', icon: Plane }, // New Tab
    { id: 'compliance', label: 'Documents', icon: Shield },
  ];

  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({
    assets: 0,
    visitors: 0,
    bookings: 0,
    watchlist: 0,
    fleet: 0,
  });
  const [activities, setActivities] = useState<any[]>([]);
  const orgId = useSystemStore((state) => state.organization?.id);

  const loadStats = useCallback(async () => {
    try {
      const [assets, visitors, facilities, compliance, vehicles] = await Promise.all([
        api.getAssets(orgId!),
        api.getVisitors(orgId!),
        api.getFacilities(orgId!),
        api.getComplianceRecords(orgId!),
        api.getVehicles(orgId!),
      ]);

      const soon = new Date();
      soon.setDate(soon.getDate() + 30);

      setStats({
        assets: assets.length,
        visitors: visitors.filter((v: any) => v.status === 'Checked-In').length,
        bookings: facilities.filter((f: any) => f.status === 'Occupied').length,
        watchlist: compliance.filter((c: any) => new Date(c.expiry_date) < soon).length,
        fleet: vehicles.length,
      });

      // Generate Activity Feed
      const recentActivities = [
        ...assets.map((a) => ({
          type: 'Asset',
          action: 'Provisioned',
          details: a.name,
          time: a.createdAt,
          icon: Package,
        })),
        ...visitors.map((v) => ({
          type: 'Visitor',
          action: 'Checked In',
          details: v.name,
          time: v.checkIn,
          icon: Users,
        })),
        ...vehicles.map((v) => ({
          type: 'Fleet',
          action: 'Registered',
          details: v.model,
          time: v.createdAt,
          icon: Truck,
        })),
        ...compliance.map((c) => ({
          type: 'Compliance',
          action: 'Record Added',
          details: c.licenseName,
          time: c.createdAt,
          icon: Shield,
        })),
      ]
        .filter((a) => a.time) // Ensure time exists
        .sort((a, b) => new Date(b.time!).getTime() - new Date(a.time!).getTime())
        .slice(0, 10);

      setActivities(recentActivities);
    } catch (error) {
      console.error('Failed to load admin stats', error);
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId && activeTab === 'dashboard') {
      loadStats();
    }
  }, [orgId, activeTab, loadStats]);

  return (
    <div className="p-6 max-w-7xl mx-auto pt-4">
      {/* Modern Tab Navigation */}
      <div className="flex gap-2 mb-8 bg-slate-900/50 p-1.5 rounded-2xl border border-slate-800 w-fit">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-6 py-3 rounded-xl transition-all duration-300
                ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/40'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }
              `}
            >
              <Icon size={18} />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Module Content Area */}
      <div className="space-y-6">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Quick Stats */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-6 rounded-3xl text-white shadow-xl">
              <p className="opacity-80 font-medium">Total Assets</p>
              <h2 className="text-4xl font-bold mt-2">{stats.assets}</h2>
              <div className="mt-4 pt-4 border-t border-white/20 flex justify-between">
                <span>Items in Inventory</span>
                <span className="bg-white/20 px-2 py-0.5 rounded text-sm">
                  {stats.fleet} Vehicles
                </span>
              </div>
            </div>

            <div className="bg-slate-800 border border-slate-700 p-6 rounded-3xl shadow-xl hover:border-slate-600 transition-all">
              <p className="text-slate-400 font-medium">Guests Today</p>
              <h2 className="text-4xl font-bold mt-2 text-white">{stats.visitors}</h2>
              <div className="mt-4 flex gap-2">
                <span className="bg-green-500/10 text-green-500 px-3 py-1 rounded-full text-xs font-bold">
                  On-site now
                </span>
              </div>
            </div>

            <div className="bg-slate-800 border border-slate-700 p-6 rounded-3xl shadow-xl hover:border-slate-600 transition-all">
              <p className="text-slate-400 font-medium">Rooms Occupied</p>
              <h2 className="text-4xl font-bold mt-2 text-white">{stats.bookings}</h2>
              <div className="mt-4 text-slate-500 text-sm">Active bookings</div>
            </div>

            {/* Activity Feed */}
            <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-3xl p-6 h-[400px]">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">Recent Activity</h3>
                <button className="text-blue-500 text-sm font-semibold hover:underline">
                  View All
                </button>
              </div>
              <div className="space-y-4 overflow-y-auto h-[300px] pr-2 custom-scrollbar">
                {activities.length === 0 ? (
                  <div className="text-slate-500 text-center py-10">No recent activity</div>
                ) : (
                  activities.map((act, i) => (
                    <div
                      key={i}
                      className="flex gap-4 p-4 bg-slate-900/50 rounded-xl border border-slate-800/50"
                    >
                      <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
                        <act.icon size={20} className="text-blue-400" />
                      </div>
                      <div>
                        <p className="text-white font-medium">
                          {act.action}: <span className="font-light">{act.details}</span>
                        </p>
                        <p className="text-slate-500 text-sm">
                          {act.type} • {new Date(act.time).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Compliance Watchlist */}
            <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 h-[400px]">
              <h3 className="text-xl font-bold text-white mb-6">Upcoming Renewals</h3>
              <div className="space-y-4">
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl">
                  <p className="text-red-400 font-bold text-sm">EXPIRING SOON</p>
                  <p className="text-white font-medium mt-1">Vehicle Insurance - Pool A</p>
                  <p className="text-slate-400 text-xs mt-1">Expires in 3 days</p>
                </div>
                <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl">
                  <p className="text-yellow-400 font-bold text-sm">RENEWAL DUE</p>
                  <p className="text-white font-medium mt-1">Fire Safety Certificate</p>
                  <p className="text-slate-400 text-xs mt-1">Due: Feb 15, 2026</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'assets' && <AssetsSubmodule />}
        {activeTab === 'visitors' && <VisitorsSubmodule />}
        {activeTab === 'facilities' && <FacilitiesSubmodule />}
        {activeTab === 'fleet' && <FleetSubmodule />}
        {activeTab === 'travel' && <TravelSubmodule />}
        {activeTab === 'compliance' && <ComplianceSubmodule />}
      </div>
    </div>
  );
};

export default GenAdminWrapper;
