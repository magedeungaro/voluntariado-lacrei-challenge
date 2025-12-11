# Getting Started

## Stack Tecnológica

- **Backend**: Python 3.12 + Django 5.2 + Django REST Framework
- **Autenticação**: OAuth2 (django-oauth-toolkit)
- **Banco de dados**: PostgreSQL 16
- **Gerenciamento de dependências**: Poetry
- **Containerização**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Infraestrutura**: Terraform + AWS (EC2, RDS, ECR)
- **Deployment**: Blue/Green via nginx + SSM (sem portas públicas)

## Estrutura do Projeto

```
lacrei-2025-tl/
├── app/                      # Código Django
│   ├── core/                 # App principal (health check, etc.)
│   ├── professionals/        # CRUD de profissionais de saúde
│   ├── appointments/         # Gerenciamento de consultas
│   ├── settings.py           # Configurações Django
│   ├── urls.py               # URLs principais
│   └── wsgi.py               # WSGI config
├── terraform/                # Infraestrutura como código
│   ├── modules/              # Módulos reutilizáveis
│   │   └── lacrei-infra/     # Módulo principal de infraestrutura
│   ├── staging/              # Ambiente de staging
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── production/           # Ambiente de produção
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml                # Lint, test, build
│   ├── cd.yml                # Deploy produção (branch: release)
│   ├── cd-staging.yml        # Deploy staging (branch: staging)
│   ├── terraform-staging.yml # Infra staging
│   └── terraform-production.yml # Infra produção
├── Dockerfile
├── docker-compose.yml        # Dev environment
├── pyproject.toml            # Poetry config
└── Makefile                  # Comandos úteis
```

## Desenvolvimento Local

### Pré-requisitos

- Python 3.12+
- Poetry
- Docker e Docker Compose

### Setup

```bash
# Clone o repositório
git clone https://github.com/magedeungaro/voluntariado-lacrei-challenge.git
cd voluntariado-lacrei-challenge

# Instale as dependências
make install

# Copie o arquivo de ambiente
cp .env.example .env

# Instale o pre-commit hook (opcional, mas recomendado)
cp hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Inicie os containers (PostgreSQL + App)
make docker-up

# Rode as migrações
make docker-migrate

# Acesse a API
open http://localhost:8000/api/docs/
```

### Comandos Úteis

```bash
make help           # Lista todos os comandos
make dev            # Roda servidor de desenvolvimento
make test           # Roda testes com coverage
make lint           # Roda linters
make format         # Formata código
make docker-up      # Inicia containers
make docker-down    # Para containers
make docker-logs    # Ver logs dos containers
```
