import { CSSProperties, MouseEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { TreeNode } from '../types';

interface NodeCardProps {
  node: TreeNode;
  onToggleCollapse?: (id: string) => void;
}

export default function NodeCard({ node, onToggleCollapse }: NodeCardProps) {
  const navigate = useNavigate();
  
  // Define CSS variables for styling
  const nodeStyle = {
    '--node-bg': node.style.color,
    '--accent': node.style.accent,
  } as CSSProperties;
  
  // Status badge color
  const statusColor = {
    pending: 'bg-yellow-500',
    active: 'bg-blue-500',
    done: 'bg-green-500',
    blocked: 'bg-red-500'
  };
  
  const handleHeaderClick = () => {
    if (onToggleCollapse) {
      onToggleCollapse(node.id);
    }
  };
  
  const handleCardClick = (e: MouseEvent<HTMLDivElement>) => {
    // If clicking on header, don't navigate
    if ((e.target as HTMLElement).closest('.node-header')) {
      return;
    }
    
    // Navigate to goal detail page
    navigate(`/goal/${node.id}`);
  };
  
  return (
    <div 
      className="node-card rounded-md shadow-lg w-full overflow-hidden"
      style={nodeStyle}
      onClick={handleCardClick}
    >
      <div 
        className="node-header p-2 flex justify-between items-center border-b border-gray-700 cursor-pointer"
        onClick={handleHeaderClick}
      >
        <h3 className="font-semibold text-white truncate">{node.title}</h3>
        <div className={`ml-2 px-2 py-0.5 rounded-full text-xs text-white ${statusColor[node.status]}`}>
          {node.status}
        </div>
      </div>
      
      <div className="p-2">
        <div className="progress-container mb-2">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-300">Progress</span>
            <span className="text-gray-300">{Math.round(node.progress * 100)}%</span>
          </div>
          <progress 
            value={node.progress} 
            max="1" 
            className="w-full h-1.5 rounded overflow-hidden"
          />
        </div>
      </div>
    </div>
  );
}