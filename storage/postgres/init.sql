CREATE TABLE IF NOT EXISTS user_data (
    user_id VARCHAR PRIMARY KEY,
    user_name VARCHAR,
    email VARCHAR UNIQUE,
    prdcer_dataset JSONB,
    prdcer_lyrs JSONB,
    prdcer_ctlgs JSONB,
    draft_ctlgs JSONB
);

CREATE TABLE IF NOT EXISTS scraped_data (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    price TEXT,
    specifications JSONB,
    additional_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS SubscriptionModels (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL UNIQUE,
    default_price VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    active BOOLEAN,
    attributes TEXT[], -- PostgreSQL array type
    caption TEXT,
    deactivate_on TEXT[], -- PostgreSQL array type
    description TEXT,
    images TEXT[], -- PostgreSQL array type
    livemode BOOLEAN,
    metadata JSONB NOT NULL DEFAULT '{"seats": 1, "free_trial": true, "free_trial_days": 7, "can_extend_seats": false}', -- JSONB type for metadata
    package_dimensions JSONB, -- Assuming package_dimensions can be a JSON object
    shippable BOOLEAN,
    statement_descriptor VARCHAR(255),
    tax_code VARCHAR(255),
    unit_label VARCHAR(255),
    url TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY, -- Unique identifier for the team
    team_name VARCHAR(255) NOT NULL, -- Name of the team
    owner_id VARCHAR(255) NOT NULL -- ID of the team owner
);

CREATE TABLE IF NOT EXISTS team_members (
    team_member_id SERIAL PRIMARY KEY, -- Unique identifier for the team member relationship
    team_id INTEGER NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE, -- ID of the team
    user_id VARCHAR(255) NOT NULL -- ID of the user
);

CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY, -- Unique identifier for the price
    price_id VARCHAR(255) NOT NULL UNIQUE, -- ID of the price
    product_id VARCHAR(255) NOT NULL REFERENCES SubscriptionModels(product_id) ON DELETE CASCADE, -- ID of the product
    currency VARCHAR(3) NOT NULL, -- Currency code (e.g., USD, EUR)
    tiers JSONB,
    unit_amount INTEGER NOT NULL, -- Amount in the smallest currency unit (e.g., cents)
    recurring_interval VARCHAR(50) NOT NULL, -- Interval for recurring payments (e.g., month, year)
    recurring_interval_count INTEGER NOT NULL, -- Number of intervals between each recurring payment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the price was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the price was last updated,
    pricing_type VARCHAR(10) CHECK (pricing_type IN ('flat', 'tier')) NOT NULL,
    base_amount INT,
    included_seats INT,
    additional_seat_price INT
);


CREATE TABLE IF NOT EXISTS stripe_subscriptions (
    subscription_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    seats INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS logs (
    log_id SERIAL PRIMARY KEY, -- Unique identifier for the log
    user_id VARCHAR(255) NOT NULL, -- ID of the user
    action VARCHAR(255) NOT NULL, -- Action performed by the user (e.g., login, logout)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp when the log was created
);

-- wallet table for storing user wallet information
CREATE TABLE IF NOT EXISTS wallet (
    wallet_id SERIAL PRIMARY KEY, -- Unique identifier for the wallet
    user_id VARCHAR(255) NOT NULL, -- ID of the user associated with the wallet
    balance INTEGER NOT NULL, -- Current balance in the wallet
    currency VARCHAR(3) NOT NULL DEFAULT 'USD', -- Currency code (e.g., USD, EUR)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the wallet was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp when the wallet was last updated
);

-- Stripe customers
CREATE TABLE IF NOT EXISTS stripe_customers (
    id SERIAL PRIMARY KEY, -- Primary key of table
    customer_id VARCHAR(255) NOT NULL, -- Stripe customer ID
    user_id VARCHAR(255) UNIQUE NOT NULL -- Reference to the user ID in your system
);


CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY, -- Unique identifier for the transaction
    user_id VARCHAR(255) NOT NULL, -- ID of the user
    subscription_id VARCHAR(255) NOT NULL REFERENCES stripe_subscriptions(subscription_id) ON DELETE CASCADE, -- ID of the subscription
    amount INTEGER NOT NULL, -- Amount of the transaction in the smallest currency unit (e.g., cents)
    currency VARCHAR(3) NOT NULL, -- Currency code (e.g., USD, EUR)
    payment_method VARCHAR(50) NOT NULL, -- Payment method used for the transaction (e.g., credit card, PayPal)
    status VARCHAR(50) NOT NULL, -- Status of the transaction (e.g., succeeded, failed)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the transaction was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp when the transaction was last updated
);


CREATE TABLE IF NOT EXISTS stripe_payment_methods (
    payment_method_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    billing_details JSONB NOT NULL
);


CREATE OR REPLACE FUNCTION get_user_wallet(p_user_id VARCHAR(255))
RETURNS TABLE (
    wallet_id INTEGER,
    user_id VARCHAR(255),
    balance INTEGER,
    currency VARCHAR(3),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT w.wallet_id, w.user_id, w.balance, w.currency, w.created_at, w.updated_at
    FROM wallet w
    WHERE w.user_id = (
        SELECT COALESCE(
            (SELECT t.owner_id
             FROM teams t
             JOIN team_members tm ON t.team_id = tm.team_id
             WHERE tm.user_id = p_user_id),
            p_user_id
        )
    );
END;
$$ LANGUAGE plpgsql;
