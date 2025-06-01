import React, { useState, useEffect } from 'react';
import { Auth as SupabaseAuth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { Session } from '@supabase/supabase-js';
import { supabase } from '../supabase';

interface AuthProps {
  onAuthChange: (session: Session | null) => void;
}

export default function Auth({ onAuthChange }: AuthProps) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      onAuthChange(session);
      setLoading(false);
      
      // Set up auth listener
      const { data: { subscription } } = await supabase.auth.onAuthStateChange(
        (_event, session) => {
          onAuthChange(session);
        }
      );
      
      return () => subscription.unsubscribe();
    };
    
    getSession();
  }, [onAuthChange]);

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <div className="max-w-md mx-auto p-4 mt-16">
      <h1 className="text-2xl font-bold mb-4 text-center">GPT GoalGraph</h1>
      <div className="bg-gray-800 p-8 rounded-lg shadow-md">
        <SupabaseAuth 
          supabaseClient={supabase}
          appearance={{
            theme: ThemeSupa,
            variables: {
              default: {
                colors: {
                  brand: '#3B82F6',
                  brandAccent: '#2563EB',
                  inputBackground: '#1F2937',
                  inputText: 'white',
                  inputPlaceholder: '#9CA3AF',
                }
              }
            }
          }}
          providers={['google', 'github']}
          theme="dark"
        />
      </div>
    </div>
  );
}