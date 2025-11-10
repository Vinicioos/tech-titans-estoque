// Verificar se o usuário está logado
document.addEventListener('DOMContentLoaded', function() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'index.html';
        return;
    }
    
    const userData = JSON.parse(user);
    
    // Verificar se é chefe
    if (userData.user_type !== 'chefe') {
        // Se não for chefe, redirecionar para dashboard do funcionário
        window.location.href = 'employee-dashboard.html';
        return;
    }

    // Carregar empresas do localStorage
    loadCompanies();
});

let companies = [];
let editingCompanyIndex = -1;

// Carregar empresas do localStorage
function loadCompanies() {
    const savedCompanies = localStorage.getItem('companies');
    if (savedCompanies) {
        companies = JSON.parse(savedCompanies);
    } else {
        // Empresa padrão
        companies = [
            { name: 'Empresa 1', id: 1 }
        ];
        saveCompanies();
    }
    renderCompanies();
}

// Salvar empresas no localStorage
function saveCompanies() {
    localStorage.setItem('companies', JSON.stringify(companies));
}

// Renderizar empresas na tela
function renderCompanies() {
    const companiesGrid = document.getElementById('companiesGrid');
    const addBtn = document.getElementById('addCompanyBtn');
    
    companiesGrid.innerHTML = '';
    
    companies.forEach((company, index) => {
        const companyCard = document.createElement('div');
        companyCard.className = 'company-card';
        companyCard.innerHTML = `
            <h3 class="company-name" onclick="openCompanyManagement(${index})">${company.name}</h3>
            <button class="edit-btn" onclick="editCompany(${index})">
                <i class="fas fa-pencil-alt"></i>
            </button>
        `;
        companiesGrid.appendChild(companyCard);
    });
    
    // Mostrar/esconder botão de adicionar
    if (companies.length >= 3) {
        addBtn.style.display = 'none';
    } else {
        addBtn.style.display = 'flex';
    }
}

// Adicionar nova empresa
function addCompany() {
    if (companies.length >= 3) {
        alert('Máximo de 3 empresas permitidas');
        return;
    }
    
    const newCompany = {
        name: `Empresa ${companies.length + 1}`,
        id: companies.length + 1
    };
    
    companies.push(newCompany);
    saveCompanies();
    renderCompanies();
}

// Editar empresa
function editCompany(index) {
    editingCompanyIndex = index;
    const modal = document.getElementById('editModal');
    const input = document.getElementById('companyNameInput');
    
    input.value = companies[index].name;
    modal.classList.add('show');
    input.focus();
}

// Fechar modal
function closeModal() {
    const modal = document.getElementById('editModal');
    modal.classList.remove('show');
    editingCompanyIndex = -1;
}

// Salvar nome da empresa
function saveCompanyName() {
    const input = document.getElementById('companyNameInput');
    const newName = input.value.trim();
    
    if (!newName) {
        alert('Nome da empresa não pode estar vazio');
        return;
    }
    
    if (newName.length > 50) {
        alert('Nome da empresa deve ter no máximo 50 caracteres');
        return;
    }
    
    if (editingCompanyIndex >= 0) {
        companies[editingCompanyIndex].name = newName;
        saveCompanies();
        renderCompanies();
        closeModal();
    }
}

// Excluir empresa
function deleteCompany() {
    if (editingCompanyIndex < 0) {
        return;
    }
    
    // Verificar se é a última empresa
    if (companies.length <= 1) {
        alert('Não é possível excluir a última empresa. Deve haver pelo menos uma empresa.');
        return;
    }
    
    const companyName = companies[editingCompanyIndex].name;
    
    if (confirm(`Tem certeza que deseja excluir "${companyName}"?\n\nEsta ação não pode ser desfeita.`)) {
        // Remover empresa do array
        companies.splice(editingCompanyIndex, 1);
        
        // Salvar alterações
        saveCompanies();
        
        // Renderizar empresas atualizadas
        renderCompanies();
        
        // Fechar modal
        closeModal();
        
        // Mostrar mensagem de sucesso
        alert(`Empresa "${companyName}" foi excluída com sucesso!`);
    }
}

// Abrir gerenciamento da empresa
function openCompanyManagement(companyIndex) {
    if (companyIndex >= 0 && companyIndex < companies.length) {
        const company = companies[companyIndex];
        // Salvar empresa selecionada no localStorage
        localStorage.setItem('selectedCompany', JSON.stringify(company));
        localStorage.setItem('selectedCompanyIndex', companyIndex);
        // Navegar para a tela de gerenciamento
        window.location.href = 'company-management.html';
    }
}

// Logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

// Fechar modal ao clicar fora dele
document.addEventListener('click', function(e) {
    const modal = document.getElementById('editModal');
    if (e.target === modal) {
        closeModal();
    }
});

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Salvar com Enter no input
document.getElementById('companyNameInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        saveCompanyName();
    }
});
