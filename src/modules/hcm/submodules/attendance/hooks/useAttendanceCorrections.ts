import { useState } from 'react';

export function useAttendanceCorrections() {
  const [correctionRequests, setCorrectionRequests] = useState([
    {
      id: '1',
      name: 'Alex Rivera',
      date: 'Jul 18, 2024',
      type: 'Missing Punch',
      reason: 'Biometric hardware failure at Site-B gate.',
      status: 'Pending',
    },
    {
      id: '2',
      name: 'Maria Garcia',
      date: 'Jul 20, 2024',
      type: 'Shift Swap',
      reason: 'Emergency family medical protocol.',
      status: 'Pending',
    },
  ]);

  const handleCorrectionAction = (id: string, action: 'Approved' | 'Rejected') => {
    setCorrectionRequests((prev) =>
      prev.map((req) => (req.id === id ? { ...req, status: action } : req))
    );
  };

  const pendingCount = correctionRequests.filter((r) => r.status === 'Pending').length;

  return {
    correctionRequests,
    handleCorrectionAction,
    pendingCount,
  };
}
