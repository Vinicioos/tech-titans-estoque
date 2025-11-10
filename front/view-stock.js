// Variáveis globais
let currentCompanyId = null;
let allProducts = [];
let filteredProducts = [];

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
    document.getElementById('companyName').textContent = `Estoque - ${company.name}`;
    
    // Definir o ID da empresa antes de configurar formulários
    currentCompanyId = company ? company.id.toString() : '1';
    console.log('Empresa selecionada:', company);
    console.log('ID da empresa para visualizar estoque:', currentCompanyId);
    
    // Configurar formulários
    setupForms();
    
    // Carregar produtos automaticamente
    console.log('Carregando produtos para empresa ID:', currentCompanyId);
    loadProducts();
});

// Configurar formulários
function setupForms() {
    // Formulário de edição
    const editForm = document.getElementById('editProductForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveProduct();
        });
    }
}

// Carregar lista de produtos
async function loadProducts() {
    const productsList = document.getElementById('productsList');
    
    console.log('🔄 Iniciando carregamento de produtos...');
    console.log('📊 ID da empresa:', currentCompanyId);
    
    // Mostrar loading
    productsList.innerHTML = '<div class="loading" id="loadingList"><i class="fas fa-spinner fa-spin"></i> Carregando produtos...</div>';
    
    try {
        const url = `http://localhost:5000/products/${currentCompanyId}`;
        console.log('🌐 Fazendo requisição para:', url);
        
        const response = await fetch(url);
        const result = await response.json();
        
        console.log('📡 Resposta do servidor:', response.status, result);
        
        if (response.ok) {
            allProducts = result.products;
            filteredProducts = [...allProducts];
            console.log('✅ Produtos carregados:', allProducts.length);
            displayProducts(filteredProducts);
            updateStats();
        } else {
            console.log('❌ Erro ao carregar produtos:', result.message);
            productsList.innerHTML = '<div class="empty-list"><i class="fas fa-exclamation-triangle"></i><h3>Erro ao carregar produtos</h3><p>' + result.message + '</p></div>';
        }
    } catch (error) {
        console.error('Erro:', error);
        productsList.innerHTML = '<div class="empty-list"><i class="fas fa-exclamation-triangle"></i><h3>Erro de conexão</h3><p>Verifique se o servidor Python está rodando.</p></div>';
    }
}

// Exibir produtos
function displayProducts(products) {
    console.log('🎨 Exibindo produtos:', products.length);
    const productsList = document.getElementById('productsList');
    const selectedCompany = JSON.parse(localStorage.getItem('selectedCompany'));
    const companyName = selectedCompany ? selectedCompany.name : 'Empresa';
    
    if (products.length === 0) {
        console.log('📦 Lista vazia - exibindo mensagem de vazio');
        productsList.innerHTML = `
            <div class="empty-list">
                <i class="fas fa-boxes"></i>
                <h3>Nenhum produto encontrado</h3>
                <p>Não há produtos cadastrados para <strong>${companyName}</strong></p>
            </div>
        `;
        return;
    }
    
    let html = '';
    products.forEach(product => {
        const formattedValue = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(product.value);
        
        html += `
            <div class="product-item">
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-quantity">Qtd: ${product.quantity}</div>
                    <div class="product-value">${formattedValue}</div>
                    <div class="product-actions">
                        <button class="edit-btn" onclick="editProduct('${product.id}')">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="delete-btn" onclick="confirmDeleteProduct('${product.id}', '${product.name}')">
                            <i class="fas fa-trash"></i> Excluir
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    productsList.innerHTML = html;
    console.log('✅ Produtos exibidos na tela');
}

// Atualizar estatísticas
function updateStats() {
    console.log('📊 Atualizando estatísticas...');
    const totalProducts = allProducts.length;
    const totalQuantity = allProducts.reduce((sum, product) => sum + product.quantity, 0);
    const totalValue = allProducts.reduce((sum, product) => sum + (product.value * product.quantity), 0);
    
    console.log(`📈 Estatísticas: ${totalProducts} produtos, ${totalQuantity} quantidade, R$ ${totalValue.toFixed(2)}`);
    
    document.getElementById('totalProducts').textContent = totalProducts;
    document.getElementById('totalQuantity').textContent = totalQuantity;
    
    console.log('✅ Estatísticas atualizadas na tela');
    
    const formattedTotalValue = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(totalValue);
    
    document.getElementById('totalValue').textContent = formattedTotalValue;
}

// Buscar produtos
function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const clearBtn = document.getElementById('clearSearchBtn');
    
    if (searchTerm === '') {
        filteredProducts = [...allProducts];
        clearBtn.style.display = 'none';
    } else {
        filteredProducts = allProducts.filter(product => 
            product.name.toLowerCase().includes(searchTerm)
        );
        clearBtn.style.display = 'flex';
    }
    
    displayProducts(filteredProducts);
}

// Limpar busca
function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('clearSearchBtn').style.display = 'none';
    filteredProducts = [...allProducts];
    displayProducts(filteredProducts);
}

// Editar produto
function editProduct(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;
    
    document.getElementById('editProductId').value = productId;
    document.getElementById('editProductName').value = product.name;
    document.getElementById('editProductQuantity').value = product.quantity;
    document.getElementById('editProductValue').value = product.value;
    
    // Limpar erros
    clearEditErrors();
    
    // Mostrar modal
    document.getElementById('editModal').classList.add('show');
}

// Salvar produto editado
async function saveProduct() {
    const productId = document.getElementById('editProductId').value;
    const name = document.getElementById('editProductName').value.trim();
    const quantity = document.getElementById('editProductQuantity').value;
    const value = document.getElementById('editProductValue').value;
    
    // Limpar erros
    clearEditErrors();
    
    let hasErrors = false;
    
    // Validar nome
    if (!name) {
        showEditError('name', 'Nome do produto é obrigatório');
        hasErrors = true;
    } else if (name.length > 100) {
        showEditError('name', 'Nome do produto deve ter no máximo 100 caracteres');
        hasErrors = true;
    }
    
    // Validar quantidade
    const qty = parseInt(quantity);
    if (isNaN(qty) || qty < 0) {
        showEditError('quantity', 'Quantidade deve ser um número maior ou igual a zero');
        hasErrors = true;
    }
    
    // Validar valor
    const val = parseFloat(value);
    if (isNaN(val) || val < 0) {
        showEditError('value', 'Valor deve ser um número maior ou igual a zero');
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/products/${currentCompanyId}/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                quantity: qty,
                value: val
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Produto atualizado com sucesso!');
            closeEditModal();
            loadProducts();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    }
}

// Excluir produto
async function deleteProduct() {
    const productId = document.getElementById('editProductId').value;
    
    if (!confirm('Tem certeza que deseja excluir este produto?\n\nEsta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/products/${currentCompanyId}/${productId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Produto excluído com sucesso!');
            closeEditModal();
            loadProducts();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    }
}

// Confirmar exclusão
function confirmDeleteProduct(productId, productName) {
    if (confirm(`Tem certeza que deseja excluir o produto "${productName}"?\n\nEsta ação não pode ser desfeita.`)) {
        deleteProductDirect(productId);
    }
}

// Excluir produto diretamente
async function deleteProductDirect(productId) {
    try {
        const response = await fetch(`http://localhost:5000/products/${currentCompanyId}/${productId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Produto excluído com sucesso!');
            loadProducts();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Verifique se o servidor Python está rodando.');
    }
}

// Fechar modal de edição
function closeEditModal() {
    document.getElementById('editModal').classList.remove('show');
    clearEditErrors();
}

// Limpar erros de edição
function clearEditErrors() {
    const fields = ['name', 'quantity', 'value'];
    fields.forEach(field => {
        const errorElement = document.getElementById('edit' + field.charAt(0).toUpperCase() + field.slice(1) + 'Error');
        const inputElement = document.getElementById('editProduct' + field.charAt(0).toUpperCase() + field.slice(1));
        
        if (errorElement) errorElement.textContent = '';
        if (inputElement) inputElement.classList.remove('error');
    });
}

// Mostrar erro de edição
function showEditError(field, message) {
    const errorElement = document.getElementById('edit' + field.charAt(0).toUpperCase() + field.slice(1) + 'Error');
    const inputElement = document.getElementById('editProduct' + field.charAt(0).toUpperCase() + field.slice(1));
    
    if (errorElement) errorElement.textContent = message;
    if (inputElement) inputElement.classList.add('error');
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

// Fechar modal ao clicar fora dele
document.addEventListener('click', function(e) {
    const modal = document.getElementById('editModal');
    if (e.target === modal) {
        closeEditModal();
    }
});

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeEditModal();
    }
});
