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
  "enable_serverless_compute": true
}
```

**サイズ選択**:
- X-Small: 小規模クエリ
- Medium: 標準分析
- X-Large: 複雑な集計

## クエリエディター

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

## ダッシュボード

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

## アラート

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

## パフォーマンス最適化

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
-- 同じクエリは自動キャッシュ
```

## ベストプラクティス

1. **Photon有効化** - 最大12倍高速
2. **Serverless使用** - インフラ管理不要
3. **パラメーター化** - クエリ再利用
4. **自動停止設定** - コスト削減

## まとめ

Databricks SQLは、Photon最適化、Serverless、結果キャッシュで高速分析を提供。ダッシュボードとアラートで、データドリブンな意思決定を支援。
