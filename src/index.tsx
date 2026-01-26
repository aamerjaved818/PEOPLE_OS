import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Debug logging
console.log('🚀 PEOPLE_OS starting...');
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
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  console.log('✅ PEOPLE_OS rendered successfully');
}
