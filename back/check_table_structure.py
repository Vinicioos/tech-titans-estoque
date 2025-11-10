#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar a estrutura real da tabela usuario
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_config
import psycopg2

try:
    conn = db_config.get_connection()
    cur = conn.cursor()
    
    print("=" * 60)
    print("🔍 ESTRUTURA DA TABELA usuario")
    print("=" * 60)
    
    # Listar todas as colunas da tabela usuario
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'usuario'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    
    if columns:
        print(f"\n📋 Colunas encontradas: {len(columns)}\n")
        for col in columns:
            col_type = col[1]
            if col[2]:
                col_type += f"({col[2]})"
            nullable = "NULL" if col[3] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[4]}" if col[4] else ""
            print(f"   • {col[0]}: {col_type} {nullable}{default}")
    else:
        print("\n❌ Tabela 'usuario' não encontrada!")
    
    # Verificar se há dados
    print("\n📊 Dados na tabela:")
    try:
        cur.execute("SELECT COUNT(*) FROM usuario")
        count = cur.fetchone()[0]
        print(f"   Total de registros: {count}")
        
        if count > 0:
            # Mostrar estrutura de um registro
            cur.execute("SELECT * FROM usuario LIMIT 1")
            result = cur.fetchone()
            if result:
                print("\n📋 Exemplo de registro:")
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = 'usuario'
                    ORDER BY ordinal_position;
                """)
                col_names = [row[0] for row in cur.fetchall()]
                for i, col_name in enumerate(col_names):
                    value = result[i]
                    if col_name == 'senha' and value:
                        value = value[:20] + "..." if len(str(value)) > 20 else value
                    print(f"   {col_name}: {value}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    cur.close()
    db_config.return_connection(conn)
    
    print("\n" + "=" * 60)
    print("✅ Verificação concluída!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()


