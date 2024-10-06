CREATE TABLE IF NOT EXISTS scraped_data (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    price TEXT,
    specifications JSONB,
    additional_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS user_data (
    user_id VARCHAR PRIMARY KEY,
    user_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    prdcer_dataset JSONB,
    prdcer_lyrs JSONB,
    prdcer_ctlgs JSONB,
    draft_ctlgs JSONB
);