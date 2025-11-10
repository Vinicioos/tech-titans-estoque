from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import db_config
import db_operations

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

def validate_cpf(cpf):
    """Valida se o CPF tem 11 dígitos numéricos"""
    cpf_numbers = re.sub(r'\D', '', cpf)
    return len(cpf_numbers) == 11

def validate_password(password):
    """Valida se a senha atende aos requisitos"""
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Senha deve conter pelo menos um caractere especial"
    
    return True, "Senha válida"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Dados não fornecidos"}), 400
        
        cpf = data.get('cpf', '')
        password = data.get('password', '')
        
        # Validar CPF
        if not validate_cpf(cpf):
            return jsonify({"message": "CPF inválido"}), 400
        
        # Validar senha
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            return jsonify({"message": password_message}), 400
        
        # Remover formatação do CPF para busca
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        print(f"🔍 Tentativa de login - CPF: {cpf_numbers}")
        
        # Buscar usuário (pode ser chefe ou funcionário)
        user = db_operations.get_user_by_cpf(cpf_numbers)
        
        if user:
            print(f"✅ Usuário encontrado: {user.get('nome', 'N/A')}")
            print(f"   Tipo: {user.get('tipo_acesso', 'N/A')}, ID Empresa: {user.get('id_empresa', 'N/A')}")
            
            password_hash = db_operations.hash_password(password)
            hash_banco = user['password_hash']
            
            print(f"   Hash calculado: {password_hash[:20]}...")
            print(f"   Hash no banco: {hash_banco[:20]}...")
            
            if hash_banco == password_hash:
                print("✅ Senha correta!")
                # Verificar tipo de acesso
                tipo_acesso = user.get('tipo_acesso', '').lower() if user.get('tipo_acesso') else ''
                id_empresa = user.get('id_empresa')
                
                if tipo_acesso == 'chefe' or (not tipo_acesso and id_empresa is None):
                    # É um chefe
                    user_data = {
                        'cpf': user['cpf'],
                        'name': user['nome'],
                        'user_type': 'chefe'
                    }
                    print("✅ Login realizado como CHEFE")
                    return jsonify({
                        "message": "Login realizado com sucesso",
                        "user": user_data
                    }), 200
                elif tipo_acesso == 'funcionario' or id_empresa is not None:
                    # É um funcionário
                    if id_empresa is None:
                        print("❌ Funcionário sem empresa associada")
                        return jsonify({"message": "Funcionário sem empresa associada"}), 401
                    
                    user_data = {
                        "cpf": user['cpf'],
                        "company_id": str(id_empresa),
                        "user_type": "funcionario"
                    }
                    print("✅ Login realizado como FUNCIONÁRIO")
                    return jsonify({
                        "message": "Login realizado com sucesso",
                        "user": user_data
                    }), 200
            else:
                print("❌ Senha incorreta!")
        else:
            print(f"❌ Usuário não encontrado no banco para CPF: {cpf_numbers}")
        
        # Se não encontrou em lugar nenhum
        return jsonify({"message": "CPF ou senha incorretos, tente novamente"}), 401
        
    except Exception as e:
        return jsonify({"message": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Dados não fornecidos"}), 400
        
        cpf = data.get('cpf', '')
        password = data.get('password', '')
        name = data.get('name', '')
        email = data.get('email', '')
        
        # Validar CPF
        if not validate_cpf(cpf):
            return jsonify({"message": "CPF inválido"}), 400
        
        # Validar senha
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            return jsonify({"message": password_message}), 400
        
        # Remover formatação do CPF
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        # Verificar se usuário já existe
        existing_user = db_operations.get_user_by_cpf(cpf_numbers)
        if existing_user:
            return jsonify({"message": "Usuário já cadastrado"}), 409
        
        # Criar novo usuário (chefe por padrão)
        password_hash = db_operations.hash_password(password)
        # id_empresa=None para chefes
        success = db_operations.create_user(cpf_numbers, password_hash, name, email, tipo_acesso='chefe', id_empresa=None)
        
        if success:
            return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
        else:
            return jsonify({"message": "Erro ao cadastrar usuário. Verifique se o CPF já está cadastrado."}), 500
        
    except Exception as e:
        return jsonify({"message": f"Erro interno do servidor: {str(e)}"}), 500

# Endpoints para funcionários
@app.route('/employees/<company_id>', methods=['GET'])
def get_employees(company_id):
    """Buscar todos os funcionários de uma empresa"""
    try:
        employees = db_operations.get_employees_by_company(company_id)
        return jsonify({"employees": employees}), 200
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/employees/<company_id>', methods=['POST'])
def create_employee(company_id):
    """Criar novo funcionário"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Dados não fornecidos"}), 400
        
        cpf = data.get('cpf', '')
        password = data.get('password', '')
        name = data.get('name', '')
        
        # Validar CPF
        if not validate_cpf(cpf):
            return jsonify({"message": "CPF inválido"}), 400
        
        # Validar senha
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            return jsonify({"message": password_message}), 400
        
        # Remover formatação do CPF
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        # Verificar se funcionário já existe
        existing_employee = db_operations.get_employee_by_cpf(cpf_numbers, company_id)
        if existing_employee:
            return jsonify({"message": "Funcionário já cadastrado nesta empresa"}), 409
        
        # Criar novo funcionário
        password_hash = db_operations.hash_password(password)
        success = db_operations.create_employee(cpf_numbers, password_hash, company_id, name)
        
        if success:
            return jsonify({
                "message": "Funcionário cadastrado com sucesso",
                "employee": {
                    "cpf": cpf_numbers,
                    "company_id": company_id
                }
            }), 201
        else:
            return jsonify({"message": "Erro ao cadastrar funcionário"}), 500
        
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/employees/<company_id>/<employee_cpf>', methods=['DELETE'])
def delete_employee(company_id, employee_cpf):
    """Excluir funcionário"""
    try:
        # Remover formatação do CPF
        cpf_numbers = re.sub(r'\D', '', employee_cpf)
        
        success = db_operations.delete_employee(cpf_numbers, company_id)
        
        if success:
            return jsonify({"message": "Funcionário excluído com sucesso"}), 200
        else:
            return jsonify({"message": "Funcionário não encontrado"}), 404
        
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/company/<company_id>', methods=['GET'])
def get_company_info(company_id):
    """Buscar informações de uma empresa"""
    try:
        company = db_operations.get_company(company_id)
        if company:
            return jsonify({
                "id": str(company['id']),
                "name": company.get('name', company.get('nome', f"Empresa {company_id}"))
            }), 200
        else:
            # Se não encontrar na tabela empresa, retornar apenas o ID
            return jsonify({
                "id": company_id,
                "name": f"Empresa {company_id}"
            }), 200
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

# Endpoints para produtos
@app.route('/products/<company_id>', methods=['GET'])
def get_products(company_id):
    """Buscar todos os produtos de uma empresa"""
    try:
        products = db_operations.get_products_by_company(company_id)
        print(f"📦 Buscando produtos da empresa {company_id}: {len(products)} produtos encontrados")
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/products/<company_id>', methods=['POST'])
def create_product(company_id):
    """Criar novo produto"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Dados não fornecidos"}), 400
        
        name = data.get('name', '').strip()
        quantity = data.get('quantity', 0)
        value = data.get('value', 0.0)
        
        # Validar nome
        if not name:
            return jsonify({"message": "Nome do produto é obrigatório"}), 400
        
        if len(name) > 100:
            return jsonify({"message": "Nome do produto deve ter no máximo 100 caracteres"}), 400
        
        # Validar quantidade
        try:
            quantity = int(quantity)
            if quantity < 0:
                return jsonify({"message": "Quantidade deve ser maior ou igual a zero"}), 400
        except (ValueError, TypeError):
            return jsonify({"message": "Quantidade deve ser um número válido"}), 400
        
        # Validar valor
        try:
            value = float(value)
            if value < 0:
                return jsonify({"message": "Valor deve ser maior ou igual a zero"}), 400
        except (ValueError, TypeError):
            return jsonify({"message": "Valor deve ser um número válido"}), 400
        
        # Verificar se já existe um produto com o mesmo nome
        existing_product = db_operations.get_product_by_name(company_id, name)
        
        if existing_product:
            # Se o produto já existe, somar a quantidade
            old_quantity = existing_product['quantity']
            new_quantity = old_quantity + quantity
            
            updated_product = db_operations.update_product_quantity(
                company_id, 
                existing_product['id'], 
                new_quantity
            )
            
            if updated_product:
                print(f"🔄 Produto '{name}' já existe. Somando quantidade: {old_quantity} + {quantity} = {new_quantity}")
                return jsonify({
                    "message": f"Produto '{name}' já existe. Quantidade atualizada de {old_quantity} para {new_quantity}",
                    "product": updated_product,
                    "updated": True
                }), 200
            else:
                return jsonify({"message": "Erro ao atualizar produto"}), 500
        else:
            # Se não existe, criar novo produto
            print(f"🔧 Criando novo produto para empresa {company_id}: {name}")
            
            new_product = db_operations.create_product(company_id, name, quantity, value)
            
            if new_product:
                return jsonify({
                    "message": "Produto cadastrado com sucesso",
                    "product": new_product,
                    "updated": False
                }), 201
            else:
                return jsonify({"message": "Erro ao cadastrar produto"}), 500
        
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/products/<company_id>/<product_id>', methods=['PUT'])
def update_product(company_id, product_id):
    """Atualizar produto"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Dados não fornecidos"}), 400
        
        # Verificar se produto existe
        product = db_operations.get_product_by_id(company_id, product_id)
        if not product:
            return jsonify({"message": "Produto não encontrado"}), 404
        
        # Preparar dados para atualização
        name = None
        quantity = None
        value = None
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({"message": "Nome do produto é obrigatório"}), 400
            if len(name) > 100:
                return jsonify({"message": "Nome do produto deve ter no máximo 100 caracteres"}), 400
        
        if 'quantity' in data:
            try:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({"message": "Quantidade deve ser maior ou igual a zero"}), 400
            except (ValueError, TypeError):
                return jsonify({"message": "Quantidade deve ser um número válido"}), 400
        
        if 'value' in data:
            try:
                value = float(data['value'])
                if value < 0:
                    return jsonify({"message": "Valor deve ser maior ou igual a zero"}), 400
            except (ValueError, TypeError):
                return jsonify({"message": "Valor deve ser um número válido"}), 400
        
        # Atualizar produto
        updated_product = db_operations.update_product(company_id, product_id, name, quantity, value)
        
        if updated_product:
            return jsonify({
                "message": "Produto atualizado com sucesso",
                "product": updated_product
            }), 200
        else:
            return jsonify({"message": "Erro ao atualizar produto"}), 500
        
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/products/<company_id>/<product_id>', methods=['DELETE'])
def delete_product(company_id, product_id):
    """Excluir produto"""
    try:
        success = db_operations.delete_product(company_id, product_id)
        
        if success:
            return jsonify({"message": "Produto excluído com sucesso"}), 200
        else:
            return jsonify({"message": "Produto não encontrado"}), 404
        
    except Exception as e:
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Servidor funcionando"}), 200

@app.route('/create-test-user', methods=['POST'])
def create_test_user():
    """Cria usuário de teste para desenvolvimento"""
    try:
        cpf = "12345678901"
        password = "Senha123!"
        name = "Usuário Teste"
        
        # Verificar se já existe
        existing_user = db_operations.get_user_by_cpf(cpf)
        if existing_user:
            return jsonify({
                "message": "Usuário de teste já existe",
                "cpf": "123.456.789-01",
                "password": password
            }), 200
        
        # Criar usuário
        password_hash = db_operations.hash_password(password)
        success = db_operations.create_user(
            cpf, 
            password_hash, 
            name, 
            email=None, 
            tipo_acesso='chefe', 
            id_empresa=None
        )
        
        if success:
            return jsonify({
                "message": "Usuário de teste criado com sucesso",
                "cpf": "123.456.789-01",
                "password": password,
                "user_type": "chefe"
            }), 201
        else:
            return jsonify({"message": "Erro ao criar usuário de teste"}), 500
            
    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500

def create_test_user_if_not_exists():
    """Cria usuário de teste se não existir"""
    try:
        cpf = "12345678901"
        password = "Senha123!"
        name = "Usuário Teste"
        
        # Verificar se já existe
        existing_user = db_operations.get_user_by_cpf(cpf)
        if existing_user:
            print(f"✅ Usuário de teste já existe: {existing_user.get('nome', 'N/A')}")
            return
        
        # Criar usuário
        print("🔧 Criando usuário de teste...")
        password_hash = db_operations.hash_password(password)
        success = db_operations.create_user(
            cpf, 
            password_hash, 
            name, 
            email=None, 
            tipo_acesso='chefe', 
            id_empresa=None
        )
        
        if success:
            print("✅ Usuário de teste criado com sucesso!")
            print(f"   CPF: 123.456.789-01")
            print(f"   Senha: {password}")
        else:
            print("⚠️  Não foi possível criar usuário de teste (pode já existir)")
            
    except Exception as e:
        print(f"⚠️  Erro ao criar usuário de teste: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando servidor Tech Titans...")
    print("📱 Frontend: http://localhost:3000 (ou abra o index.html)")
    print("🔧 Backend: http://localhost:5000")
    
    # Testar conexão com o banco de dados
    print("\n🔌 Testando conexão com PostgreSQL...")
    if db_config.test_connection():
        print("✅ Conexão com banco de dados estabelecida com sucesso!\n")
        
        # Criar usuário de teste se não existir
        create_test_user_if_not_exists()
        print("\n💡 Usuário de teste: CPF: 123.456.789-01, Senha: Senha123!\n")
    else:
        print("❌ Erro ao conectar com o banco de dados. Verifique as configurações.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
