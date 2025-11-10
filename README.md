# Tech Titans - Sistema de Estoque

Sistema completo de estoque desenvolvido com HTML, CSS, JavaScript e Python.

## Estrutura do Projeto

```
Tech Titans estoque/
├── front/                 # Frontend (HTML, CSS, JavaScript)
│   ├── index.html        # Página principal de login
│   ├── styles.css        # Estilos CSS
│   └── script.js         # Validações e lógica JavaScript
├── back/                 # Backend (Python Flask)
│   ├── app.py           # Servidor Flask
│   ├── requirements.txt # Dependências Python
│   └── README.md        # Documentação do backend
└── README.md            # Este arquivo
```

## Como Executar

### 1. Backend (Python)
```bash
cd back
pip install -r requirements.txt
python app.py
```

### 2. Frontend (HTML/CSS/JS)
Abra o arquivo `front/index.html` no seu navegador ou use um servidor local.

## Funcionalidades

### Tela de Login
- ✅ Validação de CPF (11 números obrigatórios)
- ✅ Validação de senha (maiúsculas, minúsculas, números e caracteres especiais)
- ✅ Formatação automática do CPF
- ✅ Design moderno e responsivo
- ✅ Integração com backend Python

### Backend
- ✅ API REST com Flask
- ✅ Validações de segurança
- ✅ Hash de senhas
- ✅ CORS habilitado para frontend
- ✅ Usuário de teste incluído

## Usuário de Teste

- **CPF:** 123.456.789-01
- **Senha:** Senha123!

## Tecnologias Utilizadas

- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Backend:** Python 3, Flask, Flask-CORS
- **Validações:** Regex, JavaScript, Python
