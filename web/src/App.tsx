import { useState, ReactNode } from 'react';
import { Session } from '@supabase/supabase-js';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GoalTree from './components/GoalTree';
import GoalKanban from './components/GoalKanban';
import Auth from './components/Auth';
import { supabase } from './supabase';

function App() {
  const [session, setSession] = useState<Session | null>(null);

  const handleAuthChange = (newSession: Session | null) => {
    setSession(newSession);
  };

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
        <header className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">GPT GoalGraph</h1>
          <div className="flex items-center space-x-4">
            <span>{session.user.email}</span>
            <button 
              onClick={() => supabase.auth.signOut()}
              className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 transition-colors"
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
                  <GoalTree session={session} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/goal/:id" 
              element={
                <ProtectedRoute>
                  <GoalKanban session={session} />
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