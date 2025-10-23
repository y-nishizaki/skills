---
name: s3-fundamentals
description: S3の基本概念、バケット管理、基本的なストレージクラス、Intelligent-Tiering、静的サイトホスティング、基本的なセキュリティとライフサイクル管理を学ぶ
---

# AWS S3 Fundamentals スキル

## 概要

Amazon S3（Simple Storage Service）は、業界をリードするスケーラビリティ、データ可用性、セキュリティ、パフォーマンスを提供するオブジェクトストレージサービスです。このスキルでは、S3の基本概念、バケット管理、基本的なストレージクラス、Intelligent-Tiering、静的サイトホスティング、基本的なセキュリティとライフサイクル管理を学びます。

### 2025年の重要なアップデート

- **S3 Intelligent-Tiering**: すべての新規ワークロードのデフォルト推奨
- **ライフサイクルポリシーの自動化**: 組織規模での自動適用
- **セキュリティのベストプラクティス**: パブリックアクセスブロックがデフォルト

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

### 2. S3 Intelligent-Tiering（2025年推奨）

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

### 3. 基本的なライフサイクルポリシー

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

### 4. S3バージョニング

データ保護と誤削除の防止を実現します。

```bash
# バージョニング有効化
aws s3api put-bucket-versioning \
    --bucket my-bucket \
    --versioning-configuration Status=Enabled

# バージョン一覧の確認
aws s3api list-object-versions \
    --bucket my-bucket \
    --prefix "important-file.txt"

# 特定バージョンの取得
aws s3api get-object \
    --bucket my-bucket \
    --key important-file.txt \
    --version-id VERSION_ID \
    output-file.txt

# 削除マーカーの削除（復元）
aws s3api delete-object \
    --bucket my-bucket \
    --key important-file.txt \
    --version-id DELETE_MARKER_VERSION_ID
```

### 5. バケット作成と基本設定

セキュアなバケットを作成します。

```bash
# バケットの作成
aws s3api create-bucket \
    --bucket my-secure-bucket \
    --region ap-northeast-1 \
    --create-bucket-configuration LocationConstraint=ap-northeast-1

# デフォルト暗号化の有効化（SSE-S3）
aws s3api put-bucket-encryption \
    --bucket my-secure-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'

# パブリックアクセスブロックの有効化（2025年必須）
aws s3api put-public-access-block \
    --bucket my-secure-bucket \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# バージョニングの有効化
aws s3api put-bucket-versioning \
    --bucket my-secure-bucket \
    --versioning-configuration Status=Enabled
```

## 思考プロセス

S3を使用したストレージ戦略を設計する際の段階的な思考プロセスです。

### フェーズ1: ストレージクラスの選択

```python
"""
S3ストレージクラス選択ロジック（2025年版・基本編）
"""

def choose_storage_class(access_pattern):
    """
    アクセスパターンに基づいて最適なストレージクラスを選択
    """
    if access_pattern.access_frequency == 'unknown':
        # 2025年のデフォルト推奨
        return 'INTELLIGENT_TIERING'

    if access_pattern.access_frequency == 'frequent':
        return 'STANDARD'

    if access_pattern.access_frequency == 'infrequent':
        if access_pattern.availability_requirement == 'high':
            return 'STANDARD_IA'  # Multi-AZ
        else:
            return 'ONEZONE_IA'  # Single-AZ（20%安い）

    # デフォルトはIntelligent-Tiering
    return 'INTELLIGENT_TIERING'

# 使用例
class AccessPattern:
    def __init__(self):
        self.access_frequency = 'unknown'
        self.availability_requirement = 'high'

pattern = AccessPattern()
pattern.access_frequency = 'unknown'
storage_class = choose_storage_class(pattern)
print(f"推奨ストレージクラス: {storage_class}")
# 出力: INTELLIGENT_TIERING
```

### フェーズ2: ライフサイクルポリシーの設計

```python
"""
基本的なライフサイクルポリシー生成ツール
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

### フェーズ3: 基本的なセキュリティとアクセス制御

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
```

## ベストプラクティス（2025年版）

### 1. Intelligent-Tieringをデフォルトに

**推奨**: すべての新規ワークロードでIntelligent-Tieringを使用

```bash
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
          "StorageClass": "STANDARD_IA"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90,
        "NewerNoncurrentVersions": 5
      }
    }
  ]
}
EOF
```

**ポイント**: 最新5バージョンを保持、30日後に低頻度アクセスに移行、90日後に削除

### 3. 基本的な暗号化の有効化

```bash
# バケットレベルのデフォルト暗号化（SSE-S3）
aws s3api put-bucket-encryption \
    --bucket my-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'
```

**Bucket Key有効化のメリット**:
- S3とKMS間の通信を削減
- より効率的な暗号化処理

### 4. パブリックアクセスブロックの有効化

```bash
# すべてのパブリックアクセスをブロック
aws s3api put-public-access-block \
    --bucket my-bucket \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

**重要**: 静的サイトホスティング以外のすべてのバケットで有効化すべき

### 5. 基本的なIAMポリシー

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/user-data/*"
    }
  ]
}
```

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

# ライフサイクルポリシーで古いバージョンを削除（前述）
```

### 2. 不完全なマルチパートアップロードの蓄積

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

# ライフサイクルポリシーで自動削除（推奨、前述）
```

### 3. 暗号化されていないアップロード

**症状**: セキュリティ監査で警告

**原因**: バケットポリシーで暗号化を強制していない

**対策**:

```bash
# バケットポリシーで非暗号化アップロードを拒否
# （前述のsecure-bucket-policy.jsonを参照）
```

## 判断ポイント

### 基本的なストレージクラス選択マトリクス

| アクセス頻度 | 取り出し時間 | 可用性要件 | 推奨ストレージクラス | コスト（GB/月） |
|------------|------------|----------|------------------|----------------|
| 不明・変動 | 即座 | 高 | **Intelligent-Tiering** | $0.023-0.0025 |
| 頻繁 | 即座 | 高 | **Standard** | $0.023 |
| 月1回程度 | 即座 | 高 | **Standard-IA** | $0.0125 |
| 月1回程度 | 即座 | 低 | **One Zone-IA** | $0.01 |

### バージョニングの有効化判断

```python
"""
バージョニング有効化の判断ロジック
"""

def should_enable_versioning(bucket_type):
    """
    バケットの用途に応じてバージョニングの必要性を判断
    """
    enable_versioning = {
        # 必須
        'production_data': True,
        'compliance_data': True,
        'backup': True,

        # 推奨
        'user_uploads': True,
        'application_config': True,

        # 不要
        'temp_files': False,
        'cache': False,
        'logs_archive': False
    }

    return enable_versioning.get(bucket_type, True)  # デフォルトは有効化

# 使用例
print(should_enable_versioning('production_data'))  # True
print(should_enable_versioning('temp_files'))  # False
```

## 検証ポイント

### 1. ストレージコストの分析

```bash
# バケットごとのストレージサイズを確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=my-bucket Name=StorageType,Value=StandardStorage \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 86400 \
    --statistics Average

# オブジェクト数を確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name NumberOfObjects \
    --dimensions Name=BucketName,Value=my-bucket Name=StorageType,Value=AllStorageTypes \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 86400 \
    --statistics Average
```

### 2. セキュリティ監査

```bash
# S3バケットのセキュリティ設定を確認
aws s3api get-bucket-encryption --bucket my-bucket
aws s3api get-bucket-versioning --bucket my-bucket
aws s3api get-public-access-block --bucket my-bucket
aws s3api get-bucket-policy --bucket my-bucket

# 期待値:
# - 暗号化: 有効（AES256）
# - バージョニング: 有効（重要なデータの場合）
# - パブリックアクセスブロック: すべて有効
# - バケットポリシー: 最小権限
```

### 3. ライフサイクルポリシーの検証

```bash
# ライフサイクルポリシーを確認
aws s3api get-bucket-lifecycle-configuration --bucket my-bucket

# 期待値:
# - Intelligent-Tieringへの移行ルール
# - 古いバージョンの削除ルール
# - 不完全マルチパートアップロードの削除ルール
```

## 関連スキル

### s3-advanced

より高度なS3機能を学ぶには、**s3-advanced**スキルを参照してください：

- 高度なストレージクラス（Glacier、Deep Archive、Express One Zone）
- データレイク構築
- 高度なセキュリティ（KMS暗号化、Access Points）
- レプリケーション（CRR、SRR）
- イベント通知とLambda統合
- パフォーマンス最適化
- S3 Transfer Acceleration
- Object Lock（WORM）

```bash
# s3-advancedスキルは以下のような高度な機能をカバー
# - クロスリージョンレプリケーション
# - S3 Access Pointsでのマルチテナント管理
# - S3 Object Lockでのコンプライアンス対応
# - S3イベント通知とLambda統合
```

## リソース

### 公式ドキュメント

- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/)
- [S3 Intelligent-Tiering](https://aws.amazon.com/s3/storage-classes/intelligent-tiering/)
- [S3 Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)

### ベストプラクティス

- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

### ツールとライブラリ

- [AWS CLI S3 Commands](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [Boto3 S3 Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

### コスト計算

- [AWS S3 Pricing Calculator](https://calculator.aws/#/addService/S3)
