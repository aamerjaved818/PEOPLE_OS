export interface VisitorNode {
  id: string;
  name: string;
  identificationNumber?: string;
  organization?: string;
  hostId?: string;
  hostName?: string;
  checkIn: string;
  checkOut?: string;
  purpose?: string;
  badgeNumber?: string;
  status: 'Checked-In' | 'Checked-Out' | 'Expected';
  organizationId: string;
}
