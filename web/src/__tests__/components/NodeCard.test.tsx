import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import NodeCard from '../../components/NodeCard';
import { TreeNode } from '../../types';

const mockNode: TreeNode = {
  id: '123',
  title: 'Test Goal',
  status: 'pending',
  progress: 0.65,
  parent_id: null,
  style: {
    color: '#1f2937',
    accent: '#3b82f6'
  },
  ui: {
    collapsed: false
  },
  children: []
};

const renderNodeCard = (node: TreeNode = mockNode, onToggleCollapse?: (id: string) => void) => {
  return render(
    <NodeCard node={node} onToggleCollapse={onToggleCollapse} />
  );
};

describe('NodeCard', () => {
  it('renders node information correctly', () => {
    renderNodeCard();
    
    expect(screen.getByText('Test Goal')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();
    expect(screen.getByText('Progress')).toBeInTheDocument();
    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('applies correct status badge colors', () => {
    const expectedColors = {
      pending: 'retro-status-pending',
      active: 'retro-status-active', 
      done: 'retro-status-done',
      blocked: 'retro-status-blocked'
    };

    Object.entries(expectedColors).forEach(([status, expectedClass]) => {
      const { unmount } = renderNodeCard({ ...mockNode, status: status as TreeNode['status'] });

      const statusBadge = screen.getByText(status);
      expect(statusBadge).toHaveClass(expectedClass);
      unmount();
    });
  });

  it('applies custom node styles', () => {
    const { container } = renderNodeCard();

    const nodeCard = container.querySelector('.retro-node-card');
    expect(nodeCard).toBeInTheDocument();
    expect(nodeCard).toHaveClass('retro-node-card', 'w-full', 'h-full');
  });

  it('displays progress bar with correct value', () => {
    const { container } = renderNodeCard({ ...mockNode, progress: 0.65 });

    const progressFill = container.querySelector('.retro-progress-fill');
    expect(progressFill).toHaveStyle({ width: '65%' });
  });

  it('calls onToggleCollapse when header is clicked', () => {
    const mockToggleCollapse = vi.fn();
    renderNodeCard(mockNode, mockToggleCollapse);

    const header = screen.getByText('Test Goal').closest('.retro-node-header');
    expect(header).toBeInTheDocument();
    fireEvent.click(header!);

    expect(mockToggleCollapse).toHaveBeenCalledOnce();
    expect(mockToggleCollapse).toHaveBeenCalledWith('123');
  });

  it('handles missing onToggleCollapse prop gracefully', () => {
    renderNodeCard();

    const header = screen.getByText('Test Goal').closest('.retro-node-header');
    expect(header).toBeInTheDocument();
    
    // Should not throw error when clicking header without onToggleCollapse
    expect(() => fireEvent.click(header!)).not.toThrow();
  });

  it('truncates long titles properly', () => {
    const longTitleNode = { ...mockNode, title: 'This is a very long goal title that should be truncated' };
    renderNodeCard(longTitleNode);

    const titleElement = screen.getByText('This is a very long goal title that should be truncated');
    expect(titleElement).toHaveClass('truncate');
  });

  it('handles zero progress correctly', () => {
    const { container } = renderNodeCard({ ...mockNode, progress: 0 });

    const progressFill = container.querySelector('.retro-progress-fill');
    expect(progressFill).toHaveStyle({ width: '0%' });
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('handles complete progress correctly', () => {
    const { container } = renderNodeCard({ ...mockNode, progress: 1 });

    const progressFill = container.querySelector('.retro-progress-fill');
    expect(progressFill).toHaveStyle({ width: '100%' });
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('rounds progress percentage correctly', () => {
    const { container } = renderNodeCard({ ...mockNode, progress: 0.756 });

    expect(screen.getByText('76%')).toBeInTheDocument();
    const progressFill = container.querySelector('.retro-progress-fill');
    expect(progressFill).toHaveStyle({ width: '75.6%' });
  });
});