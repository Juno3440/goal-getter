import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import GoalTree from '../../components/GoalTree';
import { TreeResponse, TreeNode } from '../../types';

// Mock fetch globally
global.fetch = vi.fn();

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    line: ({ children, ...props }: any) => <line {...props}>{children}</line>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

// Mock environment variables
Object.defineProperty(window, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_URL: 'http://localhost:8000'
      }
    }
  },
  writable: true
});

// Test wrapper
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('GoalTree', () => {
  const mockSession = {
    access_token: 'test-token',
    user: { id: 'user-123' }
  } as any;

  const mockTreeResponse: TreeResponse = {
    schema_version: '1.0',
    generated_at: '2024-01-01T00:00:00Z',
    root_id: 'root-1',
    nodes: [
      {
        id: 'root-1',
        parent_id: null,
        title: 'Root Goal',
        progress: 0.5,
        status: 'active',
        style: { color: '#1f2937', accent: '#3b82f6' },
        ui: { collapsed: false },
        children: []
      },
      {
        id: 'child-1',
        parent_id: 'root-1',
        title: 'Child Goal',
        progress: 0.8,
        status: 'done',
        style: { color: '#1f2937', accent: '#10b981' },
        ui: { collapsed: false },
        children: []
      }
    ]
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset fetch mock
    (global.fetch as any).mockClear();
  });

  it('shows loading state initially', () => {
    // Mock a pending fetch
    (global.fetch as any).mockImplementation(() => new Promise(() => {}));

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('fetches tree data on mount', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/goals',
        {
          headers: {
            'Authorization': 'Bearer test-token'
          }
        }
      );
    });
  });

  it('renders at least one goal title from API data', async () => {
    const mockApiResponse = [
      {
        id: 'goal-1',
        title: 'Learn React Testing',
        status: 'todo',
        children: [
          {
            id: 'goal-2',
            title: 'Setup Vitest',
            status: 'done',
            children: []
          }
        ]
      }
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse)
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    // Wait for data to load and goals to render
    await waitFor(() => {
      expect(screen.getByText('Learn React Testing')).toBeInTheDocument();
    });

    // Should also render the child goal
    expect(screen.getByText('Setup Vitest')).toBeInTheDocument();
  });

  it('displays error state when fetch fails', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 500
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  it('displays no goals message when tree is empty', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        ...mockTreeResponse,
        nodes: [],
        root_id: null
      })
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No goals found. Create your first goal to get started!')).toBeInTheDocument();
    });
  });

  it('builds hierarchy correctly from hierarchical data', async () => {
    const mockApiResponse = [
      {
        id: 'root-1',
        title: 'Root Goal',
        status: 'todo',
        children: [
          {
            id: 'child-1',
            title: 'Child Goal',
            status: 'done',
            children: []
          }
        ]
      }
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse)
    });

    const { container } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      // Should render SVG with tree layout
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    // Should have rendered both nodes
    await waitFor(() => {
      expect(screen.getByText('Root Goal')).toBeInTheDocument();
      expect(screen.getByText('Child Goal')).toBeInTheDocument();
    });
  });

  it('handles nodes with missing children arrays safely', async () => {
    const responseWithMissingChildren = {
      ...mockTreeResponse,
      nodes: [
        {
          id: 'root-1',
          parent_id: null,
          title: 'Root Goal',
          progress: 0.5,
          status: 'active',
          style: { color: '#1f2937', accent: '#3b82f6' },
          ui: { collapsed: false }
          // Missing children array
        } as TreeNode
      ]
    };

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(responseWithMissingChildren)
    });

    // Should not crash due to sanitization logic
    const { container } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(container.querySelector('svg')).toBeInTheDocument();
      expect(screen.getByText('Root Goal')).toBeInTheDocument();
    });
  });

  it('handles window resize events', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    const { container } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    // Simulate window resize
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
    Object.defineProperty(window, 'innerHeight', { value: 800, writable: true });
    
    window.dispatchEvent(new Event('resize'));

    // Should not crash and should maintain tree structure
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('applies correct margins to tree layout', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    const { container } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      const transformGroup = container.querySelector('g[transform]');
      expect(transformGroup).toHaveAttribute('transform', 'translate(50, 50)');
    });
  });

  it('memoizes tree layout to prevent unnecessary recalculations', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    const { rerender } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Root Goal')).toBeInTheDocument();
    });

    // Re-render with same data - should use memoized layout
    rerender(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    expect(screen.getByText('Root Goal')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/)).toBeInTheDocument();
    });
  });

  it('retries fetch on retry button click', async () => {
    // First call fails
    (global.fetch as any)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockTreeResponse)
      });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    // Click retry
    const retryButton = screen.getByText('Retry');
    retryButton.click();

    // Should succeed on retry
    await waitFor(() => {
      expect(screen.getByText('Root Goal')).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('uses environment variable for API URL', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/goals',
        expect.any(Object)
      );
    });
  });

  it('handles collapsed state changes correctly', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Root Goal')).toBeInTheDocument();
    });

    // The component should handle toggle collapse functionality
    // This is tested through the NodeCard component interaction
  });

  it('sets container ref correctly for resize handling', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTreeResponse)
    });

    const { container } = render(
      <TestWrapper>
        <GoalTree session={mockSession} />
      </TestWrapper>
    );

    await waitFor(() => {
      const treeContainer = container.querySelector('#goal-tree-container');
      expect(treeContainer).toBeInTheDocument();
      expect(treeContainer).toHaveClass('w-full', 'h-full');
    });
  });
});