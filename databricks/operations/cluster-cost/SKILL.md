---
name: "Databricksクラスター構成とコスト最適化"
description: "クラスター構成とコスト最適化。クラスタータイプ、自動スケーリング、Photon、Spot/Graviton、コスト追跡"
---

# Databricksクラスター構成とコスト最適化

## このスキルを使う場面

- クラスターコストを削減したい
- 適切なクラスター構成を選択したい
- 自動スケーリングを最適化したい
- コスト追跡・予測をしたい

## クラスタータイプ

### All-Purpose Cluster

```json
{
  "cluster_name": "Interactive Cluster",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "autotermination_minutes": 120
}
```

**用途**: 対話的分析、ノートブック開発
**課金**: 起動中は常に課金

### Job Cluster

```json
{
  "new_cluster": {
    "spark_version": "14.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 4
  }
}
```

**用途**: 本番ジョブ、自動化パイプライン
**課金**: ジョブ実行中のみ
**コスト**: All-Purposeより安価

### Serverless

```json
{
  "serverless": true
}
```

**用途**: DLT、SQL、モデルサービング
**メリット**: インフラ管理不要、即座起動

## 自動スケーリング最適化

### 適切な範囲設定

```json
// ✅ 推奨
{
  "autoscale": {
    "min_workers": 2,
    "max_workers": 10
  }
}

// ❌ 非効率
{
  "autoscale": {
    "min_workers": 1,  // 起動遅延
    "max_workers": 100  // 過剰
  }
}
```

### ワークロード別設定

```python
# バッチ処理: 固定サイズ
batch_cluster = {
    "num_workers": 8  # 自動スケーリングなし
}

# 対話的: 自動スケーリング
interactive_cluster = {
    "autoscale": {
        "min_workers": 2,
        "max_workers": 8
    }
}
```

## Photon Engine

```json
{
  "runtime_engine": "PHOTON",
  "spark_version": "14.3.x-photon-scala2.12"
}
```

**効果**: 最大12倍高速
**コスト**: わずかな追加料金で大幅な時間短縮
**推奨**: SQL重視のワークロード

## Spot/Preemptible Instances

### AWS Spot Instances

```json
{
  "aws_attributes": {
    "first_on_demand": 1,
    "availability": "SPOT_WITH_FALLBACK",
    "zone_id": "us-east-1a",
    "spot_bid_price_percent": 100
  }
}
```

**コスト削減**: 最大90%
**リスク**: 中断の可能性
**推奨**: フォールトトレラントなワークロード

### Graviton Instances (ARM)

```json
{
  "node_type_id": "m6gd.xlarge"  // Graviton
}
```

**コスト削減**: 最大20%
**互換性**: ほとんどのワークロードで動作

## クラスタープール

```json
{
  "instance_pool_id": "pool-abc123",
  "driver_instance_pool_id": "pool-def456"
}
```

**メリット**:
- 起動時間短縮 (数分 → 数秒)
- アイドルインスタンスの再利用
- コスト予測可能

## 自動終了

```json
{
  "autotermination_minutes": 30  // 30分アイドルで自動終了
}
```

**推奨設定**:
- 開発: 30-60分
- 本番: 自動終了なし (ジョブクラスター使用)

## コスト追跡

### システムテーブルで分析

```sql
SELECT
    usage_date,
    sku_name,
    usage_unit,
    SUM(usage_quantity) as total_usage,
    SUM(list_price * usage_quantity) as cost_usd
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 30 DAYS
GROUP BY usage_date, sku_name, usage_unit
ORDER BY cost_usd DESC;

-- クラスター別コスト
SELECT
    cluster_id,
    SUM(list_price * usage_quantity) as cluster_cost
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 30 DAYS
GROUP BY cluster_id
ORDER BY cluster_cost DESC;
```

## ベストプラクティス

1. **ジョブクラスター優先** - 本番ワークロードはジョブクラスター
2. **Photon有効化** - SQL/DataFrame処理で大幅高速化
3. **Spot活用** - 開発・テストでコスト削減
4. **自動終了設定** - アイドルクラスターを自動停止
5. **定期コスト分析** - システムテーブルで追跡

## まとめ

適切なクラスタータイプ選択、自動スケーリング、Photon、Spot/Gravitonの組み合わせで、最大90%のコスト削減が可能。システムテーブルで継続的に監視・最適化することが重要。
