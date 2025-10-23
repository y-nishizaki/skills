---
name: aws-glue
description: AWS Glueを使用してサーバーレスETLを実行し、Data Catalog、Glue Studio、生成AI機能でデータ統合と変換を自動化する方法
---

# AWS Glue スキル

## 概要

AWS Glueは、データの検出、準備、統合を簡素化するサーバーレスデータ統合サービスです。ETL（Extract、Transform、Load）ジョブをApache Spark上で実行し、Data Catalogでメタデータを一元管理します。

## 主な使用ケース

### 1. Glue Crawlerでスキーマ自動検出

```bash
# S3データのCrawler作成
aws glue create-crawler \
    --name s3-sales-crawler \
    --role AWSGlueServiceRole-DataCatalog \
    --database-name sales_db \
    --targets '{
        "S3Targets": [{
            "Path": "s3://my-data-lake/sales/",
            "Exclusions": ["**.tmp", "**_$folder$"]
        }]
    }' \
    --schema-change-policy '{
        "UpdateBehavior": "UPDATE_IN_DATABASE",
        "DeleteBehavior": "LOG"
    }' \
    --recrawl-policy '{
        "RecrawlBehavior": "CRAWL_NEW_FOLDERS_ONLY"
    }' \
    --schedule "cron(0 2 * * ? *)"

# Crawler実行
aws glue start-crawler --name s3-sales-crawler

# ステータス確認
aws glue get-crawler --name s3-sales-crawler
```

### 2. Glue ETLジョブ（PySpark）

```python
# glue_etl_job.py
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Data Catalogからデータ読み込み
datasource = glueContext.create_dynamic_frame.from_catalog(
    database = "sales_db",
    table_name = "raw_sales"
)

# 変換処理
# 1. 不要なカラムを削除
applymapping = ApplyMapping.apply(
    frame = datasource,
    mappings = [
        ("order_id", "string", "order_id", "string"),
        ("customer_id", "string", "customer_id", "string"),
        ("amount", "double", "amount", "decimal(10,2)"),
        ("order_date", "string", "order_date", "date")
    ]
)

# 2. 重複削除
deduplicated = applymapping.toDF().dropDuplicates(["order_id"])

# 3. Parquet形式でS3に出力
glueContext.write_dynamic_frame.from_options(
    frame = DynamicFrame.fromDF(deduplicated, glueContext, "deduplicated"),
    connection_type = "s3",
    connection_options = {
        "path": "s3://my-data-lake/processed/sales/",
        "partitionKeys": ["year", "month"]
    },
    format = "parquet",
    format_options = {
        "compression": "snappy"
    }
)

job.commit()
```

```bash
# ジョブ作成
aws glue create-job \
    --name sales-etl-job \
    --role AWSGlueServiceRole-ETL \
    --command '{
        "Name": "glueetl",
        "ScriptLocation": "s3://my-scripts/glue_etl_job.py",
        "PythonVersion": "3"
    }' \
    --default-arguments '{
        "--TempDir": "s3://my-temp/",
        "--job-language": "python",
        "--enable-glue-datacatalog": "true",
        "--enable-job-insights": "true",
        "--enable-spark-ui": "true",
        "--spark-event-logs-path": "s3://my-logs/"
    }' \
    --glue-version "4.0" \
    --number-of-workers 10 \
    --worker-type G.1X

# ジョブ実行
aws glue start-job-run --job-name sales-etl-job
```

### 3. Glue Studio（ビジュアルETL）

```bash
# Glue Studioで作成したジョブの確認
aws glue get-job --job-name visual-etl-job

# ジョブ実行履歴
aws glue get-job-runs --job-name visual-etl-job --max-results 10
```

### 4. Data Catalogテーブル操作

```bash
# テーブル一覧
aws glue get-tables --database-name sales_db

# テーブル詳細
aws glue get-table \
    --database-name sales_db \
    --name raw_sales

# パーティション追加
aws glue create-partition \
    --database-name sales_db \
    --table-name sales_partitioned \
    --partition-input '{
        "Values": ["2025", "01"],
        "StorageDescriptor": {
            "Columns": [
                {"Name": "order_id", "Type": "string"},
                {"Name": "amount", "Type": "decimal(10,2)"}
            ],
            "Location": "s3://my-data-lake/sales/2025/01/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            }
        }
    }'
```

### 5. Glue DataBrew（ノーコードデータ準備）

```bash
# DataBrewプロジェクト作成
aws databrew create-project \
    --name sales-cleanup \
    --dataset-name sales_raw \
    --role-arn arn:aws:iam::123456789012:role/DataBrewRole \
    --recipe-name sales-recipe

# レシピステップ（例：日付形式変換）
aws databrew create-recipe \
    --name sales-recipe \
    --steps '[{
        "Action": {
            "Operation": "CHANGE_TYPE",
            "Parameters": {
                "sourceColumn": "order_date",
                "targetType": "date"
            }
        }
    }]'
```

## ベストプラクティス（2025年版）

### 1. 生成AI機能の活用（Amazon Q Data Integration）

```text
2025年新機能:
- 自然言語でETLジョブ作成
- 例: 「S3の顧客データとRDSの注文データを結合して、月次売上を計算」
- 自動でPySpark/Scalaコード生成
```

### 2. Glue Data Quality

```python
# データ品質ルール定義
ruleset = """
Rules = [
    ColumnValues "amount" > 0,
    ColumnDataType "order_date" = "DATE",
    IsComplete "customer_id",
    ColumnValues "status" in ["PENDING", "COMPLETED", "CANCELLED"],
    Uniqueness "order_id" > 0.95
]
"""

# データ品質チェック実行
datasource_with_quality = EvaluateDataQuality.apply(
    frame = datasource,
    ruleset = ruleset,
    publishing_options = {
        "dataQualityEvaluationContext": "sales_dq",
        "enableDataQualityCloudWatchMetrics": True,
        "enableDataQualityResultsPublishing": True
    }
)
```

### 3. ジョブブックマーク（増分処理）

```bash
# ジョブブックマーク有効化
aws glue update-job \
    --job-name sales-etl-job \
    --job-update '{
        "DefaultArguments": {
            "--job-bookmark-option": "job-bookmark-enable"
        }
    }'
```

```python
# PySpark内でブックマーク使用
datasource = glueContext.create_dynamic_frame.from_catalog(
    database = "sales_db",
    table_name = "raw_sales",
    transformation_ctx = "datasource"  # ブックマーク追跡用
)
```

### 4. Iceberg対応（2025年機能強化）

```python
# Apache Icebergテーブル作成
additional_options = {
    "hoodie.table.name": "sales_iceberg",
    "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
    "path": "s3://my-bucket/iceberg/sales/"
}

glueContext.write_data_frame.from_catalog(
    frame = df,
    database = "sales_db",
    table_name = "sales_iceberg",
    additional_options = additional_options,
    format = "hudi"
)
```

### 5. コスト最適化

```bash
# Flex実行（非緊急ジョブで最大34%削減）
aws glue start-job-run \
    --job-name sales-etl-job \
    --execution-class FLEX \
    --timeout 120

# Auto Scaling
aws glue update-job \
    --job-name sales-etl-job \
    --job-update '{
        "MaxCapacity": null,
        "NumberOfWorkers": 10,
        "WorkerType": "G.1X",
        "ExecutionProperty": {
            "MaxConcurrentRuns": 3
        }
    }'
```

## よくある失敗パターン

### 1. 大きすぎるパーティション

```text
問題: 1パーティションに数TBのデータ
解決: year/month/dayで細かく分割

悪い例: s3://bucket/data/year=2025/
良い例: s3://bucket/data/year=2025/month=01/day=15/
```

### 2. Data Catalogスキーマ不一致

```python
# 解決: ResolveChoiceで型を統一
resolved = ResolveChoice.apply(
    frame = datasource,
    choice = "cast:long",
    transformation_ctx = "resolved"
)
```

### 3. 小ファイル問題

```python
# 解決: groupFilesオプション
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type = "s3",
    connection_options = {
        "paths": ["s3://my-bucket/small-files/"],
        "groupFiles": "inPartition",
        "groupSize": "134217728"  # 128MB
    },
    format = "parquet"
)
```

## リソース

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [Glue Studio](https://docs.aws.amazon.com/glue/latest/ug/what-is-glue-studio.html)
- [Amazon Q Data Integration](https://aws.amazon.com/glue/features/amazon-q/)
