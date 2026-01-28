import {
  Employee as EmployeeType,
  OrganizationProfile,
  Expense,
  VisitorNode,
  Candidate,
  Goal,
  NewHireNode,
  ExitNode,
  LeaveRequest,
  LeaveBalance,
  AttendanceRecord,
  OTRequest,
  Asset,
  JobVacancy,
  Course,
  BenefitEnrollment,
  BenefitTier,
  GrowthTrend,
  Milestone,
  Reward,
  Recognition,
  RewardPoint,
  RewardPointTransaction,
  AuditLog,
  BusinessRule,
  Shift,
  PayrollSettings,
  Grade,
  Designation,
  JobLevel,
  DepartmentStat,
  AttendanceStat,
  Holiday,
  Bank,
  SystemFlags,
  AISettings,
  Plant,
  Facility,
  FacilityBooking,
  Vehicle,
  AdminCompliance,
  PromotionCycle,
  PromotionRequest,
  PromotionApproval,
  TravelRequest,
} from '../types';
import { API_CONFIG } from '@/config/constants';
// Mock data imports removed to enforce strict backend dependency
import { RateLimiter } from '../utils/security';
import { GovernanceEngine } from '@/system/GovernanceEngine';
import { useSystemStore } from '@/system/systemStore';
import { secureStorage } from '@/utils/secureStorage';

const DEFAULT_PAYROLL_SETTINGS: PayrollSettings = {
  overtimeEnabled: true,
  taxYearEnd: 'June',
  currency: 'PKR',
  calculationMethod: 'Per Month',
  customFormulas: {
    staff: 'Gross salary / month days * working days + allowances - deductions = net payment',
    worker: 'Gross salary / 26 days * working days + allowances - deductions = net payment',
  },
  overtime: {
    routine: {
      staff: 'Gross salary / month days / 8 * working hours',
      worker: 'Gross salary / 26 / 8 * working hours',
    },
    gazetteHoliday: {
      staff: 'Gross salary / month days / 8 * working hours * 2',
      worker: 'Gross salary / 26 / 8 * working hours * 2',
    },
  },
};
// Mock data imports removed for production integration

import Logger from '../utils/logger';
import { convertKeysToCamel } from '../utils/case';

// const DATA_VERSION = '1.7'; // Synced with App.tsx to prevent reload loop

class ApiService {
  private async governanceIntercept(action: string, domain: string): Promise<void> {
    const decision = GovernanceEngine.evaluate({
      source: domain,
      message: action,
      risk: 'high',
    } as any);

    if (decision.reason.includes('Blocked')) {
      decision.intercepted = true;
      // Ingest into system store for visibility
      useSystemStore.getState().ingestSignal({
        source: domain,
        message: action,
        risk: 'critical',
        metadata: { intercepted: true },
      });
      throw new Error(`GOVERNANCE BLOCK: ${decision.reason}. ${decision.remediation}`);
    }
  }

  private employees: EmployeeType[] = [];
  private expenses: Expense[] = [];
  private candidates: Candidate[] = [];
  private goals: Goal[] = [];
  private hires: NewHireNode[] = [];
  private exits: ExitNode[] = [];
  private leaves: LeaveRequest[] = [];
  private leaveBalances: LeaveBalance[] = [];
  private attendance: AttendanceRecord[] = [];
  private jobs: JobVacancy[] = [];
  private courses: Course[] = [];
  private benefitEnrollments: BenefitEnrollment[] = [];
  private benefitTiers: BenefitTier[] = [];
  private growthTrends: GrowthTrend[] = [];
  private milestones: Milestone[] = [];
  private logs: AuditLog[] = [];
  private rules: BusinessRule[] = [];
  private grades: Grade[] = [];
  private designations: Designation[] = [];
  private visitors: VisitorNode[] = [];
  private assets: Asset[] = [];
  private rateLimiter: RateLimiter;
  private apiUrl: string;
  private authToken: string | null = null;

  constructor() {
    this.rateLimiter = new RateLimiter(1000, 60000); // 1000 requests per minute
    this.apiUrl = API_CONFIG.BASE_URL;
    this.authToken = secureStorage.getItem('token');

    // Data strict initialization
    this.employees = [];
    this.expenses = [];
    this.visitors = [];

    // Mock data initialization removed.
    // All data must come from Backend API.

    // Manual initialization for payrollSettings since initData expects an array
  }

  public setRateLimit(max: number): void {
    Logger.info(`Adjusting network throughput: ${max} req/min`);
    this.rateLimiter.setMaxRequests(max);
  }

  public getRateLimit(): number {
    return this.rateLimiter.getMaxRequests();
  }

  /**
   * Enforce rate limiting for API calls
   * Throws an error if rate limit is exceeded
   */
  private enforceRateLimit(): void {
    if (!this.rateLimiter.peekRequest()) {
      const remainingTime = this.rateLimiter.getRemainingTime();
      throw new Error(
        `Rate limit exceeded. Please wait ${Math.ceil(remainingTime / 1000)} seconds before making another request.`
      );
    }
  }

  public getHeaders(): Record<string, string> {
    const orgId = localStorage.getItem('selected_org_id');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Use latest token from storage if private property is null (defensive)
    const activeToken = this.authToken || secureStorage.getItem('token');
    if (activeToken) {
      headers['Authorization'] = `Bearer ${activeToken}`;
    }

    // Only attach x-organization-id if it's a valid string and not "null"/"undefined"
    // This prevents accidental filtering when Root/Admin should see everything
    if (orgId && orgId !== 'null' && orgId !== 'undefined') {
      headers['x-organization-id'] = orgId;
    }

    return headers;
  }

  // Helper for testing to reset state
  public resetForTesting() {
    Logger.info('Resetting API state to empty.');
    this.employees = [];
    this.expenses = [];
    this.visitors = [];
    this.candidates = [];
    this.goals = [];
    this.hires = [];
    this.exits = [];
    this.leaves = [];
    this.leaveBalances = [];
    this.attendance = [];
    this.assets = [];
    this.jobs = [];
    this.courses = [];
    this.benefitEnrollments = [];
    this.benefitTiers = [];
    this.growthTrends = [];
    this.milestones = [];
    this.logs = [];
    this.rules = [];
    this.rateLimiter = new RateLimiter(1000, 60000);
    sessionStorage.clear();
    secureStorage.clear();
  }

  private async request(url: string, options: RequestInit = {}): Promise<Response> {
    if (!this.rateLimiter.canMakeRequest()) {
      const waitTime = Math.ceil(this.rateLimiter.getRemainingTime() / 1000);
      throw new Error(`Rate limit exceeded. Please wait ${waitTime} seconds.`);
    }

    const headers = {
      ...this.getHeaders(),
      ...options.headers,
    };

    const method = options.method || 'GET';
    const retryAttempts = API_CONFIG.RETRY_ATTEMPTS;
    const timeout = API_CONFIG.TIMEOUT;
    let lastError: any;

    for (let attempt = 0; attempt <= retryAttempts; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      const startTime = performance.now();

      try {
        if (attempt > 0) {
          Logger.debug(`[request] Retry attempt ${attempt}/${retryAttempts} for ${method} ${url}`);
        }

        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        const duration = performance.now() - startTime;
        Logger.debug(
          `[request] Completed ${method} ${url} in ${duration.toFixed(0)}ms, status: ${response.status}`
        );

        if (response.status === 401) {
          Logger.warn('Unauthorized access detected. Session invalid. Logging out...');
          this.logout();
          window.dispatchEvent(new Event('auth:logout'));
          throw new Error('Session expired');
        }

        return response;
      } catch (error) {
        clearTimeout(timeoutId);
        lastError = error;
        const duration = performance.now() - startTime;
        const errorName = error instanceof Error ? error.name : 'Unknown';
        const errorMsg = error instanceof Error ? error.message : String(error);

        Logger.error(
          `[request] Failed ${method} ${url} (Attempt ${attempt + 1}/${retryAttempts + 1}) after ${duration.toFixed(0)}ms: ${errorName} - ${errorMsg}`
        );

        if (attempt === retryAttempts) {
          break;
        }

        // Don't retry on certain errors
        if (errorName === 'AbortError' && attempt > 0) {
          // If it already timed out once, maybe don't keep hammering if it's a hard limit,
          // but we follow the retry policy usually.
        }

        const delay = Math.pow(2, attempt) * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }

  public async post<T = any>(endpoint: string, data?: any, options: any = {}): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const opts = { method: 'POST', ...options } as RequestInit;
    let finalUrl = url;
    if (options && options.params) {
      const qs = new URLSearchParams(options.params as any).toString();
      finalUrl = qs ? `${url}?${qs}` : url;
      delete (opts as any).params;
    }
    const body = data instanceof FormData ? (data as any) : JSON.stringify(data);
    const response = await this.request(finalUrl, { ...opts, body });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { response: { data: errorData, status: response.status } };
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return (await response.text()) as unknown as T;
    }
    const json = await response.json().catch(() => ({}));
    return convertKeysToCamel(json) as T;
  }

  public async get<T = any>(endpoint: string, options: any = {}): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const opts = { method: 'GET', ...options } as RequestInit;
    let finalUrl = url;
    if (options && options.params) {
      const qs = new URLSearchParams(options.params as any).toString();
      finalUrl = qs ? `${url}?${qs}` : url;
      delete (opts as any).params;
    }
    const response = await this.request(finalUrl, opts);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { response: { data: errorData, status: response.status } };
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return (await response.text()) as unknown as T;
    }
    const json = await response.json().catch(() => ({}));
    return convertKeysToCamel(json) as T;
  }

  public async put<T = any>(endpoint: string, data?: any, options: any = {}): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const opts = { method: 'PUT', ...options } as RequestInit;
    let finalUrl = url;
    if (options && options.params) {
      const qs = new URLSearchParams(options.params as any).toString();
      finalUrl = qs ? `${url}?${qs}` : url;
      delete (opts as any).params;
    }
    const body = data instanceof FormData ? (data as any) : JSON.stringify(data);
    const response = await this.request(finalUrl, { ...opts, body });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { response: { data: errorData, status: response.status } };
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return (await response.text()) as unknown as T;
    }
    const json = await response.json().catch(() => ({}));
    return convertKeysToCamel(json) as T;
  }

  public async patch<T = any>(endpoint: string, data?: any, options: any = {}): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const opts = { method: 'PATCH', ...options } as RequestInit;
    let finalUrl = url;
    if (options && options.params) {
      const qs = new URLSearchParams(options.params as any).toString();
      finalUrl = qs ? `${url}?${qs}` : url;
      delete (opts as any).params;
    }
    const body = data instanceof FormData ? (data as any) : JSON.stringify(data);
    const response = await this.request(finalUrl, { ...opts, body });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { response: { data: errorData, status: response.status } };
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return (await response.text()) as unknown as T;
    }
    const json = await response.json().catch(() => ({}));
    return convertKeysToCamel(json) as T;
  }

  public async delete<T = any>(endpoint: string, options: any = {}): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const opts = { method: 'DELETE', ...options } as RequestInit;
    let finalUrl = url;
    if (options && options.params) {
      const qs = new URLSearchParams(options.params as any).toString();
      finalUrl = qs ? `${url}?${qs}` : url;
      delete (opts as any).params;
    }
    const response = await this.request(finalUrl, opts);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { response: { data: errorData, status: response.status } };
    }
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return (await response.text()) as unknown as T;
    }
    const json = await response.json().catch(() => ({}));
    return convertKeysToCamel(json) as T;
  }

  async checkHealth(): Promise<{ status: string; database: string; timestamp: string }> {
    try {
      return await this.get('/health');
    } catch (error) {
      console.error('Health check failed', error);
      return { status: 'Offline', database: 'Disconnected', timestamp: new Date().toISOString() };
    }
  }

  async login(username: string, password: string, rememberMe: boolean = false): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          Logger.warn(`Authentication failed for user: ${username}`);
          return false;
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Backend login failed');
      }

      const data = await response.json();
      if (data.access_token) {
        this.authToken = data.access_token;
        const storageType = rememberMe ? 'local' : 'session';
        try {
          secureStorage.setItem('token', data.access_token, storageType);
          if (data.user) {
            secureStorage.setItem('current_user', JSON.stringify(data.user), storageType);
          }
        } catch (storageErr) {
          Logger.warn('Failed to persist token to storage', String(storageErr));
        }
        return true;
      }
      return false;
    } catch (e: any) {
      Logger.error(`Network Error hitting ${this.apiUrl}/auth/login`, String(e));
      throw e; // Rethrow so the UI can catch the network error specifically
    }
  }

  logout() {
    this.authToken = null;
    secureStorage.removeItem('token');
    secureStorage.removeItem('current_user');
  }

  // --- Users & RBAC ---
  async getUsers(): Promise<any[]> {
    const response = await this.request(`${this.apiUrl}/users`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async saveUser(user: any): Promise<any> {
    const response = await this.request(`${this.apiUrl}/users`, {
      method: 'POST',
      body: JSON.stringify(user),
    });
    if (!response.ok) {
      throw new Error('Failed to save user');
    }
    return await response.json();
  }

  async updateUser(id: string, user: any): Promise<any> {
    const response = await this.request(`${this.apiUrl}/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(user),
    });
    if (!response.ok) {
      throw new Error('Failed to update user');
    }
    return await response.json();
  }

  async deleteUser(id: string): Promise<void> {
    const response = await this.request(`${this.apiUrl}/users/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || 'Failed to delete user';
      throw new Error(errorMessage);
    }
  }

  // --- Employees ---
  async getEmployees(): Promise<EmployeeType[]> {
    try {
      const data = await this.get('/hcm/employees');
      this.employees = data;
      return data;
    } catch (error) {
      Logger.warn('Backend unavailable, returning empty array for employees', error);
      this.employees = [];
      return [];
    }
  }

  async getDepartmentStats(): Promise<DepartmentStat[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Return empty stats if backend not implemented
        resolve([]);
      }, 600);
    });
  }

  async getAttendanceStats(): Promise<AttendanceStat[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Return empty stats if backend not implemented
        resolve([]);
      }, 600);
    });
  }

  // --- Organization & Master Data ---
  async getOrganizations(): Promise<OrganizationProfile[]> {
    /**
     * Get organizations based on user role.
     * - Root: Returns ALL organizations (system-wide full access)
     * - Super Admin / Other roles: Returns only their assigned organization (org-scoped)
     *
     * CRITICAL: Only Root has system-wide access. All others are org-scoped.
     */
    try {
      return await this.get('/organizations');
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      Logger.error(`Failed to fetch organizations: ${msg}`);
      // Re-throw to allow calling code to handle (don't silently fail - this makes orgs disappear!)
      throw error;
    }
  }

  async getOrganizationById(id: string): Promise<OrganizationProfile> {
    return await this.get(`/organizations/${id}`);
  }

  async createOrganization(org: any): Promise<OrganizationProfile> {
    const response = await this.request(`${this.apiUrl}/organizations`, {
      method: 'POST',
      body: JSON.stringify(org),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to create organization');
    }
    return await response.json();
  }

  async updateOrganization(
    id: string,
    org: Partial<OrganizationProfile>
  ): Promise<OrganizationProfile> {
    const response = await this.request(`${this.apiUrl}/organizations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(org),
    });
    if (!response.ok) {
      throw new Error('Failed to update organization');
    }
    return await response.json();
  }

  async deleteOrganization(id: string): Promise<void> {
    const response = await this.request(`${this.apiUrl}/organizations/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete organization');
    }
  }

  // --- Holidays ---
  async getHolidays(): Promise<Holiday[]> {
    try {
      return await this.get('/holidays');
    } catch (error) {
      Logger.warn('Failed to fetch holidays from backend, returning empty array');
      return [];
    }
  }

  async saveHoliday(holiday: Holiday): Promise<Holiday> {
    this.enforceRateLimit();
    const method = holiday.id ? 'PUT' : 'POST';
    const url = holiday.id ? `${this.apiUrl}/holidays/${holiday.id}` : `${this.apiUrl}/holidays`;

    // Convert id if it's currently a number (time.now) to undefined for creation if needed,
    // but backend expects string ID for updates.
    // If it's a number from Date.now(), it's a client ID, so we should probably treat it as new for backend if it doesn't exist?
    // Actually, OrgSetup.tsx creates with Date.now() ID.
    // I will fix OrgSetup to NOT send ID for new items.

    const response = await this.request(url, {
      method,
      body: JSON.stringify(holiday),
    });

    if (!response.ok) {
      throw new Error('Failed to save holiday');
    }
    return await response.json();
  }

  async deleteHoliday(id: string | number): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/holidays/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete holiday');
    }
  }

  // --- Banks ---
  async getBanks(): Promise<Bank[]> {
    try {
      return await this.get('/banks');
    } catch (error) {
      Logger.warn('Failed to fetch banks from backend, returning empty array');
      return [];
    }
  }

  async saveBank(bank: Bank): Promise<Bank> {
    this.enforceRateLimit();
    const method = bank.id ? 'PUT' : 'POST';
    const url = bank.id ? `${this.apiUrl}/banks/${bank.id}` : `${this.apiUrl}/banks`;

    const response = await this.request(url, {
      method,
      body: JSON.stringify(bank),
    });

    if (!response.ok) {
      throw new Error('Failed to save bank');
    }
    return await response.json();
  }

  async deleteBank(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/banks/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete bank');
    }
  }

  async getDistricts(): Promise<any[]> {
    return [];
  }

  async getSystemFlags(): Promise<SystemFlags> {
    return await this.get('/system/flags');
  }

  async updateSystemFlags(flags: Partial<SystemFlags>): Promise<SystemFlags> {
    try {
      const response = await this.request(`${this.apiUrl}/system/flags`, {
        method: 'POST',
        body: JSON.stringify(flags),
      });
      if (!response.ok) {
        throw new Error('Failed to update system flags');
      }
      return await response.json();
    } catch (e) {
      console.warn('Backend unavailable, saving system flags to LocalStorage');
      localStorage.setItem('system_flags', JSON.stringify(flags));
      // Return merged flags (mock)
      return { neural_bypass: false, ...flags } as SystemFlags;
    }
  }

  async getRolePermissions(): Promise<Record<string, string[]>> {
    try {
      return await this.get('/rbac/permissions');
    } catch (error) {
      Logger.warn('Failed to fetch role permissions from backend, returning empty record');
      return {};
    }
  }

  async updateRolePermissions(role: string, permissions: string[]): Promise<string[]> {
    const response = await this.request(`${this.apiUrl}/rbac/permissions`, {
      method: 'POST',
      body: JSON.stringify({ role, permissions }),
    });
    if (!response.ok) {
      throw new Error('Failed to update role permissions');
    }
    return await response.json();
  }

  async getShifts(): Promise<Shift[]> {
    try {
      return await this.get('/shifts');
    } catch (error) {
      Logger.warn('Failed to fetch shifts from backend, returning empty array');
      return [];
    }
  }

  async saveShift(shift: Shift): Promise<Shift> {
    this.enforceRateLimit();
    const method = shift.id ? 'PUT' : 'POST';
    const url = shift.id ? `${this.apiUrl}/shifts/${shift.id}` : `${this.apiUrl}/shifts`;

    const response = await this.request(url, {
      method,
      body: JSON.stringify(shift),
    });

    if (!response.ok) {
      throw new Error('Failed to save shift');
    }
    return await response.json();
  }

  async updateShift(id: string, shift: Partial<Shift>): Promise<Shift> {
    return this.saveShift({ ...shift, id } as Shift);
  }

  async deleteShift(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/shifts/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete shift');
    }
  }

  async getPayrollSettings(): Promise<PayrollSettings> {
    const response = await this.request(`${this.apiUrl}/payroll-settings`);
    if (!response.ok) {
      return DEFAULT_PAYROLL_SETTINGS;
    }
    return await response.json();
  }

  async savePayrollSettings(settings: PayrollSettings): Promise<void> {
    const response = await this.request(`${this.apiUrl}/payroll-settings`, {
      method: 'POST',
      body: JSON.stringify(settings),
    });
    if (!response.ok) {
      throw new Error('Failed to save payroll settings');
    }
  }

  async getNextEmployeeCode(plantId: string): Promise<string> {
    const response = await this.get(`/hcm/plants/${plantId}/next-code`);
    return response.next_code;
  }

  async saveEmployee(employee: EmployeeType): Promise<EmployeeType> {
    this.enforceRateLimit();
    await this.governanceIntercept(`Save Employee: ${employee.name}`, 'HCM_API');
    try {
      const exists = this.employees.some((e) => e.id === employee.id);
      const method = exists ? 'PUT' : 'POST';
      const url = exists ? `${this.apiUrl}/employees/${employee.id}` : `${this.apiUrl}/employees`;

      const response = await this.request(url, {
        method: method,
        body: JSON.stringify(employee),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const savedEmployee = await response.json();
      // Update local memory only
      const index = this.employees.findIndex((e) => e.id === savedEmployee.id);
      if (index !== -1) {
        this.employees[index] = savedEmployee;
      } else {
        this.employees.push(savedEmployee);
      }
      return savedEmployee;
    } catch (error) {
      Logger.error('Failed to save employee to backend', error);
      throw error;
    }
  }

  async deleteEmployee(id: string): Promise<void> {
    this.enforceRateLimit();
    await this.governanceIntercept(`Delete Employee: ${id}`, 'HCM_API');
    try {
      const response = await this.request(`${this.apiUrl}/employees/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        let errorMessage = `Backend error: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (err) {
          // ignore JSON parsing errors from non-JSON responses
        }
        throw new Error(errorMessage);
      }

      // Update local state
      this.employees = this.employees.filter((e) => e.id !== id);
    } catch (error) {
      Logger.error('Failed to delete from backend', error);
      throw error;
    }
  }

  // --- Expenses ---
  // --- Expenses ---
  async getExpenses(): Promise<Expense[]> {
    return this.get('/expenses');
  }

  async saveExpense(expense: Partial<Expense>): Promise<Expense> {
    return this.post('/expenses', expense);
  }

  async deleteExpense(id: string): Promise<void> {
    await this.delete(`/expenses/${id}`);
  }

  async updateExpenseStatus(id: string, status: Expense['status']): Promise<Expense> {
    return this.post('/expenses', { id, status }); // Save handles updates
  }

  // --- Candidates ---
  async getCandidates(): Promise<Candidate[]> {
    try {
      return await this.get('/candidates');
    } catch (error) {
      Logger.warn('Backend unavailable, returning local/empty data', error);
      return [];
    }
  }

  async saveCandidate(candidate: Candidate): Promise<void> {
    this.enforceRateLimit();
    try {
      // Check if exists
      const exists = this.candidates.some((c) => c.id === candidate.id);

      const method = exists ? 'PUT' : 'POST';
      const url = exists
        ? `${this.apiUrl}/candidates/${candidate.id}`
        : `${this.apiUrl}/candidates`;

      // Handling skills array to string conversion if needed by Backend?
      // Our backend now handles commas, but Pydantic expects list[str].
      // The frontend sends JSON, Pydantic parses.
      // The backend CRUD manually joins it. Ideally, we send list, backend receives Pydantic list.
      // It should work direct.

      const response = await this.request(url, {
        method: method,
        body: JSON.stringify(candidate),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const savedCandidate = await response.json();

      // Update local state
      const index = this.candidates.findIndex((c) => c.id === savedCandidate.id);
      if (index !== -1) {
        this.candidates[index] = savedCandidate;
      } else {
        this.candidates.unshift(savedCandidate);
      }
    } catch (error) {
      Logger.error('Failed to save candidate to backend', error);
    }
  }

  async updateCandidateStage(id: string, stage: Candidate['currentStage']): Promise<void> {
    return new Promise((resolve) => {
      const index = this.candidates.findIndex((c) => c.id === id);
      if (index !== -1) {
        this.candidates[index].currentStage = stage;
      }
      setTimeout(resolve, 500);
    });
  }

  async deleteCandidate(id: string): Promise<void> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/candidates/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      this.candidates = this.candidates.filter((c) => c.id !== id);
    } catch (error) {
      Logger.error('Failed to delete candidate from backend', error);
    }
  }

  // --- Goals ---
  async getGoals(employeeId?: string): Promise<Goal[]> {
    return this.get('/performance/goals', { params: { employee_id: employeeId } });
  }

  async saveGoal(goal: Partial<Goal>): Promise<Goal> {
    return this.post('/performance/goals', goal);
  }

  async deleteGoal(id: string): Promise<void> {
    await this.delete(`/performance/goals/${id}`);
  }

  // --- Hires & Exits [Migrated to Backend] ---

  // --- Leaves & Attendance [Migrated to Backend] ---

  // --- Organization Profile ---

  // --- Job Postings ---
  async getJobs(): Promise<JobVacancy[]> {
    try {
      return await this.get('/jobs');
    } catch (error) {
      Logger.warn('Failed to fetch jobs', error);
      return [];
    }
  }

  async saveJob(job: JobVacancy): Promise<void> {
    return new Promise((resolve) => {
      const index = this.jobs.findIndex((j) => j.id === job.id);
      if (index !== -1) {
        this.jobs[index] = job;
      } else {
        this.jobs.unshift(job);
      }
      setTimeout(resolve, 500);
    });
  }

  async deleteJob(id: string): Promise<void> {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      // If backend call was successful, update local state
      this.jobs = this.jobs.filter((j) => j.id !== id);
    } catch (error) {
      Logger.warn('Backend unavailable, deletion failed', error);
    }
  }

  async updateJobStatus(id: string, status: JobVacancy['status']): Promise<void> {
    return new Promise((resolve) => {
      const index = this.jobs.findIndex((j) => j.id === id);
      if (index !== -1) {
        this.jobs[index].status = status;
      }
      setTimeout(resolve, 500);
    });
  }

  // --- Learning ---
  async getCourses(): Promise<Course[]> {
    return this.get('/learning/courses');
  }

  async saveCourse(course: Course): Promise<Course> {
    return this.post('/learning/courses', course);
  }

  async updateCourseProgress(
    id: number,
    progress: number,
    status: Course['status'],
    score: number
  ): Promise<Course> {
    return this.put(`/learning/courses/${id}/progress`, { progress, status, score });
  }

  // --- Benefits ---
  async getBenefitEnrollments(): Promise<BenefitEnrollment[]> {
    return this.get('/benefits/enrollments');
  }

  async getBenefitTiers(): Promise<BenefitTier[]> {
    return this.get('/benefits/tiers');
  }

  async saveBenefitEnrollment(enrollment: BenefitEnrollment): Promise<BenefitEnrollment> {
    return this.post('/benefits/enrollments', enrollment);
  }

  async updateBenefitEnrollmentTier(
    id: string,
    tier: BenefitEnrollment['tier']
  ): Promise<BenefitEnrollment> {
    return this.put(`/benefits/enrollments/${id}/tier`, { tier });
  }

  // --- Rewards & Recognition ---
  async getRewards(): Promise<Reward[]> {
    return this.get('/rewards');
  }

  async getRecognitions(): Promise<Recognition[]> {
    return this.get('/rewards/recognitions');
  }

  async getRewardPoints(employeeId: string): Promise<RewardPoint | null> {
    return this.get(`/rewards/points/${employeeId}`);
  }

  async getRewardTransactions(employeeId: string): Promise<RewardPointTransaction[]> {
    return this.get(`/rewards/points/${employeeId}/transactions`);
  }

  async saveRecognition(recognition: Partial<Recognition>): Promise<Recognition> {
    return this.post('/rewards/recognitions', recognition);
  }

  async redeemReward(rewardId: number, employeeId: string): Promise<boolean> {
    return this.post(`/rewards/redeem/${rewardId}`, null, { params: { employee_id: employeeId } });
  }

  async saveReward(reward: Partial<Reward>): Promise<Reward> {
    return this.post('/rewards', reward);
  }

  // --- Promotions & Increments ---
  async getPromotionCycles(): Promise<PromotionCycle[]> {
    return this.get('/promotions/cycles');
  }

  async savePromotionCycle(cycle: Partial<PromotionCycle>): Promise<PromotionCycle> {
    return this.post('/promotions/cycles', cycle);
  }

  async getPromotionRequests(employeeId?: string): Promise<PromotionRequest[]> {
    const params: any = {};
    if (employeeId) {
      params.employee_id = employeeId;
    }
    return this.get('/promotions/requests', { params });
  }

  async savePromotionRequest(request: Partial<PromotionRequest>): Promise<PromotionRequest> {
    return this.post('/promotions/requests', request);
  }

  async approvePromotionRequest(approval: {
    requestId: number;
    level: string;
    status: string;
    remarks?: string;
  }): Promise<PromotionRequest> {
    return this.post('/promotions/approve', approval);
  }

  // --- Dashboard ---
  async getGrowthTrends(): Promise<GrowthTrend[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.growthTrends), 500);
    });
  }

  async getMilestones(): Promise<Milestone[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.milestones), 500);
    });
  }

  // --- System Management ---
  async exportData(): Promise<string> {
    Logger.info('Exporting data. Employees length:', this.employees?.length);
    const data = {
      employees: this.employees,
      candidates: this.candidates,
      goals: this.goals,
      hires: this.hires,
      exits: this.exits,
      leaves: this.leaves,
      leaveBalances: this.leaveBalances,
      attendance: this.attendance,
      assets: this.assets,
      jobs: this.jobs,
      courses: this.courses,
      benefitEnrollments: this.benefitEnrollments,
      benefitTiers: this.benefitTiers,
      logs: this.logs,
      rules: this.rules,
    };
    return JSON.stringify(data, null, 2);
  }

  async importData(json: string): Promise<boolean> {
    try {
      const data = JSON.parse(json);
      if (data.employees) {
        this.employees = data.employees;
      }
      if (data.candidates) {
        this.candidates = data.candidates;
      }
      if (data.goals) {
        this.goals = data.goals;
      }
      if (data.hires) {
        this.hires = data.hires;
      }
      if (data.exits) {
        this.exits = data.exits;
      }
      if (data.leaves) {
        this.leaves = data.leaves;
      }
      if (data.leaveBalances) {
        this.leaveBalances = data.leaveBalances;
      }
      if (data.attendance) {
        this.attendance = data.attendance;
      }
      if (data.assets) {
        this.assets = data.assets;
      }
      if (data.jobs) {
        this.jobs = data.jobs;
      }
      if (data.courses) {
        this.courses = data.courses;
      }
      if (data.benefitEnrollments) {
        this.benefitEnrollments = data.benefitEnrollments;
      }
      if (data.benefitTiers) {
        this.benefitTiers = data.benefitTiers;
      }
      if (data.logs) {
        this.logs = data.logs;
      }
      if (data.rules) {
        this.rules = data.rules;
      }
      if (data.rates) {
        // Implementation for rates import if needed
      }

      this.logAction('System', 'Data Import', 'Full system restore initiated.', 'Warning');
      return true;
    } catch (e) {
      Logger.error('Import failed', e);
      return false;
    }
  }

  // --- Data Management (Backup/Restore) ---
  async downloadBackup(): Promise<Blob> {
    const response = await this.request(`${this.apiUrl}/system/backup`);
    if (!response.ok) {
      throw new Error('Failed to generate backup');
    }
    return await response.blob();
  }

  async restoreSystem(file: File): Promise<void> {
    this.enforceRateLimit();
    const formData = new FormData();
    formData.append('file', file);

    // Custom request to handle FormData (Content-Type must be unset)
    const headers = { ...this.getHeaders() } as any;
    delete headers['Content-Type'];

    const response = await fetch(`${this.apiUrl}/system/restore`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to restore system');
    }
  }

  async getLogs(): Promise<AuditLog[]> {
    return this.getAuditLogs();
  }

  async logAction(
    user: string,
    action: string,
    details: string, // Kept for compat, but mapped to status/action if needed?
    level: 'Info' | 'Warning' | 'Error' = 'Info'
  ): Promise<void> {
    const log: AuditLog = {
      id: `LOG-${Date.now()}`,
      time: new Date().toISOString(),
      user,
      action: `${action} - ${details}`,
      status: level === 'Error' ? 'Flagged' : 'Hashed',
    };
    this.logs.push(log);
    sessionStorage.setItem('people_os_logs', JSON.stringify(this.logs));
  }

  async getRules(): Promise<BusinessRule[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.rules), 500);
    });
  }

  async saveRule(rule: BusinessRule): Promise<void> {
    return new Promise((resolve) => {
      const index = this.rules.findIndex((r) => r.id === rule.id);
      if (index !== -1) {
        this.rules[index] = rule;
      } else {
        this.rules.push(rule);
      }
      this.logAction('Admin', 'Save Rule', `Rule ${rule.name} saved.`);
      setTimeout(resolve, 500);
    });
  }

  async deleteRule(id: string): Promise<void> {
    return new Promise((resolve) => {
      this.rules = this.rules.filter((r) => r.id !== id);
      this.logAction('Admin', 'Delete Rule', `Rule ${id} deleted.`, 'Warning');
      setTimeout(resolve, 500);
    });
  }

  async savePayrollRecord(record: any): Promise<void> {
    this.enforceRateLimit();
    try {
      // Assuming record has an 'id' field
      const method = record.id ? 'PUT' : 'POST';
      const url = record.id ? `${this.apiUrl}/payroll/${record.id}` : `${this.apiUrl}/payroll`;

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(record),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      await response.json();
    } catch (error) {
      Logger.error('Failed to save payroll to backend', error);
      throw error;
    }
  }

  async deletePayrollRecord(id: string): Promise<void> {
    this.enforceRateLimit();
    try {
      const response = await fetch(`${this.apiUrl}/payroll/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }
    } catch (error) {
      Logger.error('Failed to delete payroll from backend', error);
      throw error;
    }
  }
  // --- Departments ---
  async getDepartments(): Promise<any[]> {
    try {
      return await this.get('/departments');
    } catch (error) {
      Logger.warn('Backend unavailable, returning empty departments', error);
      return [];
    }
  }

  async saveDepartment(department: any): Promise<any> {
    return this.post('/departments', department);
  }

  // --- Sub-Departments ---
  async getSubDepartments(): Promise<any[]> {
    try {
      return await this.get('/sub-departments');
    } catch (error) {
      Logger.warn('Backend unavailable, returning empty sub-departments', error);
      return [];
    }
  }

  async saveSubDepartment(subDepartment: any): Promise<any> {
    return this.post('/sub-departments', subDepartment);
  }

  // --- Plants (Locations) ---
  // --- Plants (Locations) ---
  // Replaced by typed implementations below

  // --- RBAC ---
  async getAllRolePermissions(): Promise<Record<string, string[]>> {
    try {
      return await this.get('/rbac/permissions');
    } catch (error) {
      return {};
    }
  }

  async saveRolePermissions(role: string, permissions: string[]): Promise<void> {
    await this.post('/rbac/permissions', { role, permissions });
  }

  // --- Positions ---
  async getPositions(): Promise<any[]> {
    try {
      return await this.get('/positions');
    } catch (error) {
      Logger.warn('Backend unavailable, returning empty positions', error);
      return [];
    }
  }

  async savePosition(position: any): Promise<any> {
    try {
      const method = position.id ? 'PUT' : 'POST';
      const url = position.id
        ? `${this.apiUrl}/positions/${position.id}`
        : `${this.apiUrl}/positions`;
      const response = await this.request(url, {
        method,
        body: JSON.stringify(position),
      });
      if (!response.ok) {
        throw new Error('Failed to save position');
      }
      return await response.json();
    } catch (error) {
      Logger.error('Save position failed', error);
      throw error;
    }
  }

  async updatePosition(id: string, position: any): Promise<any> {
    try {
      const response = await this.request(`${this.apiUrl}/positions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(position),
      });
      if (!response.ok) {
        throw new Error('Failed to update position');
      }
      return await response.json();
    } catch (error) {
      Logger.error('Update position failed', error);
      throw error;
    }
  }

  async getInitialData(): Promise<any> {
    try {
      return await this.get('/system/initial-data');
    } catch (error) {
      Logger.error('Failed to fetch initial system data', error);
      throw error;
    }
  }

  async deletePosition(id: string): Promise<void> {
    try {
      const response = await this.request(`${this.apiUrl}/positions/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete position');
      }
    } catch (error) {
      Logger.error('Delete position failed', error);
      throw error;
    }
  }

  // --- Grades ---
  async getGrades(): Promise<Grade[]> {
    try {
      const data = await this.get('/grades');
      this.grades = data;
      return data;
    } catch (error) {
      Logger.warn('Backend unavailable, returning empty grades', error);
      return [];
    }
  }

  async saveGrade(grade: Grade): Promise<Grade> {
    return this.post('/grades', grade);
  }

  async deleteGrade(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/grades/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete grade');
    }
    this.grades = this.grades.filter((g) => g.id !== id);
  }

  // --- Designations ---
  async getDesignations(): Promise<Designation[]> {
    try {
      return await this.get('/designations');
    } catch (error) {
      return [];
    }
  }

  async saveDesignation(designation: Designation): Promise<Designation> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/designations`, {
      method: 'POST',
      body: JSON.stringify(designation),
    });
    if (!response.ok) {
      // Extract actual error from backend
      let errorDetail = 'Failed to save designation';
      try {
        const errBody = await response.json();
        errorDetail = errBody.detail || JSON.stringify(errBody);
        Logger.error(`[API] saveDesignation failed: ${response.status} - ${errorDetail}`);
      } catch {
        Logger.error(
          `[API] saveDesignation failed: ${response.status} - Could not parse error body`
        );
      }
      throw new Error(errorDetail);
    }
    return await response.json();
  }

  async updateDesignation(id: string, designation: Partial<Designation>): Promise<Designation> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/designations/${id}`, {
        method: 'PUT',
        body: JSON.stringify(designation),
      });
      if (!response.ok) {
        throw new Error('Failed to update designation');
      }
      const updated = await response.json();

      // Update local cache
      const index = this.designations.findIndex((d) => d.id === id);
      if (index !== -1) {
        this.designations[index] = updated;
      }

      return updated;
    } catch (error) {
      Logger.error('Backend unavailable, update designation failed', error);
      throw error;
    }
  }

  async deleteDesignation(id: string): Promise<void> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/designations/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete designation');
      }

      this.designations = this.designations.filter((d) => d.id !== id);
    } catch (error) {
      Logger.error('Backend unavailable, delete designation failed', error);
      throw error;
    }
  }

  // --- Delete & Update Methods for Other Entities ---

  // Departments
  async updateDepartment(id: string, department: Partial<any>): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(department),
    });
    if (!response.ok) {
      throw new Error('Failed to update department');
    }
    return await response.json();
  }

  async deleteDepartment(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/departments/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete department');
    }
  }

  // Sub-Departments
  async updateSubDepartment(id: string, subDepartment: Partial<any>): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/sub-departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(subDepartment),
    });
    if (!response.ok) {
      throw new Error('Failed to update sub-department');
    }
    return await response.json();
  }

  async deleteSubDepartment(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/sub-departments/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete sub-department');
    }
  }

  // Plants

  // Grades
  async updateGrade(id: string, grade: any): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/grades/${id}`, {
      method: 'PUT',
      body: JSON.stringify(grade),
    });
    if (!response.ok) {
      throw new Error('Failed to update grade');
    }
    return await response.json();
  }

  // --- Shifts ---

  // --- Audit Logs ---
  async getAuditLogs(skip: number = 0, limit: number = 100): Promise<AuditLog[]> {
    const response = await this.request(`${this.apiUrl}/audit-logs?skip=${skip}&limit=${limit}`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async saveAuditLog(log: Omit<AuditLog, 'id' | 'time'>): Promise<AuditLog> {
    const response = await this.request(`${this.apiUrl}/audit-logs`, {
      method: 'POST',
      body: JSON.stringify(log),
    });
    if (!response.ok) {
      throw new Error('Failed to save audit log');
    }
    return await response.json();
  }

  // --- Recruitment ---
  async getJobVacancies(): Promise<any[]> {
    const response = await this.request(`${this.apiUrl}/job-vacancies`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async saveJobVacancy(job: any): Promise<any> {
    // Assuming create only for now, or unified save
    const method = 'POST'; // Simplified
    const response = await this.request(`${this.apiUrl}/job-vacancies`, {
      method,
      body: JSON.stringify(job),
    });
    if (!response.ok) {
      throw new Error('Failed to save job');
    }
    return await response.json();
  }

  // --- Performance (Goals) ---

  async updateGoal(goal: any): Promise<any> {
    const response = await this.request(`${this.apiUrl}/goals/${goal.id}`, {
      method: 'PUT',
      body: JSON.stringify(goal),
    });
    if (!response.ok) {
      throw new Error('Failed to update goal');
    }
    return await response.json();
  }

  async getPerformanceReviews(): Promise<any[]> {
    const response = await this.request(`${this.apiUrl}/performance-reviews`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  // --- API Keys Management ---

  async createApiKey(name: string, expiresAt?: string): Promise<any> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/system/api-keys`, {
        method: 'POST',
        body: JSON.stringify({ name, expires_at: expiresAt }),
      });
      if (!response.ok) {
        throw new Error('Failed to create API key');
      }
      return await response.json();
    } catch (e) {
      console.warn('Backend unavailable, using LocalStorage for API Key');
      const newKey = {
        id: crypto.randomUUID(),
        name,
        key_preview: 'sk-live-' + Math.random().toString(36).substring(7) + '...',
        raw_key:
          'sk-live-' +
          Math.random().toString(36).substring(2) +
          Math.random().toString(36).substring(2),
        created_at: new Date().toISOString(),
        last_used: null,
      };
      const keys = JSON.parse(localStorage.getItem('system_api_keys') || '[]');
      keys.push(newKey);
      localStorage.setItem('system_api_keys', JSON.stringify(keys));
      return newKey;
    }
  }

  async listApiKeys(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.request(
      `${this.apiUrl}/system/api-keys?skip=${skip}&limit=${limit}`
    );
    if (!response.ok) {
      return { keys: [], total: 0 };
    }
    return await response.json();
  }

  async revokeApiKey(keyId: string): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/api-keys/${keyId}/revoke`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to revoke API key');
    }
    return await response.json();
  }

  async deleteApiKey(keyId: string): Promise<any> {
    this.enforceRateLimit();
    try {
      await this.request(`${this.apiUrl}/system/api-keys/${keyId}`, { method: 'DELETE' });
    } catch (e) {
      const keys = JSON.parse(localStorage.getItem('system_api_keys') || '[]');
      const filtered = keys.filter((k: any) => k.id !== keyId);
      localStorage.setItem('system_api_keys', JSON.stringify(filtered));
    }
    return { success: true };
  }

  // --- Webhooks Management ---

  async createWebhook(
    name: string,
    url: string,
    eventTypes: string[],
    headers?: any
  ): Promise<any> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/system/webhooks`, {
        method: 'POST',
        body: JSON.stringify({ name, url, event_types: eventTypes, headers }),
      });
      if (!response.ok) {
        throw new Error('Failed to create webhook');
      }
      return await response.json();
    } catch (e) {
      console.warn('Backend unavailable, using LocalStorage for Webhook');
      const newHook = {
        id: crypto.randomUUID(),
        name,
        url,
        event_types: eventTypes,
        is_active: true,
        headers,
      };
      const hooks = JSON.parse(localStorage.getItem('system_webhooks') || '[]');
      hooks.push(newHook);
      localStorage.setItem('system_webhooks', JSON.stringify(hooks));
      return newHook;
    }
  }

  async listWebhooks(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.request(
      `${this.apiUrl}/system/webhooks?skip=${skip}&limit=${limit}`
    );
    if (!response.ok) {
      return { webhooks: [], total: 0 };
    }
    return await response.json();
  }

  async getWebhook(webhookId: string): Promise<any> {
    const response = await this.request(`${this.apiUrl}/system/webhooks/${webhookId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve webhook');
    }
    return await response.json();
  }

  async updateWebhook(webhookId: string, updates: any): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/webhooks/${webhookId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    if (!response.ok) {
      throw new Error('Failed to update webhook');
    }
    return await response.json();
  }

  async deleteWebhook(webhookId: string): Promise<any> {
    this.enforceRateLimit();
    try {
      await this.request(`${this.apiUrl}/system/webhooks/${webhookId}`, { method: 'DELETE' });
    } catch (e) {
      const hooks = JSON.parse(localStorage.getItem('system_webhooks') || '[]');
      const filtered = hooks.filter((h: any) => h.id !== webhookId);
      localStorage.setItem('system_webhooks', JSON.stringify(filtered));
    }
    return { success: true };
  }

  async getWebhookLogs(webhookId: string, skip: number = 0, limit: number = 100): Promise<any> {
    const response = await this.request(
      `${this.apiUrl}/system/webhooks/${webhookId}/logs?skip=${skip}&limit=${limit}`
    );
    if (!response.ok) {
      return { logs: [], total: 0 };
    }
    return await response.json();
  }

  async testWebhook(_webhookId: string): Promise<any> {
    this.enforceRateLimit();
    // Simulate test
    await new Promise((r) => setTimeout(r, 1000));
    return { status_code: 200, message: 'Test event delivered successfully via Local Simulation' };
  }

  async flushCache(): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/maintenance/flush-cache`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to flush cache');
    }
    return await response.json();
  }

  async optimizeDatabase(): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/maintenance/optimize-db`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to optimize database');
    }
    return await response.json();
  }

  async rotateLogs(): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/maintenance/rotate-logs`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to rotate logs');
    }
    return await response.json();
  }

  async getSystemHealth(): Promise<any> {
    const response = await this.request(`${this.apiUrl}/system/flags/health`);
    if (!response.ok) {
      return {};
    }
    return await response.json();
  }

  // --- Notification Settings ---
  async getNotificationSettings(): Promise<any> {
    const response = await this.request(`${this.apiUrl}/notifications/config`);
    if (!response.ok) {
      return {
        email: {
          smtpServer: '',
          port: 587,
          username: '',
          password: '',
          fromAddress: '',
          enabled: true,
        },
        sms: { provider: 'Twilio', apiKey: '', senderId: '', enabled: false },
      };
    }
    const data = await response.json();
    return data;
  }

  async updateNotificationSettings(settings: any): Promise<any> {
    this.enforceRateLimit();
    try {
      const response = await this.request(`${this.apiUrl}/notifications/config`, {
        method: 'POST',
        body: JSON.stringify(settings),
      });
      if (!response.ok) {
        throw new Error('Failed to update notification settings');
      }
      return await response.json();
    } catch (e) {
      console.warn('Backend unavailable, saving notification settings to LocalStorage');
      localStorage.setItem('notification_settings', JSON.stringify(settings));
      return settings;
    }
  }

  async testEmailNotification(recipient: string): Promise<any> {
    const response = await this.request(`${this.apiUrl}/notifications/test`, {
      method: 'POST',
      body: JSON.stringify({ recipient }),
    });
    if (!response.ok) {
      throw new Error('Failed to send test email');
    }
    return await response.json();
  }

  async saveNotificationSettings(settings: any): Promise<void> {
    this.enforceRateLimit();
    // Map frontend structure to backend
    const payload = {
      emailEnabled: settings.email?.enabled ?? true,
      emailProvider: 'smtp', // Default or derived
      emailFromAddress: settings.email?.fromAddress,
      emailFromName: 'System',

      smsEnabled: settings.sms?.enabled ?? false,
      smsProvider: settings.sms?.provider,
      smsFromNumber: settings.sms?.senderId,
    };

    const response = await this.request(`${this.apiUrl}/notifications/config`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to save notification settings');
    }
  }

  // --- AI Settings ---
  async getAISettings(): Promise<AISettings> {
    const response = await this.request(`${this.apiUrl}/system/ai`);
    if (!response.ok) {
      return {
        provider: 'gemini',
        status: 'offline',
        apiKeys: { openai: '', gemini: '', anthropic: '' },
        agents: { resume_screener: false, turnover_predictor: false, chat_assistant: false },
      };
    }
    const data = await response.json();
    return {
      provider: data.provider,
      status: data.status,
      apiKeys: data.apiKeys || { openai: '', gemini: '', anthropic: '' },
      agents: data.agents || {
        resume_screener: false,
        turnover_predictor: false,
        chat_assistant: false,
      },
    };
  }

  async updateAiSettings(settings: any): Promise<void> {
    this.enforceRateLimit();
    // Map frontend to backend
    const payload = {
      provider: settings.provider,
      apiKeys: settings.apiKeys,
      status: settings.status,
      agents: settings.agents,
    };

    try {
      const response = await this.request(`${this.apiUrl}/system/ai`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error('Failed to save AI settings');
      }
    } catch (e) {
      console.warn('Backend unavailable, saving AI settings to LocalStorage');
      localStorage.setItem('ai_settings', JSON.stringify(settings));
    }
  }

  async testAIConnection(): Promise<any> {
    return await this.post('/ai/test-connection', {});
  }

  // --- Compliance Settings ---
  async getComplianceSettings(): Promise<any> {
    const response = await this.request(`${this.apiUrl}/compliance/settings`);
    if (!response.ok) {
      return {};
    }
    return await response.json();
  }

  async saveComplianceSettings(settings: any): Promise<void> {
    const payload = {
      taxYear: settings.taxYear,
      minWage: settings.minWage,
      eobiRate: settings.eobiRate,
      socialSecurityRate: settings.socialSecurityRate,
    };
    const response = await this.request(`${this.apiUrl}/compliance/settings`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to save compliance settings');
    }
  }

  // --- Background Jobs Management ---

  async getBackgroundJobs(skip: number = 0, limit: number = 50, status?: string): Promise<any> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (status) {
      params.append('status', status);
    }

    const response = await this.request(
      `${this.apiUrl}/system/background-jobs?${params.toString()}`
    );
    if (!response.ok) {
      return { jobs: [], total: 0 };
    }
    return await response.json();
  }

  async getBackgroundJob(jobId: string): Promise<any> {
    const response = await this.request(`${this.apiUrl}/system/background-jobs/${jobId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve background job');
    }
    return await response.json();
  }

  async cancelBackgroundJob(jobId: string): Promise<any> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/background-jobs/${jobId}/cancel`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to cancel background job');
    }
    return await response.json();
  }

  // --- Plants & Locations ---
  async getPlants(): Promise<Plant[]> {
    try {
      const response = await this.request(`${this.apiUrl}/plants`);
      if (!response.ok) {
        return [];
      }
      return await response.json();
    } catch (error) {
      console.warn('Backend unavailable, returning empty plants', error);
      return [];
    }
  }

  async createPlant(plant: Plant): Promise<Plant> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/plants`, {
      method: 'POST',
      body: JSON.stringify(plant),
    });

    if (!response.ok) {
      throw new Error('Failed to save location');
    }
    return await response.json();
  }

  async updatePlant(id: string, plant: Partial<Plant>): Promise<Plant> {
    const response = await this.request(`${this.apiUrl}/plants/${id}`, {
      method: 'PUT',
      body: JSON.stringify(plant),
    });
    if (!response.ok) {
      throw new Error('Failed to update location');
    }
    return await response.json();
  }

  async deletePlant(id: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/plants/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete location');
    }
  }

  // --- Job Levels ---
  async getJobLevels(orgId?: string): Promise<JobLevel[]> {
    const url = orgId ? `${this.apiUrl}/job-levels?org_id=${orgId}` : `${this.apiUrl}/job-levels`;
    const response = await this.request(url);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async createJobLevel(data: Partial<JobLevel>): Promise<JobLevel> {
    const response = await this.request(`${this.apiUrl}/job-levels`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create job level');
    }
    return await response.json();
  }

  async updateJobLevel(id: string, data: Partial<JobLevel>): Promise<JobLevel> {
    const response = await this.request(`${this.apiUrl}/job-levels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to update job level');
    }
    return await response.json();
  }

  async deleteJobLevel(id: string): Promise<void> {
    const response = await this.request(`${this.apiUrl}/job-levels/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete job level');
    }
  }

  // --- System Maintenance ---
  async getBackups(): Promise<Array<{ filename: string; size: number; created_at: string }>> {
    const response = await this.request(`${this.apiUrl}/system/maintenance/backups`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async restoreFromServer(filename: string): Promise<void> {
    this.enforceRateLimit();
    const response = await this.request(`${this.apiUrl}/system/maintenance/restore/${filename}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to restore system');
    }
  }

  // --- Attendance ---
  async getAttendanceRecords(date?: string): Promise<AttendanceRecord[]> {
    const query = date ? `?date=${date}` : '';
    const response = await this.request(`${this.apiUrl}/hcm/attendance${query}`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async createAttendanceRecord(data: Partial<AttendanceRecord>): Promise<AttendanceRecord> {
    const response = await this.request(`${this.apiUrl}/hcm/attendance`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create attendance');
    }
    return await response.json();
  }

  // --- Payroll ---
  async getPayrollRecords(): Promise<any[]> {
    const response = await this.request(`${this.apiUrl}/hcm/payroll`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async runPayroll(data: any): Promise<any> {
    const response = await this.request(`${this.apiUrl}/hcm/payroll`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to run payroll');
    }
    return await response.json();
  }

  // --- Leaves ---
  async getLeaveRequests(): Promise<LeaveRequest[]> {
    const response = await this.request(`${this.apiUrl}/hcm/leaves`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async saveLeaveRequest(data: Partial<LeaveRequest>): Promise<LeaveRequest> {
    const response = await this.request(`${this.apiUrl}/hcm/leaves`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create leave request');
    }
    return await response.json();
  }

  async updateLeaveRequestStatus(id: string, status: string): Promise<LeaveRequest> {
    const response = await this.request(`${this.apiUrl}/hcm/leaves/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
    if (!response.ok) {
      throw new Error('Failed to update leave status');
    }
    return await response.json();
  }

  async getLeaveBalances(): Promise<LeaveBalance[]> {
    const response = await this.request(`${this.apiUrl}/hcm/leaves/balances`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  // --- Overtime ---
  async getOvertimeRequests(params?: {
    status?: string;
    employee_id?: string;
  }): Promise<OTRequest[]> {
    let url = `${this.apiUrl}/overtime`;
    const queryParts = [];
    if (params?.status) {
      queryParts.push(`status=${params.status}`);
    }
    if (params?.employee_id) {
      queryParts.push(`employee_id=${params.employee_id}`);
    }
    if (queryParts.length > 0) {
      url += `?${queryParts.join('&')}`;
    }

    const response = await this.request(url);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  }

  async createOvertimeRequest(data: Partial<OTRequest>): Promise<OTRequest> {
    const response = await this.request(`${this.apiUrl}/overtime`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create overtime request');
    }
    return await response.json();
  }

  async updateOvertimeStatus(
    id: string,
    payload: { action: string; rejectionReason?: string }
  ): Promise<OTRequest> {
    const response = await this.request(`${this.apiUrl}/overtime/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to update overtime status');
    }
    return await response.json();
  }

  // --- General Administration ---
  async getAssets(organizationId?: string): Promise<Asset[]> {
    const params = organizationId ? { params: { organization_id: organizationId } } : undefined;
    return this.get('/gen-admin/assets', params);
  }

  async createAsset(asset: Partial<Asset>, organizationId: string): Promise<Asset> {
    return this.post('/gen-admin/assets', asset, { params: { organization_id: organizationId } });
  }

  async getVisitors(organizationId?: string): Promise<VisitorNode[]> {
    const params = organizationId ? { params: { organization_id: organizationId } } : undefined;
    return this.get('/gen-admin/visitors', params);
  }

  async createVisitor(visitor: Partial<VisitorNode>, organizationId: string): Promise<VisitorNode> {
    return this.post('/gen-admin/visitors', visitor, {
      params: { organization_id: organizationId },
    });
  }

  async checkoutVisitor(visitorId: string): Promise<VisitorNode> {
    return this.put(`/gen-admin/visitors/${visitorId}/checkout`);
  }

  async getFacilities(organizationId: string): Promise<Facility[]> {
    return this.get('/gen-admin/facilities', { params: { organization_id: organizationId } });
  }

  async createFacility(facility: Partial<Facility>, organizationId: string): Promise<Facility> {
    return this.post('/gen-admin/facilities', facility, {
      params: { organization_id: organizationId },
    });
  }

  async createFacilityBooking(booking: Partial<FacilityBooking>): Promise<FacilityBooking> {
    return this.post('/gen-admin/bookings', booking);
  }

  async getVehicles(organizationId: string): Promise<Vehicle[]> {
    return this.get('/gen-admin/vehicles', { params: { organization_id: organizationId } });
  }

  async createVehicle(vehicle: Partial<Vehicle>, organizationId: string): Promise<Vehicle> {
    return this.post('/gen-admin/vehicles', vehicle, {
      params: { organization_id: organizationId },
    });
  }

  async updateVehicle(
    id: string,
    vehicle: Partial<Vehicle>,
    organizationId: string
  ): Promise<Vehicle> {
    return this.put(`/gen-admin/vehicles/${id}`, vehicle, {
      params: { organization_id: organizationId },
    });
  }

  async deleteVehicle(id: string): Promise<void> {
    return this.delete(`/gen-admin/vehicles/${id}`);
  }

  async assignVehicleDriver(vehicleId: string, driverId: string): Promise<Vehicle> {
    return this.put(`/gen-admin/vehicles/${vehicleId}/assign`, { driver_id: driverId });
  }

  async getVehicleMaintenance(vehicleId: string): Promise<any[]> {
    return this.get(`/gen-admin/vehicles/${vehicleId}/maintenance`);
  }

  async logVehicleMaintenance(vehicleId: string, log: any): Promise<any> {
    return this.post(`/gen-admin/vehicles/${vehicleId}/maintenance`, log);
  }

  async getComplianceRecords(organizationId: string): Promise<AdminCompliance[]> {
    return this.get('/gen-admin/compliance', { params: { organization_id: organizationId } });
  }

  async createComplianceRecord(
    record: Partial<AdminCompliance>,
    organizationId: string
  ): Promise<AdminCompliance> {
    return this.post('/gen-admin/compliance', record, {
      params: { organization_id: organizationId },
    });
  }

  async getTravelRequests(organizationId: string): Promise<TravelRequest[]> {
    return this.get('/gen-admin/travel', { params: { organization_id: organizationId } });
  }

  async createTravelRequest(
    request: Partial<TravelRequest>,
    organizationId: string
  ): Promise<TravelRequest> {
    return this.post('/gen-admin/travel', request, {
      params: { organization_id: organizationId },
    });
  }

  async updateTravelRequestStatus(
    id: string,
    status: string,
    organizationId: string
  ): Promise<TravelRequest> {
    return this.put(
      `/gen-admin/travel/${id}/status`,
      { status },
      {
        params: { organization_id: organizationId },
      }
    );
  }

  // --- Onboarding ---
  async getHires(): Promise<NewHireNode[]> {
    return this.get('/onboarding/hires');
  }

  async saveHire(hire: NewHireNode): Promise<NewHireNode> {
    return this.post('/onboarding/hires', hire);
  }

  async updateHireStep(hireId: string, stepId: string): Promise<NewHireNode> {
    return this.put(`/onboarding/hires/${hireId}/steps/${stepId}`);
  }

  // --- Offboarding ---
  async getExits(): Promise<ExitNode[]> {
    return this.get('/offboarding/exits');
  }

  async saveExit(exit: Partial<ExitNode>): Promise<ExitNode> {
    return this.post('/offboarding/exits', exit);
  }

  async updateExitChecklist(exitId: string, itemId: string): Promise<ExitNode> {
    return this.put(`/offboarding/exits/${exitId}/checklist/${itemId}`);
  }
  async getSystemLogs(
    lines: number = 100
  ): Promise<{ logs: string[]; total: number; shown: number }> {
    const response = await this.request(`${this.apiUrl}/system/logs?lines=${lines}`);
    if (!response.ok) {
      throw new Error('Failed to fetch system logs');
    }
    return await response.json();
  }
}

export const api = new ApiService();
export default api;
