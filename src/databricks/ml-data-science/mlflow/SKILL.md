---
name: "Databricks MLflow活用"
description: "MLflowによる機械学習ライフサイクル管理。実験追跡、モデル登録、デプロイメント、バージョン管理、Unity Catalog統合"
---

# Databricks MLflow活用

## このスキルを使う場面

- ML実験を追跡・比較したい
- モデルをバージョン管理したい
- モデルを本番環境にデプロイしたい
- MLパイプラインを再現したい
- チームでMLアセットを共有したい

## MLflow 基礎

### 実験追跡

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 実験開始
with mlflow.start_run(run_name="rf_experiment"):
    # パラメーター記録
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # モデル訓練
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)
    
    # メトリクス記録
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    mlflow.log_metric("accuracy", accuracy)
    
    # モデル保存
    mlflow.sklearn.log_model(model, "model")
    
    # アーティファクト保存
    mlflow.log_artifact("feature_importance.png")
```

### Auto-Logging

```python
# 自動ログ記録 (パラメーター、メトリクス、モデル)
mlflow.autolog()

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)  # 自動的に記録される
```

## Unity Catalog Model Registry

### モデル登録

```python
# モデル登録 (Unity Catalog)
model_name = "main.ml_models.churn_prediction"

with mlflow.start_run():
    # モデル訓練
    model = train_model(X_train, y_train)
    
    # Unity Catalogに登録
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name=model_name
    )
```

### モデルバージョン管理

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# 新バージョン登録
model_version = client.create_model_version(
    name=model_name,
    source="runs:/abc123/model",
    run_id="abc123"
)

# ステージ移行
client.set_registered_model_alias(
    name=model_name,
    alias="Champion",
    version=model_version.version
)

# バージョン情報取得
versions = client.search_model_versions(f"name='{model_name}'")
```

## モデルデプロイメント

### Mosaic AI Model Serving

```python
# REST APIとしてデプロイ
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput

w = WorkspaceClient()

# エンドポイント作成
w.serving_endpoints.create(
    name="churn-model-endpoint",
    config=EndpointCoreConfigInput(
        served_models=[{
            "model_name": model_name,
            "model_version": "1",
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }]
    )
)

# 推論リクエスト
import requests

url = f"https://{workspace_url}/serving-endpoints/churn-model-endpoint/invocations"
headers = {"Authorization": f"Bearer {token}"}
data = {"dataframe_records": [{"age": 35, "income": 50000}]}

response = requests.post(url, headers=headers, json=data)
predictions = response.json()
```

### バッチ推論

```python
# モデルロード
model_uri = f"models:/{model_name}@Champion"
loaded_model = mlflow.pyfunc.load_model(model_uri)

# バッチ予測
predictions = loaded_model.predict(df_features)

# 結果保存
df_predictions = df.withColumn("prediction", predictions)
df_predictions.write.format("delta").mode("overwrite") \
    .save("/mnt/predictions/")
```

## MLflow Projects

```yaml
# MLproject ファイル
name: churn_prediction

conda_env: conda.yaml

entry_points:
  main:
    parameters:
      n_estimators: {type: int, default: 100}
      max_depth: {type: int, default: 10}
    command: "python train.py {n_estimators} {max_depth}"
```

```python
# プロジェクト実行
mlflow.run(
    ".",
    parameters={"n_estimators": 200, "max_depth": 15}
)
```

## 実験比較

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# 実験検索
experiment_id = mlflow.get_experiment_by_name("churn_prediction").experiment_id
runs = client.search_runs(
    experiment_ids=[experiment_id],
    order_by=["metrics.accuracy DESC"],
    max_results=10
)

# 比較
for run in runs:
    print(f"Run ID: {run.info.run_id}")
    print(f"Accuracy: {run.data.metrics['accuracy']}")
    print(f"Params: {run.data.params}")
```

## カスタムモデル

```python
import mlflow.pyfunc

class CustomModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # モデル初期化
        self.model = load_custom_model(context.artifacts["model_path"])
    
    def predict(self, context, model_input):
        # カスタム前処理
        processed = preprocess(model_input)
        
        # 推論
        predictions = self.model.predict(processed)
        
        # カスタム後処理
        return postprocess(predictions)

# ロギング
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=CustomModel(),
        artifacts={"model_path": "path/to/model"}
    )
```

## ベストプラクティス

1. **Unity Catalog使用** - モデルガバナンスと共有
2. **Autolog活用** - 自動追跡で記録漏れ防止
3. **命名規則統一** - `catalog.schema.model_name`
4. **ステージ管理** - Champion/Challenger でA/Bテスト
5. **モデルシグネチャ** - 入出力スキーマを明示

## まとめ

MLflowはML実験追跡、モデル登録、デプロイメントの全ライフサイクルを管理。Unity Catalogとの統合で、エンタープライズレベルのMLガバナンスを実現。
