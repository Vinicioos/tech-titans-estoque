// Verificar se o usuário está logado e se há empresa selecionada
document.addEventListener('DOMContentLoaded', function() {
    const user = localStorage.getItem('user');
    const selectedCompany = localStorage.getItem('selectedCompany');
    
    if (!user) {
        window.location.href = 'index.html';
        return;
    }
    
    if (!selectedCompany) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Carregar nome da empresa selecionada
    const company = JSON.parse(selectedCompany);
    document.getElementById('companyName').textContent = `Funcionários - ${company.name}`;
    
    // Configurar formulários
    setupForms();
    
    // Carregar lista de funcionários
    loadEmployees();
});

let currentCompanyId = null;

// Configurar formulários
function setupForms() {
    const selectedCompany = JSON.parse(localStorage.getItem('selectedCompany'));
    
    // Usar o ID real da empresa selecionada
    currentCompanyId = selectedCompany ? selectedCompany.id.toString() : '1';
    
    // Formulário de cadastro
    const createForm = document.getElementById('createEmployeeForm');
    createForm.addEventListener('submit', handleCreateEmployee);
    
    // Formulário de exclusão
    const deleteForm = document.getElementById('deleteEmployeeForm');
    deleteForm.addEventListener('submit', handleDeleteEmployee);
    
    // Formatação de CPF
    setupCpfFormatting();
}

// Configurar formatação de CPF
function setupCpfFormatting() {
    const cpfInputs = document.querySelectorAll('input[name="cpf"]');
    
    cpfInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
                e.target.value = value;
            }
            clearError(e.target.name);
        });
    });
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

// Validar CPF
function validateCPF(cpf) {
    const cpfNumbers = cpf.replace(/\D/g, '');
    return cpfNumbers.length === 11;
}

// Validar senha
function validatePassword(password) {
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!hasUpperCase) {
        return { valid: false, message: 'Senha deve conter pelo menos uma letra maiúscula' };
    }
    if (!hasLowerCase) {
        return { valid: false, message: 'Senha deve conter pelo menos uma letra minúscula' };
    }
    if (!hasNumbers) {
        return { valid: false, message: 'Senha deve conter pelo menos um número' };
    }
    if (!hasSpecialChar) {
        return { valid: false, message: 'Senha deve conter pelo menos um caractere especial' };
    }
    return { valid: true, message: '' };
}

// Cadastrar funcionário
async function handleCreateEmployee(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const cpf = formData.get('cpf');
    const password = formData.get('password');
    
    // Limpar erros
    clearError('cpf');
    clearError('password');
    
    let hasErrors = false;
    
    // Validar CPF
    if (!validateCPF(cpf)) {
        showError('cpf', 'CPF deve ter exatamente 11 números');
        hasErrors = true;
    }
    
    // Validar senha
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        showError('password', passwordValidation.message);
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    // Mostrar loading
    const createBtn = document.getElementById('createBtn');
    createBtn.disabled = true;
    createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';
    
    try {
        const response = await fetch(`http://localhost:5000/employees/${currentCompanyId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cpf, password })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Funcionário cadastrado com sucesso!');
            e.target.reset();
            // Recarregar lista se estiver na aba de visualização
            if (document.getElementById('listContent').classList.contains('active')) {
                loadEmployees();
            }
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    } finally {
        // Restaurar botão
        createBtn.disabled = false;
        createBtn.innerHTML = '<i class="fas fa-user-plus"></i> Cadastrar Funcionário';
    }
}

// Excluir funcionário
async function handleDeleteEmployee(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const cpf = formData.get('cpf');
    
    // Limpar erro
    clearError('cpf');
    
    // Validar CPF
    if (!validateCPF(cpf)) {
        showError('cpf', 'CPF deve ter exatamente 11 números');
        return;
    }
    
    const cpfNumbers = cpf.replace(/\D/g, '');
    
    if (!confirm(`Tem certeza que deseja excluir o funcionário com CPF ${cpf}?\n\nEsta ação não pode ser desfeita.`)) {
        return;
    }
    
    // Mostrar loading
    const deleteBtn = document.getElementById('deleteBtn');
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Excluindo...';
    
    try {
        const response = await fetch(`http://localhost:5000/employees/${currentCompanyId}/${cpfNumbers}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Funcionário excluído com sucesso!');
            e.target.reset();
            // Recarregar lista se estiver na aba de visualização
            if (document.getElementById('listContent').classList.contains('active')) {
                loadEmployees();
            }
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    } finally {
        // Restaurar botão
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Excluir Funcionário';
    }
}

// Carregar lista de funcionários
async function loadEmployees() {
    const employeesList = document.getElementById('employeesList');
    const loading = document.getElementById('loadingList');
    
    loading.style.display = 'block';
    employeesList.innerHTML = '<div class="loading" id="loadingList"><i class="fas fa-spinner fa-spin"></i> Carregando funcionários...</div>';
    
    try {
        const response = await fetch(`http://localhost:5000/employees/${currentCompanyId}`);
        const result = await response.json();
        
        if (response.ok) {
            displayEmployees(result.employees);
        } else {
            employeesList.innerHTML = '<div class="empty-list"><i class="fas fa-exclamation-triangle"></i><h3>Erro ao carregar funcionários</h3><p>' + result.message + '</p></div>';
        }
    } catch (error) {
        console.error('Erro:', error);
        employeesList.innerHTML = '<div class="empty-list"><i class="fas fa-exclamation-triangle"></i><h3>Erro de conexão</h3><p>Verifique se o servidor Python está rodando.</p></div>';
    }
}

// Exibir funcionários
function displayEmployees(employees) {
    const employeesList = document.getElementById('employeesList');
    const selectedCompany = JSON.parse(localStorage.getItem('selectedCompany'));
    const companyName = selectedCompany ? selectedCompany.name : 'Empresa';
    
    if (employees.length === 0) {
        employeesList.innerHTML = `
            <div class="empty-list">
                <i class="fas fa-users"></i>
                <h3>Nenhum funcionário cadastrado</h3>
                <p>Cadastre o primeiro funcionário para <strong>${companyName}</strong> usando a aba "Cadastrar Funcionário"</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    employees.forEach(employee => {
        const formattedCpf = employee.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        html += `
            <div class="employee-item">
                <div class="employee-info">
                    <div class="employee-cpf">CPF: ${formattedCpf}</div>
                    <div class="employee-company">Empresa: ${companyName}</div>
                </div>
            </div>
        `;
    });
    
    employeesList.innerHTML = html;
}

// Trocar abas
function showTab(tabName) {
    // Remover classe active de todas as abas e conteúdos
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Adicionar classe active na aba e conteúdo selecionados
    document.getElementById(tabName + 'Tab').classList.add('active');
    document.getElementById(tabName + 'Content').classList.add('active');
    
    // Se for a aba de lista, recarregar funcionários
    if (tabName === 'list') {
        loadEmployees();
    }
}

// Voltar para o gerenciamento da empresa
function goBack() {
    window.location.href = 'company-management.html';
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
