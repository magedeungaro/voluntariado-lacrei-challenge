# API Reference

## Documentação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI Schema |

## Profissionais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/professionals/` | Lista profissionais |
| POST | `/api/v1/professionals/` | Cria profissional |
| GET | `/api/v1/professionals/{uuid}/` | Detalhes do profissional |
| PUT | `/api/v1/professionals/{uuid}/` | Atualiza profissional |
| PATCH | `/api/v1/professionals/{uuid}/` | Atualiza parcialmente |
| DELETE | `/api/v1/professionals/{uuid}/` | Remove profissional |

## Consultas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/appointments/` | Lista consultas |
| POST | `/api/v1/appointments/` | Cria consulta |
| GET | `/api/v1/appointments/{uuid}/` | Detalhes da consulta |
| PUT | `/api/v1/appointments/{uuid}/` | Atualiza consulta |
| PATCH | `/api/v1/appointments/{uuid}/` | Atualiza parcialmente |
| DELETE | `/api/v1/appointments/{uuid}/` | Remove consulta |

## Autenticação (OAuth2)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/o/token/` | Obter access token |

## Acesso à API

**URLs da API:**
- **Produção**: `https://api.magenifica.dev/api/v1/`
- **Staging**: `https://api-stg.magenifica.dev/api/v1/`

**Endpoints disponíveis:**
- `GET /api/v1/health/` - Health check
- `GET /api/v1/professionals/` - Lista profissionais (requer OAuth2)
- `POST /api/v1/professionals/` - Cria profissional (requer OAuth2)
- `GET /api/v1/appointments/` - Lista consultas (requer OAuth2)
- `POST /api/v1/appointments/` - Cria consulta (requer OAuth2)

**Exemplo de requisição:**
```bash
# Health check (público)
curl https://api.magenifica.dev/api/v1/health/

# Endpoints protegidos (requer token OAuth2)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```
