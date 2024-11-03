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

CREATE TABLE IF NOT EXISTS Product (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL UNIQUE
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
    product_id VARCHAR(255) NOT NULL REFERENCES Product(product_id) ON DELETE CASCADE -- ID of the product
);


CREATE TABLE IF NOT EXISTS stripe_subscriptions (
    subscription_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS logs (
    log_id SERIAL PRIMARY KEY, -- Unique identifier for the log
    user_id VARCHAR(255) NOT NULL, -- ID of the user
    action VARCHAR(255) NOT NULL, -- Action performed by the user (e.g., login, logout)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp when the log was created
);


-- Stripe customers
CREATE TABLE IF NOT EXISTS stripe_customers (
    id SERIAL PRIMARY KEY, -- Primary key of table
    customer_id VARCHAR(255) NOT NULL UNIQUE, -- Stripe customer ID
    user_id VARCHAR(255) UNIQUE NOT NULL UNIQUE  -- Reference to the user ID in your system
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
