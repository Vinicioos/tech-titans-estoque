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
    document.getElementById('companyName').textContent = `Gerenciamento - ${company.name}`;
});

// Voltar para o dashboard
function goBack() {
    window.location.href = 'dashboard.html';
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

// Função para criar funcionário
function openCreateEmployee() {
    window.location.href = 'employee-management.html';
}

// Função para visualizar estoque
function openViewStock() {
    window.location.href = 'view-stock.html';
}

// Função para adicionar produtos
function openAddProducts() {
    window.location.href = 'add-products.html';
}

