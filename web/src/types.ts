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