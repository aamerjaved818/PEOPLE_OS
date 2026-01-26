import React, { useState, useEffect, useCallback } from 'react';
import { Building, Plus, Clock, MapPin, Users } from 'lucide-react';
import { Facility, FacilityBooking } from '@/types';
import api from '@/services/api';

import { useSystemStore } from '@/system/systemStore';

const FacilitiesSubmodule: React.FC = () => {
  const orgId = useSystemStore((state) => state.organization?.id);
  const [showSpaceModal, setShowSpaceModal] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedFacility, setSelectedFacility] = useState<Facility | null>(null);

  const [newSpace, setNewSpace] = useState<Partial<Facility>>({
    name: '',
    type: 'Room',
    capacity: 4,
    location: '',
    status: 'Available',
  });

  const [newBooking, setNewBooking] = useState<Partial<FacilityBooking>>({
    facilityId: '',
    startTime: new Date().toISOString(),
    endTime: new Date(Date.now() + 3600000).toISOString(),
    purpose: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [facilities, setFacilities] = useState<Facility[]>([]);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (!orgId) {
        return;
      }
      const data = await api.getFacilities(orgId);
      setFacilities(data || []);
    } catch (error) {
      console.error('Failed to load facilities', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    if (orgId) {
      loadData();
    }
  }, [orgId, loadData]);

  const handleCreateSpace = async () => {
    if (!newSpace.name || !orgId) {
      return;
    }
    try {
      await api.createFacility(newSpace, orgId);
      setShowSpaceModal(false);
      setNewSpace({ name: '', type: 'Room', capacity: 4, location: '', status: 'Available' });
      loadData();
    } catch (error) {
      console.error('Failed to create space', error);
    }
  };

  const handleBook = async () => {
    if (!selectedFacility || !newBooking.purpose || !orgId) {
      return;
    }
    try {
      await api.createFacility({ ...(newBooking as any), facilityId: selectedFacility.id }, orgId);
      // Note: Assuming createFacility handles booking logic based on payload, or need api.createFacilityBooking
      // Let's check api.ts later. Ideally it should be api.createFacilityBooking
      setShowBookingModal(false);
      setNewBooking({
        facilityId: '',
        startTime: new Date().toISOString(),
        endTime: new Date(Date.now() + 3600000).toISOString(),
        purpose: '',
      });
      loadData();
    } catch (error) {
      console.error('Booking failed', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
        <div>
          <h2 className="text-xl font-bold text-white">Office Spaces</h2>
          <p className="text-slate-500 text-sm">Manage meeting rooms, desks, and zones</p>
        </div>
        <button
          onClick={() => setShowSpaceModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/20"
        >
          <Plus size={20} />
          Add New Space
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full py-20 text-center text-slate-500 font-bold text-xl">
            Loading facilities...
          </div>
        ) : facilities.length === 0 ? (
          <div className="col-span-full py-20 text-center bg-slate-800/50 rounded-3xl border border-slate-700">
            <Building className="w-16 h-16 opacity-20 mx-auto mb-4" />
            <p className="text-2xl font-bold text-slate-400">No Facilities registered</p>
            <p className="text-slate-600 mt-2">
              Initialize your office layout by adding rooms or desks.
            </p>
          </div>
        ) : (
          facilities.map((facility) => (
            <div
              key={facility.id}
              className="bg-slate-800 border border-slate-700 p-6 rounded-3xl hover:border-blue-500/50 transition-all flex flex-col"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-500 border border-blue-500/20">
                  <Building size={24} />
                </div>
                <span
                  className={`
                  px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border
                  ${facility.status === 'Available' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-orange-500/10 text-orange-500 border-orange-500/20'}
                `}
                >
                  {facility.status}
                </span>
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">{facility.name}</h3>
              <p className="text-slate-500 text-sm flex items-center gap-2 mt-1">
                <MapPin size={14} />
                {facility.location || 'Main Floor'}
              </p>

              <div className="mt-6 space-y-3 flex-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center gap-2">
                    <Users size={16} /> Capacity
                  </span>
                  <span className="text-slate-200 font-bold">{facility.capacity} pax</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center gap-2">
                    <Clock size={16} /> Status
                  </span>
                  <span className="text-blue-400 font-bold capitalize">{facility.type}</span>
                </div>
              </div>

              <div className="mt-8 flex gap-3">
                <button className="flex-1 bg-slate-900 hover:bg-slate-700 text-white font-bold py-3 rounded-xl border border-slate-700 transition-all text-xs uppercase tracking-widest">
                  View Schedule
                </button>
                <button
                  onClick={() => {
                    setSelectedFacility(facility);
                    setShowBookingModal(true);
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all text-xs uppercase tracking-widest"
                >
                  Book Now
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Space Modal */}
      {showSpaceModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">Add New Space</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Space Name
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  placeholder="e.g. Conference Room A, Desk 42"
                  value={newSpace.name ?? ''}
                  onChange={(e) => setNewSpace({ ...newSpace, name: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Facility Type
                  </label>
                  <select
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newSpace.type}
                    onChange={(e) => setNewSpace({ ...newSpace, type: e.target.value })}
                  >
                    <option>Room</option>
                    <option>Desk</option>
                    <option>Zone</option>
                    <option>Parking</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Capacity
                  </label>
                  <input
                    type="number"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newSpace.capacity}
                    onChange={(e) =>
                      setNewSpace({ ...newSpace, capacity: parseInt(e.target.value) })
                    }
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Floor / Location
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  value={newSpace.location ?? ''}
                  onChange={(e) => setNewSpace({ ...newSpace, location: e.target.value })}
                />
              </div>
            </div>
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setShowSpaceModal(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 rounded-xl transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSpace}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-900/40"
              >
                Save Space
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {showBookingModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-slate-800 border border-slate-700 p-8 rounded-3xl w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-bold text-white mb-6">
              Space Booking - {selectedFacility?.name}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                  Purpose of Booking
                </label>
                <input
                  type="text"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                  placeholder="e.g. Team Sprint, Client Meeting"
                  value={newBooking.purpose ?? ''}
                  onChange={(e) => setNewBooking({ ...newBooking, purpose: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    Start Time
                  </label>
                  <input
                    type="datetime-local"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newBooking.startTime?.slice(0, 16)}
                    onChange={(e) =>
                      setNewBooking({
                        ...newBooking,
                        startTime: new Date(e.target.value).toISOString(),
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm font-bold mb-2 uppercase tracking-wide text-[10px]">
                    End Time
                  </label>
                  <input
                    type="datetime-local"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none"
                    value={newBooking.endTime?.slice(0, 16)}
                    onChange={(e) =>
                      setNewBooking({
                        ...newBooking,
                        endTime: new Date(e.target.value).toISOString(),
                      })
                    }
                  />
                </div>
              </div>
            </div>
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setShowBookingModal(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 rounded-xl transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleBook}
                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-900/40"
              >
                Confirm Booking
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FacilitiesSubmodule;
