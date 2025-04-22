import { useEffect, useRef, useState } from 'react';
import { Session } from '@supabase/supabase-js';
import * as d3 from 'd3';
import { Goal } from '../types';

interface GoalTreeProps {
  data: Goal[];
  onUpdate: () => void;
  session: Session;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function GoalTree({ data, onUpdate, session }: GoalTreeProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 30, right: 30, bottom: 30, left: 50 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const height = svgRef.current.clientHeight - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create a hierarchy from the root data
    const root = d3.hierarchy({ children: data });

    // Generate tree layout
    const treeLayout = d3.tree().size([height, width]);
    treeLayout(root);

    // Add links between nodes
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkHorizontal()
        .x(d => d.y)
        .y(d => d.x)
      );

    // Create node groups
    const nodes = g.selectAll('.node')
      .data(root.descendants().slice(1)) // Skip the artificial root
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .attr('data-id', d => d.data.id)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        setSelectedGoal(d.data);
      });

    // Add circles for nodes
    nodes.append('circle')
      .attr('r', 8)
      .attr('class', d => `node-${d.data.status}`);

    // Add labels to nodes
    nodes.append('text')
      .attr('dy', '.31em')
      .attr('x', d => d.children ? -12 : 12)
      .attr('text-anchor', d => d.children ? 'end' : 'start')
      .text(d => d.data.title)
      .style('fill', 'white');

  }, [data]);

  const updateGoalStatus = async (goalId: string, newStatus: string) => {
    try {
      await fetch(`${API_URL}/goals/${goalId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      onUpdate(); // Refresh the goal tree
      setSelectedGoal(null);
    } catch (error) {
      console.error('Failed to update goal status:', error);
    }
  };

  const deleteGoal = async (goalId: string) => {
    if (confirm('Are you sure you want to delete this goal?')) {
      try {
        await fetch(`${API_URL}/goals/${goalId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        });
        onUpdate(); // Refresh the goal tree
        setSelectedGoal(null);
      } catch (error) {
        console.error('Failed to delete goal:', error);
      }
    }
  };

  return (
    <div className="relative w-full h-full">
      <svg ref={svgRef} className="w-full h-full"></svg>
      
      {selectedGoal && (
        <div className="absolute top-4 right-4 bg-gray-800 p-4 rounded-lg shadow-lg w-64">
          <h3 className="text-lg font-bold mb-2">{selectedGoal.title}</h3>
          <div className="mb-4">
            <p className="text-sm">Status: {selectedGoal.status}</p>
          </div>
          <div className="flex flex-col space-y-2">
            <h4 className="text-sm font-bold">Change Status:</h4>
            <div className="flex space-x-2">
              <button 
                className="px-3 py-1 bg-gray-600 rounded hover:bg-gray-500 text-xs"
                onClick={() => updateGoalStatus(selectedGoal.id, 'todo')}
              >
                Todo
              </button>
              <button 
                className="px-3 py-1 bg-blue-600 rounded hover:bg-blue-500 text-xs"
                onClick={() => updateGoalStatus(selectedGoal.id, 'doing')}
              >
                Doing
              </button>
              <button 
                className="px-3 py-1 bg-green-600 rounded hover:bg-green-500 text-xs"
                onClick={() => updateGoalStatus(selectedGoal.id, 'done')}
              >
                Done
              </button>
            </div>
            <button 
              className="px-3 py-1 bg-red-600 rounded hover:bg-red-500 mt-4 text-xs"
              onClick={() => deleteGoal(selectedGoal.id)}
            >
              Delete Goal
            </button>
          </div>
          <button 
            className="absolute top-2 right-2 text-gray-400 hover:text-white"
            onClick={() => setSelectedGoal(null)}
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}

export default GoalTree;