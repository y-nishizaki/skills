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
# 5. Task Skew - タスク間の実行時間差
```

### Spark UI詳細分析

**Jobs Tab**:
```python
# ジョブレベル分析
# - DAG Visualization: ステージ間の依存関係確認
# - Event Timeline: 並列実行状況の可視化
# - 実行時間の大部分を占めるステージ特定

# アクセス: Spark UI -> Jobs -> 特定のJob ID
```

**Stages Tab**:
```python
# ステージレベル分析
# - Input/Output Size: データ量確認
# - Shuffle Read/Write: シャッフル量測定
# - Task Distribution: タスク実行時間の分布

# 問題のあるステージの特徴:
# - Shuffle Write >> Shuffle Read: 不必要な広いシャッフル
# - 高いGC Time: メモリ不足
# - Task Skew: データ分散の偏り
```

**Storage Tab**:
```python
# キャッシュ状況確認
# - Cached Partitions: キャッシュされたパーティション数
# - Fraction Cached: キャッシュ率
# - Size in Memory: メモリ使用量

# キャッシュされているRDD/DataFrame確認
```

**Environment Tab**:
```python
# 設定確認
# - Spark Properties: spark.conf設定値
# - System Properties: JVM設定
# - Classpath Entries: 依存ライブラリ

# パフォーマンスチューニング時に確認
```

### SQL Tab

```sql
-- クエリ実行計画確認
EXPLAIN FORMATTED
SELECT * FROM large_table WHERE amount > 1000;

-- 物理プランでスキャン量確認

-- コスト分析
EXPLAIN COST
SELECT t1.*, t2.name
FROM large_table t1
JOIN dim_table t2 ON t1.id = t2.id
WHERE t1.date = '2025-01-15';
```

**SQL Metricsの読み方**:
```sql
-- 実行計画のメトリクス
-- - numOutputRows: 出力行数
-- - dataSize: データサイズ
-- - filesRead: 読み込みファイル数
-- - pruned: スキップされたファイル/パーティション

-- 非効率なクエリの兆候:
-- - filesRead多数、pruned少ない → パーティショニング不適切
-- - Broadcast Hash Join → Shuffle Hash Join: ブロードキャスト閾値調整必要
```

### Executorメトリクス監視

```python
# Executors Tab分析
# 各Executorのリソース使用状況

# 確認項目:
# 1. Task Time: 各Executorのタスク実行時間
# 2. GC Time: GC時間（10%超えると問題）
# 3. Shuffle Read/Write: データ転送量
# 4. Storage Memory: キャッシュ使用量

# 不均衡の検出
# - 特定Executorのみ高負荷 → データスキュー
# - 全Executorで高GC Time → メモリ不足
```

## システムテーブル監視

### ジョブ実行履歴

```sql
-- ジョブ実行履歴
SELECT
    job_id,
    run_id,
    start_time,
    end_time,
    state,
    result_state,
    DATEDIFF(minute, start_time, end_time) as duration_minutes
FROM system.lakeflow.job_run_timeline
WHERE start_time >= current_date() - INTERVAL 7 DAYS
ORDER BY start_time DESC;

-- 失敗ジョブ調査
SELECT * FROM system.lakeflow.job_run_timeline
WHERE result_state = 'FAILED'
ORDER BY start_time DESC;

-- ジョブ成功率分析
SELECT
    job_id,
    COUNT(*) as total_runs,
    SUM(CASE WHEN result_state = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
    ROUND(SUM(CASE WHEN result_state = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate,
    AVG(DATEDIFF(minute, start_time, end_time)) as avg_duration_minutes
FROM system.lakeflow.job_run_timeline
WHERE start_time >= current_date() - INTERVAL 30 DAYS
GROUP BY job_id
HAVING success_rate < 95  -- 成功率95%未満
ORDER BY total_runs DESC;
```

### クラスター使用状況

```sql
-- クラスター使用状況
SELECT
    cluster_id,
    usage_metadata.cluster_name,
    usage_start_time,
    usage_end_time,
    DATEDIFF(hour, usage_start_time, usage_end_time) as usage_hours,
    sku_name,
    usage_quantity
FROM system.billing.usage
WHERE usage_start_time >= current_date() - INTERVAL 7 DAYS
    AND usage_metadata.cluster_name IS NOT NULL
ORDER BY usage_hours DESC;

-- DBU消費分析
SELECT
    DATE_TRUNC('day', usage_start_time) as date,
    usage_metadata.cluster_name,
    SUM(usage_quantity) as total_dbus,
    SUM(usage_quantity * list_prices.pricing.default) as estimated_cost
FROM system.billing.usage
LEFT JOIN system.billing.list_prices ON usage.sku_name = list_prices.sku_name
WHERE usage_start_time >= current_date() - INTERVAL 30 DAYS
GROUP BY date, usage_metadata.cluster_name
ORDER BY date DESC, total_dbus DESC;
```

### クエリ履歴分析

```sql
-- 遅いクエリトップ20
SELECT
    query_id,
    statement_text,
    user_name,
    warehouse_id,
    start_time,
    end_time,
    total_duration_ms / 1000 as duration_seconds,
    rows_produced,
    executed_as_user_name
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 1 DAYS
    AND total_duration_ms > 30000  -- 30秒以上
ORDER BY total_duration_ms DESC
LIMIT 20;

-- ユーザー別クエリ統計
SELECT
    user_name,
    COUNT(*) as query_count,
    AVG(total_duration_ms) / 1000 as avg_duration_sec,
    SUM(total_duration_ms) / 1000 / 60 as total_compute_minutes,
    SUM(read_bytes) / 1024 / 1024 / 1024 as total_gb_read
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY user_name
ORDER BY total_compute_minutes DESC;
```

## パフォーマンス問題の診断

### OOMエラー

```python
# メモリ不足の兆候:
# - Spark UI で "Spill (Memory)" が大きい
# - GC Time が長い（Total Time の10%以上）
# - TaskのFailed Reason: "OutOfMemoryError"

# 解決策:
# 1. パーティション数を増やす
df.repartition(200).write.parquet("/output")

# 2. 永続化レベルを変更
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK_SER)

# 3. より大きいノードタイプ
# Standard_DS13_v2 (56GB) → Standard_DS14_v2 (112GB)

# 4. Executor メモリ増加
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.executor.memoryOverhead", "4g")

# 5. ブロードキャスト閾値調整
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")  # 無効化
```

**OOM診断フロー**:
```python
# ステップ1: Executorログ確認
# "java.lang.OutOfMemoryError: Java heap space"

# ステップ2: Spark UI確認
# - Storage Tab: キャッシュ使用量
# - Executors Tab: Memory Used

# ステップ3: コード確認
# - collect()使用 → 大量データをDriverに転送
# - 不必要なキャッシュ
# - カルテシアン積（cross join）

# ステップ4: データサイズ確認
df = spark.read.format("delta").load("/path")
print(f"Total Size: {df.count()} rows")
print(f"Partition Count: {df.rdd.getNumPartitions()}")

# 推奨: 1パーティション = 128MB-1GB
target_partitions = total_size_gb * 1024 / 128  # 128MB/partition
```

### データスキュー

```python
# スキューの確認
df.groupBy("key").count().orderBy(col("count").desc()).show()

# 詳細分析
from pyspark.sql.functions import col, count, sum as _sum

skew_stats = df.groupBy("partition_key") \
    .agg(
        count("*").alias("row_count"),
        _sum("data_size").alias("total_size")
    ) \
    .orderBy(col("row_count").desc())

skew_stats.show()

# スキュー率計算
skew_ratio = skew_stats.first()["row_count"] / skew_stats.agg({"row_count": "avg"}).first()[0]
print(f"Skew Ratio: {skew_ratio:.2f}x")  # 3x以上は問題

# 解決策1: ソルト追加
from pyspark.sql.functions import rand
df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
df_salted.repartition("key", "salt")

# 解決策2: AQE Skew Join最適化
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# 解決策3: ブロードキャストジョイン（小さいテーブル側）
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

**スキュー検出の自動化**:
```python
def detect_skew(df, partition_col, threshold=3.0):
    """データスキューを検出"""
    stats = df.groupBy(partition_col).count()

    # 統計計算
    from pyspark.sql.functions import mean, stddev, max as _max
    summary = stats.agg(
        mean("count").alias("avg"),
        stddev("count").alias("stddev"),
        _max("count").alias("max")
    ).first()

    skew_ratio = summary["max"] / summary["avg"]

    if skew_ratio > threshold:
        print(f"⚠️ Skew detected: {skew_ratio:.2f}x")
        print(f"Avg: {summary['avg']:.0f}, Max: {summary['max']}")
        return True
    return False

# 使用例
if detect_skew(df, "customer_id"):
    # スキュー対策実施
    df = df.withColumn("salt", (rand() * 10).cast("int"))
```

### シャッフル最適化

```python
# AQE有効化 (自動最適化)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# シャッフルパーティション数調整
# デフォルト: 200（小規模）、推奨: データサイズに応じて
spark.conf.set("spark.sql.shuffle.partitions", "400")

# ブロードキャスト結合
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")

# ブロードキャスト閾値調整（デフォルト10MB）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50MB")
```

**シャッフル量削減テクニック**:
```python
# テクニック1: フィルタを早めに適用
# ❌ 悪い例
df1.join(df2, "key").filter(col("date") == "2025-01-01")

# ✅ 良い例
df1_filtered = df1.filter(col("date") == "2025-01-01")
df2_filtered = df2.filter(col("date") == "2025-01-01")
df1_filtered.join(df2_filtered, "key")

# テクニック2: 事前集計
# ❌ 悪い例
df.join(large_fact, "id").groupBy("category").sum("amount")

# ✅ 良い例
aggregated = large_fact.groupBy("id", "category").sum("amount")
df.join(aggregated, "id")

# テクニック3: パーティショニング活用
df1.write.partitionBy("date").save("/path1")
df2.write.partitionBy("date").save("/path2")

# 同じパーティションキーでjoin → シャッフル不要
spark.read.format("delta").load("/path1") \
    .join(spark.read.format("delta").load("/path2"), ["date", "key"])
```

### スロークエリ分析

```python
# クエリ実行計画の詳細分析
query = """
SELECT customer_id, SUM(amount)
FROM large_table
WHERE date >= '2025-01-01'
GROUP BY customer_id
"""

# 実行計画確認
explain_df = spark.sql(f"EXPLAIN EXTENDED {query}")
explain_df.show(truncate=False)

# パフォーマンス測定
import time

start = time.time()
result = spark.sql(query)
result.count()  # アクション実行
duration = time.time() - start

print(f"Duration: {duration:.2f}s")

# Spark UIでメトリクス確認
# - Input Size: 読み込みデータ量
# - Shuffle Write: シャッフルデータ量
# - Output Rows: 出力行数
```

## ログ分析

### ドライバーログ

```python
# ドライバーログ
dbutils.fs.ls("dbfs:/cluster-logs/<cluster-id>/driver/")

# エラーログ検索
logs = spark.read.text("dbfs:/cluster-logs/<cluster-id>/driver/stderr")
logs.filter(col("value").contains("ERROR")).show(truncate=False)

# 特定エラーパターン検索
error_patterns = [
    "OutOfMemoryError",
    "TimeoutException",
    "FileNotFoundException",
    "AnalysisException"
]

for pattern in error_patterns:
    count = logs.filter(col("value").contains(pattern)).count()
    print(f"{pattern}: {count} occurrences")
```

### Executorログ

```python
# Executorログ一覧
executor_logs = dbutils.fs.ls("dbfs:/cluster-logs/<cluster-id>/executor/")

# 全Executorログ統合分析
from pyspark.sql.functions import input_file_name

all_logs = spark.read.text("dbfs:/cluster-logs/<cluster-id>/executor/*/stderr") \
    .withColumn("executor", input_file_name())

# タスク失敗の分析
task_failures = all_logs.filter(
    col("value").contains("Task") & col("value").contains("failed")
)
task_failures.show(truncate=False)
```

### ログベースアラート

```python
# 定期的なログ監視ジョブ
def monitor_cluster_logs(cluster_id, lookback_minutes=60):
    """クラスターログを監視してアラート"""

    logs_path = f"dbfs:/cluster-logs/{cluster_id}/driver/stderr"

    # 最新ログ読み込み
    from datetime import datetime, timedelta
    cutoff_time = datetime.now() - timedelta(minutes=lookback_minutes)

    logs = spark.read.text(logs_path)

    # 重大エラー検出
    critical_errors = logs.filter(
        col("value").contains("FATAL") |
        col("value").contains("OutOfMemoryError")
    )

    if critical_errors.count() > 0:
        # アラート送信
        send_alert(f"Critical errors detected in cluster {cluster_id}")
        critical_errors.show(10, truncate=False)

    # パフォーマンス警告
    slow_tasks = logs.filter(col("value").contains("took") & col("value").contains("s"))
    if slow_tasks.count() > 100:
        send_alert(f"High number of slow tasks in cluster {cluster_id}")

# 定期実行（Databricks Jobs）
monitor_cluster_logs("1234-567890-abcdef")
```

## アラート設定

### メトリクスベースアラート

```python
# Databricks SDK でアラート設定
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

w = WorkspaceClient()

# ジョブ失敗アラート
def check_job_health(job_id):
    """ジョブの健全性チェック"""
    runs = w.jobs.list_runs(job_id=job_id, limit=10)

    failed_count = sum(1 for run in runs if run.state.result_state == "FAILED")
    success_rate = (len(runs) - failed_count) / len(runs)

    if success_rate < 0.9:  # 90%未満
        send_alert(f"Job {job_id} success rate: {success_rate:.1%}")

    return success_rate

# クラスターリソースアラート
def check_cluster_resources(cluster_id):
    """クラスターリソース使用状況チェック"""
    cluster = w.clusters.get(cluster_id=cluster_id)

    # メモリ使用率が80%以上で警告
    if cluster.driver.memory_mb_used / cluster.driver.memory_mb_total > 0.8:
        send_alert(f"High memory usage on cluster {cluster_id}")
```

### SQLアラート

```sql
-- データ品質アラート
CREATE ALERT data_quality_check
USING QUERY (
    SELECT COUNT(*) as null_records
    FROM my_table
    WHERE important_field IS NULL
        AND date = current_date()
)
WITH (
    threshold = 100,  -- NULL100件以上で通知
    frequency = 3600  -- 1時間ごと
);

-- SLAアラート
CREATE ALERT sla_violation
USING QUERY (
    SELECT COUNT(*) as late_jobs
    FROM system.lakeflow.job_run_timeline
    WHERE start_time >= current_timestamp() - INTERVAL 1 HOUR
        AND DATEDIFF(minute, start_time, end_time) > 60  -- 60分以上
)
WITH (
    threshold = 5
);
```

## トラブルシューティングチェックリスト

### ジョブ失敗時

1. **エラーメッセージ確認**
   - ジョブ実行画面のエラー詳細
   - ドライバーログ確認

2. **最近の変更確認**
   - コード変更
   - データスキーマ変更
   - クラスター設定変更

3. **リソース確認**
   - クラスターサイズ適切か
   - メモリ不足発生していないか

4. **データ確認**
   - 入力データ存在するか
   - データサイズ急増していないか

### パフォーマンス劣化時

1. **Spark UI分析**
   - 遅いステージ特定
   - シャッフル量確認
   - スキュー確認

2. **実行計画確認**
   - EXPLAIN実行
   - 不要なフルスキャン
   - 非効率なJOIN

3. **統計情報更新**
   ```sql
   ANALYZE TABLE my_table COMPUTE STATISTICS;
   ```

4. **最適化実行**
   ```sql
   OPTIMIZE my_table ZORDER BY (common_filter_column);
   ```

## ベストプラクティス

1. **プロアクティブ監視**
   - システムテーブル定期確認
   - メトリクスダッシュボード作成
   - アラート設定

2. **ログ保持**
   - クラスターログS3/ADLS保存
   - 長期分析用データ保持

3. **定期レビュー**
   - 週次: 失敗ジョブレビュー
   - 月次: パフォーマンストレンド分析
   - 四半期: コスト最適化レビュー

4. **ドキュメント化**
   - よくある問題と解決策
   - エスカレーション手順
   - 連絡先リスト

## まとめ

Spark UIとシステムテーブルでプロアクティブに監視。OOM、スキュー、シャッフル問題を早期発見し、適切に対処することで、安定したパイプラインを維持。定期的なログ分析とアラート設定で、問題の予兆を検知し、ダウンタイムを最小化。
