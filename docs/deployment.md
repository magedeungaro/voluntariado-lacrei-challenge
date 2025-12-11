# Deployment (AWS)

## Arquitetura

- **EC2**: Instância privada rodando Docker + nginx (uma por ambiente)
- **RDS**: PostgreSQL 16 (instância privada por ambiente)
- **ECR**: Registro de imagens Docker (um por ambiente)
- **SSM**: Acesso seguro sem portas públicas
- **Blue/Green**: Dois containers (8001/8002) com switch via nginx
- **SSL/HTTPS**: Certificados Let's Encrypt via Certbot (renovação automática)

## Ambientes

| Ambiente | Branch | URL | Workflow |
|----------|--------|-----|----------|
| Staging | `staging` | `https://api-stg.magenifica.dev` | `cd-staging.yml` |
| Production | `release` | `https://api.magenifica.dev` | `cd.yml` |

## HTTPS & SSL

A aplicação é servida via **HTTPS** usando certificados gratuitos do **Let's Encrypt**:

- **Certificados SSL**: Obtidos automaticamente via Certbot durante o provisionamento da instância EC2
- **Renovação automática**: Certbot renova certificados a cada 60 dias (antes da expiração de 90 dias)
- **Redirecionamento HTTP → HTTPS**: Todas as requisições HTTP são automaticamente redirecionadas para HTTPS
- **Nginx como reverse proxy**: Gerencia SSL/TLS e distribui tráfego entre containers blue/green

**Por que HTTPS?**
- **Segurança**: Criptografia de dados em trânsito (protege tokens OAuth2, credenciais)
- **Requisito OAuth**: Providers OAuth (Google, Facebook) exigem HTTPS em produção
- **SEO e Confiança**: Navegadores modernos sinalizam sites HTTP como "não seguros"
- **Grátis**: Let's Encrypt fornece certificados SSL sem custo

**Configuração**:
```bash
# Domínios configurados no Terraform
domain_name = "api.magenifica.dev"        # Produção
domain_name = "api-stg.magenifica.dev"    # Staging

# Certbot obtém certificado automaticamente via user_data.sh
# Nginx é reconfigurado para HTTPS com redirecionamento
```

## Estratégia de Deploy: Blue/Green Simplificado

### Contexto do Desafio

Este projeto implementa uma estratégia **Blue/Green deployment** simplificada, adequada para demonstrar conhecimentos de CI/CD e deploy seguro dentro do contexto de um desafio técnico.

### Arquitetura Implementada (Simplificada)

```
┌─────────────────────────────────────────────────────┐
│                    EC2 Instance                      │
│  ┌───────────────────────────────────────────────┐  │
│  │                   Nginx                        │  │
│  │            (reverse proxy/switch)              │  │
│  └───────────────┬───────────────┬───────────────┘  │
│                  │               │                   │
│         ┌────────▼────┐   ┌─────▼───────┐          │
│         │ Container   │   │ Container   │          │
│         │   BLUE      │   │   GREEN     │          │
│         │  :8001      │   │   :8002     │          │
│         └─────────────┘   └─────────────┘          │
└─────────────────────────────────────────────────────┘
```

**Características:**
- Uma única instância EC2 rodando dois containers Docker
- Nginx alterna o tráfego entre blue (porta 8001) e green (porta 8002)
- Deploy acontece no slot inativo, depois o tráfego é alternado
- Rollback instantâneo: basta alternar de volta para o slot anterior

### Arquitetura Real (Produção em Escala)

Em uma aplicação real de produção, a arquitetura seria significativamente diferente:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Application Load Balancer                     │
│                    (ALB com Health Checks)                        │
└─────────────────────────┬────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌──────────▼─────────┐
│   Target Group    │         │    Target Group    │
│      BLUE         │         │       GREEN        │
├───────────────────┤         ├────────────────────┤
│ ┌───┐ ┌───┐ ┌───┐│         │ ┌───┐ ┌───┐ ┌───┐ │
│ │EC2│ │EC2│ │EC2││         │ │EC2│ │EC2│ │EC2│ │
│ └───┘ └───┘ └───┘│         │ └───┘ └───┘ └───┘ │
│    (ou ECS/EKS)  │         │    (ou ECS/EKS)   │
└──────────────────┘         └────────────────────┘
```

**Diferenças principais:**

| Aspecto | Este Projeto | Produção Real |
|---------|--------------|---------------|
| **Instâncias** | 1 EC2 com 2 containers | Múltiplas instâncias por ambiente |
| **Load Balancer** | Nginx local | ALB/NLB da AWS |
| **Auto Scaling** | Não | Sim, baseado em métricas |
| **Target Groups** | N/A | Blue e Green separados |
| **Switch de tráfego** | Script local no nginx | ALB listener rules |
| **Health checks** | Simples (curl) | ALB health checks + CloudWatch |
| **Rollback** | Manual via script | Automático via ALB |
| **Custo** | ~$15-30/mês | $200-1000+/mês |

### Por que esta abordagem?

1. **Custo**: Para um desafio técnico, manter múltiplas instâncias 24/7 seria desnecessário
2. **Demonstração**: Os conceitos de blue/green ficam claros mesmo na versão simplificada
3. **Funcionalidade**: O mecanismo de deploy seguro funciona da mesma forma
4. **Escalabilidade conceitual**: A migração para ALB + Auto Scaling é direta

### Fluxo de Branches e Deploy

```
develop (local) ──► staging (branch) ──► release (branch)
                          │                     │
                          ▼                     ▼
                    Deploy Staging        Deploy Produção
                    (automático)          (automático)
```

- **develop**: Desenvolvimento local, sem deploy automático
- **staging**: Push nesta branch dispara deploy no ambiente de staging
- **release**: Push nesta branch dispara deploy em produção

### Evolução para Produção

Para escalar esta arquitetura para produção real, seria necessário considerar:

#### Fase 1: Multi-Instância com ALB

1. **Criar ALB** com dois Target Groups (blue/green)
2. **Configurar Auto Scaling Groups** para cada Target Group
3. **Atualizar workflows** para usar AWS CodeDeploy ou alternar ALB listeners
4. **Adicionar CloudWatch Alarms** para rollback automático
5. **Implementar canary deployments** (opcional) - tráfego gradual 10% → 50% → 100%

#### Fase 2: Alta Escala (Kubernetes)

Para workloads de alta demanda, considerar migrar para **Amazon EKS** (Kubernetes):

```
┌─────────────────────────────────────────────────────────────────┐
│                        Amazon EKS Cluster                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Ingress Controller                       │ │
│  │                  (ALB Ingress / Nginx)                      │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │                      Service                                │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────┬───────────┬───┴────┬───────────┬──────────┐      │
│  │  Pod     │   Pod     │  Pod   │   Pod     │   Pod    │      │
│  │ (app)   │  (app)   │ (app)  │  (app)   │  (app)   │      │
│  └──────────┴───────────┴────────┴───────────┴──────────┘      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  HPA (Horizontal Pod Autoscaler) - escala baseado em CPU    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```
