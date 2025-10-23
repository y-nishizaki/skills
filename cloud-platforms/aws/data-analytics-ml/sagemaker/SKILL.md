---
name: aws-sagemaker
description: AWS SageMakerを使用して機械学習モデルの構築、トレーニング、デプロイを実行し、Serverless Inference、Multi-Model Endpoint、A/Bテストで本番運用する方法
---

# AWS SageMaker スキル

## 概要

Amazon SageMakerは、機械学習モデルの構築、トレーニング、デプロイを統合的に提供するフルマネージド機械学習サービスです。Jupyter NotebooksからMLOpsパイプラインまで、エンドツーエンドのML開発を支援します。

## 主な使用ケース

### 1. SageMaker Notebookでモデル開発

```python
# notebook_example.py
import sagemaker
from sagemaker import get_execution_role
from sagemaker.sklearn.estimator import SKLearn

role = get_execution_role()
session = sagemaker.Session()

# S3にトレーニングデータをアップロード
train_data = session.upload_data(
    path='data/train.csv',
    bucket='my-ml-bucket',
    key_prefix='sagemaker/training'
)

# Estimator定義（scikit-learn）
sklearn_estimator = SKLearn(
    entry_point='train.py',
    role=role,
    instance_type='ml.m5.xlarge',
    framework_version='1.2-1',
    py_version='py3',
    hyperparameters={
        'n_estimators': 100,
        'max_depth': 5
    }
)

# トレーニング実行
sklearn_estimator.fit({'train': train_data})
```

```python
# train.py (エントリポイント)
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=5)
    args, _ = parser.parse_known_args()

    # データ読み込み
    train_data = pd.read_csv('/opt/ml/input/data/train/train.csv')
    X = train_data.drop('target', axis=1)
    y = train_data['target']

    # モデルトレーニング
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    model.fit(X, y)

    # モデル保存
    joblib.dump(model, '/opt/ml/model/model.joblib')
```

### 2. リアルタイム推論エンドポイント

```python
# エンドポイントデプロイ
predictor = sklearn_estimator.deploy(
    initial_instance_count=2,
    instance_type='ml.m5.large',
    endpoint_name='sklearn-endpoint'
)

# 推論実行
import numpy as np

test_data = np.array([[5.1, 3.5, 1.4, 0.2]])
prediction = predictor.predict(test_data)
print(prediction)

# エンドポイント削除
predictor.delete_endpoint()
```

```bash
# AWS CLI経由での推論
echo '[5.1, 3.5, 1.4, 0.2]' > input.json

aws sagemaker-runtime invoke-endpoint \
    --endpoint-name sklearn-endpoint \
    --body fileb://input.json \
    --content-type application/json \
    output.json

cat output.json
```

### 3. Serverless Inference（2025年推奨）

```python
from sagemaker.serverless import ServerlessInferenceConfig

# Serverlessエンドポイント作成
serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=4096,
    max_concurrency=20
)

predictor = sklearn_estimator.deploy(
    serverless_inference_config=serverless_config,
    endpoint_name='sklearn-serverless'
)
```

### 4. Multi-Model Endpoint（コスト最適化）

```python
from sagemaker.multidatamodel import MultiDataModel

# 複数モデルを1エンドポイントでホスト
multi_model = MultiDataModel(
    name='multi-model-endpoint',
    model_data_prefix='s3://my-ml-bucket/models/',
    image_uri=sklearn_estimator.image_uri,
    role=role,
    sagemaker_session=session
)

predictor = multi_model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.xlarge',
    endpoint_name='multi-model-endpoint'
)

# 特定モデルで推論
prediction = predictor.predict(
    data=test_data,
    target_model='model-v1.tar.gz'
)
```

### 5. A/Bテスト

```python
from sagemaker.session import production_variant

# 2つのモデルバリアント
variant1 = production_variant(
    model_name='model-v1',
    instance_type='ml.m5.large',
    initial_instance_count=1,
    variant_name='ModelV1',
    initial_weight=70
)

variant2 = production_variant(
    model_name='model-v2',
    instance_type='ml.m5.large',
    initial_instance_count=1,
    variant_name='ModelV2',
    initial_weight=30
)

# エンドポイント作成（70% v1、30% v2）
session.create_endpoint(
    endpoint_name='ab-test-endpoint',
    config_name='ab-test-config',
    production_variants=[variant1, variant2]
)
```

### 6. Batch Transform（バッチ推論）

```python
# バッチ変換ジョブ
transformer = sklearn_estimator.transformer(
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path='s3://my-ml-bucket/batch-output/'
)

transformer.transform(
    data='s3://my-ml-bucket/batch-input/',
    content_type='text/csv',
    split_type='Line'
)

transformer.wait()
```

## ベストプラクティス（2025年版）

### 1. エンドポイント選択ガイド

```text
Serverless Inference:
- 断続的なトラフィック
- アイドル時間が長い
- コールドスタート許容（数秒）
- 例: 週次レポート生成、不定期な予測

Real-time Endpoint:
- 低レイテンシ必須（< 100ms）
- 継続的なトラフィック
- SLA要件厳しい
- 例: リアルタイム不正検出、レコメンデーション

Batch Transform:
- 大量データの一括推論
- リアルタイム性不要
- コスト最小化
- 例: 全顧客スコアリング、日次予測
```

### 2. マルチAZ高可用性

```python
# 複数AZにインスタンス配置
predictor = model.deploy(
    initial_instance_count=3,  # 最小2以上推奨
    instance_type='ml.m5.xlarge',
    endpoint_name='ha-endpoint'
)
```

### 3. Auto Scaling設定

```bash
# Application Auto Scaling設定
aws application-autoscaling register-scalable-target \
    --service-namespace sagemaker \
    --resource-id endpoint/sklearn-endpoint/variant/AllTraffic \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --min-capacity 2 \
    --max-capacity 10

# スケーリングポリシー
aws application-autoscaling put-scaling-policy \
    --service-namespace sagemaker \
    --resource-id endpoint/sklearn-endpoint/variant/AllTraffic \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --policy-name target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
        },
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'
```

### 4. モデルモニタリング

```python
from sagemaker.model_monitor import DataCaptureConfig, DefaultModelMonitor

# データキャプチャ有効化
data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri='s3://my-ml-bucket/data-capture'
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.xlarge',
    data_capture_config=data_capture_config
)

# モデルモニター設定
monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600
)

monitor.suggest_baseline(
    baseline_dataset='s3://my-ml-bucket/baseline/train.csv',
    dataset_format={'csv': {'header': True}}
)

monitor.create_monitoring_schedule(
    endpoint_input=predictor.endpoint_name,
    output_s3_uri='s3://my-ml-bucket/monitoring-output',
    schedule_cron_expression='cron(0 * * * ? *)'  # 毎時
)
```

### 5. コスト最適化

```python
# Reserved Instances（75%削減）
# コンソールまたはAWS営業経由で購入

# Spot Instancesでトレーニング（70%削減）
sklearn_estimator = SKLearn(
    entry_point='train.py',
    role=role,
    instance_type='ml.m5.xlarge',
    use_spot_instances=True,
    max_wait=7200,
    max_run=3600
)
```

## よくある失敗パターン

### 1. 単一AZ配置

```text
問題: initial_instance_count=1
解決: 最小2以上で複数AZ配置

# 悪い例
predictor = model.deploy(initial_instance_count=1)

# 良い例
predictor = model.deploy(initial_instance_count=2)
```

### 2. Auto Scaling未設定

```text
問題: 固定インスタンス数でトラフィック急増時に対応できない
解決: Target Tracking Scalingで自動スケール
```

### 3. Shadow Test未実施

```python
# 新モデルをShadow Modeでテスト
shadow_variant = production_variant(
    model_name='model-v2',
    instance_type='ml.m5.large',
    initial_instance_count=1,
    variant_name='Shadow',
    initial_weight=0  # トラフィック0%
)

# 本番トラフィックをコピーしてShadowに送信
# CloudWatchでメトリクス比較
```

## リソース

- [SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Deployment Best Practices](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-best-practices.html)
- [SageMaker Examples](https://github.com/aws/amazon-sagemaker-examples)
