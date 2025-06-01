export interface Goal {
  id: string;
  title: string;
  status: 'todo' | 'doing' | 'done';
  user_id?: string;
  parent_id?: string | null;
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