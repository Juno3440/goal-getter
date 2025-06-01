import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NodeCard from '../../components/NodeCard';
import { TreeNode } from '../../types';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Test wrapper with router
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('NodeCard', () => {
  const mockTreeNode: TreeNode = {
    id: 'test-node-1',
    parent_id: null,
    title: 'Test Goal',
    progress: 0.65,
    status: 'active',
    style: {
      color: '#1f2937',
      accent: '#3b82f6'
    },
    ui: {
      collapsed: false
    },
    children: []
  };

  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders node information correctly', () => {
    render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} />
      </TestWrapper>
    );

    expect(screen.getByText('Test Goal')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('applies correct status badge colors', () => {
    const statuses: Array<TreeNode['status']> = ['pending', 'active', 'done', 'blocked'];
    const expectedColors = {
      pending: 'bg-yellow-500',
      active: 'bg-blue-500',
      done: 'bg-green-500',
      blocked: 'bg-red-500'
    };

    statuses.forEach(status => {
      const { unmount } = render(
        <TestWrapper>
          <NodeCard node={{ ...mockTreeNode, status }} />
        </TestWrapper>
      );

      const statusBadge = screen.getByText(status);
      expect(statusBadge).toHaveClass(expectedColors[status]);
      unmount();
    });
  });

  it('applies custom node styles', () => {
    const customNode = {
      ...mockTreeNode,
      style: {
        color: '#red',
        accent: '#blue'
      }
    };

    const { container } = render(
      <TestWrapper>
        <NodeCard node={customNode} />
      </TestWrapper>
    );

    const nodeCard = container.querySelector('.node-card');
    expect(nodeCard).toHaveStyle({
      '--node-bg': '#red',
      '--accent': '#blue'
    });
  });

  it('displays progress bar with correct value', () => {
    const { container } = render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} />
      </TestWrapper>
    );

    const progressBar = container.querySelector('progress');
    expect(progressBar).toHaveAttribute('value', '0.65');
    expect(progressBar).toHaveAttribute('max', '1');
  });

  it('calls onToggleCollapse when header is clicked', () => {
    const mockToggleCollapse = vi.fn();
    
    render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} onToggleCollapse={mockToggleCollapse} />
      </TestWrapper>
    );

    const header = screen.getByText('Test Goal').closest('.node-header');
    fireEvent.click(header!);

    expect(mockToggleCollapse).toHaveBeenCalledOnce();
    expect(mockToggleCollapse).toHaveBeenCalledWith('test-node-1');
  });

  it('navigates to goal detail when card body is clicked', () => {
    render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} />
      </TestWrapper>
    );

    const cardBody = screen.getByText('Progress').closest('.p-2');
    fireEvent.click(cardBody!);

    expect(mockNavigate).toHaveBeenCalledOnce();
    expect(mockNavigate).toHaveBeenCalledWith('/goal/test-node-1');
  });

  it('does not navigate when header is clicked', () => {
    const mockToggleCollapse = vi.fn();
    
    render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} onToggleCollapse={mockToggleCollapse} />
      </TestWrapper>
    );

    const header = screen.getByText('Test Goal').closest('.node-header');
    fireEvent.click(header!);

    // Should call toggle collapse but not navigate
    expect(mockToggleCollapse).toHaveBeenCalledOnce();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('handles missing onToggleCollapse prop gracefully', () => {
    render(
      <TestWrapper>
        <NodeCard node={mockTreeNode} />
      </TestWrapper>
    );

    const header = screen.getByText('Test Goal').closest('.node-header');
    
    // Should not throw error when clicking header without onToggleCollapse
    expect(() => fireEvent.click(header!)).not.toThrow();
  });

  it('truncates long titles properly', () => {
    const longTitleNode = {
      ...mockTreeNode,
      title: 'This is a very long goal title that should be truncated in the UI to prevent layout issues and maintain readability'
    };

    const { container } = render(
      <TestWrapper>
        <NodeCard node={longTitleNode} />
      </TestWrapper>
    );

    const titleElement = screen.getByText(longTitleNode.title);
    expect(titleElement).toHaveClass('truncate');
  });

  it('handles zero progress correctly', () => {
    const zeroProgressNode = { ...mockTreeNode, progress: 0 };
    
    render(
      <TestWrapper>
        <NodeCard node={zeroProgressNode} />
      </TestWrapper>
    );

    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('handles complete progress correctly', () => {
    const completeNode = { ...mockTreeNode, progress: 1 };
    
    render(
      <TestWrapper>
        <NodeCard node={completeNode} />
      </TestWrapper>
    );

    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('rounds progress percentage correctly', () => {
    const preciseProgressNode = { ...mockTreeNode, progress: 0.6789 };
    
    render(
      <TestWrapper>
        <NodeCard node={preciseProgressNode} />
      </TestWrapper>
    );

    expect(screen.getByText('68%')).toBeInTheDocument();
  });
});