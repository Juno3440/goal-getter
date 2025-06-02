import { useState, ReactNode, useCallback } from 'react';
import { Session } from '@supabase/supabase-js';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GoalTree from './components/GoalTree';
import GoalInput from './components/GoalInput';
import Auth from './components/Auth';
import { supabase } from './supabase';

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAuthChange = (newSession: Session | null) => {
    setSession(newSession);
  };

  const handleGoalCreated = useCallback(() => {
    // Trigger refresh of GoalTree by updating key
    setRefreshKey(prev => prev + 1);
  }, []);

  // Auth wrapper component to protect routes
  const ProtectedRoute = ({ children }: { children: ReactNode }) => {
    if (!session) {
      return <Navigate to="/" replace />;
    }
    return <>{children}</>;
  };

  // If not logged in, show auth page
  if (!session) {
    return <Auth onAuthChange={handleAuthChange} />;
  }

  return (
    <Router>
      <div className="flex h-screen flex-col p-4 bg-[#09090B] text-white">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold" style={{ fontFamily: 'Orbitron, monospace', color: 'var(--retro-red)', textShadow: '0 0 10px var(--retro-red)' }}>
            GPT GOALNET
          </h1>
          <div className="flex items-center space-x-4">
            <span style={{ fontFamily: 'Orbitron, monospace' }}>{session.user.email}</span>
            <button 
              onClick={() => supabase.auth.signOut()}
              className="retro-button"
            >
              Sign Out
            </button>
          </div>
        </header>
        
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <div className="space-y-6">
                    <GoalInput session={session} onGoalCreated={handleGoalCreated} />
                    <GoalTree key={refreshKey} session={session} />
                  </div>
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;