/**
 * Configuration Type Definitions
 * Centralized types for full application type safety
 *
 * RECOMMENDED IMPLEMENTATION - Place in src/config/types.ts
 *
 * These types ensure:
 * - Type-safe configuration access
 * - Better IDE support
 * - Compile-time error detection
 * - Clear configuration contracts
 */

// === API Configuration Types ===
export interface ApiConfigType {
  readonly BASE_URL: string;
  readonly TIMEOUT: number;
  readonly RETRY_ATTEMPTS: number;
  readonly RATE_LIMIT: {
    readonly MAX_REQUESTS: number;
    readonly WINDOW_MS: number;
  };
}

export interface PortsConfig {
  readonly BACKEND_API: number;
  readonly FRONTEND_DEV: number;
  readonly FRONTEND_TEST: number;
  readonly FRONTEND_PROD: number;
  readonly AI_ENGINE: number;
}

export interface DatabaseConfigType {
  readonly FILES: {
    readonly DEVELOPMENT: string;
    readonly TEST: string;
    readonly PRODUCTION: string;
  };
  readonly PATH: string;
}

// === Theme Configuration Types ===
export type Theme = 'light' | 'dark';
export type ColorTheme =
  | 'quartz'
  | 'cyber'
  | 'forest'
  | 'sunset'
  | 'navy'
  | 'gold'
  | 'deeppink'
  | 'fuchsia'
  | 'orange';
export type Density = 'compact' | 'normal' | 'relaxed';

export interface ThemeConfig {
  theme: Theme;
  colorTheme: ColorTheme;
  density: Density;
}

export interface PaletteType {
  readonly themes: Record<ColorTheme, string>;
  readonly primary: string;
  readonly success: string;
  readonly warning: string;
  readonly danger: string;
  readonly info: string;
  readonly white: string;
  readonly charts: readonly string[];
  readonly grid: string;
  readonly border: string;
  readonly axis: string;
  readonly tooltipBg: string;
  readonly tooltipText: string;
  readonly attendance: {
    readonly Present: string;
    readonly Absent: string;
    readonly Late: string;
    readonly 'On Leave': string;
  };
}

// === UI State Types ===
export interface UIState {
  activeModule: string;
  isSidebarOpen: boolean;
  theme: Theme;
  colorTheme: ColorTheme;
  density: Density;
}

export interface UIConfig extends UIState {
  setActiveModule: (module: string) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  setTheme: (theme: Theme) => void;
  setColorTheme: (colorTheme: ColorTheme) => void;
  setDensity: (density: Density) => void;
}

// === System Configuration Types ===
export interface AppLimits {
  readonly MAX_FILE_SIZE_MB: number;
  readonly MAX_UPLOAD_SIZE_MB: number;
  readonly STORAGE_QUOTA_MB: number;
  readonly MAX_BATCH_SIZE: number;
  readonly MAX_SEARCH_RESULTS: number;
}

export interface AppMetadata {
  readonly NAME: string;
  readonly VERSION: string;
  readonly API_VERSION: string;
  readonly NODE_NAME: string;
  readonly CLUSTER_TYPE: string;
}

export interface Timeouts {
  readonly SHORT: number;
  readonly MEDIUM: number;
  readonly LONG: number;
  readonly HEALTH_CHECK: number;
}

// === Storage Keys Types ===
export interface StorageKeysType {
  readonly TOKEN: string;
  readonly DATA_VERSION: string;
  readonly CLEAN_SLATE: string;
  readonly THEME: string;
}

// === Unified App Configuration ===
export interface AppConfig {
  readonly api: ApiConfigType;
  readonly database: DatabaseConfigType;
  readonly theme: ThemeConfig;
  readonly palette: PaletteType;
  readonly ui: UIConfig;
  readonly limits: AppLimits;
  readonly metadata: AppMetadata;
  readonly timeouts: Timeouts;
  readonly storage: StorageKeysType;
  readonly ports: PortsConfig;
}

// === Permissions Types ===
export interface PermissionSet {
  readonly [key: string]: boolean;
}

export interface RolePermissions {
  readonly [role: string]: PermissionSet;
}

// === Validation Schema Types ===
export interface ValidationSchema {
  validate: (config: any) => boolean;
  getErrors: () => string[];
}

/**
 * Usage Examples:
 *
 * // In a component
 * import type { ThemeConfig, ColorTheme } from '@/config/types';
 *
 * const myTheme: ThemeConfig = {
 *   theme: 'dark',
 *   colorTheme: 'cyber',
 *   density: 'normal',
 * };
 *
 * // In a service
 * import type { AppConfig, ApiConfigType } from '@/config/types';
 *
 * function initializeAPI(config: ApiConfigType) {
 *   // Type-safe config access
 *   const url: string = config.BASE_URL;
 *   const timeout: number = config.TIMEOUT;
 * }
 */
