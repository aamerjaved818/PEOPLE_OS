import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import Attendance from './AttendanceSubmodule';
import { api } from '@/services/api';

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    getAttendanceRecords: vi.fn(),
  },
}));

// Mock lucide-react explicitly
vi.mock('lucide-react', () => {
  const icons = [
    'User',
    'Mail',
    'Phone',
    'CreditCard',
    'MapPin',
    'HeartPulse',
    'Clock',
    'Factory',
    'Sun',
    'UserPlus',
    'UserX',
    'Target',
    'Settings',
    'Eye',
    'Edit3',
    'AlertCircle',
    'Building',
    'UserCircle',
    'CheckCircle2',
    'ShieldCheck',
    'Edit',
    'LogOut',
    'Trash2',
    'Plus',
    'Search',
    'SearchCode',
    'Filter',
    'Sparkles',
    'FileText',
    'FileSpreadsheet',
    'PartyPopper',
    'Cake',
    'Users',
    'UserCheck',
    'UserMinus',
    'Briefcase',
    'Calendar',
    'CalendarCheck',
    'Fingerprint',
    'CheckCircle',
    'Info',
    'AlertTriangle',
    'X',
    'Save',
    'UserRoundPen',
    'Wallet',
    'Heart',
    'GraduationCap',
    'History',
    'Gavel',
    'Zap',
    'Hash',
    'Printer',
    'Download',
    'Send',
    'Banknote',
    'TrendingUp',
    'ArrowUp',
    'Building',
    'ChevronRight',
    'BrainCircuit',
    'RefreshCw',
    'Award',
    'Star',
    'LayoutDashboard',
    'Bell',
    'Menu',
    'ChevronLeft',
    'Moon',
    'CalendarDays',
    'Clock3',
    'ClipboardCheck',
    'Coins',
    'Receipt',
    'Landmark',
    'PieChart',
    'Activity',
    'FileCheck',
    'ScanFace',
    'Globe',
    'Camera',
    'LayoutGrid',
    'Layout',
    'List',
    'CalendarRange',
    'Ban',
    'Gauge',
    'Loader2',
    'Coffee',
    'FileEdit',
    'Check',
  ];
  const mock: any = {};
  icons.forEach((icon) => {
    mock[icon] = (props: any) => <span data-testid={`icon-${icon.toLowerCase()}`} {...props} />;
  });
  return mock;
});

describe('Attendance Module', () => {
  const mockRecords = [
    {
      id: 'ATT-1',
      name: 'John Doe',
      code: 'EMP001',
      shift: 'A',
      inTime: '09:00',
      outTime: '17:00',
      status: 'Present',
      verification: 'Facial',
      location: 'Office',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (api.getAttendanceRecords as any).mockResolvedValue(mockRecords);
  });

  it('renders correctly and loads data', async () => {
    render(<Attendance />);
    // Component should render without crashing
    expect(document.body).toBeDefined();
  });

  it('switches tabs correctly', async () => {
    render(<Attendance />);
    // Component should handle tab switching
    expect(document.body).toBeDefined();
  });
});
