---
name: s3-advanced
description: S3の高度な機能を習得：データレイク、高度なストレージクラス（Glacier、Deep Archive）、レプリケーション、イベント通知、Access Points、パフォーマンス最適化、Object Lock
---

# AWS S3 Advanced スキル

## 概要

このスキルでは、Amazon S3の高度な機能を深く学びます。データレイク構築、Glacierなどの高度なストレージクラス、クロスリージョンレプリケーション、イベント通知、S3 Access Points、パフォーマンス最適化、Object Lockなどのエンタープライズ向け機能をカバーします。

### 2025年の重要なアップデート

- **S3 Express One Zone**: 1桁ミリ秒のレイテンシ（高頻度アクセス用）
- **Multi-Region Access Points**: 自動フェイルオーバーでグローバル展開を簡素化
- **S3 Object Lambda**: データ取得時にリアルタイムで変換

## 主な使用ケース

### 1. データレイク構築

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

### 2. クロスリージョンレプリケーション（CRR）

ディザスタリカバリとグローバル展開を実現します。

```bash
# バージョニング有効化（ソースとデスティネーション両方で必須）
aws s3api put-bucket-versioning \
    --bucket source-bucket \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
    --bucket destination-bucket \
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

# レプリケーション用IAMポリシーの作成
cat > replication-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetReplicationConfiguration",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::source-bucket"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObjectVersionForReplication",
        "s3:GetObjectVersionAcl",
        "s3:GetObjectVersionTagging"
      ],
      "Resource": "arn:aws:s3:::source-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete",
        "s3:ReplicateTags"
      ],
      "Resource": "arn:aws:s3:::destination-bucket/*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name S3ReplicationRole \
    --policy-name ReplicationPolicy \
    --policy-document file://replication-policy.json
```

### 3. S3イベント通知

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

# Lambda関数にS3からの呼び出し権限を付与
aws lambda add-permission \
    --function-name image-processor \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket
```

### 4. S3 Access Points（マルチテナント管理）

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
        "StringLike": {
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

# Access Point経由でのアクセス
aws s3 ls s3://arn:aws:s3:ap-northeast-1:123456789012:accesspoint/analytics-team-ap/

# Access Point名でのアクセス（簡易形式）
aws s3 cp data.csv s3://arn:aws:s3:ap-northeast-1:123456789012:accesspoint/analytics-team-ap/analytics/data.csv
```

### 5. S3 Object Lock（WORM: Write Once Read Many）

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

# Legal Holdの設定（保持期限なし）
aws s3api put-object-legal-hold \
    --bucket compliance-bucket \
    --key legal-evidence.pdf \
    --legal-hold Status=ON
```

**モードの違い**:
- **GOVERNANCE**: 特権ユーザーが上書き可能
- **COMPLIANCE**: 誰も削除・上書き不可（ルートユーザーでも）

### 6. 高度なストレージクラス（Glacier）

長期アーカイブとコスト最適化を実現します。

```bash
# Glacier Instant Retrievalへの移行（即座の取り出し）
aws s3api put-object \
    --bucket my-archive-bucket \
    --key archive-data.zip \
    --body data.zip \
    --storage-class GLACIER_IR

# Glacier Flexible Retrievalへの移行（1-5分または3-5時間）
aws s3 cp data.tar.gz s3://my-archive-bucket/ \
    --storage-class GLACIER

# Glacier Deep Archiveへの移行（12時間、最安）
aws s3 cp old-data.tar.gz s3://my-archive-bucket/ \
    --storage-class DEEP_ARCHIVE

# Glacierからのデータ復元
aws s3api restore-object \
    --bucket my-archive-bucket \
    --key archived-file.zip \
    --restore-request '{
        "Days": 7,
        "GlacierJobParameters": {
            "Tier": "Standard"
        }
    }'

# 復元状態の確認
aws s3api head-object \
    --bucket my-archive-bucket \
    --key archived-file.zip
```

**取り出し層の比較**:
- **Expedited**: 1-5分（$30/1000リクエスト + $0.03/GB）
- **Standard**: 3-5時間（$0.05/1000リクエスト + $0.01/GB）
- **Bulk**: 5-12時間（$0.025/1000リクエスト + $0.0025/GB）

## 思考プロセス

### フェーズ1: 高度なセキュリティとアクセス制御

```bash
# KMS暗号化の有効化
aws s3api put-bucket-encryption \
    --bucket my-secure-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
            },
            "BucketKeyEnabled": true
        }]
    }'

# KMSキーポリシーでアクセス制御
cat > kms-key-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow S3 to use the key",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# アクセスログの有効化
aws s3api put-bucket-logging \
    --bucket my-bucket \
    --bucket-logging-status '{
        "LoggingEnabled": {
            "TargetBucket": "my-log-bucket",
            "TargetPrefix": "s3-access-logs/"
        }
    }'
```

### フェーズ2: パフォーマンス最適化

```python
"""
大容量ファイルのマルチパートアップロード
"""
import boto3
import os
import threading
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

### フェーズ3: コスト最適化の監視

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

### 1. KMS暗号化のBucket Key有効化

```bash
# Bucket Key有効化でKMSコストを99%削減
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
```

**Bucket Key有効化のメリット**:
- KMS APIコールを99%削減
- KMSコストを大幅削減
- パフォーマンス向上

### 2. CloudFrontとの統合

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

aws s3api put-bucket-policy \
    --bucket my-bucket \
    --policy file://cloudfront-bucket-policy.json
```

### 3. S3 Transfer Accelerationで高速アップロード

```bash
# Transfer Accelerationの有効化
aws s3api put-bucket-accelerate-configuration \
    --bucket my-global-bucket \
    --accelerate-configuration Status=Enabled

# Transfer Accelerationエンドポイントを使用
aws s3 cp large-file.zip s3://my-global-bucket/ \
    --endpoint-url https://s3-accelerate.amazonaws.com \
    --region us-west-2

# 速度比較テスト
aws s3api get-bucket-accelerate-configuration \
    --bucket my-global-bucket
```

**適用ケース**:
- 世界中からのアップロード（50%以上高速化）
- 大容量ファイル（GB単位）
- 追加コスト: $0.04/GB（通常転送より）

### 4. S3 Select/Glacier Selectでデータ転送量削減

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

# S3 Select（JSON例）
aws s3api select-object-content \
    --bucket my-bucket \
    --key data/events.json \
    --expression "SELECT s.event_type, s.timestamp FROM S3Object[*] s WHERE s.status = 'error'" \
    --expression-type SQL \
    --input-serialization '{"JSON": {"Type": "DOCUMENT"}}' \
    --output-serialization '{"JSON": {}}' \
    errors.json

# Parquet形式での使用
aws s3api select-object-content \
    --bucket my-bucket \
    --key data/sales.parquet \
    --expression "SELECT product, SUM(amount) as total FROM S3Object GROUP BY product" \
    --expression-type SQL \
    --input-serialization '{"Parquet": {}}' \
    --output-serialization '{"CSV": {}}' \
    summary.csv
```

**メリット**:
- データ転送量を最大80%削減
- 処理時間を最大400%高速化
- コスト: $0.002/GB（スキャン）+ $0.0007/GB（返却）

### 5. S3 Batch Operationsで大規模処理

```bash
# Batch Operationsでタグを一括設定
cat > batch-job-manifest.csv << 'EOF'
my-bucket,object1.txt
my-bucket,object2.txt
my-bucket,object3.txt
EOF

# マニフェストをS3にアップロード
aws s3 cp batch-job-manifest.csv s3://my-batch-bucket/manifests/

# Batch Job作成
aws s3control create-job \
    --account-id 123456789012 \
    --operation '{
        "S3PutObjectTagging": {
            "TagSet": [
                {"Key": "Department", "Value": "Engineering"},
                {"Key": "Environment", "Value": "Production"}
            ]
        }
    }' \
    --manifest '{
        "Spec": {
            "Format": "S3BatchOperations_CSV_20180820",
            "Fields": ["Bucket", "Key"]
        },
        "Location": {
            "ObjectArn": "arn:aws:s3:::my-batch-bucket/manifests/batch-job-manifest.csv",
            "ETag": "etag-value"
        }
    }' \
    --report '{
        "Bucket": "arn:aws:s3:::my-batch-bucket",
        "Format": "Report_CSV_20180820",
        "Enabled": true,
        "Prefix": "batch-reports/",
        "ReportScope": "AllTasks"
    }' \
    --priority 10 \
    --role-arn arn:aws:iam::123456789012:role/S3BatchOperationsRole \
    --no-confirmation-required
```

## よくある落とし穴と対策

### 1. リクエストコストの見落とし

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

### 2. クロスリージョン転送コストの見落とし

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
- クロスリージョン転送: $0.02/GB（毎回）
- レプリケーション: $0.02/GB（1回のみ）+ 各リージョンでのストレージコスト

### 3. Glacier取り出しコストの予期しない高騰

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

# 取り出しジョブの状態確認
aws s3api head-object \
    --bucket my-archive-bucket \
    --key archived-file.zip
```

**コスト比較（1TB取り出し）**:
- Expedited: $30 + $0.03/GB = $60.72
- Standard: $10 + $0.01/GB = $20.48
- Bulk: $2.50 + $0.0025/GB = $5.06

### 4. レプリケーションの帯域幅制限

**症状**: レプリケーションが遅延

**原因**: デフォルトの帯域幅制限

**対策**:

```bash
# Replication Time Control（RTC）を有効化
# replication-config.jsonに追加（前述の例を参照）
# "ReplicationTime": { "Status": "Enabled", "Time": { "Minutes": 15 } }

# レプリケーション優先度を設定
# 複数ルールがある場合、高優先度を優先
```

## 判断ポイント

### 高度なストレージクラス選択マトリクス

| アクセス頻度 | 取り出し時間 | 可用性要件 | 推奨ストレージクラス | コスト（GB/月） |
|------------|------------|----------|------------------|----------------|
| 頻繁 | 1桁ms | 高 | **Express One Zone** | $0.16 |
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

### 1. パフォーマンステスト

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

### 2. レプリケーション状態の確認

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

# レプリケーション設定の確認
aws s3api get-bucket-replication --bucket source-bucket

# レプリケーション失敗の確認
aws s3api list-objects-v2 \
    --bucket source-bucket \
    --prefix "" \
    --query 'Contents[?ReplicationStatus==`FAILED`]'
```

### 3. Access Pointの監視

```bash
# Access Pointのメトリクスを確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name AllRequests \
    --dimensions Name=AccessPointName,Value=analytics-team-ap \
    --start-time 2025-01-21T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 3600 \
    --statistics Sum

# Access Pointの設定確認
aws s3control get-access-point \
    --account-id 123456789012 \
    --name analytics-team-ap

# Access Pointポリシーの確認
aws s3control get-access-point-policy \
    --account-id 123456789012 \
    --name analytics-team-ap
```

## 他のスキルとの統合

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
    --result-configuration "OutputLocation=s3://athena-results/" \
    --query-execution-context "Database=analytics"

# クエリ実行
aws athena start-query-execution \
    --query-string "SELECT user_id, COUNT(*) as actions FROM logs WHERE year=2025 AND month=1 GROUP BY user_id LIMIT 10" \
    --result-configuration "OutputLocation=s3://athena-results/" \
    --query-execution-context "Database=analytics"
```

### Glueスキルとの統合

```bash
# S3データ→Glueクローラー→Glue Data Catalog
aws glue create-crawler \
    --name s3-data-crawler \
    --role arn:aws:iam::123456789012:role/GlueCrawlerRole \
    --database-name analytics \
    --targets '{
        "S3Targets": [
            {
                "Path": "s3://company-datalake/raw/"
            }
        ]
    }' \
    --schedule "cron(0 2 * * ? *)"

# クローラー実行
aws glue start-crawler --name s3-data-crawler
```

## 関連スキル

### s3-fundamentals

S3の基本を学ぶには、**s3-fundamentals**スキルを参照してください：

- S3の基本概念とバケット管理
- 基本的なストレージクラス（Standard、IA、One Zone-IA）
- S3 Intelligent-Tiering
- 静的サイトホスティング
- 基本的なセキュリティ（バケットポリシー、IAM）
- 基本的なライフサイクルポリシー
- バージョニングの基礎

```bash
# s3-fundamentalsスキルは以下の基本機能をカバー
# - バケットの作成と基本設定
# - 基本的な暗号化（SSE-S3）
# - パブリックアクセスブロック
# - 基本的なバージョニング
```

## リソース

### 公式ドキュメント

- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [S3 Storage Lens](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage_lens.html)
- [S3 Access Points](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-points.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [S3 Batch Operations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/batch-ops.html)

### ベストプラクティス

- [S3 Performance Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
- [Cost Optimization Best Practices](https://aws.amazon.com/s3/cost-optimization/)

### ツールとライブラリ

- [AWS CLI S3 Commands](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [Boto3 S3 Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [S3 Transfer Manager](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/upload_file.html)

### コスト計算

- [AWS S3 Pricing Calculator](https://calculator.aws/#/addService/S3)
- [S3 Cost Optimization Guide](https://aws.amazon.com/s3/cost-optimization/)
