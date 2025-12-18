# Lacrei Saúde API

API REST para gerenciamento de profissionais de saúde e consultas - Desafio Lacrei Saúde.

## 📋 Escopo Funcional

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

## 🛠️ Stack

Python 3.12 • Django 5.2 • DRF • PostgreSQL 16 • Docker • AWS (EC2, RDS, ECR, S3) • Terraform • GitHub Actions

## 📚 Documentação

| Documento | O que você vai encontrar |
|-----------|--------------------------|
| **[Primeiros Passos](docs/getting-started.md)** | Setup local, stack tecnológica, estrutura do projeto |
| **[Referência da API](docs/api-reference.md)** ⭐ | Endpoints completos, exemplos de request/response, autenticação |
| **[Segurança e Autenticação](docs/security.md)** | OAuth2, rotas protegidas, boas práticas de segurança |
| **[Testes](docs/testing.md)** | Suite de testes, cobertura, como executar testes |
| **[Implantação](docs/deployment.md)** | AWS, blue/green, HTTPS/SSL, estratégia de CI/CD |
| **[Decisões Técnicas e Limitações](docs/technical-decisions-and-limitations.md)** | Arquitetura, trade-offs, limitações conhecidas, melhorias futuras |
