// Verificar se o usuário está logado e se há empresa selecionada
document.addEventListener('DOMContentLoaded', async function() {
    const user = localStorage.getItem('user');
    
    if (!user) {
        window.location.href = 'index.html';
        return;
    }
    
    const userData = JSON.parse(user);
    let selectedCompany = localStorage.getItem('selectedCompany');
    
    // Se não há empresa selecionada, verificar se é funcionário
    if (!selectedCompany) {
        if (userData.user_type === 'funcionario') {
            // Funcionário: buscar empresa pelo company_id
            try {
                const response = await fetch(`http://localhost:5000/company/${userData.company_id}`);
                const result = await response.json();
                
                if (response.ok) {
                    // Criar objeto de empresa a partir da resposta da API
                    const company = {
                        id: result.id,
                        name: result.name
                    };
                    // Salvar no localStorage para uso posterior
                    localStorage.setItem('selectedCompany', JSON.stringify(company));
                    selectedCompany = JSON.stringify(company);
                } else {
                    // Se não conseguir buscar, criar empresa básica
                    const company = {
                        id: userData.company_id,
                        name: `Empresa ${userData.company_id}`
                    };
                    localStorage.setItem('selectedCompany', JSON.stringify(company));
                    selectedCompany = JSON.stringify(company);
                }
            } catch (error) {
                console.error('Erro ao buscar informações da empresa:', error);
                // Criar empresa básica em caso de erro
                const company = {
                    id: userData.company_id,
                    name: `Empresa ${userData.company_id}`
                };
                localStorage.setItem('selectedCompany', JSON.stringify(company));
                selectedCompany = JSON.stringify(company);
            }
        } else {
            // Se não é funcionário e não há empresa selecionada, redirecionar
            window.location.href = 'dashboard.html';
            return;
        }
    }
    
    // Carregar nome da empresa selecionada
    const company = JSON.parse(selectedCompany);
    document.getElementById('companyName').textContent = `Produtos - ${company.name}`;
    
    // Configurar formulários
    setupForms();
});

let currentCompanyId = null;

// Configurar formulários
function setupForms() {
    const selectedCompany = JSON.parse(localStorage.getItem('selectedCompany'));
    
    // Usar o ID real da empresa selecionada
    currentCompanyId = selectedCompany ? selectedCompany.id.toString() : '1';
    
    console.log('Empresa selecionada:', selectedCompany);
    console.log('ID da empresa para produtos:', currentCompanyId);
    
    // Formulário de adicionar produto
    const addForm = document.getElementById('addProductForm');
    addForm.addEventListener('submit', handleAddProduct);
}

// Limpar erro
function clearError(fieldName) {
    const errorElement = document.getElementById(fieldName + 'Error');
    if (errorElement) {
        errorElement.textContent = '';
    }
    const inputElement = document.querySelector(`[name="${fieldName}"]`);
    if (inputElement) {
        inputElement.classList.remove('error');
    }
}

// Mostrar erro
function showError(fieldName, message) {
    const errorElement = document.getElementById(fieldName + 'Error');
    const inputElement = document.querySelector(`[name="${fieldName}"]`);
    
    if (errorElement) {
        errorElement.textContent = message;
    }
    if (inputElement) {
        inputElement.classList.add('error');
    }
}

// Validar nome do produto
function validateProductName(name) {
    if (!name.trim()) {
        return { valid: false, message: 'Nome do produto é obrigatório' };
    }
    if (name.length > 100) {
        return { valid: false, message: 'Nome do produto deve ter no máximo 100 caracteres' };
    }
    return { valid: true, message: '' };
}

// Validar quantidade
function validateQuantity(quantity) {
    const qty = parseInt(quantity);
    if (isNaN(qty) || qty < 0) {
        return { valid: false, message: 'Quantidade deve ser um número maior ou igual a zero' };
    }
    return { valid: true, message: '' };
}

// Validar valor
function validateValue(value) {
    const val = parseFloat(value);
    if (isNaN(val) || val < 0) {
        return { valid: false, message: 'Valor deve ser um número maior ou igual a zero' };
    }
    return { valid: true, message: '' };
}

// Adicionar produto
async function handleAddProduct(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const name = formData.get('name');
    const quantity = formData.get('quantity');
    const value = formData.get('value');
    
    // Limpar erros
    clearError('name');
    clearError('quantity');
    clearError('value');
    
    let hasErrors = false;
    
    // Validar nome
    const nameValidation = validateProductName(name);
    if (!nameValidation.valid) {
        showError('name', nameValidation.message);
        hasErrors = true;
    }
    
    // Validar quantidade
    const quantityValidation = validateQuantity(quantity);
    if (!quantityValidation.valid) {
        showError('quantity', quantityValidation.message);
        hasErrors = true;
    }
    
    // Validar valor
    const valueValidation = validateValue(value);
    if (!valueValidation.valid) {
        showError('value', valueValidation.message);
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    // Mostrar loading
    const addBtn = document.getElementById('addBtn');
    addBtn.disabled = true;
    addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';
    
    try {
        const response = await fetch(`http://localhost:5000/products/${currentCompanyId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name: name.trim(), 
                quantity: parseInt(quantity), 
                value: parseFloat(value) 
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Verificar se o produto foi atualizado (já existia) ou criado
            if (result.updated) {
                alert(result.message || 'Produto já existia. Quantidade foi somada ao estoque!');
            } else {
                alert('Produto adicionado com sucesso!');
            }
            e.target.reset();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    } finally {
        // Restaurar botão
        addBtn.disabled = false;
        addBtn.innerHTML = '<i class="fas fa-plus-circle"></i> Adicionar Produto';
    }
}


// Voltar para o gerenciamento da empresa
function goBack() {
    const user = localStorage.getItem('user');
    if (user) {
        const userData = JSON.parse(user);
        if (userData.user_type === 'funcionario') {
            window.location.href = 'employee-dashboard.html';
        } else {
            window.location.href = 'company-management.html';
        }
    } else {
        window.location.href = 'dashboard.html';
    }
}

// Logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        localStorage.removeItem('user');
        localStorage.removeItem('selectedCompany');
        localStorage.removeItem('selectedCompanyIndex');
        window.location.href = 'index.html';
    }
}
