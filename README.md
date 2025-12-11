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

- **EC2**: Instância privada rodando Docker + nginx (uma por ambiente)
- **RDS**: PostgreSQL 16 (instância privada por ambiente)
- **ECR**: Registro de imagens Docker (um por ambiente)
- **SSM**: Acesso seguro sem portas públicas
- **Blue/Green**: Dois containers (8001/8002) com switch via nginx

### Ambientes

| Ambiente | Branch | Terraform | Workflow |
|----------|--------|-----------|----------|
| Staging | `staging` | `terraform/staging/` | `cd-staging.yml` |
| Production | `release` | `terraform/production/` | `cd.yml` |

### Provisionar Infraestrutura

```bash
# Para STAGING:
cd terraform/staging
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com seus valores

terraform init
terraform plan
terraform apply

# Anote o ec2_instance_id e adicione ao GitHub Secrets como EC2_INSTANCE_ID_STAGING

# Para PRODUCTION:
cd terraform/production
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com seus valores

terraform init
terraform plan
terraform apply

# Anote o ec2_instance_id e adicione ao GitHub Secrets como EC2_INSTANCE_ID
```

### GitHub Secrets Necessários

| Secret | Descrição |
|--------|-----------|
| `AWS_ACCESS_KEY_ID` | Credencial AWS para deploy |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS para deploy |
| `EC2_INSTANCE_ID_STAGING` | ID da instância EC2 de staging (output do Terraform) |
| `EC2_INSTANCE_ID` | ID da instância EC2 de produção (output do Terraform) |
| `DB_PASSWORD_STAGING` | Senha do banco de staging |
| `DB_PASSWORD` | Senha do banco de produção |
| `DJANGO_SECRET_KEY_STAGING` | Secret key Django para staging |
| `DJANGO_SECRET_KEY` | Secret key Django para produção |

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

### Acesso à API

**⚠️ Nota sobre Arquitetura de Rede:**

A API está implantada em uma **instância EC2 com IP público** para facilitar a avaliação do desafio. Em um ambiente de produção real, a arquitetura recomendada seria:

- **Application Load Balancer (ALB)** na camada pública
- **Instâncias EC2 em subnets privadas** (sem IPs públicos)
- **Acesso via ALB com SSL/TLS** (HTTPS)
- **WAF (Web Application Firewall)** para proteção adicional

Esta simplificação foi adotada por **razões de custo** (~$20-25/mês para ALB + certificado SSL), mas a infraestrutura está preparada para migração para ALB quando necessário (basta descomentar o módulo ALB no Terraform).

**URL da API em produção:**
```
http://3.239.228.179/api/v1/
```

⚠️ **HTTP only**: HTTPS requer domínio próprio, não implementado para manter foco em infraestrutura/CI/CD.

**Endpoints disponíveis:**
- `GET /api/v1/health/` - Health check
- `GET /api/v1/professionals/` - Lista profissionais
- `POST /api/v1/professionals/` - Cria profissional
- `GET /api/v1/appointments/` - Lista consultas
- `POST /api/v1/appointments/` - Cria consulta

**⚠️ Nota sobre CORS:**

A API está configurada com `CORS_ALLOW_ALL_ORIGINS=true` para facilitar testes e avaliação. Em um ambiente de produção real:

- **APIs REST públicas** geralmente permitem qualquer origem, pois a segurança vem da autenticação (OAuth2/JWT), não de restrições CORS
- **Restrições de origem** são úteis quando você tem um frontend específico (ex: `https://app.lacrei.com`) e quer impedir que outros sites façam requisições do browser do usuário

A proteção da API é garantida pela **autenticação OAuth2** implementada via `django-oauth-toolkit`.

## Segurança

### Infraestrutura
- ✅ IMDSv2 obrigatório
- ✅ Secrets em variáveis de ambiente (nunca no código)
- ✅ Security groups restritivos
- ✅ VPC endpoints para SSM
- ✅ RDS em subnet privada
- ✅ Criptografia em trânsito e em repouso
- ✅ IAM com princípio de menor privilégio

### API
- ✅ **Autenticação OAuth2 obrigatória** via django-oauth-toolkit (todos os endpoints requerem token)
- ✅ **Rate Limiting**: 300 requisições por segundo por usuário autenticado
- ✅ **CORS configurado** (allow all origins para APIs públicas)
- ✅ **Validação de dados** via Django REST Framework serializers

## Estratégia de Deploy: Blue/Green Simplificado

### Contexto do Desafio

Este projeto implementa uma estratégia **Blue/Green deployment** simplificada, adequada para demonstrar conhecimentos de CI/CD e deploy seguro dentro do contexto de um desafio técnico.

### Arquitetura Implementada (Simplificada)

```
┌─────────────────────────────────────────────────────┐
│                    EC2 Instance                      │
│  ┌───────────────────────────────────────────────┐  │
│  │                   Nginx                        │  │
│  │            (reverse proxy/switch)              │  │
│  └───────────────┬───────────────┬───────────────┘  │
│                  │               │                   │
│         ┌────────▼────┐   ┌─────▼───────┐          │
│         │ Container   │   │ Container   │          │
│         │   BLUE      │   │   GREEN     │          │
│         │  :8001      │   │   :8002     │          │
│         └─────────────┘   └─────────────┘          │
└─────────────────────────────────────────────────────┘
```

**Características:**
- Uma única instância EC2 rodando dois containers Docker
- Nginx alterna o tráfego entre blue (porta 8001) e green (porta 8002)
- Deploy acontece no slot inativo, depois o tráfego é alternado
- Rollback instantâneo: basta alternar de volta para o slot anterior

### Arquitetura Real (Produção em Escala)

Em uma aplicação real de produção, a arquitetura seria significativamente diferente:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Application Load Balancer                     │
│                    (ALB com Health Checks)                        │
└─────────────────────────┬────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌──────────▼─────────┐
│   Target Group    │         │    Target Group    │
│      BLUE         │         │       GREEN        │
├───────────────────┤         ├────────────────────┤
│ ┌───┐ ┌───┐ ┌───┐│         │ ┌───┐ ┌───┐ ┌───┐ │
│ │EC2│ │EC2│ │EC2││         │ │EC2│ │EC2│ │EC2│ │
│ └───┘ └───┘ └───┘│         │ └───┘ └───┘ └───┘ │
│    (ou ECS/EKS)  │         │    (ou ECS/EKS)   │
└──────────────────┘         └────────────────────┘
```

**Diferenças principais:**

| Aspecto | Este Projeto | Produção Real |
|---------|--------------|---------------|
| **Instâncias** | 1 EC2 com 2 containers | Múltiplas instâncias por ambiente |
| **Load Balancer** | Nginx local | ALB/NLB da AWS |
| **Auto Scaling** | Não | Sim, baseado em métricas |
| **Target Groups** | N/A | Blue e Green separados |
| **Switch de tráfego** | Script local no nginx | ALB listener rules |
| **Health checks** | Simples (curl) | ALB health checks + CloudWatch |
| **Rollback** | Manual via script | Automático via ALB |
| **Custo** | ~$15-30/mês | $200-1000+/mês |

### Por que esta abordagem?

1. **Custo**: Para um desafio técnico, manter múltiplas instâncias 24/7 seria desnecessário
2. **Demonstração**: Os conceitos de blue/green ficam claros mesmo na versão simplificada
3. **Funcionalidade**: O mecanismo de deploy seguro funciona da mesma forma
4. **Escalabilidade conceitual**: A migração para ALB + Auto Scaling é direta

### Fluxo de Branches e Deploy

```
develop (local) ──► staging (branch) ──► release (branch)
                          │                     │
                          ▼                     ▼
                    Deploy Staging        Deploy Produção
                    (automático)          (automático)
```

- **develop**: Desenvolvimento local, sem deploy automático
- **staging**: Push nesta branch dispara deploy no ambiente de staging
- **release**: Push nesta branch dispara deploy em produção

### Evolução para Produção

Para escalar esta arquitetura para produção real, seria necessário considerar:

1. **Criar ALB** com dois Target Groups (blue/green)
2. **Configurar Auto Scaling Groups** para cada Target Group
3. **Atualizar workflows** para usar AWS CodeDeploy ou alternar ALB listeners
4. **Adicionar CloudWatch Alarms** para rollback automático
5. **Implementar canary deployments** (opcional) - tráfego gradual 10% → 50% → 100%

#### Fase 2: Alta Escala (Kubernetes)
Para workloads de alta demanda, considerar migrar para **Amazon EKS** (Kubernetes):

```
┌─────────────────────────────────────────────────────────────────┐
│                        Amazon EKS Cluster                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Ingress Controller                       │ │
│  │                  (ALB Ingress / Nginx)                      │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │                      Service                                │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────┬───────────┬───┴────┬───────────┬──────────┐      │
│  │  Pod     │   Pod     │  Pod   │   Pod     │   Pod    │      │
│  │ (app)   │  (app)   │ (app)  │  (app)   │  (app)   │      │
│  └──────────┴───────────┴────────┴───────────┴──────────┘      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  HPA (Horizontal Pod Autoscaler) - escala baseado em CPU    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Licença

Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
