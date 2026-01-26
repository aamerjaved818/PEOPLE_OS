import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Login from './Login';
import { ThemeProvider } from '@/contexts/ThemeContext';

// Mock dependencies to isolate component logic
vi.mock('@/services/api', () => ({
  api: {
    login: vi.fn(),
  },
}));

vi.mock('@/utils/security', () => ({
  sanitizeInput: (input: string) => input,
}));

// Mock `import.meta.env` if needed, but Vitest usually handles it via config or it's empty in node.
// Wrapper for Theme Context
const renderWithProviders = (ui: React.ReactElement) => {
  return render(<ThemeProvider>{ui}</ThemeProvider>);
};

describe('Login Component', () => {
  it('renders without crashing', () => {
    renderWithProviders(<Login onLogin={vi.fn()} />);
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
  });

  it('renders input fields for username and password', () => {
    renderWithProviders(<Login onLogin={vi.fn()} />);
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  it('handles input changes', () => {
    renderWithProviders(<Login onLogin={vi.fn()} />);
    const usernameInput = screen.getByLabelText(/Username/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/Password/i) as HTMLInputElement;

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });
});
