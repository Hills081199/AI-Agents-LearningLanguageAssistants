-- Create Topics table
create table if not exists public.topics (
    id uuid default gen_random_uuid() primary key,
    name text not null,
    level text not null,
    language text not null default 'chinese',
    created_at timestamptz default now() not null,
    unique(name, level, language)
);
-- Enable RLS for Topics
alter table public.topics enable row level security;
-- Allow read access to all authenticated users
create policy "Users can view all topics" on public.topics for
select using (auth.role() = 'authenticated');
-- Allow insert access (for seeding/admin) - simplified for now
create policy "Authenticated users can insert topics" on public.topics for
insert with check (auth.role() = 'authenticated');