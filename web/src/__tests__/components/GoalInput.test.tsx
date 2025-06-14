import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import GoalInput from '../../components/GoalInput';

// Mock session
const mockSession = {
  access_token: 'test-token',
  user: { id: 'user-123', email: 'test@example.com' }
} as any;

// Mock environment variable
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

// MSW server setup
const server = setupServer();

describe('GoalInput', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    server.resetHandlers();
  });

  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('renders input field and add button', () => {
    render(<GoalInput session={mockSession} />);

    expect(screen.getByPlaceholderText('Enter goal title...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'ADD' })).toBeInTheDocument();
  });

  it('updates input value when user types', () => {
    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    fireEvent.change(input, { target: { value: 'New Goal' } });

    expect(input).toHaveValue('New Goal');
  });

  it('disables button when input is empty', () => {
    render(<GoalInput session={mockSession} />);

    const button = screen.getByRole('button', { name: 'ADD' });
    expect(button).toBeDisabled();
  });

  it('enables button when input has text', () => {
    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    const button = screen.getByRole('button', { name: 'ADD' });

    fireEvent.change(input, { target: { value: 'New Goal' } });
    expect(button).not.toBeDisabled();
  });

  it('shows error when submitting empty title', async () => {
    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    const form = input.closest('form')!;
    
    // Set whitespace-only text
    fireEvent.change(input, { target: { value: '   ' } });
    
    // Submit form directly (button would be disabled)
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText('Goal title is required')).toBeInTheDocument();
    });
  });

  it('successfully creates goal and calls onGoalCreated', async () => {
    const mockOnGoalCreated = vi.fn();
    
    // Mock successful API response
    server.use(
      http.post('http://localhost:8000/goals', () => {
        return HttpResponse.json(
          { id: 'new-goal-id', title: 'Test Goal', status: 'todo' },
          { status: 201 }
        );
      })
    );

    render(<GoalInput session={mockSession} onGoalCreated={mockOnGoalCreated} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    const button = screen.getByRole('button', { name: 'ADD' });

    // Fill input and submit
    fireEvent.change(input, { target: { value: 'Test Goal' } });
    fireEvent.click(button);

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'ADDING...' })).toBeInTheDocument();
    });

    // Should clear input and call callback after success
    await waitFor(() => {
      expect(input).toHaveValue('');
      expect(mockOnGoalCreated).toHaveBeenCalledOnce();
      expect(screen.getByRole('button', { name: 'ADD' })).toBeInTheDocument();
    });
  });

  it('shows error message on API failure', async () => {
    // Mock failed API response
    server.use(
      http.post('http://localhost:8000/goals', () => {
        return HttpResponse.json(
          { error: 'Server error' },
          { status: 500 }
        );
      })
    );

    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    const button = screen.getByRole('button', { name: 'ADD' });

    fireEvent.change(input, { target: { value: 'Test Goal' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Failed to create goal')).toBeInTheDocument();
    });

    // Input should retain its value on error
    expect(input).toHaveValue('Test Goal');
  });

  it('sends correct request to API', async () => {
    let capturedRequest: any = null;

    server.use(
      http.post('http://localhost:8000/goals', async ({ request }) => {
        capturedRequest = {
          headers: Object.fromEntries(request.headers.entries()),
          body: await request.json()
        };
        return HttpResponse.json({ id: 'new-goal', title: 'Test Goal' }, { status: 201 });
      })
    );

    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    fireEvent.change(input, { target: { value: 'Test Goal' } });
    fireEvent.click(screen.getByRole('button', { name: 'ADD' }));

    await waitFor(() => {
      expect(capturedRequest).not.toBeNull();
    });

    expect(capturedRequest.headers['authorization']).toBe('Bearer test-token');
    expect(capturedRequest.headers['content-type']).toBe('application/json');
    expect(capturedRequest.body).toEqual({ title: 'Test Goal' });
  });

  it('trims whitespace from input', async () => {
    let capturedRequest: any = null;

    server.use(
      http.post('http://localhost:8000/goals', async ({ request }) => {
        capturedRequest = await request.json();
        return HttpResponse.json({ id: 'new-goal' }, { status: 201 });
      })
    );

    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    fireEvent.change(input, { target: { value: '  Test Goal  ' } });
    fireEvent.click(screen.getByRole('button', { name: 'ADD' }));

    await waitFor(() => {
      expect(capturedRequest).not.toBeNull();
    });

    expect(capturedRequest.title).toBe('Test Goal');
  });

  it('respects maxLength attribute', () => {
    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    expect(input).toHaveAttribute('maxLength', '200');
  });

  it('disables input and button during loading', async () => {
    // Mock slow API response
    server.use(
      http.post('http://localhost:8000/goals', async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return HttpResponse.json({ id: 'new-goal' }, { status: 201 });
      })
    );

    render(<GoalInput session={mockSession} />);

    const input = screen.getByPlaceholderText('Enter goal title...');
    const button = screen.getByRole('button', { name: 'ADD' });

    fireEvent.change(input, { target: { value: 'Test Goal' } });
    fireEvent.click(button);

    // Should disable both input and button during loading
    await waitFor(() => {
      expect(input).toBeDisabled();
      expect(screen.getByRole('button', { name: 'ADDING...' })).toBeDisabled();
    });
  });
});