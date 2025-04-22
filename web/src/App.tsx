import { useEffect, useState } from 'react';
import { Session } from '@supabase/supabase-js';
import GoalTree from './components/GoalTree';
import Auth from './components/Auth';
import { Goal } from './types';
import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [goals, setGoals] = useState<Goal[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAuthChange = (newSession: Session | null) => {
    setSession(newSession);
    if (newSession) {
      fetchGoals(newSession);
    } else {
      setGoals(null);
    }
  };

  const fetchGoals = async (authSession: Session) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/goals`, {
        headers: {
          'Authorization': `Bearer ${authSession.access_token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch goals');
      }
      
      const data = await response.json();
      // Expect the API to return a root goal with children array
      setGoals(data.children || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const refreshGoals = () => {
    if (session) {
      fetchGoals(session);
    }
  };

  if (!session) {
    return <Auth onAuthChange={handleAuthChange} />;
  }

  return (
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
        {loading ? (
          <div className="flex h-full items-center justify-center">Loading...</div>
        ) : error ? (
          <div className="flex h-full items-center justify-center text-red-500">{error}</div>
        ) : goals && goals.length > 0 ? (
          <GoalTree data={goals} onUpdate={refreshGoals} session={session} />
        ) : (
          <div className="flex h-full flex-col items-center justify-center">
            <p className="mb-4">No goals yet. Create your first goal to get started!</p>
            <button
              onClick={async () => {
                try {
                  await fetch(`${API_URL}/goals`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${session.access_token}`
                    },
                    body: JSON.stringify({ title: 'My First Goal' })
                  });
                  refreshGoals();
                } catch (err) {
                  setError('Failed to create goal');
                }
              }}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
            >
              Create First Goal
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;