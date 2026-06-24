# Mobile app (Flutter/Node) PostgreSQL tables — aligned with db_solar_app/backend/database/*.sql
from django.db import migrations


MOBILE_APP_SCHEMA_SQL = r"""
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- user_app (app registrations)
ALTER TABLE user_app ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE user_app ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE user_app ALTER COLUMN role SET DEFAULT 'customer';
CREATE UNIQUE INDEX IF NOT EXISTS user_app_email_key ON user_app (email);
CREATE INDEX IF NOT EXISTS idx_user_app_email ON user_app (email);

-- app_auth_links (links app user to consumer auth_user)
CREATE UNIQUE INDEX IF NOT EXISTS app_auth_links_app_user_auth_user_uniq
    ON app_auth_links (app_user_id, auth_user_id);
CREATE INDEX IF NOT EXISTS app_auth_links_app_user_id_idx ON app_auth_links (app_user_id);

-- leads_lead (Get Quote from mobile app)
CREATE TABLE IF NOT EXISTS leads_lead (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    property_type TEXT,
    roof_type TEXT,
    electricity_bill TEXT,
    monthly_consumption TEXT,
    sorting_address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    email TEXT,
    contact TEXT,
    phone TEXT,
    address TEXT,
    stage TEXT NOT NULL DEFAULT 'new_app',
    status TEXT,
    payment_mode TEXT,
    user_app_id BIGINT,
    assigned_to_id INTEGER,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    source TEXT,
    campaign TEXT,
    score INTEGER DEFAULT 0,
    tags TEXT DEFAULT '[]',
    extra JSONB DEFAULT '{}'::jsonb,
    probability INTEGER NOT NULL DEFAULT 0,
    next_followup TIMESTAMP WITH TIME ZONE,
    rooftop_area DOUBLE PRECISION,
    rooftop_area_unit TEXT DEFAULT 'sq_m',
    alternate_phone TEXT,
    notes TEXT,
    internal_notes TEXT,
    lost_reason TEXT,
    competitor TEXT,
    budget NUMERIC,
    estimated_value NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_leads_lead_user_app_id ON leads_lead (user_app_id);
CREATE INDEX IF NOT EXISTS idx_leads_lead_stage ON leads_lead (stage);

-- growatt_credentials (Growatt API login per consumer)
CREATE TABLE IF NOT EXISTS growatt_credentials (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    plant_ids JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_growatt_user FOREIGN KEY (user_id)
        REFERENCES auth_user(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_growatt_credentials_user_id ON growatt_credentials(user_id);
ALTER TABLE growatt_credentials ADD COLUMN IF NOT EXISTS plant_ids JSONB DEFAULT '[]'::jsonb;

-- plants (Growatt-linked solar plants)
CREATE TABLE IF NOT EXISTS plants (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    capacity DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    installation_date DATE NOT NULL,
    daily_generation DECIMAL(10, 2),
    monthly_generation DECIMAL(10, 2),
    yearly_generation DECIMAL(10, 2),
    lifetime_generation DECIMAL(10, 2),
    efficiency DECIMAL(5, 2),
    health_metrics JSONB,
    growatt_plant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plants_user FOREIGN KEY (user_id)
        REFERENCES auth_user(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plants_user_id ON plants(user_id);
CREATE INDEX IF NOT EXISTS idx_plants_growatt_id ON plants(growatt_plant_id);
CREATE INDEX IF NOT EXISTS idx_plants_status ON plants(status);
ALTER TABLE plants ADD COLUMN IF NOT EXISTS growatt_plant_id VARCHAR(255);

-- generation_data (daily generation per plant)
CREATE TABLE IF NOT EXISTS generation_data (
    id BIGSERIAL PRIMARY KEY,
    plant_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    generation DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (plant_id, date)
);
CREATE INDEX IF NOT EXISTS idx_generation_data_plant_id ON generation_data(plant_id);
CREATE INDEX IF NOT EXISTS idx_generation_data_date ON generation_data(date);
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'generation_data_plant_id_fkey'
    ) THEN
        ALTER TABLE generation_data
            ADD CONSTRAINT generation_data_plant_id_fkey
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Legacy prototype tables still used by Node API routes
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer',
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS faqs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    expected_load DECIMAL(10, 2),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS support_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0120_mobile_app_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql=MOBILE_APP_SCHEMA_SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
