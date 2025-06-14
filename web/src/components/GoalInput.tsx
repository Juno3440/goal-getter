import React, { useState } from 'react';
import { Session } from '@supabase/supabase-js';
import { GoalCreate } from '../types';

interface GoalInputProps {
  session: Session;
  onGoalCreated?: () => void;
}

export default function GoalInput({ session, onGoalCreated }: GoalInputProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(3);
  const [impact, setImpact] = useState(3);
  const [urgency, setUrgency] = useState(3);
  const [kind, setKind] = useState<'outcome' | 'process' | 'habit' | 'milestone'>('outcome');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

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
      
      const goalData: GoalCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
        kind,
        priority,
        impact,
        urgency,
        status: 'todo',
        metadata: {}
      };

      const response = await fetch(`${apiUrl}/goals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(goalData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create goal');
      }

      const newGoal = await response.json();
      console.log('Goal created:', newGoal);
      
      // Clear the inputs
      setTitle('');
      setDescription('');
      setPriority(3);
      setImpact(3);
      setUrgency(3);
      setKind('outcome');
      setShowAdvanced(false);
      
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
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-3 items-start">
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
          </div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="retro-button-secondary"
          >
            {showAdvanced ? 'SIMPLE' : 'ADVANCED'}
          </button>
          <button
            type="submit"
            disabled={isLoading || !title.trim()}
            className="retro-button"
          >
            {isLoading ? 'ADDING...' : 'ADD'}
          </button>
        </div>

        {showAdvanced && (
          <div className="retro-panel p-4 space-y-4">
            <div>
              <label className="block text-sm retro-text mb-2">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Goal description (optional)..."
                className="retro-input w-full h-20 resize-none"
                disabled={isLoading}
                maxLength={500}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm retro-text mb-2">Kind</label>
                <select
                  value={kind}
                  onChange={(e) => setKind(e.target.value as any)}
                  className="retro-input w-full"
                  disabled={isLoading}
                >
                  <option value="outcome">Outcome</option>
                  <option value="process">Process</option>
                  <option value="habit">Habit</option>
                  <option value="milestone">Milestone</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm retro-text mb-2">Priority (1-5)</label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={priority}
                  onChange={(e) => setPriority(parseInt(e.target.value))}
                  className="retro-slider w-full"
                  disabled={isLoading}
                />
                <div className="text-center retro-text text-sm mt-1">{priority}</div>
              </div>
              
              <div>
                <label className="block text-sm retro-text mb-2">Impact (1-5)</label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={impact}
                  onChange={(e) => setImpact(parseInt(e.target.value))}
                  className="retro-slider w-full"
                  disabled={isLoading}
                />
                <div className="text-center retro-text text-sm mt-1">{impact}</div>
              </div>
              
              <div>
                <label className="block text-sm retro-text mb-2">Urgency (1-5)</label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={urgency}
                  onChange={(e) => setUrgency(parseInt(e.target.value))}
                  className="retro-slider w-full"
                  disabled={isLoading}
                />
                <div className="text-center retro-text text-sm mt-1">{urgency}</div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="retro-error">
            {error}
          </div>
        )}
      </form>
    </div>
  );
}