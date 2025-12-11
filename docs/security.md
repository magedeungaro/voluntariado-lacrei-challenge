# Security

## Infraestrutura

- ✅ IMDSv2 obrigatório
- ✅ Secrets em variáveis de ambiente (nunca no código)
- ✅ Security groups restritivos
- ✅ VPC endpoints para SSM
- ✅ RDS em subnet privada
- ✅ Criptografia em trânsito e em repouso
- ✅ IAM com princípio de menor privilégio

## API

- ✅ **Autenticação OAuth2 obrigatória** via django-oauth-toolkit (todos os endpoints requerem token)
- ✅ **Rate Limiting**: 300 requisições por segundo por usuário autenticado
- ✅ **CORS configurado** (allow all origins para APIs públicas)
- ✅ **Validação de dados** via Django REST Framework serializers

## Best Practices

1. **Nunca commite secrets** - Use variáveis de ambiente e AWS Secrets Manager
2. **Princípio do menor privilégio** - IAM roles com permissões mínimas necessárias
3. **Criptografia em trânsito** - HTTPS obrigatório em produção
4. **Criptografia em repouso** - RDS com criptografia habilitada
5. **Auditoria** - CloudWatch Logs para todas as operações críticas
6. **Segmentação de rede** - VPC com subnets públicas e privadas
7. **Atualizações regulares** - Dependências mantidas atualizadas via Dependabot
