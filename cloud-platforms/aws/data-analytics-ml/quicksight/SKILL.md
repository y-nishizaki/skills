---
name: aws-quicksight
description: AWS QuickSightを使用してBIダッシュボードを作成し、SPICE、インクリメンタルリフレッシュ、組み込み分析で高速なデータ可視化を実現する方法
---

# AWS QuickSight スキル

## 概要

Amazon QuickSightは、クラウドネイティブなサーバーレスBIサービスで、SPICE（Super-fast, Parallel, In-memory Calculation Engine）によるインメモリ計算で高速なダッシュボードを提供します。

## 主な使用ケース

### 1. SPICE データセット作成

```bash
# データセット作成（S3ソース）
aws quicksight create-data-set \
    --aws-account-id 123456789012 \
    --data-set-id sales-spice-dataset \
    --name "Sales Data (SPICE)" \
    --physical-table-map '{
        "s3-sales": {
            "S3Source": {
                "DataSourceArn": "arn:aws:quicksight:ap-northeast-1:123456789012:datasource/s3-datasource",
                "InputColumns": [
                    {"Name": "order_id", "Type": "STRING"},
                    {"Name": "amount", "Type": "DECIMAL"},
                    {"Name": "order_date", "Type": "DATETIME"}
                ]
            }
        }
    }' \
    --import-mode SPICE

# データセット更新（リフレッシュ）
aws quicksight create-ingestion \
    --aws-account-id 123456789012 \
    --data-set-id sales-spice-dataset \
    --ingestion-id $(date +%s)

# インクリメンタルリフレッシュ設定
aws quicksight update-data-set \
    --aws-account-id 123456789012 \
    --data-set-id sales-spice-dataset \
    --import-mode SPICE \
    --incremental-refresh '{
        "LookbackWindow": {
            "ColumnName": "order_date",
            "Size": 1,
            "SizeUnit": "DAY"
        }
    }'
```

### 2. ダッシュボード作成（CLI）

```bash
# 分析作成
aws quicksight create-analysis \
    --aws-account-id 123456789012 \
    --analysis-id sales-analysis \
    --name "Sales Analysis" \
    --source-entity '{
        "SourceTemplate": {
            "DataSetReferences": [{
                "DataSetPlaceholder": "SalesData",
                "DataSetArn": "arn:aws:quicksight:ap-northeast-1:123456789012:dataset/sales-spice-dataset"
            }],
            "Arn": "arn:aws:quicksight:ap-northeast-1:123456789012:template/sales-template"
        }
    }'

# ダッシュボード公開
aws quicksight create-dashboard \
    --aws-account-id 123456789012 \
    --dashboard-id sales-dashboard \
    --name "Sales Dashboard" \
    --source-entity '{
        "SourceTemplate": {
            "DataSetReferences": [{
                "DataSetPlaceholder": "SalesData",
                "DataSetArn": "arn:aws:quicksight:ap-northeast-1:123456789012:dataset/sales-spice-dataset"
            }],
            "Arn": "arn:aws:quicksight:ap-northeast-1:123456789012:template/sales-template"
        }
    }' \
    --permissions '[{
        "Principal": "arn:aws:quicksight:ap-northeast-1:123456789012:group/default/sales-team",
        "Actions": ["quicksight:DescribeDashboard", "quicksight:ListDashboardVersions", "quicksight:QueryDashboard"]
    }]'
```

### 3. 計算フィールド

```text
# ダッシュボード内で使用する計算フィールド例

# 月次売上（集計関数）
monthlyRevenue = sumOver(amount, [truncDate('MM', order_date)], PRE_AGG)

# 前年比
yoy_growth = (sum(amount) - sumOver(sum(amount), [addDateTime(1, 'YYYY', truncDate('YYYY', order_date))], PRE_AGG))
             / sumOver(sum(amount), [addDateTime(1, 'YYYY', truncDate('YYYY', order_date))], PRE_AGG) * 100

# 条件付き書式
status_color = ifelse(amount > 10000, 'High', ifelse(amount > 5000, 'Medium', 'Low'))

# パーセンタイル
percentile_rank = percentileOver(amount, [customer_id], PRE_AGG, 0.95)
```

### 4. データソース接続（Athena / Redshift）

```bash
# Athenaデータソース作成
aws quicksight create-data-source \
    --aws-account-id 123456789012 \
    --data-source-id athena-datasource \
    --name "Athena Data Lake" \
    --type ATHENA \
    --data-source-parameters '{
        "AthenaParameters": {
            "WorkGroup": "primary"
        }
    }' \
    --permissions '[{
        "Principal": "arn:aws:quicksight:ap-northeast-1:123456789012:user/default/admin",
        "Actions": ["quicksight:DescribeDataSource", "quicksight:PassDataSource"]
    }]'

# Redshift Serverlessデータソース
aws quicksight create-data-source \
    --aws-account-id 123456789012 \
    --data-source-id redshift-datasource \
    --name "Redshift DW" \
    --type REDSHIFT \
    --data-source-parameters '{
        "RedshiftParameters": {
            "Host": "my-workgroup.123456789012.ap-northeast-1.redshift-serverless.amazonaws.com",
            "Port": 5439,
            "Database": "analytics"
        }
    }' \
    --credentials '{
        "CredentialPair": {
            "Username": "admin",
            "Password": "SecurePassword123!"
        }
    }'
```

### 5. 組み込み分析（Embedded Analytics）

```python
# Python SDK - ダッシュボード埋め込みURL生成
import boto3

quicksight = boto3.client('quicksight', region_name='ap-northeast-1')

response = quicksight.generate_embed_url_for_registered_user(
    AwsAccountId='123456789012',
    ExperienceConfiguration={
        'Dashboard': {
            'InitialDashboardId': 'sales-dashboard'
        }
    },
    UserArn='arn:aws:quicksight:ap-northeast-1:123456789012:user/default/embedded-user',
    SessionLifetimeInMinutes=600,
    AllowedDomains=['https://myapp.example.com']
)

embed_url = response['EmbedUrl']
print(embed_url)
```

## ベストプラクティス（2025年版）

### 1. SPICE vs Direct Query選択

```text
SPICE推奨ケース:
- 日次/週次更新のデータ
- 100GB以下のデータセット
- 高速なダッシュボード応答が必要
- 複数ユーザーからの同時アクセス

Direct Query推奨ケース:
- リアルタイム性が必須
- データ量が極端に大きい（数TB）
- データ更新頻度が高い（15分未満）

ハイブリッドアプローチ（2025年推奨）:
- 集計データ → SPICE（日次更新）
- 詳細データ → Direct Query（常に最新）
```

### 2. 計算フィールドの最適化

```text
悪い例: ビジュアル内での複雑な計算
良い例: データセット準備時に事前計算

# データセット内で計算フィールドを定義
aws quicksight update-data-set \
    --data-set-id sales-dataset \
    --logical-table-map '{
        "calculated-fields": {
            "Source": "s3-sales",
            "DataTransforms": [{
                "CreateColumnsOperation": {
                    "Columns": [{
                        "ColumnName": "revenue",
                        "ColumnId": "revenue",
                        "Expression": "quantity * unit_price"
                    }]
                }
            }]
        }
    }'
```

### 3. リフレッシュスケジュール最適化

```bash
# 増分リフレッシュ（15分ごと、最小）
aws quicksight create-refresh-schedule \
    --aws-account-id 123456789012 \
    --data-set-id sales-dataset \
    --schedule '{
        "ScheduleId": "incremental-refresh",
        "ScheduleFrequency": {
            "Interval": "MINUTE15",
            "RefreshOnDay": {
                "DayOfWeek": "MONDAY"
            }
        },
        "RefreshType": "INCREMENTAL_REFRESH"
    }'

# フルリフレッシュ（週次、深夜）
aws quicksight create-refresh-schedule \
    --aws-account-id 123456789012 \
    --data-set-id sales-dataset \
    --schedule '{
        "ScheduleId": "weekly-full-refresh",
        "ScheduleFrequency": {
            "Interval": "WEEKLY",
            "TimeOfTheDay": "02:00"
        },
        "RefreshType": "FULL_REFRESH"
    }'
```

### 4. Row-Level Security（RLS）

```bash
# データセットルール作成
aws quicksight create-data-set \
    --data-set-id sales-rls \
    --row-level-permission-data-set '{
        "Namespace": "default",
        "Arn": "arn:aws:quicksight:ap-northeast-1:123456789012:dataset/rls-rules",
        "PermissionPolicy": "GRANT_ACCESS"
    }'

# RLSルールテーブル（例）
# user_name | region
# john@example.com | US
# jane@example.com | EU
```

### 5. SPICE容量管理

```bash
# SPICE使用量確認
aws quicksight describe-account-subscription \
    --aws-account-id 123456789012

# SPICE容量購入
aws quicksight update-account-customization \
    --aws-account-id 123456789012 \
    --namespace default \
    --account-customization '{
        "DefaultTheme": "arn:aws:quicksight::aws:theme/MIDNIGHT"
    }'
```

## よくある失敗パターン

### 1. 不要なデータセットの残置

```bash
# 未使用データセット削除
aws quicksight list-data-sets --aws-account-id 123456789012

aws quicksight delete-data-set \
    --aws-account-id 123456789012 \
    --data-set-id unused-dataset
```

### 2. Direct Queryでの大量データスキャン

```text
問題: Athena Direct Queryで毎回全テーブルスキャン
解決: パーティション付きデータセット + フィルタ設定

# データセットにデフォルトフィルタ追加
WHERE year = 2025 AND month = MONTH(now())
```

### 3. 計算フィールドの重複定義

```text
問題: 同じ計算を複数のビジュアルで定義
解決: データセットレベルで1回だけ定義

データセット → 計算フィールド → 全ビジュアルで再利用
```

## リソース

- [QuickSight Documentation](https://docs.aws.amazon.com/quicksight/)
- [SPICE Best Practices](https://aws.amazon.com/blogs/business-intelligence/best-practices-for-amazon-quicksight-spice-and-direct-query-mode/)
- [Embedded Analytics](https://docs.aws.amazon.com/quicksight/latest/user/embedded-analytics.html)
