---
name: "Databricksデータ品質管理"
description: "データ品質管理の実践。Expectations、データ検証、異常検知、品質メトリクス、モニタリング、自動アラート"
---

# Databricksデータ品質管理

## このスキルを使う場面

- データ品質を保証したい
- データ検証ルールを実装したい
- 異常データを検知・除外したい
- 品質メトリクスを追跡したい
- データ品質レポートを自動化したい

## Delta Live Tables Expectations

### 基本的なExpectations

```python
import dlt
from pyspark.sql.functions import col

# 警告のみ (データは保持)
@dlt.expect("valid_email", "email LIKE '%@%.%'")

# 違反行を削除
@dlt.expect_or_drop("positive_amount", "amount > 0")

# 違反時にパイプライン停止
@dlt.expect_or_fail("required_id", "id IS NOT NULL")

# 例
@dlt.table
@dlt.expect("valid_date", "event_date >= '2020-01-01'")
@dlt.expect_or_drop("valid_status", "status IN ('active', 'pending', 'completed')")
@dlt.expect_or_fail("not_null_id", "user_id IS NOT NULL")
def validated_events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/mnt/raw-data/")
```

### 複雑な品質ルール

```python
# 複数条件
@dlt.expect("business_rule", """
    (status = 'completed' AND amount > 0) OR
    (status = 'pending' AND amount IS NULL)
""")

# カスタム関数を使用
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType

@udf(returnType=BooleanType())
def is_valid_credit_card(number):
    # Luhnアルゴリズムなど
    return len(number) == 16 and number.isdigit()

@dlt.table
def validated_payments():
    df = dlt.read_stream("raw_payments")
    return df.where(is_valid_credit_card(col("card_number")))
```

## 従来のDataFrameでの検証

```python
from pyspark.sql.functions import col, count, when

# NULL値チェック
null_counts = df.select([
    count(when(col(c).isNull(), c)).alias(f"{c}_nulls")
    for c in df.columns
])

# 重複チェック
duplicate_count = df.count() - df.dropDuplicates(["id"]).count()

# 値範囲チェック
invalid_age = df.filter((col("age") < 0) | (col("age") > 150)).count()

# カスタムルール
invalid_email = df.filter(~col("email").rlike(r"[^@]+@[^@]+\.[^@]+")).count()
```

## 品質メトリクスの追跡

```python
from pyspark.sql.functions import current_timestamp, lit

# 品質メトリクスをテーブルに記録
quality_metrics = spark.createDataFrame([{
    "table_name": "orders",
    "metric_name": "null_customer_id",
    "metric_value": null_count,
    "check_timestamp": current_timestamp()
}])

quality_metrics.write.format("delta") \
    .mode("append") \
    .save("/mnt/quality-metrics/")
```

## Great Expectations統合

```python
import great_expectations as gx

# コンテキスト作成
context = gx.get_context()

# データソース設定
datasource = context.data_sources.add_spark("spark_datasource")

# データアセット
data_asset = datasource.add_dataframe_asset(name="orders_df")

# Expectation Suite
suite = context.suites.add(gx.ExpectationSuite(name="orders_suite"))

# Expectations追加
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="status",
        value_set=["pending", "completed", "cancelled"]
    )
)

# 検証実行
batch = data_asset.add_batch_definition_whole_dataframe("orders_batch")
results = batch.run_validation(suite)
```

## 異常検知

```python
from pyspark.sql.functions import stddev, avg, abs

# 統計的異常検知 (Z-score)
stats = df.select(
    avg("amount").alias("mean"),
    stddev("amount").alias("stddev")
).collect()[0]

df_with_zscore = df.withColumn(
    "z_score",
    abs((col("amount") - lit(stats["mean"])) / lit(stats["stddev"]))
)

# 異常値フラグ
df_flagged = df_with_zscore.withColumn(
    "is_outlier",
    when(col("z_score") > 3, True).otherwise(False)
)

# 異常値を別テーブルに保存
outliers = df_flagged.filter(col("is_outlier") == True)
outliers.write.format("delta").mode("append").save("/mnt/outliers/")
```

## データプロファイリング

```python
# 基本統計
df.describe().show()

# 詳細統計
df.summary("count", "mean", "stddev", "min", "25%", "50%", "75%", "max").show()

# カラムごとの一意値数
from pyspark.sql.functions import approx_count_distinct

df.select([
    approx_count_distinct(c).alias(f"{c}_distinct")
    for c in df.columns
]).show()

# データ分布
df.groupBy("category").count().orderBy(col("count").desc()).show()
```

## 品質レポート自動化

```python
def generate_quality_report(table_name, df):
    report = {
        "table": table_name,
        "timestamp": str(current_timestamp()),
        "row_count": df.count(),
        "column_count": len(df.columns),
        "null_counts": {},
        "duplicate_count": df.count() - df.dropDuplicates().count()
    }
    
    # NULL値カウント
    for col_name in df.columns:
        null_count = df.filter(col(col_name).isNull()).count()
        report["null_counts"][col_name] = null_count
    
    # レポート保存
    report_df = spark.createDataFrame([report])
    report_df.write.format("delta").mode("append") \
        .save("/mnt/quality-reports/")
    
    return report

# 実行
report = generate_quality_report("orders", orders_df)
```

## アラート設定

```python
# 品質閾値チェック
if null_count > 1000:
    # Slack/Email通知
    import requests
    
    webhook_url = dbutils.secrets.get("alerts", "slack_webhook")
    message = {
        "text": f"Data Quality Alert: {null_count} null values in orders table"
    }
    requests.post(webhook_url, json=message)
```

## ベストプラクティス

1. **段階的な品質チェック** - Bronze→Silver→Goldで厳格化
2. **メトリクス追跡** - 品質トレンドを可視化
3. **自動アラート** - 閾値超過時に通知
4. **異常値の保存** - 調査用に別テーブルに保存
5. **ドキュメント化** - 品質ルールの理由を記録

## まとめ

Delta Live Tables Expectationsと品質メトリクス追跡により、信頼性の高いデータパイプラインを構築できる。異常検知とアラートで、問題を早期に発見・対処可能。
