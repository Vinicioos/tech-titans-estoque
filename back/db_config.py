import psycopg2
from psycopg2 import pool
import os

# Configurações do banco de dados
DB_CONFIG = {
    'user': 'postgres',
    'password': 'VIA2609',
    'host': 'localhost',
    'port': '5432',
    'database': 'Estoque'
}

# Pool de conexões (opcional, mas recomendado para performance)
connection_pool = None


def get_connection():
    """Obtém uma conexão do banco de dados"""
    try:
        if connection_pool:
            return connection_pool.getconn()
        else:
            return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


def return_connection(conn):
    """Retorna uma conexão ao pool"""
    if connection_pool:
        connection_pool.putconn(conn)
    else:
        conn.close()


def init_connection_pool(minconn=1, maxconn=10):
    """Inicializa o pool de conexões"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn, maxconn, **DB_CONFIG
        )
        print("✅ Pool de conexões inicializado com sucesso")
    except psycopg2.Error as e:
        print(f"Erro ao inicializar pool de conexões: {e}")
        connection_pool = None


def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"✅ Conexão com PostgreSQL estabelecida: {db_version[0]}")
        cur.close()
        return_connection(conn)
        return True
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False


