-- Seed data for AlloyDB AI Query Agent demo
-- Custom dataset: AI tools and platforms
-- Run this script once against your AlloyDB / PostgreSQL instance.

-- ================================================================
-- AI Tools Table
-- ================================================================
CREATE TABLE ai_tools (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    popularity_score INT
);

-- ================================================================
-- Insert AI Tools Data
-- ================================================================
INSERT INTO ai_tools (name, category, description, popularity_score) VALUES
('LangChain', 'LLM Framework', 'Framework for building LLM-powered apps', 95),
('FastAPI', 'Backend', 'High-performance Python web framework', 90),
('Pinecone', 'Vector DB', 'Vector database for similarity search', 88),
('Weaviate', 'Vector DB', 'Open-source vector database', 85),
('Hugging Face', 'ML Platform', 'Platform for ML models and datasets', 92),
('OpenAI API', 'LLM API', 'API for GPT models', 98),
('Gemini', 'LLM API', 'Google AI model for multimodal tasks', 96),
('Supabase', 'Backend', 'Open-source Firebase alternative', 87),
('Docker', 'DevOps', 'Containerization platform', 93),
('Kubernetes', 'DevOps', 'Container orchestration system', 91);
