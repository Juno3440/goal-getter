import { useState, useEffect, useMemo, useCallback } from 'react';
import { Session } from '@supabase/supabase-js';
import { Tree } from '@visx/hierarchy';
import { hierarchy } from 'd3-hierarchy';
import { motion } from 'framer-motion';
import { TreeNode, TreeResponse, HierarchyNode } from '../types';
import NodeCard from './NodeCard';

// Dead-man switch wrapper to sanitize data and prevent crashes
function deepCloneAndSanitize(node: TreeNode): TreeNode {
  // Deep copy so we never mutate the original
  const copy: TreeNode = JSON.parse(JSON.stringify(node));

  const stack = [copy];
  const offenders: string[] = [];

  while (stack.length) {
    const n = stack.pop();
    if (n && !Array.isArray(n.children)) {
      offenders.push(n.id ?? '[no-id]');
      n.children = [];              // Force-fix so layout never crashes
    }
    if (n?.children) {
      stack.push(...n.children);
    }
  }

  if (offenders.length) {
    console.error('⚠️ Nodes missing children array → fixed on the fly:', offenders);
  }
  return copy;
}


// Node dimensions
const NODE_WIDTH = 200;
const NODE_HEIGHT = 120;

interface GoalTreeProps {
  onUpdate?: () => void;
  session: Session;
}

// Using the HierarchyNode interface from types.ts

export default function GoalTree({ onUpdate: _onUpdate, session }: GoalTreeProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [treeData, setTreeData] = useState<TreeResponse | null>(null);
  const [hierarchyData, setHierarchyData] = useState<HierarchyNode | null>(null);
  const [containerRef, setContainerRef] = useState<HTMLDivElement | null>(null);
  
  // Use clientWidth/Height directly from the ref instead of state
  const containerWidth = containerRef?.clientWidth || 1000;
  const containerHeight = containerRef?.clientHeight || 600;

  // Fetch tree data from API
  const fetchTreeData = useCallback(async () => {
    console.log('Beginning fetchTreeData');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    setLoading(true);
    setError(null);
    
    try {
      console.log('Fetching data from API...');
      const response = await fetch(`${apiUrl}/api/tree`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch tree data');
      }
      
      const data = await response.json();
      console.log('Received data:', data);
      setTreeData(data);
    } catch (err) {
      console.error('Error fetching tree data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
      console.log('Finished fetchTreeData');
    }
  }, [session.access_token]);

  // Build hierarchy from flat nodes array
  const buildHierarchy = (nodes: TreeNode[], rootId: string | null): HierarchyNode | null => {
    if (!nodes.length) return null;
    
    // Find the root node (either specified by rootId or first one without parent)
    const rootNode = rootId 
      ? nodes.find(n => n.id === rootId) 
      : nodes.find(n => n.parent_id === null);
    
    if (!rootNode) return null;
    
    // Recursive function to build the tree
    const buildNode = (node: TreeNode): HierarchyNode => {
      // Get children for this node - ONLY find immediate children
      // IMPORTANT: Don't filter by collapsed state here - we must preserve structure
      // The UI will handle showing/hiding based on collapsed state
      const kids = nodes
        .filter(n => n.parent_id === node.id) 
        .map(childNode => buildNode(childNode));
      
      // CRITICAL FIX: Always return an array for children, guaranteeing consistency
      return {
        ...node,
        children: kids // ALWAYS an array (even if empty)
      };
    };
    
    const result = buildNode(rootNode);
    return result;
  };

  // Toggle collapse state for a node
  const handleToggleCollapse = (id: string) => {
    if (!treeData) return;
    
    console.log('Toggling collapse for node:', id);
    
    const updatedNodes = treeData.nodes.map(node => {
      if (node.id === id) {
        console.log(`Node ${id} collapse state changing to:`, !node.ui.collapsed);
        return {
          ...node,
          ui: {
            ...node.ui,
            collapsed: !node.ui.collapsed
          }
        };
      }
      return node;
    });
    
    setTreeData({
      ...treeData,
      nodes: updatedNodes
    });
  };

  // Initial fetch of tree data
  useEffect(() => {
    console.log('Session effect triggered, fetching tree data');
    fetchTreeData();
  }, [fetchTreeData]);
  
  // Update hierarchy data when tree data changes
  useEffect(() => {
    console.log('Tree data changed effect triggered');
    if (treeData) {
      console.log('Building hierarchy from tree data with nodes:', treeData.nodes.length);
      const hierarchyRoot = buildHierarchy(treeData.nodes, treeData.root_id);
      console.log('Setting hierarchy data:', hierarchyRoot);
      
      // Log type of hierarchyRoot to help debug
      if (hierarchyRoot) {
        console.log('hierarchyRoot children type:', 
          Array.isArray(hierarchyRoot.children) ? 'array' : typeof hierarchyRoot.children,
          'length:', hierarchyRoot.children ? hierarchyRoot.children.length : 'N/A'
        );
      }
      
      setHierarchyData(hierarchyRoot);
    }
  }, [treeData]);

  // Update dimensions on window resize
  useEffect(() => {
    console.log('Window resize effect setup');
    const handleResize = () => {
      // Force a re-render without changing state
      if (containerRef) {
        console.log('Window resized, forcing re-render');
        containerRef.style.height = `${containerRef.clientHeight - 1}px`;
        setTimeout(() => {
          if (containerRef) {
            containerRef.style.height = '100%';
          }
        }, 0);
      }
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [containerRef]);

  // Define margins for layout
  const margin = { top: 50, left: 50, right: 20, bottom: 20 };
  
  // Use memoization to prevent unnecessary layout calculations
  const treeLayout = useMemo(() => {
    if (!hierarchyData) {
      console.log('No hierarchy data available for layout');
      return null;
    }
    
    console.log('Creating memoized layout...');
    try {
      // Apply the dead-man switch to guarantee sanitized data
      const safeData = deepCloneAndSanitize(hierarchyData);
      
      // Using a simple accessor now that we've sanitized the data
      const root = hierarchy(safeData, d => d.children);
      console.log('Hierarchy created successfully');
      
      // Adjust size to account for margins
      const treeLayout = Tree<HierarchyNode>()
        .size([
          containerHeight - margin.top - margin.bottom,
          containerWidth - margin.left - margin.right
        ]);
      
      const computed = treeLayout(root);
      console.log('Layout computed successfully with nodes:', computed.descendants().length);
      return computed;
    } catch (err) {
      console.error('Error creating layout:', err);
      return null;
    }
  }, [hierarchyData, containerWidth, containerHeight, margin.top, margin.bottom, margin.left, margin.right]);

  if (loading) {
    return <div className="flex items-center justify-center h-full">Loading...</div>;
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        Error: {error}
        <button 
          onClick={fetchTreeData}
          className="ml-4 px-3 py-1 bg-gray-800 rounded hover:bg-gray-700"
        >
          Retry
        </button>
      </div>
    );
  }
  
  if (!hierarchyData || !treeLayout) {
    return (
      <div className="flex items-center justify-center h-full">
        No goals found. Create your first goal to get started!
      </div>
    );
  }

  console.log('Rendering tree with dimensions:', containerWidth, 'x', containerHeight);
  
  // Additional guard for treeLayout
  if (!treeLayout) {
    console.log('treeLayout is null at render time');
    return (
      <div className="flex items-center justify-center h-full">
        Preparing layout...
      </div>
    );
  }
  
  // Make sure we have access to links and descendants
  let links = [];
  let descendants = [];
  
  try {
    links = treeLayout.links();
    descendants = treeLayout.descendants();
    console.log(`Render has ${links.length} links and ${descendants.length} nodes`);
  } catch (err) {
    console.error('Error accessing layout data:', err);
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        Error rendering tree visualization
      </div>
    );
  }
  
  return (
    <div 
      id="goal-tree-container" 
      className="w-full h-full"
      ref={setContainerRef}
    >
      <svg width={containerWidth} height={containerHeight}>
        {/* Using a group element with transform to create margin space */}
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {/* Links */}
          {links.map((link: any, i: number) => (
            <motion.line 
              key={`link-${i}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              x1={link.source.y} // Swapped x and y for vertical layout
              y1={link.source.x}
              x2={link.target.y}
              y2={link.target.x}
              stroke="#374151"
              strokeWidth={2}
            />
          ))}
          
          {/* Nodes */}
          {descendants.map((node: any) => (
            <foreignObject
              key={`node-${node.data.id}`}
              x={node.y - NODE_WIDTH/2} // Swapped x and y for vertical layout
              y={node.x - NODE_HEIGHT/2}
              width={NODE_WIDTH}
              height={NODE_HEIGHT}
            >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              style={{ width: '100%', height: '100%' }}
            >
              <NodeCard 
                node={node.data} 
                onToggleCollapse={handleToggleCollapse}
              />
            </motion.div>
          </foreignObject>
        ))}
        </g>
      </svg>
    </div>
  );
}