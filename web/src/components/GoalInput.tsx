import { useState } from 'react';
import { Session } from '@supabase/supabase-js';

interface GoalInputProps {
  session: Session;
  onGoalCreated?: () => void;
}

export default function GoalInput({ session, onGoalCreated }: GoalInputProps) {
  const [title, setTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Goal title is required');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/goals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          title: title.trim()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create goal');
      }

      const newGoal = await response.json();
      console.log('Goal created:', newGoal);
      
      // Clear the input
      setTitle('');
      
      // Notify parent component
      if (onGoalCreated) {
        onGoalCreated();
      }
    } catch (err) {
      console.error('Error creating goal:', err);
      setError(err instanceof Error ? err.message : 'Failed to create goal');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="retro-goal-input mb-6">
      <form onSubmit={handleSubmit} className="flex gap-3 items-start">
        <div className="flex-1">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter goal title..."
            className="retro-input w-full"
            disabled={isLoading}
            maxLength={200}
          />
          {error && (
            <div className="retro-error mt-2">
              {error}
            </div>
          )}
        </div>
        <button
          type="submit"
          disabled={isLoading || !title.trim()}
          className="retro-button"
        >
          {isLoading ? 'ADDING...' : 'ADD'}
        </button>
      </form>
    </div>
  );
}