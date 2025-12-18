# Referência da API

Documentação completa dos endpoints da API REST para gerenciamento de profissionais de saúde e consultas.

## 📚 Índice

- [URLs Base](#urls-base)
- [Autenticação](#autenticação)
- [Documentação Interativa](#documentação-interativa)
- [Health Check](#health-check)
- [Profissionais de Saúde](#profissionais-de-saúde)
- [Consultas](#consultas)
- [Códigos de Status HTTP](#códigos-de-status-http)

---

## URLs Base

| Ambiente | URL Base |
|----------|----------|
| **Produção** | `https://api.magenifica.dev/api/v1/` |
| **Staging** | `https://api-stg.magenifica.dev/api/v1/` |
| **Local** | `http://localhost:8000/api/v1/` |

---

## Autenticação

A API utiliza **OAuth2** com o fluxo **Client Credentials** para autenticação. Todos os endpoints (exceto `/health/`) requerem um token de acesso válido.

### Obter Token de Acesso

**Endpoint:** `POST /oauth/token/`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-urlencoded):**
```
grant_type=client_credentials
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
```

**Exemplo de Requisição:**
```bash
curl -X POST https://api.magenifica.dev/oauth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

**Resposta (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 36000,
  "scope": "read write"
}
```

### Usar Token nas Requisições

Inclua o token no header `Authorization` de todas as requisições protegidas:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```

---

## Documentação Interativa

### Swagger UI (Interface Interativa)

**URL:** `https://api.magenifica.dev/api/docs/`

Interface visual para testar endpoints diretamente no navegador.

### OpenAPI Schema

**Formato YAML:** [docs/schema.yaml](schema.yaml)  
**Endpoint JSON:** `https://api.magenifica.dev/api/schema/`

Schema completo em formato OpenAPI 3.0 para importar em ferramentas como Postman, Insomnia ou geradores de código.

---

## Health Check

### Verificar Status da API

**Endpoint:** `GET /api/v1/health/`  
**Autenticação:** Não requerida  
**Descrição:** Endpoint público para verificar se a API está online e operacional.

**Exemplo de Requisição:**
```bash
curl https://api.magenifica.dev/api/v1/health/
```

**Resposta (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Profissionais de Saúde

### Listar Profissionais

**Endpoint:** `GET /api/v1/professionals/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Retorna uma lista paginada de todos os profissionais de saúde cadastrados.

**Parâmetros de Query:**
- `page` (opcional) - Número da página (padrão: 1)

**Exemplo de Requisição:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/?page=1
```

**Resposta (200 OK):**
```json
{
  "count": 42,
  "next": "https://api.magenifica.dev/api/v1/professionals/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "social_name": "Dr. Maria Silva",
      "profession": "Médica",
      "contacts": [
        {
          "kind": "email",
          "value": "maria.silva@email.com"
        },
        {
          "kind": "whatsapp",
          "value": "11999999999"
        }
      ]
    }
  ]
}
```

---

### Criar Profissional

**Endpoint:** `POST /api/v1/professionals/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Cria um novo profissional de saúde com endereço e contatos.

**Body (JSON):**
```json
{
  "social_name": "Dr. João Santos",
  "profession": "Psicólogo",
  "address": {
    "street": "Av. Paulista",
    "number": "1000",
    "neighborhood": "Bela Vista",
    "complement": "Conjunto 501",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310100"
  },
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos@email.com"
    },
    {
      "kind": "whatsapp",
      "value": "11988887777"
    }
  ]
}
```

**Exemplo de Requisição:**
```bash
curl -X POST https://api.magenifica.dev/api/v1/professionals/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "social_name": "Dr. João Santos",
    "profession": "Psicólogo",
    "address": {
      "street": "Av. Paulista",
      "number": "1000",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01310100"
    },
    "contacts": [
      {"kind": "email", "value": "joao.santos@email.com"}
    ]
  }'
```

**Resposta (201 Created):**
```json
{
  "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "social_name": "Dr. João Santos",
  "profession": "Psicólogo",
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos@email.com"
    }
  ]
}
```

**Status HTTP:**
- `201 Created` - Profissional criado com sucesso
- `400 Bad Request` - Dados inválidos ou campos obrigatórios ausentes
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Obter Detalhes do Profissional

**Endpoint:** `GET /api/v1/professionals/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Retorna os detalhes completos de um profissional específico.

**Parâmetros de Path:**
- `uuid` - UUID do profissional

**Exemplo de Requisição:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/7c9e6679-7425-40de-944b-e07fc1f90ae7/
```

**Resposta (200 OK):**
```json
{
  "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "social_name": "Dr. João Santos",
  "profession": "Psicólogo",
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos@email.com"
    },
    {
      "kind": "whatsapp",
      "value": "11988887777"
    }
  ],
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-15T10:30:00Z"
}
```

**Status HTTP:**
- `200 OK` - Sucesso
- `404 Not Found` - Profissional não encontrado
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Atualizar Profissional (Completo)

**Endpoint:** `PUT /api/v1/professionals/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Atualiza todos os campos de um profissional. Todos os campos são obrigatórios.

**Parâmetros de Path:**
- `uuid` - UUID do profissional

**Body (JSON):**
```json
{
  "social_name": "Dr. João Santos Updated",
  "profession": "Psicólogo Clínico",
  "address": {
    "street": "Av. Paulista",
    "number": "2000",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310100"
  },
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos.novo@email.com"
    }
  ]
}
```

**Resposta (200 OK):**
```json
{
  "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "social_name": "Dr. João Santos Updated",
  "profession": "Psicólogo Clínico",
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos.novo@email.com"
    }
  ]
}
```

**Status HTTP:**
- `200 OK` - Profissional atualizado com sucesso
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Profissional não encontrado
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Atualizar Profissional (Parcial)

**Endpoint:** `PATCH /api/v1/professionals/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Atualiza apenas os campos fornecidos de um profissional.

**Parâmetros de Path:**
- `uuid` - UUID do profissional

**Body (JSON):**
```json
{
  "social_name": "Dr. João Santos Atualizado"
}
```

**Resposta (200 OK):**
```json
{
  "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "social_name": "Dr. João Santos Atualizado",
  "profession": "Psicólogo",
  "contacts": [
    {
      "kind": "email",
      "value": "joao.santos@email.com"
    }
  ]
}
```

**Status HTTP:**
- `200 OK` - Profissional atualizado com sucesso
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Profissional não encontrado
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Excluir Profissional

**Endpoint:** `DELETE /api/v1/professionals/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Remove um profissional do sistema.

**Parâmetros de Path:**
- `uuid` - UUID do profissional

**Exemplo de Requisição:**
```bash
curl -X DELETE https://api.magenifica.dev/api/v1/professionals/7c9e6679-7425-40de-944b-e07fc1f90ae7/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Resposta (204 No Content):**
```
(sem body)
```

**Status HTTP:**
- `204 No Content` - Profissional excluído com sucesso
- `404 Not Found` - Profissional não encontrado
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

## Consultas

### Listar Consultas

**Endpoint:** `GET /api/v1/appointments/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Retorna uma lista paginada de todas as consultas agendadas com informações do profissional.

**Parâmetros de Query:**
- `page` (opcional) - Número da página (padrão: 1)
- `professional_uuid` (opcional) - Filtrar consultas por UUID do profissional

**Exemplo de Requisição:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/appointments/?page=1
```

**Resposta (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "uuid": "a3bb189e-8bf9-3888-9912-ace4e6543002",
      "date": "2024-12-20T14:30:00Z",
      "professional": {
        "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "social_name": "Dr. João Santos",
        "profession": "Psicólogo",
        "contacts": [
          {
            "kind": "email",
            "value": "joao.santos@email.com"
          }
        ]
      },
      "created_at": "2024-12-15T10:30:00Z",
      "updated_at": "2024-12-15T10:30:00Z"
    }
  ]
}
```

---

### Criar Consulta

**Endpoint:** `POST /api/v1/appointments/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Cria uma nova consulta vinculada a um profissional.

**Body (JSON):**
```json
{
  "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "date": "2024-12-20T14:30:00Z"
}
```

**Exemplo de Requisição:**
```bash
curl -X POST https://api.magenifica.dev/api/v1/appointments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "date": "2024-12-20T14:30:00Z"
  }'
```

**Resposta (201 Created):**
```json
{
  "uuid": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "date": "2024-12-20T14:30:00Z",
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-15T10:30:00Z"
}
```

**Status HTTP:**
- `201 Created` - Consulta criada com sucesso
- `400 Bad Request` - Dados inválidos ou campos obrigatórios ausentes
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Obter Detalhes da Consulta

**Endpoint:** `GET /api/v1/appointments/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Retorna os detalhes completos de uma consulta com informações do profissional.

**Parâmetros de Path:**
- `uuid` - UUID da consulta

**Exemplo de Requisição:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.magenifica.dev/api/v1/appointments/a3bb189e-8bf9-3888-9912-ace4e6543002/
```

**Resposta (200 OK):**
```json
{
  "uuid": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "date": "2024-12-20T14:30:00Z",
  "professional": {
    "uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "social_name": "Dr. João Santos",
    "profession": "Psicólogo",
    "contacts": [
      {
        "kind": "email",
        "value": "joao.santos@email.com"
      }
    ]
  },
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-15T10:30:00Z"
}
```

**Status HTTP:**
- `200 OK` - Sucesso
- `404 Not Found` - Consulta não encontrada
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Atualizar Consulta (Completo)

**Endpoint:** `PUT /api/v1/appointments/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Atualiza todos os campos de uma consulta.

**Parâmetros de Path:**
- `uuid` - UUID da consulta

**Body (JSON):**
```json
{
  "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "date": "2024-12-21T15:00:00Z"
}
```

**Resposta (200 OK):**
```json
{
  "uuid": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "date": "2024-12-21T15:00:00Z",
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-17T09:15:00Z"
}
```

**Status HTTP:**
- `200 OK` - Consulta atualizada com sucesso
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Consulta não encontrada
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Atualizar Consulta (Parcial)

**Endpoint:** `PATCH /api/v1/appointments/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Atualiza apenas os campos fornecidos de uma consulta.

**Parâmetros de Path:**
- `uuid` - UUID da consulta

**Body (JSON):**
```json
{
  "date": "2024-12-22T10:00:00Z"
}
```

**Resposta (200 OK):**
```json
{
  "uuid": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "professional_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "date": "2024-12-22T10:00:00Z",
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-17T09:20:00Z"
}
```

**Status HTTP:**
- `200 OK` - Consulta atualizada com sucesso
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Consulta não encontrada
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

### Excluir Consulta

**Endpoint:** `DELETE /api/v1/appointments/{uuid}/`  
**Autenticação:** Requerida (OAuth2)  
**Descrição:** Remove uma consulta do sistema (cancelamento).

**Parâmetros de Path:**
- `uuid` - UUID da consulta

**Exemplo de Requisição:**
```bash
curl -X DELETE https://api.magenifica.dev/api/v1/appointments/a3bb189e-8bf9-3888-9912-ace4e6543002/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Resposta (204 No Content):**
```
(sem body)
```

**Status HTTP:**
- `204 No Content` - Consulta excluída com sucesso
- `404 Not Found` - Consulta não encontrada
- `401 Unauthorized` - Token de acesso inválido ou ausente

---

## Códigos de Status HTTP

A API utiliza os seguintes códigos de status HTTP:

| Código | Descrição |
|--------|-----------|
| `200 OK` | Requisição bem-sucedida |
| `201 Created` | Recurso criado com sucesso |
| `204 No Content` | Requisição bem-sucedida sem conteúdo de resposta (geralmente em DELETE) |
| `400 Bad Request` | Dados inválidos ou mal formatados |
| `401 Unauthorized` | Token de autenticação ausente, inválido ou expirado |
| `403 Forbidden` | Acesso negado (permissões insuficientes) |
| `404 Not Found` | Recurso não encontrado |
| `500 Internal Server Error` | Erro interno do servidor |

---

## Tipos de Contato

Os seguintes tipos de contato são suportados no campo `kind`:

| Valor | Descrição |
|-------|-----------|
| `email` | Endereço de e-mail |
| `whatsapp` | Número do WhatsApp |
| `mobile` | Número de celular |
| `phone` | Número de telefone fixo |
| `linkedin` | URL do perfil do LinkedIn |

---

## Recursos Adicionais

## Recursos Adicionais

### Postman Collection

Uma collection Postman completa está disponível em [postman_collection.json](postman_collection.json) com todos os endpoints configurados.

**Como usar:**

1. **Importe a collection** no Postman
2. **Configure as variáveis de ambiente**:
   - `client_id`: Seu OAuth2 Client ID
   - `client_secret`: Seu OAuth2 Client Secret
   - `baseUrl`: URL da API (produção ou staging)
3. **Execute `fallback_token_request` primeiro**:
   - Localizado em `api > oauth > fallback_token_request`
   - Gera um novo access token OAuth2
   - Atualiza automaticamente a variável `{{token}}` na collection
4. **Use os outros endpoints**: Todos já configurados com `Authorization: Bearer {{token}}`

> ⚠️ **Importante**: Sempre execute `fallback_token_request` antes de testar endpoints protegidos. O token expira após 10 horas.

### Swagger UI

Acesse a documentação interativa em:
- **Produção:** `https://api.magenifica.dev/api/docs/`
- **Staging:** `https://api-stg.magenifica.dev/api/docs/`
- **Local:** `http://localhost:8000/api/docs/`

### OpenAPI Schema

O schema completo OpenAPI 3.0 está disponível em:
- **Arquivo YAML:** [schema.yaml](schema.yaml)
- **Endpoint JSON:** `https://api.magenifica.dev/api/schema/`

---

## Suporte e Contato

Para questões sobre a API ou reportar problemas, consulte o [repositório do projeto](https://github.com/magedeungaro/voluntariado-lacrei-challenge).
