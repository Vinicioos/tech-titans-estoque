-- Estrutura esperada das tabelas no banco de dados PostgreSQL
-- Este arquivo é apenas uma referência. As tabelas devem estar criadas no banco "Estoque"

-- Tabela de usuários (chefes)
CREATE TABLE IF NOT EXISTS usuarios (
    cpf VARCHAR(11) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de empresas
CREATE TABLE IF NOT EXISTS empresas (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de funcionários
CREATE TABLE IF NOT EXISTS funcionarios (
    cpf VARCHAR(11) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_id VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cpf, company_id),
    FOREIGN KEY (company_id) REFERENCES empresas(id) ON DELETE CASCADE
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    value DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    company_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES empresas(id) ON DELETE CASCADE,
    UNIQUE(company_id, name)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_funcionarios_company ON funcionarios(company_id);
CREATE INDEX IF NOT EXISTS idx_produtos_company ON produtos(company_id);
CREATE INDEX IF NOT EXISTS idx_produtos_name ON produtos(name);

