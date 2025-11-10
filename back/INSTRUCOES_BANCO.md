# 📋 Instruções - Conexão com PostgreSQL

## ✅ O que foi feito:

1. **Configuração de conexão** (`db_config.py`)
   - Usuário: `postgres`
   - Senha: `VIA2609`
   - Database: `Estoque`
   - Host: `localhost`
   - Port: `5432`

2. **Operações de banco de dados** (`db_operations.py`)
   - Operações CRUD para usuários, funcionários, empresas e produtos

3. **Integração no app.py**
   - Todas as operações agora usam PostgreSQL ao invés de dicionários em memória

## 🔍 Como testar a conexão:

### Opção 1: Executar o servidor (recomendado)
```bash
cd back
python app.py
```

O servidor vai testar a conexão automaticamente ao iniciar e mostrar se foi bem-sucedida.

### Opção 2: Executar script de diagnóstico
```bash
cd back
python check_database.py
```

Este script vai:
- Testar a conexão
- Listar todas as tabelas existentes
- Mostrar a estrutura de cada tabela
- Verificar se as tabelas esperadas existem

## 📊 Tabelas esperadas:

O sistema espera as seguintes tabelas no banco `Estoque`:

### 1. `usuarios` (Chefes/Administradores)
```sql
- cpf (VARCHAR(11), PRIMARY KEY)
- password_hash (VARCHAR(255))
- name (VARCHAR(255))
- email (VARCHAR(255))
- created_at (TIMESTAMP)
```

### 2. `empresas`
```sql
- id (VARCHAR(50), PRIMARY KEY)
- name (VARCHAR(255))
- created_at (TIMESTAMP)
```

### 3. `funcionarios`
```sql
- cpf (VARCHAR(11))
- password_hash (VARCHAR(255))
- company_id (VARCHAR(50))
- name (VARCHAR(255))
- created_at (TIMESTAMP)
- PRIMARY KEY (cpf, company_id)
- FOREIGN KEY (company_id) REFERENCES empresas(id)
```

### 4. `produtos`
```sql
- id (SERIAL, PRIMARY KEY)
- name (VARCHAR(100))
- quantity (INTEGER)
- value (DECIMAL(10,2))
- company_id (VARCHAR(50))
- created_at (TIMESTAMP)
- FOREIGN KEY (company_id) REFERENCES empresas(id)
- UNIQUE(company_id, name)
```

## 🔧 Se as tabelas tiverem nomes diferentes:

Se você criou as tabelas com nomes diferentes, você precisa ajustar o arquivo `db_operations.py`:

1. Abra `back/db_operations.py`
2. Procure pelas queries SQL (ex: `SELECT ... FROM usuarios`)
3. Substitua os nomes das tabelas/colunas pelos nomes corretos do seu banco

## 🚨 Possíveis problemas:

### Erro: "relation does not exist"
- **Causa**: Tabela não existe ou nome está errado
- **Solução**: Verifique os nomes das tabelas no banco e ajuste `db_operations.py`

### Erro: "column does not exist"
- **Causa**: Coluna não existe ou nome está errado
- **Solução**: Verifique os nomes das colunas e ajuste `db_operations.py`

### Erro: "connection refused"
- **Causa**: PostgreSQL não está rodando
- **Solução**: Inicie o serviço PostgreSQL

### Erro: "authentication failed"
- **Causa**: Usuário ou senha incorretos
- **Solução**: Verifique as credenciais em `db_config.py`

### Erro: "database does not exist"
- **Causa**: Banco de dados 'Estoque' não existe
- **Solução**: Crie o banco de dados:
  ```sql
  CREATE DATABASE "Estoque";
  ```

## 📝 Próximos passos:

1. Execute `python check_database.py` para verificar as tabelas
2. Se necessário, ajuste os nomes das tabelas/colunas em `db_operations.py`
3. Execute `python app.py` para iniciar o servidor
4. Teste os endpoints da API

## 💡 Dica:

Se você não tem certeza dos nomes das tabelas, execute o script `check_database.py` que vai listar todas as tabelas e suas estruturas!


