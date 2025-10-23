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
```

### Delta Caching (Disk Cache)

自動的に有効（SSD使用）
- ローカルSSDにParquetデータをキャッシュ
- メモリキャッシュより大容量
- クラスター再起動で消失

```python
# Delta Cachingは自動
# Photonクラスターで最適化
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
```

## データスキッピング最適化

Delta Lakeは最初の32列の統計を自動収集:
- min, max, null_count

```python
# 統計を活用したクエリ
df = spark.read.format("delta").load("/mnt/data/") \
    .filter(col("amount") > 1000)  # min/max統計でファイルスキップ
```

## ベストプラクティス

1. **頻繁アクセスデータをキャッシュ**
2. **パーティション: 1GB以上/パーティション**
3. **Z-ORDER: 高カーディナリティ列**
4. **定期的なOPTIMIZE実行**

## まとめ

適切なキャッシング戦略とパーティション設計で、クエリパフォーマンスを大幅に向上。Z-ORDERとデータスキッピングで、I/Oを最小化。
