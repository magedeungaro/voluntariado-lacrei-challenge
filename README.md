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

Python 3.12 • Django 5.2 • DRF • PostgreSQL 16 • Docker • AWS (EC2, RDS, ECR) • Terraform • GitHub Actions

## 📄 Licença

Projeto desenvolvido para o desafio de voluntariado Lacrei Saúde.
