---
name: aws-microservices
description: AWSでマイクロサービスアーキテクチャを実装し、EventBridge、SNS/SQS、API Gateway、サービスメッシュでイベント駆動の分散システムを構築する方法
---

# AWS Microservices Architecture スキル

## 概要

マイクロサービスアーキテクチャは、アプリケーションを小さな独立したサービスに分割し、各サービスが独自のビジネス機能を担当する設計パターンです。AWSのサーバーレスサービスとイベント駆動アーキテクチャを組み合わせて実装します。

## 主な使用ケース

### 1. イベント駆動アーキテクチャ（EventBridge）

```bash
# EventBusの作成
aws events create-event-bus --name microservices-bus

# ルール作成（注文サービス → 在庫サービス）
aws events put-rule \
    --name order-created-rule \
    --event-bus-name microservices-bus \
    --event-pattern '{
        "source": ["order-service"],
        "detail-type": ["Order Created"],
        "detail": {
            "status": ["pending"]
        }
    }'

# ターゲット設定（Lambda）
aws events put-targets \
    --rule order-created-rule \
    --event-bus-name microservices-bus \
    --targets '[{
        "Id": "1",
        "Arn": "arn:aws:lambda:ap-northeast-1:123456789012:function:inventory-service",
        "RetryPolicy": {"MaximumRetryAttempts": 2}
    }]'
```

```python
# Producer（Order Service）
import boto3
import json

eventbridge = boto3.client('events')

def create_order(order_data):
    # 注文処理...

    # イベント発行
    eventbridge.put_events(
        Entries=[{
            'Source': 'order-service',
            'DetailType': 'Order Created',
            'Detail': json.dumps({
                'orderId': '12345',
                'customerId': 'user123',
                'items': [{'sku': 'ABC-001', 'quantity': 2}],
                'status': 'pending'
            }),
            'EventBusName': 'microservices-bus'
        }]
    )

# Consumer（Inventory Service）
def lambda_handler(event, context):
    detail = event['detail']
    order_id = detail['orderId']
    items = detail['items']

    # 在庫確認・予約処理
    reserve_inventory(items)

    # 完了イベント発行
    eventbridge.put_events(
        Entries=[{
            'Source': 'inventory-service',
            'DetailType': 'Inventory Reserved',
            'Detail': json.dumps({
                'orderId': order_id,
                'status': 'reserved'
            }),
            'EventBusName': 'microservices-bus'
        }]
    )
```

### 2. Pub/Sub パターン（SNS + SQS）

```bash
# SNSトピック作成
aws sns create-topic --name order-events

# SQSキュー作成（各マイクロサービス用）
aws sqs create-queue --queue-name inventory-service-queue
aws sqs create-queue --queue-name notification-service-queue
aws sqs create-queue --queue-name analytics-service-queue

# サブスクリプション作成
aws sns subscribe \
    --topic-arn arn:aws:sns:ap-northeast-1:123456789012:order-events \
    --protocol sqs \
    --notification-endpoint arn:aws:sqs:ap-northeast-1:123456789012:inventory-service-queue

# SQS権限追加
aws sqs set-queue-attributes \
    --queue-url https://sqs.ap-northeast-1.amazonaws.com/123456789012/inventory-service-queue \
    --attributes '{
        "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"sqs:SendMessage\",\"Resource\":\"arn:aws:sqs:ap-northeast-1:123456789012:inventory-service-queue\",\"Condition\":{\"ArnEquals\":{\"aws:SourceArn\":\"arn:aws:sns:ap-northeast-1:123456789012:order-events\"}}}]}"
    }'
```

```python
# Producer（SNS発行）
import boto3
import json

sns = boto3.client('sns')

def publish_order_event(order_data):
    sns.publish(
        TopicArn='arn:aws:sns:ap-northeast-1:123456789012:order-events',
        Message=json.dumps(order_data),
        Subject='Order Created',
        MessageAttributes={
            'event_type': {'DataType': 'String', 'StringValue': 'order_created'},
            'order_id': {'DataType': 'String', 'StringValue': order_data['orderId']}
        }
    )

# Consumer（SQSポーリング）
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.ap-northeast-1.amazonaws.com/123456789012/inventory-service-queue'

def process_messages():
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20  # Long Polling
    )

    for message in response.get('Messages', []):
        body = json.loads(message['Body'])
        event_data = json.loads(body['Message'])

        # イベント処理
        process_order_event(event_data)

        # メッセージ削除
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
```

### 3. API Gateway + Lambda（サービス境界）

```bash
# API Gateway作成（各マイクロサービス用）
aws apigatewayv2 create-api \
    --name order-service-api \
    --protocol-type HTTP \
    --cors-configuration '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowHeaders": ["Content-Type", "Authorization"]
    }'

# Lambda統合
aws apigatewayv2 create-integration \
    --api-id API_ID \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:ap-northeast-1:123456789012:function:order-service" \
    --payload-format-version "2.0"

# ルート作成
aws apigatewayv2 create-route \
    --api-id API_ID \
    --route-key "POST /orders" \
    --target "integrations/INTEGRATION_ID"

# ステージ作成
aws apigatewayv2 create-stage \
    --api-id API_ID \
    --stage-name production \
    --auto-deploy
```

### 4. サービスメッシュ（AWS App Mesh）

```bash
# App Mesh作成
aws appmesh create-mesh --mesh-name microservices-mesh

# Virtual Service作成（Order Service）
aws appmesh create-virtual-service \
    --mesh-name microservices-mesh \
    --virtual-service-name order-service.local \
    --spec '{
        "provider": {
            "virtualNode": {"virtualNodeName": "order-service-node"}
        }
    }'

# Virtual Node作成
aws appmesh create-virtual-node \
    --mesh-name microservices-mesh \
    --virtual-node-name order-service-node \
    --spec '{
        "listeners": [{
            "portMapping": {"port": 8080, "protocol": "http"}
        }],
        "serviceDiscovery": {
            "awsCloudMap": {
                "serviceName": "order-service",
                "namespaceName": "microservices.local"
            }
        },
        "backends": [{
            "virtualService": {"virtualServiceName": "inventory-service.local"}
        }]
    }'
```

### 5. データ管理（Database per Service）

```bash
# 各サービス専用のDynamoDBテーブル
aws dynamodb create-table \
    --table-name OrderService \
    --attribute-definitions \
        AttributeName=orderId,AttributeType=S \
    --key-schema AttributeName=orderId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
    --table-name InventoryService \
    --attribute-definitions \
        AttributeName=sku,AttributeType=S \
    --key-schema AttributeName=sku,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
    --table-name CustomerService \
    --attribute-definitions \
        AttributeName=customerId,AttributeType=S \
    --key-schema AttributeName=customerId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### 6. Saga パターン（分散トランザクション）

```python
# Orchestration Saga（中央コーディネータ）
import boto3
import json

stepfunctions = boto3.client('stepfunctions')

def start_order_saga(order_data):
    stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:ap-northeast-1:123456789012:stateMachine:order-saga',
        input=json.dumps(order_data)
    )

# Step Functions定義（ASL）
{
  "Comment": "Order Saga",
  "StartAt": "ReserveInventory",
  "States": {
    "ReserveInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:inventory-reserve",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "SagaFailed"
      }],
      "Next": "ChargePayment"
    },
    "ChargePayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:payment-charge",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "CompensateInventory"
      }],
      "Next": "ShipOrder"
    },
    "ShipOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:shipping-create",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "CompensatePayment"
      }],
      "End": true
    },
    "CompensateInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:inventory-release",
      "Next": "SagaFailed"
    },
    "CompensatePayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:payment-refund",
      "Next": "CompensateInventory"
    },
    "SagaFailed": {
      "Type": "Fail"
    }
  }
}
```

## ベストプラクティス（2025年版）

### 1. イベント駆動アーキテクチャ推奨

```text
EventBridge優先ケース:
- SaaS統合必要
- スキーマバリデーション
- ルールベースルーティング
- イベントリプレイ機能

SNS/SQS優先ケース:
- 高スループット（> 10,000 msg/秒）
- FIFO保証必要
- 低レイテンシ（< 100ms）
- 既存SNS/SQS実装
```

### 2. サービス分離原則

```text
1. ビジネス機能単位
   - Order Service: 注文管理
   - Inventory Service: 在庫管理
   - Payment Service: 決済処理

2. Database per Service
   - 各サービスが独自のデータストア
   - 直接的なDB共有禁止

3. API境界明確化
   - RESTful API設計
   - バージョニング（/v1/、/v2/）
```

### 3. 非同期通信優先

```python
# 同期呼び出し（避ける）
response = requests.post('https://inventory-service/reserve', data=order_data)
if response.status_code != 200:
    raise Exception('Inventory reservation failed')

# 非同期イベント（推奨）
eventbridge.put_events(
    Entries=[{
        'Source': 'order-service',
        'DetailType': 'Inventory Reservation Requested',
        'Detail': json.dumps(order_data)
    }]
)
# 結果はイベントで受信
```

### 4. Idempotency（冪等性）

```python
# DynamoDBでIdempotency Key管理
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IdempotencyKeys')

def process_event_idempotent(event_id, handler_func):
    try:
        # Idempotency Key登録（条件付き書き込み）
        table.put_item(
            Item={
                'eventId': event_id,
                'processedAt': int(time.time()),
                'ttl': int(time.time()) + 86400  # 24時間後に削除
            },
            ConditionExpression='attribute_not_exists(eventId)'
        )

        # イベント処理
        handler_func()

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # 既に処理済み
            print(f'Event {event_id} already processed')
            return
        raise
```

### 5. Circuit Breaker（障害分離）

```python
# PyBreaker ライブラリ使用
from pybreaker import CircuitBreaker

# Circuit Breaker設定
breaker = CircuitBreaker(
    fail_max=5,  # 5回失敗でOpen
    timeout_duration=60  # 60秒後にHalf-Open
)

@breaker
def call_external_service(data):
    response = requests.post('https://payment-service/charge', json=data)
    response.raise_for_status()
    return response.json()

# 使用
try:
    result = call_external_service(payment_data)
except CircuitBreakerError:
    # Fallback処理
    save_to_queue_for_retry(payment_data)
```

## よくある失敗パターン

### 1. 分散モノリス

```text
問題: マイクロサービス間の同期呼び出し多用
解決: イベント駆動アーキテクチャ採用

悪い例:
Order -> Inventory -> Payment -> Shipping（同期チェーン）

良い例:
Order -> [EventBridge] -> (Inventory, Payment, Shipping並列処理)
```

### 2. 共有データベース

```text
問題: 全サービスが同じRDSに接続
解決: Database per Service

各サービス:
- Order Service -> OrderDB（DynamoDB）
- Inventory Service -> InventoryDB（DynamoDB）
- Customer Service -> CustomerDB（RDS）
```

### 3. 過度な細分化

```text
問題: 機能毎に数百のマイクロサービス
解決: ドメイン境界を適切に設定

推奨サービス粒度:
- チーム単位（5〜10人）で管理可能
- ビジネス機能の完結性
- デプロイ独立性
```

## リソース

- [Event-Driven Architecture](https://aws.amazon.com/event-driven-architecture/)
- [Microservices on AWS](https://aws.amazon.com/microservices/)
- [AWS App Mesh](https://aws.amazon.com/app-mesh/)
