-- Supabase Schema for Seti Prediction Markets
-- Run this in Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    address VARCHAR(66) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    total_predictions INTEGER DEFAULT 0,
    total_volume BIGINT DEFAULT 0,
    markets_created INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    loss_count INTEGER DEFAULT 0,
    total_pnl BIGINT DEFAULT 0,
    follower_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]'::jsonb,
    notification_settings JSONB DEFAULT '{}'::jsonb,
    theme_preference VARCHAR(20) DEFAULT 'system',
    first_seen TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE
);

-- Markets table
CREATE TABLE IF NOT EXISTS markets (
    id VARCHAR(66) PRIMARY KEY,
    question VARCHAR(500) NOT NULL,
    description TEXT,
    end_time BIGINT NOT NULL,
    creator VARCHAR(66) NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    winning_outcome INTEGER,
    total_liquidity BIGINT DEFAULT 0,
    outcome_a_shares BIGINT DEFAULT 0,
    outcome_b_shares BIGINT DEFAULT 0,
    volume_24h BIGINT DEFAULT 0,
    created_timestamp BIGINT NOT NULL,
    category VARCHAR(50),
    image_url VARCHAR(500),
    tags JSONB,
    last_updated TIMESTAMP DEFAULT NOW(),
    indexed_at TIMESTAMP DEFAULT NOW(),
    view_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    slug VARCHAR(200) UNIQUE,
    featured BOOLEAN DEFAULT FALSE,
    trending_score FLOAT DEFAULT 0.0
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    user_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    outcome INTEGER NOT NULL CHECK (outcome IN (0, 1)),
    amount BIGINT NOT NULL,
    price BIGINT,
    shares BIGINT,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Liquidity Providers table
CREATE TABLE IF NOT EXISTS liquidity_providers (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    provider_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    amount BIGINT NOT NULL,
    shares_received BIGINT,
    timestamp BIGINT NOT NULL,
    withdrawn BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Liquidity Withdrawals table
CREATE TABLE IF NOT EXISTS liquidity_withdrawals (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    provider_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    amount BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    user_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id INTEGER REFERENCES comments(id),
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    market_id VARCHAR(66) REFERENCES markets(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_address, market_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_address VARCHAR(66) REFERENCES users(address) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    link VARCHAR(500),
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Activity Feed table
CREATE TABLE IF NOT EXISTS activity_feed (
    id SERIAL PRIMARY KEY,
    activity_type VARCHAR(50) NOT NULL,
    user_address VARCHAR(66) REFERENCES users(address),
    market_id VARCHAR(66) REFERENCES markets(id),
    prediction_id INTEGER REFERENCES predictions(id),
    data JSONB,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_markets_category ON markets(category);
CREATE INDEX IF NOT EXISTS idx_markets_resolved ON markets(resolved);
CREATE INDEX IF NOT EXISTS idx_markets_created_timestamp ON markets(created_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_markets_volume ON markets(volume_24h DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_market_id ON predictions(market_id);
CREATE INDEX IF NOT EXISTS idx_predictions_user_address ON predictions(user_address);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_comments_market_id ON comments(market_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_address ON favorites(user_address);
CREATE INDEX IF NOT EXISTS idx_notifications_user_address ON notifications(user_address);
CREATE INDEX IF NOT EXISTS idx_activity_feed_timestamp ON activity_feed(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE markets ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE liquidity_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE liquidity_withdrawals ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_feed ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow public read access for now)
CREATE POLICY "Allow public read access on markets" ON markets FOR SELECT USING (true);
CREATE POLICY "Allow public read access on users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public read access on predictions" ON predictions FOR SELECT USING (true);
CREATE POLICY "Allow public read access on comments" ON comments FOR SELECT USING (true);
CREATE POLICY "Allow public read access on activity_feed" ON activity_feed FOR SELECT USING (true);

-- For write operations, use service role key in backend
-- Users can update their own profile
-- CREATE POLICY "Users can update own profile" ON users FOR UPDATE 
--   USING (auth.uid()::text = address);

