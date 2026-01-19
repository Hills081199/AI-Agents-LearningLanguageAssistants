-- Update study_sessions table to support Activity Logging
-- Add lesson_id to link with lesson_history
ALTER TABLE public.study_sessions
ADD COLUMN IF NOT EXISTS lesson_id UUID REFERENCES public.lesson_history(id);
-- Add activity_type to distinguish between 'quiz', 'writing', etc.
ALTER TABLE public.study_sessions
ADD COLUMN IF NOT EXISTS activity_type VARCHAR(50);
-- Add score fields
ALTER TABLE public.study_sessions
ADD COLUMN IF NOT EXISTS score INTEGER;
ALTER TABLE public.study_sessions
ADD COLUMN IF NOT EXISTS max_score INTEGER;
-- Add data column for storing detailed answers or submissions
ALTER TABLE public.study_sessions
ADD COLUMN IF NOT EXISTS data JSONB;
-- Comment on columns
COMMENT ON COLUMN public.study_sessions.lesson_id IS 'Link to the lesson history record';
COMMENT ON COLUMN public.study_sessions.activity_type IS 'Type of activity: quiz, writing, speaking, etc.';
COMMENT ON COLUMN public.study_sessions.data IS 'Detailed activity data (answers, submission text, etc.)';
-- Policy update (if needed, but existing policies usually allow owner access)
-- Ensure RLS is enabled (should already be)
ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;