---
name: aws-api-gateway
description: AWS API Gatewayを使用してREST、HTTP、WebSocket APIを構築し、Lambda統合、認証、スロットリング、カスタムドメインで本番APIを運用する方法
---

# AWS API Gateway スキル

## 概要

Amazon API Gatewayは、あらゆる規模のREST、HTTP、WebSocket APIを作成、公開、管理できるフルマネージドサービスです。Lambda統合によるサーバーレスAPI、認証・認可、レート制限、モニタリングを提供します。

## 主な使用ケース

### 1. REST API（フル機能）

```bash
# REST API作成
aws apigateway create-rest-api \
    --name "ProductAPI" \
    --description "Product management API" \
    --endpoint-configuration types=REGIONAL

# リソース作成
ROOT_ID=$(aws apigateway get-resources --rest-api-id API_ID --query 'items[?path==`/`].id' --output text)

aws apigateway create-resource \
    --rest-api-id API_ID \
    --parent-id $ROOT_ID \
    --path-part products

# メソッド作成（GET）
aws apigateway put-method \
    --rest-api-id API_ID \
    --resource-id RESOURCE_ID \
    --http-method GET \
    --authorization-type "AWS_IAM" \
    --api-key-required

# Lambda統合
aws apigateway put-integration \
    --rest-api-id API_ID \
    --resource-id RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-1:123456789012:function:getProducts/invocations"

# デプロイ
aws apigateway create-deployment \
    --rest-api-id API_ID \
    --stage-name production \
    --stage-description "Production environment" \
    --description "Initial deployment"
```

### 2. HTTP API（シンプル・低コスト）

```bash
# HTTP API作成（REST APIの70%コスト削減）
aws apigatewayv2 create-api \
    --name "SimpleAPI" \
    --protocol-type HTTP \
    --target "arn:aws:lambda:ap-northeast-1:123456789012:function:simpleFunction"

# ルート追加
aws apigatewayv2 create-route \
    --api-id API_ID \
    --route-key "GET /products" \
    --target "integrations/INTEGRATION_ID"

# 自動デプロイステージ
aws apigatewayv2 create-stage \
    --api-id API_ID \
    --stage-name '$default' \
    --auto-deploy
```

### 3. WebSocket API（双方向通信）

```bash
# WebSocket API作成
aws apigatewayv2 create-api \
    --name "ChatAPI" \
    --protocol-type WEBSOCKET \
    --route-selection-expression '$request.body.action'

# ルート作成（$connect、$disconnect、カスタム）
aws apigatewayv2 create-route \
    --api-id API_ID \
    --route-key '$connect' \
    --authorization-type AWS_IAM \
    --target "integrations/INTEGRATION_ID"

aws apigatewayv2 create-route \
    --api-id API_ID \
    --route-key 'sendMessage' \
    --target "integrations/INTEGRATION_ID"

# デプロイ
aws apigatewayv2 create-deployment \
    --api-id API_ID \
    --stage-name production
```

```python
# WebSocket Lambda関数例
import json
import boto3

apigateway_client = boto3.client('apigatewaymanagementapi',
    endpoint_url='https://API_ID.execute-api.ap-northeast-1.amazonaws.com/production')

def lambda_handler(event, context):
    route_key = event['requestContext']['routeKey']
    connection_id = event['requestContext']['connectionId']

    if route_key == '$connect':
        # DynamoDBに接続情報保存
        return {'statusCode': 200}

    elif route_key == 'sendMessage':
        body = json.loads(event['body'])
        message = body['message']

        # 全接続にメッセージ送信
        connections = get_all_connections()  # DynamoDBから取得

        for conn_id in connections:
            try:
                apigateway_client.post_to_connection(
                    ConnectionId=conn_id,
                    Data=json.dumps({'message': message})
                )
            except apigateway_client.exceptions.GoneException:
                # 切断済み接続を削除
                delete_connection(conn_id)

        return {'statusCode': 200}

    elif route_key == '$disconnect':
        # DynamoDBから接続情報削除
        return {'statusCode': 200}
```

### 4. 認証・認可

```bash
# Cognito Authorizer（REST API）
aws apigateway create-authorizer \
    --rest-api-id API_ID \
    --name CognitoAuthorizer \
    --type COGNITO_USER_POOLS \
    --provider-arns "arn:aws:cognito-idp:ap-northeast-1:123456789012:userpool/ap-northeast-1_ABC123" \
    --identity-source "method.request.header.Authorization"

# Lambda Authorizer（カスタム認証）
aws apigateway create-authorizer \
    --rest-api-id API_ID \
    --name CustomAuthorizer \
    --type TOKEN \
    --authorizer-uri "arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/arn:aws:lambda:ap-northeast-1:123456789012:function:authFunction/invocations" \
    --identity-source "method.request.header.Authorization" \
    --authorizer-result-ttl-in-seconds 300
```

```python
# Lambda Authorizer関数
def lambda_handler(event, context):
    token = event['authorizationToken']

    # トークン検証ロジック
    if validate_token(token):
        return generate_policy('user123', 'Allow', event['methodArn'])
    else:
        return generate_policy('user123', 'Deny', event['methodArn'])

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
```

### 5. スロットリングとAPIキー

```bash
# 使用プラン作成
aws apigateway create-usage-plan \
    --name "BasicPlan" \
    --throttle burstLimit=200,rateLimit=100 \
    --quota limit=10000,period=MONTH \
    --api-stages apiId=API_ID,stage=production

# APIキー作成
aws apigateway create-api-key \
    --name "ClientApp1" \
    --enabled

# 使用プランとAPIキーを関連付け
aws apigateway create-usage-plan-key \
    --usage-plan-id PLAN_ID \
    --key-id KEY_ID \
    --key-type API_KEY
```

### 6. カスタムドメイン

```bash
# カスタムドメイン作成
aws apigateway create-domain-name \
    --domain-name api.example.com \
    --regional-certificate-arn "arn:aws:acm:ap-northeast-1:123456789012:certificate/abc-123" \
    --endpoint-configuration types=REGIONAL

# ベースパスマッピング
aws apigateway create-base-path-mapping \
    --domain-name api.example.com \
    --rest-api-id API_ID \
    --stage production \
    --base-path v1

# Route 53レコード作成
aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456 \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "api.example.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "d-abc123.execute-api.ap-northeast-1.amazonaws.com",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'
```

## ベストプラクティス（2025年版）

### 1. REST API vs HTTP API選択

```text
REST API推奨ケース:
- APIキー・使用プラン必要
- クライアント毎のスロットリング
- リクエストバリデーション
- AWS WAF統合
- Private API（VPC内部）

HTTP API推奨ケース（2025年デフォルト）:
- シンプルなLambda/HTTP統合
- コスト最小化（REST APIの70%削減）
- OIDC/OAuth 2.0認証
- CORS自動設定
- 低レイテンシ
```

### 2. Lambda Proxy統合

```python
# Lambda関数（API Gateway Proxy統合）
def lambda_handler(event, context):
    # event['body']にリクエストボディ
    # event['headers']にヘッダー
    # event['queryStringParameters']にクエリパラメータ

    body = json.loads(event['body'])

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Success',
            'data': process_data(body)
        })
    }
```

### 3. WebSocket接続管理

```python
# DynamoDBで接続管理
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('WebSocketConnections')

def save_connection(connection_id, user_id):
    table.put_item(
        Item={
            'connectionId': connection_id,
            'userId': user_id,
            'timestamp': int(time.time())
        }
    )

def get_connections_by_user(user_id):
    response = table.query(
        IndexName='UserIdIndex',
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id}
    )
    return [item['connectionId'] for item in response['Items']]
```

### 4. エラーハンドリング

```bash
# Gateway Responseカスタマイズ
aws apigateway update-gateway-response \
    --rest-api-id API_ID \
    --response-type DEFAULT_4XX \
    --patch-operations '[
        {
            "op": "replace",
            "path": "/responseTemplates/application~1json",
            "value": "{\"error\": \"$context.error.message\", \"requestId\": \"$context.requestId\"}"
        }
    ]'
```

### 5. CloudWatch Logs有効化

```bash
# アクセスログ設定
aws apigateway update-stage \
    --rest-api-id API_ID \
    --stage-name production \
    --patch-operations '[
        {
            "op": "replace",
            "path": "/accessLogSettings/destinationArn",
            "value": "arn:aws:logs:ap-northeast-1:123456789012:log-group:/aws/apigateway/ProductAPI"
        },
        {
            "op": "replace",
            "path": "/accessLogSettings/format",
            "value": "$context.requestId $context.error.message $context.status"
        }
    ]'

# メトリクス詳細有効化
aws apigateway update-stage \
    --rest-api-id API_ID \
    --stage-name production \
    --patch-operations '[
        {
            "op": "replace",
            "path": "/*/*/metrics/enabled",
            "value": "true"
        }
    ]'
```

## よくある失敗パターン

### 1. Lambda統合タイムアウト

```text
問題: API Gatewayタイムアウト（29秒）
解決: 長時間処理はStep FunctionsまたはSQS + 非同期処理

# Lambda関数で即座にレスポンス
return {'statusCode': 202, 'body': 'Processing started'}

# SQSにメッセージ送信して別Lambdaで処理
```

### 2. CORS未設定

```bash
# OPTIONS メソッド作成（プリフライト）
aws apigateway put-method \
    --rest-api-id API_ID \
    --resource-id RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE

# Mock統合でCORSヘッダー返却
aws apigateway put-integration-response \
    --rest-api-id API_ID \
    --resource-id RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{
        "method.response.header.Access-Control-Allow-Headers": "'\''Content-Type,X-Amz-Date,Authorization'\''",
        "method.response.header.Access-Control-Allow-Methods": "'\''GET,POST,OPTIONS'\''",
        "method.response.header.Access-Control-Allow-Origin": "'\''*'\''"
    }'
```

### 3. WebSocket接続リーク

```text
問題: $disconnectイベントで削除されない接続がDynamoDBに残る
解決: TTLまたは定期的なクリーンアップLambda

# DynamoDB TTL有効化
aws dynamodb update-time-to-live \
    --table-name WebSocketConnections \
    --time-to-live-specification "Enabled=true, AttributeName=ttl"
```

## リソース

- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [HTTP API vs REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)
- [WebSocket API Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html)
