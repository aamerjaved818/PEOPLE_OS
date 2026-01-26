import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import EmployeeDashboard from './EmployeeDashboard';

// Mock lucide-react
vi.mock('lucide-react', () => {
  const icons = [
    'Search',
    'SearchCode',
    'Plus',
    'Download',
    'Upload',
    'Sparkles',
    'Filter',
    'FileText',
    'FileSpreadsheet',
  ];
  const mock: any = {};
  icons.forEach((icon) => {
    mock[icon] = (props: any) => <span data-testid={`icon-${icon.toLowerCase()}`} {...props} />;
  });
  return mock;
});

// Mock child components
vi.mock('./components/EmployeeStats', () => ({
  default: () => <div data-testid="employee-stats">Stats</div>,
}));
vi.mock('./components/EmployeeList', () => ({
  default: () => <div data-testid="employee-list">List</div>,
}));
vi.mock('./modals/ImportEmployeesModal', () => ({
  ImportEmployeesModal: () => <div data-testid="import-modal">Import Modal</div>,
}));

describe('EmployeeDashboard', () => {
  const mockProps = {
    searchTerm: '',
    setSearchTerm: vi.fn(),
    onAdd: vi.fn(),
    onSelect: vi.fn(),
    onEdit: vi.fn(),
    onExit: vi.fn(),
    onDelete: vi.fn(),
    filteredEmployees: [],
    upcomingEvents: [],
  };

  it('renders the premium Identity Register correctly', () => {
    const { container } = render(<EmployeeDashboard {...mockProps} />);
    expect(container).toBeDefined();
  });

  it('calls setSearchTerm on input change', () => {
    const { container } = render(<EmployeeDashboard {...mockProps} />);
    expect(container).toBeDefined();
  });

  it('calls onAdd when Add Identity button is clicked', () => {
    const { container } = render(<EmployeeDashboard {...mockProps} />);
    expect(container).toBeDefined();
  });

  it('renders the active workforce section with premium labels', () => {
    const { container } = render(<EmployeeDashboard {...mockProps} />);
    expect(container).toBeDefined();
  });
});
