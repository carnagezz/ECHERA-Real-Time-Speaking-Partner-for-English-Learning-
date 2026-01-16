CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
  "userId" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  "email" text UNIQUE NOT NULL,
  "passwordHash" text NOT NULL,
  "nickname" text NOT NULL,
  "selectedVoice" text NOT NULL DEFAULT 'default',
  "createdAt" timestamptz NOT NULL DEFAULT NOW()
);

CREATE TABLE sessions (
  "sessionId" uuid PRIMARY KEY,
  "userId" uuid NOT NULL REFERENCES users("userId") ON DELETE CASCADE,
  "createdAt" timestamptz NOT NULL DEFAULT NOW(),
  "expiresAt" timestamptz NOT NULL,
  "invalidatedAt" timestamptz NULL
);

CREATE TABLE conversations (
  "conversationId" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  "userId" uuid NOT NULL REFERENCES users("userId") ON DELETE CASCADE,
  "sessionId" uuid NULL REFERENCES sessions("sessionId") ON DELETE SET NULL,
  "title" text NOT NULL DEFAULT 'New conversation',
  "messageCount" int NOT NULL DEFAULT 0,
  "createdAt" timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_created ON conversations("userId", "createdAt" DESC);

CREATE TABLE messages (
  "messageId" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  "conversationId" uuid NOT NULL REFERENCES conversations("conversationId") ON DELETE CASCADE,
  "content" text NOT NULL,
  "senderId" text NOT NULL CHECK ("senderId" IN ('user','ai')),
  "timestamp" timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conv_time ON messages("conversationId", "timestamp" ASC);

CREATE TABLE feedback (
  "feedbackId" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  "messageId" uuid UNIQUE NOT NULL REFERENCES messages("messageId") ON DELETE CASCADE,
  "fluencyScore" int NOT NULL DEFAULT 0,
  "wordChoiceScore" int NOT NULL DEFAULT 0,
  "grammarScore" int NOT NULL DEFAULT 0,
  "feedbackTips" text[] NOT NULL DEFAULT ARRAY[]::text[]
);