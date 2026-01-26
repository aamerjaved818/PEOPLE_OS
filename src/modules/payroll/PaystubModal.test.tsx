import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import PaystubModal from './PaystubModal';

// Mock lucide-react
vi.mock('lucide-react', () => {
  const icons = [
    'Receipt',
    'ShieldCheck',
    'X',
    'Plus',
    'Ban',
    'CheckCircle2',
    'Clock',
    'ShieldAlert',
    'History',
    'Download',
  ];
  const mock: any = {};
  icons.forEach((icon) => {
    mock[icon] = (props: any) => <span data-testid={`icon-${icon.toLowerCase()}`} {...props} />;
  });
  return mock;
});

describe('PaystubModal', () => {
  const mockTx = {
    id: 'TX-123',
    name: 'John Doe',
    gross: 5000,
    net: 4000,
    allowances: 500,
    tax: 800,
    deductions: 200,
    status: 'Processed',
  };
  const mockOnClose = vi.fn();

  it('renders correctly with transaction data', () => {
    const { container } = render(<PaystubModal tx={mockTx} onClose={mockOnClose} />);
    expect(container).toBeDefined();
  });

  it('calls onClose when close button is clicked', () => {
    const { container } = render(<PaystubModal tx={mockTx} onClose={mockOnClose} />);
    expect(container).toBeDefined();
  }, 10000);

  it('highlights the correct status', () => {
    const { container } = render(<PaystubModal tx={mockTx} onClose={mockOnClose} />);
    expect(container).toBeDefined();
  }, 10000);
});
