export interface Facility {
  id: string;
  name: string;
  type: string;
  capacity: number;
  location?: string;
  status: 'Available' | 'Maintenance' | 'Restricted';
  organizationId: string;
}

export interface FacilityBooking {
  id: number;
  facilityId: string;
  facilityName?: string;
  userId: string;
  userName?: string;
  startTime: string;
  endTime: string;
  purpose?: string;
  attendees: number;
}

export interface Vehicle {
  id: string;
  model: string;
  plateNumber: string;
  category: string;
  status: 'Available' | 'In-Use' | 'Maintenance';
  assignedToId?: string;
  assignedToName?: string;
  lastServiceDate?: string;
  lastServiceMileage: number;
  currentMileage: number;
  organizationId: string;
  createdAt?: string;
}

export interface TravelRequest {
  id: string;
  employeeId: string;
  employeeName?: string;
  destination: string;
  departureDate: string;
  returnDate: string;
  reason: string;
  status: 'Pending' | 'Approved' | 'Rejected' | 'Completed';
  budget?: number;
  organizationId: string;
  createdAt?: string;
}

export interface AdminCompliance {
  id: number;
  licenseName: string;
  provider?: string;
  expiryDate: string;
  status: 'Active' | 'Expired' | 'Renewal-Pending';
  reminderDaysBefore: number;
  documentUrl?: string;
  organizationId: string;
  createdAt?: string;
}
