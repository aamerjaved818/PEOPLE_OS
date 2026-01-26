export type AssetCategory =
  | 'Laptop'
  | 'Desktop PC'
  | 'Mobile'
  | 'Tablet'
  | 'IT Gadget'
  | 'Vehicle'
  | 'Software'
  | 'Furniture'
  | 'Network';

export interface Asset {
  id: string;
  name: string;
  category: string;
  serialNumber: string;
  employeeId?: string;
  employeeName?: string;
  purchaseDate?: string;
  purchaseValue?: number;
  currency?: string;
  status: 'Active' | 'Maintenance' | 'Retired' | 'Disposed';
  specifications?: string;
  location?: string;
  maintenanceScheduleDays?: number;
  lastMaintenanceDate?: string;
  organizationId: string;
  createdAt?: string;
}
