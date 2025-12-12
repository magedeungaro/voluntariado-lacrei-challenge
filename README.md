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

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)** - Setup, stack tecnológica, estrutura do projeto
- **[API Reference](docs/api-reference.md)** - Endpoints e exemplos de uso
- **[Authentication](docs/authentication.md)** - Guia OAuth2
- **[Deployment](docs/deployment.md)** - AWS, blue/green, HTTPS/SSL
- **[Security](docs/security.md)** - Práticas de segurança

## 🌐 Live Environments

| Ambiente | URL | Branch |
|----------|-----|--------|
| Production | `https://api.magenifica.dev` | `release` |
| Staging | `https://api-stg.magenifica.dev` | `staging` |

> **Nota:** O ambiente de staging utiliza um certificado de teste do Let's Encrypt (staging) por questões de custo e limites de emissão. Esse certificado não é confiável para navegadores e exibirá um aviso de segurança (`ERR_CERT_AUTHORITY_INVALID`). Isso é intencional para fins de teste e não afeta o ambiente de produção, que utiliza um certificado válido e confiável.

## 🔑 Quick API Test

```bash
# Health check (público)
curl https://api.magenifica.dev/api/v1/health/

# Endpoints protegidos (requer OAuth2 token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```

## 🛠️ Stack

Python 3.12 • Django 5.2 • DRF • PostgreSQL 16 • Docker • AWS (EC2, RDS, ECR, S3) • Terraform • GitHub Actions

## 🔧 Development

### Pre-push Hook for Script Updates

The project includes a pre-push hook that automatically uploads changed setup scripts to S3:

```bash
# Install the pre-push hook
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

This hook:
- Detects changes to scripts in `terraform/modules/lacrei-infra/scripts/`
- Automatically uploads them to the appropriate S3 bucket (staging or production)
- Runs before `git push` on `staging` and `main` branches only
- Can be skipped with `git push --no-verify` if needed

### EC2 User Data Architecture

The infrastructure uses a modular approach for EC2 instance initialization:

1. **Bootstrap Script** (`bootstrap.sh`) - Minimal script uploaded via Terraform
   - Downloads modular scripts from S3
   - Executes them in order
   - Stays under AWS 16KB user_data limit

2. **Modular Scripts** (stored in S3):
   - `00-init.sh` - Logging setup and initialization
   - `01-ssm-agent.sh` - SSM agent configuration
   - `02-system-packages.sh` - Docker, nginx, certbot installation
   - `03-app-setup.sh` - Application directory and environment setup
   - `04-nginx-config.sh` - Nginx reverse proxy configuration
   - `05-deployment-scripts.sh` - Blue/green deployment utilities
   - `06-ssl-certificates.sh` - SSL certificate management
   - `99-finalize.sh` - Final checks and logging

This architecture allows:
- Easy script updates without Terraform changes
- Bypassing AWS user_data size limits
- Better organization and maintainability
- Independent script development and testing

## 📄 Licença

Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
