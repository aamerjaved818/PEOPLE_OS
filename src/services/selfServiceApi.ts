/**
 * Self-Service API Integration
 * Handles all employee self-service API calls
 */

import { api } from '../services/api';

export interface MyProfile {
  id: string;
  employeeCode?: string;
  name: string;
  email: string;
  phone?: string;
  personalEmail?: string;
  personalPhone?: string;
  department?: string;
  designation?: string;
  joinDate?: string;
  status?: string;
  dateOfBirth?: string;
  gender?: string;
  maritalStatus?: string;
  bloodGroup?: string;
  presentAddress?: string;
  permanentAddress?: string;
  emergencyContactName?: string;
  emergencyContactPhone?: string;
  emergencyContactRelation?: string;
  profilePhotoUrl?: string;
  bio?: string;
  grossSalary?: number;
  bankName?: string;
}

export interface DocumentRequest {
  id: string;
  documentType: string;
  purpose?: string;
  status: string;
  requestedDate: string;
  approvedDate?: string;
  documentUrl?: string;
  employeeName?: string;
}

export interface EmployeeDocument {
  id: string;
  documentType: string;
  documentName: string;
  documentUrl: string;
  fileSize?: number;
  uploadDate: string;
  expiryDate?: string;
}

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  phone?: string;
  department?: string;
  designation?: string;
  profilePhotoUrl?: string;
  bio?: string;
  joinDate?: string;
}

export const selfServiceApi = {
  // Profile Management
  getMyProfile: () => api.get<MyProfile>('/self-service/profile'),

  updateProfile: (data: { profilePhotoUrl?: string; bio?: string }) =>
    api.put('/self-service/profile', data),

  updateEmergencyContact: (data: {
    emergencyContactName?: string;
    emergencyContactPhone?: string;
    emergencyContactRelation?: string;
  }) => api.put('/self-service/emergency-contact', data),

  uploadProfilePhoto: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/profile-photo', formData);
  },

  // Document Requests
  requestDocument: (data: { documentType: string; purpose?: string; additionalNotes?: string }) =>
    api.post<DocumentRequest>('/self-service/document-requests', data),

  getMyDocumentRequests: () => api.get<DocumentRequest[]>('/self-service/document-requests'),

  // Document Library
  getMyDocuments: () => api.get<EmployeeDocument[]>('/self-service/documents'),

  // Payslips
  getMyPayslips: (year?: number, month?: string) =>
    api.get('/self-service/payslips', { params: { year, month } }),

  // Team Directory
  getTeamDirectory: (departmentId?: string) =>
    api.get<TeamMember[]>('/self-service/team-directory', {
      params: { department_id: departmentId },
    }),

  getTeamMember: (employeeId: string) => api.get<TeamMember>(`/self-service/team/${employeeId}`),

  // Info Update Requests
  requestInfoUpdate: (data: { fieldName: string; newValue: string; reason?: string }) =>
    api.post('/self-service/info-update-request', data),
};
