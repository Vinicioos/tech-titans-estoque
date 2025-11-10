document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const cpfInput = document.getElementById('cpf');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('loginButton');
    const cpfError = document.getElementById('cpfError');
    const passwordError = document.getElementById('passwordError');

    // Formatação automática do CPF
    cpfInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            e.target.value = value;
        }
        clearError('cpf');
    });

    // Limpar erro quando usuário digita
    passwordInput.addEventListener('input', function() {
        clearError('password');
    });

    // Validação de CPF (11 números)
    function validateCPF(cpf) {
        const cpfNumbers = cpf.replace(/\D/g, '');
        if (cpfNumbers.length !== 11) {
            return 'CPF deve ter exatamente 11 números';
        }
        return null;
    }

    // Validação de senha (maiúsculas, minúsculas, números e caracteres especiais)
    function validatePassword(password) {
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (!hasUpperCase) {
            return 'Senha deve conter pelo menos uma letra maiúscula';
        }
        if (!hasLowerCase) {
            return 'Senha deve conter pelo menos uma letra minúscula';
        }
        if (!hasNumbers) {
            return 'Senha deve conter pelo menos um número';
        }
        if (!hasSpecialChar) {
            return 'Senha deve conter pelo menos um caractere especial';
        }
        return null;
    }

    // Mostrar erro
    function showError(field, message) {
        const errorElement = field === 'cpf' ? cpfError : passwordError;
        const inputElement = field === 'cpf' ? cpfInput : passwordInput;
        
        errorElement.textContent = message;
        inputElement.classList.add('error');
    }

    // Limpar erro
    function clearError(field) {
        const errorElement = field === 'cpf' ? cpfError : passwordError;
        const inputElement = field === 'cpf' ? cpfInput : passwordInput;
        
        errorElement.textContent = '';
        inputElement.classList.remove('error');
    }

    // Envio do formulário
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const cpf = cpfInput.value;
        const password = passwordInput.value;
        
        // Limpar erros anteriores
        clearError('cpf');
        clearError('password');
        
        let hasErrors = false;
        
        // Validar CPF
        const cpfValidationError = validateCPF(cpf);
        if (cpfValidationError) {
            showError('cpf', cpfValidationError);
            hasErrors = true;
        }
        
        // Validar senha
        const passwordValidationError = validatePassword(password);
        if (passwordValidationError) {
            showError('password', passwordValidationError);
            hasErrors = true;
        }
        
        if (hasErrors) {
            return;
        }
        
        // Mostrar loading
        loginButton.disabled = true;
        loginButton.textContent = 'Entrando...';
        
        try {
            // Enviar dados para o backend Python
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cpf: cpf,
                    password: password
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Salvar dados do usuário no localStorage
                localStorage.setItem('user', JSON.stringify(result.user));
                
                // Verificar tipo de usuário e redirecionar
                if (result.user.user_type === 'chefe') {
                    // Chefe vai para o dashboard completo
                    window.location.href = 'dashboard.html';
                } else if (result.user.user_type === 'funcionario') {
                    // Funcionário vai para o dashboard limitado
                    window.location.href = 'employee-dashboard.html';
                } else {
                    // Fallback para o dashboard completo
                    window.location.href = 'dashboard.html';
                }
            } else {
                // Mostrar mensagem de erro específica
                if (result.message.includes('não encontrado') || result.message.includes('incorreta')) {
                    alert('CPF ou senha incorretos, tente novamente');
                } else {
                    alert('Erro no login: ' + result.message);
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro de conexão. Verifique se o servidor Python está rodando.');
        } finally {
            // Restaurar botão
            loginButton.disabled = false;
            loginButton.textContent = 'Entrar';
        }
    });
});
