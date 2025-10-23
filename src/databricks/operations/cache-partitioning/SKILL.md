---
name: "Databricksキャッシュ・パーティショニング戦略"
description: "キャッシングとパーティショニングの最適化戦略。Disk/Memory caching、パーティション設計、データスキッピング、Z-ORDER"
---

# Databricksキャッシュ・パーティショニング戦略

## キャッシング戦略

### Sparkキャッシング

```python
# メモリキャッシュ
df_cached = df.cache()
df_cached.count()  # キャッシュを実行

# 永続化レベル指定
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)

# キャッシュ解放
df_cached.unpersist()

# シリアライズ永続化（メモリ効率重視）
df.persist(StorageLevel.MEMORY_AND_DISK_SER)

# ディスクのみ（大容量データ向け）
df.persist(StorageLevel.DISK_ONLY)
```

**永続化レベルの選択基準**:

| レベル | メモリ使用量 | CPU負荷 | 用途 |
|--------|------------|---------|------|
| MEMORY_ONLY | 高 | 低 | 小〜中規模データ、高速処理 |
| MEMORY_AND_DISK | 高 | 低 | 大規模データ、複数回アクセス |
| MEMORY_AND_DISK_SER | 中 | 中 | メモリ節約重視 |
| DISK_ONLY | 低 | 低 | 超大規模データ |

```python
# キャッシュ効果の確認
from pyspark.sql.functions import *

# キャッシュなし
start = time.time()
df.filter(col("amount") > 1000).count()
print(f"キャッシュなし: {time.time() - start}秒")

# キャッシュあり
df_cached = df.cache()
df_cached.count()  # キャッシュ実行

start = time.time()
df_cached.filter(col("amount") > 1000).count()
print(f"キャッシュあり: {time.time() - start}秒")

# ストレージレベル確認
print(df_cached.storageLevel)
```

### Delta Caching (Disk Cache)

自動的に有効（SSD使用）
- ローカルSSDにParquetデータをキャッシュ
- メモリキャッシュより大容量
- クラスター再起動で消失

```python
# Delta Cachingは自動
# Photonクラスターで最適化

# キャッシュ状態確認
spark.conf.get("spark.databricks.io.cache.enabled")  # true

# Delta Cacheメトリクス
display(spark.sql("""
    SELECT
        cached_bytes,
        used_cached_bytes,
        cache_hit_ratio
    FROM delta.`/mnt/data/`.history()
"""))
```

**Delta Caching最適化**:

```python
# 頻繁アクセステーブルの手動キャッシュ
spark.sql("CACHE SELECT * FROM sales WHERE date >= '2025-01-01'")

# キャッシュクリア
spark.sql("CLEAR CACHE")

# 特定テーブルのキャッシュクリア
spark.sql("UNCACHE TABLE sales")
```

### キャッシング戦略の使い分け

```python
# シナリオ1: 機械学習の反復学習
# → MEMORY_AND_DISK（高速アクセス必須）
train_df = spark.read.parquet("/mnt/data/train")
train_cached = train_df.cache()
train_cached.count()

for epoch in range(10):
    model.fit(train_cached)

# シナリオ2: 大規模ETL中間テーブル
# → Delta Caching（自動、大容量）
df = spark.read.format("delta").load("/mnt/raw/")
transformed = df.transform(heavy_processing)
transformed.write.format("delta").save("/mnt/silver/")

# シナリオ3: 複数ジョブでの共有データ
# → Delta Lake + Delta Caching
# 自動的に複数クラスター間で効率化
```

## パーティショニング戦略

### 基本パーティショニング

```python
# 日付でパーティション
df.write.format("delta") \
    .partitionBy("date") \
    .save("/mnt/data/")

# 複数列
df.write.partitionBy("year", "month", "day").save("/mnt/data/")

# パーティション情報確認
spark.sql("DESCRIBE DETAIL delta.`/mnt/data/`").show()
```

### 最適なパーティション設計

```python
# ✅ 良いパーティション
# - カーディナリティ: 数十〜数千
# - サイズ: 1GB以上/パーティション
df.write.partitionBy("date", "region").save("/path")

# ❌ 悪いパーティション
# - カーディナリティ高すぎ (small file problem)
df.write.partitionBy("user_id").save("/path")

# ❌ カーディナリティ低すぎ (大きすぎるパーティション)
df.write.partitionBy("year").save("/path")
```

**パーティションサイズ分析**:

```python
# パーティションごとのサイズ確認
from pyspark.sql.functions import col, sum as _sum

partition_stats = spark.sql("""
    SELECT
        date,
        region,
        COUNT(*) as file_count,
        SUM(size) / 1024 / 1024 / 1024 as size_gb
    FROM delta.`/mnt/data/`.files()
    GROUP BY date, region
    ORDER BY size_gb DESC
""")
partition_stats.show()

# Small File Problem検出
small_files = partition_stats.filter(col("file_count") > 100)
print(f"Small file問題のパーティション数: {small_files.count()}")
```

### パーティション最適化テクニック

```python
# 1. リパーティション（書き込み前）
df.repartition(100, "date") \
    .write.format("delta") \
    .partitionBy("date") \
    .save("/mnt/optimized/")

# 2. Coalesce（パーティション数削減）
df.coalesce(10) \
    .write.format("delta") \
    .save("/mnt/optimized/")

# 3. Adaptive Query Execution（自動最適化）
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

### Z-ORDER クラスタリング

```sql
-- 複数列での高速フィルタ
OPTIMIZE my_table
ZORDER BY (customer_id, order_date);

-- 効果
SELECT * FROM my_table
WHERE customer_id = 12345
    AND order_date BETWEEN '2025-01-01' AND '2025-01-31';
-- データスキッピングで不要なファイルをスキップ

-- Z-ORDER前後のパフォーマンス比較
-- ファイルスキャン: 10,000 → 50ファイル（99.5%削減）
```

**Z-ORDER詳細戦略**:

```python
# Z-ORDER列選択ガイドライン
# 1. WHERE句で頻繁に使用される列
# 2. 高カーディナリティ列（user_id、order_id等）
# 3. 範囲検索される列（date、amount等）

# 最適なZ-ORDER設定
spark.sql("""
    OPTIMIZE events
    ZORDER BY (user_id, event_timestamp, event_type)
""")

# Z-ORDER効果測定
pre_stats = spark.sql("DESCRIBE HISTORY events").first()

# Z-ORDER実行
spark.sql("OPTIMIZE events ZORDER BY (user_id, event_timestamp)")

post_stats = spark.sql("DESCRIBE HISTORY events").first()

print(f"ファイル数: {pre_stats['numFiles']} → {post_stats['numFiles']}")
```

### 動的パーティショニング

```python
# Hiveスタイル動的パーティショニング
df.write.format("delta") \
    .mode("append") \
    .partitionBy("year", "month") \
    .option("partitionOverwriteMode", "dynamic") \
    .save("/mnt/data/")

# 特定パーティションのみ上書き
df.filter(col("date") == "2025-01-15") \
    .write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "date = '2025-01-15'") \
    .save("/mnt/data/")
```

## データスキッピング最適化

Delta Lakeは最初の32列の統計を自動収集:
- min, max, null_count

```python
# 統計を活用したクエリ
df = spark.read.format("delta").load("/mnt/data/") \
    .filter(col("amount") > 1000)  # min/max統計でファイルスキップ
```

**データスキッピング詳細**:

```sql
-- テーブル統計確認
DESCRIBE DETAIL delta.`/mnt/data/`;

-- ファイルレベル統計
SELECT
    path,
    min(amount) as min_amount,
    max(amount) as max_amount,
    null_count(amount) as null_count
FROM delta.`/mnt/data/`.files();

-- データスキッピング効果測定
EXPLAIN FORMATTED
SELECT * FROM sales
WHERE amount > 10000 AND date = '2025-01-15';
-- 出力: "PartitionFilters", "PushedFilters"確認
```

### 統計収集の最適化

```python
# Delta Lake統計更新
spark.sql("ANALYZE TABLE sales COMPUTE STATISTICS")

# 列統計収集
spark.sql("ANALYZE TABLE sales COMPUTE STATISTICS FOR COLUMNS amount, date")

# 統計確認
stats = spark.sql("DESCRIBE EXTENDED sales").collect()
for row in stats:
    if "Statistics" in str(row):
        print(row)
```

## Small File Problem解決

```python
# Small Fileの検出
files_df = spark.sql("""
    SELECT
        COUNT(*) as total_files,
        AVG(size) / 1024 / 1024 as avg_size_mb,
        MIN(size) / 1024 / 1024 as min_size_mb,
        MAX(size) / 1024 / 1024 as max_size_mb
    FROM delta.`/mnt/data/`.files()
""")
files_df.show()

# OPTIMIZE実行（自動ファイル結合）
spark.sql("OPTIMIZE my_table")

# 自動OPTIMIZE設定
spark.conf.set("spark.databricks.delta.autoOptimize.optimizeWrite", "true")
spark.conf.set("spark.databricks.delta.autoOptimize.autoCompact", "true")
```

## 実践的な最適化パターン

### パターン1: 日次バッチ処理

```python
# 効率的な日次パーティション更新
from datetime import datetime, timedelta

date = datetime.now().strftime("%Y-%m-%d")

# 1. その日のデータのみ処理
daily_df = spark.read.parquet(f"/mnt/raw/{date}/")

# 2. キャッシュ（複数変換で再利用）
daily_cached = daily_df.cache()

# 3. 変換処理
transformed = daily_cached.transform(business_logic)

# 4. 最適化された書き込み
transformed.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", f"date = '{date}'") \
    .option("dataChange", "false") \
    .partitionBy("date") \
    .save("/mnt/silver/")

# 5. OPTIMIZE実行
spark.sql(f"""
    OPTIMIZE delta.`/mnt/silver/`
    WHERE date = '{date}'
    ZORDER BY (user_id, event_time)
""")
```

### パターン2: 大規模テーブルのスキャン最適化

```python
# パーティションプルーニング活用
# ✅ 効率的
result = spark.sql("""
    SELECT * FROM large_table
    WHERE date BETWEEN '2025-01-01' AND '2025-01-31'
        AND region = 'us-west'
""")
# → パーティション絞り込み発生

# ❌ 非効率
result = spark.sql("""
    SELECT * FROM large_table
    WHERE month(date) = 1 AND year(date) = 2025
""")
# → 全パーティションスキャン

# ブロードキャストジョイン活用
from pyspark.sql.functions import broadcast

# ディメンションテーブルをブロードキャスト
result = large_fact.join(
    broadcast(small_dim),
    "dim_id"
)
```

## ベストプラクティス

1. **頻繁アクセスデータをキャッシュ**
   - ML学習データ: `MEMORY_AND_DISK`
   - 中間集計結果: Delta Caching活用

2. **パーティション: 1GB以上/パーティション**
   - 分析: カーディナリティ測定
   - 調整: リパーティション、OPTIMIZE

3. **Z-ORDER: 高カーディナリティ列**
   - WHERE句頻出列を優先
   - 2-4列が最適（それ以上は効果減少）

4. **定期的なOPTIMIZE実行**
   - 日次: 新規パーティション
   - 週次: 全テーブル

5. **自動最適化機能活用**
   - Auto Optimize: 書き込み時に自動最適化
   - Adaptive Query Execution: 実行時最適化

## アンチパターンと解決策

### アンチパターン1: 過度なキャッシュ

```python
# ❌ 悪い例
df1 = spark.read.parquet("/data1").cache()
df2 = spark.read.parquet("/data2").cache()
df3 = spark.read.parquet("/data3").cache()
df4 = spark.read.parquet("/data4").cache()
# → メモリ枯渇、GC頻発

# ✅ 良い例
df1 = spark.read.parquet("/data1")
df2 = spark.read.parquet("/data2")
result = df1.join(df2, "key").cache()  # 結果のみキャッシュ
```

### アンチパターン2: 不適切なパーティションキー

```python
# ❌ 悪い例: タイムスタンプでパーティション
df.write.partitionBy("timestamp").save("/path")
# → 数百万パーティション生成

# ✅ 良い例: 日付に変換
from pyspark.sql.functions import to_date
df.withColumn("date", to_date("timestamp")) \
    .write.partitionBy("date").save("/path")
```

## トラブルシューティング

### 問題: キャッシュが効いていない

```python
# 診断
print(df.is_cached)  # False

# 原因1: アクションを実行していない
df.cache()  # これだけでは不十分
df.count()  # アクション実行でキャッシュ実行

# 原因2: メモリ不足
# → StorageLevelを変更
df.persist(StorageLevel.MEMORY_AND_DISK)
```

### 問題: パーティション読み込みが遅い

```python
# 診断
spark.sql("""
    SELECT COUNT(*) FROM delta.`/path/`.files()
""").show()
# → 大量の小ファイル検出

# 解決
spark.sql("OPTIMIZE delta.`/path/`")
```

## まとめ

適切なキャッシング戦略とパーティション設計で、クエリパフォーマンスを大幅に向上。Z-ORDERとデータスキッピングで、I/Oを最小化。定期的な最適化とモニタリングで、長期的なパフォーマンスを維持。
