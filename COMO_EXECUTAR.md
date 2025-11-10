# 🚀 Como Executar o Sistema Tech Titans

## ⚠️ IMPORTANTE: Execute os passos nesta ordem!

### 1️⃣ **PASSO 1: Iniciar o Backend (Python)**
Abra um terminal/PowerShell e execute:

```bash
# Navegar para a pasta back
cd "C:\Users\kaual\OneDrive\Documentos\Tech Titans estoque\back"

# Instalar dependências (só precisa fazer uma vez)
pip install -r requirements.txt

# Iniciar o servidor
python app.py
```

**✅ Quando funcionar, você verá:**
```
🚀 Iniciando servidor Tech Titans...
📱 Frontend: http://localhost:3000 (ou abra o index.html)
🔧 Backend: http://localhost:5000
💡 Usuário de teste: CPF: 123.456.789-01, Senha: Senha123!
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### 2️⃣ **PASSO 2: Abrir o Frontend**
1. Abra o arquivo `front/index.html` no seu navegador
2. Ou navegue até: `C:\Users\kaual\OneDrive\Documentos\Tech Titans estoque\front\index.html`

### 3️⃣ **PASSO 3: Fazer Login**
Use as credenciais de teste:
- **CPF:** 123.456.789-01
- **Senha:** Senha123!

## 🔧 **Se der erro:**

### Erro: "Erro de conexão"
- ✅ Verifique se o servidor Python está rodando (Passo 1)
- ✅ Mantenha o terminal do Python aberto
- ✅ O servidor deve estar rodando na porta 5000

### Erro: "Módulo não encontrado"
- ✅ Execute: `pip install -r requirements.txt` na pasta back

### Erro: "Python não encontrado"
- ✅ Instale Python 3.11+ do site oficial

## 📱 **Funcionalidades do Sistema:**

### Tela de Login:
- ✅ Validação de CPF (11 números)
- ✅ Validação de senha (maiúsculas, minúsculas, números, especiais)
- ✅ Formatação automática do CPF

### Tela 2 (Dashboard):
- ✅ Mensagem "BEM VINDO!"
- ✅ Botões de empresas (máximo 3)
- ✅ Editar nome da empresa (ícone de lápis)
- ✅ Adicionar empresas (botão +)

## 🆘 **Precisa de Ajuda?**
Se ainda não funcionar, me avise qual erro específico está aparecendo!
