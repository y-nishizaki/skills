---
name: aws-athena
description: AWS Athenaを使用してS3データレイクに対してSQLクエリを実行し、Parquet最適化、パーティション、クエリチューニングでコストとパフォーマンスを改善する方法
---

# AWS Athena スキル

## 概要

Amazon Athenaは、S3上のデータに対してSQL (Presto/Trino) を使用してクエリを実行できるサーバーレス対話型クエリサービスです。インフラ管理不要で、スキャンしたデータ量に応じた従量課金でビッグデータ分析を実現します。

## 主な使用ケース

### 1. Parquet形式でのデータ最適化

```bash
# Athenaテーブル作成（Parquet形式）
CREATE EXTERNAL TABLE IF NOT EXISTS sales_parquet (
    order_id STRING,
    product_id STRING,
    customer_id STRING,
    amount DECIMAL(10,2),
    order_date DATE
)
STORED AS PARQUET
LOCATION 's3://my-bucket/sales-parquet/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

# CSVからParquetへの変換（CTAS）
CREATE TABLE sales_optimized
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    external_location = 's3://my-bucket/sales-optimized/'
)
AS SELECT * FROM sales_csv;
```

### 2. パーティション戦略

```sql
-- パーティション付きテーブル作成
CREATE EXTERNAL TABLE logs_partitioned (
    request_id STRING,
    user_id STRING,
    status_code INT,
    response_time DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT,
    day INT
)
STORED AS PARQUET
LOCATION 's3://my-bucket/logs/';

-- パーティション追加
ALTER TABLE logs_partitioned ADD IF NOT EXISTS
    PARTITION (year=2025, month=1, day=15)
    LOCATION 's3://my-bucket/logs/2025/01/15/';

-- Partition Projection（自動パーティション検出）
CREATE EXTERNAL TABLE logs_projected (
    request_id STRING,
    user_id STRING
)
PARTITIONED BY (dt STRING)
STORED AS PARQUET
LOCATION 's3://my-bucket/logs/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.dt.type' = 'date',
    'projection.dt.range' = '2024-01-01,NOW',
    'projection.dt.format' = 'yyyy-MM-dd',
    'storage.location.template' = 's3://my-bucket/logs/${dt}/'
);
```

### 3. クエリ最適化

```sql
-- 悪い例：全カラム選択
SELECT * FROM sales WHERE order_date = '2025-01-15';

-- 良い例：必要なカラムのみ選択
SELECT order_id, amount
FROM sales
WHERE order_date = '2025-01-15';

-- パーティションフィルタを活用
SELECT SUM(amount)
FROM sales_partitioned
WHERE year = 2025 AND month = 1;

-- WITH句で複雑なクエリを整理
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS total
    FROM sales
    WHERE year = 2025
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT * FROM monthly_sales ORDER BY total DESC;
```

### 4. AWS CLIでのクエリ実行

```bash
# クエリ実行
aws athena start-query-execution \
    --query-string "SELECT COUNT(*) FROM sales WHERE year=2025" \
    --query-execution-context Database=analytics \
    --result-configuration OutputLocation=s3://athena-results/

# クエリステータス確認
QUERY_ID=$(aws athena start-query-execution \
    --query-string "SELECT * FROM sales LIMIT 10" \
    --query-execution-context Database=analytics \
    --result-configuration OutputLocation=s3://athena-results/ \
    --query 'QueryExecutionId' --output text)

aws athena get-query-execution --query-execution-id $QUERY_ID

# 結果取得
aws athena get-query-results --query-execution-id $QUERY_ID
```

### 5. Glue Data Catalogとの連携

```bash
# Glue Crawlerでスキーマ自動検出
aws glue create-crawler \
    --name sales-crawler \
    --role AWSGlueServiceRole \
    --database-name analytics \
    --targets '{
        "S3Targets": [{
            "Path": "s3://my-bucket/sales/"
        }]
    }' \
    --schema-change-policy '{
        "UpdateBehavior": "UPDATE_IN_DATABASE",
        "DeleteBehavior": "LOG"
    }'

# Crawler実行
aws glue start-crawler --name sales-crawler
```

## ベストプラクティス（2025年版）

### 1. ファイルサイズの最適化

```text
推奨ファイルサイズ: 128MB〜512MB
- 小さすぎるファイル（< 128MB）: メタデータオーバーヘッド増加
- 大きすぎるファイル（> 512MB）: 並列処理の効率低下

Parquet設定:
- Row Group Size: 128MB（デフォルト）
- カラム数が多い場合: 256MB以上に増加を検討
```

### 2. 圧縮形式の選択

```sql
-- Parquet: SNAPPY推奨（バランス型）
CREATE TABLE data_snappy
WITH (format = 'PARQUET', parquet_compression = 'SNAPPY')
AS SELECT * FROM source;

-- GZIP: 圧縮率重視（クエリは遅くなる）
CREATE TABLE data_gzip
WITH (format = 'PARQUET', parquet_compression = 'GZIP')
AS SELECT * FROM source;
```

### 3. データソート

```sql
-- 頻繁にフィルタするカラムでソート
CREATE TABLE sales_sorted
WITH (
    format = 'PARQUET',
    bucketed_by = ARRAY['customer_id'],
    bucket_count = 10
)
AS SELECT * FROM sales ORDER BY order_date, customer_id;
```

### 4. コスト最適化

```bash
# スキャン量確認（コスト見積もり）
aws athena start-query-execution \
    --query-string "SELECT COUNT(*) FROM sales WHERE year=2025" \
    --query-execution-context Database=analytics \
    --result-configuration OutputLocation=s3://athena-results/ \
    --query 'QueryExecutionId' --output text

# CloudWatch Metricsで監視
aws cloudwatch put-metric-alarm \
    --alarm-name athena-high-scan \
    --metric-name DataScannedInBytes \
    --namespace AWS/Athena \
    --statistic Sum \
    --period 3600 \
    --threshold 1000000000000 \
    --comparison-operator GreaterThanThreshold
```

### 5. ワークグループの活用

```bash
# ワークグループ作成（クエリコスト制限）
aws athena create-work-group \
    --name analytics-team \
    --configuration '{
        "ResultConfigurationUpdates": {
            "OutputLocation": "s3://athena-results/analytics/"
        },
        "EnforceWorkGroupConfiguration": true,
        "EngineVersion": {
            "SelectedEngineVersion": "Athena engine version 3"
        },
        "BytesScannedCutoffPerQuery": 100000000000
    }' \
    --description "Analytics team workgroup with 100GB scan limit"
```

## よくある失敗パターン

### 1. SELECT * の乱用

```sql
-- 悪い例：不要なカラムもスキャン
SELECT * FROM large_table WHERE id = 123;

-- 良い例：必要なカラムのみ
SELECT id, name, created_at FROM large_table WHERE id = 123;
```

### 2. パーティション未使用

```sql
-- 悪い例：全データスキャン
SELECT * FROM sales WHERE order_date = '2025-01-15';

-- 良い例：パーティションフィルタ
SELECT * FROM sales_partitioned
WHERE year = 2025 AND month = 1 AND day = 15;
```

### 3. 小さすぎるファイル

```text
問題: 数千の小さなファイル（< 1MB）
解決: S3上でファイルを統合してから読み込む

# AWS Glue ETLで統合
groupFiles='inPartition'
groupSize='134217728'  # 128MB
```

## リソース

- [Athena Documentation](https://docs.aws.amazon.com/athena/)
- [Performance Tuning Tips](https://aws.amazon.com/blogs/big-data/top-10-performance-tuning-tips-for-amazon-athena/)
- [Partition Projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)
