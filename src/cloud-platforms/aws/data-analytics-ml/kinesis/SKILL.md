---
name: aws-kinesis
description: AWS Kinesisを使用してリアルタイムストリーミングデータを収集・処理し、Data Streams、Firehose、Analytics、Enhanced Fan-Outでスケーラブルなデータパイプラインを構築する方法
---

# AWS Kinesis スキル

## 概要

Amazon Kinesisは、リアルタイムストリーミングデータを収集、処理、分析するためのフルマネージドサービスです。Data Streams、Data Firehose、Data Analyticsの3つのサービスで構成され、大規模なストリーミングアプリケーションを構築します。

**重要**: 2025年10月15日以降、Kinesis Data Analytics for SQL Applicationsの新規作成は不可。2026年1月27日に削除予定。Managed Service for Apache Flinkへの移行を推奨。

## 主な使用ケース

### 1. Kinesis Data Streams（基本）

```bash
# ストリーム作成
aws kinesis create-stream \
    --stream-name clickstream \
    --shard-count 2

# ストリーム詳細確認
aws kinesis describe-stream --stream-name clickstream

# On-Demandモード（自動スケーリング、2025年推奨）
aws kinesis create-stream \
    --stream-name clickstream-auto \
    --stream-mode-details StreamMode=ON_DEMAND
```

```python
# Producer（Python SDK）
import boto3
import json
import time

kinesis = boto3.client('kinesis', region_name='ap-northeast-1')

# データ送信
for i in range(100):
    data = {
        'user_id': f'user_{i}',
        'event': 'click',
        'timestamp': int(time.time())
    }

    kinesis.put_record(
        StreamName='clickstream',
        Data=json.dumps(data),
        PartitionKey=data['user_id']
    )

    print(f"Sent record {i}")
    time.sleep(0.1)

# バッチ送信（最大500レコード）
records = [
    {
        'Data': json.dumps({'user_id': f'user_{i}', 'event': 'click'}),
        'PartitionKey': f'user_{i}'
    }
    for i in range(100)
]

kinesis.put_records(
    StreamName='clickstream',
    Records=records
)
```

```python
# Consumer（Python SDK）
import boto3
import json

kinesis = boto3.client('kinesis', region_name='ap-northeast-1')

# Shard Iterator取得
response = kinesis.describe_stream(StreamName='clickstream')
shard_id = response['StreamDescription']['Shards'][0]['ShardId']

shard_iterator = kinesis.get_shard_iterator(
    StreamName='clickstream',
    ShardId=shard_id,
    ShardIteratorType='TRIM_HORIZON'
)['ShardIterator']

# レコード取得
while shard_iterator:
    response = kinesis.get_records(
        ShardIterator=shard_iterator,
        Limit=100
    )

    for record in response['Records']:
        data = json.loads(record['Data'])
        print(f"User: {data['user_id']}, Event: {data['event']}")

    shard_iterator = response['NextShardIterator']
    time.sleep(1)
```

### 2. Enhanced Fan-Out（複数コンシューマ）

```bash
# コンシューマ登録（2MB/秒専用スループット）
aws kinesis register-stream-consumer \
    --stream-arn arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream \
    --consumer-name analytics-app

# コンシューマ一覧
aws kinesis list-stream-consumers \
    --stream-arn arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream
```

```python
# Enhanced Fan-Out Consumer（SubscribeToShard）
import boto3

kinesis = boto3.client('kinesis', region_name='ap-northeast-1')

response = kinesis.subscribe_to_shard(
    ConsumerARN='arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream/consumer/analytics-app:1234567890',
    ShardId='shardId-000000000000',
    StartingPosition={'Type': 'LATEST'}
)

# イベントストリーム処理
for event in response['EventStream']:
    if 'SubscribeToShardEvent' in event:
        for record in event['SubscribeToShardEvent']['Records']:
            data = json.loads(record['Data'])
            print(f"Received: {data}")
```

### 3. Kinesis Data Firehose（S3/Redshift配信）

```bash
# Firehose配信ストリーム作成（S3）
aws firehose create-delivery-stream \
    --delivery-stream-name clickstream-to-s3 \
    --delivery-stream-type DirectPut \
    --s3-destination-configuration '{
        "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
        "BucketARN": "arn:aws:s3:::my-analytics-bucket",
        "Prefix": "clickstream/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
        "ErrorOutputPrefix": "errors/",
        "BufferingHints": {
            "SizeInMBs": 128,
            "IntervalInSeconds": 300
        },
        "CompressionFormat": "GZIP",
        "CloudWatchLoggingOptions": {
            "Enabled": true,
            "LogGroupName": "/aws/kinesisfirehose/clickstream",
            "LogStreamName": "S3Delivery"
        }
    }'

# Data Streamsからの配信
aws firehose create-delivery-stream \
    --delivery-stream-name kinesis-to-s3 \
    --delivery-stream-type KinesisStreamAsSource \
    --kinesis-stream-source-configuration '{
        "KinesisStreamARN": "arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream",
        "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole"
    }' \
    --extended-s3-destination-configuration '{
        "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
        "BucketARN": "arn:aws:s3:::my-analytics-bucket",
        "Prefix": "processed/",
        "BufferingHints": {"SizeInMBs": 128, "IntervalInSeconds": 300},
        "CompressionFormat": "GZIP",
        "DataFormatConversionConfiguration": {
            "SchemaConfiguration": {
                "DatabaseName": "analytics",
                "TableName": "clickstream",
                "Region": "ap-northeast-1",
                "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole"
            },
            "OutputFormatConfiguration": {
                "Serializer": {
                    "ParquetSerDe": {}
                }
            },
            "Enabled": true
        }
    }'
```

### 4. Lambda統合（リアルタイム処理）

```python
# Lambda関数（Kinesis Data Streams トリガー）
import json
import base64

def lambda_handler(event, context):
    for record in event['Records']:
        # Kinesisレコードはbase64エンコード
        payload = base64.b64decode(record['kinesis']['data'])
        data = json.loads(payload)

        # データ処理
        if data['event'] == 'purchase':
            print(f"Purchase: User {data['user_id']}, Amount ${data['amount']}")

            # DynamoDBに保存、SNS通知など

    return {
        'statusCode': 200,
        'body': json.dumps('Processed successfully')
    }
```

```bash
# Lambda EventSourceMapping作成
aws lambda create-event-source-mapping \
    --function-name process-clickstream \
    --event-source-arn arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream \
    --starting-position LATEST \
    --batch-size 100 \
    --maximum-batching-window-in-seconds 10 \
    --parallelization-factor 10 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:ap-northeast-1:123456789012:dlq"
        }
    }'
```

### 5. Managed Service for Apache Flink（旧Kinesis Data Analytics）

```bash
# Flink Application作成
aws kinesisanalyticsv2 create-application \
    --application-name clickstream-analytics \
    --runtime-environment FLINK-1_15 \
    --service-execution-role arn:aws:iam::123456789012:role/KinesisAnalyticsRole \
    --application-configuration '{
        "ApplicationCodeConfiguration": {
            "CodeContent": {
                "S3ContentLocation": {
                    "BucketARN": "arn:aws:s3:::my-flink-bucket",
                    "FileKey": "flink-app.jar"
                }
            },
            "CodeContentType": "ZIPFILE"
        },
        "FlinkApplicationConfiguration": {
            "CheckpointConfiguration": {
                "ConfigurationType": "DEFAULT"
            },
            "MonitoringConfiguration": {
                "ConfigurationType": "CUSTOM",
                "MetricsLevel": "APPLICATION",
                "LogLevel": "INFO"
            }
        }
    }'
```

## ベストプラクティス（2025年版）

### 1. On-Demandモード vs Provisioned

```bash
# On-Demand（2025年推奨、自動スケーリング）
aws kinesis update-stream-mode \
    --stream-arn arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream \
    --stream-mode-details StreamMode=ON_DEMAND

# Provisioned（固定シャード数）
aws kinesis update-stream-mode \
    --stream-arn arn:aws:kinesis:ap-northeast-1:123456789012:stream/clickstream \
    --stream-mode-details StreamMode=PROVISIONED
```

### 2. データ保持期間の設定

```bash
# 7日間保持（デフォルト24時間）
aws kinesis increase-stream-retention-period \
    --stream-name clickstream \
    --retention-period-hours 168

# 最大365日間
aws kinesis increase-stream-retention-period \
    --stream-name clickstream \
    --retention-period-hours 8760
```

### 3. 暗号化の有効化

```bash
# サーバーサイド暗号化（KMS）
aws kinesis start-stream-encryption \
    --stream-name clickstream \
    --encryption-type KMS \
    --key-id alias/kinesis-key
```

### 4. CloudWatch監視

```bash
# メトリクスアラーム設定
aws cloudwatch put-metric-alarm \
    --alarm-name kinesis-write-throttle \
    --metric-name WriteProvisionedThroughputExceeded \
    --namespace AWS/Kinesis \
    --statistic Sum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=StreamName,Value=clickstream \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:ops-alerts
```

### 5. パーティションキーの選択

```python
# 悪い例: 固定値（ホットシャード）
kinesis.put_record(
    StreamName='clickstream',
    Data=json.dumps(data),
    PartitionKey='constant'  # 全データが1シャードに集中
)

# 良い例: 均等分散
import hashlib

partition_key = hashlib.md5(data['user_id'].encode()).hexdigest()
kinesis.put_record(
    StreamName='clickstream',
    Data=json.dumps(data),
    PartitionKey=partition_key
)
```

## よくある失敗パターン

### 1. シャード数過小評価

```text
問題: 1シャード（1MB/秒）で10MB/秒のデータ送信
解決: シャード数を10以上に増やす、またはOn-Demandモード使用

スループット計算:
- 書き込み: 1MB/秒または1,000レコード/秒
- 読み込み: 2MB/秒
```

### 2. GetRecords過剰呼び出し

```text
問題: GetRecordsを無限ループで呼び出し（ReadProvisionedThroughputExceeded）
解決: Enhanced Fan-Out使用、またはsleep追加

# 5回/秒の制限あり
time.sleep(0.2)  # 200ms待機
```

### 3. Firehoseバッファ未調整

```bash
# 悪い例: デフォルト（5MB/300秒）
# 問題: 低スループット時に5分待機

# 良い例: 最小化（1MB/60秒）
aws firehose update-destination \
    --delivery-stream-name clickstream-to-s3 \
    --current-delivery-stream-version-id 1 \
    --destination-id destinationId-1 \
    --s3-destination-update '{
        "BufferingHints": {
            "SizeInMBs": 1,
            "IntervalInSeconds": 60
        }
    }'
```

## リソース

- [Kinesis Data Streams Documentation](https://docs.aws.amazon.com/kinesis/)
- [Best Practices](https://docs.aws.amazon.com/streams/latest/dev/kinesis-record-processor-implementation-app-java.html)
- [Apache Flink Migration Guide](https://docs.aws.amazon.com/kinesisanalytics/latest/java/what-is.html)
