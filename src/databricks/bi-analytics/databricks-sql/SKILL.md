---
name: "Databricks SQL"
description: "Databricks SQLによるデータ分析。SQLウェアハウス、クエリエディター、ダッシュボード、アラート、Photon最適化"
---

# Databricks SQL

## SQLウェアハウス

### ウェアハウス作成

```json
{
  "name": "Analytics Warehouse",
  "cluster_size": "Medium",
  "min_num_clusters": 1,
  "max_num_clusters": 3,
  "auto_stop_mins": 10,
  "enable_photon": true,
  "enable_serverless_compute": true,
  "spot_instance_policy": "COST_OPTIMIZED",
  "tags": {
    "team": "analytics",
    "environment": "production"
  }
}
```

**サイズ選択**:
- X-Small: 小規模クエリ（1-2ユーザー）
- Small: 軽量分析（3-5ユーザー）
- Medium: 標準分析（10-20ユーザー）
- Large: 大規模分析（20-40ユーザー）
- X-Large: 複雑な集計（40-80ユーザー）
- 2X-Large: エンタープライズ級（80+ユーザー）

**ウェアハウスタイプ比較**:

| タイプ | 起動時間 | スケーリング | コスト | 用途 |
|--------|---------|-------------|--------|------|
| Classic | 5-7分 | 手動/自動 | 標準 | 予測可能なワークロード |
| Pro | 5-7分 | 高度な自動 | +30% | 高負荷、並行ユーザー多 |
| Serverless | <1秒 | 完全自動 | +50% | 即時性、変動ワークロード |

### ウェアハウス管理

```sql
-- ウェアハウス情報確認
SHOW WAREHOUSES;

-- ウェアハウス使用状況
SELECT
    warehouse_name,
    query_count,
    total_duration_ms / 1000 / 60 as duration_minutes,
    total_queued_time_ms / 1000 as queued_seconds
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY warehouse_name;
```

### スケーリング戦略

```python
# プログラムでウェアハウス制御
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import sql

w = WorkspaceClient()

# ピーク時間前にウェアハウス起動
w.warehouses.start(id="abc123")

# オフピーク時にスケールダウン
w.warehouses.edit(
    id="abc123",
    max_num_clusters=1
)

# クエリキューイング確認
metrics = w.warehouses.get(id="abc123")
print(f"Active queries: {metrics.num_active_sessions}")
```

## クエリエディター

### 基本クエリ

```sql
-- パラメーター化クエリ
SELECT *
FROM sales
WHERE date = :date_param
    AND region = :region_param;

-- CTEで可読性向上
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', date) as month,
        SUM(amount) as total
    FROM sales
    GROUP BY 1
)
SELECT * FROM monthly_sales
WHERE total > 100000;
```

### 高度なクエリパターン

```sql
-- ウィンドウ関数活用
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total,
    AVG(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7days,
    RANK() OVER (
        PARTITION BY DATE_TRUNC('month', order_date)
        ORDER BY amount DESC
    ) as monthly_rank
FROM orders
WHERE order_date >= '2025-01-01';

-- 複雑な集計
WITH customer_segments AS (
    SELECT
        customer_id,
        SUM(amount) as total_spent,
        COUNT(DISTINCT order_id) as order_count,
        MAX(order_date) as last_order_date,
        DATEDIFF(current_date(), MAX(order_date)) as days_since_last_order
    FROM orders
    WHERE order_date >= current_date() - INTERVAL 365 DAYS
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN total_spent > 10000 AND days_since_last_order <= 30 THEN 'VIP Active'
        WHEN total_spent > 10000 AND days_since_last_order > 30 THEN 'VIP At Risk'
        WHEN total_spent > 1000 THEN 'Regular'
        ELSE 'Occasional'
    END as segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spent,
    AVG(order_count) as avg_orders
FROM customer_segments
GROUP BY segment;
```

### クエリ最適化テクニック

```sql
-- ✅ プッシュダウン最適化
-- フィルタは早めに適用
SELECT customer_id, SUM(amount)
FROM orders
WHERE date >= '2025-01-01'  -- パーティションプルーニング
    AND status = 'completed'  -- 早期フィルタ
GROUP BY customer_id;

-- ❌ 非効率パターン
-- 全データ読み込み後にフィルタ
SELECT customer_id, total_amount
FROM (
    SELECT customer_id, SUM(amount) as total_amount
    FROM orders
    GROUP BY customer_id
)
WHERE total_amount > 1000;  -- HAVING使うべき

-- ✅ ブロードキャストジョイン
SELECT /*+ BROADCAST(d) */
    f.order_id,
    f.amount,
    d.customer_name
FROM fact_orders f
JOIN dim_customers d ON f.customer_id = d.customer_id
WHERE d.region = 'US';

-- 実行計画確認
EXPLAIN FORMATTED
SELECT * FROM large_table
WHERE amount > 1000;
```

## ダッシュボード

### 基本ダッシュボード

```sql
-- ダッシュボード用クエリ
SELECT
    region,
    COUNT(*) as order_count,
    SUM(amount) as revenue,
    AVG(amount) as avg_order_value
FROM sales
WHERE date >= current_date() - INTERVAL 30 DAYS
GROUP BY region
ORDER BY revenue DESC;
```

### 高度なダッシュボードパターン

```sql
-- KPIダッシュボード: 前月比較
WITH current_month AS (
    SELECT
        SUM(amount) as revenue,
        COUNT(DISTINCT customer_id) as customers,
        COUNT(*) as orders
    FROM sales
    WHERE date >= DATE_TRUNC('month', current_date())
),
previous_month AS (
    SELECT
        SUM(amount) as revenue,
        COUNT(DISTINCT customer_id) as customers,
        COUNT(*) as orders
    FROM sales
    WHERE date >= DATE_TRUNC('month', current_date()) - INTERVAL 1 MONTH
        AND date < DATE_TRUNC('month', current_date())
)
SELECT
    c.revenue as current_revenue,
    p.revenue as previous_revenue,
    ROUND((c.revenue - p.revenue) / p.revenue * 100, 2) as revenue_growth_pct,
    c.customers as current_customers,
    p.customers as previous_customers,
    ROUND((c.customers - p.customers) / p.customers * 100, 2) as customer_growth_pct
FROM current_month c, previous_month p;

-- コホート分析
SELECT
    DATE_TRUNC('month', first_order_date) as cohort_month,
    DATEDIFF(DATE_TRUNC('month', order_date), DATE_TRUNC('month', first_order_date)) / 30 as months_since_first,
    COUNT(DISTINCT customer_id) as retained_customers,
    SUM(amount) as cohort_revenue
FROM (
    SELECT
        o.customer_id,
        o.order_date,
        o.amount,
        MIN(o.order_date) OVER (PARTITION BY o.customer_id) as first_order_date
    FROM orders o
)
WHERE first_order_date >= '2024-01-01'
GROUP BY cohort_month, months_since_first
ORDER BY cohort_month, months_since_first;

-- リアルタイムダッシュボード（ストリーミングテーブル）
CREATE OR REFRESH STREAMING TABLE real_time_metrics AS
SELECT
    window.start as window_start,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(response_time_ms) as avg_response_time
FROM STREAM(events)
GROUP BY window(event_timestamp, '5 minutes');
```

### ダッシュボードビジュアライゼーション

```sql
-- 時系列チャート用
SELECT
    DATE_TRUNC('day', date) as day,
    SUM(amount) as daily_revenue
FROM sales
WHERE date >= current_date() - INTERVAL 90 DAYS
GROUP BY day
ORDER BY day;

-- カテゴリ分布（パイチャート用）
SELECT
    category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM products
GROUP BY category
ORDER BY count DESC;

-- ヒートマップ用
SELECT
    DAYOFWEEK(date) as day_of_week,
    HOUR(timestamp) as hour,
    COUNT(*) as order_count
FROM orders
WHERE date >= current_date() - INTERVAL 30 DAYS
GROUP BY day_of_week, hour;
```

## アラート

### 基本アラート

```sql
-- アラート設定
SELECT
    COUNT(*) as failed_orders
FROM orders
WHERE status = 'failed'
    AND date = current_date();

-- 閾値: failed_orders > 100
-- 通知: Slack, Email
```

### 高度なアラートパターン

```sql
-- 異常検知アラート: 売上急減
WITH daily_revenue AS (
    SELECT
        date,
        SUM(amount) as revenue
    FROM sales
    WHERE date >= current_date() - INTERVAL 30 DAYS
    GROUP BY date
),
stats AS (
    SELECT
        AVG(revenue) as avg_revenue,
        STDDEV(revenue) as stddev_revenue
    FROM daily_revenue
    WHERE date < current_date()
),
today AS (
    SELECT SUM(amount) as today_revenue
    FROM sales
    WHERE date = current_date()
)
SELECT
    today.today_revenue,
    stats.avg_revenue,
    CASE
        WHEN today.today_revenue < (stats.avg_revenue - 2 * stats.stddev_revenue)
        THEN 'ALERT: Revenue is 2 standard deviations below average'
        ELSE 'OK'
    END as status
FROM today, stats;

-- SLAアラート: レスポンスタイム
SELECT
    COUNT(*) as slow_queries,
    AVG(execution_time_ms) as avg_time_ms
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 1 HOUR
    AND execution_time_ms > 10000  -- 10秒以上
HAVING COUNT(*) > 50;  -- 50クエリ以上

-- データ品質アラート
SELECT
    table_name,
    COUNT(*) as null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales) as null_percentage
FROM sales
WHERE customer_id IS NULL
    OR amount IS NULL
    OR date IS NULL
GROUP BY table_name
HAVING null_percentage > 5;  -- 5%以上のNULL
```

### アラート管理

```python
# Databricks REST APIでアラート管理
import requests

# アラート作成
alert_config = {
    "name": "High Error Rate Alert",
    "query_id": "abc-123",
    "options": {
        "column": "error_count",
        "op": ">",
        "value": 100
    },
    "rearm": 300  # 5分後に再アラート可能
}

# 通知先設定
notification = {
    "destination_type": "slack",
    "addresses": ["#alerts-channel"]
}
```

## パフォーマンス最適化

### Photon最適化

```sql
-- ✅ Photon最適化済みクエリ
SELECT
    customer_id,
    SUM(amount) as total_spent
FROM purchases
WHERE date >= '2025-01-01'
GROUP BY customer_id
HAVING total_spent > 1000;

-- Result Cache活用
-- 同じクエリは自動キャッシュ（24時間）
```

**Photon最適化効果**:

| クエリタイプ | 高速化率 | 対象演算 |
|------------|---------|---------|
| 集計クエリ | 3-8x | GROUP BY, SUM, AVG |
| JOIN | 5-12x | Hash Join, Sort Merge Join |
| フィルタリング | 2-5x | WHERE, HAVING |
| ウィンドウ関数 | 4-10x | RANK, ROW_NUMBER, LAG/LEAD |

### クエリプロファイリング

```sql
-- クエリ履歴分析
SELECT
    query_id,
    query_text,
    execution_time_ms / 1000 as execution_sec,
    rows_produced,
    bytes_read / 1024 / 1024 as mb_read,
    user_name
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 1 DAYS
    AND execution_time_ms > 30000  -- 30秒以上
ORDER BY execution_time_ms DESC
LIMIT 20;

-- リソース使用状況
SELECT
    DATE_TRUNC('hour', start_time) as hour,
    warehouse_name,
    COUNT(*) as query_count,
    SUM(execution_time_ms) / 1000 / 60 as total_minutes,
    AVG(execution_time_ms) / 1000 as avg_seconds,
    SUM(bytes_read) / 1024 / 1024 / 1024 as total_gb_read
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY hour, warehouse_name
ORDER BY hour DESC, total_minutes DESC;
```

### Result Cache活用

```sql
-- Result Cacheヒット確認
SELECT
    query_id,
    query_text,
    result_cache_hit,
    execution_time_ms
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 1 HOUR
ORDER BY start_time DESC;

-- キャッシュ最適化パターン
-- 1. 完全一致クエリ（自動キャッシュ）
SELECT * FROM sales WHERE date = '2025-01-15';

-- 2. パラメーター化で再利用
SELECT * FROM sales WHERE date = :date_param;

-- 3. マテリアライズドビュー
CREATE MATERIALIZED VIEW sales_daily_summary AS
SELECT
    date,
    SUM(amount) as total_amount,
    COUNT(*) as order_count
FROM sales
GROUP BY date;

-- 定期リフレッシュ
REFRESH MATERIALIZED VIEW sales_daily_summary;
```

## コスト最適化

```sql
-- ウェアハウスコスト分析
SELECT
    warehouse_name,
    DATE_TRUNC('day', start_time) as day,
    COUNT(*) as query_count,
    SUM(execution_time_ms) / 1000 / 60 / 60 as compute_hours,
    SUM(bytes_read) / 1024 / 1024 / 1024 / 1024 as tb_read
FROM system.query.history
WHERE start_time >= current_date() - INTERVAL 30 DAYS
GROUP BY warehouse_name, day
ORDER BY compute_hours DESC;

-- 非効率クエリ検出
SELECT
    user_name,
    COUNT(*) as slow_query_count,
    AVG(execution_time_ms) / 1000 as avg_seconds
FROM system.query.history
WHERE execution_time_ms > 60000  -- 1分以上
    AND start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY user_name
HAVING COUNT(*) > 10
ORDER BY slow_query_count DESC;
```

## セキュリティとガバナンス

```sql
-- Unity Catalog統合
-- 3層ネームスペース: catalog.schema.table
SELECT * FROM production.sales.orders;

-- 動的データマスキング
CREATE FUNCTION mask_pii(email STRING)
RETURNS STRING
RETURN CONCAT(LEFT(email, 3), '***@***.com');

-- 行レベルセキュリティ
CREATE VIEW sales_by_region AS
SELECT *
FROM sales
WHERE region IN (
    SELECT region
    FROM user_permissions
    WHERE user_name = current_user()
);

-- 監査ログ
SELECT
    user_name,
    action_name,
    request_params,
    result,
    event_time
FROM system.access.audit
WHERE event_time >= current_date() - INTERVAL 7 DAYS
    AND action_name IN ('createTable', 'deleteTable', 'readFiles')
ORDER BY event_time DESC;
```

## ベストプラクティス

1. **Photon有効化** - 最大12倍高速
   - 全ての本番ウェアハウスで有効化
   - 集計・JOIN多用時に特に効果的

2. **Serverless使用** - インフラ管理不要
   - 変動ワークロード向け
   - 即座の起動が必要な場合

3. **パラメーター化** - クエリ再利用
   - Result Cache活用
   - SQLインジェクション防止

4. **自動停止設定** - コスト削減
   - 開発: 10分
   - 本番: 30-60分（ワークロードに応じて）

5. **クエリ最適化**
   - パーティションプルーニング活用
   - 早期フィルタリング
   - 適切なJOIN順序

6. **モニタリング**
   - システムテーブル活用
   - 定期的なパフォーマンスレビュー
   - アラート設定

## トラブルシューティング

### 問題: クエリが遅い

```sql
-- 診断
EXPLAIN FORMATTED
SELECT * FROM large_table WHERE amount > 1000;

-- 確認ポイント:
-- 1. PartitionFilters: パーティションプルーニング発生しているか
-- 2. PushedFilters: フィルタがプッシュダウンされているか
-- 3. Statistics: テーブル統計が最新か

-- 解決策
ANALYZE TABLE large_table COMPUTE STATISTICS;
OPTIMIZE large_table ZORDER BY (amount);
```

### 問題: ウェアハウスキューイング

```python
# 診断
metrics = w.warehouses.get(id="abc123")
print(f"Queued queries: {metrics.num_queued_queries}")

# 解決策
# 1. クラスター数増加
w.warehouses.edit(id="abc123", max_num_clusters=5)

# 2. より大きいサイズ
w.warehouses.edit(id="abc123", cluster_size="LARGE")

# 3. クエリ最適化
# → 実行計画確認、不要なフルスキャン削除
```

## まとめ

Databricks SQLは、Photon最適化、Serverless、結果キャッシュで高速分析を提供。ダッシュボードとアラートで、データドリブンな意思決定を支援。Unity Catalogとの統合で、エンタープライズグレードのガバナンスを実現。
