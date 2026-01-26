import React from 'react';
import { Fingerprint, RefreshCw } from 'lucide-react';
import { Plant } from '@/types';

interface AttendanceHeaderProps {
  selectedPlantId: string;
  plants: Plant[];
  onRefresh: () => void;
}

export const AttendanceHeader: React.FC<AttendanceHeaderProps> = ({
  selectedPlantId,
  plants,
  onRefresh,
}) => {
  const activePlant = plants.find((p) => p.id === selectedPlantId);

  return (
    <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
      <div>
        <h1 className="text-4xl font-black text-text-primary tracking-tighter leading-none">
          Attendance
        </h1>
        <p className="text-text-muted mt-4 font-black uppercase tracking-[0.4em] text-[0.625rem] flex items-center gap-3">
          <span className="w-8 h-[0.125rem] bg-primary"></span>
          Biometric & Geofenced Tracking
        </p>
        {selectedPlantId && (
          <div className="mt-2 flex items-center gap-2">
            <span className="px-2 py-1 rounded bg-primary/10 border border-primary/20 text-[0.6rem] font-black text-primary uppercase tracking-widest">
              Rule: Auto-Attendance (Plant-Wise)
            </span>
            <span className="text-[0.6rem] font-bold text-text-muted uppercase tracking-wider">
              Active Plant: {activePlant?.name || 'Unknown'}
            </span>
          </div>
        )}
      </div>
      <div className="flex gap-4 p-4 bg-surface rounded-md shadow-md border border-border">
        <button
          onClick={onRefresh}
          aria-label="Refresh data"
          className="bg-muted-bg p-4 rounded-md text-text-muted hover:text-primary transition-all shadow-sm"
        >
          <RefreshCw size={20} />
        </button>
        <button
          aria-label="Force synchronization"
          className="bg-primary text-white px-10 py-4 rounded-md font-black uppercase text-[0.6875rem] tracking-widest flex items-center gap-4 shadow-md shadow-primary/20 hover:-translate-y-1 transition-all active:scale-95"
        >
          <Fingerprint size={18} /> Sync {activePlant?.name ? `(${activePlant.name})` : ''}
        </button>
      </div>
    </div>
  );
};
