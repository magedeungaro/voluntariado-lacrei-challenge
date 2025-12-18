# Lacrei Saúde API

API REST para gerenciamento de profissionais de saúde e consultas - Desafio Lacrei Saúde.

## � Escopo Funcional

Esta API oferece um sistema completo para cadastro e gerenciamento de:

- **Profissionais de Saúde** - CRUD completo incluindo nome social, profissão, endereço e múltiplos contatos (email, telefone, WhatsApp)
- **Consultas** - Agendamento e gerenciamento de consultas vinculadas a profissionais de saúde
- **Autenticação OAuth2** - Client Credentials Flow para acesso seguro aos endpoints protegidos
- **Health Check** - Endpoint público para monitoramento de disponibilidade da API

**Recursos principais:**
- Paginação automática em listagens
- Validação robusta de dados
- Relacionamentos entre entidades (consultas → profissionais)
- Filtros por parâmetros (ex: consultas por profissional)
- Timestamps automáticos (created_at, updated_at)
- Identificadores UUID para segurança

## 🚀 Quick Start

```bash
# Clone e configure
git clone https://github.com/magedeungaro/voluntariado-lacrei-challenge.git
cd voluntariado-lacrei-challenge
make install
cp .env.example .env

# Inicie o ambiente
make docker-up
make docker-migrate

# Acesse a API
open http://localhost:8000/api/docs/
```

## 📚 Documentação

- **[Começando](docs/getting-started.md)** - Setup, stack tecnológica, estrutura do projeto
- **[Referência da API](docs/api-reference.md)** - ⭐ Documentação completa dos endpoints com exemplos
- **[Testes](docs/testing.md)** - Guia completo de testes automatizados
- **[Segurança & Autenticação](docs/security.md)** - OAuth2, rotas protegidas, boas práticas
- **[Decisões Técnicas](docs/technical-decisions-and-limitations.md)** - Arquitetura, trade-offs e limitações conhecidas
- **[Deploy](docs/deployment.md)** - AWS, blue/green, HTTPS/SSL

## 🌐 Ambientes

| Ambiente | URL | Branch |
|----------|-----|--------|
| Produção | `https://api.magenifica.dev` | `release` |
| Staging | `https://api-stg.magenifica.dev` | `staging` |

> **Nota:** Ambos os ambientes utilizam certificados SSL válidos (ZeroSSL) com HTTPS habilitado.

## � Documentação da API

### Referência Completa dos Endpoints

📘 **[Documentação Completa da API](docs/api-reference.md)**

Documentação detalhada de todos os endpoints incluindo:
- ✅ Rotas, métodos HTTP e finalidade de cada endpoint
- ✅ Exemplos completos de request e response
- ✅ Status HTTP esperados e códigos de erro
- ✅ Parâmetros de path, query e body
- ✅ Autenticação OAuth2

### Swagger UI (Documentação Interativa)

🌐 **Interface Interativa:** `https://api.magenifica.dev/api/docs/`

Teste os endpoints diretamente no navegador com a interface Swagger UI.

### OpenAPI Schema

📄 **[Schema YAML](docs/schema.yaml)** | **[Schema JSON](https://api.magenifica.dev/api/schema/)**

Schema completo em formato OpenAPI 3.0 para:
- Importar em Postman/Insomnia
- Gerar SDKs/clientes automaticamente
- Validar requisições e respostas

### Postman Collection

📦 **[Postman Collection](docs/postman_collection.json)**

Collection com todos os endpoints configurados, incluindo:
- Autenticação OAuth2 automática
- Variáveis de ambiente (produção/staging)
- Exemplos de todas as operações CRUD
- Testes automatizados

### Quick Test

```bash
# Health check (público)
curl https://api.magenifica.dev/api/v1/health/

# Obter token OAuth2
curl -X POST https://api.magenifica.dev/oauth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Listar profissionais (com token)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```

## 🛠️ Stack

Python 3.12 • Django 5.2 • DRF • PostgreSQL 16 • Docker • AWS (EC2, RDS, ECR, S3) • Terraform • GitHub Actions

## 🧪 Testes Automatizados

A API possui uma suite completa de testes automatizados cobrindo todos os principais fluxos e endpoints.

### Quick Test

```bash
# Com Docker
docker compose up -d
docker compose exec web pytest

# Localmente (requer Poetry instalado)
poetry run pytest
```

### Cobertura

- ✅ **Profissionais de Saúde** - CRUD completo, validações, relacionamentos
- ✅ **Consultas** - CRUD completo, vinculação com profissionais
- ✅ **Health Check** - Endpoint público de monitoramento
- ✅ **Autenticação** - OAuth2 nos endpoints protegidos

**📘 Para instruções completas de configuração, execução e troubleshooting, consulte o [Guia de Testes](docs/testing.md).**

## 🔧 Desenvolvimento

### Git Hooks

O projeto inclui dois hooks para automação de qualidade e deploy:

#### Pre-Commit Hook (Qualidade de Código)

Executa verificações automáticas antes de cada commit:

```bash
# Instalar o hook pre-commit
cp hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Este hook executa:
- **Black**: Verificação de formatação de código
- **isort**: Verificação de ordenação de imports
- **Flake8**: Análise de estilo de código
- **MyPy**: Verificação de tipos estáticos

#### Pre-Push Hook (Atualização de Scripts)

Envia automaticamente scripts modificados para S3 antes de cada push:

```bash
# Instalar o hook pre-push
cp hooks/pre-push.sample .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

Este hook:
- Detecta mudanças em scripts em `terraform/modules/lacrei-infra/scripts/`
- Automaticamente envia para o bucket S3 apropriado (staging ou produção)
- Executa antes de `git push` apenas nas branches `staging` e `main`
- Pode ser ignorado com `git push --no-verify` se necessário

### Arquitetura User Data do EC2

A infraestrutura usa uma abordagem modular para inicialização das instâncias EC2:

1. **Script Bootstrap** (`bootstrap.sh`) - Script mínimo enviado via Terraform
   - Baixa scripts modulares do S3
   - Executa em ordem
   - Permanece sob o limite de 16KB do user_data da AWS

2. **Scripts Modulares** (armazenados no S3):
   - `00-init.sh` - Configuração de logs e inicialização
   - `01-ssm-agent.sh` - Configuração do agente SSM
   - `02-system-packages.sh` - Instalação de Docker, nginx, certbot, cronie
   - `03-app-setup.sh` - Configuração de diretório da aplicação e arquivo de ambiente
   - `04-nginx-config.sh` - Configuração do proxy reverso Nginx com SSL
   - `05-install-tools.sh` - Instalação de scripts operacionais (deploy, switch-backend, migrations, backup)
   - `06-ssl-certificates.sh` - Gerenciamento de certificados SSL (certificados manuais do S3 ou Let's Encrypt)
   - `99-finalize.sh` - Verificações finais e logs

Esta arquitetura permite:
- Atualizações fáceis de scripts sem mudanças no Terraform (via hook pre-push)
- Contornar limites de tamanho do user_data da AWS (16KB)
- Melhor organização e manutenibilidade
- Desenvolvimento e testes independentes de scripts
- Configuração específica por ambiente através de substituição de variáveis template

### Scripts Operacionais

Os seguintes scripts estão disponíveis nas instâncias EC2 para operações manuais:

- `/usr/local/bin/deploy.sh <blue|green> [image-tag]` - Deploy da aplicação no slot blue ou green
- `/usr/local/bin/switch-backend.sh <blue|green>` - Alterna tráfego do nginx entre slots
- `/usr/local/bin/run-migrations.sh` - Executa migrações de banco de dados no container ativo
- `/usr/local/bin/backup-certificates.sh` - Backup de certificados SSL para S3

Todos os scripts operacionais carregam variáveis de ambiente de `/etc/lacrei-env.sh`.


### Arquitetura e Estrutura

- **Django REST Framework (DRF):** Escolhido por sua robustez, documentação extensa e ecossistema maduro para APIs REST
- **PostgreSQL:** Banco de dados relacional confiável com excelente suporte a tipos de dados complexos e UUID
- **Docker & Docker Compose:** Containerização para ambiente consistente entre desenvolvimento, staging e produção
- **Separação de concerns:** Apps Django modulares (`core`, `professionals`, `appointments`) para facilitar manutenção

### Autenticação OAuth2

- **Client Credentials Flow:** Adequado para comunicação machine-to-machine
- **Django OAuth Toolkit:** Biblioteca madura e bem mantida com suporte completo ao OAuth2
- **Tokens JWT:** Stateless, escaláveis e seguros

### Identificadores UUID

- **UUIDs como chave primária:** Evita exposição de IDs sequenciais e facilita sincronização entre ambientes
- **Formato:** UUID4 (aleatório) para máxima segurança

### Deploy Blue/Green

- **Zero downtime:** Deploy sem interrupção do serviço
- **Rollback rápido:** Fácil retorno à versão anterior em caso de problemas
- **Nginx como proxy reverso:** Gerencia tráfego entre slots blue e green

### Infraestrutura como Código

- **Terraform:** Provisionamento automatizado e versionado da infraestrutura AWS
- **Módulos reutilizáveis:** Scripts modulares no S3 para inicialização de EC2
- **GitHub Actions:** CI/CD automatizado com deploy em staging e produção

### Documentação

- **OpenAPI 3.0 (drf-spectacular):** Documentação gerada automaticamente a partir do código
- **Swagger UI:** Interface interativa para testar endpoints
- **Postman Collection:** Facilita integração e testes manuais


Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
