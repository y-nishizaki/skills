---
name: "Databricks Lakehouseアーキテクチャ"
description: "Lakehouseアーキテクチャの理解。データレイク+ウェアハウス統合、メダリオンアーキテクチャ、Delta Lake、Unity Catalog"
---

# Databricks Lakehouseアーキテクチャ

## Lakehouse概念

**データレイク + データウェアハウス = Lakehouse**

### 従来アーキテクチャの課題

**データレイク**:
- ✅ 大容量・低コスト（オブジェクトストレージ）
- ✅ 非構造化・半構造化データ対応
- ✅ スケーラビリティ
- ❌ ACIDトランザクションなし
- ❌ クエリパフォーマンス低い
- ❌ データ品質管理困難
- ❌ スキーマ進化対応弱い

**データウェアハウス**:
- ✅ 高速クエリ
- ✅ ACIDトランザクション
- ✅ 成熟したBI統合
- ✅ スキーマ管理
- ❌ 高コスト（専用ストレージ）
- ❌ スケーラビリティ制限
- ❌ 非構造化データ未対応
- ❌ リアルタイム処理弱い

**Lakehouse**:
- ✅ 両方の利点を統合
- ✅ Delta Lakeで信頼性（ACID）
- ✅ Unity Catalogでガバナンス
- ✅ オブジェクトストレージで低コスト
- ✅ 構造化・非構造化データ統合
- ✅ リアルタイムバッチ処理統合

### Lakehouse主要コンポーネント

```
┌─────────────────────────────────────┐
│      Unity Catalog (ガバナンス)      │
│  - メタデータ管理                     │
│  - アクセス制御                       │
│  - データリネージ                     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    Compute Layer (Spark/Photon)     │
│  - クエリエンジン                     │
│  - ストリーミング                     │
│  - ML                               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     Storage Layer (Delta Lake)      │
│  - ACID トランザクション              │
│  - タイムトラベル                     │
│  - データバージョニング                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Object Storage (S3/ADLS/GCS)       │
│  - 低コスト                          │
│  - 無制限スケール                     │
└─────────────────────────────────────┘
```

## メダリオンアーキテクチャ

```
Raw Data → Bronze → Silver → Gold → BI/ML/Applications
           (生)    (整形)   (集計)
```

**メダリオンの目的**:
- データ品質の段階的向上
- 処理の分離と再利用
- 複数消費者への最適化
- データリネージの明確化

### Bronze層（Raw Layer）

```python
# 生データ保存
@dlt.table(
    comment="Raw events from source systems",
    table_properties={
        "quality": "bronze",
        "delta.enableChangeDataFeed": "true"
    }
)
def bronze_events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .option("cloudFiles.inferColumnTypes", "true") \
        .option("cloudFiles.schemaLocation", "/mnt/schemas/events") \
        .load("/mnt/raw/events/")
```

**Bronze層の設計原則**:
- ソースデータをそのまま保存（スキーマレス）
- 最小限の変換のみ
- 監査トレール・データリプレイ可能
- メタデータ追加（取込時刻、ソース等）

```python
# メタデータ追加
from pyspark.sql.functions import current_timestamp, input_file_name

@dlt.table
def bronze_sales():
    return spark.readStream \
        .format("cloudFiles") \
        .option("cloudFiles.format", "csv") \
        .load("/mnt/raw/sales/") \
        .withColumn("ingestion_time", current_timestamp()) \
        .withColumn("source_file", input_file_name())
```

**Bronze層のユースケース**:
- 監査・コンプライアンス
- データリプレイ（障害復旧）
- スキーマ進化への対応
- 歴史的データ保持

### Silver層（Refined Layer）

```python
# クレンジング・統合
@dlt.table(
    comment="Cleaned and enriched events",
    table_properties={
        "quality": "silver"
    }
)
@dlt.expect_or_drop("valid_user", "user_id IS NOT NULL")
@dlt.expect_or_drop("valid_amount", "amount >= 0")
def silver_events():
    return dlt.read_stream("bronze_events") \
        .filter(col("status") == "active") \
        .withColumn("processed_at", current_timestamp()) \
        .dropDuplicates(["event_id"]) \
        .withColumn("amount_usd", col("amount") * col("exchange_rate"))
```

**Silver層の処理**:
- 重複削除
- データ品質検証
- 型変換・標準化
- ディメンション結合
- エンリッチメント

```python
# 複雑な変換例
@dlt.table
def silver_orders():
    bronze = dlt.read("bronze_orders")
    customers = dlt.read("silver_customers")

    return bronze \
        .filter(col("order_status").isin(["completed", "shipped"])) \
        .withColumn("order_date", to_date(col("order_timestamp"))) \
        .join(customers, "customer_id", "left") \
        .select(
            col("order_id"),
            col("customer_id"),
            col("customer_name"),
            col("order_date"),
            col("amount"),
            col("region")
        )

# CDC処理
@dlt.table
def silver_customer_scd():
    """Type 2 SCD実装"""
    return dlt.read_stream("bronze_customers") \
        .withColumn("valid_from", current_timestamp()) \
        .withColumn("valid_to", lit(None).cast("timestamp")) \
        .withColumn("is_current", lit(True))
```

**Silver層のベストプラクティス**:
- 一つのBronzeテーブルから複数Silverテーブル作成可能
- ビジネスロジック適用開始
- データ品質expectation設定
- 増分処理活用

### Gold層（Curated Layer）

```python
# ビジネス集計
@dlt.table(
    comment="Daily sales metrics by region",
    table_properties={
        "quality": "gold"
    }
)
def gold_daily_metrics():
    return dlt.read("silver_events") \
        .groupBy("date", "region", "category") \
        .agg(
            count("*").alias("event_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            countDistinct("user_id").alias("unique_users")
        )
```

**Gold層の目的**:
- ビジネスレベル集計
- ダッシュボード用データマート
- ML特徴量テーブル
- レポート用最適化

```python
# BI用ビュー
@dlt.table
def gold_sales_dashboard():
    """ダッシュボード最適化テーブル"""
    silver_sales = dlt.read("silver_sales")
    dim_products = dlt.read("gold_dim_products")
    dim_customers = dlt.read("gold_dim_customers")

    return silver_sales \
        .join(dim_products, "product_id") \
        .join(dim_customers, "customer_id") \
        .select(
            col("order_date"),
            col("product_name"),
            col("product_category"),
            col("customer_segment"),
            col("region"),
            col("amount"),
            col("quantity")
        )

# ML特徴量テーブル
@dlt.table
def gold_customer_features():
    """ML用顧客特徴量"""
    from pyspark.sql.window import Window

    orders = dlt.read("silver_orders")

    window_spec = Window.partitionBy("customer_id") \
        .orderBy(col("order_date").desc())

    return orders \
        .groupBy("customer_id") \
        .agg(
            count("*").alias("total_orders"),
            sum("amount").alias("total_spent"),
            avg("amount").alias("avg_order_value"),
            max("order_date").alias("last_order_date"),
            datediff(current_date(), max("order_date")).alias("days_since_last_order")
        )
```

### メダリオン間のデータフロー

```python
# エンドツーエンドのDLTパイプライン
import dlt
from pyspark.sql.functions import *

# Bronze
@dlt.table
def bronze_raw_events():
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:9092") \
        .option("subscribe", "events") \
        .load()

# Silver
@dlt.table
@dlt.expect_all({
    "valid_timestamp": "event_time IS NOT NULL",
    "valid_user": "user_id IS NOT NULL"
})
def silver_events():
    return dlt.read_stream("bronze_raw_events") \
        .select(
            get_json_object(col("value").cast("string"), "$.event_id").alias("event_id"),
            get_json_object(col("value").cast("string"), "$.user_id").alias("user_id"),
            get_json_object(col("value").cast("string"), "$.event_time").cast("timestamp").alias("event_time")
        ) \
        .dropDuplicates(["event_id"])

# Gold
@dlt.table
def gold_hourly_events():
    return dlt.read("silver_events") \
        .groupBy(window("event_time", "1 hour")) \
        .agg(
            count("*").alias("event_count"),
            countDistinct("user_id").alias("unique_users")
        )
```

## Delta Lake統合

### ACID トランザクション

```sql
-- MERGE (UPSERT)
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- 条件付きMERGE
MERGE INTO customer_silver
USING customer_bronze
ON customer_silver.customer_id = customer_bronze.customer_id
WHEN MATCHED AND customer_bronze.last_updated > customer_silver.last_updated
    THEN UPDATE SET *
WHEN NOT MATCHED
    THEN INSERT *;

-- DELETE
DELETE FROM orders WHERE order_date < '2023-01-01';

-- UPDATE
UPDATE products
SET price = price * 1.1
WHERE category = 'electronics';
```

### タイムトラベル

```sql
-- バージョン指定
SELECT * FROM my_table VERSION AS OF 10;

-- タイムスタンプ指定
SELECT * FROM my_table TIMESTAMP AS OF '2025-01-01 00:00:00';

-- 履歴確認
DESCRIBE HISTORY my_table;

-- 特定バージョンとの差分
SELECT current.*, previous.*
FROM my_table AS current
JOIN my_table VERSION AS OF 5 AS previous
    ON current.id = previous.id
WHERE current.value <> previous.value;
```

### Change Data Feed (CDF)

```python
# CDF有効化
spark.sql("""
    CREATE TABLE events
    USING DELTA
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
    AS SELECT * FROM source
""")

# 変更データ読み取り
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 5) \
    .option("endingVersion", 10) \
    .table("events")

changes.filter(col("_change_type") == "insert").show()
```

### Delta Lake最適化

```sql
-- OPTIMIZE（ファイル結合）
OPTIMIZE my_table;

-- Z-ORDER（データスキッピング最適化）
OPTIMIZE my_table
ZORDER BY (customer_id, order_date);

-- VACUUM（古いファイル削除）
VACUUM my_table RETAIN 168 HOURS;  -- 7日間保持

-- データスキップ統計
ANALYZE TABLE my_table COMPUTE STATISTICS FOR ALL COLUMNS;
```

### スキーマ進化

```python
# スキーママージ
df_new_schema = spark.read.parquet("/new_data")

df_new_schema.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/delta/table")

# スキーマ強制
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "false")

# 明示的なスキーマ変更
spark.sql("""
    ALTER TABLE my_table
    ADD COLUMNS (new_column STRING COMMENT 'New field')
""")
```

## Unity Catalog統合

### 3層ネームスペース

```sql
-- Catalog -> Schema -> Table/View/Function
SELECT * FROM production.sales.orders;

-- Catalog作成
CREATE CATALOG lakehouse
COMMENT 'Main data lakehouse catalog'
MANAGED LOCATION 's3://bucket/lakehouse/';

-- Schema作成
CREATE SCHEMA lakehouse.bronze
COMMENT 'Raw ingested data';

CREATE SCHEMA lakehouse.silver
COMMENT 'Cleaned and enriched data';

CREATE SCHEMA lakehouse.gold
COMMENT 'Business aggregates and features';

-- Table作成
CREATE TABLE lakehouse.bronze.events (
    event_id STRING,
    user_id STRING,
    event_time TIMESTAMP,
    event_data STRING
)
USING DELTA
PARTITIONED BY (date(event_time));
```

### アクセス制御

```sql
-- グループ作成
CREATE GROUP data_engineers;
CREATE GROUP data_analysts;
CREATE GROUP ml_engineers;

-- Catalog権限
GRANT USE CATALOG lakehouse TO data_analysts;

-- Schema権限
GRANT USE SCHEMA lakehouse.silver TO data_analysts;
GRANT SELECT ON SCHEMA lakehouse.silver TO data_analysts;

-- テーブル権限
GRANT SELECT ON TABLE lakehouse.gold.sales_summary TO data_analysts;
GRANT ALL PRIVILEGES ON SCHEMA lakehouse.bronze TO data_engineers;

-- 動的ビュー（行レベルセキュリティ）
CREATE VIEW restricted_sales AS
SELECT *
FROM sales
WHERE region = (
    SELECT region
    FROM user_mapping
    WHERE username = current_user()
);
```

### データリネージ

```sql
-- リネージ確認（システムテーブル）
SELECT
    source_table_full_name,
    target_table_full_name,
    notebook_id,
    created_at
FROM system.access.table_lineage
WHERE target_table_full_name = 'lakehouse.gold.sales_summary';

-- 列レベルリネージ
SELECT
    source_column_name,
    target_column_name,
    transformation_type
FROM system.access.column_lineage
WHERE target_table_full_name = 'lakehouse.gold.sales_summary';
```

## データガバナンス

### データ品質管理

```python
# Delta Live Tables Expectations
@dlt.table
@dlt.expect_all_or_drop({
    "valid_email": "email LIKE '%@%.%'",
    "valid_age": "age BETWEEN 0 AND 120",
    "valid_amount": "amount >= 0"
})
def validated_customers():
    return dlt.read("bronze_customers")

# Great Expectations統合
from great_expectations.dataset import SparkDFDataset

def validate_dataframe(df, expectation_suite):
    """データ品質検証"""
    ge_df = SparkDFDataset(df)
    result = ge_df.validate(expectation_suite)

    if not result.success:
        raise ValueError(f"Validation failed: {result}")

    return df
```

### 監査とコンプライアンス

```sql
-- アクセス監査
SELECT
    user_identity.email,
    action_name,
    request_params.table_full_name,
    event_time
FROM system.access.audit
WHERE event_time >= current_date() - INTERVAL 30 DAYS
    AND action_name IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE')
ORDER BY event_time DESC;

-- データ系統追跡
SELECT
    table_full_name,
    table_owner,
    created_at,
    last_altered
FROM system.information_schema.tables
WHERE table_catalog = 'lakehouse';
```

## 実装パターン

### パターン1: バッチETL

```python
# 日次バッチ処理
from datetime import datetime

def daily_etl_pipeline(date: str):
    """日次データ処理パイプライン"""

    # Bronze: データ取込
    bronze_df = spark.read \
        .format("parquet") \
        .load(f"/mnt/raw/sales/{date}/") \
        .withColumn("ingestion_date", lit(date))

    bronze_df.write.format("delta") \
        .mode("append") \
        .partitionBy("ingestion_date") \
        .save("/delta/bronze/sales")

    # Silver: クレンジング
    silver_df = spark.read.format("delta") \
        .load("/delta/bronze/sales") \
        .filter(col("ingestion_date") == date) \
        .dropDuplicates(["order_id"]) \
        .filter(col("amount") > 0)

    silver_df.write.format("delta") \
        .mode("append") \
        .partitionBy("order_date") \
        .save("/delta/silver/sales")

    # Gold: 集計
    gold_df = spark.read.format("delta") \
        .load("/delta/silver/sales") \
        .filter(col("order_date") == date) \
        .groupBy("order_date", "region", "product_category") \
        .agg(
            sum("amount").alias("total_sales"),
            count("*").alias("order_count")
        )

    gold_df.write.format("delta") \
        .mode("overwrite") \
        .option("replaceWhere", f"order_date = '{date}'") \
        .save("/delta/gold/sales_daily")

# 実行
daily_etl_pipeline("2025-01-15")
```

### パターン2: ストリーミングETL

```python
# リアルタイムストリーミング
from pyspark.sql.functions import from_json, col

# スキーマ定義
event_schema = StructType([
    StructField("event_id", StringType()),
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", TimestampType())
])

# Bronze: ストリーム取込
bronze_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "events") \
    .load() \
    .select(from_json(col("value").cast("string"), event_schema).alias("data")) \
    .select("data.*")

bronze_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/bronze_events") \
    .start("/delta/bronze/events")

# Silver: リアルタイム変換
silver_stream = spark.readStream \
    .format("delta") \
    .load("/delta/bronze/events") \
    .filter(col("event_type").isin(["purchase", "view"])) \
    .dropDuplicates(["event_id"])

silver_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/silver_events") \
    .start("/delta/silver/events")
```

### パターン3: Lambda Architecture

```python
# バッチ層とスピード層の統合
def unified_view():
    """Lambda Architecture実装"""

    # バッチ層（履歴データ）
    batch_layer = spark.read.format("delta") \
        .load("/delta/gold/sales_daily") \
        .filter(col("date") < current_date())

    # スピード層（当日データ）
    speed_layer = spark.read.format("delta") \
        .load("/delta/silver/sales") \
        .filter(col("date") == current_date()) \
        .groupBy("date", "region") \
        .agg(sum("amount").alias("total_sales"))

    # 統合ビュー
    unified = batch_layer.union(speed_layer)

    return unified
```

## マイグレーション戦略

### 従来DWHからの移行

```python
# ステップ1: データ抽出
source_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://server:1433;database=db") \
    .option("dbtable", "sales") \
    .option("user", "username") \
    .option("password", "password") \
    .load()

# ステップ2: Delta Lake変換
source_df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .save("/delta/migrated/sales")

# ステップ3: 増分同期設定
from datetime import datetime, timedelta

last_sync = datetime.now() - timedelta(days=1)

incremental_df = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("query", f"SELECT * FROM sales WHERE updated_at > '{last_sync}'") \
    .load()

# Delta MERGEで更新
delta_table = DeltaTable.forPath(spark, "/delta/migrated/sales")
delta_table.alias("target").merge(
    incremental_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

## ベストプラクティス

1. **メダリオン採用** - データ品質段階的向上
   - 明確な責任分離
   - 再処理容易性
   - 複数消費者対応

2. **Delta Lake使用** - 全テーブルDelta形式
   - ACIDトランザクション
   - タイムトラベル
   - スキーマ進化

3. **Unity Catalog** - 統合ガバナンス
   - 一元的メタデータ管理
   - きめ細かいアクセス制御
   - データリネージ

4. **増分処理** - ストリーミング/CDC活用
   - コスト効率
   - リアルタイム性
   - リソース最適化

5. **自動化** - DLTパイプラインで宣言的定義
   - コード簡素化
   - 自動スケーリング
   - データ品質管理

6. **パーティショニング戦略**
   - 適切なパーティションキー選択
   - OPTIMIZE定期実行
   - Z-ORDER活用

7. **コスト最適化**
   - VACUUM定期実行
   - 不要データ削除
   - ストレージクラス最適化

## まとめ

Lakehouseは、データレイクの柔軟性・コスト効率とデータウェアハウスの信頼性・パフォーマンスを統合。メダリオンアーキテクチャ、Delta Lake、Unity Catalogで、モダンデータプラットフォームを実現。適切な設計と実装パターンで、スケーラブルで信頼性の高いデータ基盤を構築。
