# Segurança e Autenticação

Este documento descreve a estratégia de segurança e autenticação implementada na API, incluindo configurações, rotas protegidas e boas práticas.

---

## 🔐 Estratégia de Autenticação

### OAuth2 com Client Credentials

A API utiliza **OAuth2** com o fluxo **Client Credentials** para autenticação machine-to-machine (M2M).

**Framework:** Django OAuth Toolkit  
**Fluxo:** Client Credentials Grant  
**Formato de Token:** JWT (JSON Web Tokens)

### Configuração no Código

**Arquivo:** `app/settings.py`

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.TokenHasReadWriteScope",
    ],
}

OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read access",
        "write": "Write access",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,  # 10 hours
    "REFRESH_TOKEN_EXPIRE_SECONDS": 86400,  # 24 hours
    "ROTATE_REFRESH_TOKEN": True,
}
```

### Criando uma Aplicação OAuth2

Para usar a API, primeiro é necessário criar uma aplicação OAuth2 no Django Admin.

#### Passo 1: Criar Superusuário (se necessário)

```bash
# Com Docker
docker compose exec web python manage.py createsuperuser

# Localmente
poetry run python manage.py createsuperuser
```

#### Passo 2: Acessar Django Admin

```bash
# Local
open http://localhost:8000/admin/

# Produção
open https://api.magenifica.dev/admin/
```

#### Passo 3: Criar Aplicação OAuth2

No Django Admin, navegue para **OAuth2 Provider > Applications** e crie uma nova aplicação com as seguintes configurações:

| Campo | Valor |
|-------|-------|
| **Client type** | Confidential |
| **Authorization grant type** | Client credentials |
| **Name** | Nome da sua aplicação (ex: "Mobile App") |

Após salvar, você receberá:
- **Client ID** - Identificador público da aplicação
- **Client Secret** - Chave secreta (mantenha em segurança!)

### Como Obter Token

**Endpoint:** `POST /oauth/token/`

**Request:**
```bash
curl -X POST https://api.magenifica.dev/oauth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 36000,
  "scope": "read write"
}
```

### Como Usar o Token

Inclua o token no header `Authorization` de todas as requisições:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.magenifica.dev/api/v1/professionals/
```

---

## 🛡️ Rotas Protegidas vs Públicas

### Rotas Públicas (Sem Autenticação)

Apenas o endpoint de health check não requer autenticação:

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/api/v1/health/` | Health check para monitoramento | ❌ Não requerida |

**Implementação no código:**

```python
# app/core/views.py
class HealthCheckView(APIView):
    """Endpoint público de verificação de saúde."""
    
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request: Request) -> Response:
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
```

### Rotas Protegidas (Requerem OAuth2)

Todos os outros endpoints requerem autenticação OAuth2:

#### Profissionais de Saúde

| Método | Endpoint | Descrição | Scopes Necessários |
|--------|----------|-----------|-------------------|
| GET | `/api/v1/professionals/` | Listar profissionais | `read` |
| POST | `/api/v1/professionals/` | Criar profissional | `write` |
| GET | `/api/v1/professionals/{uuid}/` | Detalhes do profissional | `read` |
| PUT | `/api/v1/professionals/{uuid}/` | Atualizar profissional | `write` |
| PATCH | `/api/v1/professionals/{uuid}/` | Atualizar parcialmente | `write` |
| DELETE | `/api/v1/professionals/{uuid}/` | Excluir profissional | `write` |

#### Consultas

| Método | Endpoint | Descrição | Scopes Necessários |
|--------|----------|-----------|-------------------|
| GET | `/api/v1/appointments/` | Listar consultas | `read` |
| POST | `/api/v1/appointments/` | Criar consulta | `write` |
| GET | `/api/v1/appointments/{uuid}/` | Detalhes da consulta | `read` |
| PUT | `/api/v1/appointments/{uuid}/` | Atualizar consulta | `write` |
| PATCH | `/api/v1/appointments/{uuid}/` | Atualizar parcialmente | `write` |
| DELETE | `/api/v1/appointments/{uuid}/` | Excluir consulta | `write` |

**Implementação padrão nos ViewSets:**

```python
# app/professionals/views.py
class ProfessionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet protegido por OAuth2.
    Herda automaticamente as configurações de autenticação do REST_FRAMEWORK.
    """
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    # Autenticação e permissões aplicadas globalmente via settings.py
```

### Respostas de Erro de Autenticação

**Token ausente ou inválido:**
```json
HTTP 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Token expirado:**
```json
HTTP 401 Unauthorized
{
  "detail": "The access token has expired."
}
```

**Permissões insuficientes:**
```json
HTTP 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

---

## 🔒 Medidas de Segurança da API

### 1. Rate Limiting

Proteção contra abuso e ataques DDoS.

**Configuração:**
```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "300/second",  # 300 requisições por segundo por usuário
    },
}
```

### 2. CORS (Cross-Origin Resource Sharing)

Controle de origens permitidas para requisições cross-origin.

**Configuração:**
```python
# Configurado via variável de ambiente
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=Csv(),
)
```

### 3. CSRF Protection

**Configuração:**
```python
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost,http://127.0.0.1,https://api.magenifica.dev,https://api-stg.magenifica.dev",
    cast=Csv(),
)
```

### 4. Security Headers (Produção)

Headers de segurança habilitados automaticamente em produção:

```python
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True          # Proteção XSS
    SECURE_CONTENT_TYPE_NOSNIFF = True        # Previne MIME sniffing
    X_FRAME_OPTIONS = "DENY"                  # Previne clickjacking
    
    if config("USE_HTTPS", default=False, cast=bool):
        CSRF_COOKIE_SECURE = True             # Cookies apenas via HTTPS
        SESSION_COOKIE_SECURE = True          # Sessions apenas via HTTPS
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

### 5. Validação de Dados

Todas as requisições passam por validação via serializers do Django REST Framework:

```python
# Exemplo de validação automática
class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['uuid', 'social_name', 'profession', 'contacts']
    
    def validate_social_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Nome social não pode ser vazio")
        return value
```

### 6. HTTPS Obrigatório

- ✅ Produção: `https://api.magenifica.dev`
- ✅ Staging: `https://api-stg.magenifica.dev`
- ✅ Certificados SSL válidos (ZeroSSL)
- ✅ Renovação automática via Let's Encrypt

---

## 🏗️ Segurança de Infraestrutura

### AWS Security

- ✅ **IMDSv2 obrigatório** - Proteção contra ataques SSRF
- ✅ **RDS em subnet privada** - Banco de dados isolado da internet
- ✅ **Security groups restritivos** - Apenas portas necessárias abertas
- ✅ **VPC endpoints para SSM** - Comunicação segura sem internet pública
- ✅ **IAM roles com menor privilégio** - Permissões mínimas necessárias

### Criptografia

- ✅ **Em trânsito:** HTTPS/TLS 1.2+ em todas as comunicações
- ✅ **Em repouso:** RDS com criptografia habilitada (AES-256)
- ✅ **Secrets:** Nunca no código, sempre em variáveis de ambiente

### Network Segmentation

```
┌─────────────────────────────────────────┐
│  Internet                               │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  Load Balancer     │
        │  (Public Subnet)   │
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  EC2 Instances     │
        │  (Public Subnet)   │
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  RDS PostgreSQL    │
        │  (Private Subnet)  │
        └────────────────────┘
```

---

## 📋 Boas Práticas Implementadas

### 1. Secrets Management

❌ **NUNCA:**
```python
# NÃO FAÇA ISSO!
SECRET_KEY = "django-insecure-hardcoded-key-123"
DB_PASSWORD = "mypassword123"
```

✅ **SEMPRE:**
```python
# Usar variáveis de ambiente
from decouple import config

SECRET_KEY = config("SECRET_KEY")
DB_PASSWORD = config("DB_PASSWORD")
```

### 2. Princípio do Menor Privilégio

Cada componente tem apenas as permissões necessárias:

```python
# IAM role para EC2
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "s3:GetObject"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Auditoria e Logging

Todas as operações críticas são registradas:

```python
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
```

### 4. Dependency Management

- ✅ Dependências fixadas em `pyproject.toml`
- ✅ Atualizações regulares via Dependabot
- ✅ Scan de vulnerabilidades em CI/CD

### 5. Input Validation

Toda entrada é validada antes do processamento:

```python
# Validação de CEP
zip_code = serializers.CharField(
    max_length=8,
    validators=[RegexValidator(r'^\d{8}$')]
)
```

---

## 🔍 Monitoramento e Detecção

### CloudWatch Logs

- ✅ Logs de aplicação centralizados
- ✅ Logs de acesso do Nginx
- ✅ Logs de erro do Django

### Alertas

- ✅ Taxa de erro 5xx
- ✅ Latência elevada
- ✅ Tentativas de autenticação falhadas

---

## 📚 Recursos Adicionais

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

---

Para mais informações sobre autenticação OAuth2, consulte [docs/authentication.md](authentication.md).
