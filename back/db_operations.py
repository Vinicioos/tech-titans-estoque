from db_config import get_connection, return_connection
import psycopg2
from psycopg2 import sql
import hashlib


def _get_table_columns(table_name):
    """
    Retorna a lista de colunas de uma tabela ou lista vazia se não existir.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
            """,
            (table_name,),
        )
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        return columns
    except psycopg2.Error as e:
        print(f"Erro ao obter colunas da tabela '{table_name}': {e}")
        return []
    finally:
        if conn:
            return_connection(conn)


def _ensure_funcionarios_table():
    """
    Garante a existência de uma tabela 'funcionarios' auxiliar para armazenar vínculos de empresa.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS funcionarios (
                cpf VARCHAR(14) PRIMARY KEY,
                nome VARCHAR(100),
                senha VARCHAR(255),
                id_empresa INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao garantir tabela funcionarios: {e}")
    finally:
        if conn:
            return_connection(conn)


def _detect_column(columns, candidates):
    """
    Retorna o primeiro nome de coluna encontrado em `columns` que esteja na lista `candidates`.
    """
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _get_company_from_funcionarios(cpf):
    """
    Busca o id da empresa na tabela funcionarios para manter compatibilidade com estruturas antigas.
    """
    conn = None
    try:
        _ensure_funcionarios_table()
        columns = _get_table_columns("funcionarios")
        if not columns:
            return None

        cpf_col = _detect_column(columns, ["cpf", "cpf_funcionario", "cpf_colaborador", "cpf_colab"])
        empresa_col = _detect_column(columns, ["id_empresa", "empresa_id", "company_id", "idempresa", "empresa"])

        if not cpf_col or not empresa_col:
            return None

        conn = get_connection()
        cur = conn.cursor()

        query = (
            sql.SQL("SELECT {empresa_col} FROM funcionarios WHERE {cpf_col} = %s OR {cpf_col} = %s LIMIT 1")
            .format(empresa_col=sql.Identifier(empresa_col), cpf_col=sql.Identifier(cpf_col))
        )

        cpf_clean = cpf.replace(".", "").replace("-", "").strip()
        cpf_formatted = (
            f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}" if len(cpf_clean) == 11 else cpf_clean
        )

        cur.execute(query, (cpf_clean, cpf_formatted))
        row = cur.fetchone()
        cur.close()

        if row and row[0] is not None:
            return row[0]
        return None
    except psycopg2.Error as e:
        print(f"Erro ao buscar empresa em funcionarios: {e}")
        return None
    finally:
        if conn:
            return_connection(conn)


def _sync_funcionarios_record(cpf, password_hash, company_id, name=None):
    """
    Garante que a tabela funcionarios (se existir) receba/atualize o vínculo do funcionário com a empresa.
    """
    conn = None
    try:
        _ensure_funcionarios_table()
        columns = _get_table_columns("funcionarios")
        if not columns:
            return

        cpf_clean = cpf.replace('.', '').replace('-', '').strip()
        cpf_col = _detect_column(columns, ["cpf", "cpf_funcionario", "cpf_colaborador", "cpf_colab"])
        empresa_col = _detect_column(columns, ["id_empresa", "empresa_id", "company_id", "idempresa", "empresa"])
        senha_col = _detect_column(columns, ["senha", "password_hash", "hash_senha"])
        nome_col = _detect_column(columns, ["nome", "name"])

        if not cpf_col or not empresa_col:
            return

        try:
            empresa_val = int(company_id)
        except (ValueError, TypeError):
            empresa_val = company_id

        conn = get_connection()
        cur = conn.cursor()

        exists_query = (
            sql.SQL(
                "SELECT 1 FROM funcionarios WHERE {cpf_col} = %s AND {empresa_col} = %s LIMIT 1"
            ).format(cpf_col=sql.Identifier(cpf_col), empresa_col=sql.Identifier(empresa_col))
        )
        cur.execute(exists_query, (cpf_clean, empresa_val))
        exists = cur.fetchone()

        if exists:
            updates = []
            params = []
            if senha_col:
                updates.append(sql.SQL("{col} = %s").format(col=sql.Identifier(senha_col)))
                params.append(password_hash)
            if nome_col and name:
                updates.append(sql.SQL("{col} = %s").format(col=sql.Identifier(nome_col)))
                params.append(name)

            if updates:
                params.extend([cpf_clean, empresa_val])
                update_query = (
                    sql.SQL("UPDATE funcionarios SET {updates} WHERE {cpf_col} = %s AND {empresa_col} = %s")
                    .format(
                        updates=sql.SQL(", ").join(updates),
                        cpf_col=sql.Identifier(cpf_col),
                        empresa_col=sql.Identifier(empresa_col),
                    )
                )
                cur.execute(update_query, params)
        else:
            insert_cols = [sql.Identifier(cpf_col), sql.Identifier(empresa_col)]
            values = [cpf_clean, empresa_val]
            placeholders = [sql.Placeholder(), sql.Placeholder()]

            if senha_col:
                insert_cols.append(sql.Identifier(senha_col))
                values.append(password_hash)
                placeholders.append(sql.Placeholder())

            if nome_col and name:
                insert_cols.append(sql.Identifier(nome_col))
                values.append(name)
                placeholders.append(sql.Placeholder())

            insert_query = (
                sql.SQL("INSERT INTO funcionarios ({cols}) VALUES ({placeholders})")
                .format(cols=sql.SQL(", ").join(insert_cols), placeholders=sql.SQL(", ").join(placeholders))
            )
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao sincronizar funcionarios: {e}")
    finally:
        if conn:
            return_connection(conn)


def _delete_funcionarios_record(cpf, company_id):
    """
    Remove o vínculo do funcionário na tabela funcionarios (se existir).
    """
    conn = None
    try:
        _ensure_funcionarios_table()
        columns = _get_table_columns("funcionarios")
        if not columns:
            return

        cpf_col = _detect_column(columns, ["cpf", "cpf_funcionario", "cpf_colaborador", "cpf_colab"])
        empresa_col = _detect_column(columns, ["id_empresa", "empresa_id", "company_id", "idempresa", "empresa"])

        if not cpf_col or not empresa_col:
            return

        try:
            empresa_val = int(company_id)
        except (ValueError, TypeError):
            empresa_val = company_id

        conn = get_connection()
        cur = conn.cursor()
        delete_query = (
            sql.SQL("DELETE FROM funcionarios WHERE {cpf_col} = %s AND {empresa_col} = %s")
            .format(cpf_col=sql.Identifier(cpf_col), empresa_col=sql.Identifier(empresa_col))
        )
        cur.execute(delete_query, (cpf, empresa_val))
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao remover funcionário da tabela funcionarios: {e}")
    finally:
        if conn:
            return_connection(conn)


def _get_employees_from_funcionarios(company_id):
    """
    Retorna funcionários a partir da tabela funcionarios para cenários legados.
    """
    conn = None
    try:
        _ensure_funcionarios_table()
        columns = _get_table_columns("funcionarios")
        if not columns:
            return []

        id_col = _detect_column(columns, ["id", "id_funcionario", "funcionario_id"])
        cpf_col = _detect_column(columns, ["cpf", "cpf_funcionario", "cpf_colaborador", "cpf_colab"])
        empresa_col = _detect_column(columns, ["id_empresa", "empresa_id", "company_id", "idempresa", "empresa"])
        nome_col = _detect_column(columns, ["nome", "name"])

        if not cpf_col or not empresa_col:
            return []

        try:
            empresa_val = int(company_id)
        except (ValueError, TypeError):
            empresa_val = company_id

        select_parts = []
        order = []

        if id_col:
            select_parts.append(sql.Identifier(id_col))
            order.append("id")

        select_parts.append(sql.Identifier(cpf_col))
        order.append("cpf")

        select_parts.append(sql.Identifier(empresa_col))
        order.append("empresa")

        if nome_col:
            select_parts.append(sql.Identifier(nome_col))
            order.append("nome")

        conn = get_connection()
        cur = conn.cursor()
        query = (
            sql.SQL("SELECT {cols} FROM funcionarios WHERE {empresa_col} = %s")
            .format(cols=sql.SQL(", ").join(select_parts), empresa_col=sql.Identifier(empresa_col))
        )
        cur.execute(query, (empresa_val,))
        rows = cur.fetchall()
        cur.close()

        employees = []
        for row in rows:
            data = {key: row[idx] for idx, key in enumerate(order)}
            employees.append(
                {
                    "id": data.get("id"),
                    "nome": data.get("nome", f"Funcionário {str(data.get('cpf', ''))[:3]}"),
                    "cpf": str(data.get("cpf", "")),
                    "id_empresa": str(data.get("empresa")) if data.get("empresa") is not None else None,
                }
            )
        return employees
    except psycopg2.Error as e:
        print(f"Erro ao buscar funcionários na tabela funcionarios: {e}")
        return []
    finally:
        if conn:
            return_connection(conn)

def hash_password(password):
    """Gera hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== OPERAÇÕES DE USUÁRIOS (CHEFES E FUNCIONÁRIOS) ====================

def get_user_by_cpf(cpf):
    """Busca usuário por CPF (pode ser chefe ou funcionário)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Remover formatação do CPF se houver
        cpf_clean = cpf.replace('.', '').replace('-', '').strip()
        
        # Primeiro, descobrir quais colunas existem na tabela
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'usuario'
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cur.fetchall()]
        
        # Construir SELECT dinamicamente baseado nas colunas que existem
        select_cols = []
        if 'id' in columns:
            select_cols.append('id')
        if 'nome' in columns:
            select_cols.append('nome')
        if 'cpf' in columns:
            select_cols.append('cpf')
        if 'senha' in columns:
            select_cols.append('senha')
        if 'tipo_acesso' in columns:
            select_cols.append('tipo_acesso')
        # Tentar variações do nome da coluna de empresa
        id_empresa_col = None
        for col_name in ['id_empresa', 'empresa_id', 'empresa', 'company_id']:
            if col_name in columns:
                id_empresa_col = col_name
                select_cols.append(col_name)
                break
        
        if not select_cols:
            print("❌ Nenhuma coluna encontrada na tabela usuario")
            cur.close()
            return None
        
        # Construir query
        query = f"SELECT {', '.join(select_cols)} FROM usuario WHERE cpf = %s"
        cur.execute(query, (cpf_clean,))
        result = cur.fetchone()
        
        # Se não encontrou, tentar buscar com LIKE (caso o CPF no banco tenha formatação)
        if not result:
            cpf_formatado = f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
            query_like = f"SELECT {', '.join(select_cols)} FROM usuario WHERE cpf LIKE %s OR cpf = %s"
            cur.execute(query_like, (f"%{cpf_clean}%", cpf_formatado))
            result = cur.fetchone()
        
        cur.close()
        
        if result:
            # Mapear resultados para dicionário
            user_dict = {}
            idx = 0
            if 'id' in select_cols:
                user_dict['id'] = result[idx]
                idx += 1
            if 'nome' in select_cols:
                user_dict['nome'] = result[idx]
                idx += 1
            if 'cpf' in select_cols:
                user_dict['cpf'] = result[idx]
                idx += 1
            if 'senha' in select_cols:
                user_dict['password_hash'] = result[idx]
                idx += 1
            if 'tipo_acesso' in select_cols:
                user_dict['tipo_acesso'] = result[idx] if result[idx] else None
                idx += 1
            if id_empresa_col and id_empresa_col in select_cols:
                user_dict['id_empresa'] = result[idx] if result[idx] else None
            else:
                user_dict['id_empresa'] = None

            if user_dict.get('id_empresa') is None:
                fallback_empresa = _get_company_from_funcionarios(cpf_clean)
                if fallback_empresa is not None:
                    user_dict['id_empresa'] = fallback_empresa
            
            return user_dict
        return None
    except psycopg2.Error as e:
        print(f"Erro ao buscar usuário: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if conn:
            return_connection(conn)

def create_user(cpf, password_hash, name, email=None, tipo_acesso='chefe', id_empresa=None):
    """Cria um novo usuário"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Remover formatação do CPF
        cpf_clean = cpf.replace('.', '').replace('-', '').strip()
        
        # Descobrir quais colunas existem na tabela
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'usuario'
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cur.fetchall()]
        
        # Construir INSERT dinamicamente
        insert_cols = []
        insert_values = []
        
        if 'nome' in columns:
            insert_cols.append('nome')
            insert_values.append(name)
        if 'cpf' in columns:
            insert_cols.append('cpf')
            insert_values.append(cpf_clean)
        if 'senha' in columns:
            insert_cols.append('senha')
            insert_values.append(password_hash)
        
        # Adicionar tipo_acesso se a coluna existir
        if 'tipo_acesso' in columns:
            if not tipo_acesso:
                tipo_acesso = 'chefe'
            insert_cols.append('tipo_acesso')
            insert_values.append(tipo_acesso)
        
        # Adicionar id_empresa se a coluna existir E id_empresa foi fornecido
        id_empresa_col = None
        for col_name in ['id_empresa', 'empresa_id', 'empresa', 'company_id']:
            if col_name in columns:
                id_empresa_col = col_name
                # Só adicionar se id_empresa foi fornecido (não None)
                if id_empresa is not None:
                    insert_cols.append(col_name)
                    insert_values.append(id_empresa)
                break
        
        # Adicionar email se a coluna existir e email foi fornecido
        if email and 'email' in columns:
            insert_cols.append('email')
            insert_values.append(email)
        
        if not insert_cols:
            print("❌ Nenhuma coluna válida para inserção")
            cur.close()
            return False
        
        # Construir query INSERT
        placeholders = ', '.join(['%s'] * len(insert_values))
        query = f"INSERT INTO usuario ({', '.join(insert_cols)}) VALUES ({placeholders}) RETURNING id"
        
        cur.execute(query, insert_values)
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return True
    except psycopg2.IntegrityError as e:
        print(f"Erro de integridade: {e}")
        if conn:
            conn.rollback()
        return False  # Usuário já existe
    except psycopg2.Error as e:
        print(f"Erro ao criar usuário: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

# ==================== OPERAÇÕES DE FUNCIONÁRIOS ====================

def get_employees_by_company(company_id):
    """Busca todos os funcionários de uma empresa"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Descobrir quais colunas existem
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'usuario'
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cur.fetchall()]
        
        # Verificar se id_empresa existe
        id_empresa_col = None
        for col_name in ['id_empresa', 'empresa_id', 'empresa', 'company_id']:
            if col_name in columns:
                id_empresa_col = col_name
                break
        
        # Se não tem coluna de empresa, retornar vazio ou todos os funcionários
        if not id_empresa_col:
            # Se não tem coluna de empresa, buscar apenas por tipo_acesso
            if 'tipo_acesso' in columns:
                cur.execute(
                    "SELECT id, nome, cpf FROM usuario WHERE tipo_acesso = 'funcionario'"
                )
            else:
                # Se não tem tipo_acesso, retornar vazio
                cur.close()
                return []
        else:
            # Converter company_id para int se possível
            try:
                company_id_int = int(company_id)
            except (ValueError, TypeError):
                company_id_int = company_id
            
            if 'tipo_acesso' in columns:
                cur.execute(
                    f"SELECT id, nome, cpf FROM usuario WHERE {id_empresa_col} = %s AND tipo_acesso = 'funcionario'",
                    (company_id_int,)
                )
            else:
                cur.execute(
                    f"SELECT id, nome, cpf FROM usuario WHERE {id_empresa_col} = %s",
                    (company_id_int,)
                )
        
        results = cur.fetchall()
        cur.close()
        
        employees = []
        if id_empresa_col:
            for result in results:
                employees.append({
                    'id': result[0],
                    'nome': result[1],
                    'cpf': result[2],
                    'id_empresa': str(company_id_int)
                })
        else:
            legacy_employees = _get_employees_from_funcionarios(company_id)
            if legacy_employees:
                return legacy_employees
            for result in results:
                employees.append({
                    'id': result[0],
                    'nome': result[1],
                    'cpf': result[2],
                    'id_empresa': None
                })
        return employees
    except psycopg2.Error as e:
        print(f"Erro ao buscar funcionários: {e}")
        return []
    finally:
        if conn:
            return_connection(conn)

def get_employee_by_cpf(cpf, company_id=None):
    """Busca funcionário por CPF"""
    # Usar a mesma função get_user_by_cpf que já detecta colunas dinamicamente
    user = get_user_by_cpf(cpf)
    if user:
        # Verificar se é funcionário
        tipo_acesso = user.get('tipo_acesso', '').lower() if user.get('tipo_acesso') else ''
        id_empresa = user.get('id_empresa')
        
        # Se tem tipo_acesso e é funcionário, ou se não tem tipo_acesso mas tem id_empresa
        if tipo_acesso == 'funcionario' or (not tipo_acesso and id_empresa is not None):
            if company_id and id_empresa and str(id_empresa) != str(company_id):
                return None  # Não pertence à empresa especificada
            return user
    
    return None

def create_employee(cpf, password_hash, company_id, name=None):
    """Cria um novo funcionário"""
    # Converter company_id para int se possível
    try:
        company_id_int = int(company_id)
    except (ValueError, TypeError):
        company_id_int = company_id
    
    display_name = name or f"Funcionário {cpf[:3]}"
    success = create_user(
        cpf,
        password_hash,
        display_name,
        tipo_acesso='funcionario',
        id_empresa=company_id_int
    )

    if success:
        _sync_funcionarios_record(cpf, password_hash, company_id_int, display_name)

    return success

def delete_employee(cpf, company_id):
    """Exclui um funcionário"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Remover formatação do CPF
        cpf_clean = cpf.replace('.', '').replace('-', '').strip()
        
        # Descobrir quais colunas existem
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'usuario'
            ORDER BY ordinal_position;
        """)
        columns = [row[0] for row in cur.fetchall()]
        
        # Construir WHERE dinamicamente
        where_conditions = ["cpf = %s"]
        where_params = [cpf_clean]
        
        # Adicionar tipo_acesso se existir
        if 'tipo_acesso' in columns:
            where_conditions.append("tipo_acesso = 'funcionario'")
        
        # Adicionar id_empresa se existir
        id_empresa_col = None
        for col_name in ['id_empresa', 'empresa_id', 'empresa', 'company_id']:
            if col_name in columns:
                id_empresa_col = col_name
                try:
                    company_id_int = int(company_id)
                except (ValueError, TypeError):
                    company_id_int = company_id
                where_conditions.append(f"{col_name} = %s")
                where_params.append(company_id_int)
                break
        
        query = f"DELETE FROM usuario WHERE {' AND '.join(where_conditions)}"
        cur.execute(query, where_params)
        
        if cur.rowcount == 0:
            cur.close()
            return False  # Funcionário não encontrado
        
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro ao excluir funcionário: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

# ==================== OPERAÇÕES DE EMPRESAS ====================

def get_company(company_id):
    """Busca informações de uma empresa"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Tentar buscar em uma tabela empresa, se existir
        # Se não existir, retornar None (a empresa será identificada pelo id_empresa)
        try:
            cur.execute(
                "SELECT id, nome FROM empresa WHERE id = %s",
                (company_id,)
            )
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1]
                }
        except psycopg2.Error:
            # Tabela empresa pode não existir, isso é ok
            pass
        
        cur.close()
        return None
    except psycopg2.Error as e:
        print(f"Erro ao buscar empresa: {e}")
        return None
    finally:
        if conn:
            return_connection(conn)

# ==================== OPERAÇÕES DE PRODUTOS ====================

def get_products_by_company(company_id):
    """Busca todos os produtos de uma empresa"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter company_id para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        cur.execute(
            "SELECT id, nome, quantidade, preco, id_empresa FROM produto WHERE id_empresa = %s ORDER BY id",
            (company_id_int,)
        )
        results = cur.fetchall()
        cur.close()
        
        products = []
        for result in results:
            products.append({
                'id': str(result[0]),
                'name': result[1],
                'quantity': result[2],
                'value': float(result[3]),
                'company_id': str(result[4]),
                'created_at': None  # Se não houver created_at na tabela
            })
        return products
    except psycopg2.Error as e:
        print(f"Erro ao buscar produtos: {e}")
        return []
    finally:
        if conn:
            return_connection(conn)

def get_product_by_name(company_id, name):
    """Busca produto por nome na empresa"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter company_id para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        cur.execute(
            "SELECT id, nome, quantidade, preco, id_empresa FROM produto WHERE id_empresa = %s AND nome = %s",
            (company_id_int, name)
        )
        result = cur.fetchone()
        cur.close()
        
        if result:
            return {
                'id': str(result[0]),
                'name': result[1],
                'quantity': result[2],
                'value': float(result[3]),
                'company_id': str(result[4]),
                'created_at': None
            }
        return None
    except psycopg2.Error as e:
        print(f"Erro ao buscar produto: {e}")
        return None
    finally:
        if conn:
            return_connection(conn)

def get_product_by_id(company_id, product_id):
    """Busca produto por ID"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter company_id para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        # Converter product_id para int se possível
        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            product_id_int = product_id
        
        cur.execute(
            "SELECT id, nome, quantidade, preco, id_empresa FROM produto WHERE id = %s AND id_empresa = %s",
            (product_id_int, company_id_int)
        )
        result = cur.fetchone()
        cur.close()
        
        if result:
            return {
                'id': str(result[0]),
                'name': result[1],
                'quantity': result[2],
                'value': float(result[3]),
                'company_id': str(result[4]),
                'created_at': None
            }
        return None
    except psycopg2.Error as e:
        print(f"Erro ao buscar produto: {e}")
        return None
    finally:
        if conn:
            return_connection(conn)

def create_product(company_id, name, quantity, value):
    """Cria um novo produto"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter company_id para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        cur.execute(
            "INSERT INTO produto (nome, quantidade, preco, id_empresa) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, quantity, value, company_id_int)
        )
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        # Buscar o produto criado para retornar
        return get_product_by_id(company_id, product_id)
    except psycopg2.Error as e:
        print(f"Erro ao criar produto: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def update_product_quantity(company_id, product_id, new_quantity):
    """Atualiza a quantidade de um produto"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter IDs para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            product_id_int = product_id
        
        cur.execute(
            "UPDATE produto SET quantidade = %s WHERE id = %s AND id_empresa = %s",
            (new_quantity, product_id_int, company_id_int)
        )
        
        if cur.rowcount == 0:
            cur.close()
            return None
        
        conn.commit()
        cur.close()
        
        return get_product_by_id(company_id, product_id)
    except psycopg2.Error as e:
        print(f"Erro ao atualizar produto: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def update_product(company_id, product_id, name=None, quantity=None, value=None):
    """Atualiza um produto"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter IDs para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            product_id_int = product_id
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("nome = %s")
            params.append(name)
        if quantity is not None:
            updates.append("quantidade = %s")
            params.append(quantity)
        if value is not None:
            updates.append("preco = %s")
            params.append(value)
        
        if not updates:
            cur.close()
            return get_product_by_id(company_id, product_id)
        
        params.extend([product_id_int, company_id_int])
        query = f"UPDATE produto SET {', '.join(updates)} WHERE id = %s AND id_empresa = %s"
        
        cur.execute(query, params)
        
        if cur.rowcount == 0:
            cur.close()
            return None
        
        conn.commit()
        cur.close()
        
        return get_product_by_id(company_id, product_id)
    except psycopg2.Error as e:
        print(f"Erro ao atualizar produto: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def delete_product(company_id, product_id):
    """Exclui um produto"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Converter IDs para int se possível
        try:
            company_id_int = int(company_id)
        except (ValueError, TypeError):
            company_id_int = company_id
        
        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            product_id_int = product_id
        
        cur.execute(
            "DELETE FROM produto WHERE id = %s AND id_empresa = %s",
            (product_id_int, company_id_int)
        )
        
        if cur.rowcount == 0:
            cur.close()
            return False
        
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro ao excluir produto: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)
