import { CSSProperties, MouseEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { TreeNode } from '../types';

interface NodeCardProps {
  node: TreeNode;
  onToggleCollapse?: (id: string) => void;
}

export default function NodeCard({ node, onToggleCollapse }: NodeCardProps) {
  const navigate = useNavigate();
  
  // Status badge styling
  const statusClasses = {
    pending: 'retro-status-pending',
    active: 'retro-status-active',
    done: 'retro-status-done',
    blocked: 'retro-status-blocked'
  };
  
  const handleHeaderClick = () => {
    if (onToggleCollapse) {
      onToggleCollapse(node.id);
    }
  };
  
  const handleCardClick = (e: MouseEvent<HTMLDivElement>) => {
    // If clicking on header, don't navigate
    if ((e.target as HTMLElement).closest('.retro-node-header')) {
      return;
    }
    
    // Navigate to goal detail page
    navigate(`/goal/${node.id}`);
  };
  
  return (
    <div 
      className="retro-node-card w-full h-full"
      onClick={handleCardClick}
    >
      <div 
        className="retro-node-header flex justify-between items-center cursor-pointer"
        onClick={handleHeaderClick}
      >
        <h3 className="retro-node-title truncate flex-1">{node.title}</h3>
        <div className={`retro-status-badge ${statusClasses[node.status]} ml-2`}>
          {node.status}
        </div>
      </div>
      
      <div className="retro-progress-container">
        <div className="flex justify-between mb-2">
          <span className="retro-progress-label">Progress</span>
          <span className="retro-progress-label">{Math.round(node.progress * 100)}%</span>
        </div>
        <div className="retro-progress-bar">
          <div 
            className="retro-progress-fill"
            style={{ width: `${node.progress * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}