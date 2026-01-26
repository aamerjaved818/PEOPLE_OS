import { useState, useMemo, useEffect } from 'react';
import { api } from '@/services/api';
import { AttendanceRecord } from '@/types';
import { useOrgStore } from '@/store/orgStore';

export function useAttendance() {
  const [searchTerm, setSearchTerm] = useState('');
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { plants } = useOrgStore();
  const [selectedPlantId, setSelectedPlantId] = useState<string>('');

  useEffect(() => {
    if (plants.length > 0 && !selectedPlantId) {
      const active = plants.find((p) => p.isActive);
      if (active) {
        setSelectedPlantId(active.id);
      }
    }
  }, [plants, selectedPlantId]);

  useEffect(() => {
    loadData();
  }, [selectedPlantId]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAttendanceRecords();
      setAttendanceRecords(data);
    } catch (error) {
      console.error('Failed to load attendance records:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredRecords = useMemo(() => {
    return attendanceRecords.filter(
      (record) =>
        (record.employeeName?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
        (record.employeeCode?.toLowerCase() || '').includes(searchTerm.toLowerCase())
    );
  }, [attendanceRecords, searchTerm]);

  return {
    searchTerm,
    setSearchTerm,
    attendanceRecords,
    filteredRecords,
    isLoading,
    plants,
    selectedPlantId,
    setSelectedPlantId,
    loadData,
  };
}
