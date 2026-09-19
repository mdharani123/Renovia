-- Kabadiwala Connect Schema Definition
-- PostgreSQL Database Initialization Script

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Role Enum
CREATE TYPE user_role AS ENUM ('collector', 'recycler', 'admin');

-- Item Status Enum
CREATE TYPE scrap_status AS ENUM ('pending', 'matched', 'offer_accepted', 'collected', 'recycled', 'cancelled');

-- Offer Status Enum
CREATE TYPE offer_status AS ENUM ('pending', 'accepted', 'rejected', 'expired');

-- Pickup & Recycling Status Enum
CREATE TYPE pickup_status AS ENUM ('scheduled', 'in_transit', 'completed', 'failed');
CREATE TYPE recycling_status AS ENUM ('pending', 'processing', 'completed');

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Collectors Table
CREATE TABLE collectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    verification_status BOOLEAN DEFAULT TRUE
);

-- 3. Recyclers Table
CREATE TABLE recyclers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(150) NOT NULL,
    license_number VARCHAR(100) NOT NULL UNIQUE,
    accepted_materials TEXT[] NOT NULL,
    service_area VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    verification_status BOOLEAN DEFAULT FALSE,
    rating DOUBLE PRECISION DEFAULT 5.0
);

-- 4. Scrap Items Table
CREATE TABLE scrap_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collector_id UUID NOT NULL REFERENCES collectors(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    predicted_category VARCHAR(50),
    quality VARCHAR(50) NOT NULL,
    predicted_quality VARCHAR(50),
    weight DOUBLE PRECISION NOT NULL,
    image_url TEXT,
    description TEXT,
    status scrap_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Offers Table
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scrap_id UUID NOT NULL REFERENCES scrap_items(id) ON DELETE CASCADE,
    recycler_id UUID NOT NULL REFERENCES recyclers(id) ON DELETE CASCADE,
    offered_price DOUBLE PRECISION NOT NULL,
    pickup_available BOOLEAN DEFAULT TRUE,
    estimated_pickup_date TIMESTAMP WITH TIME ZONE,
    status offer_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Transactions Table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scrap_id UUID NOT NULL REFERENCES scrap_items(id) ON DELETE CASCADE,
    collector_id UUID NOT NULL REFERENCES collectors(id) ON DELETE CASCADE,
    recycler_id UUID NOT NULL REFERENCES recyclers(id) ON DELETE CASCADE,
    accepted_price DOUBLE PRECISION NOT NULL,
    pickup_status pickup_status DEFAULT 'scheduled',
    recycling_status recycling_status DEFAULT 'pending',
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 7. Recycling Records Table
CREATE TABLE recycling_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID UNIQUE NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    material_type VARCHAR(50) NOT NULL,
    weight DOUBLE PRECISION NOT NULL,
    recycling_method VARCHAR(100) NOT NULL,
    completion_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    certificate_reference_number VARCHAR(100) UNIQUE NOT NULL
);

-- Indexes for efficient queries
CREATE INDEX idx_scrap_collector ON scrap_items(collector_id);
CREATE INDEX idx_offers_scrap ON offers(scrap_id);
CREATE INDEX idx_offers_recycler ON offers(recycler_id);
CREATE INDEX idx_transactions_collector ON transactions(collector_id);
CREATE INDEX idx_transactions_recycler ON transactions(recycler_id);
