CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criação da tabela 'users'
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_on TIMESTAMP DEFAULT NOW()
);

-- Criação da tabela 'toys'
CREATE TABLE IF NOT EXISTS toys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_on TIMESTAMP DEFAULT NOW()
);

-- Criação da tabela de associação 'user_toy' para a relação muitos-para-muitos
CREATE TABLE IF NOT EXISTS user_toy (
    users_id UUID REFERENCES users(id),
    toys_id UUID REFERENCES toys(id),
    PRIMARY KEY (users_id, toys_id)
);