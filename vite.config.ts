import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');

  return {
    server: {
      port: parseInt(env.FRONTEND_PORT || '5000'),
      host: true,
      open: false,
    },
    preview: {
      port: parseInt(env.PREVIEW_PORT || '9000'),
      host: true,
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@services': path.resolve(__dirname, './src/services'),
        '@store': path.resolve(__dirname, './src/store'),
        '@utils': path.resolve(__dirname, './src/utils'),
      },
    },
    build: {
      outDir: 'dist',
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, 'index.html'),
        },
        output: {
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              // React Core
              if (
                id.includes('react') ||
                id.includes('react-dom') ||
                id.includes('react-router-dom')
              ) {
                return 'vendor-react';
              }
              // Icons (Large package)
              if (id.includes('lucide-react')) {
                return 'vendor-icons';
              }
              // Charts
              if (id.includes('chart.js') || id.includes('recharts')) {
                return 'vendor-charts';
              }
              // All other vendors
              return 'vendor-utils';
            }
            return null;
          },
        },
      },
      chunkSizeWarningLimit: 1200,
    },
  };
});
