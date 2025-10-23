---
name: "Databricks ETLパイプライン構築"
description: "DatabricksでのETLパイプライン構築。Delta Live Tables、メダリオンアーキテクチャ、バッチ/ストリーミング処理、データ品質チェック"
---

# Databricks ETLパイプライン構築

## このスキルを使う場面

- ETLパイプラインを設計・構築したい
- Delta Live Tablesを活用したい
- メダリオンアーキテクチャを実装したい
- データ品質を保証したい
- バッチとストリーミングを統合したい

## ETLパイプラインの基本

### 従来のアプローチ

```python
# Extract
df_raw = spark.read.json("s3://bucket/raw-data/")

# Transform
df_cleaned = df_raw.filter(col("status") == "active") \
    .withColumn("processed_at", current_timestamp())

# Load
df_cleaned.write.format("delta").mode("append").save("/mnt/processed/")
```

### Delta Live Tables (DLT) アプローチ

宣言的な定義により、Databricksが自動的に最適化・実行:

```python
import dlt
from pyspark.sql.functions import col, current_timestamp

# Bronze層: 生データ
@dlt.table(
    comment="Raw data from source"
)
def bronze_events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("s3://bucket/raw-data/")

# Silver層: クレンジング済みデータ
@dlt.table(
    comment="Cleaned and validated events"
)
@dlt.expect_or_drop("valid_status", "status IS NOT NULL")
@dlt.expect("recent_data", "event_date > '2020-01-01'")
def silver_events():
    return dlt.read_stream("bronze_events") \
        .filter(col("status").isNotNull()) \
        .withColumn("processed_at", current_timestamp())

# Gold層: ビジネスレベルの集計
@dlt.table(
    comment="Daily aggregated metrics"
)
def gold_daily_metrics():
    return dlt.read("silver_events") \
        .groupBy("date", "category") \
        .agg(
            count("*").alias("event_count"),
            sum("amount").alias("total_amount")
        )
```

## メダリオンアーキテクチャ

### Bronze層 (ブロンズ)

**目的**: 生データの保存
- ソースからのデータをそのまま保存
- スキーマ推論または緩いスキーマ
- 監査とリプレイのための完全な履歴

### Silver層 (シルバー)

**目的**: クレンジングと統合
- 重複削除
- NULL値の処理
- データ型の標準化
- 軽微なビジネスルールの適用

### Gold層 (ゴールド)

**目的**: ビジネス集計
- レポート用の集計テーブル
- ダッシュボード用のマート
- ML特徴量テーブル

## データ品質 (Expectations)

```python
# データ品質チェック
@dlt.table
@dlt.expect("valid_email", "email LIKE '%@%.%'")
@dlt.expect_or_drop("positive_amount", "amount > 0")
@dlt.expect_or_fail("required_id", "id IS NOT NULL")
def quality_checked_data():
    return dlt.read_stream("source_table")
```

## ストリーミングETL

```python
# Auto Loader でストリーミング取り込み
@dlt.table
def streaming_bronze():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .option("cloudFiles.schemaLocation", "/mnt/schema/") \
        .load("/mnt/raw-data/")

# ストリーミング集計
@dlt.table
def streaming_aggregation():
    return dlt.read_stream("streaming_bronze") \
        .withWatermark("timestamp", "10 minutes") \
        .groupBy(window("timestamp", "5 minutes"), "user_id") \
        .count()
```

## ベストプラクティス

1. **Photon Engineを有効化** - 最大12倍高速
2. **Serverlessを使用** - 起動時間を秒単位に短縮
3. **メダリオンアーキテクチャを採用** - データ品質の段階的向上
4. **Expectationsで品質保証** - 各層で厳格化
5. **増分処理** - 新規データのみ処理して高速化

## まとめ

Delta Live Tablesは、ETLパイプラインを宣言的に定義し、Databricksが自動的に最適化・実行。メダリオンアーキテクチャとデータ品質チェックで信頼性の高いパイプラインを構築できる。
