# 📋 Logbook do Residente - Sistema HEIPOC

Sistema web para registro e validação de procedimentos médicos seguindo a metodologia HEIPOC oficial da FAMED UFU.

## 🏥 Sobre o Sistema

O **Logbook do Residente** é uma aplicação desenvolvida para facilitar o registro detalhado de procedimentos médicos por residentes e sua posterior validação por preceptores, seguindo rigorosamente a metodologia **HEIPOC** (História clínica, Exame físico, Interpretação/diagnósticos, Plano terapêutico, Orientação ao paciente, Conhecimento adquirido).

## 🎯 Metodologia HEIPOC

O sistema implementa os 6 campos obrigatórios da metodologia oficial:

- **H** - História Clínica
- **E** - Exame Físico  
- **I** - Interpretação e Diagnósticos
- **P** - Plano Terapêutico
- **O** - Orientação ao Paciente
- **C** - Conhecimento e Aprendizagem

## ⚡ Funcionalidades

### 👨‍⚕️ Para Residentes:
- ✅ Registro estruturado de procedimentos usando metodologia HEIPOC
- ✅ Validação de campos obrigatórios com tamanhos mínimos
- ✅ Visualização do histórico de procedimentos
- ✅ Status de validação em tempo real
- ✅ Interface intuitiva com accordion organizado

### 👩‍⚕️ Para Preceptores:
- ✅ Avaliação detalhada de procedimentos pendentes
- ✅ Visualização completa da metodologia HEIPOC
- ✅ Sistema de validação/rejeição com observações
- ✅ Histórico de procedimentos avaliados
- ✅ Geração de relatórios em PDF

### 🔐 Sistema de Autenticação:
- ✅ Login seguro para residentes e preceptores
- ✅ Verificação de CRM para preceptores
- ✅ Cadastro de novos usuários
- ✅ Controle de acesso baseado em perfis

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Database:** SQLAlchemy + SQLite
- **Frontend:** Bootstrap 5 + JavaScript
- **Forms:** WTForms + Flask-WTF
- **Authentication:** Flask-Login
- **PDF Generation:** WeasyPrint
- **Email:** Flask-Mail
- **Environment:** python-dotenv

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Git

### Passos para instalação:

1. **Clone o repositório:**
```bash
git clone [URL_DO_REPOSITORIO]
cd "LOGBOOK DO RESIDENTE"
```

2. **Crie e ative o ambiente virtual:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua_chave_secreta_aqui
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

5. **Execute a aplicação:**
```bash
python run.py
```

6. **Acesse o sistema:**
Abra o navegador em `http://localhost:5000`

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais:
- **Residente:** Dados dos residentes
- **Preceptor:** Dados dos preceptores  
- **Procedimento:** Registros HEIPOC dos procedimentos

### Campos HEIPOC no Procedimento:
- `historia_clinica` (TEXT, obrigatório)
- `exame_fisico` (TEXT, obrigatório)
- `interpretacao_diagnostico` (TEXT, obrigatório)
- `plano_terapeutico` (TEXT, obrigatório)
- `orientacao_paciente` (TEXT, obrigatório)
- `conhecimento_aprendizagem` (TEXT, obrigatório)

## 🎨 Interface

### Design System:
- **Framework:** Bootstrap 5
- **Ícones:** Bootstrap Icons
- **Cores:** Paleta médica profissional (#003366)
- **Componentes:** Accordion, Modals, Cards, Tables
- **Responsividade:** Mobile-first design

### Validação Frontend:
- **Campos obrigatórios:** Validação em tempo real
- **Tamanhos mínimos:** História (10 chars), outros campos (10+ chars)
- **Feedback visual:** Mensagens de erro em português
- **UX otimizada:** Foco automático em campos com erro

## 📊 Relatórios

### Geração de PDF:
- **Metodologia HEIPOC** completa formatada
- **Dados do residente** e preceptor
- **Status de validação** com timestamp
- **Layout profissional** para impressão

## 🔒 Segurança

- ✅ **Hash de senhas** com Werkzeug
- ✅ **CSRF Protection** com Flask-WTF  
- ✅ **Session Management** com Flask-Login
- ✅ **Validação de entrada** em todos os formulários
- ✅ **Controle de acesso** baseado em roles

## 🚀 Deploy

### Variáveis de Ambiente Necessárias:
```env
SECRET_KEY=chave_secreta_producao
MAIL_SERVER=servidor_smtp
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=email_sistema
MAIL_PASSWORD=senha_app
```

## 🤝 Contribuição

Este projeto segue a metodologia oficial da **FAMED UFU**. Para contribuições:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de uso acadêmico e segue as diretrizes da FAMED UFU.

## 📞 Suporte

Para suporte técnico ou dúvidas sobre a metodologia HEIPOC, entre em contato com a coordenação da residência.

---

**Desenvolvido com ❤️ para a educação médica brasileira**
