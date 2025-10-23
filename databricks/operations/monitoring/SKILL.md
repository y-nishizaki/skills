---
name: "Databricks監視・トラブルシューティング"
description: "クラスター監視、ジョブ監視、パフォーマンス分析、エラー調査、Spark UI活用、ログ分析"
---

# Databricks監視・トラブルシューティング

## Spark UI活用

### Jobs/Stages/Tasks

- **Jobs**: アクション(show, write)ごと
- **Stages**: シャッフル境界で分割
- **Tasks**: パーティションごとの実行単位

```python
# UIアクセス: クラスター -> Spark UI

# 確認ポイント:
# 1. Duration - 実行時間
# 2. Shuffle Read/Write - データ移動量
# 3. GC Time - ガベージコレクション時間
# 4. Spill (Memory) - メモリ不足
```

### SQL Tab

```sql
-- クエリ実行計画確認
EXPLAIN FORMATTED
SELECT * FROM large_table WHERE amount > 1000;

-- 物理プランでスキャン量確認
```

## システムテーブル監視

```sql
-- ジョブ実行履歴
SELECT
    job_id,
    run_id,
    start_time,
    end_time,
    state,
    result_state
FROM system.lakeflow.job_run_timeline
WHERE start_time >= current_date() - INTERVAL 7 DAYS
ORDER BY start_time DESC;

-- 失敗ジョブ調査
SELECT * FROM system.lakeflow.job_run_timeline
WHERE result_state = 'FAILED';
```

## パフォーマンス問題の診断

### OOMエラー

```python
# メモリ不足の兆候:
# - Spark UI で "Spill (Memory)" が大きい
# - GC Time が長い

# 解決策:
# 1. パーティション数を増やす
df.repartition(200).write.parquet("/output")

# 2. 永続化レベルを変更
df.persist(StorageLevel.MEMORY_AND_DISK_SER)

# 3. より大きいノードタイプ
```

### データスキュー

```python
# スキューの確認
df.groupBy("key").count().orderBy(col("count").desc()).show()

# 解決策: ソルト追加
from pyspark.sql.functions import rand
df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
df_salted.repartition("key", "salt")
```

### シャッフル最適化

```python
# AQE有効化 (自動最適化)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# ブロードキャスト結合
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")
```

## ログ分析

```python
# ドライバーログ
dbutils.fs.ls("dbfs:/cluster-logs/<cluster-id>/driver/")

# エラーログ検索
logs = spark.read.text("dbfs:/cluster-logs/<cluster-id>/driver/stderr")
logs.filter(col("value").contains("ERROR")).show(truncate=False)
```

## まとめ

Spark UIとシステムテーブルでプロアクティブに監視。OOM、スキュー、シャッフル問題を早期発見し、適切に対処することで、安定したパイプラインを維持。
