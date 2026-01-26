/**
 * Configuration Validation with Zod
 * Runtime validation for all application configuration
 *
 * RECOMMENDED IMPLEMENTATION - Place in src/config/validation.ts
 *
 * Install first: npm install zod
 *
 * This ensures:
 * - Runtime type checking
 * - Clear error messages
 * - Fail-fast on invalid configuration
 * - Type inference from schemas
 */

import { z } from 'zod';

// === API Configuration Schema ===
export const APIConfigSchema = z
  .object({
    BASE_URL: z.string().url('Invalid API URL'),
    TIMEOUT: z.number().int().positive('Timeout must be positive'),
    RETRY_ATTEMPTS: z.number().int().min(0, 'Retry attempts cannot be negative'),
    RATE_LIMIT: z.object({
      MAX_REQUESTS: z.number().int().positive(),
      WINDOW_MS: z.number().int().positive(),
    }),
  })
  .readonly();

// === Theme Schema ===
export const ThemeSchema = z.enum(['light', 'dark']);
export const ColorThemeSchema = z.enum(['quartz', 'cyber', 'forest', 'sunset']);
export const DensitySchema = z.enum(['compact', 'normal', 'relaxed']);

export const ThemeConfigSchema = z.object({
  theme: ThemeSchema,
  colorTheme: ColorThemeSchema,
  density: DensitySchema,
});

// === UI State Schema ===
export const UIStateSchema = z.object({
  activeModule: z.string().min(1),
  isSidebarOpen: z.boolean(),
  theme: ThemeSchema,
  colorTheme: ColorThemeSchema,
  density: DensitySchema,
});

// === Palette Schema ===
export const PaletteSchema = z
  .object({
    themes: z.any(),
    primary: z.string(),
    success: z.string(),
    warning: z.string(),
    danger: z.string(),
    info: z.string(),
    white: z.string(),
    charts: z.array(z.string()),
    grid: z.string(),
    border: z.string(),
    axis: z.string(),
    tooltipBg: z.string(),
    tooltipText: z.string(),
    attendance: z.object({
      Present: z.string(),
      Absent: z.string(),
      Late: z.string(),
      'On Leave': z.string(),
    }),
  })
  .readonly();

// === Limits Schema ===
export const LimitsSchema = z
  .object({
    MAX_FILE_SIZE_MB: z.number().positive(),
    MAX_UPLOAD_SIZE_MB: z.number().positive(),
    STORAGE_QUOTA_MB: z.number().positive(),
    MAX_BATCH_SIZE: z.number().int().positive(),
    MAX_SEARCH_RESULTS: z.number().int().positive(),
  })
  .readonly();

// === Master App Configuration Schema ===
export const AppConfigSchema = z.object({
  api: APIConfigSchema,
  theme: ThemeConfigSchema,
  palette: PaletteSchema,
  limits: LimitsSchema,
  // Add other sections as needed
});

// === Validation Helper Functions ===

/**
 * Validate entire app configuration
 * Call during app initialization
 */
export function validateAppConfig(config: any): boolean {
  try {
    AppConfigSchema.parse(config);
    // eslint-disable-next-line no-console
    console.log('✅ Configuration validated successfully');
    return true;
  } catch (error) {
    if (error instanceof z.ZodError) {
       
      console.error('❌ Configuration validation failed:');
      error.issues.forEach((err: any) => {
        console.error(`  - ${err.path.join('.')}: ${err.message}`);
      });
    }
    return false;
  }
}

/**
 * Validate API configuration
 */
export function validateAPIConfig(config: any): boolean {
  try {
    APIConfigSchema.parse(config);
    return true;
  } catch (error) {
    console.error('Invalid API configuration:', error);
    return false;
  }
}

/**
 * Validate theme configuration
 */
export function validateThemeConfig(config: any): boolean {
  try {
    ThemeConfigSchema.parse(config);
    return true;
  } catch (error) {
    console.error('Invalid theme configuration:', error);
    return false;
  }
}

/**
 * Get validation errors as readable messages
 */
export function getConfigErrors(config: any): string[] {
  try {
    AppConfigSchema.parse(config);
    return [];
  } catch (error) {
    if (error instanceof z.ZodError) {
      return error.issues.map((err: any) => `${err.path.join('.')}: ${err.message}`);
    }
    return ['Unknown validation error'];
  }
}

/**
 * Usage Example:
 *
 * // In main.tsx or App.tsx
 * import { validateAppConfig } from '@/config/validation';
 * import { API_CONFIG, PALETTE } from '@/config';
 *
 * // Validate on app init
 * if (!validateAppConfig({ api: API_CONFIG, palette: PALETTE })) {
 *   throw new Error('Invalid application configuration');
 * }
 *
 * // Or validate specific parts
 * import { validateThemeConfig } from '@/config/validation';
 *
 * if (!validateThemeConfig({ theme: 'dark', colorTheme: 'cyber', density: 'normal' })) {
 *   console.warn('Theme config invalid, using defaults');
 * }
 */
