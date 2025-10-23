---
name: aws-kms-secrets
description: AWS KMSとSecrets Managerを使用して暗号化キー管理、シークレットローテーション、アプリケーションの機密情報保護を実現する方法
---

# AWS KMS / Secrets Manager スキル

## 概要

AWS KMS（Key Management Service）とSecrets Managerは、暗号化キーと機密情報を管理するマネージドサービスです。KMSは暗号化キーを管理し、Secrets Managerはパスワード、APIキー、データベース認証情報などを安全に保存・ローテーションします。

### 2025年の重要なアップデート

- **KMS自動ローテーション**: カスタマイズ可能な間隔（30-365日）
- **Secrets Managerローテーション**: Lambda自動実行
- **マルチリージョンキー**: グローバル暗号化
- **料金**: KMS $1/キー/月、Secrets Manager $0.40/シークレット/月

## 主な使用ケース

### 1. KMSキーの作成と使用

```bash
# カスタマー管理キーの作成
aws kms create-key \
    --description "Application encryption key" \
    --key-usage ENCRYPT_DECRYPT \
    --origin AWS_KMS

KEY_ID=$(aws kms describe-key --key-id alias/app-key --query 'KeyMetadata.KeyId' --output text)

# エイリアスの作成
aws kms create-alias \
    --alias-name alias/app-key \
    --target-key-id $KEY_ID

# 自動ローテーション有効化
aws kms enable-key-rotation --key-id $KEY_ID

# カスタムローテーション期間設定（90日）
aws kms enable-key-rotation \
    --key-id $KEY_ID \
    --rotation-period-in-days 90

# データ暗号化
aws kms encrypt \
    --key-id alias/app-key \
    --plaintext "Sensitive data" \
    --output text \
    --query CiphertextBlob | base64 --decode > encrypted-data.bin

# データ復号化
aws kms decrypt \
    --ciphertext-blob fileb://encrypted-data.bin \
    --output text \
    --query Plaintext | base64 --decode
```

### 2. Secrets Managerでシークレット管理

```bash
# データベース認証情報の保存
aws secretsmanager create-secret \
    --name production/db/credentials \
    --description "Production database credentials" \
    --secret-string '{
        "username": "admin",
        "password": "SecurePassword123!",
        "host": "db.example.com",
        "port": 3306,
        "database": "production"
    }' \
    --kms-key-id alias/app-key

# シークレット取得
SECRET=$(aws secretsmanager get-secret-value \
    --secret-id production/db/credentials \
    --query SecretString \
    --output text)

echo $SECRET | jq -r '.password'

# シークレット更新
aws secretsmanager update-secret \
    --secret-id production/db/credentials \
    --secret-string '{
        "username": "admin",
        "password": "NewSecurePassword456!",
        "host": "db.example.com",
        "port": 3306,
        "database": "production"
    }'
```

### 3. 自動ローテーション

```bash
# RDS自動ローテーションの設定
aws secretsmanager rotate-secret \
    --secret-id production/db/credentials \
    --rotation-lambda-arn arn:aws:lambda:ap-northeast-1:123456789012:function:SecretsManagerRDSRotation \
    --rotation-rules '{
        "AutomaticallyAfterDays": 30,
        "Duration": "2h",
        "ScheduleExpression": "rate(30 days)"
    }'

# カスタムローテーションLambda
cat > rotation-function.py << 'EOF'
import boto3
import json

def lambda_handler(event, context):
    service_client = boto3.client('secretsmanager')
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    metadata = service_client.describe_secret(SecretId=arn)

    if step == "createSecret":
        # 新しいパスワード生成
        new_password = generate_secure_password()
        service_client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps({"password": new_password}),
            VersionStages=['AWSPENDING']
        )

    elif step == "setSecret":
        # データベースのパスワードを更新
        update_database_password(new_password)

    elif step == "testSecret":
        # 新しいパスワードでテスト接続
        test_database_connection(new_password)

    elif step == "finishSecret":
        # AWSCURRENT に昇格
        service_client.update_secret_version_stage(
            SecretId=arn,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId=metadata['VersionIdsToStages']['AWSCURRENT'][0]
        )
EOF
```

### 4. アプリケーションでの使用

```python
"""
Secrets Managerからシークレット取得
"""
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name):
    """
    Secrets Managerからシークレットを取得
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='ap-northeast-1'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

# データベース接続
import pymysql

db_credentials = get_secret('production/db/credentials')

connection = pymysql.connect(
    host=db_credentials['host'],
    user=db_credentials['username'],
    password=db_credentials['password'],
    database=db_credentials['database'],
    port=db_credentials['port']
)
```

### 5. S3暗号化（KMS）

```bash
# S3バケットのデフォルト暗号化
aws s3api put-bucket-encryption \
    --bucket my-encrypted-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
            },
            "BucketKeyEnabled": true
        }]
    }'

# Bucket Keyで99%のKMSコスト削減
```

### 6. EBS暗号化（KMS）

```bash
# アカウントレベルでデフォルト暗号化
aws ec2 enable-ebs-encryption-by-default

# デフォルトKMSキー設定
aws ec2 modify-ebs-default-kms-key-id \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012

# 暗号化済みEBSボリューム作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 100 \
    --volume-type gp3 \
    --encrypted \
    --kms-key-id alias/app-key
```

### 7. マルチリージョンキー

```bash
# プライマリキー作成
aws kms create-key \
    --description "Multi-region application key" \
    --multi-region true

PRIMARY_KEY_ID=$(aws kms describe-key --key-id alias/global-app-key --query 'KeyMetadata.KeyId' --output text)

# レプリカキー作成（別リージョン）
aws kms replicate-key \
    --key-id $PRIMARY_KEY_ID \
    --replica-region us-west-2 \
    --description "Replica in us-west-2"

# グローバルアプリケーションで同じキーを使用可能
```

## ベストプラクティス（2025年版）

### 1. キーポリシーで最小権限

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "Enable IAM policies",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
    "Action": "kms:*",
    "Resource": "*"
  },{
    "Sid": "Allow app role to decrypt",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123456789012:role/AppRole"},
    "Action": ["kms:Decrypt", "kms:DescribeKey"],
    "Resource": "*"
  }]
}
```

### 2. Secrets Managerでローテーション

```bash
# 30日ごとの自動ローテーション必須
# Lambda関数で安全にパスワード更新
```

### 3. KMSキーのタグ付け

```bash
aws kms tag-resource \
    --key-id $KEY_ID \
    --tags TagKey=Environment,TagValue=Production TagKey=Application,TagValue=WebApp
```

## よくある落とし穴と対策

### 1. KMSスロットリング

**症状**: TooManyRequestsException

**対策**: Bucket Key有効化、キャッシング

### 2. Secrets Managerコスト

**症状**: 高額なシークレット料金

**対策**: 不要なシークレット削除、Systems Managerパラメータストア検討（無料）

## リソース

- [KMS Documentation](https://docs.aws.amazon.com/kms/)
- [Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
