---
name: "MLOps"
description: "機械学習モデルの運用自動化。CI/CD、モニタリング、再学習"
---

# MLOps: 機械学習の運用管理

## このスキルを使う場面

- モデルを本番環境にデプロイしたい
- モデルのパフォーマンスを継続監視したい
- 再学習を自動化したい
- バージョン管理を適切に行いたい

## MLOpsのコンポーネント

### 1. モデルバージョン管理

```python
# MLflow
import mlflow
import mlflow.sklearn

with mlflow.start_run():
    # モデル訓練
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # メトリクス記録
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # モデル保存
    mlflow.sklearn.log_model(model, "model")
```

### 2. モデルデプロイ

```python
# FastAPI でモデルサービング
from fastapi import FastAPI
import joblib

app = FastAPI()
model = joblib.load("model.pkl")

@app.post("/predict")
def predict(features: dict):
    X = preprocess(features)
    prediction = model.predict(X)
    return {"prediction": prediction.tolist()}
```

### 3. データパイプライン

```python
# Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG('ml_pipeline', schedule_interval='@daily')

extract_data = PythonOperator(
    task_id='extract',
    python_callable=extract_data_func,
    dag=dag
)

train_model = PythonOperator(
    task_id='train',
    python_callable=train_model_func,
    dag=dag
)

extract_data >> train_model
```

### 4. モニタリング

```python
# モデルパフォーマンス監視
def monitor_model(y_true, y_pred):
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred)
    }

    # 閾値チェック
    if metrics['accuracy'] < 0.8:
        send_alert("Model performance degradation")

    log_metrics(metrics)
```

### 5. データドリフト検出

```python
from scipy.stats import ks_2samp

# 分布の変化を検出
for feature in features:
    statistic, p_value = ks_2samp(
        training_data[feature],
        production_data[feature]
    )

    if p_value < 0.05:
        print(f"Drift detected in {feature}")
```

## MLOpsツール

**実験管理**: MLflow, Weights & Biases
**モデルサービング**: TensorFlow Serving, TorchServe, FastAPI
**パイプライン**: Airflow, Kubeflow, Prefect
**モニタリング**: Prometheus, Grafana, Evidently
**フィーチャーストア**: Feast, Tecton

## ベストプラクティス

- CI/CDパイプラインの構築
- A/Bテストでの段階的デプロイ
- 継続的モニタリング
- 自動再学習の仕組み
- モデルのrollback戦略

## 検証ポイント

- [ ] バージョン管理している
- [ ] 自動デプロイパイプライン
- [ ] パフォーマンス監視
- [ ] データドリフト検出
- [ ] 再学習の自動化
