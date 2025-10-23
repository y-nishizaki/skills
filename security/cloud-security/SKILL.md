---
name: "cloud-security"
description: >
  クラウドセキュリティの実践を支援します。AWS、Azure、GCPのセキュリティサービス、
  IAM、ネットワークセキュリティ、データ保護、コンテナセキュリティ、CSPM、CWPP、
  クラウドネイティブセキュリティなど、マルチクラウド環境のセキュリティ確保に使用します。
  キーワード - クラウドセキュリティ、AWS、Azure、GCP、IAM、CSPM、CWPP、
  コンテナセキュリティ、Zero Trust。
version: 1.0.0
---

# クラウドセキュリティスキル

## 目的

このスキルは、AWS、Azure、GCPなどのクラウドプラットフォームにおけるセキュリティ対策を
提供します。IAM、ネットワークセキュリティ、データ保護、コンテナセキュリティ、
コンプライアンス監視など、クラウド環境全体のセキュリティを確保するための実践的知識を含みます。

## クラウドセキュリティの責任共有モデル

### 責任分担

**クラウドプロバイダの責任:**
- 物理的セキュリティ
- インフラストラクチャ
- ハードウェア
- ネットワークインフラ

**顧客の責任:**
- データ
- アプリケーション
- アクセス管理
- OS、ミドルウェア（IaaSの場合）
- ネットワーク設定

### サービスモデル別責任

```
IaaS (EC2, Virtual Machines):
└─ 顧客: OS, ミドルウェア, ランタイム, データ, アプリケーション
└─ プロバイダ: 仮想化, サーバー, ストレージ, ネットワーク

PaaS (App Service, Cloud Run):
└─ 顧客: データ, アプリケーション
└─ プロバイダ: OS, ミドルウェア, ランタイム, 仮想化以下

SaaS (Office 365, Salesforce):
└─ 顧客: データ, アクセス制御
└─ プロバイダ: アプリケーション以下すべて
```

## AWS セキュリティ

### IAM (Identity and Access Management)

**IAMポリシー例:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "192.0.2.0/24"
        }
      }
    }
  ]
}
```

**最小権限の原則:**
```bash
# IAMポリシーシミュレータで権限確認
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/test-user \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Access Analyzer でポリシー検証
aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY
```

**IAMロールの使用:**
```python
# EC2インスタンスでIAMロール使用
import boto3

# ロールから自動的に認証情報取得
s3 = boto3.client('s3')
response = s3.list_buckets()
```

### ネットワークセキュリティ

**VPCセキュリティ設計:**
```yaml
# VPC構成例
VPC: 10.0.0.0/16
  Public Subnet (DMZ): 10.0.1.0/24
    - ALB
    - NAT Gateway
  Private Subnet (App): 10.0.10.0/24
    - EC2インスタンス
    - ECS
  Private Subnet (DB): 10.0.20.0/24
    - RDS
```

**セキュリティグループ:**
```bash
# Webサーバー用セキュリティグループ
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Web server security group" \
  --vpc-id vpc-xxxxx

# HTTPSインバウンド許可
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# SSHはVPN/踏み台からのみ
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --source-group sg-bastion
```

**Network ACL:**
```bash
# ステートレスファイアウォール
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --egress false \
  --rule-action allow
```

### データ保護

**S3暗号化:**
```bash
# デフォルト暗号化有効化
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:region:account:key/key-id"
      }
    }]
  }'

# パブリックアクセスブロック
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

**RDS暗号化:**
```bash
# 暗号化RDSインスタンス作成
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:region:account:key/key-id
```

### ログとモニタリング

**CloudTrail:**
```bash
# CloudTrail設定
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail

# ログファイル検証有効化
aws cloudtrail update-trail \
  --name my-trail \
  --enable-log-file-validation
```

**GuardDuty:**
```bash
# GuardDuty有効化
aws guardduty create-detector --enable

# 検出結果取得
aws guardduty list-findings \
  --detector-id <detector-id>
```

**CloudWatch Logs Insights クエリ:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

### セキュリティサービス

**AWS Security Hub:**
```bash
# Security Hub有効化
aws securityhub enable-security-hub

# CIS AWS Foundations Benchmark有効化
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0
```

**AWS Config:**
```yaml
# Config ルール例 - 暗号化されていないS3バケット検出
ConfigRule:
  ConfigRuleName: s3-bucket-encryption-enabled
  Source:
    Owner: AWS
    SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED
  Scope:
    ComplianceResourceTypes:
      - AWS::S3::Bucket
```

## Azure セキュリティ

### Azure Active Directory

**条件付きアクセス:**
```powershell
# Azure AD 条件付きアクセスポリシー
New-AzureADMSConditionalAccessPolicy -DisplayName "Require MFA for Admins" `
  -State "Enabled" `
  -Conditions @{
    Users = @{
      IncludeRoles = @("62e90394-69f5-4237-9190-012177145e10") # Global Admin
    }
    Applications = @{
      IncludeApplications = "All"
    }
  } `
  -GrantControls @{
    BuiltInControls = @("mfa")
  }
```

**Privileged Identity Management (PIM):**
```powershell
# Just-In-Time アクセス
Enable-AzureADMSPrivilegedRoleAssignmentScheduleRequest `
  -RoleDefinitionId "62e90394-69f5-4237-9190-012177145e10" `
  -SubjectId "user-id" `
  -Duration "PT8H"
```

### ネットワークセキュリティ

**Network Security Groups (NSG):**
```bash
# NSGルール作成
az network nsg rule create \
  --resource-group myRG \
  --nsg-name myNSG \
  --name allow-https \
  --priority 100 \
  --source-address-prefixes '*' \
  --destination-port-ranges 443 \
  --protocol Tcp \
  --access Allow
```

**Azure Firewall:**
```bash
# Azure Firewall作成
az network firewall create \
  --name myFirewall \
  --resource-group myRG \
  --location eastus

# アプリケーションルール
az network firewall application-rule create \
  --collection-name app-rules \
  --firewall-name myFirewall \
  --name allow-github \
  --protocols https=443 \
  --source-addresses '*' \
  --target-fqdns '*.github.com' \
  --priority 100 \
  --action Allow \
  --resource-group myRG
```

### データ保護

**Storage Account暗号化:**
```bash
# カスタマーマネージドキー使用
az storage account update \
  --name mystorageaccount \
  --resource-group myRG \
  --encryption-key-source Microsoft.Keyvault \
  --encryption-key-vault https://myvault.vault.azure.net \
  --encryption-key-name mykey
```

**Azure Key Vault:**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Key Vaultからシークレット取得
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)

secret = client.get_secret("database-password")
print(secret.value)
```

### セキュリティセンター

**Microsoft Defender for Cloud:**
```bash
# Defender有効化
az security pricing create \
  --name VirtualMachines \
  --tier Standard

# セキュリティアラート取得
az security alert list
```

## GCP セキュリティ

### IAM

**IAMポリシー:**
```bash
# プロジェクトレベルでIAMロール付与
gcloud projects add-iam-policy-binding my-project \
  --member=user:user@example.com \
  --role=roles/storage.objectViewer

# サービスアカウント作成
gcloud iam service-accounts create my-service-account \
  --display-name="My Service Account"

# サービスアカウントキー作成
gcloud iam service-accounts keys create key.json \
  --iam-account=my-service-account@my-project.iam.gserviceaccount.com
```

**Workload Identity（推奨）:**
```yaml
# Kubernetes ServiceAccountとGCP SAの紐付け
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-ksa
  annotations:
    iam.gke.io/gcp-service-account: my-gsa@my-project.iam.gserviceaccount.com
```

### VPCセキュリティ

**Firewall ルール:**
```bash
# ファイアウォールルール作成
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags web-server

# SSHは特定IPからのみ
gcloud compute firewall-rules create allow-ssh-from-office \
  --allow tcp:22 \
  --source-ranges 203.0.113.0/24 \
  --target-tags bastion
```

**Private Google Access:**
```bash
# プライベートサブネットからGoogle APIアクセス
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --enable-private-ip-google-access
```

### データ保護

**Cloud Storage暗号化:**
```bash
# カスタマーマネージドキー使用
gcloud storage buckets create gs://my-bucket \
  --default-encryption-key=projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key

# バケットポリシー設定（パブリックアクセス防止）
gsutil iam ch -d allUsers:objectViewer gs://my-bucket
```

**Cloud KMS:**
```python
from google.cloud import kms

# KMSで暗号化
client = kms.KeyManagementServiceClient()
key_name = "projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key"

plaintext = b"Sensitive data"
encrypt_response = client.encrypt(request={'name': key_name, 'plaintext': plaintext})
ciphertext = encrypt_response.ciphertext
```

### セキュリティサービス

**Security Command Center:**
```bash
# セキュリティ検出結果取得
gcloud scc findings list organizations/123456789012

# アセット検索
gcloud asset search-all-resources \
  --scope=projects/my-project \
  --query="securityCenterProperties.resourceType:google.compute.Instance"
```

**Web Security Scanner:**
```bash
# スキャン実行
gcloud web-security-scanner scan-runs create \
  --scan-config=projects/my-project/scanConfigs/scan-config-id
```

## コンテナセキュリティ

### Kubernetes セキュリティ

**Pod Security Standards:**
```yaml
# Restrictedポリシー
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

**NetworkPolicy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

### コンテナイメージスキャン

**AWS ECR:**
```bash
# ECRイメージスキャン
aws ecr start-image-scan \
  --repository-name my-app \
  --image-id imageTag=latest

# スキャン結果取得
aws ecr describe-image-scan-findings \
  --repository-name my-app \
  --image-id imageTag=latest
```

**Azure Container Registry:**
```bash
# Microsoft Defender for Containers
az security assessment list \
  --resource-group myRG
```

**GCP Artifact Registry:**
```bash
# Container Scanning有効化（自動）
gcloud artifacts repositories create my-repo \
  --repository-format=docker \
  --location=us-central1

# 脆弱性情報取得
gcloud artifacts docker images list us-central1-docker.pkg.dev/my-project/my-repo \
  --include-occurrences
```

## CSPM (Cloud Security Posture Management)

### ツール

**Prowler (AWS/Azure/GCP):**
```bash
# AWS スキャン
prowler aws -M csv html

# CIS Benchmark チェック
prowler aws -c cis_level1

# 特定サービスのみ
prowler aws -s s3,iam
```

**CloudSploit:**
```bash
# インストール
npm install -g cloudsploit

# スキャン実行
cloudsploit scan --config config.json
```

### コンプライアンスフレームワーク

**CIS Benchmarks 実装例:**
```python
def check_s3_bucket_public_access(bucket_name):
    """
    CIS AWS 2.1.5: S3バケットのパブリックアクセス確認
    """
    s3 = boto3.client('s3')

    try:
        result = s3.get_public_access_block(Bucket=bucket_name)
        config = result['PublicAccessBlockConfiguration']

        if all([
            config['BlockPublicAcls'],
            config['IgnorePublicAcls'],
            config['BlockPublicPolicy'],
            config['RestrictPublicBuckets']
        ]):
            return "PASS"
        else:
            return "FAIL"
    except:
        return "FAIL"
```

## Zero Trust アーキテクチャ

### 実装

**BeyondCorp (Google):**
```yaml
# Identity-Aware Proxy
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata:
  name: iap-config
spec:
  iap:
    enabled: true
    oauthclientCredentials:
      secretName: oauth-client-secret
```

**AWS Verified Access:**
```bash
# Verified Access エンドポイント作成
aws ec2 create-verified-access-endpoint \
  --verified-access-group-id vag-xxxxx \
  --attachment-type vpc \
  --domain-certificate-arn arn:aws:acm:... \
  --application-domain app.example.com \
  --endpoint-type network-interface
```

## インシデント対応

### クラウドフォレンジック

**AWS インスタンススナップショット:**
```bash
# 侵害されたEC2インスタンスのスナップショット
INSTANCE_ID=i-xxxxx
VOLUME_ID=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' \
  --output text)

# スナップショット作成
aws ec2 create-snapshot \
  --volume-id $VOLUME_ID \
  --description "Forensic snapshot - incident-001" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Incident,Value=001}]'

# インスタンス隔離（セキュリティグループ変更）
aws ec2 modify-instance-attribute \
  --instance-id $INSTANCE_ID \
  --groups sg-isolation
```

**Azure ディスクスナップショット:**
```bash
# ディスクスナップショット
az snapshot create \
  --resource-group myRG \
  --name incident-snapshot \
  --source /subscriptions/.../disks/osdisk

# VMネットワーク隔離
az vm nic set \
  --vm-name compromised-vm \
  --resource-group myRG \
  --nics isolated-nic
```

## ベストプラクティス

1. **IDベースのセキュリティ**
   - IAMロール/サービスアカウント使用
   - 最小権限原則
   - MFA必須化

2. **ネットワークセグメンテーション**
   - VPC/VNet分離
   - セキュリティグループ/NSG最小化
   - プライベートサブネット活用

3. **データ保護**
   - 保存時暗号化
   - 通信時暗号化（TLS）
   - キー管理サービス使用

4. **ロギングとモニタリング**
   - 全APIコールログ記録
   - 異常検知アラート
   - SIEM統合

5. **自動化**
   - Infrastructure as Code
   - セキュリティスキャン自動化
   - 自動修復

## 参考リソース

- AWS Well-Architected Framework - Security Pillar
- Azure Security Benchmark
- GCP Security Best Practices
- CIS Benchmarks for Cloud
- NIST SP 800-210 Cloud Security

## 注意事項

- 責任共有モデルの理解
- マルチクラウド環境の複雑性
- コストとセキュリティのバランス
- 定期的なセキュリティレビュー
