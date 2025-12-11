# Authentication

A API utiliza OAuth2 com client credentials flow. Para acessar os endpoints protegidos:

## 1. Criar aplicação OAuth2

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

## 2. Obter access token

```bash
curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

## 3. Usar o token nas requisições

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/professionals/
```

## Configurações de Segurança

- ✅ **Autenticação OAuth2 obrigatória** via django-oauth-toolkit (todos os endpoints requerem token)
- ✅ **Rate Limiting**: 300 requisições por segundo por usuário autenticado
- ✅ **CORS configurado** (allow all origins para APIs públicas)
- ✅ **Validação de dados** via Django REST Framework serializers
