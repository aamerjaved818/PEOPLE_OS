/**
 * Global Constants
 * Single source of truth for all configuration values
 */

// API Configuration
// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RATE_LIMIT: {
    MAX_REQUESTS: 100,
    WINDOW_MS: 60000, // 1 minute
  },
} as const;

// Server Ports
export const PORTS = {
  BACKEND_API: Number(import.meta.env.VITE_API_PORT) || 8000,
  FRONTEND_DEV: Number(import.meta.env.VITE_FRONTEND_PORT) || 5173,
  FRONTEND_PREVIEW: Number(import.meta.env.VITE_PREVIEW_PORT) || 9000,
  FRONTEND_TEST: 4040,
} as const;

// Environment URLs
export const ENVIRONMENT_URLS = {
  DEVELOPMENT: `http://localhost:${PORTS.FRONTEND_DEV}`,
  TEST: `http://localhost:${PORTS.FRONTEND_TEST}`,
  PREVIEW: `http://localhost:${PORTS.FRONTEND_PREVIEW}`,
} as const;

// Database Configuration
export const DATABASE_CONFIG = {
  FILES: {
    DEVELOPMENT: 'people_os.db',
    TEST: 'people_os_test.db',
    PRODUCTION: 'people_os.db',
  },
  PATH: './backend/data/',
} as const;

// Storage Keys
export const STORAGE_KEYS = {
  TOKEN: 'token',
  DATA_VERSION: 'data_version',
  CLEAN_SLATE: 'clean_slate_verified',
  THEME: 'theme_preference',
} as const;

// Timeouts (ms)
export const TIMEOUTS = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 10000,
  HEALTH_CHECK: 60000,
} as const;

// System Limits
export const LIMITS = {
  MAX_FILE_SIZE_MB: 10,
  MAX_UPLOAD_SIZE_MB: 50,
  STORAGE_QUOTA_MB: 5.0,
  MAX_BATCH_SIZE: 1000,
  MAX_SEARCH_RESULTS: 100,
} as const;

// Application Metadata
export const APP_METADATA = {
  NAME: 'peopleOS eBusiness Suite',
  NODE_NAME: 'Production Node',
  CLUSTER_TYPE: 'Static Cluster',
} as const;

// Employee Code Prefix
export const EMPLOYEE_CODE = {
  PREFIX: 'ABC01',
  PATTERN: 'ABC01-XXXX',
} as const;

// System Sections
export const SYSTEM_SECTIONS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'sys-admin', label: 'Access Control' },
  { id: 'ai', label: 'AI Settings' },
  { id: 'integrations', label: 'Integrations' },
  { id: 'audit', label: 'Audit Logs' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'maintenance', label: 'Maintenance' },
] as const;

// CORS Origins
export const CORS_ORIGINS = [
  `http://localhost:${PORTS.FRONTEND_DEV}`,
  `http://localhost:${PORTS.FRONTEND_TEST}`,
  `http://localhost:${PORTS.FRONTEND_PREVIEW}`,
  'http://localhost:8000',
  'http://127.0.0.1:5173',
] as const;
