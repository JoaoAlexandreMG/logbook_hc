# Logbook HC-UFU

Sistema web para registro e validação de procedimentos clínicos de residentes, com fluxo de supervisão por preceptores, emissão de relatório e trilha formativa baseada na metodologia HEIPOC (FAMED/UFU).

> Contexto: projeto acadêmico de iniciação científica com foco em continuidade por outro aluno.

---

## 1) Objetivo do projeto

Centralizar o acompanhamento da formação prática de residentes por meio de:

- registro estruturado de procedimentos;
- validação por preceptores;
- histórico auditável por status (Pendente, Validado, Rejeitado);
- emissão de relatório consolidado por residente;
- comunicação por e-mail após avaliação do procedimento.

---

## 2) Escopo funcional atual

### Perfis suportados

- **Residente**
  - registra procedimentos clínicos;
  - acompanha status e feedback do preceptor;
  - gera seu relatório (com restrição de acesso ao próprio ID).
- **Preceptor**
  - avalia procedimentos recebidos;
  - valida ou rejeita com observação opcional;
  - acompanha residentes supervisionados via procedimentos.

### Funcionalidades principais

1. Autenticação (login/logout) para residente e preceptor.
2. Verificação prévia de CRM em API externa (CFM) no cadastro.
3. Cadastro de residente e preceptor após CRM válido.
4. Dashboard de residente para envio de novos procedimentos.
5. Dashboard de preceptor para avaliação dos pendentes.
6. Notificação por e-mail no ato da avaliação.
7. Geração de relatório por residente:
   - PDF (quando WeasyPrint está disponível);
   - fallback para HTML em caso de indisponibilidade.

---

## 3) Stack e dependências

### Linguagem e framework

- Python
- Flask

### Bibliotecas principais (requirements.txt)

- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Mail
- WTForms
- wtforms_sqlalchemy
- requests
- weasyprint
- pytz
- Werkzeug
- python-dotenv

---

## 4) Arquitetura da aplicação

### Visão geral

Aplicação Flask no padrão **Application Factory**, com:

- extensões inicializadas em `app/__init__.py`;
- configuração central em `config.py`;
- rotas no blueprint `main_bp` em `app/routes.py`;
- modelos em `app/models.py`;
- formulários em `app/forms.py`;
- envio de e-mail em `app/email.py`.

### Banco de dados

- SGBD: **SQLite**
- arquivo: `residentes.db` na **raiz do repositório**.
- a criação de tabelas ocorre automaticamente caso tabelas esperadas não existam.

---

## 5) Estrutura de diretórios

```text
logbook_hc/
├── app/
│   ├── __init__.py
│   ├── email.py
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── login.html
│       ├── verificar_crm.html
│       ├── selecionar_perfil.html
│       ├── registrar.html
│       ├── registrar_preceptor.html
│       ├── dashboard_residente.html
│       ├── dashboard_preceptor.html
│       ├── modais_preceptor.html
│       └── relatorio_template.html
├── config.py
├── requirements.txt
└── run.py
```

---

## 6) Modelo de dados (entidades)

### `Residente`

- dados pessoais e de autenticação;
- vínculo com universidade, hospital, especialidade e supervisor (preceptor);
- relacionamento com vários procedimentos.

### `Preceptor`

- dados pessoais e de autenticação;
- vínculo com universidade, hospital e especialidade;
- relacionamento com procedimentos a validar.

### `Procedimento`

- identificação do procedimento e data;
- campos HEIPOC:
  - H: história clínica
  - E: exame físico
  - I: interpretação/diagnósticos diferenciais
  - P: plano terapêutico
  - O: orientação ao paciente
  - C: conhecimento/aprendizagem
- status (`Pendente`, `Validado`, `Rejeitado`);
- observação do preceptor;
- vínculo com residente e preceptor.

### Cadastros auxiliares

- `Universidade`
- `Hospital`
- `Especialidade`

> Observação importante: o fluxo de cadastro depende da existência desses registros no banco.

---

## 7) Fluxos de negócio

### 7.1 Cadastro (residente/preceptor)

1. usuário acessa `/verificar-crm`;
2. CRM é validado na API externa;
3. CRM regular é salvo em sessão (`crm_verificado`);
4. usuário escolhe perfil em `/selecionar-perfil`;
5. finaliza cadastro em `/registrar` ou `/registrar-preceptor`.

### 7.2 Registro e avaliação de procedimento

1. residente cria procedimento no dashboard;
2. procedimento entra como `Pendente`;
3. preceptor avalia (valida/rejeita);
4. sistema registra observação;
5. sistema envia e-mail ao residente com resultado.

### 7.3 Relatório

1. usuário autorizado solicita `/relatorio/residente/<id>`;
2. sistema consolida estatísticas e procedimentos validados;
3. gera PDF com WeasyPrint (ou HTML de fallback).

---

## 8) Rotas principais

- `/` → redireciona para login
- `/login` → autenticação
- `/logout` → encerramento de sessão
- `/home` → redirecionamento por perfil
- `/dashboard/residente` → registro e histórico do residente
- `/dashboard/preceptor` → avaliação pelo preceptor
- `/relatorio/residente/<int:residente_id>` → relatório por residente
- `/verificar-crm` → etapa 1 do cadastro
- `/selecionar-perfil` → etapa 2 do cadastro
- `/registrar` → cadastro de residente
- `/registrar-preceptor` → cadastro de preceptor

---

## 9) Configuração de ambiente

## 9.1 Pré-requisitos

- Python 3.10+ (recomendado)
- pip

> Para PDF com WeasyPrint, pode ser necessário instalar bibliotecas de sistema adicionais conforme o SO.

## 9.2 Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## 9.3 Variáveis de ambiente (`.env`)

Criar arquivo `.env` na raiz:

```env
SECRET_KEY=sua_chave_secreta

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu_email
MAIL_PASSWORD=sua_senha_ou_app_password
MAIL_DEFAULT_SENDER=noreply@logbook-residente.com
```

### Observações

- sem variáveis de e-mail válidas, o envio de notificação pode falhar;
- existe chave secreta padrão no código, mas em produção é obrigatório sobrescrever.

---

## 10) Execução

```bash
python run.py
```

Aplicação sobe em:

- `http://localhost:5000`

---

## 11) Operação inicial recomendada

1. Subir aplicação.
2. Confirmar criação de `residentes.db`.
3. Garantir existência de registros em:
   - universidade;
   - hospital;
   - especialidade;
   - ao menos um preceptor (para seleção de supervisor no cadastro de residente).
4. Executar um cadastro completo (CRM + registro).
5. Registrar e avaliar um procedimento de ponta a ponta.
6. Testar geração de relatório.
7. Validar disparo de e-mail.

---

## 12) Segurança e boas práticas

- Nunca versionar `.env` (já ignorado no `.gitignore`).
- Definir `SECRET_KEY` forte fora do código.
- Usar credenciais de e-mail dedicadas (idealmente com app password).
- Em produção:
  - desativar `debug=True`;
  - usar WSGI server (gunicorn/uwsgi);
  - configurar proxy reverso e HTTPS.

---

## 13) Limitações técnicas conhecidas

- Dependência de API externa para verificação de CRM.
- Banco SQLite (adequado para desenvolvimento/piloto, limitado para alta concorrência).
- Ausência de migrações versionadas (create_all cria tabela, mas não faz evolução controlada de schema).
- Não há suíte de testes automatizados no estado atual.

---

## 14) Troubleshooting

### Erro ao enviar e-mail

- conferir `MAIL_USERNAME`/`MAIL_PASSWORD`;
- conferir TLS/porta SMTP;
- validar bloqueios do provedor de e-mail.

### CRM não valida

- verificar disponibilidade da API do CFM;
- conferir timeout/conectividade;
- confirmar UF e número informados.

### PDF não gera

- validar instalação completa do WeasyPrint e dependências do sistema;
- em falha, sistema retorna relatório em HTML.

### Erro de cadastro por instituição/hospital

- confirmar existência de registros de universidade/hospital no banco.

---

## 15) Guia de continuidade (handover)

Para o próximo aluno:

1. **Mapear regra de negócio com orientador/preceptoria**
   - confirmar critérios de validação e campos obrigatórios.
2. **Formalizar estratégia de dados**
   - decidir se manter SQLite ou migrar para PostgreSQL.
3. **Adicionar migrações**
   - introduzir Flask-Migrate/Alembic para evolução segura de schema.
4. **Criar seed inicial**
   - popular universidade/hospital/especialidades/preceptores padrão.
5. **Cobertura de testes**
   - priorizar autenticação, cadastro, avaliação e relatório.
6. **Observabilidade**
   - logs estruturados para erros de integração (CRM/e-mail/PDF).
7. **Endurecimento para produção**
   - debug off, gestão de secrets, backup e monitoramento.

---

## 16) Sugestão de roadmap

- Curto prazo:
  - seed de dados iniciais;
  - validações adicionais de formulário;
  - testes de fluxo crítico.
- Médio prazo:
  - migração para banco relacional robusto;
  - trilha de auditoria mais detalhada;
  - painéis e métricas por especialidade/preceptor.
- Longo prazo:
  - integração com sistemas institucionais;
  - gestão de permissões avançada;
  - API externa para interoperabilidade.

---

## 17) Licença e créditos

Definir política de licença com orientador e instituição (ainda não especificada no repositório).

Projeto desenvolvido no contexto de iniciação científica para suporte à residência médica no HC-UFU.
