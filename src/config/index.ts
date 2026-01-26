/**
 * Unified Configuration Index
 * Single entry point for all application configuration and theme settings
 *
 * Benefits:
 * - Single import point for all configs
 * - Improved IDE autocompletion
 * - Centralized management
 * - Easier maintenance
 */

// === API & Database Configuration ===
export { API_CONFIG, PORTS, ENVIRONMENT_URLS, DATABASE_CONFIG, CORS_ORIGINS } from './constants';

// === Application Settings ===
export {
  STORAGE_KEYS,
  TIMEOUTS,
  LIMITS,
  APP_METADATA,
  SYSTEM_SECTIONS,
  EMPLOYEE_CODE,
} from './constants';

// === Permissions Configuration ===
export {
  SYSTEM_ROLES,
  SUPER_ROLES,
  DEFAULT_ROLE_PERMISSIONS,
  ROLE_HIERARCHY,
  hasPermission,
  getRoleLevel,
  isHigherRole,
  isSystemRole,
  hasAuthorityOver,
} from './permissions';

// === Types ===
export type { AppConfig, ApiConfigType, DatabaseConfigType, ThemeConfig, UIConfig } from './types';
