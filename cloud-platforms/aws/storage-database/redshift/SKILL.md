---
name: aws-redshift
description: AWS Redshiftを使用してペタバイト級のデータウェアハウスを構築し、Serverless、RA3ノード、Spectrumを活用してコスト効率良く分析する方法
---

# AWS Redshift スキル

## 概要

Amazon Redshiftは、クラウド上で完全マネージドなペタバイト級のデータウェアハウスサービスです。このスキルでは、Redshift Serverless、RA3ノード、Redshift Spectrumを活用して、コスト効率の高いデータ分析基盤を構築する方法を学びます。

### 2025年の重要なアップデート

- **Redshift Serverless**: インフラ管理不要、使った分だけ課金（2025年推奨）
- **RA3ノード**: コンピュートとストレージを独立にスケール
- **マルチウェアハウスアーキテクチャ**: データ共有でワークロード分離
- **ゼロETL統合**: RDS、Aurora、DynamoDBから直接クエリ

## 主な使用ケース

### 1. Redshift Serverless（2025年推奨）

インフラ管理なしでデータウェアハウスを使用します。

```bash
# Serverlessワークグループの作成
aws redshift-serverless create-workgroup \
    --workgroup-name production-analytics \
    --namespace-name analytics-namespace \
    --base-capacity 128 \
    --subnet-ids subnet-12345678 subnet-87654321 \
    --security-group-ids sg-0123456789abcdef0 \
    --enhanced-vpc-routing \
    --publicly-accessible false

# Serverless名前空間の作成
aws redshift-serverless create-namespace \
    --namespace-name analytics-namespace \
    --db-name analyticsdb \
    --admin-username admin \
    --admin-user-password 'SecurePassword123!' \
    --iam-roles arn:aws:iam::123456789012:role/RedshiftServerlessRole \
    --log-exports '["userlog","connectionlog","useractivitylog"]'
```

**Serverlessの特徴**:
- 料金: $1.50/時～（RPU-hours単位）
- 自動スケーリング: ワークロードに応じて自動調整
- アイドル時の課金: なし（自動シャットダウン）
- 用途: 変動するワークロード、新規プロジェクト

### 2. Redshift Provisioned（RA3ノード）

コンピュートとストレージを独立にスケールします。

```bash
# RA3クラスターの作成
aws redshift create-cluster \
    --cluster-identifier production-warehouse \
    --node-type ra3.4xlarge \
    --number-of-nodes 2 \
    --master-username admin \
    --master-user-password 'SecurePassword123!' \
    --db-name warehousedb \
    --cluster-subnet-group-name redshift-subnet-group \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --iam-roles arn:aws:iam::123456789012:role/RedshiftRole \
    --encrypted \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678 \
    --enhanced-vpc-routing \
    --publicly-accessible false \
    --automated-snapshot-retention-period 7 \
    --preferred-maintenance-window sun:05:00-sun:06:00
```

**RA3の特徴**:
- Managed Storage: $0.024/GB/月（独立課金）
- ノード料金: ra3.4xlarge = $3.26/時
- ストレージ: 自動スケーリング（最大PB級）
- 用途: 予測可能な高負荷ワークロード

### 3. Redshift Spectrum

S3のデータレイクを直接クエリします。

```sql
-- 外部スキーマの作成（S3データカタログ）
CREATE EXTERNAL SCHEMA spectrum_schema
FROM DATA CATALOG
DATABASE 'glue_catalog_database'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftSpectrumRole'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- 外部テーブルの作成（Parquet形式）
CREATE EXTERNAL TABLE spectrum_schema.sales (
    order_id BIGINT,
    product_id INT,
    customer_id INT,
    quantity INT,
    price DECIMAL(10,2),
    order_date DATE
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET
LOCATION 's3://datalake-bucket/sales/';

-- パーティションの追加
ALTER TABLE spectrum_schema.sales
ADD PARTITION (year=2025, month=1)
LOCATION 's3://datalake-bucket/sales/year=2025/month=01/';

-- S3とRedshiftのデータを結合してクエリ
SELECT
    c.customer_name,
    s.order_date,
    SUM(s.quantity * s.price) AS total_amount
FROM spectrum_schema.sales s
JOIN customers c ON s.customer_id = c.customer_id
WHERE s.year = 2025 AND s.month = 1
GROUP BY c.customer_name, s.order_date
ORDER BY total_amount DESC
LIMIT 10;
```

**Spectrumの料金**:
- $5.00/TB スキャンされたデータ量
- Parquet/ORCで圧縮・パーティション化してコスト削減

### 4. データ共有（マルチウェアハウス）

複数のワークグループ間でデータを共有します。

```sql
-- プロデューサー側: データシェアの作成
CREATE DATASHARE sales_share;

-- テーブルをデータシェアに追加
ALTER DATASHARE sales_share ADD SCHEMA public;
ALTER DATASHARE sales_share ADD TABLE public.orders;
ALTER DATASHARE sales_share ADD TABLE public.customers;

-- コンシューマーにアクセス許可
GRANT USAGE ON DATASHARE sales_share TO ACCOUNT '987654321098';

-- コンシューマー側: データシェアから読み取り専用データベースを作成
CREATE DATABASE sales_from_producer FROM DATASHARE sales_share
OF ACCOUNT '123456789012' NAMESPACE 'production-namespace';

-- クエリ実行（読み取り専用）
SELECT * FROM sales_from_producer.public.orders
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days';
```

**データ共有のメリット**:
- ETLなしでリアルタイムアクセス
- ストレージコピー不要
- ワークロード分離（本番/分析/開発）

### 5. ゼロETL統合

RDS/Aurora/DynamoDBから直接クエリします。

```bash
# RDSからRedshiftへのゼロETL統合を作成
aws rds create-integration \
    --integration-name rds-to-redshift-integration \
    --source-arn arn:aws:rds:ap-northeast-1:123456789012:db:mysql-prod \
    --target-arn arn:aws:redshift-serverless:ap-northeast-1:123456789012:namespace/analytics-namespace \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678
```

```sql
-- RedshiftでゼロETLデータベースをクエリ
SELECT
    DATE_TRUNC('day', created_at) AS date,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM rds_integration.public.orders
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC
LIMIT 30;
```

**ゼロETLのメリット**:
- ETLパイプライン不要
- ニアリアルタイムレプリケーション（数秒～数分）
- トランザクションデータを分析

### 6. マテリアライズドビュー

クエリパフォーマンスを大幅に向上させます。

```sql
-- マテリアライズドビューの作成
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
    DATE_TRUNC('day', order_date) AS date,
    product_id,
    COUNT(*) AS order_count,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_revenue
FROM orders
GROUP BY DATE_TRUNC('day', order_date), product_id;

-- 自動リフレッシュの設定
ALTER MATERIALIZED VIEW daily_sales_summary AUTO REFRESH YES;

-- 手動リフレッシュ
REFRESH MATERIALIZED VIEW daily_sales_summary;

-- マテリアライズドビューをクエリ（高速）
SELECT * FROM daily_sales_summary
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY total_revenue DESC;
```

### 7. Redshift ML

SQLで機械学習モデルを作成・使用します。

```sql
-- 機械学習モデルの作成（SageMaker Autopilot使用）
CREATE MODEL customer_churn_model
FROM (
    SELECT
        customer_id,
        total_purchases,
        days_since_last_purchase,
        average_order_value,
        churned
    FROM customer_features
)
TARGET churned
FUNCTION predict_churn
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftMLRole'
AUTO ON
MODEL_TYPE XGBOOST
OBJECTIVE 'binary:logistic'
SETTINGS (
    S3_BUCKET 'ml-models-bucket'
);

-- 予測の実行
SELECT
    customer_id,
    predict_churn(total_purchases, days_since_last_purchase, average_order_value) AS churn_probability
FROM customer_features
WHERE predict_churn(total_purchases, days_since_last_purchase, average_order_value) > 0.7
ORDER BY churn_probability DESC;
```

### 8. Redshiftパフォーマンス最適化

適切な分散キーとソートキーを設定します。

```sql
-- 分散キーとソートキーの設定
CREATE TABLE orders (
    order_id BIGINT NOT NULL,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
)
DISTKEY(customer_id)  -- 結合キーで分散
SORTKEY(order_date);  -- 日付でソート（範囲クエリ高速化）

-- 圧縮エンコーディングの最適化
ANALYZE COMPRESSION orders;

-- テーブルの最適化（VACUUM + ANALYZE）
VACUUM orders;
ANALYZE orders;

-- クエリプランの確認
EXPLAIN
SELECT customer_id, SUM(total_amount)
FROM orders
WHERE order_date >= '2025-01-01'
GROUP BY customer_id;
```

**最適化の原則**:
- **DISTKEY**: 結合キーまたは均等分散
- **SORTKEY**: WHERE句/ORDER BYで頻繁に使う列
- **圧縮**: 自動圧縮または手動ENCODING指定

## 思考プロセス

Redshiftのデータウェアハウスを設計する際の段階的な思考プロセスです。

### フェーズ1: Serverless vs Provisioned の選択

```python
"""
Redshift Serverless vs Provisioned 選択ロジック
"""

def choose_redshift_deployment(requirements):
    """
    要件に基づいてServerless vs Provisionedを選択
    """
    # Serverless推奨ケース
    if requirements.workload_pattern == 'intermittent':
        return {
            'deployment': 'Serverless',
            'reason': '間欠的なワークロード、アイドル時間が長い',
            'cost_model': '使用時間のみ課金'
        }

    if requirements.is_new_project:
        return {
            'deployment': 'Serverless',
            'reason': '新規プロジェクト、使用量が不明',
            'recommendation': '6ヶ月後にコスト分析してProvisionedを検討'
        }

    if requirements.unpredictable_workload:
        return {
            'deployment': 'Serverless',
            'reason': '予測不可能なワークロード、自動スケーリング必要'
        }

    # Provisioned推奨ケース
    if requirements.continuous_workload and requirements.high_concurrency:
        return {
            'deployment': 'Provisioned (RA3)',
            'reason': '継続的な高負荷ワークロード',
            'cost_savings': 'Serverlessより30-50%安い（連続稼働時）'
        }

    if requirements.data_size_tb > 100:
        return {
            'deployment': 'Provisioned (RA3)',
            'reason': '大規模データ（100TB以上）',
            'benefits': 'Managed Storageでコスト効率が良い'
        }

    # デフォルト
    return {
        'deployment': 'Serverless',
        'reason': '2025年のデフォルト推奨（管理不要）'
    }

# 使用例
class Requirements:
    workload_pattern = 'continuous'
    is_new_project = False
    unpredictable_workload = False
    continuous_workload = True
    high_concurrency = True
    data_size_tb = 150

requirements = Requirements()
recommendation = choose_redshift_deployment(requirements)
print(f"推奨デプロイメント: {recommendation}")
```

### フェーズ2: テーブル設計

```python
"""
Redshiftテーブル設計の最適化
"""

def design_redshift_table(table_characteristics):
    """
    テーブル特性に基づいて最適な設計を提案
    """
    design = {}

    # 分散キー（DISTKEY）の選択
    if table_characteristics.has_frequent_joins:
        # 結合キーで分散
        design['distkey'] = table_characteristics.join_column
        design['distkey_reason'] = '結合キーで分散してコロケーション最適化'
    elif table_characteristics.size_gb < 10:
        # 小さいテーブルは全ノードに複製
        design['diststyle'] = 'ALL'
        design['distkey_reason'] = '小さいテーブルは全ノードに複製'
    else:
        # 均等分散
        design['diststyle'] = 'EVEN'
        design['distkey_reason'] = '結合なし、均等分散'

    # ソートキー（SORTKEY）の選択
    if table_characteristics.has_time_column:
        # 時系列データはタイムスタンプでソート
        design['sortkey'] = table_characteristics.time_column
        design['sortkey_reason'] = '範囲クエリ高速化'
    elif table_characteristics.frequent_filter_column:
        # フィルタ列でソート
        design['sortkey'] = table_characteristics.frequent_filter_column
        design['sortkey_reason'] = 'WHERE句で頻繁に使用'

    # 圧縮
    design['compression'] = 'AUTO'
    design['compression_reason'] = 'COPY時に自動圧縮エンコーディング適用'

    return design

# 使用例
class TableCharacteristics:
    has_frequent_joins = True
    join_column = 'customer_id'
    size_gb = 500
    has_time_column = True
    time_column = 'order_date'
    frequent_filter_column = 'status'

table = TableCharacteristics()
table_design = design_redshift_table(table)
print(f"推奨テーブル設計: {table_design}")
```

### フェーズ3: コスト最適化

```python
"""
Redshiftコスト最適化戦略
"""

def optimize_redshift_cost(current_config):
    """
    現在の構成からコスト最適化の提案を生成
    """
    recommendations = []

    # 1. Redshift Spectrumで古いデータをS3に移行
    if current_config.has_historical_data:
        # 過去1年以上のデータはS3に移行
        s3_storage_cost = current_config.historical_data_tb * 0.023  # S3 Standard
        redshift_storage_cost = current_config.historical_data_tb * 24  # RA3 Managed Storage
        savings = redshift_storage_cost - s3_storage_cost

        recommendations.append({
            'action': '古いデータをS3に移行してSpectrumでクエリ',
            'savings_per_month': savings,
            'implementation': 'UNLOAD ... TO S3, CREATE EXTERNAL TABLE'
        })

    # 2. Reserved Instances（Provisioned のみ）
    if current_config.deployment == 'provisioned' and current_config.uptime_percentage > 75:
        savings = current_config.monthly_cost * 0.4  # 40%削減
        recommendations.append({
            'action': 'Reserved Instances（1年契約）に変更',
            'savings_per_month': savings,
            'roi_months': 12 / 0.4
        })

    # 3. Concurrency Scaling（使用状況確認）
    if current_config.concurrency_scaling_usage_hours < 10:
        # 1日1時間の無料枠を使い切っていない
        recommendations.append({
            'action': 'Concurrency Scalingの設定見直し',
            'reason': '無料枠を活用できていない',
            'recommendation': 'max_concurrency_scaling_clustersを増やす'
        })

    # 4. マテリアライズドビューの活用
    if len(current_config.slow_queries) > 0:
        recommendations.append({
            'action': '頻繁なクエリにマテリアライズドビューを作成',
            'benefit': 'クエリ時間を10-100倍高速化',
            'cost_tradeoff': 'ストレージ増加 vs コンピュート削減'
        })

    return recommendations

# 使用例
class CurrentConfig:
    has_historical_data = True
    historical_data_tb = 50
    deployment = 'provisioned'
    uptime_percentage = 95
    monthly_cost = 5000
    concurrency_scaling_usage_hours = 5
    slow_queries = ['daily_sales_report', 'customer_segmentation']

config = CurrentConfig()
optimizations = optimize_redshift_cost(config)
for opt in optimizations:
    print(f"最適化提案: {opt}")
```

### フェーズ4: パフォーマンス監視

```sql
-- クエリパフォーマンスの監視
SELECT
    query,
    TRIM(querytxt) AS sql,
    starttime,
    endtime,
    DATEDIFF(seconds, starttime, endtime) AS duration_seconds,
    aborted
FROM stl_query
WHERE userid > 1  -- システムクエリを除外
    AND starttime >= DATEADD(hour, -1, GETDATE())
ORDER BY duration_seconds DESC
LIMIT 10;

-- テーブルのディスク使用量
SELECT
    TRIM(pgn.nspname) AS schema_name,
    TRIM(a.name) AS table_name,
    SUM(a.rows) AS row_count,
    SUM(a.used_mb) AS used_mb,
    SUM(a.unsorted_mb) AS unsorted_mb
FROM (
    SELECT
        db_id, id, name,
        SUM(rows) AS rows,
        SUM(used) / 1024 / 1024 AS used_mb,
        SUM(unsorted_rows) / 1024 / 1024 AS unsorted_mb
    FROM stv_tbl_perm
    GROUP BY db_id, id, name
) AS a
JOIN pg_class AS pgc ON pgc.oid = a.id
JOIN pg_namespace AS pgn ON pgn.oid = pgc.relnamespace
GROUP BY schema_name, table_name
ORDER BY used_mb DESC;

-- VACUUMが必要なテーブル
SELECT
    TRIM(schema) AS schema_name,
    TRIM("table") AS table_name,
    unsorted / NULLIF(total, 0) * 100 AS unsorted_percentage
FROM svv_table_info
WHERE unsorted / NULLIF(total, 0) > 0.05  -- 5%以上
ORDER BY unsorted_percentage DESC;
```

## ベストプラクティス（2025年版）

### 1. Redshift Serverlessをデフォルトに

**推奨**: 新規プロジェクトはServerlessで開始

```bash
# Serverlessの利点
# - インフラ管理不要
# - 自動スケーリング
# - アイドル時の課金なし
# - 数分で開始可能
```

### 2. RA3ノードでコンピュートとストレージを分離

```bash
# Provisionedの場合はRA3を選択
# DC2は2025年に非推奨
```

### 3. Redshift Spectrumで古いデータをS3に

```sql
-- 過去1年以上のデータはS3に
UNLOAD ('SELECT * FROM orders WHERE order_date < DATEADD(year, -1, GETDATE())')
TO 's3://datalake-bucket/historical-orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftUnloadRole'
PARQUET
PARTITION BY (year, month);

-- 外部テーブルで引き続きアクセス可能
```

### 4. マテリアライズドビューで頻繁なクエリを高速化

```sql
-- 集計クエリをマテリアライズドビューに
CREATE MATERIALIZED VIEW sales_summary AS ...
AUTO REFRESH YES;
```

### 5. データ共有でワークロード分離

```sql
-- 本番クラスター → 分析クラスター
-- ETLなしでデータ共有
```

### 6. ゼロETL統合でリアルタイム分析

```bash
# RDS/Aurora → Redshift
# ETLパイプライン不要
```

## よくある落とし穴と対策

### 1. 不適切な分散キー

**症状**: データスキュー、クエリが遅い

**対策**:

```sql
-- データスキューを確認
SELECT
    slice,
    COUNT(*) AS row_count
FROM stv_blocklist
WHERE tbl = (SELECT id FROM stv_tbl_perm WHERE name = 'orders')
GROUP BY slice
ORDER BY row_count DESC;

-- 分散キーを変更
ALTER TABLE orders ALTER DISTKEY customer_id;
```

### 2. VACUUMとANALYZEの未実施

**症状**: クエリが徐々に遅くなる

**対策**:

```sql
-- 定期的にVACUUMとANALYZE
VACUUM orders;
ANALYZE orders;

-- または自動VACUUMを有効化
ALTER TABLE orders ALTER AUTOSTAT YES;
```

### 3. Spectrumでフルスキャン

**症状**: 高額なSpectrum料金

**対策**:

```sql
-- Parquet/ORC形式で圧縮
-- パーティション化
-- 列指定（SELECT * を避ける）

SELECT order_id, total_amount
FROM spectrum_schema.sales
WHERE year = 2025 AND month = 1;  -- パーティションフィルタ
```

## 判断ポイント

### Serverless vs Provisioned 選択マトリクス

| ワークロード | 推奨 | 理由 |
|------------|------|------|
| 新規プロジェクト | **Serverless** | 使用量不明 |
| 間欠的（1日数時間） | **Serverless** | アイドル時課金なし |
| 連続稼働（24時間） | **Provisioned** | Serverlessより安い |
| 予測不可能 | **Serverless** | 自動スケーリング |
| 100TB以上 | **Provisioned (RA3)** | コスト効率 |

## 検証ポイント

### 1. パフォーマンステスト

```sql
-- ベンチマーククエリの実行
EXPLAIN
SELECT ...;

-- 実行時間計測
SET enable_result_cache_for_session TO OFF;
SELECT ...;
```

### 2. コスト分析

```bash
# Cost Explorerで月間コストを確認
# Serverless: RPU-hours
# Provisioned: ノード時間 + Managed Storage
# Spectrum: スキャンデータ量
```

## 他のスキルとの統合

### S3スキルとの統合

```sql
-- S3データレイク → Redshift Spectrum
CREATE EXTERNAL SCHEMA ...
```

### Glueスキルとの統合

```bash
# Glue Catalog → Redshift Spectrum
# メタデータ共有
```

## リソース

### 公式ドキュメント

- [Amazon Redshift Documentation](https://docs.aws.amazon.com/redshift/)
- [Redshift Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html)
- [Redshift Best Practices](https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html)
- [Redshift Spectrum](https://docs.aws.amazon.com/redshift/latest/dg/c-using-spectrum.html)

### ツールとライブラリ

- [AWS CLI Redshift Commands](https://docs.aws.amazon.com/cli/latest/reference/redshift/)
- [Boto3 Redshift Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html)
