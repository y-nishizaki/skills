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
- 複数モデルを協調動作させたい
- モデルのコストとパフォーマンスを最適化したい

## MLOpsのコンポーネント

### 1. モデルバージョン管理

```python
# MLflow での詳細なバージョン管理
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

with mlflow.start_run(run_name="experiment-v1.2.3") as run:
    # パラメータ記録
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    mlflow.log_params(params)

    # モデル訓練
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # 複数メトリクス記録
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
        "recall": recall_score(y_test, y_pred, average='weighted'),
        "f1_score": f1_score(y_test, y_pred, average='weighted'),
        "roc_auc": roc_auc_score(y_test, y_pred_proba)
    }
    mlflow.log_metrics(metrics)

    # アーティファクト保存（モデル、図表、データ）
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="fraud_detection_model"
    )

    # 混同行列の保存
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots()
    ax.imshow(cm)
    mlflow.log_figure(fig, "confusion_matrix.png")

    # 特徴量重要度の記録
    feature_importance = dict(zip(feature_names, model.feature_importances_))
    mlflow.log_dict(feature_importance, "feature_importance.json")

# モデルレジストリ操作
client = MlflowClient()

# 本番環境に昇格
client.transition_model_version_stage(
    name="fraud_detection_model",
    version=3,
    stage="Production"
)
```

### 2. モデルデプロイと推論API

```python
# FastAPI での本番向けモデルサービング
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
import joblib
import numpy as np
from typing import List, Optional
import logging
from prometheus_client import Counter, Histogram
import time

# メトリクス定義
prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

app = FastAPI(title="ML Model API", version="1.0.0")

# モデルのロード（起動時）
class ModelLoader:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None

    def load(self):
        self.model = joblib.load("model.pkl")
        self.scaler = joblib.load("scaler.pkl")
        self.feature_names = joblib.load("features.pkl")

model_loader = ModelLoader()

@app.on_event("startup")
async def startup_event():
    model_loader.load()
    logging.info("Model loaded successfully")

# リクエストモデル
class PredictionRequest(BaseModel):
    features: dict
    request_id: Optional[str] = None

    @validator('features')
    def validate_features(cls, v):
        if not v:
            raise ValueError("Features cannot be empty")
        return v

class PredictionResponse(BaseModel):
    prediction: List[float]
    prediction_proba: Optional[List[float]] = None
    model_version: str
    request_id: Optional[str] = None
    latency_ms: float

# ヘルスチェック
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_loader.model is not None
    }

# 予測エンドポイント
@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    start_time = time.time()

    try:
        # 特徴量の前処理
        X = preprocess_features(
            request.features,
            model_loader.feature_names,
            model_loader.scaler
        )

        # 予測実行
        prediction = model_loader.model.predict(X)
        prediction_proba = model_loader.model.predict_proba(X)

        # メトリクス記録
        prediction_counter.inc()
        latency = (time.time() - start_time) * 1000
        prediction_latency.observe(latency / 1000)

        # バックグラウンドでログ記録
        background_tasks.add_task(
            log_prediction,
            request.features,
            prediction,
            request.request_id
        )

        return PredictionResponse(
            prediction=prediction.tolist(),
            prediction_proba=prediction_proba.tolist(),
            model_version="v1.2.3",
            request_id=request.request_id,
            latency_ms=latency
        )

    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# バッチ予測
@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    predictions = []
    for req in requests:
        pred = await predict(req, BackgroundTasks())
        predictions.append(pred)
    return {"predictions": predictions}

def preprocess_features(features, feature_names, scaler):
    """特徴量の前処理"""
    X = np.array([[features.get(f, 0) for f in feature_names]])
    X_scaled = scaler.transform(X)
    return X_scaled

def log_prediction(features, prediction, request_id):
    """予測ログの記録（バックグラウンド処理）"""
    # データベースやログファイルに記録
    pass
```

### 3. コンテナ化とKubernetesデプロイ

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# モデルとコードをコピー
COPY model.pkl scaler.pkl features.pkl ./
COPY app.py .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# アプリケーション起動
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-deployment
  labels:
    app: ml-model
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model
  template:
    metadata:
      labels:
        app: ml-model
        version: v1.2.3
    spec:
      containers:
      - name: ml-model
        image: your-registry/ml-model:v1.2.3
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-service
spec:
  selector:
    app: ml-model
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 4. CI/CDパイプライン

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Model CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/ --cov=./ --cov-report=xml

      - name: Data validation
        run: python scripts/validate_data.py

      - name: Model validation
        run: python scripts/validate_model.py

  train:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2

      - name: Train model
        run: python train.py
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_URI }}

      - name: Evaluate model
        run: python evaluate.py

      - name: Register model
        if: success()
        run: python register_model.py

  deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t ml-model:${{ github.sha }} .

      - name: Push to registry
        run: |
          docker tag ml-model:${{ github.sha }} registry/ml-model:latest
          docker push registry/ml-model:latest

      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/

      - name: Run integration tests
        run: python tests/integration_test.py

      - name: Deploy to production
        if: success()
        run: kubectl apply -f k8s/production/
```

### 5. データパイプラインの構築

```python
# Airflow での包括的なMLパイプライン
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3Hook
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_pipeline_comprehensive',
    default_args=default_args,
    description='End-to-end ML pipeline',
    schedule_interval='@daily',
    catchup=False
)

def extract_data(**context):
    """データ抽出"""
    execution_date = context['execution_date']

    # データベースから抽出
    df = pd.read_sql(
        f"SELECT * FROM transactions WHERE date = '{execution_date}'",
        connection
    )

    # S3に保存
    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.load_file_obj(
        df.to_csv(index=False),
        key=f'raw_data/{execution_date}.csv',
        bucket_name='ml-data'
    )

    return f'raw_data/{execution_date}.csv'

def validate_data(**context):
    """データ品質チェック"""
    file_path = context['task_instance'].xcom_pull(task_ids='extract_data')
    df = pd.read_csv(file_path)

    # 必須チェック
    assert df.shape[0] > 0, "Empty dataset"
    assert df.isnull().sum().sum() < len(df) * 0.1, "Too many nulls"
    assert all(col in df.columns for col in required_columns), "Missing columns"

    # 統計的チェック
    for col in numeric_columns:
        mean = df[col].mean()
        std = df[col].std()

        # 過去の分布と比較
        historical_mean = get_historical_mean(col)
        if abs(mean - historical_mean) > 3 * std:
            send_alert(f"Anomaly detected in {col}")

def feature_engineering(**context):
    """特徴量エンジニアリング"""
    file_path = context['task_instance'].xcom_pull(task_ids='extract_data')
    df = pd.read_csv(file_path)

    # 特徴量生成
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    df['transaction_velocity'] = df.groupby('user_id')['amount'].transform('count')

    # 特徴量ストアに保存
    save_to_feature_store(df)

    return 'features_ready'

def train_model(**context):
    """モデル訓練"""
    features = load_from_feature_store()

    with mlflow.start_run():
        # 訓練
        model = train_model_function(features)

        # 評価
        metrics = evaluate_model(model, test_data)

        # 既存モデルと比較
        current_model_metrics = get_production_model_metrics()

        if metrics['auc'] > current_model_metrics['auc']:
            # 新しいモデルが優れている場合のみ保存
            mlflow.sklearn.log_model(model, "model")
            context['task_instance'].xcom_push(key='model_uri', value=mlflow.get_artifact_uri())
            return 'model_improved'
        else:
            return 'model_not_improved'

def deploy_model(**context):
    """モデルデプロイ"""
    model_status = context['task_instance'].xcom_pull(task_ids='train_model')

    if model_status == 'model_improved':
        model_uri = context['task_instance'].xcom_pull(
            task_ids='train_model',
            key='model_uri'
        )

        # カナリアデプロイ（10%のトラフィック）
        deploy_canary(model_uri, traffic_percentage=10)

        # 監視期間
        time.sleep(3600)  # 1時間待機

        # メトリクス確認
        if check_canary_metrics():
            # 全トラフィックに展開
            promote_to_production(model_uri)
        else:
            # ロールバック
            rollback_deployment()

# タスク定義
extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag
)

engineer_features = PythonOperator(
    task_id='feature_engineering',
    python_callable=feature_engineering,
    dag=dag
)

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

deploy = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag
)

# 依存関係
extract >> validate >> engineer_features >> train >> deploy
```

### 6. モニタリングと観測性

```python
# 包括的なモデルモニタリング
import prometheus_client as prom
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
import logging

# Prometheusメトリクス定義
prediction_latency = prom.Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing prediction',
    buckets=[.001, .01, .1, .5, 1, 2.5, 5, 10]
)

prediction_errors = prom.Counter(
    'model_prediction_errors_total',
    'Total number of prediction errors'
)

model_accuracy = prom.Gauge(
    'model_accuracy',
    'Current model accuracy'
)

data_drift_score = prom.Gauge(
    'data_drift_score',
    'Data drift score',
    ['feature']
)

class ModelMonitor:
    def __init__(self, model, reference_data):
        self.model = model
        self.reference_data = reference_data
        self.predictions_buffer = []
        self.actuals_buffer = []

    @prediction_latency.time()
    def predict_and_monitor(self, X):
        """予測とモニタリング"""
        try:
            prediction = self.model.predict(X)
            self.predictions_buffer.append(prediction)
            return prediction
        except Exception as e:
            prediction_errors.inc()
            logging.error(f"Prediction error: {str(e)}")
            raise

    def add_actual(self, y_true):
        """実際の結果を追加"""
        self.actuals_buffer.append(y_true)

    def calculate_performance_metrics(self):
        """パフォーマンスメトリクスの計算"""
        if len(self.actuals_buffer) < 100:
            return  # 十分なデータが溜まるまで待機

        y_true = np.array(self.actuals_buffer)
        y_pred = np.array(self.predictions_buffer)

        # メトリクス計算
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')

        # Prometheusに送信
        model_accuracy.set(accuracy)

        # アラート条件
        if accuracy < 0.8:
            send_alert(
                "Model accuracy degradation",
                f"Current accuracy: {accuracy:.3f}"
            )

        # バッファクリア
        self.predictions_buffer = []
        self.actuals_buffer = []

    def detect_data_drift(self, current_data):
        """データドリフトの検出"""
        # Evidentlyを使用した詳細なドリフト分析
        report = Report(metrics=[
            DataDriftPreset(),
            TargetDriftPreset()
        ])

        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )

        # レポートをJSON形式で取得
        drift_report = report.as_dict()

        # 各特徴量のドリフトスコアを記録
        for feature, metrics in drift_report['metrics'].items():
            if 'drift_score' in metrics:
                score = metrics['drift_score']
                data_drift_score.labels(feature=feature).set(score)

                if score > 0.5:
                    send_alert(
                        f"Data drift detected in {feature}",
                        f"Drift score: {score:.3f}"
                    )

        return drift_report

    def detect_concept_drift(self):
        """コンセプトドリフトの検出"""
        # モデルの予測分布の変化を監視
        recent_predictions = self.predictions_buffer[-1000:]

        if len(recent_predictions) < 100:
            return

        # 過去の予測分布と比較
        historical_mean = np.mean(self.historical_predictions)
        current_mean = np.mean(recent_predictions)

        # t検定
        from scipy import stats
        statistic, p_value = stats.ttest_ind(
            self.historical_predictions,
            recent_predictions
        )

        if p_value < 0.01:
            send_alert(
                "Concept drift detected",
                f"P-value: {p_value:.6f}"
            )

def send_alert(title, message):
    """アラート送信（Slack、Email等）"""
    # Slack通知
    import requests
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

    payload = {
        'text': f"*{title}*\n{message}",
        'username': 'ML Monitor',
        'icon_emoji': ':robot_face:'
    }

    requests.post(slack_webhook, json=payload)
```

### 7. A/Bテストとカナリアデプロイ

```python
# A/Bテストフレームワーク
import random
from typing import Dict, Any
import json

class ABTestingFramework:
    def __init__(self, models: Dict[str, Any], traffic_split: Dict[str, float]):
        """
        models: {'model_a': model_obj, 'model_b': model_obj}
        traffic_split: {'model_a': 0.5, 'model_b': 0.5}
        """
        self.models = models
        self.traffic_split = traffic_split
        self.results = {model_name: [] for model_name in models.keys()}

    def get_model_for_request(self, user_id: str = None) -> str:
        """リクエストに対してモデルを割り当て"""
        if user_id:
            # ユーザーIDベースの一貫した割り当て
            hash_value = hash(user_id) % 100
            cumulative = 0
            for model_name, split in self.traffic_split.items():
                cumulative += split * 100
                if hash_value < cumulative:
                    return model_name
        else:
            # ランダム割り当て
            return random.choices(
                list(self.traffic_split.keys()),
                weights=list(self.traffic_split.values())
            )[0]

    def predict(self, X, user_id: str = None):
        """A/Bテストを実施して予測"""
        model_name = self.get_model_for_request(user_id)
        model = self.models[model_name]

        prediction = model.predict(X)

        # ログ記録
        self.log_experiment(model_name, X, prediction)

        return prediction, model_name

    def log_experiment(self, model_name, features, prediction):
        """実験結果のログ記録"""
        self.results[model_name].append({
            'timestamp': datetime.now().isoformat(),
            'features': features.tolist(),
            'prediction': prediction.tolist()
        })

    def add_outcome(self, model_name, outcome):
        """実際の結果を追加"""
        if len(self.results[model_name]) > 0:
            self.results[model_name][-1]['outcome'] = outcome

    def analyze_results(self):
        """A/Bテスト結果の統計的分析"""
        from scipy import stats

        results_summary = {}

        for model_name in self.models.keys():
            outcomes = [
                r['outcome'] for r in self.results[model_name]
                if 'outcome' in r
            ]

            if len(outcomes) > 0:
                results_summary[model_name] = {
                    'mean': np.mean(outcomes),
                    'std': np.std(outcomes),
                    'count': len(outcomes)
                }

        # モデル間の比較
        if len(results_summary) == 2:
            model_names = list(results_summary.keys())
            outcomes_a = [r['outcome'] for r in self.results[model_names[0]] if 'outcome' in r]
            outcomes_b = [r['outcome'] for r in self.results[model_names[1]] if 'outcome' in r]

            # t検定
            t_stat, p_value = stats.ttest_ind(outcomes_a, outcomes_b)

            results_summary['statistical_test'] = {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }

        return results_summary

# カナリアデプロイの実装
class CanaryDeployment:
    def __init__(self, stable_model, canary_model, initial_traffic=0.1):
        self.stable_model = stable_model
        self.canary_model = canary_model
        self.canary_traffic = initial_traffic
        self.stable_metrics = []
        self.canary_metrics = []

    def predict(self, X):
        """カナリアトラフィックを考慮した予測"""
        if random.random() < self.canary_traffic:
            # カナリアモデルを使用
            prediction = self.canary_model.predict(X)
            model_used = 'canary'
        else:
            # 安定版モデルを使用
            prediction = self.stable_model.predict(X)
            model_used = 'stable'

        return prediction, model_used

    def record_metrics(self, model_used, latency, error=None):
        """メトリクス記録"""
        metric = {
            'timestamp': time.time(),
            'latency': latency,
            'error': error
        }

        if model_used == 'canary':
            self.canary_metrics.append(metric)
        else:
            self.stable_metrics.append(metric)

    def evaluate_canary(self, window_size=1000):
        """カナリアの評価"""
        if len(self.canary_metrics) < window_size:
            return {'status': 'insufficient_data'}

        recent_stable = self.stable_metrics[-window_size:]
        recent_canary = self.canary_metrics[-window_size:]

        # レイテンシ比較
        stable_latency = np.mean([m['latency'] for m in recent_stable])
        canary_latency = np.mean([m['latency'] for m in recent_canary])

        # エラー率比較
        stable_errors = sum(1 for m in recent_stable if m['error'])
        canary_errors = sum(1 for m in recent_canary if m['error'])

        stable_error_rate = stable_errors / len(recent_stable)
        canary_error_rate = canary_errors / len(recent_canary)

        # 判定
        is_healthy = (
            canary_latency < stable_latency * 1.2 and  # 20%以内の遅延
            canary_error_rate < stable_error_rate * 1.5  # 50%以内のエラー増加
        )

        return {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'stable_latency': stable_latency,
            'canary_latency': canary_latency,
            'stable_error_rate': stable_error_rate,
            'canary_error_rate': canary_error_rate
        }

    def promote_or_rollback(self):
        """カナリアの昇格またはロールバック"""
        evaluation = self.evaluate_canary()

        if evaluation['status'] == 'healthy':
            # 段階的にトラフィックを増加
            self.canary_traffic = min(self.canary_traffic + 0.1, 1.0)

            if self.canary_traffic >= 1.0:
                # 完全に昇格
                self.stable_model = self.canary_model
                return 'promoted'
            return 'increasing_traffic'
        else:
            # ロールバック
            self.canary_traffic = 0
            return 'rolled_back'
```

## MLOpsツールエコシステム

### 実験管理とトラッキング

- **MLflow**: オープンソースの実験管理プラットフォーム
- **Weights & Biases**: クラウドベースの実験トラッキング
- **Neptune.ai**: チーム向け実験管理
- **Comet.ml**: MLライフサイクル管理

### モデルサービング

- **TensorFlow Serving**: TensorFlowモデル専用
- **TorchServe**: PyTorchモデル専用
- **FastAPI**: 汎用的で柔軟なAPI構築
- **BentoML**: モデルサービング特化フレームワーク
- **Seldon Core**: Kubernetes上でのモデルデプロイ

### パイプライン管理

- **Apache Airflow**: 汎用ワークフローオーケストレーション
- **Kubeflow**: Kubernetes上のMLパイプライン
- **Prefect**: モダンなワークフローエンジン
- **Metaflow**: Netflix開発のMLパイプライン

### モニタリング

- **Prometheus + Grafana**: メトリクス収集と可視化
- **Evidently**: MLモデル品質監視
- **Arize**: MLモデル観測性プラットフォーム
- **Fiddler**: モデルパフォーマンス監視

### フィーチャーストア

- **Feast**: オープンソースのフィーチャーストア
- **Tecton**: エンタープライズ向けフィーチャープラットフォーム
- **Hopsworks**: MLデータプラットフォーム

## ベストプラクティス

### 1. バージョン管理の徹底

- コード、データ、モデルのバージョンを全て追跡
- 再現可能な環境（Dockerコンテナ、requirements.txt）
- 実験結果の体系的な記録

### 2. デプロイ戦略

- カナリアデプロイで段階的にリリース
- A/Bテストで新旧モデルを比較
- ロールバック戦略を事前に準備
- Blue-Greenデプロイメントの活用

### 3. 継続的モニタリング

- リアルタイムでのパフォーマンス監視
- データドリフト、コンセプトドリフトの検出
- アラート設定と自動通知
- 定期的なモデル監査

### 4. 自動化

- 再学習トリガーの自動化
- データ品質チェックの自動化
- デプロイプロセスの自動化
- レポート生成の自動化

### 5. セキュリティとコンプライアンス

- モデルへのアクセス制御
- 予測ログの暗号化
- GDPR、個人情報保護法への対応
- 監査ログの保持

## よくある問題とトラブルシューティング

### 問題1: モデルの予測レイテンシが高い

**原因**:

- モデルサイズが大きすぎる
- 前処理が重い
- バッチ処理を活用していない

**解決策**:

```python
# モデル量子化
import torch.quantization

quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# バッチ予測の実装
def predict_batch(requests, batch_size=32):
    predictions = []
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i+batch_size]
        batch_predictions = model.predict(batch)
        predictions.extend(batch_predictions)
    return predictions
```

### 問題2: データドリフトが検出された

**対応手順**:

1. ドリフトの原因を特定（季節性、イベント、システム変更等）
2. 影響範囲を評価（どの特徴量が影響を受けているか）
3. 短期対応（モデルの重み調整、アラート条件の見直し）
4. 長期対応（再学習、特徴量の見直し）

### 問題3: モデルのパフォーマンスが徐々に低下

**チェックリスト**:

- [ ] データ分布の変化を確認
- [ ] 特徴量の欠損率を確認
- [ ] ラベルの質を確認
- [ ] モデルの過学習を確認
- [ ] システムのボトルネックを確認

## 実践的ケーススタディ

### ケース1: ECサイトのレコメンデーションシステム

**課題**: 1日1億リクエストに対応するスケーラブルなシステム

**実装**:

- モデル: LightGBM + 協調フィルタリング
- デプロイ: Kubernetes上で50ポッド
- キャッシング: Redisで頻繁なリクエストを高速化
- A/Bテスト: 新モデルを10%のトラフィックで検証
- 結果: CVR 15%向上、レイテンシ50ms以下

### ケース2: 金融機関の不正検知

**課題**: リアルタイムでの不正トランザクション検出

**実装**:

- モデル: XGBoost + ルールベースのハイブリッド
- ストリーミング: Kafka + Flink
- 再学習: 週次で自動再学習
- モニタリング: False Positive率を重点監視
- 結果: 不正検知率98%、False Positive 0.5%

## 検証ポイント

- [ ] モデルとコードのバージョン管理
- [ ] 自動化されたCI/CDパイプライン
- [ ] 本番環境でのモニタリング
- [ ] データドリフト検出の仕組み
- [ ] 自動再学習のトリガー設定
- [ ] A/Bテストまたはカナリアデプロイ
- [ ] ロールバック手順の確立
- [ ] アラートと通知の設定
- [ ] セキュリティ対策の実装
- [ ] ドキュメントとランブックの整備
