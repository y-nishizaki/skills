---
name: "Databricks Apache Spark基礎"
description: "DatabricksにおけるApache Sparkの基礎理解。RDD、DataFrame、Dataset API、Spark SQL、遅延評価、カタリストオプティマイザの理解と実践的な使用方法"
---

# Databricks Apache Spark基礎

## このスキルを使う場面

- Sparkの基本概念を理解したい
- RDD、DataFrame、Dataset APIの使い分けを知りたい
- Spark SQLの効率的な使い方を学びたい
- カタリストオプティマイザの仕組みを理解したい
- パフォーマンスチューニングの基礎を学びたい

## Apache Sparkとは

Apache Sparkは、大規模データ処理のための統合分析エンジン。Databricksの中核技術。

**主な特徴:**
- インメモリ処理による高速性
- 統一されたAPI（バッチ、ストリーミング、ML、SQL）
- スケーラビリティ（単一ノード〜数千ノード）
- 多言語サポート（Python、Scala、SQL、R、Java）

## Sparkの3つのAPI

### 1. RDD (Resilient Distributed Dataset)

低レベルAPI。最も柔軟だが、最適化は手動。

**基本操作:**

```python
# RDD作成
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# 変換（Transformation）
rdd_squared = rdd.map(lambda x: x * x)
rdd_filtered = rdd.filter(lambda x: x > 2)

# アクション（Action）
result = rdd_squared.collect()
count = rdd.count()
```

**使用場面:**
- 非構造化データ（テキストストリーム、メディアなど）
- 低レベル制御が必要
- 関数型プログラミング的な操作

**2025年の重要な制限:**
Unity Catalog有効な共有クラスターではRDDは使用不可。シングルユーザークラスターを使用するか、DataFrame APIに移行すること。

### 2. DataFrame API

構造化データ向けの高レベルAPI。推奨される標準。

**基本操作:**

```python
# DataFrame作成
data = [(1, "Alice", 30), (2, "Bob", 25), (3, "Charlie", 35)]
df = spark.createDataFrame(data, ["id", "name", "age"])

# 選択
df.select("name", "age").show()

# フィルタ
df.filter(df.age > 25).show()

# 集計
df.groupBy("age").count().show()

# 結合
df2 = spark.createDataFrame([(1, "Tokyo"), (2, "Osaka")], ["id", "city"])
df.join(df2, on="id", how="inner").show()
```

**列の操作:**

```python
from pyspark.sql.functions import col, when, lit

# 列の追加・変更
df = df.withColumn("age_group",
    when(col("age") < 30, "young")
    .when(col("age") < 40, "middle")
    .otherwise("senior")
)

# 列名変更
df = df.withColumnRenamed("age", "user_age")

# 列の削除
df = df.drop("age_group")
```

**メリット:**
- カタリストオプティマイザによる自動最適化
- スキーマ推論とエンフォースメント
- SQL的な操作
- 全言語で同等のパフォーマンス

### 3. Spark SQL

SQLインターフェース。DataFrameと完全互換。

```python
# DataFrameをビューとして登録
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
    ORDER BY age DESC
""")
result.show()

# DataFrameとSQLの混在
df2 = spark.sql("SELECT * FROM users WHERE age > 25")
df2.filter(col("age") < 40).show()
```

## 遅延評価 (Lazy Evaluation)

Sparkは変換を即座に実行せず、アクションが呼ばれた時に実行計画を最適化して実行。

**変換（Transformation）:** 遅延評価
```python
df_filtered = df.filter(col("age") > 25)  # 実行されない
df_selected = df_filtered.select("name")   # 実行されない
```

**アクション（Action）:** 即座に実行
```python
result = df_selected.collect()  # ここで実行される
df_selected.show()              # ここで実行される
df_selected.count()             # ここで実行される
```

**主な変換:**
- `select()`, `filter()`, `where()`, `groupBy()`, `join()`
- `withColumn()`, `drop()`, `distinct()`, `orderBy()`

**主なアクション:**
- `show()`, `collect()`, `count()`, `take()`, `first()`
- `write.save()`, `write.parquet()`, `write.delta()`

## カタリストオプティマイザ

Sparkの実行計画を自動最適化するエンジン。

**最適化プロセス:**

1. **論理プランの生成** - クエリを論理的な操作に変換
2. **論理プランの最適化** - 述語プッシュダウン、列の削除など
3. **物理プランの生成** - 複数の実行戦略を生成
4. **コストベース最適化** - 統計情報を使って最適な戦略を選択
5. **コード生成** - JVMバイトコードを生成

**実行計画の確認:**

```python
# 論理プラン
df.explain(True)

# 物理プランのみ
df.explain()

# コストベース最適化の詳細
df.explain("cost")
```

**例: 自動的な述語プッシュダウン**

```python
# このコードは...
df = spark.read.parquet("/path/to/data")
df_filtered = df.filter(col("age") > 30)
df_selected = df_filtered.select("name", "age")

# カタリストにより以下のように最適化される:
# 1. フィルタがParquetファイルの読み込み時に適用される
# 2. 必要な列（name, age）のみが読み込まれる
# 3. 不要なデータをスキップ
```

## パフォーマンス最適化

### 1. 適応的クエリ実行 (AQE)

実行時に統計情報を使ってクエリプランを再最適化（Spark 3.0以降）。

```python
# AQE有効化（Databricksではデフォルトで有効）
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

### 2. ブロードキャスト結合

小さいテーブルを全ノードに配布して結合を高速化。

```python
from pyspark.sql.functions import broadcast

# 明示的なブロードキャスト
large_df.join(broadcast(small_df), on="key", how="inner")

# 自動ブロードキャスト閾値（デフォルト: 10MB）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10485760)
```

### 3. キャッシング

頻繁にアクセスするデータをメモリに保持。

```python
# キャッシュ
df_cached = df.cache()
df_cached.count()  # キャッシュを実行

# 永続化レベルを指定
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)

# キャッシュ解放
df_cached.unpersist()
```

### 4. パーティショニング

```python
# 読み込み時のパーティション数を調整
df = spark.read.option("spark.sql.files.maxPartitionBytes", 134217728).parquet("/path")

# 再パーティション
df_repartitioned = df.repartition(100)
df_repartitioned = df.repartition("date", "country")

# パーティション削減（シャッフルなし）
df_coalesced = df.coalesce(10)
```

## ベストプラクティス

### DataFrame APIを使用する

```python
# ❌ RDD（避ける）
rdd = spark.sparkContext.textFile("/path/to/data")
result = rdd.map(lambda x: x.split(",")) \
    .filter(lambda x: int(x[2]) > 30) \
    .collect()

# ✅ DataFrame（推奨）
df = spark.read.csv("/path/to/data", header=True, inferSchema=True)
result = df.filter(col("age") > 30).collect()
```

### 明示的なスキーマ定義

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# ✅ スキーマを定義
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

df = spark.read.schema(schema).json("/path/to/data.json")
```

### 述語を早期に適用

```python
# ✅ フィルタを早期に適用
df = spark.read.parquet("/path/to/data") \
    .filter(col("date") == "2025-01-01") \
    .select("id", "name", "amount")

# ❌ 全データを読んでからフィルタ
df = spark.read.parquet("/path/to/data")
df = df.select("id", "name", "amount", "date")
df = df.filter(col("date") == "2025-01-01")
```

### アクションの最小化

```python
# ❌ 複数のアクション
df.count()  # アクション1
df.show()   # アクション2
df.write.parquet("/output")  # アクション3

# ✅ キャッシュして複数アクション
df.cache()
df.count()
df.show()
df.write.parquet("/output")
df.unpersist()
```

## トラブルシューティング

### OOM (Out of Memory)

```python
# パーティション数を増やす
df.repartition(200).write.parquet("/output")

# ブロードキャスト閾値を下げる
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

# 永続化レベルを変更
df.persist(StorageLevel.MEMORY_AND_DISK_SER)
```

### データスキュー

```python
# スキューキーを特定
df.groupBy("key").count().orderBy(col("count").desc()).show()

# ソルトを追加してスキューを軽減
from pyspark.sql.functions import rand
df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
df_salted = df_salted.repartition("key", "salt")
```

### スパークUIの活用

```python
# Databricksでは自動的に利用可能
# クラスター -> Spark UI -> Jobs/Stages/Storage

# 確認ポイント:
# - タスクの実行時間
# - データのシャッフル量
# - GC時間
# - メモリ使用量
```

## まとめ

**2025年の推奨アプローチ:**

1. **DataFrame APIを優先** - RDDは特別な理由がない限り使わない
2. **Spark SQLを活用** - SQLとDataFrameを組み合わせて柔軟に
3. **カタリストに任せる** - 明示的な最適化は必要最小限に
4. **AQEを信頼** - 実行時最適化が自動的に適用される
5. **Unity Catalogを使用** - 共有クラスターとガバナンスのために

Sparkの基本を理解することで、Databricks上での効率的なデータ処理が可能になる。
