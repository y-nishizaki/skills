---
name: "Databricks AutoML実装"
description: "Databricks AutoMLとNotebooksによるML実装。自動モデル選択、ハイパーパラメーターチューニング、コード生成、カスタマイズ"
---

# Databricks AutoML実装

## このスキルを使う場面

- 迅速にMLモデルを構築したい
- ベースラインモデルを自動生成したい
- ベストプラクティスコードを学びたい
- ハイパーパラメーターを最適化したい

## AutoML 基礎

### 分類タスク

```python
from databricks import automl

# データ準備
train_df = spark.table("main.default.iris_train")

# AutoML実行
summary = automl.classify(
    dataset=train_df,
    target_col="species",
    primary_metric="f1",
    timeout_minutes=30,
    max_trials=100
)

# ベストモデル
print(f"Best trial run_id: {summary.best_trial.mlflow_run_id}")
print(f"Best model F1 score: {summary.best_trial.metrics['test_f1_score']}")

# モデル登録
import mlflow
model_uri = f"runs:/{summary.best_trial.mlflow_run_id}/model"
mlflow.register_model(model_uri, "main.ml_models.iris_classifier")
```

### 回帰タスク

```python
summary = automl.regress(
    dataset=train_df,
    target_col="price",
    primary_metric="r2",
    time_col="date",  # 時系列の場合
    timeout_minutes=30
)
```

### 予測（時系列）

```python
summary = automl.forecast(
    dataset=train_df,
    target_col="sales",
    time_col="date",
    frequency="D",  # 日次
    horizon=30,  # 30日先まで予測
    identity_col="store_id"  # 複数系列
)
```

## 生成されたノートブックの活用

AutoMLは以下のノートブックを自動生成:

1. **Data Exploration Notebook** - EDA
2. **Best Trial Notebook** - ベストモデルのコード
3. **Model Training Notebook** - 全試行の詳細

```python
# ベストトライアルのノートブックパス取得
notebook_path = summary.best_trial.notebook_path
print(f"Best trial notebook: {notebook_path}")

# ノートブックをカスタマイズして再実行可能
```

## カスタマイズ

### 前処理のカスタマイズ

```python
# 生成されたノートブックをベースに修正
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

# カスタム前処理追加
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ]
)

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', model)  # AutoMLのモデル
])
```

### ハイパーパラメーター再調整

```python
from hyperopt import hp, fmin, tpe, Trials

# ハイパーパラメーター空間
space = {
    'n_estimators': hp.quniform('n_estimators', 100, 1000, 100),
    'max_depth': hp.quniform('max_depth', 5, 50, 5),
    'learning_rate': hp.loguniform('learning_rate', -5, 0)
}

# 最適化
best_params = fmin(
    fn=objective_function,
    space=space,
    algo=tpe.suggest,
    max_evals=100
)
```

## ベストプラクティス

1. **ベースライン作成** - AutoMLでまず実行
2. **コード学習** - 生成ノートブックから学ぶ
3. **カスタマイズ** - 必要に応じてコード修正
4. **実験管理** - MLflowで追跡
5. **本番化** - Unity Catalogに登録

## まとめ

AutoMLは迅速なモデル構築とコード生成を提供。生成されたノートブックをベースにカスタマイズすることで、効率的にMLパイプラインを構築できる。
