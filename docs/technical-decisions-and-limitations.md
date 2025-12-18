# Decisões Técnicas e Limitações

Este documento registra as decisões técnicas relevantes tomadas durante o desenvolvimento do projeto, suas justificativas e trade-offs, além de limitações conhecidas e possíveis melhorias futuras.

---

## 📋 Índice

- [Decisões de Arquitetura](#decisões-de-arquitetura)
- [Decisões de Implementação](#decisões-de-implementação)
- [Decisões de Infraestrutura](#decisões-de-infraestrutura)
- [Limitações Conhecidas](#limitações-conhecidas)
- [Melhorias Futuras](#melhorias-futuras)

---

## 🏗️ Decisões de Arquitetura

### 1. Camada de Serviços (Service Layer)

**Decisão:** Implementar uma camada de serviços separada para lógica de negócios e validações complexas, ao invés de concentrar tudo nos serializers.

**Justificativa:**
- **Separação de responsabilidades:** Serializers focam apenas em serialização/deserialização de dados
- **Testabilidade:** Lógica de negócio isolada e mais fácil de testar
- **Reutilização:** Serviços podem ser utilizados em diferentes contextos (API, CLI, tasks assíncronas)
- **Manutenibilidade:** Código de negócio centralizado e organizado

```python
# app/professionals/services.py
class ProfessionalService:
    """Serviço para lógica de negócio de Profissionais."""
    
    @staticmethod
    def create_professional(data: dict) -> Professional:
        """Cria um profissional com endereço e contatos."""
        # Validações de negócio complexas
        # Criação de objetos relacionados
        # Lógica transacional
        pass
```

**Trade-offs:**
- ✅ **Vantagem:** Código mais organizado e testável
- ✅ **Vantagem:** Facilita evolução do sistema
- ⚠️ **Desvantagem:** Camada adicional aumenta complexidade inicial
- ⚠️ **Desvantagem:** Desenvolvedores precisam entender o padrão

---

### 2. Normalização de Dados - Endereço e Contatos

**Decisão:** Normalizar endereços e contatos como tabelas separadas com relacionamento one-to-many com Professional.

**Justificativa:**
- **Flexibilidade:** Profissional pode ter múltiplos endereços (consultório, clínica, atendimento domiciliar)
- **Flexibilidade:** Profissional pode ter múltiplos contatos (WhatsApp, email pessoal, email comercial, telefone)
- **Integridade:** Dados estruturados e validados separadamente
- **Evolução:** Facilita adicionar campos específicos (tipo de endereço, endereço principal)

**Modelo de Dados:**

```python
# app/professionals/models.py
class Professional(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    social_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=255)

class Address(models.Model):
    professional = models.ForeignKey(Professional, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    # ... outros campos

class Contact(models.Model):
    professional = models.ForeignKey(Professional, related_name='contacts')
    kind = models.CharField(choices=CONTACT_TYPES)
    value = models.CharField(max_length=255)
```

**Trade-offs:**
- ✅ **Vantagem:** Escalável e flexível para casos de uso futuros
- ✅ **Vantagem:** Evita campos JSON não estruturados
- ✅ **Vantagem:** Validações específicas por tipo de dado
- ⚠️ **Desvantagem:** Mais JOINs em queries (mitigado com `select_related`)
- ⚠️ **Desvantagem:** Serialização nested mais complexa

---

## 🚀 Decisões de Implementação

### 3. UUIDs para Identificação Externa

**Decisão:** Utilizar UUIDs (UUID4) como identificadores externos na API, mantendo IDs auto-incrementais como chave primária interna.

**Justificativa:**
- **Segurança:** IDs sequenciais expõem volume de dados e facilitam enumeração
- **Ocultação de informações:** UUID não revela informações sobre crescimento ou volume da base
- **APIs públicas:** Melhor prática para identificadores expostos externamente

**Implementação:**

```python
class Professional(models.Model):
    # id = auto-incrementing primary key (implícito do Django)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,  # Índice para lookups rápidos via UUID
    )
    
# ViewSet usa UUID para lookup externo
class ProfessionalViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'  # API usa UUID, não ID numérico
```
---

### 4. OAuth2 Client Credentials Flow

**Decisão:** Implementar OAuth2 com fluxo Client Credentials para autenticação.

**Justificativa:**
- **Padrão da indústria:** OAuth2 é amplamente adotado e compreendido
- **Machine-to-Machine:** Ideal para APIs sem interação de usuário final
- **Escalabilidade:** Stateless tokens (JWT) não requerem lookup de sessão
- **Scopes:** Controle granular de permissões (read/write)

**Trade-offs:**
- ✅ **Vantagem:** Padrão de mercado, bem documentado
- ✅ **Vantagem:** Suporte a múltiplas aplicações cliente
- ✅ **Vantagem:** Tokens com expiração automática
- ⚠️ **Desvantagem:** Complexidade inicial maior que API Key simples
- ⚠️ **Desvantagem:** Clientes precisam gerenciar refresh de tokens

---

## 🏗️ Decisões de Infraestrutura

### 5. Blue-Green Deployment com Slots (Portas)

**Decisão:** Implementar Blue-Green deployment usando dois "slots" (containers nas portas 8001 e 8002) no mesmo servidor, com Nginx fazendo o roteamento.

**Justificativa:**
- **Simplicidade:** Conceito fácil de entender e implementar
- **Zero Downtime:** Deploy sem interrupção do serviço
- **Rollback rápido:** Basta trocar o upstream do Nginx
- **Custo-efetivo:** Não requer infraestrutura complexa (sem Load Balancer adicional)

**Arquitetura:**

```
┌─────────────────────────────────────┐
│  Nginx (porta 80/443)               │
│  upstream: blue ou green            │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼────┐  ┌──▼─────┐
│ Blue   │  │ Green  │
│ :8001  │  │ :8002  │
└────────┘  └────────┘
```

**Fluxo de Deploy:**
```bash
# 1. Deploy no slot inativo (green)
./deploy.sh green v1.2.0

# 2. Testar o slot green
curl http://localhost:8002/api/v1/health/

# 3. Switch de tráfego
./switch-backend.sh green

# 4. Blue fica como backup para rollback
```

**Trade-offs:**
- ✅ **Vantagem:** Simples de implementar e debugar
- ✅ **Vantagem:** Zero downtime garantido
- ✅ **Vantagem:** Rollback instantâneo
- ⚠️ **Limitação:** Requer memória para 2 containers simultâneos
- ⚠️ **Limitação:** Não escala horizontalmente (limitado a 1 servidor)
- ⚠️ **Limitação:** Sem balanceamento de carga entre slots

**Quando evoluir:**
- Quando tráfego exigir múltiplos servidores
- Quando precisar de auto-scaling
- Considerar migração para Kubernetes (EKS) ou ECS com ALB

---

### 6. Modularização de Scripts User Data (Bootstrap)

**Decisão:** Dividir o user data do EC2 em um script bootstrap mínimo que baixa e executa scripts modulares do S3.

**Justificativa:**
- **Limite da AWS:** User data tem limite de 16KB - scripts modulares contornam isso
- **Manutenibilidade:** Scripts separados por responsabilidade (packages, nginx, ssl, etc.)
- **Versionamento:** Scripts no Git, fácil de revisar mudanças
- **Deploy independente:** Atualizar scripts sem recriar infraestrutura Terraform
- **Testabilidade:** Scripts podem ser testados individualmente

**Arquitetura:**

```
Terraform user_data
    ↓
bootstrap.sh (< 2KB)
    ↓
Baixa do S3:
    ├── 00-init.sh              # Setup básico
    ├── 01-ssm-agent.sh         # Agente SSM
    ├── 02-system-packages.sh   # Docker, nginx, etc
    ├── 03-app-setup.sh         # Diretórios e env
    ├── 04-nginx-config.sh      # Proxy reverso
    ├── 05-install-tools.sh     # Scripts operacionais
    ├── 06-ssl-certificates.sh  # Certificados SSL
    └── 99-finalize.sh          # Verificações finais
```

**Pre-push Hook Automático:**
```bash
# Detecta mudanças em scripts e envia para S3 automaticamente
cp hooks/pre-push.sample .git/hooks/pre-push
```

**Trade-offs:**
- ✅ **Vantagem:** Sem limite de tamanho prático
- ✅ **Vantagem:** Scripts organizados por responsabilidade
- ✅ **Vantagem:** Fácil manutenção e evolução
- ✅ **Vantagem:** Deploy de scripts sem terraform apply
- ⚠️ **Desvantagem:** Dependência do S3 (mitigado com retry logic)
- ⚠️ **Desvantagem:** Necessita sincronização manual (resolvido com hook)

---

## ⚠️ Limitações Conhecidas

### 1. Escalabilidade Horizontal Limitada

**Descrição:** Arquitetura atual baseada em servidor único com blue-green deployment não escala horizontalmente.

**Impacto:** 
- Sistema limitado à capacidade de uma única instância EC2
- Sem redundância geográfica
- Ponto único de falha (SPOF)
---

### 2. Validação de Conflitos de Agendamento

**Descrição:** Sistema não valida se já existe uma consulta agendada no mesmo horário para o mesmo profissional.

**Impacto:**
- Possível dupla marcação para o mesmo horário
- Conflitos precisam ser resolvidos manualmente
---

### 3. Idempotência de Requisições

**Descrição:** API não implementa mecanismo de idempotência para requisições POST.

**Impacto:**
- Requisições duplicadas (retry, timeout) podem criar recursos duplicados
- Sem garantia de "exactly-once" processing
---

### 4. Cache de Queries

**Descrição:** Não há camada de cache para queries repetidas.

**Impacto:**
- Todas as requisições vão ao banco de dados
- Queries idênticas são executadas repetidamente
- Performance subótima para listagens frequentes

**Queries que se Beneficiariam de Cache:**
- Lista de profissionais (raramente muda)
- Detalhes de profissional específico
- Lista de consultas de um profissional
---

### 5. Rate Limiting Básico

**Descrição:** Rate limiting atual é simplificado (300 req/s por usuário).

**Limitações:**
- Sem diferenciação por endpoint (read vs write)
---

## 📚 Referências

- [12 Factor App](https://12factor.net/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [REST API Design Best Practices](https://restfulapi.net/)
