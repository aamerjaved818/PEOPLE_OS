import { useState, useEffect, useCallback } from 'react';
import { Truck, Search, Plus, MapPin, Gauge, User, Wrench, Edit3, Trash2 } from 'lucide-react';
import api from '@/services/api';
import { useSystemStore } from '@/system/systemStore';
import { Employee } from '@/types';

const FleetSubmodule = () => {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const orgId = useSystemStore((state) => state.organization?.id);

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);

  // Selected Item
  const [selectedVehicle, setSelectedVehicle] = useState<any>(null);

  // Form State
  const [newVehicle, setNewVehicle] = useState<any>({
    model: '',
    plate_number: '',
    category: 'Pool A',
    status: 'Available',
    current_mileage: 0,
  });

  const [assignmentData, setAssignmentData] = useState({ driverId: '' });
  const [maintenanceData, setMaintenanceData] = useState({
    description: '',
    cost: '',
    date: '',
    type: 'Routine',
  });

  const loadVehicles = useCallback(async () => {
    try {
      if (!orgId) {
        return;
      }
      setIsLoading(true);
      const data = await api.getVehicles(orgId);
      setVehicles(data);
    } catch (error) {
      console.error('Failed to load vehicles', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId) {
      loadVehicles();
      loadEmployees();
    }
  }, [orgId, loadVehicles]);

  const loadEmployees = async () => {
    try {
      const data = await api.getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error('Failed to load employees', error);
    }
  };

  const handleSaveVehicle = async () => {
    if (!newVehicle.model || !newVehicle.plate_number || !orgId) {
      return;
    }
    try {
      if (selectedVehicle) {
        await api.updateVehicle(selectedVehicle.id, newVehicle, orgId);
      } else {
        await api.createVehicle(newVehicle, orgId);
      }
      setShowAddModal(false);
      setSelectedVehicle(null);
      setNewVehicle({
        model: '',
        plate_number: '',
        category: 'Pool A',
        status: 'Available',
        current_mileage: 0,
      });
      loadVehicles();
    } catch (error) {
      console.error('Failed to save vehicle', error);
    }
  };

  const handleDeleteVehicle = async (id: string) => {
    if (!confirm('Are you sure you want to delete this vehicle?')) {
      return;
    }
    try {
      await api.deleteVehicle(id);
      loadVehicles();
    } catch (error) {
      console.error('Failed to delete vehicle', error);
    }
  };

  const handleAssignDriver = async () => {
    if (!selectedVehicle || !assignmentData.driverId) {
      return;
    }
    try {
      await api.assignVehicleDriver(selectedVehicle.id, assignmentData.driverId);
      setShowAssignModal(false);
      loadVehicles();
    } catch (error) {
      console.error('Failed to assign driver', error);
    }
  };

  const handleLogMaintenance = async () => {
    if (!selectedVehicle || !maintenanceData.description) {
      return;
    }
    try {
      await api.logVehicleMaintenance(selectedVehicle.id, maintenanceData);
      setShowMaintenanceModal(false);
      setMaintenanceData({ description: '', cost: '', date: '', type: 'Routine' });
      // In a real app, refresh maintenance logs
    } catch (error) {
      console.error('Failed to log maintenance', error);
    }
  };

  const openEdit = (vehicle: any) => {
    setSelectedVehicle(vehicle);
    setNewVehicle({ ...vehicle });
    setShowAddModal(true);
  };

  const filteredVehicles = vehicles.filter(
    (v) =>
      v.model.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.plate_number.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input
            type="text"
            placeholder="Search vehicles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>
        <button
          onClick={() => {
            setSelectedVehicle(null);
            setNewVehicle({
              model: '',
              plate_number: '',
              category: 'Pool A',
              status: 'Available',
              current_mileage: 0,
            });
            setShowAddModal(true);
          }}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/40"
        >
          <Plus size={18} />
          Add Vehicle
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVehicles.map((vehicle) => {
            const assignedDriver = employees.find((e) => e.id === vehicle.driver_id);
            return (
              <div
                key={vehicle.id}
                className="bg-slate-800 border border-slate-700 rounded-2xl p-5 hover:border-slate-600 transition-all group relative"
              >
                <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => openEdit(vehicle)}
                    className="p-2 bg-slate-700 hover:bg-blue-600 rounded-lg text-white transition-colors"
                  >
                    <Edit3 size={14} />
                  </button>
                  <button
                    onClick={() => handleDeleteVehicle(vehicle.id)}
                    className="p-2 bg-slate-700 hover:bg-red-600 rounded-lg text-white transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>

                <div className="flex justify-between items-start mb-4 pr-16">
                  <div className="p-3 bg-slate-900 rounded-xl border border-slate-700 text-blue-500">
                    <Truck size={24} />
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      vehicle.status === 'Available'
                        ? 'bg-green-500/10 text-green-500'
                        : vehicle.status === 'In Use'
                          ? 'bg-blue-500/10 text-blue-500'
                          : 'bg-red-500/10 text-red-500'
                    }`}
                  >
                    {vehicle.status}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-white mb-1">{vehicle.model}</h3>
                <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-4">
                  {vehicle.plate_number}
                </p>

                <div className="space-y-3 bg-slate-900/50 p-4 rounded-xl border border-slate-700/50">
                  <div className="flex items-center gap-3 text-slate-300 text-sm">
                    <Gauge size={16} className="text-slate-500" />
                    <span>{vehicle.current_mileage?.toLocaleString() || 0} km</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-300 text-sm">
                    <MapPin size={16} className="text-slate-500" />
                    <span>{vehicle.category}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-300 text-sm">
                    <User size={16} className="text-slate-500" />
                    <span>{assignedDriver ? assignedDriver.name : 'Unassigned'}</span>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => {
                      setSelectedVehicle(vehicle);
                      // open the assignment modal
                      setShowAssignModal(true);
                    }}
                    className="flex-1 bg-slate-700/50 hover:bg-slate-700 text-white py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-2"
                  >
                    <User size={14} /> Assign
                  </button>
                  <button
                    onClick={() => {
                      setSelectedVehicle(vehicle);
                      setShowMaintenanceModal(true);
                    }}
                    className="flex-1 bg-slate-700/50 hover:bg-slate-700 text-white py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-2"
                  >
                    <Wrench size={14} /> Log Service
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modals */}
      {showAddModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg">
            <h2 className="text-2xl font-bold text-white mb-6">
              {selectedVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
            </h2>
            <div className="space-y-4">
              <input
                placeholder="Vehicle Model"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                value={newVehicle.model}
                onChange={(e) => setNewVehicle({ ...newVehicle, model: e.target.value })}
              />
              <input
                placeholder="Plate Number"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                value={newVehicle.plate_number}
                onChange={(e) => setNewVehicle({ ...newVehicle, plate_number: e.target.value })}
              />
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="number"
                  placeholder="Mileage"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                  value={newVehicle.current_mileage}
                  onChange={(e) =>
                    setNewVehicle({ ...newVehicle, current_mileage: parseInt(e.target.value) })
                  }
                />
                <select
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                  value={newVehicle.category}
                  onChange={(e) => setNewVehicle({ ...newVehicle, category: e.target.value })}
                >
                  <option>Pool A</option>
                  <option>Executive</option>
                  <option>Delivery</option>
                </select>
              </div>
            </div>
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 bg-slate-700 text-white font-bold py-3 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveVehicle}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {showAssignModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Assign Driver</h2>
            <p className="text-slate-400 mb-6 text-sm">
              Assigning vehicle:{' '}
              <span className="text-white font-bold">{selectedVehicle?.model}</span>
            </p>

            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 block">
              Select Employee
            </label>
            <select
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500 mb-6"
              value={assignmentData.driverId}
              onChange={(e) => setAssignmentData({ ...assignmentData, driverId: e.target.value })}
            >
              <option value="">Select a driver...</option>
              {employees.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} - {e.designation}
                </option>
              ))}
            </select>

            <div className="flex gap-3">
              <button
                onClick={() => setShowAssignModal(false)}
                className="flex-1 bg-slate-700 text-white font-bold py-3 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={handleAssignDriver}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl"
              >
                Confirm Assignment
              </button>
            </div>
          </div>
        </div>
      )}

      {showMaintenanceModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Log Maintenance</h2>
            <div className="space-y-4">
              <input
                placeholder="Description (e.g. Oil Change)"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                value={maintenanceData.description}
                onChange={(e) =>
                  setMaintenanceData({ ...maintenanceData, description: e.target.value })
                }
              />
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="number"
                  placeholder="Cost"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                  value={maintenanceData.cost}
                  onChange={(e) => setMaintenanceData({ ...maintenanceData, cost: e.target.value })}
                />
                <input
                  type="date"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"
                  value={maintenanceData.date}
                  onChange={(e) => setMaintenanceData({ ...maintenanceData, date: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button
                onClick={() => setShowMaintenanceModal(false)}
                className="flex-1 bg-slate-700 text-white font-bold py-3 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={handleLogMaintenance}
                className="flex-1 bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-xl"
              >
                Log Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetSubmodule;
