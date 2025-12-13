# Lacrei Saúde API

API REST para gerenciamento de profissionais de saúde e consultas - Desafio Lacrei Saúde.

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
- **[Referência da API](docs/api-reference.md)** - Endpoints e exemplos de uso
- **[Autenticação](docs/authentication.md)** - Guia OAuth2
- **[Deploy](docs/deployment.md)** - AWS, blue/green, HTTPS/SSL
- **[Segurança](docs/security.md)** - Práticas de segurança

## 🌐 Ambientes

| Ambiente | URL | Branch |
|----------|-----|--------|
| Produção | `https://api.magenifica.dev` | `release` |
| Staging | `https://api-stg.magenifica.dev` | `staging` |

> **Nota:** Ambos os ambientes utilizam certificados SSL válidos (ZeroSSL) com HTTPS habilitado.

## 🔑 Quick API Test

### Using cURL

```bash
# Health check (público)
curl https://api.magenifica.dev/api/v1/health/

# Obter token OAuth2 (Client Credentials)
curl -X POST https://api.magenifica.dev/api/v1/auth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Usar token em endpoints protegidos
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```

### Usando Postman

Importe a collection do Postman para testar todos os endpoints:

📦 **[Postman Collection](docs/postman_collection.json)**

A collection inclui:
- Configuração de autenticação OAuth2
- Exemplos de todos os endpoints (CRUD completo)
- Variáveis de ambiente para staging e produção
- Testes automatizados

## 🛠️ Stack

Python 3.12 • Django 5.2 • DRF • PostgreSQL 16 • Docker • AWS (EC2, RDS, ECR, S3) • Terraform • GitHub Actions

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

## 📄 Licença

Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
