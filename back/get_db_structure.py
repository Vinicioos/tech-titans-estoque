#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obter a estrutura completa do banco de dados
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import db_config
    import psycopg2
    
    conn = db_config.get_connection()
    cur = conn.cursor()
    
    # Listar todas as tabelas
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    
    db_structure = {}
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Tabela: {table_name}")
        
        # Obter colunas
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cur.fetchall()
        
        table_info = {
            'columns': []
        }
        
        for col in columns:
            col_info = {
                'name': col[0],
                'type': col[1],
                'max_length': col[2],
                'nullable': col[3],
                'default': col[4]
            }
            table_info['columns'].append(col_info)
            print(f"   • {col[0]}: {col[1]}{f'({col[2]})' if col[2] else ''} {'NULL' if col[3] == 'YES' else 'NOT NULL'}")
        
        # Obter chaves primárias
        cur.execute("""
            SELECT column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = %s 
                AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position;
        """, (table_name,))
        pk_columns = cur.fetchall()
        if pk_columns:
            table_info['primary_key'] = [pk[0] for pk in pk_columns]
            print(f"   🔑 Primary Key: {', '.join([pk[0] for pk in pk_columns])}")
        
        # Obter chaves estrangeiras
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = %s;
        """, (table_name,))
        fk_columns = cur.fetchall()
        if fk_columns:
            table_info['foreign_keys'] = []
            for fk in fk_columns:
                fk_info = {
                    'column': fk[0],
                    'references_table': fk[1],
                    'references_column': fk[2]
                }
                table_info['foreign_keys'].append(fk_info)
                print(f"   🔗 Foreign Key: {fk[0]} -> {fk[1]}.{fk[2]}")
        
        db_structure[table_name] = table_info
    
    cur.close()
    db_config.return_connection(conn)
    
    # Salvar estrutura em arquivo JSON
    with open('db_structure.json', 'w', encoding='utf-8') as f:
        json.dump(db_structure, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Estrutura salva em db_structure.json")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()


