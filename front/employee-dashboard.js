// Verificar se o usuário está logado
document.addEventListener('DOMContentLoaded', function() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'index.html';
        return;
    }
    
    const userData = JSON.parse(user);
    
    // Verificar se é funcionário
    if (userData.user_type !== 'funcionario') {
        // Se não for funcionário, redirecionar para dashboard do chefe
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Carregar informações da empresa
    loadCompanyInfo(userData.company_id);
});

// Carregar informações da empresa
async function loadCompanyInfo(companyId) {
    try {
        // Primeiro, tentar buscar do localStorage (se estiver disponível)
        const companies = JSON.parse(localStorage.getItem('companies') || '[]');
        const company = companies.find(c => c.id == companyId);
        
        if (company) {
            document.getElementById('companyInfo').textContent = `Empresa: ${company.name}`;
            // Salvar empresa selecionada para uso nas outras páginas
            localStorage.setItem('selectedCompany', JSON.stringify(company));
        } else {
            // Se não encontrou no localStorage, buscar da API
            try {
                const response = await fetch(`http://localhost:5000/company/${companyId}`);
                const result = await response.json();
                
                if (response.ok) {
                    const companyData = {
                        id: result.id,
                        name: result.name
                    };
                    document.getElementById('companyInfo').textContent = `Empresa: ${result.name}`;
                    // Salvar empresa selecionada para uso nas outras páginas
                    localStorage.setItem('selectedCompany', JSON.stringify(companyData));
                } else {
                    document.getElementById('companyInfo').textContent = `Empresa ID: ${companyId}`;
                }
            } catch (apiError) {
                console.error('Erro ao buscar empresa da API:', apiError);
                document.getElementById('companyInfo').textContent = `Empresa ID: ${companyId}`;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar informações da empresa:', error);
        document.getElementById('companyInfo').textContent = `Empresa ID: ${companyId}`;
    }
}

// Função para visualizar estoque
function openViewStock() {
    window.location.href = 'view-stock.html';
}

// Função para adicionar produtos
function openAddProducts() {
    window.location.href = 'add-products.html';
}

// Logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}
