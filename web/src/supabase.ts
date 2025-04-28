import { createClient } from '@supabase/supabase-js';

// Vite env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// 🔍  Make life easier when you’re debugging in the browser console
if (import.meta.env.DEV) {
  // @ts-ignore
  window.supabase = supabase;              // now run  window.supabase.auth.getSession()
}