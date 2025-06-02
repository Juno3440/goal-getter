export interface Goal {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'blocked' | 'done';
  kind: 'outcome' | 'process' | 'habit' | 'milestone';
  priority: number; // 1-5 scale
  impact: number; // 1-5 scale  
  urgency: number; // 1-5 scale
  user_id?: string;
  parent_id?: string | null;
  path?: string; // ltree path
  depth?: number;
  metadata: { [key: string]: any };
  ai_state: { [key: string]: any };
  deadline?: string;
  completed_at?: string;
  created_at?: string;
  updated_at?: string;
  children?: Goal[];
}

export interface TreeNode {
  id: string;
  parent_id: string | null;
  title: string;
  progress: number;
  status: 'pending' | 'active' | 'done' | 'blocked';
  style: {
    color: string;
    accent: string;
  };
  ui: {
    collapsed: boolean;
  };
  children?: TreeNode[];
}

export interface HierarchyNode extends TreeNode {
  children: HierarchyNode[]; // Required, never undefined
}

export interface TreeResponse {
  schema_version: string;
  generated_at: string;
  root_id: string | null;
  nodes: TreeNode[];
}

// Enhanced goal creation interface
export interface GoalCreate {
  title: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'blocked' | 'done';
  kind?: 'outcome' | 'process' | 'habit' | 'milestone';
  priority?: number;
  impact?: number;
  urgency?: number;
  parent_id?: string;
  deadline?: string;
  metadata?: { [key: string]: any };
}

// Enhanced goal update interface
export interface GoalUpdate {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'blocked' | 'done';
  kind?: 'outcome' | 'process' | 'habit' | 'milestone';
  priority?: number;
  impact?: number;
  urgency?: number;
  parent_id?: string;
  deadline?: string;
  completed_at?: string;
  metadata?: { [key: string]: any };
  ai_state?: { [key: string]: any };
}