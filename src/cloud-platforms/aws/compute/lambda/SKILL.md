---
name: "AWS Lambda"
description: "サーバーレスコンピューティング。イベント駆動アーキテクチャ、関数の作成・デプロイ、トリガー設定、パフォーマンス最適化、コスト管理、ベストプラクティスに関する思考プロセスを提供"
---

# AWS Lambda

## このスキルを使う場面

- サーバーレスアプリケーションの構築
- イベント駆動アーキテクチャの実装
- バックエンドAPIの構築
- データ処理パイプラインの自動化
- スケジュールタスクの実行
- リアルタイムファイル処理

## Lambdaとは

AWS Lambdaは、サーバーの管理なしでコードを実行できるサーバーレスコンピューティングサービス。イベントに応答して自動的にコードを実行し、使用したコンピューティング時間に対してのみ課金される。

### Lambdaの主要機能

**サーバーレス実行:**

- サーバーのプロビジョニング・管理不要
- 自動スケーリング
- 高可用性（複数AZで自動実行）

**イベント駆動:**

- 200以上のAWSサービスとSaaSアプリケーションからトリガー
- S3、DynamoDB、API Gateway、EventBridgeなど
- カスタムイベントソース

**柔軟な実行環境:**

- 複数のランタイム（Python, Node.js, Java, Go, .NET, Ruby）
- カスタムランタイム
- コンテナイメージのサポート

**従量課金:**

- リクエスト数と実行時間に基づく課金
- 月100万リクエストと40万GB秒の無料利用枠
- アイドル時の課金なし

## Lambdaの制限（2025年時点）

**実行時間:**
- 最大15分（900秒）
- それ以上必要な場合はECS/EKSやStep Functionsを検討

**メモリ:**
- 128MB〜10,240MB（10GB）
- メモリに比例してCPUも増加

**デプロイパッケージ:**
- Zipファイル：50MB（圧縮時）、250MB（解凍時）
- コンテナイメージ：10GB

**同時実行数:**
- デフォルト：1,000（リージョンごと）
- 上限引き上げ可能

**環境変数:**
- 最大4KB

## 思考プロセス

### フェーズ1: Lambda関数の設計

**ステップ1: ユースケースの明確化**

Lambdaが適しているケース:

- [ ] 短時間の処理（15分以内）
- [ ] イベント駆動型ワークロード
- [ ] 断続的な実行（常時稼働不要）
- [ ] 自動スケーリングが必要
- [ ] サーバー管理を避けたい

Lambdaが適していないケース:

- [ ] 長時間実行（15分以上）
- [ ] 常時稼働が必要
- [ ] 大量のメモリが必要（10GB以上）
- [ ] 低レイテンシが絶対条件（コールドスタート問題）

**ステップ2: ランタイムの選択**

```bash
# 利用可能なランタイムを確認
aws lambda list-runtimes

# 主要なランタイム（2025年）
# - python3.12, python3.11
# - nodejs20.x, nodejs18.x
# - java21, java17
# - dotnet8, dotnet6
# - go1.x
# - ruby3.3, ruby3.2
# - provided.al2023（カスタムランタイム）
```

**ランタイム選択のポイント:**

| 言語 | コールドスタート | 使用場面 |
|-----|--------------|---------|
| Python | 速い | データ処理、スクリプト |
| Node.js | 最速 | API、リアルタイム処理 |
| Java | 遅い | エンタープライズアプリ |
| Go | 速い | 高パフォーマンス |

**ステップ3: メモリとタイムアウトの設定**

```bash
# メモリ設定（128MB〜10,240MB）
# メモリ↑ = CPU↑ = 実行速度↑ = コスト↑

# 推奨アプローチ：
# 1. 512MBから開始
# 2. CloudWatchで実際の使用量を確認
# 3. 必要に応じて調整
```

**移行条件:**

- [ ] ユースケースがLambdaに適していることを確認
- [ ] ランタイムを選択
- [ ] 初期メモリ・タイムアウト設定を決定

### フェーズ2: Lambda関数の作成

**ステップ1: 基本的な関数の作成**

**Python例:**

```python
# lambda_function.py
import json
import boto3
import os

# 環境変数の取得
TABLE_NAME = os.environ.get('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Lambda関数のエントリーポイント

    Args:
        event: イベントデータ
        context: ランタイム情報

    Returns:
        dict: レスポンス
    """
    try:
        # イベントデータの処理
        print(f"Received event: {json.dumps(event)}")

        # ビジネスロジック
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={'id': event['id']})

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response.get('Item', {}))
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Node.js例:**

```javascript
// index.js
const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        console.log('Received event:', JSON.stringify(event, null, 2));

        const params = {
            TableName: process.env.TABLE_NAME,
            Key: { id: event.id }
        };

        const result = await dynamodb.get(params).promise();

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify(result.Item || {})
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
```

**ステップ2: IAMロールの作成**

```bash
# Lambda実行ロールの作成
aws iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'

# 基本実行権限をアタッチ
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# カスタムポリシーの作成（DynamoDBアクセス）
aws iam put-role-policy \
    --role-name lambda-execution-role \
    --policy-name DynamoDBAccess \
    --policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Action": [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ],
        "Resource": "arn:aws:dynamodb:region:account-id:table/MyTable"
      }]
    }'
```

**ステップ3: 関数のデプロイ**

```bash
# Zipファイルの作成
zip function.zip lambda_function.py

# 関数の作成
aws lambda create-function \
    --function-name my-function \
    --runtime python3.12 \
    --role arn:aws:iam::123456789012:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment Variables={TABLE_NAME=MyTable} \
    --tags Environment=Production,Application=MyApp

# 関数の更新
aws lambda update-function-code \
    --function-name my-function \
    --zip-file fileb://function.zip
```

**移行条件:**

- [ ] 関数コードを作成
- [ ] IAMロールを作成
- [ ] 関数をデプロイ
- [ ] 環境変数を設定

### フェーズ3: イベントソースの設定

**ステップ1: API Gatewayトリガー**

```bash
# REST APIの作成
aws apigateway create-rest-api \
    --name my-api \
    --description "My Lambda API"

# Lambda統合の設定（コンソールまたはSAM/CDKで実施が推奨）
```

**ステップ2: S3トリガー**

```bash
# S3イベント通知の設定
aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration '{
      "LambdaFunctionConfigurations": [{
        "LambdaFunctionArn": "arn:aws:lambda:region:account-id:function:my-function",
        "Events": ["s3:ObjectCreated:*"],
        "Filter": {
          "Key": {
            "FilterRules": [{
              "Name": "prefix",
              "Value": "uploads/"
            }, {
              "Name": "suffix",
              "Value": ".jpg"
            }]
          }
        }
      }]
    }'

# Lambdaに権限を付与
aws lambda add-permission \
    --function-name my-function \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket
```

**ステップ3: DynamoDB Streamsトリガー**

```bash
# イベントソースマッピングの作成
aws lambda create-event-source-mapping \
    --function-name my-function \
    --event-source-arn arn:aws:dynamodb:region:account-id:table/MyTable/stream/2025-01-01T00:00:00.000 \
    --starting-position LATEST \
    --batch-size 100
```

**ステップ4: EventBridgeスケジュール**

```bash
# スケジュールルールの作成
aws events put-rule \
    --name daily-cleanup \
    --schedule-expression "cron(0 2 * * ? *)" \
    --state ENABLED

# Lambdaをターゲットに追加
aws events put-targets \
    --rule daily-cleanup \
    --targets "Id"="1","Arn"="arn:aws:lambda:region:account-id:function:my-function"

# Lambdaに権限を付与
aws lambda add-permission \
    --function-name my-function \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:region:account-id:rule/daily-cleanup
```

**移行条件:**

- [ ] イベントソースを設定
- [ ] 必要な権限を付与
- [ ] トリガーをテスト

### フェーズ4: パフォーマンス最適化

**ステップ1: コールドスタートの最小化**

**Provisioned Concurrency（予約済み同時実行数）:**

```bash
# 予約済み同時実行数の設定
aws lambda put-provisioned-concurrency-config \
    --function-name my-function \
    --provisioned-concurrent-executions 5 \
    --qualifier PRODUCTION

# Auto Scalingの設定
aws application-autoscaling register-scalable-target \
    --service-namespace lambda \
    --resource-id function:my-function:PRODUCTION \
    --scalable-dimension lambda:function:ProvisionedConcurrentExecutions \
    --min-capacity 5 \
    --max-capacity 100
```

**コード最適化:**

```python
# ❌ 悪い例：毎回初期化
def lambda_handler(event, context):
    import boto3  # 毎回インポート
    dynamodb = boto3.resource('dynamodb')  # 毎回接続
    # 処理

# ✅ 良い例：グローバルスコープで初期化
import boto3
dynamodb = boto3.resource('dynamodb')  # 1回のみ

def lambda_handler(event, context):
    # 処理（接続を再利用）
```

**ステップ2: メモリの最適化**

```bash
# Lambda Power Tuningで最適なメモリサイズを特定
# https://github.com/alexcasalboni/aws-lambda-power-tuning

# CloudWatchでメモリ使用量を確認
aws logs filter-log-events \
    --log-group-name /aws/lambda/my-function \
    --filter-pattern "Max Memory Used" \
    --limit 10
```

**ステップ3: 依存関係の最小化**

```bash
# Lambda Layersを使用
# 共通ライブラリを分離して再利用

# Layerの作成
mkdir python
pip install requests -t python/
zip -r layer.zip python/

aws lambda publish-layer-version \
    --layer-name my-dependencies \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.12

# 関数にLayerをアタッチ
aws lambda update-function-configuration \
    --function-name my-function \
    --layers arn:aws:lambda:region:account-id:layer:my-dependencies:1
```

**移行条件:**

- [ ] コールドスタート対策を実施
- [ ] メモリサイズを最適化
- [ ] Lambda Layersを活用

### フェーズ5: エラーハンドリングと監視

**ステップ1: リトライとDLQ設定**

```bash
# デッドレターキューの設定
aws lambda update-function-configuration \
    --function-name my-function \
    --dead-letter-config TargetArn=arn:aws:sqs:region:account-id:my-dlq

# 非同期呼び出しの設定
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 2 \
    --maximum-event-age-in-seconds 3600
```

**ステップ2: CloudWatch Logsとメトリクス**

```python
# 構造化ログ
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        'event': 'function_invoked',
        'request_id': context.request_id,
        'user_id': event.get('userId'),
        'timestamp': context.get_remaining_time_in_millis()
    }))

    # 処理

    return {'statusCode': 200}
```

```bash
# カスタムメトリクスの送信
import boto3
cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[{
        'MetricName': 'ProcessedItems',
        'Value': 100,
        'Unit': 'Count'
    }]
)
```

**ステップ3: X-Rayトレーシング**

```bash
# X-Rayトレーシングの有効化
aws lambda update-function-configuration \
    --function-name my-function \
    --tracing-config Mode=Active
```

```python
# X-Ray SDKの使用
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()  # すべてのAWSクライアントを自動的にトレース

@xray_recorder.capture('process_data')
def process_data(data):
    # 処理
    pass

def lambda_handler(event, context):
    process_data(event)
```

**移行条件:**

- [ ] エラーハンドリングを実装
- [ ] DLQを設定
- [ ] ログとメトリクスを設定
- [ ] X-Rayトレーシングを有効化

## イベント駆動アーキテクチャのベストプラクティス

### 1. 同期チェーンを避ける

**❌ 悪い例：**
```
Lambda A (同期呼び出し) → Lambda B → Lambda C
```

**✅ 良い例：**
```
Lambda A → SQS → Lambda B
Lambda A → EventBridge → Lambda C
Lambda A → Step Functions → (Lambda B, C, D)
```

### 2. バッチ処理よりリアルタイム処理

```python
# ❌ 悪い例：1時間ごとにバッチ処理
# 大量データを一度に処理 → タイムアウトリスク

# ✅ 良い例：イベントごとに処理
# S3にファイルアップロード → 即座にLambdaで処理
```

### 3. サービスを活用、コードを減らす

```bash
# EventBridge、SQS、Step Functions、DynamoDB Streamsを活用
# カスタムコードでイベントルーティングを実装しない
```

### 4. 非同期処理の優先

```python
# API Gateway + Lambda（同期）の代わりに
# API Gateway + SQS + Lambda（非同期）
# ユーザーに即座にレスポンスを返し、バックグラウンドで処理
```

### 5. 再帰ループの回避

```python
# ❌ 危険：S3トリガーで同じバケットに書き込み
def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    s3.put_object(Bucket=bucket, Key='output.txt', Body='data')
    # 無限ループ！

# ✅ 安全：別のバケットまたはプレフィックスフィルター使用
def lambda_handler(event, context):
    s3.put_object(Bucket='output-bucket', Key='output.txt', Body='data')
```

## コスト最適化

**1. 適切なメモリサイズ:**

```bash
# メモリ最適化で最大70%のコスト削減可能
# Lambda Power Tuningツールを使用
```

**2. Graviton2（arm64）の使用:**

```bash
# 最大34%のコストパフォーマンス向上
aws lambda update-function-configuration \
    --function-name my-function \
    --architectures arm64
```

**3. 実行時間の短縮:**

```python
# 不要な処理を削除
# 並列処理の活用
# キャッシングの実装
```

**4. 予約済み同時実行数の最適化:**

```bash
# 本当に必要な場合のみ使用
# Auto Scalingで動的に調整
```

## よくある落とし穴

1. **コールドスタートの無視**
   - ❌ コールドスタートを考慮しない設計
   - ✅ Provisioned Concurrencyまたは軽量ランタイムの使用

2. **環境変数での機密情報管理**
   - ❌ 平文で機密情報を保存
   - ✅ Secrets Managerまたはパラメータストアを使用

3. **過剰なメモリ割り当て**
   - ❌ デフォルトで3008MBを割り当て
   - ✅ 実際の使用量に基づいて最適化

4. **エラーハンドリングの欠如**
   - ❌ エラーを無視
   - ✅ try-except、DLQ、リトライ設定

5. **VPC設定の誤用**
   - ❌ 不要なVPC設定（コールドスタート増加）
   - ✅ 必要な場合のみVPC設定

6. **同期チェーン**
   - ❌ Lambda → Lambda → Lambda（同期）
   - ✅ イベント駆動アーキテクチャ（SQS, EventBridge）

## 判断のポイント

### Lambda vs EC2

| 要件 | Lambda | EC2 |
|-----|--------|-----|
| 実行時間 | <15分 | 任意 |
| トラフィック | 断続的 | 常時 |
| スケーリング | 自動 | 手動/Auto Scaling |
| 管理 | なし | あり |
| コスト | 従量課金 | 時間課金 |

### Lambda vs Fargate

| 要件 | Lambda | Fargate |
|-----|--------|---------|
| 起動時間 | ミリ秒 | 秒 |
| 実行時間 | <15分 | 任意 |
| コンテナ | 制限あり | 完全対応 |
| ステート | ステートレス | ステートフル可 |

## 検証ポイント

### 設計

- [ ] ユースケースがLambdaに適している
- [ ] 15分の制限内で処理可能
- [ ] イベント駆動アーキテクチャを設計

### 実装

- [ ] 関数を作成・デプロイ
- [ ] IAMロールを適切に設定
- [ ] 環境変数を設定
- [ ] エラーハンドリングを実装

### パフォーマンス

- [ ] メモリサイズを最適化
- [ ] コールドスタート対策を実施
- [ ] Lambda Layersを活用

### 監視

- [ ] CloudWatch Logsを設定
- [ ] カスタムメトリクスを送信
- [ ] X-Rayトレーシングを有効化
- [ ] アラームを設定

## 他スキルとの連携

### lambda + api-gateway

LambdaとAPI Gatewayの組み合わせ:

1. api-gatewayでREST/HTTP APIを作成
2. lambdaでバックエンドロジックを実装
3. サーバーレスAPIを構築

### lambda + dynamodb

LambdaとDynamoDBの組み合わせ:

1. dynamodbでデータ保存
2. lambdaでCRUD操作
3. DynamoDB Streamsでイベント処理

### lambda + step-functions

LambdaとStep Functionsの組み合わせ:

1. lambdaで個別タスクを実装
2. step-functionsでワークフロー管理
3. 複雑な処理パイプラインを構築

## リソース

### 公式ドキュメント

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)

### ツール

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [Serverless Framework](https://www.serverless.com/)

### 学習リソース

- [AWS Lambda Operator Guide](https://docs.aws.amazon.com/lambda/latest/operatorguide/intro.html)
- [Event-Driven Architecture Patterns](https://aws.amazon.com/blogs/compute/operating-lambda-understanding-event-driven-architecture-part-1/)
