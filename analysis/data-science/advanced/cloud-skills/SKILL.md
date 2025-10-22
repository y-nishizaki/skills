---
name: "クラウドスキル"
description: "AWS、GCP、Azureでのデータ分析環境構築とスケーラブルな運用"
---

# クラウドスキル: クラウドネイティブなデータ分析

## このスキルを使う場面

- スケーラブルな分析環境が必要
- インフラ管理を自動化したい
- チームでリソースを共有したい
- コストを最適化したい

## 主要クラウドサービス

### AWS

```python
# S3からデータ読み込み
import boto3
import pandas as pd

s3 = boto3.client('s3')
obj = s3.get_object(Bucket='my-bucket', Key='data.csv')
df = pd.read_csv(obj['Body'])

# SageMaker で機械学習
from sagemaker import Session
from sagemaker.estimator import Estimator

estimator = Estimator(
    image_uri="training-image",
    role="SageMakerRole",
    instance_count=1,
    instance_type='ml.m5.xlarge'
)
estimator.fit({'training': 's3://bucket/data'})
```


### GCP

```python
# BigQuery
from google.cloud import bigquery

client = bigquery.Client()
query = """
    SELECT * FROM `project.dataset.table`
    WHERE date >= '2024-01-01'
"""
df = client.query(query).to_dataframe()

# Vertex AI
from google.cloud import aiplatform
aiplatform.init(project="my-project")
```


### Azure

```python
# Azure ML
from azureml.core import Workspace, Experiment

ws = Workspace.from_config()
experiment = Experiment(workspace=ws, name="my-experiment")
```


## 主要サービス

**ストレージ**: S3, Cloud Storage, Blob Storage
**データウェアハウス**: Redshift, BigQuery, Synapse
**機械学習**: SageMaker, Vertex AI, Azure ML
**コンピューティング**: EC2, Compute Engine, VM
**コンテナ**: ECS/EKS, GKE, AKS

## ベストプラクティス

- Infrastructure as Code (Terraform, CloudFormation)
- コスト監視と最適化
- セキュリティ設定
- 自動スケーリング
- バックアップ戦略

## 検証ポイント

- [ ] 適切なサービスを選択した
- [ ] セキュリティを確保した
- [ ] コストを最適化した
- [ ] 可用性を確保した
