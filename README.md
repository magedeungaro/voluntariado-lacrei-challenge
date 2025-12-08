# Lacrei Saúde API

API REST para gerenciamento de profissionais de saúde e consultas - Desafio Lacrei Saúde.

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
│   ├── profissionais/        # CRUD de profissionais de saúde
│   ├── consultas/            # Gerenciamento de consultas
│   ├── settings.py           # Configurações Django
│   ├── urls.py               # URLs principais
│   └── wsgi.py               # WSGI config
├── terraform/                # Infraestrutura como código
│   ├── provider.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── security.tf
│   ├── iam.tf
│   ├── ecr.tf
│   ├── rds.tf
│   ├── ec2.tf
│   └── outputs.tf
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml                # Lint, test, build
│   ├── cd.yml                # Deploy blue/green
│   └── terraform.yml         # Infra provisioning
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

## API Endpoints

### Documentação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI Schema |

### Profissionais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/professionals/` | Lista profissionais |
| POST | `/api/v1/professionals/` | Cria profissional |
| GET | `/api/v1/professionals/{uuid}/` | Detalhes do profissional |
| PUT | `/api/v1/professionals/{uuid}/` | Atualiza profissional |
| PATCH | `/api/v1/professionals/{uuid}/` | Atualiza parcialmente |
| DELETE | `/api/v1/professionals/{uuid}/` | Remove profissional |

### Consultas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/appointments/` | Lista consultas |
| POST | `/api/v1/appointments/` | Cria consulta |
| GET | `/api/v1/appointments/{uuid}/` | Detalhes da consulta |
| PUT | `/api/v1/appointments/{uuid}/` | Atualiza consulta |
| PATCH | `/api/v1/appointments/{uuid}/` | Atualiza parcialmente |
| DELETE | `/api/v1/appointments/{uuid}/` | Remove consulta |

### Autenticação (OAuth2)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/o/token/` | Obter access token |

## Autenticação

A API utiliza OAuth2 com client credentials flow. Para acessar os endpoints protegidos:

### 1. Criar aplicação OAuth2

```bash
# Acesse o Django Admin
open http://localhost:8000/admin/

# Crie um superuser (se ainda não existir)
make docker-exec
python manage.py createsuperuser

# No admin, vá em OAuth2 Provider > Applications e crie:
# - Client type: Confidential
# - Authorization grant type: Client credentials
```

### 2. Obter access token

```bash
curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### 3. Usar o token nas requisições

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/professionals/
```

## Deployment (AWS)

### Arquitetura

- **EC2**: Instância privada rodando Docker + nginx
- **RDS**: PostgreSQL 16 (instância privada)
- **ECR**: Registro de imagens Docker
- **SSM**: Acesso seguro sem portas públicas
- **Blue/Green**: Dois containers (8001/8002) com switch via nginx

### Provisionar Infraestrutura

```bash
cd terraform

# Copie e configure as variáveis
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com seus valores

# Inicialize Terraform
terraform init

# Planeje as mudanças
terraform plan

# Aplique (cria recursos)
terraform apply

# Para destruir após o demo
terraform destroy
```

### Deploy Manual

```bash
# 1. Build e push para ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ECR_URL>
docker build -t <ECR_URL>:latest .
docker push <ECR_URL>:latest

# 2. Deploy no slot blue
aws ssm send-command \
  --instance-ids "<INSTANCE_ID>" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo /usr/local/bin/deploy.sh blue latest"]'

# 3. Rodar migrações
aws ssm send-command \
  --instance-ids "<INSTANCE_ID>" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo /usr/local/bin/run-migrations.sh"]'

# 4. Switch traffic para blue
aws ssm send-command \
  --instance-ids "<INSTANCE_ID>" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo /usr/local/bin/switch-backend.sh blue"]'
```

### Acesso do Avaliador (SSM Port Forwarding)

```bash
# Instale AWS CLI e session-manager-plugin

# Configure as credenciais fornecidas
aws configure

# Inicie port forwarding
aws ssm start-session \
  --target <INSTANCE_ID> \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["80"],"localPortNumber":["8080"]}'

# Acesse em http://localhost:8080
```

## Segurança

- ✅ Sem portas públicas abertas (acesso via SSM)
- ✅ IMDSv2 obrigatório
- ✅ Secrets em variáveis de ambiente (nunca no código)
- ✅ Security groups restritivos
- ✅ VPC endpoints para SSM
- ✅ RDS em subnet privada
- ✅ Criptografia em trânsito e em repouso
- ✅ IAM com princípio de menor privilégio

## Licença

Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
