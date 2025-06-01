import '@testing-library/jest-dom'

// Mock environment variables for tests
Object.defineProperty(window, 'import.meta', {
  value: {
    env: {
      VITE_SUPABASE_URL: 'http://localhost:54321',
      VITE_SUPABASE_ANON_KEY: 'test-key',
      VITE_API_URL: 'http://localhost:8000',
    },
  },
})