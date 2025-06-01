import { ReactNode } from 'react';
import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

// Mock React Router
vi.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Route: ({ element }: { element: ReactNode }) => <div>{element}</div>,
}))

// Mock Supabase
vi.mock('../supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } }),
    },
  },
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(document.body).toBeInTheDocument()
  })
})