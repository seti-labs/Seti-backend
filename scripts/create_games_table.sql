-- Migration script to add games table
-- Run this in Supabase SQL Editor or via psql

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER UNIQUE NOT NULL,
    home_team VARCHAR(200) NOT NULL,
    away_team VARCHAR(200) NOT NULL,
    league VARCHAR(100) NOT NULL,
    league_id INTEGER,
    kickoff_time TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    home_score INTEGER,
    away_score INTEGER,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    api_data JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_games_fixture_id ON games(fixture_id);
CREATE INDEX IF NOT EXISTS idx_games_kickoff_time ON games(kickoff_time);

-- Enable RLS on games table
ALTER TABLE games ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for public read access
CREATE POLICY "Allow public read access on games" ON games FOR SELECT USING (true);

-- Grant necessary permissions
GRANT SELECT ON games TO authenticated;
GRANT SELECT ON games TO anon;
