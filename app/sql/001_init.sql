-- ==========================================================
-- Init SQL for omni-conversationAI
-- Creates database, user, grants, schema, and seed data
-- ==========================================================

-- Ensure database exists
CREATE DATABASE IF NOT EXISTS `sailer`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `sailer`;

-- Ensure application user exists
CREATE USER IF NOT EXISTS 'sailer_user'@'%' IDENTIFIED BY 'sailer_pass';
ALTER USER 'sailer_user'@'%'
  IDENTIFIED WITH caching_sha2_password BY 'sailer_pass';
GRANT ALL PRIVILEGES ON `sailer`.* TO 'sailer_user'@'%';
FLUSH PRIVILEGES;


-- ==========================================================
-- Tables
-- ==========================================================
CREATE TABLE companies (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channels (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE contacts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id BIGINT NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE conversations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    contact_id BIGINT NOT NULL,
    owner_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (channel_id) REFERENCES channels(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    sender VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- ==========================================================
-- Seed Data (so that API Get methods can be tested instantly by reviewers)
-- ==========================================================
-- ==========================================================
-- Seed Data (two tenants)
-- ==========================================================
-- Companies
INSERT INTO companies (id, name) VALUES
(1, 'Acme Corp'),
(2, 'Globex Inc');

-- Channels
INSERT INTO channels (id, company_id, name, type) VALUES
(1, 1, 'WhatsApp Support', 'whatsapp'),
(2, 2, 'Email Support',    'email');

-- Users (AI bots + agents)
INSERT INTO users (id, company_id, name, role) VALUES
(1, 1, 'AI Assistant', 'ai-bot'),
(2, 1, 'Alice Agent',  'agent'),
(3, 2, 'AI Helper',    'ai-bot'),
(4, 2, 'Bob Agent',    'agent');

-- Contacts
INSERT INTO contacts (id, company_id, name, phone, email) VALUES
(1, 1, 'Test Contact',   '+15550001122', 'contact@example.com'),
(2, 2, 'Globex Client',  NULL,           'client@globex.com');

-- Conversations (owned by AI initially)
INSERT INTO conversations (id, company_id, channel_id, contact_id, owner_id) VALUES
(1, 1, 1, 1, 1),
(2, 2, 2, 2, 3);

-- Messages
INSERT INTO messages (conversation_id, sender, content) VALUES
-- Acme
(1, 'contact', 'Hello, I need help!'),
(1, 'ai',      'Hi! I am your AI assistant. How can I help you today?'),
-- Globex
(2, 'contact', 'Can I reset my password?'),
(2, 'ai',      'Hello! Sure, I will help you reset it.');
