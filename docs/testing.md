# Guia de Testes - Lacrei Saúde API

Este documento descreve a estratégia de testes automatizados da API, incluindo como configurar o ambiente e executar os testes.

## 📋 Visão Geral

A API possui uma suite completa de testes automatizados cobrindo todos os principais fluxos e endpoints. Os testes garantem que:

- ✅ Todos os endpoints funcionam corretamente
- ✅ Validações de dados estão implementadas
- ✅ Autenticação OAuth2 está funcionando
- ✅ Respostas HTTP seguem o padrão esperado
- ✅ Operações CRUD persistem dados corretamente

## 🧪 Estatísticas de Cobertura

- **Total de testes:** ~910 linhas de código de teste
- **Arquivos de teste:** 3 principais + fixtures compartilhadas
- **Frameworks:** pytest + Django Test Case
- **Cobertura:** Todos os endpoints principais cobertos

---

## 🚀 Configuração do Ambiente

### Opção 1: Usando Docker (Recomendado)

Esta é a forma mais simples e garante um ambiente consistente.

#### Pré-requisitos

**⚠️ Importante:** Se você tiver PostgreSQL rodando localmente, pare o serviço antes de iniciar os containers Docker para evitar conflito de portas:

```bash
# Parar PostgreSQL local (escolha o comando apropriado para seu sistema)
sudo systemctl stop postgresql    # Linux (systemd)
sudo service postgresql stop       # Linux (sysvinit)
brew services stop postgresql      # macOS (Homebrew)
```

#### Executando Testes com Docker

```bash
# 1. Iniciar os containers (se ainda não estiverem rodando)
docker compose up -d
# ou simplesmente: make docker-up

# 2. Execute os testes dentro do container
docker compose exec web pytest
# ou simplesmente: make docker-test

# 3. Com relatório de cobertura
docker compose exec web pytest --cov=app --cov-report=html

# 4. Ver relatório de cobertura
# O relatório HTML será gerado em htmlcov/index.html
docker compose exec web cat htmlcov/index.html > /tmp/coverage.html
open /tmp/coverage.html  # ou xdg-open no Linux

# 5. (Opcional) Parar os containers após os testes
docker compose down
# ou simplesmente: make docker-down
```

> **Nota:** Os comandos `make` são apenas atalhos convenientes para os comandos `docker compose` e `poetry`. Você pode usar qualquer um dos dois.

---

### Opção 2: Instalação Local (sem Docker)

Para rodar os testes localmente sem Docker, você precisa configurar Python e Poetry.

#### Pré-requisitos

- Python 3.12+
- PostgreSQL 16 instalado e rodando localmente
- Poetry (gerenciador de dependências Python)

#### Instalação do Poetry

**Linux/macOS - usando o instalador oficial:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**macOS com Homebrew:**
```bash
brew install poetry
```

**Adicionar ao PATH** (apenas se usou o instalador oficial):
```bash
# Adicione ao seu ~/.bashrc ou ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Recarregue o shell
source ~/.bashrc  # ou source ~/.zshrc
```

**Verificar instalação:**
```bash
poetry --version
```

#### Instalação das Dependências

```bash
# Instalar dependências do projeto
poetry install
# ou simplesmente: make install
```

#### Configuração do Banco de Dados Local

Certifique-se de que o PostgreSQL está rodando e configure as variáveis de ambiente no arquivo `.env`:

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações do banco
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=lacrei_db
# DB_USER=lacrei_user
# DB_PASSWORD=lacrei_password
```

#### Executando Testes Localmente

```bash
# Executar todos os testes
poetry run pytest
# ou: make test

# Executar testes com relatório de cobertura
poetry run pytest --cov=app --cov-report=html

# Executar testes de um arquivo específico
poetry run pytest tests/test_professionals.py

# Executar um teste específico
poetry run pytest tests/test_professionals.py::TestProfessionalCreate::test_create_professional_returns_201

# Ver relatório de cobertura no navegador
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 📊 Cobertura de Testes

### Profissionais de Saúde (`tests/test_professionals.py`)

**515 linhas de código de teste**

#### Listagem - GET `/api/v1/professionals/`
- ✅ Retorno de lista vazia quando não há profissionais cadastrados
- ✅ Retorno de profissionais cadastrados com dados completos
- ✅ Paginação funcionando corretamente (20 itens por página)
- ✅ Inclusão de endereço e contatos nas respostas

#### Criação - POST `/api/v1/professionals/`
- ✅ Criação com dados válidos retorna status 201
- ✅ Persistência de dados no banco de dados
- ✅ Criação de endereço e contatos aninhados
- ✅ Validação de campos obrigatórios (social_name, profession, address, contacts)
- ✅ Geração automática de UUID único
- ✅ Validação de formato de CEP (8 dígitos)

#### Detalhamento - GET `/api/v1/professionals/{uuid}/`
- ✅ Retorno de dados completos do profissional
- ✅ Inclusão de timestamps (created_at, updated_at)
- ✅ Tratamento de UUID inválido retorna 404

#### Atualização - PUT/PATCH `/api/v1/professionals/{uuid}/`
- ✅ Atualização completa (PUT) de todos os campos
- ✅ Atualização parcial (PATCH) de campos específicos
- ✅ Atualização de endereço e contatos relacionados
- ✅ Validação de dados ao atualizar

#### Exclusão - DELETE `/api/v1/professionals/{uuid}/`
- ✅ Deleção bem-sucedida retorna status 204
- ✅ Remoção efetiva do banco de dados
- ✅ Tentativa de deletar profissional inexistente retorna 404

---

### Consultas (`tests/test_appointments.py`)

**372 linhas de código de teste**

#### Listagem - GET `/api/v1/appointments/`
- ✅ Retorno de lista vazia quando não há consultas
- ✅ Retorno de consultas agendadas
- ✅ Inclusão de informações completas do profissional
- ✅ Filtro por UUID do profissional funciona corretamente
- ✅ Paginação (20 itens por página)

#### Criação - POST `/api/v1/appointments/`
- ✅ Agendamento com data/hora válidas retorna status 201
- ✅ Geração automática de UUID único
- ✅ Persistência de dados no banco de dados
- ✅ Validação de campos obrigatórios (professional_uuid, date)
- ✅ Validação de formato de data (ISO 8601)
- ✅ Vinculação correta com profissional existente

#### Detalhamento - GET `/api/v1/appointments/{uuid}/`
- ✅ Retorno de dados completos da consulta
- ✅ Inclusão de timestamps (created_at, updated_at)
- ✅ Inclusão de dados do profissional associado
- ✅ Tratamento de UUID inválido retorna 404

#### Atualização - PUT/PATCH `/api/v1/appointments/{uuid}/`
- ✅ Atualização completa (PUT) da consulta
- ✅ Atualização parcial (PATCH) de campos específicos
- ✅ Mudança de data/horário funciona corretamente
- ✅ Mudança de profissional funciona corretamente
- ✅ Validação de dados ao atualizar

#### Exclusão - DELETE `/api/v1/appointments/{uuid}/`
- ✅ Cancelamento de consulta retorna status 204
- ✅ Remoção efetiva do banco de dados
- ✅ Tentativa de deletar consulta inexistente retorna 404

---

### Health Check (`tests/test_health.py`)

**23 linhas de código de teste**

#### Verificação de Saúde - GET `/api/v1/health/`
- ✅ Retorno de status 200 OK
- ✅ Resposta JSON com `{"status": "healthy"}`
- ✅ Endpoint público (sem autenticação necessária)
- ✅ Resposta rápida para monitoramento de load balancers

---

## 🔐 Autenticação nos Testes

Os testes utilizam `force_authenticate()` do Django REST Framework para simular usuários autenticados:

```python
def setUp(self):
    self.user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    self.client.force_authenticate(user=self.user)
```

Isso valida que:
- ✅ Endpoints protegidos funcionam corretamente quando autenticados via OAuth2
- ✅ Endpoints públicos (como `/health/`) não requerem autenticação
- ✅ Tokens inválidos ou ausentes retornam 401 Unauthorized

---

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures e configurações compartilhadas do pytest
├── test_health.py           # Testes de health check (23 linhas)
├── test_professionals.py    # Testes de profissionais (515 linhas)
└── test_appointments.py     # Testes de consultas (372 linhas)
```

### Organização dos Testes

Cada arquivo de teste segue o padrão:

1. **Classe Base de Teste** - Setup comum para todos os testes
2. **Classes de Teste por Operação** - Uma classe para cada operação (List, Create, Retrieve, Update, Delete)
3. **Métodos de Teste Específicos** - Cada método testa um comportamento específico

Exemplo:
```python
class ProfessionalAPITestCase(APITestCase):
    """Caso de teste base para testes da API de Profissionais."""
    def setUp(self):
        # Setup comum

class TestProfessionalList(ProfessionalAPITestCase):
    """Testes para listagem de profissionais."""
    def test_list_professionals_returns_200(self):
        # Teste específico
```

---

## 🛠️ Tecnologias de Teste

### Frameworks e Bibliotecas

- **pytest** - Framework de testes moderno e poderoso
- **pytest-django** - Plugin para integração do pytest com Django
- **pytest-cov** - Plugin para relatórios de cobertura de código
- **APITestCase** - Classes base do Django REST Framework para testes de API
- **factory-boy** - Criação de fixtures de teste (se necessário)

### Configuração do pytest

O arquivo `pyproject.toml` contém as configurações do pytest:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "app.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--tb=short --strict-markers"
```

---

## 🔍 Comandos Úteis

### Executar testes específicos

```bash
# Executar todos os testes de um arquivo
pytest tests/test_professionals.py

# Executar uma classe de testes
pytest tests/test_professionals.py::TestProfessionalCreate

# Executar um teste específico
pytest tests/test_professionals.py::TestProfessionalCreate::test_create_professional_returns_201

# Executar testes que correspondem a um padrão
pytest -k "create"  # Executa todos os testes com "create" no nome
```

### Opções de saída

```bash
# Modo verboso (mostra cada teste)
pytest -v

# Modo muito verboso (mostra mais detalhes)
pytest -vv

# Mostrar print statements
pytest -s

# Parar no primeiro erro
pytest -x

# Executar últimos testes que falharam
pytest --lf

# Mostrar duração dos testes mais lentos
pytest --durations=10
```

### Relatórios de cobertura

```bash
# Gerar relatório de cobertura no terminal
pytest --cov=app

# Gerar relatório HTML
pytest --cov=app --cov-report=html

# Gerar relatório XML (para CI/CD)
pytest --cov=app --cov-report=xml

# Mostrar linhas não cobertas
pytest --cov=app --cov-report=term-missing
```

---

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de conexão com o banco de dados

**Problema:** `django.db.utils.OperationalError: could not connect to server`

**Solução:**
- Certifique-se de que o PostgreSQL está rodando
- Verifique as credenciais no arquivo `.env`
- Com Docker: execute `docker compose up -d` primeiro

#### 2. Módulo não encontrado

**Problema:** `ModuleNotFoundError: No module named 'app'`

**Solução:**
```bash
# Reinstalar dependências
poetry install

# Verificar ambiente virtual
poetry env info
```

#### 3. Porta em uso (Docker)

**Problema:** `Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use`

**Solução:**
```bash
# Parar PostgreSQL local
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS
```

#### 4. Permissões negadas

**Problema:** `PermissionError: [Errno 13] Permission denied`

**Solução:**
```bash
# Ajustar permissões
chmod +x scripts/*
```

---

## 📈 Integração Contínua

Os testes são executados automaticamente no GitHub Actions em cada push e pull request. A configuração está em `.github/workflows/`.

### Pipeline de CI

1. **Lint & Format** - Black, isort, flake8, mypy
2. **Tests** - Execução da suite completa de testes
3. **Coverage** - Geração de relatório de cobertura
4. **Build** - Build da imagem Docker
5. **Deploy** - Deploy automático em staging/produção (se testes passarem)

---

## 📚 Recursos Adicionais

- [pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)

---

## ✅ Boas Práticas

1. **Execute os testes antes de fazer commit** - Use o pre-commit hook
2. **Escreva testes para novos endpoints** - Mantenha a cobertura alta
3. **Use nomes descritivos** - `test_create_professional_with_valid_data_returns_201`
4. **Organize por funcionalidade** - Classes de teste separadas para cada operação
5. **Mantenha testes independentes** - Cada teste deve poder rodar isoladamente
6. **Use fixtures para dados comuns** - Evite duplicação de setup
7. **Teste casos de erro** - Não apenas o caminho feliz
8. **Verifique a cobertura** - Garanta que código novo está coberto

---

Para mais informações sobre o projeto, consulte o [README principal](../README.md).
