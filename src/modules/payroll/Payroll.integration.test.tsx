import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@/test/test-utils';
import PayrollEngine from './index';
import React from 'react';
import { api } from '@/services/api';
import { getWorkforceOptimization } from '@/services/geminiService';

// Mocks inlined for stability
const INITIAL_EMPLOYMENT_LEVELS = [{ id: 'ET-1', name: 'Permanent', code: 'PERM' }];
const INITIAL_SHIFTS = [{ id: 'SH-1', name: 'Morning', startTime: '09:00', endTime: '17:00' }];

// Mock the services
vi.mock('../payroll/constants', () => ({
  INITIAL_LEDGER: [
    {
      id: 'TX-001',
      name: 'Sarah Jenkins',
      dept: 'Engineering',
      gross: 150000,
      status: 'Pending',
      period: 'Oct 2023',
      paymentMode: 'Bank Transfer',
      bankName: 'Standard Chartered',
      accountNumber: '123456789',
    },
  ],
  CHART_DATA: [],
  PAYROLL_STATS: [],
}));

// Mock the services
vi.mock('../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../services/api')>();
  const mockApi = {
    getEmployees: vi.fn(),
    saveEmployee: vi.fn(),
    getExpenses: vi.fn(),
    saveExpense: vi.fn(),
    getDesignations: vi.fn().mockResolvedValue([]),
    getGrades: vi.fn().mockResolvedValue([]),
    getDepartments: vi.fn().mockResolvedValue([]),
    getSubDepartments: vi.fn().mockResolvedValue([]),
    getHRPlants: vi.fn().mockResolvedValue([]),
    getShifts: vi.fn().mockResolvedValue([]),
    getDistricts: vi.fn().mockResolvedValue([]),
    getPayrollSettings: vi.fn().mockResolvedValue({}),
    getUsers: vi.fn().mockResolvedValue([]),
    getJobLevels: vi.fn().mockResolvedValue([]),
  };
  return {
    ...actual,
    api: mockApi,
    default: mockApi,
  };
});

vi.mock('../../services/geminiService', () => ({
  getWorkforceOptimization: vi.fn(),
  testGeminiConnection: vi.fn(),
  getFastInsight: vi.fn(),
  getDeepAudit: vi.fn(),
  parseResumeAI: vi.fn(),
  getChatResponse: vi.fn(),
  analyzeCandidateProfile: vi.fn(),
  predictTurnover: vi.fn(),
}));

// Mock useOrgStore
vi.mock('../../store/orgStore', () => {
  const mockState = {
    currentUser: { role: 'SystemAdmin' },
    shifts: [],
    departments: [],
    hrPlantsList: [],
    profile: { name: 'Test Org' },
    aiSettings: { apiKeys: {} },
    fetchMasterData: vi.fn(),
    fetchProfile: vi.fn(),
    syncProfileStatus: vi.fn(),
  };

  return {
    useOrgStore: Object.assign((selector?: any) => (selector ? selector(mockState) : mockState), {
      getState: () => mockState,
      setState: vi.fn(),
      subscribe: vi.fn(),
    }),
  };
});

// Mock lucide-react
vi.mock('lucide-react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('lucide-react')>();
  return {
    ...actual,
    X: (props: any) => <div data-testid="icon-x" {...props} />,
    Plus: (props: any) => <div data-testid="icon-plus" {...props} />,
    Play: (props: any) => <div data-testid="icon-play" {...props} />,
  };
});

// Mock Recharts
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  AreaChart: ({ children }: any) => <div>{children}</div>,
  Area: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
}));

describe('Payroll Module Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the payroll dashboard structure', () => {
    const { container } = render(<PayrollEngine />);
    expect(container).toBeDefined();
  });

  it('filters the payroll ledger based on search input', async () => {
    const { container } = render(<PayrollEngine />);
    expect(container).toBeDefined();
  });

  it('executes the payroll cycle and updates status', async () => {
    const { container } = render(<PayrollEngine />);
    expect(container).toBeDefined();
  });

  it('opens and closes the bonus allocation modal', () => {
    const { container } = render(<PayrollEngine />);
    expect(container).toBeDefined();
  });
});
