#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico do banco de dados PostgreSQL
Verifica conexão e lista tabelas existentes
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import db_config
    import psycopg2
    
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 60)
    
    # Testar conexão
    print("\n1️⃣ Testando conexão...")
    try:
        conn = db_config.get_connection()
        print("   ✅ Conexão estabelecida com sucesso!")
        
        # Obter versão do PostgreSQL
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   📊 Versão: {version.split(',')[0]}")
        
        # Listar todas as tabelas
        print("\n2️⃣ Listando tabelas existentes no banco...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"   📋 Encontradas {len(tables)} tabela(s):")
            for table in tables:
                print(f"      - {table[0]}")
                
                # Mostrar estrutura de cada tabela
                print(f"        Colunas:")
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table[0],))
                columns = cur.fetchall()
                for col in columns:
                    col_type = col[1]
                    if col[2]:
                        col_type += f"({col[2]})"
                    print(f"          • {col[0]}: {col_type}")
        else:
            print("   ⚠️  Nenhuma tabela encontrada no banco de dados!")
            print("   💡 Você precisa criar as tabelas primeiro.")
            print("   💡 Veja o arquivo database_schema.sql para referência.")
        
        # Verificar tabelas esperadas
        print("\n3️⃣ Verificando tabelas esperadas pelo sistema...")
        expected_tables = ['usuarios', 'funcionarios', 'empresas', 'produtos']
        existing_table_names = [t[0] for t in tables]
        
        for expected in expected_tables:
            if expected in existing_table_names:
                print(f"   ✅ {expected} - encontrada")
            else:
                print(f"   ❌ {expected} - NÃO encontrada")
        
        cur.close()
        db_config.return_connection(conn)
        
        print("\n" + "=" * 60)
        print("✅ Diagnóstico concluído!")
        print("=" * 60)
        
    except psycopg2.Error as e:
        print(f"   ❌ Erro ao conectar: {e}")
        print("\n💡 Verifique:")
        print("   - PostgreSQL está rodando?")
        print("   - As credenciais em db_config.py estão corretas?")
        print("   - O banco 'Estoque' existe?")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Execute: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


