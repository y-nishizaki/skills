---
name: "Databricks Feature Store活用"
description: "Feature Storeによる特徴量管理。特徴量定義、オンライン/オフライン利用、バージョン管理、再利用性向上"
---

# Databricks Feature Store活用

## このスキルを使う場面

- 特徴量を一元管理したい
- 訓練と推論で特徴量を統一したい
- 特徴量を再利用・共有したい
- オンライン推論が必要
- 特徴量のバージョン管理が必要

## Feature Store 基礎

### 特徴量テーブル作成

```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

# 特徴量計算
features_df = spark.sql("""
    SELECT
        user_id,
        COUNT(*) as purchase_count_30d,
        AVG(amount) as avg_purchase_amount_30d,
        MAX(last_purchase_date) as last_purchase_date
    FROM purchases
    WHERE date >= current_date() - INTERVAL 30 DAYS
    GROUP BY user_id
""")

# Feature Tableとして登録
fe.create_table(
    name="main.features.user_purchase_features",
    primary_keys=["user_id"],
    df=features_df,
    description="User purchase behavior features"
)
```

### 特徴量更新

```python
# 定期更新 (MERGE)
fe.write_table(
    name="main.features.user_purchase_features",
    df=new_features_df,
    mode="merge"
)
```

## ML訓練での利用

```python
from databricks.feature_engineering import FeatureLookup

# 特徴量ルックアップ定義
feature_lookups = [
    FeatureLookup(
        table_name="main.features.user_purchase_features",
        feature_names=["purchase_count_30d", "avg_purchase_amount_30d"],
        lookup_key="user_id"
    ),
    FeatureLookup(
        table_name="main.features.user_demographic_features",
        feature_names=["age", "city"],
        lookup_key="user_id"
    )
]

# トレーニングセット作成
training_set = fe.create_training_set(
    df=labels_df,  # user_id と label のみ
    feature_lookups=feature_lookups,
    label="churned",
    exclude_columns=["user_id"]
)

# DataFrameとして取得
training_df = training_set.load_df()

# モデル訓練 + 自動的に特徴量メタデータを記録
fe.log_model(
    model=model,
    artifact_path="model",
    flavor=mlflow.sklearn,
    training_set=training_set,
    registered_model_name="main.ml_models.churn_model"
)
```

## オンライン推論

```python
# オンラインストア公開
from databricks.feature_engineering import FeatureSpec

spec = FeatureSpec(
    name="main.features.user_purchase_features",
    online_store="databricks_online_store"
)

fe.publish_table(spec)

# リアルタイム推論
# (Model Servingが自動的にオンラインストアから特徴量取得)
```

## バッチ推論

```python
# 推論用データセット (user_id のみ)
batch_df = spark.table("users_to_score")

# 特徴量自動結合 + 予測
predictions = fe.score_batch(
    model_uri=f"models:/main.ml_models.churn_model@Champion",
    df=batch_df
)

predictions.write.format("delta").save("/mnt/predictions/")
```

## 時系列特徴量

```python
from databricks.feature_engineering import FeatureLookup

# Point-in-time lookup
feature_lookups = [
    FeatureLookup(
        table_name="main.features.stock_prices",
        feature_names=["price", "volume"],
        lookup_key="symbol",
        timestamp_lookup_key="trade_date"  # 時系列考慮
    )
]

training_set = fe.create_training_set(
    df=labels_df,  # symbol, trade_date, label
    feature_lookups=feature_lookups,
    label="price_up",
    exclude_columns=["symbol", "trade_date"]
)
```

## 特徴量リネージ

```python
# 特徴量の系統確認
lineage = fe.get_table("main.features.user_purchase_features").lineage

# どのモデルがこの特徴量を使用しているか確認
consuming_models = lineage.downstream_models
```

## ベストプラクティス

1. **主キー設計** - エンティティごとにテーブル分割
2. **定期更新** - バッチジョブで特徴量を最新化
3. **ドキュメント** - 特徴量の意味と計算ロジックを記載
4. **バージョン管理** - Unity Catalogで変更履歴追跡
5. **オンライン最適化** - レイテンシ要件に応じて公開

## まとめ

Feature Storeは特徴量の一元管理、訓練/推論での一貫性、再利用性を実現。オンライン/オフライン両対応で、リアルタイム推論も効率化。
