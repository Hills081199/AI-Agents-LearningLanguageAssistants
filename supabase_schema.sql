-- Create Study Sessions table
create table if not exists public.study_sessions (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users(id) on delete cascade not null,
    topic text not null,
    level text not null,
    language text not null default 'chinese',
    start_time timestamptz default now() not null,
    end_time timestamptz
);
-- Enable RLS for Study Sessions
alter table public.study_sessions enable row level security;
create policy "Users can view their own sessions" on public.study_sessions for
select using (auth.uid() = user_id);
create policy "Users can insert their own sessions" on public.study_sessions for
insert with check (auth.uid() = user_id);
create policy "Users can update their own sessions" on public.study_sessions for
update using (auth.uid() = user_id);
-- Create Lesson History table
create table if not exists public.lesson_history (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users(id) on delete cascade not null,
    session_id uuid references public.study_sessions(id) on delete
    set null,
        topic text not null,
        level text not null,
        language text not null default 'chinese',
        lesson_content jsonb not null,
        quiz_score integer,
        writing_score integer,
        created_at timestamptz default now() not null
);
-- Enable RLS for Lesson History
alter table public.lesson_history enable row level security;
create policy "Users can view their own history" on public.lesson_history for
select using (auth.uid() = user_id);
create policy "Users can insert their own history" on public.lesson_history for
insert with check (auth.uid() = user_id);
create policy "Users can update their own history" on public.lesson_history for
update using (auth.uid() = user_id);
create policy "Users can delete their own history" on public.lesson_history for delete using (auth.uid() = user_id);