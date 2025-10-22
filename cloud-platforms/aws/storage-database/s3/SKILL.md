---
name: aws-s3
description: AWS S3（Simple Storage Service）を使用してオブジェクトストレージを管理し、ストレージクラス、ライフサイクルポリシー、バージョニングを活用してコストを最適化する方法
---

# AWS S3 スキル

## 概要

Amazon S3（Simple Storage Service）は、業界をリードするスケーラビリティ、データ可用性、セキュリティ、パフォーマンスを提供するオブジェクトストレージサービスです。このスキルでは、S3のストレージクラス、ライフサイクルポリシー、バージョニング、暗号化、アクセス制御を駆使して、コスト効率の高いストレージ戦略を構築する方法を学びます。

### 2025年の重要なアップデート

- **S3 Intelligent-Tiering**: すべての新規ワークロードのデフォルト推奨
- **S3 Express One Zone**: 1桁ミリ秒のレイテンシ（高頻度アクセス用）
- **ライフサイクルポリシーの自動化**: 組織規模での自動適用

## 主な使用ケース

### 1. 静的Webサイトホスティング

S3で静的WebサイトをホストしCloudFrontで配信します。

```bash
# バケットの作成
aws s3 mb s3://my-static-website --region ap-northeast-1

# 静的Webサイトホスティングの有効化
aws s3 website s3://my-static-website/ \
    --index-document index.html \
    --error-document error.html

# ファイルのアップロード
aws s3 sync ./website/ s3://my-static-website/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --exclude "index.html"

# HTMLファイルは短いキャッシュ期間
aws s3 sync ./website/ s3://my-static-website/ \
    --exclude "*" \
    --include "*.html" \
    --cache-control "public, max-age=3600"

# バケットポリシーで読み取りアクセスを許可
cat > bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-static-website/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket my-static-website \
    --policy file://bucket-policy.json
```

### 2. データレイク構築

大量のデータを効率的に保存し、Athena、Glue、EMRで分析します。

```bash
# データレイクバケットの作成（暗号化必須）
aws s3 mb s3://company-datalake --region ap-northeast-1

# デフォルト暗号化の有効化（SSE-S3）
aws s3api put-bucket-encryption \
    --bucket company-datalake \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'

# バージョニングの有効化（誤削除対策）
aws s3api put-bucket-versioning \
    --bucket company-datalake \
    --versioning-configuration Status=Enabled

# パーティション構造でデータを保存
# s3://company-datalake/raw/year=2025/month=01/day=22/data.parquet
aws s3 cp data.parquet s3://company-datalake/raw/year=2025/month=01/day=22/ \
    --storage-class INTELLIGENT_TIERING
```

### 3. S3 Intelligent-Tiering（2025年推奨）

アクセスパターンに基づいて自動的にストレージクラスを最適化します。

```bash
# 新規データを直接Intelligent-Tieringにアップロード
aws s3 cp large-file.zip s3://my-bucket/ \
    --storage-class INTELLIGENT_TIERING

# バケット全体のデフォルトをIntelligent-Tieringに設定
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket my-bucket \
    --id default-config \
    --intelligent-tiering-configuration file://it-config.json

# it-config.json
cat > it-config.json << 'EOF'
{
  "Id": "default-config",
  "Status": "Enabled",
  "Tierings": [
    {
      "Days": 90,
      "AccessTier": "ARCHIVE_ACCESS"
    },
    {
      "Days": 180,
      "AccessTier": "DEEP_ARCHIVE_ACCESS"
    }
  ]
}
EOF
```

**コスト削減効果**:
- 30日後（低頻度アクセス層）: 40%削減
- 90日後（アーカイブ即時アクセス層）: 68%削減
- 180日後（ディープアーカイブアクセス層）: 95%削減

### 4. ライフサイクルポリシー

オブジェクトを自動的に移行・削除してコストを最適化します。

```bash
# ライフサイクルポリシーの設定
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration file://lifecycle-policy.json

# lifecycle-policy.json
cat > lifecycle-policy.json << 'EOF'
{
  "Rules": [
    {
      "Id": "Move to Intelligent-Tiering",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "Transitions": [
        {
          "Days": 0,
          "StorageClass": "INTELLIGENT_TIERING"
        }
      ]
    },
    {
      "Id": "Delete old versions",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30,
        "NewerNoncurrentVersions": 3
      }
    },
    {
      "Id": "Clean incomplete multipart uploads",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
EOF
```

**重要ポイント**:
- 現行バージョンと非現行バージョンで別々のルールを定義
- `NewerNoncurrentVersions`で最新N個を保持
- 不完全なマルチパートアップロードを定期的にクリーンアップ

### 5. S3バージョニングとレプリケーション

データ保護とディザスタリカバリを実現します。

```bash
# バージョニング有効化
aws s3api put-bucket-versioning \
    --bucket source-bucket \
    --versioning-configuration Status=Enabled

# クロスリージョンレプリケーション（CRR）の設定
aws s3api put-bucket-replication \
    --bucket source-bucket \
    --replication-configuration file://replication-config.json

# replication-config.json
cat > replication-config.json << 'EOF'
{
  "Role": "arn:aws:iam::123456789012:role/S3ReplicationRole",
  "Rules": [
    {
      "Id": "ReplicateAll",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {
            "Minutes": 15
          }
        },
        "Metrics": {
          "Status": "Enabled",
          "EventThreshold": {
            "Minutes": 15
          }
        },
        "StorageClass": "INTELLIGENT_TIERING"
      },
      "DeleteMarkerReplication": {
        "Status": "Enabled"
      }
    }
  ]
}
EOF

# IAMロールの作成
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name S3ReplicationRole \
    --assume-role-policy-document file://trust-policy.json
```

### 6. S3イベント通知

オブジェクトの変更を検知してLambda、SQS、SNSに通知します。

```bash
# Lambda関数をトリガー
aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration file://notification-config.json

# notification-config.json
cat > notification-config.json << 'EOF'
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "ProcessNewImages",
      "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-1:123456789012:function:image-processor",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "uploads/images/"
            },
            {
              "Name": "suffix",
              "Value": ".jpg"
            }
          ]
        }
      }
    }
  ],
  "QueueConfigurations": [
    {
      "Id": "SendToQueue",
      "QueueArn": "arn:aws:sqs:ap-northeast-1:123456789012:s3-events",
      "Events": ["s3:ObjectCreated:Put"]
    }
  ]
}
EOF
```

### 7. S3 Access Points（マルチテナント管理）

複数のアプリケーションやチームで同じバケットを共有します。

```bash
# Access Pointの作成
aws s3control create-access-point \
    --account-id 123456789012 \
    --name analytics-team-ap \
    --bucket my-shared-bucket \
    --vpc-configuration VpcId=vpc-12345678

# Access Pointポリシー
cat > ap-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/AnalyticsTeamRole"
      },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:ap-northeast-1:123456789012:accesspoint/analytics-team-ap/object/*",
      "Condition": {
        "StringEquals": {
          "s3:prefix": "analytics/*"
        }
      }
    }
  ]
}
EOF

aws s3control put-access-point-policy \
    --account-id 123456789012 \
    --name analytics-team-ap \
    --policy file://ap-policy.json
```

### 8. S3 Object Lock（WORM: Write Once Read Many）

コンプライアンス要件に対応した削除不可能なデータ保存です。

```bash
# Object Lock有効化（バケット作成時のみ）
aws s3api create-bucket \
    --bucket compliance-bucket \
    --region ap-northeast-1 \
    --create-bucket-configuration LocationConstraint=ap-northeast-1 \
    --object-lock-enabled-for-bucket

# バケットバージョニング有効化（必須）
aws s3api put-bucket-versioning \
    --bucket compliance-bucket \
    --versioning-configuration Status=Enabled

# デフォルトObject Lock設定
aws s3api put-object-lock-configuration \
    --bucket compliance-bucket \
    --object-lock-configuration '{
        "ObjectLockEnabled": "Enabled",
        "Rule": {
            "DefaultRetention": {
                "Mode": "GOVERNANCE",
                "Days": 365
            }
        }
    }'

# 個別オブジェクトにCompliance モードを適用
aws s3api put-object \
    --bucket compliance-bucket \
    --key important-document.pdf \
    --body document.pdf \
    --object-lock-mode COMPLIANCE \
    --object-lock-retain-until-date 2026-12-31T23:59:59Z
```

**モードの違い**:
- **GOVERNANCE**: 特権ユーザーが上書き可能
- **COMPLIANCE**: 誰も削除・上書き不可（ルートユーザーでも）

## 思考プロセス

S3を使用したストレージ戦略を設計する際の段階的な思考プロセスです。

### フェーズ1: ストレージクラスの選択

```python
"""
S3ストレージクラス選択ロジック（2025年版）
"""

def choose_storage_class(access_pattern):
    """
    アクセスパターンに基づいて最適なストレージクラスを選択
    """
    if access_pattern.access_frequency == 'unknown':
        # 2025年のデフォルト推奨
        return 'INTELLIGENT_TIERING'

    if access_pattern.access_frequency == 'frequent':
        if access_pattern.latency_requirement == 'single_digit_ms':
            return 'EXPRESS_ONE_ZONE'  # 2025年新機能
        else:
            return 'STANDARD'

    if access_pattern.access_frequency == 'infrequent':
        if access_pattern.availability_requirement == 'high':
            return 'STANDARD_IA'  # Multi-AZ
        else:
            return 'ONEZONE_IA'  # Single-AZ（20%安い）

    if access_pattern.access_frequency == 'archive':
        if access_pattern.retrieval_time == 'instant':
            return 'GLACIER_INSTANT_RETRIEVAL'  # ミリ秒
        elif access_pattern.retrieval_time == 'flexible':
            return 'GLACIER_FLEXIBLE_RETRIEVAL'  # 1-5分または1-12時間
        else:
            return 'GLACIER_DEEP_ARCHIVE'  # 12-48時間（最安）

    # デフォルトはIntelligent-Tiering
    return 'INTELLIGENT_TIERING'

# 使用例
class AccessPattern:
    def __init__(self):
        self.access_frequency = 'unknown'
        self.latency_requirement = 'standard'
        self.availability_requirement = 'high'
        self.retrieval_time = 'instant'

pattern = AccessPattern()
pattern.access_frequency = 'unknown'
storage_class = choose_storage_class(pattern)
print(f"推奨ストレージクラス: {storage_class}")
# 出力: INTELLIGENT_TIERING
```

### フェーズ2: ライフサイクルポリシーの設計

```python
"""
ライフサイクルポリシー生成ツール
"""
import json

def generate_lifecycle_policy(config):
    """
    設定に基づいてライフサイクルポリシーを生成
    """
    rules = []

    # ルール1: Intelligent-Tieringへの移行
    if config.get('use_intelligent_tiering'):
        rules.append({
            'Id': 'Move to Intelligent-Tiering',
            'Status': 'Enabled',
            'Filter': {'Prefix': config.get('prefix', '')},
            'Transitions': [{
                'Days': 0,
                'StorageClass': 'INTELLIGENT_TIERING'
            }]
        })

    # ルール2: 古いバージョンの削除
    if config.get('delete_old_versions'):
        rules.append({
            'Id': 'Delete old versions',
            'Status': 'Enabled',
            'Filter': {'Prefix': config.get('prefix', '')},
            'NoncurrentVersionExpiration': {
                'NoncurrentDays': config.get('version_retention_days', 30),
                'NewerNoncurrentVersions': config.get('versions_to_keep', 3)
            }
        })

    # ルール3: 不完全マルチパートアップロードの削除
    rules.append({
        'Id': 'Clean incomplete uploads',
        'Status': 'Enabled',
        'Filter': {'Prefix': ''},
        'AbortIncompleteMultipartUpload': {
            'DaysAfterInitiation': 7
        }
    })

    # ルール4: 一時ファイルの自動削除
    if config.get('temp_files_prefix'):
        rules.append({
            'Id': 'Delete temp files',
            'Status': 'Enabled',
            'Filter': {'Prefix': config.get('temp_files_prefix')},
            'Expiration': {
                'Days': config.get('temp_files_retention_days', 7)
            }
        })

    return {'Rules': rules}

# 使用例
config = {
    'use_intelligent_tiering': True,
    'delete_old_versions': True,
    'version_retention_days': 30,
    'versions_to_keep': 5,
    'temp_files_prefix': 'tmp/',
    'temp_files_retention_days': 3
}

policy = generate_lifecycle_policy(config)
print(json.dumps(policy, indent=2))
```

### フェーズ3: セキュリティとアクセス制御

```bash
# S3バケットポリシー生成（最小権限の原則）
cat > secure-bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-secure-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-secure-bucket",
        "arn:aws:s3:::my-secure-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "AllowSpecificRoleAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/AppServerRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-secure-bucket/app-data/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket my-secure-bucket \
    --policy file://secure-bucket-policy.json

# パブリックアクセスブロックの有効化（2025年必須）
aws s3api put-public-access-block \
    --bucket my-secure-bucket \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### フェーズ4: パフォーマンス最適化

```python
"""
大容量ファイルのマルチパートアップロード
"""
import boto3
from boto3.s3.transfer import TransferConfig

def upload_large_file(file_path, bucket, key):
    """
    マルチパートアップロードで大容量ファイルを効率的にアップロード
    """
    # TransferConfigで並列アップロードを設定
    config = TransferConfig(
        multipart_threshold=1024 * 25,  # 25 MB
        max_concurrency=10,
        multipart_chunksize=1024 * 25,  # 25 MB
        use_threads=True
    )

    s3 = boto3.client('s3')

    # プログレスコールバック
    class ProgressPercentage:
        def __init__(self, filename):
            self._filename = filename
            self._size = float(os.path.getsize(filename))
            self._seen_so_far = 0
            self._lock = threading.Lock()

        def __call__(self, bytes_amount):
            with self._lock:
                self._seen_so_far += bytes_amount
                percentage = (self._seen_so_far / self._size) * 100
                print(f"\r{self._filename}: {self._seen_so_far} / {self._size} ({percentage:.2f}%)", end='')

    # アップロード実行
    s3.upload_file(
        file_path,
        bucket,
        key,
        Config=config,
        Callback=ProgressPercentage(file_path),
        ExtraArgs={
            'StorageClass': 'INTELLIGENT_TIERING',
            'ServerSideEncryption': 'AES256',
            'Metadata': {
                'uploaded-by': 'automated-process',
                'upload-date': '2025-01-22'
            }
        }
    )

    print(f"\nアップロード完了: s3://{bucket}/{key}")

# 使用例
upload_large_file('large-video.mp4', 'my-media-bucket', 'videos/large-video.mp4')
```

### フェーズ5: コスト最適化の監視

```bash
# S3 Storage Lensでコストと使用状況を分析
aws s3control put-storage-lens-configuration \
    --account-id 123456789012 \
    --config-id default-dashboard \
    --storage-lens-configuration file://storage-lens-config.json

# storage-lens-config.json
cat > storage-lens-config.json << 'EOF'
{
  "Id": "default-dashboard",
  "AccountLevel": {
    "ActivityMetrics": {
      "IsEnabled": true
    },
    "BucketLevel": {
      "ActivityMetrics": {
        "IsEnabled": true
      },
      "PrefixLevel": {
        "StorageMetrics": {
          "IsEnabled": true,
          "SelectionCriteria": {
            "Delimiter": "/",
            "MaxDepth": 5,
            "MinStorageBytesPercentage": 1.0
          }
        }
      }
    }
  },
  "IsEnabled": true,
  "DataExport": {
    "S3BucketDestination": {
      "OutputSchemaVersion": "V_1",
      "Format": "Parquet",
      "AccountId": "123456789012",
      "Arn": "arn:aws:s3:::storage-lens-reports",
      "Prefix": "storage-lens-reports/"
    }
  }
}
EOF

# CloudWatchメトリクスでストレージコストを監視
aws cloudwatch put-metric-alarm \
    --alarm-name s3-storage-cost-high \
    --alarm-description "S3 storage cost exceeds threshold" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=ServiceName,Value=AmazonS3 Name=Currency,Value=USD
```

## ベストプラクティス（2025年版）

### 1. Intelligent-Tieringをデフォルトに

**推奨**: すべての新規ワークロードでIntelligent-Tieringを使用

```bash
# バケットのデフォルトストレージクラスをIntelligent-Tieringに設定
# （注: S3にはデフォルトストレージクラス設定がないため、アプリケーションレベルで実装）

# Python Boto3での実装例
import boto3

s3 = boto3.client('s3')

def upload_with_intelligent_tiering(bucket, key, file_path):
    """デフォルトでIntelligent-Tieringを使用"""
    s3.upload_file(
        file_path,
        bucket,
        key,
        ExtraArgs={'StorageClass': 'INTELLIGENT_TIERING'}
    )
```

**理由**:
- アクセスパターンが不明な場合でも自動最適化
- 30-60%のコスト削減（典型的なワークロード）
- 監視費用: わずか$0.0025/1000オブジェクト

### 2. バージョニングとライフサイクルポリシーの組み合わせ

```bash
# バージョニング + ライフサイクルで誤削除を防ぎつつコスト管理
cat > versioning-lifecycle.json << 'EOF'
{
  "Rules": [
    {
      "Id": "Keep recent versions, archive old ones",
      "Status": "Enabled",
      "Filter": {"Prefix": ""},
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 30,
          "StorageClass": "GLACIER_INSTANT_RETRIEVAL"
        },
        {
          "NoncurrentDays": 90,
          "StorageClass": "GLACIER_DEEP_ARCHIVE"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 365,
        "NewerNoncurrentVersions": 5
      }
    }
  ]
}
EOF
```

**ポイント**: 最新5バージョンを保持、それ以前は1年後に削除

### 3. 暗号化とセキュリティのレイヤー化

```bash
# レイヤー1: バケットレベルのデフォルト暗号化
aws s3api put-bucket-encryption \
    --bucket my-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
            },
            "BucketKeyEnabled": true
        }]
    }'

# レイヤー2: バケットポリシーで非暗号化アップロードを拒否（既出）

# レイヤー3: IAMポリシーで最小権限
cat > iam-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/app-data/${aws:username}/*"
    }
  ]
}
EOF
```

**Bucket Key有効化のメリット**:
- KMS APIコールを99%削減
- KMSコストを大幅削減

### 4. CloudFrontとの統合

```bash
# CloudFront Origin Access Identity（OAI）の作成
aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config \
        CallerReference="my-oai-$(date +%s)",Comment="OAI for my-bucket"

# S3バケットポリシーでCloudFrontからのアクセスのみ許可
cat > cloudfront-bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAI",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ABCDEFGHIJK"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
EOF
```

### 5. S3 Transfer Accelerationで高速アップロード

```bash
# Transfer Accelerationの有効化
aws s3api put-bucket-accelerate-configuration \
    --bucket my-global-bucket \
    --accelerate-configuration Status=Enabled

# Transfer Accelerationエンドポイントを使用
aws s3 cp large-file.zip s3://my-global-bucket/ \
    --endpoint-url https://s3-accelerate.amazonaws.com \
    --region us-west-2
```

**適用ケース**:
- 世界中からのアップロード（50%以上高速化）
- 大容量ファイル（GB単位）
- 追加コスト: $0.04/GB（通常転送より）

### 6. S3 Select/Glacier Selectでデータ転送量削減

```bash
# S3 Selectで必要なデータのみ取得（CSV例）
aws s3api select-object-content \
    --bucket my-bucket \
    --key data/users.csv \
    --expression "SELECT * FROM S3Object WHERE age > 30" \
    --expression-type SQL \
    --input-serialization '{"CSV": {"FileHeaderInfo": "USE", "RecordDelimiter": "\n", "FieldDelimiter": ","}}' \
    --output-serialization '{"CSV": {}}' \
    output.csv
```

**メリット**:
- データ転送量を最大80%削減
- 処理時間を最大400%高速化

## よくある落とし穴と対策

### 1. バージョニング有効化後のコスト爆発

**症状**: バケットのストレージコストが予想外に高騰

**原因**: 古いバージョンが自動削除されず蓄積

**対策**:

```bash
# 現在のバージョン数を確認
aws s3api list-object-versions \
    --bucket my-bucket \
    --max-keys 1000 \
    --query 'length(Versions)'

# 非現行バージョンのストレージ使用量を確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=my-bucket Name=StorageType,Value=StandardStorage \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 86400 \
    --statistics Average

# ライフサイクルポリシーで古いバージョンを削除（対策済み）
```

### 2. リクエストコストの見落とし

**症状**: 大量の小さなファイルでコストが高い

**原因**: GETリクエストが数百万回/日発生

**対策**:

```bash
# CloudFrontでキャッシュしてS3リクエストを削減
# CloudFront作成（TTL長め）

# S3 Select で複数オブジェクトを1回のリクエストで取得

# バッチ処理: 小さなファイルを結合
aws s3api put-object \
    --bucket my-bucket \
    --key combined/data-2025-01-22.json \
    --body combined-data.json
```

**コスト比較**:
- 1,000,000ファイル × $0.0004/1000 GET = $400/月
- CloudFrontキャッシュヒット率90% → $40/月

### 3. クロスリージョン転送コストの見落とし

**症状**: 予想外のデータ転送料金

**原因**: 異なるリージョンからのアクセス

**対策**:

```bash
# 同一リージョンのリソースからアクセス（無料）
# EC2 → S3（同一リージョン）: 無料

# クロスリージョンアクセスが必要な場合はレプリケーション
aws s3api put-bucket-replication \
    --bucket us-east-1-bucket \
    --replication-configuration file://crr-config.json
```

**コスト比較**:
- クロスリージョン転送: $0.02/GB
- レプリケーション: $0.02/GB（1回のみ）+ 各リージョンでのストレージコスト

### 4. Glacier取り出しコストの予期しない高騰

**症状**: Glacierからの大量取り出しで高額請求

**原因**: Expedited取り出し（高速だが高額）を多用

**対策**:

```bash
# Bulk取り出し（5-12時間）を使用
aws s3api restore-object \
    --bucket my-archive-bucket \
    --key archived-file.zip \
    --restore-request '{
        "Days": 7,
        "GlacierJobParameters": {
            "Tier": "Bulk"
        }
    }'
```

**コスト比較（1TB取り出し）**:
- Expedited: $30 + $0.03/GB = $60.72
- Standard: $10 + $0.01/GB = $20.48
- Bulk: $2.50 + $0.0025/GB = $5.06

### 5. 不完全なマルチパートアップロードの蓄積

**症状**: ストレージコストが予想より高い

**原因**: 失敗したマルチパートアップロードが削除されていない

**検出と対策**:

```bash
# 不完全なマルチパートアップロードを確認
aws s3api list-multipart-uploads --bucket my-bucket

# 手動削除
aws s3api abort-multipart-upload \
    --bucket my-bucket \
    --key large-file.zip \
    --upload-id UPLOAD_ID

# ライフサイクルポリシーで自動削除（推奨、既出）
```

## 判断ポイント

### ストレージクラス選択マトリクス（2025年版）

| アクセス頻度 | 取り出し時間 | 可用性要件 | 推奨ストレージクラス | コスト（GB/月） |
|------------|------------|----------|------------------|----------------|
| 不明・変動 | 即座 | 高 | **Intelligent-Tiering** | $0.023-0.0025 |
| 頻繁 | 1桁ms | 高 | **Express One Zone** | $0.16 |
| 頻繁 | 即座 | 高 | **Standard** | $0.023 |
| 月1回程度 | 即座 | 高 | **Standard-IA** | $0.0125 |
| 月1回程度 | 即座 | 低 | **One Zone-IA** | $0.01 |
| 四半期1回 | 即座 | 高 | **Glacier Instant Retrieval** | $0.004 |
| 年1回 | 3-5時間 | 高 | **Glacier Flexible Retrieval** | $0.0036 |
| 7年保管 | 12時間 | 高 | **Glacier Deep Archive** | $0.00099 |

### レプリケーション戦略の選択

```python
"""
レプリケーション戦略の選択ロジック
"""

def choose_replication_strategy(requirements):
    """
    要件に基づいてレプリケーション戦略を選択
    """
    strategies = []

    # ディザスタリカバリ
    if requirements.disaster_recovery:
        strategies.append({
            'type': 'Cross-Region Replication',
            'destination_region': 'ap-southeast-1',  # 異なるリージョン
            'priority': 'high',
            'replication_time_control': True  # 15分以内
        })

    # コンプライアンス（複数リージョン保管）
    if requirements.compliance:
        strategies.append({
            'type': 'Cross-Region Replication',
            'destination_region': 'eu-west-1',
            'storage_class': 'GLACIER',
            'delete_marker_replication': False  # 削除は複製しない
        })

    # 低レイテンシアクセス（グローバル）
    if requirements.global_low_latency:
        strategies.append({
            'type': 'Multi-Region Access Points',
            'regions': ['us-east-1', 'eu-west-1', 'ap-northeast-1'],
            'failover': 'automatic'
        })

    # バックアップ（同一リージョン）
    if requirements.backup:
        strategies.append({
            'type': 'Same-Region Replication',
            'destination_bucket': 'backup-bucket',
            'storage_class': 'INTELLIGENT_TIERING'
        })

    return strategies

# 使用例
class Requirements:
    disaster_recovery = True
    compliance = False
    global_low_latency = False
    backup = True

requirements = Requirements()
strategies = choose_replication_strategy(requirements)
print(f"推奨レプリケーション戦略: {strategies}")
```

## 検証ポイント

### 1. ストレージコストの分析

```bash
# S3 Storage Lensでバケットごとのコストを確認
aws s3control get-storage-lens-configuration \
    --account-id 123456789012 \
    --config-id default-dashboard

# コスト最適化の機会を特定
# - 利用率の低いStandardストレージ → Intelligent-Tiering
# - 古い非現行バージョン → Glacier/削除
# - 不完全なマルチパートアップロード → 削除
```

### 2. パフォーマンステスト

```python
"""
S3パフォーマンスベンチマーク
"""
import boto3
import time
import concurrent.futures

def benchmark_s3_operations(bucket, num_objects=100):
    """
    S3の読み書きパフォーマンスを計測
    """
    s3 = boto3.client('s3')

    # 書き込みベンチマーク
    start = time.time()
    for i in range(num_objects):
        s3.put_object(
            Bucket=bucket,
            Key=f'benchmark/object-{i}.txt',
            Body=b'x' * 1024 * 100  # 100 KB
        )
    write_time = time.time() - start
    write_throughput = (num_objects * 100 / 1024) / write_time

    print(f"書き込み: {num_objects}オブジェクト in {write_time:.2f}秒")
    print(f"スループット: {write_throughput:.2f} MB/s")

    # 読み込みベンチマーク
    start = time.time()
    for i in range(num_objects):
        s3.get_object(Bucket=bucket, Key=f'benchmark/object-{i}.txt')
    read_time = time.time() - start
    read_throughput = (num_objects * 100 / 1024) / read_time

    print(f"読み込み: {num_objects}オブジェクト in {read_time:.2f}秒")
    print(f"スループット: {read_throughput:.2f} MB/s")

    # 並列アップロードベンチマーク
    def upload_object(i):
        s3.put_object(
            Bucket=bucket,
            Key=f'benchmark-parallel/object-{i}.txt',
            Body=b'x' * 1024 * 100
        )

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(upload_object, range(num_objects))
    parallel_time = time.time() - start
    parallel_throughput = (num_objects * 100 / 1024) / parallel_time

    print(f"並列書き込み: {num_objects}オブジェクト in {parallel_time:.2f}秒")
    print(f"スループット: {parallel_throughput:.2f} MB/s")
    print(f"高速化: {write_time / parallel_time:.2f}倍")

# 使用例
benchmark_s3_operations('my-benchmark-bucket', num_objects=1000)
```

### 3. セキュリティ監査

```bash
# S3バケットのセキュリティ設定を確認
aws s3api get-bucket-encryption --bucket my-bucket
aws s3api get-bucket-versioning --bucket my-bucket
aws s3api get-public-access-block --bucket my-bucket
aws s3api get-bucket-policy --bucket my-bucket

# アクセスログの有効化確認
aws s3api get-bucket-logging --bucket my-bucket

# 期待値:
# - 暗号化: 有効（AES256またはKMS）
# - バージョニング: 有効
# - パブリックアクセスブロック: すべて有効
# - バケットポリシー: 最小権限
# - アクセスログ: 有効
```

### 4. レプリケーション状態の確認

```bash
# レプリケーションメトリクスを確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name ReplicationLatency \
    --dimensions Name=SourceBucket,Value=source-bucket Name=DestinationBucket,Value=destination-bucket Name=RuleId,Value=ReplicateAll \
    --start-time 2025-01-21T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 3600 \
    --statistics Average,Maximum

# 期待値（RTC有効時）:
# - 95%以上のオブジェクトが15分以内に複製
```

## 他のスキルとの統合

### CloudFrontスキルとの統合

```bash
# S3 + CloudFrontでグローバルコンテンツ配信
# CloudFrontディストリビューション作成（詳細はCloudFrontスキル参照）

# S3バケットポリシーでCloudFrontのみ許可（既出）
```

### Lambdaスキルとの統合

```python
"""
S3イベント→Lambda→画像リサイズ→S3保存
"""
import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    S3に画像がアップロードされたらサムネイルを生成
    """
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # 元画像を取得
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()

        # サムネイル生成
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((200, 200))

        # サムネイルを保存
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)

        thumbnail_key = f"thumbnails/{key}"
        s3.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=buffer,
            ContentType='image/jpeg',
            StorageClass='INTELLIGENT_TIERING'
        )

    return {'statusCode': 200}
```

### Athenaスキルとの統合

```bash
# S3データレイク→Athenaでクエリ
# Athenaテーブル定義（Parquet形式）
cat > create-table.sql << 'EOF'
CREATE EXTERNAL TABLE logs (
  timestamp STRING,
  user_id STRING,
  action STRING,
  details STRING
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET
LOCATION 's3://company-datalake/logs/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');
EOF

# パーティション追加
aws athena start-query-execution \
    --query-string "MSCK REPAIR TABLE logs" \
    --result-configuration "OutputLocation=s3://athena-results/"
```

## リソース

### 公式ドキュメント

- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/)
- [S3 Intelligent-Tiering](https://aws.amazon.com/s3/storage-classes/intelligent-tiering/)
- [S3 Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)

### ベストプラクティス

- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Cost Optimization Best Practices](https://aws.amazon.com/s3/cost-optimization/)

### ツールとライブラリ

- [AWS CLI S3 Commands](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [Boto3 S3 Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [S3 Transfer Manager](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/upload_file.html)

### コスト計算

- [AWS S3 Pricing Calculator](https://calculator.aws/#/addService/S3)
- [S3 Cost Optimization Guide](https://aws.amazon.com/s3/cost-optimization/)
