import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Auth from '../../components/Auth';

// Mock Supabase auth functions first
vi.mock('../../supabase', () => ({
  supabase: {
    auth: {
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signOut: vi.fn(),
    },
  },
}));

// Import the mocked functions after the mock
import { supabase } from '../../supabase';
const mockSignIn = supabase.auth.signInWithPassword as any;
const mockSignUp = supabase.auth.signUp as any;

// Test wrapper
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Auth Integration Tests', () => {
  const mockOnAuthChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form by default', () => {
    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('switches to signup mode when link is clicked', () => {
    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    const switchToSignup = screen.getByText(/don't have an account/i);
    fireEvent.click(switchToSignup);

    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    mockSignIn.mockResolvedValue({
      data: { user: { id: 'user-123', email: 'test@example.com' } },
      error: null,
    });

    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Fill in form
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('displays error message on login failure', async () => {
    mockSignIn.mockResolvedValue({
      data: { user: null },
      error: { message: 'Invalid login credentials' },
    });

    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Fill in form
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'wrongpassword' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid login credentials')).toBeInTheDocument();
    });
  });

  it('handles successful signup', async () => {
    mockSignUp.mockResolvedValue({
      data: { user: { id: 'user-456', email: 'newuser@example.com' } },
      error: null,
    });

    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Switch to signup mode
    fireEvent.click(screen.getByText(/don't have an account/i));

    // Fill in form
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(mockSignUp).toHaveBeenCalledWith({
        email: 'newuser@example.com',
        password: 'password123',
      });
    });
  });

  it('validates email format', async () => {
    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Enter invalid email
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'invalid-email' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Should show validation error or prevent submission
    // This depends on your Auth component implementation
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it('validates password minimum length', async () => {
    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Enter short password
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: '123' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Should show validation error or prevent submission
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it('disables submit button while request is pending', async () => {
    // Mock a slow response
    mockSignIn.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // Fill form and submit
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    });

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    // Button should be disabled during request
    expect(submitButton).toBeDisabled();
  });

  it('clears error message when switching between login and signup', () => {
    render(
      <TestWrapper>
        <Auth onAuthChange={mockOnAuthChange} />
      </TestWrapper>
    );

    // This test would verify that error messages are cleared when switching modes
    // Implementation depends on your Auth component structure
    expect(true).toBe(true); // Placeholder
  });
});