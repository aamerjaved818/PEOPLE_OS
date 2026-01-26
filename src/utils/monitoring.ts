// Basic Sentry Stub
// To enable, install @sentry/react and uncomment

// import * as Sentry from '@sentry/react';

const isProd = import.meta.env.PROD;
// Sentry removed

import Logger from './logger';

export const initMonitoring = () => {
  // Monitoring initialized (Internal Logger)
};

export const logError = (error: Error, _context?: Record<string, any>) => {
  if (isProd) {
    Logger.error('[Monitor] Error:', error);
  } else {
    Logger.error('[Dev] Error:', error);
  }
};
