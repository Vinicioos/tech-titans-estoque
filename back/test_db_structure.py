#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido da estrutura do banco de dados
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_config
import psycopg2

try:
    conn = db_config.get_connection()
    cur = conn.cursor()
    
    print("🔍 Verificando estrutura das tabelas...\n")
    
    # Verificar tabela usuario
    print("📋 Tabela: usuario")
    try:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'usuario'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            for col in columns:
                print(f"   • {col[0]}: {col[1]}")
        else:
            print("   ❌ Tabela 'usuario' não encontrada")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Verificar tabela produto
    print("\n📋 Tabela: produto")
    try:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'produto'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            for col in columns:
                print(f"   • {col[0]}: {col[1]}")
        else:
            print("   ❌ Tabela 'produto' não encontrada")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar uma query simples
    print("\n🧪 Testando query SELECT na tabela usuario...")
    try:
        cur.execute("SELECT COUNT(*) FROM usuario")
        count = cur.fetchone()[0]
        print(f"   ✅ Tabela usuario tem {count} registro(s)")
    except Exception as e:
        print(f"   ❌ Erro ao consultar: {e}")
    
    print("\n🧪 Testando query SELECT na tabela produto...")
    try:
        cur.execute("SELECT COUNT(*) FROM produto")
        count = cur.fetchone()[0]
        print(f"   ✅ Tabela produto tem {count} registro(s)")
    except Exception as e:
        print(f"   ❌ Erro ao consultar: {e}")
    
    cur.close()
    db_config.return_connection(conn)
    
    print("\n✅ Teste concluído!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()


