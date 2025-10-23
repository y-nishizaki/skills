---
name: "Databricks PySpark/SQL習熟"
description: "DatabricksにおけるPySparkとSQLの効率的な使用方法。データ操作、関数、最適化、SQLとの統合、実践的なデータ処理パターン"
---

# Databricks PySpark/SQL習熟

## このスキルを使う場面

- PySparkでのデータ操作を学びたい
- Spark SQLの効率的な使い方を知りたい
- PySpark関数を使いこなしたい
- SQLとPySparkを組み合わせたい
- データ変換・集計のベストプラクティスを学びたい

## PySpark基礎

### DataFrameの作成

```python
# リストから作成
data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])

# 辞書から作成
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
df = spark.createDataFrame(data)

# Pandasから作成
import pandas as pd
pdf = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
df = spark.createDataFrame(pdf)

# ファイルから作成
df = spark.read.csv("/path/to/file.csv", header=True, inferSchema=True)
df = spark.read.parquet("/path/to/file.parquet")
df = spark.read.format("delta").load("/path/to/delta-table")
```

### 基本操作

```python
from pyspark.sql.functions import col, lit

# 列選択
df.select("name", "age").show()
df.select(col("name"), col("age") + 1).show()

# フィルタ
df.filter(col("age") > 25).show()
df.where((col("age") > 25) & (col("name") != "Bob")).show()

# 並び替え
df.orderBy("age").show()
df.orderBy(col("age").desc()).show()

# 制限
df.limit(10).show()

# 重複削除
df.distinct().show()
df.dropDuplicates(["name"]).show()
```

## 列操作

### 列の追加・変更

```python
from pyspark.sql.functions import col, when, lit, concat

# リテラル値
df = df.withColumn("country", lit("Japan"))

# 既存列から計算
df = df.withColumn("age_plus_10", col("age") + 10)

# 条件分岐
df = df.withColumn("age_group",
    when(col("age") < 30, "young")
    .when(col("age") < 40, "middle")
    .otherwise("senior")
)

# 文字列連結
df = df.withColumn("greeting", concat(lit("Hello, "), col("name")))
```

### 列の変換

```python
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql.functions import col, upper, lower, trim, substring

# 型変換
df = df.withColumn("age", col("age").cast(IntegerType()))
df = df.withColumn("age_str", col("age").cast(StringType()))

# 文字列操作
df = df.withColumn("name_upper", upper(col("name")))
df = df.withColumn("name_lower", lower(col("name")))
df = df.withColumn("name_trimmed", trim(col("name")))
df = df.withColumn("first_char", substring(col("name"), 1, 1))

# NULL処理
df = df.withColumn("age_filled", col("age").isNull().cast("int"))
df = df.fillna({"age": 0, "name": "Unknown"})
df = df.na.drop(subset=["age"])
```

## よく使う関数

### 集計関数

```python
from pyspark.sql.functions import count, sum, avg, max, min, stddev

# グループ集計
result = df.groupBy("age_group").agg(
    count("*").alias("count"),
    avg("age").alias("avg_age"),
    max("age").alias("max_age"),
    min("age").alias("min_age")
)

# 全体集計
from pyspark.sql.functions import sum as _sum
total = df.select(_sum("age").alias("total_age")).collect()[0]["total_age"]
```

### 日付・時刻関数

```python
from pyspark.sql.functions import (
    current_date, current_timestamp, to_date, date_format,
    year, month, dayofmonth, hour, minute, second,
    datediff, date_add, date_sub
)

# 現在日時
df = df.withColumn("today", current_date())
df = df.withColumn("now", current_timestamp())

# 日付変換
df = df.withColumn("date", to_date(col("date_string"), "yyyy-MM-dd"))
df = df.withColumn("formatted", date_format(col("timestamp"), "yyyy/MM/dd"))

# 日付要素抽出
df = df.withColumn("year", year(col("date")))
df = df.withColumn("month", month(col("date")))
df = df.withColumn("day", dayofmonth(col("date")))

# 日付演算
df = df.withColumn("days_diff", datediff(current_date(), col("date")))
df = df.withColumn("next_week", date_add(col("date"), 7))
```

### ウィンドウ関数

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank, lag, lead, sum as _sum

# ウィンドウ定義
window = Window.partitionBy("category").orderBy(col("amount").desc())

# ランキング
df = df.withColumn("row_num", row_number().over(window))
df = df.withColumn("rank", rank().over(window))
df = df.withColumn("dense_rank", dense_rank().over(window))

# 前後の値
df = df.withColumn("prev_amount", lag("amount", 1).over(window))
df = df.withColumn("next_amount", lead("amount", 1).over(window))

# 累積合計
window_cumsum = Window.partitionBy("category").orderBy("date").rowsBetween(Window.unboundedPreceding, Window.currentRow)
df = df.withColumn("cumulative_sum", _sum("amount").over(window_cumsum))
```

### 配列・マップ操作

```python
from pyspark.sql.functions import array, map_from_arrays, explode, size, array_contains

# 配列作成
df = df.withColumn("numbers", array(lit(1), lit(2), lit(3)))

# 配列展開
df_exploded = df.select("id", explode(col("array_col")).alias("item"))

# 配列サイズ
df = df.withColumn("array_size", size(col("array_col")))

# 配列検索
df = df.filter(array_contains(col("array_col"), "value"))
```

## SQL統合

### ビュー作成とSQL実行

```python
# 一時ビュー作成
df.createOrReplaceTempView("users")

# SQL実行
result = spark.sql("""
    SELECT
        name,
        age,
        CASE
            WHEN age < 30 THEN 'young'
            WHEN age < 40 THEN 'middle'
            ELSE 'senior'
        END as age_group
    FROM users
    WHERE age > 25
""")

# グローバル一時ビュー
df.createOrReplaceGlobalTempView("global_users")
spark.sql("SELECT * FROM global_temp.global_users").show()
```

### SQLとPySparkの組み合わせ

```python
# SQLで抽出、PySparkで加工
df_sql = spark.sql("SELECT * FROM users WHERE age > 25")
df_processed = df_sql.withColumn("age_doubled", col("age") * 2)

# PySparkで加工、SQLで集計
df.createOrReplaceTempView("temp_data")
result = spark.sql("""
    SELECT age_group, COUNT(*) as count
    FROM temp_data
    GROUP BY age_group
""")
```

## 結合操作

```python
# 内部結合
df_joined = df1.join(df2, on="id", how="inner")
df_joined = df1.join(df2, df1.id == df2.user_id, how="inner")

# 左外部結合
df_joined = df1.join(df2, on="id", how="left")

# 右外部結合
df_joined = df1.join(df2, on="id", how="right")

# 完全外部結合
df_joined = df1.join(df2, on="id", how="outer")

# 複数キーでの結合
df_joined = df1.join(df2, on=["id", "date"], how="inner")

# ブロードキャスト結合（小さいテーブル）
from pyspark.sql.functions import broadcast
df_joined = large_df.join(broadcast(small_df), on="id", how="inner")
```

## 最適化テクニック

### フィルタプッシュダウン

```python
# ✅ 早期フィルタ
df = spark.read.parquet("/path/to/data") \
    .filter(col("date") == "2025-01-01") \
    .select("id", "name", "amount")

# ❌ 遅延フィルタ
df = spark.read.parquet("/path/to/data") \
    .select("id", "name", "amount", "date") \
    .filter(col("date") == "2025-01-01")
```

### 列の選択

```python
# ✅ 必要な列のみ選択
df = spark.read.parquet("/path/to/data").select("id", "name", "age")

# ❌ 全列読み込み
df = spark.read.parquet("/path/to/data")
```

### キャッシング戦略

```python
# 複数回使用するDataFrameをキャッシュ
df_cached = df.filter(col("age") > 25).cache()
df_cached.count()  # キャッシュを実行

# 使用
result1 = df_cached.groupBy("city").count()
result2 = df_cached.groupBy("age_group").count()

# 解放
df_cached.unpersist()
```

## 実践的パターン

### ETL処理

```python
# 抽出 (Extract)
df_raw = spark.read.json("/path/to/raw-data/")

# 変換 (Transform)
df_cleaned = df_raw \
    .filter(col("status") == "active") \
    .withColumn("created_date", to_date(col("created_at"))) \
    .withColumn("amount", col("amount").cast("double")) \
    .select("id", "user_id", "amount", "created_date")

# 集計
df_aggregated = df_cleaned.groupBy("user_id", "created_date").agg(
    count("*").alias("transaction_count"),
    sum("amount").alias("total_amount")
)

# ロード (Load)
df_aggregated.write.format("delta").mode("overwrite").save("/path/to/output/")
```

### データ品質チェック

```python
# NULL確認
from pyspark.sql.functions import col, count, when, isnan

df_quality = df.select([
    count(when(col(c).isNull(), c)).alias(f"{c}_nulls")
    for c in df.columns
])

# 重複確認
duplicate_count = df.count() - df.dropDuplicates().count()

# 統計サマリ
df.describe().show()
df.summary("count", "mean", "stddev", "min", "max").show()
```

### デバッグ・確認

```python
# スキーマ確認
df.printSchema()

# データサンプル
df.show(10)
df.show(10, truncate=False)

# 件数確認
df.count()

# 特定条件のデータ確認
df.filter(col("age") > 100).show()

# 実行計画確認
df.explain()
df.explain(True)  # 詳細
```

## ベストプラクティス

### スキーマ定義

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# ✅ スキーマを明示的に定義
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

df = spark.read.schema(schema).csv("/path/to/data.csv")
```

### 列参照の明確化

```python
# ✅ col() を使用
from pyspark.sql.functions import col
df.filter(col("age") > 25)

# ❌ 文字列参照（一部の操作で制限あり）
df.filter("age > 25")
```

### エイリアスの活用

```python
# ✅ 結合時にエイリアス使用
df1.alias("t1").join(
    df2.alias("t2"),
    col("t1.id") == col("t2.user_id"),
    how="inner"
).select("t1.name", "t2.amount")
```

## まとめ

**効率的なPySpark/SQL使用の鍵:**

1. **適切なAPI選択** - 単純な操作はSQL、複雑な変換はPySpark
2. **早期フィルタ** - データ量を早めに削減
3. **列の最小化** - 必要な列のみ選択
4. **スキーマ定義** - 推論を避けてパフォーマンス向上
5. **ブロードキャスト** - 小さいテーブルとの結合を最適化

PySparkとSQLを適切に組み合わせることで、柔軟で高速なデータ処理が実現できる。
