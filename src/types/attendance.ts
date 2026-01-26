export interface Holiday {
  id: number;
  name: string;
  date: string;
  type: 'Public' | 'National' | 'Religious' | 'International';
}

export interface Shift {
  id: string;
  name: string;
  code: string;
  type: 'Fixed' | 'Reliever' | 'Rotating' | 'Flexible';
  startTime: string;
  endTime: string;
  gracePeriod: number; // minutes
  breakDuration: number; // minutes
  workDays: string[]; // e.g., ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  color?: string;
  description?: string;
}

export interface LeaveRequest {
  id: string;
  employeeId: string;
  employeeName: string;
  type: 'Annual' | 'Sick' | 'Casual' | 'Unpaid';
  startDate: string;
  endDate: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  reason: string;
}

export interface OTRequest {
  id: string;
  employeeId: string;
  employeeName: string;
  date: string;
  hours: number;
  rate: number; // For compatibility
  multiplier?: number; // Backend alignment

  status: 'Pending' | 'Approved' | 'Rejected' | 'Processed';
  reason: string;
  rejectionReason?: string;
  approvedBy?: string;
  approvedAt?: string;
}

export interface LeaveBalance {
  employeeId: string;
  name: string;
  annual: number;
  sick: number;
  casual: number;
  total: number;
  used: number;
}

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeCode?: string;
  date: string;
  clockIn: string | null;
  clockOut: string | null;
  status: 'Present' | 'Absent' | 'Leave' | 'Late' | 'Half Day';
  shiftId: string;
  shiftName?: string;
  verificationType: 'Facial' | 'GPS' | 'Manual' | 'Biometric';
  location?: string;
  duration?: string;
  remarks?: string;
}

export interface AttendanceStats {
  present: number;
  late: number;
  absent: number;
  onLeave: number;
  halfDay: number;
  totalEmployees: number;
  date: string;
}

export interface AttendanceStat {
  name: string;
  value: number;
}

export interface AttendanceCorrection {
  id: string;
  employeeId: string;
  employeeName?: string;
  employeeCode?: string;
  date: string;
  type: 'Missing Punch' | 'Shift Swap' | 'Time Correction' | 'Wrong Status';
  originalClockIn?: string;
  originalClockOut?: string;
  originalStatus?: string;
  requestedClockIn?: string;
  requestedClockOut?: string;
  requestedStatus?: string;
  reason: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
  createdAt?: string;
}

export interface CreateCorrectionPayload {
  employeeId: string;
  date: string;
  type: string;
  originalClockIn?: string;
  originalClockOut?: string;
  originalStatus?: string;
  requestedClockIn?: string;
  requestedClockOut?: string;
  requestedStatus?: string;
  reason: string;
}
