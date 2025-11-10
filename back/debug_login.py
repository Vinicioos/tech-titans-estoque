#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para problemas de login
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_config
import db_operations
import re

def main():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE LOGIN")
    print("=" * 60)
    
    # CPF de teste
    cpf_teste = "123.456.789-01"
    senha_teste = "Senha123!"
    cpf_limpo = re.sub(r'\D', '', cpf_teste)
    
    print(f"\n📋 Dados de teste:")
    print(f"   CPF: {cpf_teste}")
    print(f"   CPF limpo: {cpf_limpo}")
    print(f"   Senha: {senha_teste}")
    
    # Verificar se usuário existe
    print(f"\n1️⃣ Buscando usuário no banco...")
    user = db_operations.get_user_by_cpf(cpf_limpo)
    
    if user:
        print(f"   ✅ Usuário encontrado!")
        print(f"   ID: {user['id']}")
        print(f"   Nome: {user['nome']}")
        print(f"   CPF: {user['cpf']}")
        print(f"   Tipo Acesso: {user.get('tipo_acesso', 'N/A')}")
        print(f"   ID Empresa: {user.get('id_empresa', 'N/A')}")
        print(f"   Hash da senha (primeiros 20 chars): {user['password_hash'][:20]}...")
        
        # Testar hash da senha
        print(f"\n2️⃣ Testando hash da senha...")
        hash_calculado = db_operations.hash_password(senha_teste)
        hash_banco = user['password_hash']
        
        print(f"   Hash calculado (primeiros 20 chars): {hash_calculado[:20]}...")
        print(f"   Hash no banco (primeiros 20 chars): {hash_banco[:20]}...")
        
        if hash_calculado == hash_banco:
            print(f"   ✅ Senhas coincidem!")
        else:
            print(f"   ❌ Senhas NÃO coincidem!")
            print(f"   💡 A senha no banco pode estar diferente ou em texto plano")
    else:
        print(f"   ❌ Usuário NÃO encontrado no banco!")
        print(f"   💡 É necessário criar o usuário primeiro")
        
        # Perguntar se quer criar
        print(f"\n3️⃣ Criando usuário de teste...")
        password_hash = db_operations.hash_password(senha_teste)
        success = db_operations.create_user(
            cpf_limpo, 
            password_hash, 
            "Usuário Teste",
            email=None,
            tipo_acesso='chefe',
            id_empresa=None
        )
        
        if success:
            print(f"   ✅ Usuário criado com sucesso!")
            print(f"   💡 Agora você pode fazer login com:")
            print(f"      CPF: {cpf_teste}")
            print(f"      Senha: {senha_teste}")
        else:
            print(f"   ❌ Erro ao criar usuário")
            print(f"   💡 Verifique se o CPF já existe ou se há algum problema no banco")
    
    # Listar todos os usuários
    print(f"\n4️⃣ Listando todos os usuários no banco...")
    try:
        conn = db_config.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, cpf, tipo_acesso, id_empresa FROM usuario ORDER BY id")
        users = cur.fetchall()
        cur.close()
        db_config.return_connection(conn)
        
        if users:
            print(f"   📋 Total de usuários: {len(users)}")
            for u in users:
                print(f"      - ID: {u[0]}, Nome: {u[1]}, CPF: {u[2]}, Tipo: {u[3]}, Empresa: {u[4]}")
        else:
            print(f"   ⚠️  Nenhum usuário encontrado no banco")
    except Exception as e:
        print(f"   ❌ Erro ao listar usuários: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico concluído!")
    print("=" * 60)

if __name__ == "__main__":
    main()


