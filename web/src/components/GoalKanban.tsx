import { useParams } from 'react-router-dom';
import { Session } from '@supabase/supabase-js';

interface GoalKanbanProps {
  session: Session;
}

export default function GoalKanban({ session: _session }: GoalKanbanProps) {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div className="flex items-center justify-center h-full">
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-6">Kanban for Goal: {id}</h2>
        <p className="text-gray-300">This is a placeholder for the GoalKanban component.</p>
        <p className="text-gray-300 mt-4">
          Future implementation will include a Kanban board view for this specific goal and its sub-tasks.
        </p>
      </div>
    </div>
  );
}