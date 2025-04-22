-- enable UUID generation
create extension if not exists "uuid-ossp";

create table public.goals (
  id         uuid        primary key default uuid_generate_v4(),
  user_id    uuid        not null references auth.users(id),
  title      text        not null,
  status     text        not null default 'todo',
  parent_id  uuid        null references public.goals(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- RLS
alter table public.goals enable row level security;
create policy user_can_read on public.goals
  for select using (auth.uid() = user_id);
create policy user_can_write on public.goals
  for insert, update, delete using (auth.uid() = user_id);