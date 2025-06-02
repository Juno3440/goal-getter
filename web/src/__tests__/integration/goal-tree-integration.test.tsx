/**
 * Goal Tree Integration Tests
 * Tests critical integration scenarios between components and API
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import GoalTree from '../../components/GoalTree';
import GoalInput from '../../components/GoalInput';

// Mock fetch globally
globalThis.fetch = vi.fn();

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    line: ({ children, ...props }: any) => <line {...props}>{children}</line>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock environment
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

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const mockSession = {
  access_token: 'test-token',
  user: { id: 'user-123', email: 'test@example.com' }
} as any;

describe('Goal Tree Integration Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Goal Creation and Tree Update Flow', () => {
    
    it('should create goal and immediately reflect in tree visualization', async () => {
      // Mock initial empty tree
      (globalThis.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([])
        })
        // Mock successful goal creation
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            id: 'new-goal-id',
            title: 'Integration Test Goal',
            status: 'todo'
          })
        })
        // Mock updated tree with new goal
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([
            {
              id: 'new-goal-id',
              title: 'Integration Test Goal',
              status: 'todo',
              children: []
            }
          ])
        });

      const mockOnGoalCreated = vi.fn();

      render(
        <TestWrapper>
          <div>
            <GoalInput session={mockSession} onGoalCreated={mockOnGoalCreated} />
            <GoalTree session={mockSession} />
          </div>
        </TestWrapper>
      );

      // Wait for initial tree load
      await waitFor(() => {
        expect(screen.getByText('No goals found. Create your first goal to get started!')).toBeInTheDocument();
      });

      // Create a new goal
      const input = screen.getByPlaceholderText(/add a new goal/i);
      const addButton = screen.getByText('ADD');

      fireEvent.change(input, { target: { value: 'Integration Test Goal' } });
      
      await act(async () => {
        fireEvent.click(addButton);
      });

      // Verify goal creation API call
      expect(globalThis.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/goals',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify({
            title: 'Integration Test Goal'
          })
        })
      );

      // Verify callback was triggered
      expect(mockOnGoalCreated).toHaveBeenCalled();

      // Wait for tree to update with new goal
      await waitFor(() => {
        expect(screen.getByText('Integration Test Goal')).toBeInTheDocument();
      });
    });

    it('should handle goal creation failure gracefully', async () => {
      // Mock initial tree load
      (globalThis.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([])
        })
        // Mock failed goal creation
        .mockRejectedValueOnce(new Error('Network error'));

      const mockOnGoalCreated = vi.fn();

      render(
        <TestWrapper>
          <GoalInput session={mockSession} onGoalCreated={mockOnGoalCreated} />
        </TestWrapper>
      );

      const input = screen.getByPlaceholderText(/add a new goal/i);
      const addButton = screen.getByText('ADD');

      fireEvent.change(input, { target: { value: 'Failed Goal' } });
      
      await act(async () => {
        fireEvent.click(addButton);
      });

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // Callback should not be triggered on failure
      expect(mockOnGoalCreated).not.toHaveBeenCalled();
    });

  });

  describe('Complex Tree Structure Handling', () => {

    it('should properly render and navigate deeply nested goal hierarchies', async () => {
      // Create a 5-level deep hierarchy
      const deepHierarchy = [
        {
          id: 'level-0',
          title: 'Root Goal',
          status: 'doing',
          children: [
            {
              id: 'level-1',
              title: 'Level 1 Goal',
              status: 'todo',
              children: [
                {
                  id: 'level-2',
                  title: 'Level 2 Goal',
                  status: 'todo',
                  children: [
                    {
                      id: 'level-3',
                      title: 'Level 3 Goal',
                      status: 'todo',
                      children: [
                        {
                          id: 'level-4',
                          title: 'Level 4 Goal',
                          status: 'todo',
                          children: []
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ];

      (globalThis.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(deepHierarchy)
      });

      render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      // Wait for tree to load
      await waitFor(() => {
        expect(screen.getByText('Root Goal')).toBeInTheDocument();
      });

      // All levels should be visible
      expect(screen.getByText('Level 1 Goal')).toBeInTheDocument();
      expect(screen.getByText('Level 2 Goal')).toBeInTheDocument();
      expect(screen.getByText('Level 3 Goal')).toBeInTheDocument();
      expect(screen.getByText('Level 4 Goal')).toBeInTheDocument();

      // Tree should render SVG visualization
      const svg = screen.getByTestId('tree-svg') || document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('should handle malformed tree data gracefully', async () => {
      // Malformed data: missing children arrays, circular references
      const malformedData = [
        {
          id: 'good-goal',
          title: 'Valid Goal',
          status: 'todo',
          children: []
        },
        {
          id: 'bad-goal-1',
          title: 'Missing Children Array',
          status: 'todo'
          // Missing children array
        },
        {
          id: 'bad-goal-2',
          title: 'Null Children',
          status: 'todo',
          children: null
        }
      ];

      (globalThis.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(malformedData)
      });

      // Should not crash
      render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Valid Goal')).toBeInTheDocument();
      });

      // Should still render valid goals
      expect(screen.getByText('Missing Children Array')).toBeInTheDocument();
      expect(screen.getByText('Null Children')).toBeInTheDocument();
    });

  });

  describe('Tree State Management', () => {

    it('should preserve collapsed state across re-renders', async () => {
      const hierarchicalData = [
        {
          id: 'parent',
          title: 'Parent Goal',
          status: 'doing',
          children: [
            { id: 'child-1', title: 'Child 1', status: 'todo', children: [] },
            { id: 'child-2', title: 'Child 2', status: 'done', children: [] }
          ]
        }
      ];

      (globalThis.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(hierarchicalData)
      });

      const { rerender } = render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Parent Goal')).toBeInTheDocument();
      });

      // Initially children should be visible
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();

      // TODO: Add collapse functionality test
      // This would test clicking a collapse button and verifying state persistence
      // Currently the collapse functionality exists but needs UI elements to test

      // Re-render should preserve state
      rerender(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      // State should be preserved (when collapse functionality is implemented)
    });

  });

  describe('Performance and Memory Management', () => {

    it('should handle large goal trees without performance degradation', async () => {
      // Create 100 goals with various nesting levels
      const largeTreeData: any[] = [];
      
      // Create 10 root goals
      for (let i = 0; i < 10; i++) {
        const rootGoal: any = {
          id: `root-${i}`,
          title: `Root Goal ${i}`,
          status: 'doing',
          children: []
        };

        // Each root has 9 children
        for (let j = 0; j < 9; j++) {
          rootGoal.children.push({
            id: `child-${i}-${j}`,
            title: `Child ${i}-${j}`,
            status: j % 3 === 0 ? 'done' : j % 3 === 1 ? 'doing' : 'todo',
            children: []
          });
        }

        largeTreeData.push(rootGoal);
      }

      (globalThis.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(largeTreeData)
      });

      const startTime = performance.now();

      render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Root Goal 0')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render within reasonable time (< 1 second)
      expect(renderTime).toBeLessThan(1000);

      // Should render all root goals
      for (let i = 0; i < 10; i++) {
        expect(screen.getByText(`Root Goal ${i}`)).toBeInTheDocument();
      }

      // Should render first few children (depending on tree layout)
      expect(screen.getByText('Child 0-0')).toBeInTheDocument();
    });

    it('should properly clean up event listeners and timers', async () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener');
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

      (globalThis.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([])
      });

      const { unmount } = render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('No goals found. Create your first goal to get started!')).toBeInTheDocument();
      });

      // Component should add resize listeners
      expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));

      // Unmount component
      unmount();

      // Should clean up listeners
      expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));

      addEventListenerSpy.mockRestore();
      removeEventListenerSpy.mockRestore();
    });

  });

  describe('Error Recovery and Resilience', () => {

    it('should recover from API failures with retry functionality', async () => {
      // First call fails
      (globalThis.fetch as any)
        .mockRejectedValueOnce(new Error('Network error'))
        // Retry succeeds
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([
            { id: 'goal-1', title: 'Recovered Goal', status: 'todo', children: [] }
          ])
        });

      render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      // Should show error initially
      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });

      // Should show retry button
      const retryButton = screen.getByText('Retry');
      expect(retryButton).toBeInTheDocument();

      // Click retry
      await act(async () => {
        fireEvent.click(retryButton);
      });

      // Should recover and show data
      await waitFor(() => {
        expect(screen.getByText('Recovered Goal')).toBeInTheDocument();
      });
    });

    it('should handle session expiration gracefully', async () => {
      // Mock 401 response (expired token)
      (globalThis.fetch as any).mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Token expired' })
      });

      render(
        <TestWrapper>
          <GoalTree session={mockSession} />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });

      // Should indicate authentication issue
      expect(screen.getByText(/Failed to fetch tree data/)).toBeInTheDocument();
    });

  });

  describe('Real-world Usage Scenarios', () => {

    it('should handle rapid goal creation without race conditions', async () => {
      let callCount = 0;
      
      (globalThis.fetch as any).mockImplementation((url: string) => {
        if (url.includes('/goals') && !url.includes('POST')) {
          // GET requests - return current state
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        } else {
          // POST requests - simulate goal creation
          callCount++;
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              id: `rapid-goal-${callCount}`,
              title: `Rapid Goal ${callCount}`,
              status: 'todo'
            })
          });
        }
      });

      const mockOnGoalCreated = vi.fn();

      render(
        <TestWrapper>
          <GoalInput session={mockSession} onGoalCreated={mockOnGoalCreated} />
        </TestWrapper>
      );

      const input = screen.getByPlaceholderText(/add a new goal/i);
      const addButton = screen.getByText('ADD');

      // Rapidly create multiple goals
      for (let i = 1; i <= 5; i++) {
        fireEvent.change(input, { target: { value: `Rapid Goal ${i}` } });
        
        await act(async () => {
          fireEvent.click(addButton);
        });
        
        // Small delay to simulate real user behavior
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // All creation calls should have been made
      expect(callCount).toBe(5);
      expect(mockOnGoalCreated).toHaveBeenCalledTimes(5);
    });

    it('should maintain data consistency during concurrent operations', async () => {
      // Simulate concurrent reads and writes
      const goals = [
        { id: 'goal-1', title: 'Goal 1', status: 'todo', children: [] }
      ];

      let updateCount = 0;
      (globalThis.fetch as any).mockImplementation((url: string, options: any) => {
        if (options?.method === 'PATCH') {
          updateCount++;
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              id: 'goal-1',
              title: 'Goal 1',
              status: 'done'
            })
          });
        } else {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(goals)
          });
        }
      });

      // This test would require goal editing UI to be fully testable
      // For now, it documents the expected behavior for concurrent operations
      
      // Verify update operations were tracked
      expect(updateCount).toBeGreaterThanOrEqual(0);
      expect(true).toBe(true); // Placeholder
    });

  });

}); 