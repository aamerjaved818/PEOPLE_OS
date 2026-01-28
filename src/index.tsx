import React from 'react';
import ReactDOM from 'react-dom/client';
// import App from './App'; // Switched to dynamic import
import './index.css';

// Debug logging
console.log('🚀 PEOPLE_OS starting...');
fetch(`${import.meta.env.VITE_API_URL}/health?boot=index_started`).catch(() => {});
console.log('Environment:', import.meta.env.MODE);
console.log('API URL:', import.meta.env.VITE_API_URL);

// Global error handler
window.addEventListener('error', (event) => {
  console.error('💥 Global error:', event.error);
  document.body.innerHTML = `
    <div style="padding: 20px; font-family: monospace; color: red;">
      <h1>Application Error</h1>
      <p>${event.error?.message || 'Unknown error'}</p>
      <pre>${event.error?.stack || ''}</pre>
    </div>
  `;
});

const rootElement = document.getElementById('root');

if (!rootElement) {
  console.error('❌ Root element not found');
  document.body.innerHTML = '<h1 style="color: red;">Error: Root element not found</h1>';
} else {
  // Dynamic import to catch load errors that would otherwise block the entire script
  import('./App')
    .then(({ default: App }) => {
      console.log('✅ App module loaded successfully');
      ReactDOM.createRoot(rootElement).render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
      console.log('✅ PEOPLE_OS rendered successfully');
    })
    .catch((error) => {
      console.error('❌ Failed to load App component:', error);
      document.body.innerHTML = `
        <div style="padding: 20px; font-family: sans-serif; background: #1a1a1a; color: white; height: 100vh; display: flex; flex-direction: column; justify-content: center; items-items: center; text-align: center;">
          <h1 style="color: #ef4444; margin-bottom: 20px;">Startup Error</h1>
          <p style="font-size: 1.2rem; margin-bottom: 20px;">Failed to load application modules.</p>
          <pre style="background: #000; padding: 20px; border-radius: 8px; text-align: left; overflow: auto; max-width: 800px; margin: 0 auto; border: 1px solid #333;">${error.message}\n${error.stack || ''}</pre>
          <button onclick="window.location.reload()" style="margin-top: 40px; padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem;">Retry / Reload</button>
        </div>
      `;
    });
}
