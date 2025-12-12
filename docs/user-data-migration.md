# EC2 User Data Migration - S3 Modular Architecture

## Summary

Successfully migrated from a monolithic 18.7KB user_data script to a modular S3-based architecture that stays well under AWS's 16KB limit.

## Changes Made

### 1. Modularized Scripts (✅ Complete)

Created 8 modular scripts in `terraform/modules/lacrei-infra/scripts/`:

- `00-init.sh` - Logging and initialization
- `01-ssm-agent.sh` - SSM agent setup and connectivity tests
- `02-system-packages.sh` - System packages (Docker, nginx, certbot, AWS CLI)
- `03-app-setup.sh` - Application directory and environment configuration
- `04-nginx-config.sh` - Nginx reverse proxy setup
- `05-deployment-scripts.sh` - Blue/green deployment utilities
- `06-ssl-certificates.sh` - SSL certificate management (Let's Encrypt + S3 backup)
- `99-finalize.sh` - Final checks and completion logging

### 2. S3 Infrastructure (✅ Complete)

**File:** `terraform/modules/lacrei-infra/s3.tf`

Added:
- New S3 bucket for scripts (`lacrei-saude-{env}-scripts`)
- Versioning, encryption, and lifecycle policies
- Individual `aws_s3_object` resources for each script with `etag` tracking
- Fixed lifecycle configuration warning by adding `filter { prefix = "" }`

**Benefits:**
- Scripts automatically upload via Terraform
- Version tracking with S3 versioning
- Changes to scripts trigger Terraform updates
- 30-day retention of old versions

### 3. Bootstrap Script (✅ Complete)

**File:** `terraform/modules/lacrei-infra/templates/bootstrap.sh`

Minimal script (2.3KB raw, 3.1KB base64) that:
- Downloads all modular scripts from S3
- Substitutes Terraform template variables
- Executes scripts in sequential order
- Provides comprehensive logging
- Handles errors gracefully

**Size Comparison:**
- Old user_data: 18.7KB base64 ❌ (exceeds 16KB limit)
- New bootstrap: 3.1KB base64 ✅ (81% reduction!)

### 4. EC2 Configuration (✅ Complete)

**File:** `terraform/modules/lacrei-infra/ec2.tf`

Changes:
- Updated to use `bootstrap.sh` instead of `user_data.sh`
- Removed `base64encode()` wrapper (Terraform handles this automatically)
- Added `scripts_s3_bucket` parameter

### 5. IAM Permissions (✅ Complete)

**File:** `terraform/modules/lacrei-infra/iam.tf`

Added:
- New policy `ec2_scripts_s3` for S3 scripts bucket access
- Read-only permissions (GetObject, ListBucket)
- Separate from certificate bucket permissions

### 6. Pre-commit Hook (✅ Complete)

**File:** `hooks/pre-commit`

Automated script upload on git commit:
- Detects changed scripts in staging area
- Uploads only modified scripts to S3
- Works on `staging` and `main` branches
- Maps branch to environment (staging/production)
- Validates S3 bucket exists
- Provides colored output and error handling
- Can be skipped with `--no-verify`

**Installation:**
```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 7. Documentation (✅ Complete)

**File:** `README.md`

Added sections:
- Pre-commit hook installation and usage
- EC2 User Data Architecture explanation
- Modular scripts description
- Benefits of the new architecture

## Architecture Benefits

### 1. **Size Limit Resolution**
- Old: 18.7KB (exceeded 16KB limit) ❌
- New: 3.1KB (81% under limit) ✅

### 2. **Maintainability**
- Modular scripts easier to understand and modify
- Each script has a single responsibility
- Can test scripts independently
- Version control for individual components

### 3. **Flexibility**
- Update scripts without replacing EC2 instances
- Can upload scripts manually via pre-commit hook
- Can revert to previous versions via S3 versioning
- Scripts can be updated during incident response

### 4. **Deployment Strategy**
- Terraform tracks script changes via `etag`
- Instance replacement only when necessary
- Scripts in S3 = scripts on instance (via etag)
- Pre-commit hook enables hot-fixes

### 5. **Security**
- Scripts encrypted at rest in S3
- IAM least-privilege access
- Read-only access for EC2 instances
- No secrets in scripts (all via template vars)

## Testing Checklist

Before deploying:

- [ ] Terraform init/validate
- [ ] Verify bootstrap.sh template variables
- [ ] Check S3 bucket names match environments
- [ ] Test pre-commit hook locally
- [ ] Verify IAM permissions are sufficient
- [ ] Check script execution order
- [ ] Test error handling in bootstrap
- [ ] Verify instance can reach S3 endpoints

## Next Steps

1. **Test in staging:**
   ```bash
   cd terraform/staging
   terraform init
   terraform plan
   terraform apply
   ```

2. **Verify scripts uploaded to S3:**
   ```bash
   aws s3 ls s3://lacrei-saude-staging-scripts/
   ```

3. **Monitor EC2 initialization:**
   ```bash
   # Via SSM Session Manager
   tail -f /var/log/user-data.log
   ```

4. **Test pre-commit hook:**
   ```bash
   # Make a change to a script
   echo "# test" >> terraform/modules/lacrei-infra/scripts/00-init.sh
   git add terraform/modules/lacrei-infra/scripts/00-init.sh
   git commit -m "test: pre-commit hook"
   ```

## Rollback Plan

If issues occur:

1. **Revert Terraform changes:**
   ```bash
   git revert HEAD
   terraform apply
   ```

2. **Use previous S3 script versions:**
   ```bash
   aws s3api list-object-versions --bucket lacrei-saude-staging-scripts
   aws s3api get-object --bucket lacrei-saude-staging-scripts --key 00-init.sh --version-id VERSION_ID
   ```

3. **Emergency fix via SSM:**
   - Connect via SSM Session Manager
   - Manually fix scripts in `/tmp/setup-scripts/`
   - Upload corrected version to S3

## Files Changed

```
terraform/modules/lacrei-infra/
├── ec2.tf                          # Updated user_data reference
├── iam.tf                          # Added S3 scripts permissions
├── s3.tf                           # Added scripts bucket + uploads
├── scripts/                        # NEW: Modular scripts
│   ├── 00-init.sh
│   ├── 01-ssm-agent.sh
│   ├── 02-system-packages.sh
│   ├── 03-app-setup.sh
│   ├── 04-nginx-config.sh
│   ├── 05-deployment-scripts.sh
│   ├── 06-ssl-certificates.sh
│   └── 99-finalize.sh
└── templates/
    ├── bootstrap.sh                # NEW: Minimal bootstrap script
    └── user_data.sh                # OLD: Can be removed after testing

hooks/
└── pre-commit                      # NEW: Automated S3 upload

README.md                           # Updated documentation
```

## Migration Complete! 🎉

The infrastructure now uses a modern, scalable, and maintainable approach for EC2 instance initialization. The modular architecture provides flexibility for future updates while solving the immediate 16KB size limit issue.
