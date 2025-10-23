---
name: aws-multi-account
description: AWS Organizationsを使用してマルチアカウント戦略を実装し、Control Tower、SCPs、アカウント分離でガバナンス、セキュリティ、コスト管理を強化する方法
---

# AWS Multi-Account Architecture スキル

## 概要

AWS Organizationsは、複数のAWSアカウントを一元管理するサービスで、Control TowerとSCPs（Service Control Policies）を組み合わせることで、大規模環境のガバナンス、セキュリティ、コンプライアンスを自動化します。

## 主な使用ケース

### 1. AWS Organizations基本セットアップ

```bash
# Organizationアカウント作成（Management Account）
aws organizations create-organization \
    --feature-set ALL

# Organization情報確認
aws organizations describe-organization

# 新規アカウント作成
aws organizations create-account \
    --email production@example.com \
    --account-name "Production Account" \
    --role-name OrganizationAccountAccessRole

# アカウント招待（既存アカウント）
aws organizations invite-account-to-organization \
    --target Id=123456789012,Type=ACCOUNT
```

### 2. OU（Organizational Unit）階層構造

```bash
# ルートOU取得
ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

# OU作成
aws organizations create-organizational-unit \
    --parent-id $ROOT_ID \
    --name Production

aws organizations create-organizational-unit \
    --parent-id $ROOT_ID \
    --name Development

aws organizations create-organizational-unit \
    --parent-id $ROOT_ID \
    --name Security

# アカウントをOUに移動
aws organizations move-account \
    --account-id 123456789012 \
    --source-parent-id $ROOT_ID \
    --destination-parent-id ou-prod-123
```

```text
推奨OU構造（2025年版）:

Root
├── Security
│   ├── Log Archive Account
│   └── Security Audit Account
├── Infrastructure
│   ├── Network Account
│   └── Shared Services Account
├── Workloads
│   ├── Production OU
│   │   ├── App1 Production
│   │   └── App2 Production
│   ├── Staging OU
│   └── Development OU
└── Suspended
    └── （削除予定アカウント）
```

### 3. SCPs（Service Control Policies）

```bash
# SCP作成（S3パブリックアクセス禁止）
cat > deny-s3-public.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyS3PublicAccess",
    "Effect": "Deny",
    "Action": [
      "s3:PutAccountPublicAccessBlock"
    ],
    "Resource": "*",
    "Condition": {
      "Bool": {
        "s3:BlockPublicAcls": "false",
        "s3:BlockPublicPolicy": "false",
        "s3:IgnorePublicAcls": "false",
        "s3:RestrictPublicBuckets": "false"
      }
    }
  }]
}
EOF

aws organizations create-policy \
    --content file://deny-s3-public.json \
    --description "Deny S3 public access" \
    --name DenyS3PublicAccess \
    --type SERVICE_CONTROL_POLICY

# SCPをOUに適用
aws organizations attach-policy \
    --policy-id p-abc123 \
    --target-id ou-prod-123
```

```json
// リージョン制限SCP
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyAllOutsideJapan",
    "Effect": "Deny",
    "NotAction": [
      "cloudfront:*",
      "iam:*",
      "route53:*",
      "support:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": [
          "ap-northeast-1",
          "ap-northeast-3"
        ]
      }
    }
  }]
}
```

```json
// ルートユーザー保護SCP
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyRootAccount",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringLike": {
        "aws:PrincipalArn": "arn:aws:iam::*:root"
      }
    }
  }]
}
```

### 4. AWS Control Tower

```bash
# Control Tower有効化（コンソール経由推奨）
# 1. Management Accountでコンソールにログイン
# 2. Control Towerサービスに移動
# 3. 「Set up landing zone」をクリック

# OU登録（CLI）
aws controltower register-organizational-unit \
    --organizational-unit-id ou-prod-123

# アカウントファクトリーで新規アカウント作成
aws servicecatalog provision-product \
    --product-id prod-abc123 \
    --provisioning-artifact-id pa-def456 \
    --provisioned-product-name "production-app1" \
    --provisioning-parameters '[
        {"Key": "AccountEmail", "Value": "app1-prod@example.com"},
        {"Key": "AccountName", "Value": "App1 Production"},
        {"Key": "ManagedOrganizationalUnit", "Value": "Production"},
        {"Key": "SSOUserEmail", "Value": "admin@example.com"},
        {"Key": "SSOUserFirstName", "Value": "Admin"},
        {"Key": "SSOUserLastName", "Value": "User"}
    ]'
```

### 5. Consolidated Billing（一括請求）

```bash
# コスト配分タグ有効化
aws ce update-cost-allocation-tags-status \
    --cost-allocation-tags-status '[
        {"TagKey": "Environment", "Status": "Active"},
        {"TagKey": "Project", "Status": "Active"},
        {"TagKey": "CostCenter", "Status": "Active"}
    ]'

# 予算アラート作成
aws budgets create-budget \
    --account-id 123456789012 \
    --budget '{
        "BudgetName": "Monthly-Production-Budget",
        "BudgetLimit": {"Amount": "10000", "Unit": "USD"},
        "TimeUnit": "MONTHLY",
        "BudgetType": "COST",
        "CostFilters": {"TagKeyValue": ["Environment$Production"]}
    }' \
    --notifications-with-subscribers '[{
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 80,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [{
            "SubscriptionType": "EMAIL",
            "Address": "finance@example.com"
        }]
    }]'
```

### 6. Cross-Account Access

```bash
# 信頼関係ポリシー（AssumeRole）
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::111111111111:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "unique-external-id"
      }
    }
  }]
}
EOF

# クロスアカウントロール作成
aws iam create-role \
    --role-name CrossAccountAdminRole \
    --assume-role-policy-document file://trust-policy.json

# ポリシーアタッチ
aws iam attach-role-policy \
    --role-name CrossAccountAdminRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

```python
# Python SDK - クロスアカウントアクセス
import boto3

sts_client = boto3.client('sts')

# AssumeRole
assumed_role = sts_client.assume_role(
    RoleArn='arn:aws:iam::222222222222:role/CrossAccountAdminRole',
    RoleSessionName='cross-account-session',
    ExternalId='unique-external-id'
)

credentials = assumed_role['Credentials']

# 別アカウントのS3にアクセス
s3 = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)

s3.list_buckets()
```

## ベストプラクティス（2025年版）

### 1. 必須アカウント構成

```text
Management Account:
- Organizations管理のみ
- ワークロード実行禁止
- MFA必須

Security Account:
- GuardDuty Delegated Administrator
- Security Hub集約
- CloudTrail Lake

Log Archive Account:
- 全アカウントのCloudTrailログ
- S3 Object Lock有効
- ライフサイクルポリシー（7年保持）

Network Account:
- Transit Gateway
- VPC共有（RAM）
- Direct Connect/VPN

各環境専用アカウント:
- Production、Staging、Development
- 環境間の完全分離
```

### 2. SCP階層戦略

```text
上位OU（広範囲な制限）:
- リージョン制限
- ルートユーザー禁止
- 監査ログ保護

下位OU（具体的な制限）:
- インスタンスタイプ制限
- 特定サービス禁止
- タグ付け強制

原則:
- 5つまでのSCP/OU（Control Tower制限）
- テスト環境で検証後に本番適用
- Deny優先（明示的拒否）
```

### 3. Control Tower Guardrails

```bash
# Preventive Guardrails（SCPベース）
- S3パブリックアクセス禁止
- CloudTrail無効化禁止
- MFA削除保護

# Detective Guardrails（AWS Configベース）
- 未使用IAMユーザー検出
- セキュリティグループ過剰許可検出
- S3暗号化未設定検出
```

### 4. AWS Single Sign-On（SSO）統合

```bash
# SSO有効化（Control Towerで自動設定）
aws sso-admin create-permission-set \
    --instance-arn arn:aws:sso:::instance/ssoins-abc123 \
    --name ProductionAdmin \
    --description "Production environment administrator" \
    --session-duration PT8H

# Managed Policy添付
aws sso-admin attach-managed-policy-to-permission-set \
    --instance-arn arn:aws:sso:::instance/ssoins-abc123 \
    --permission-set-arn arn:aws:sso:::permissionSet/ps-abc123 \
    --managed-policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# アカウント割り当て
aws sso-admin create-account-assignment \
    --instance-arn arn:aws:sso:::instance/ssoins-abc123 \
    --target-id 123456789012 \
    --target-type AWS_ACCOUNT \
    --permission-set-arn arn:aws:sso:::permissionSet/ps-abc123 \
    --principal-type USER \
    --principal-id user-abc123
```

### 5. Organizationレベルのサービス統合

```bash
# CloudTrail組織レベル有効化
aws cloudtrail create-trail \
    --name organization-trail \
    --s3-bucket-name org-cloudtrail-logs \
    --is-organization-trail

# GuardDuty Delegated Administrator設定
aws guardduty enable-organization-admin-account \
    --admin-account-id 333333333333

# Security Hub集約
aws securityhub enable-organization-admin-account \
    --admin-account-id 333333333333
```

## よくある失敗パターン

### 1. Management Accountでワークロード実行

```text
問題: Management Accountで本番アプリケーション稼働
解決: 専用ワークロードアカウント作成

Management Account用途:
- Organizations管理
- 一括請求
- SCPs管理
のみ
```

### 2. SCP適用前のテスト不足

```text
問題: 本番OUに直接SCPを適用してサービス停止
解決: テストOU作成 → テストアカウント検証 → 本番適用

# テストOU作成
aws organizations create-organizational-unit \
    --parent-id $ROOT_ID \
    --name TestOU
```

### 3. ルートメールアドレス管理の欠如

```text
問題: 全アカウントで同じメールアドレス使用
解決: アカウント毎に一意のメールアドレス

推奨形式:
aws+prod-app1@example.com
aws+dev-app1@example.com
aws+security@example.com
```

## リソース

- [AWS Organizations Documentation](https://docs.aws.amazon.com/organizations/)
- [Control Tower Documentation](https://docs.aws.amazon.com/controltower/)
- [Multi-Account Best Practices](https://aws.amazon.com/organizations/getting-started/best-practices/)
