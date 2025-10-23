---
name: aws-cognito
description: AWS Cognitoを使用してユーザー認証とアクセス管理を実装し、User Pools、Identity Pools、ソーシャルログイン、MFAでセキュアなアプリケーションを構築する方法
---

# AWS Cognito スキル

## 概要

Amazon Cognitoは、Webおよびモバイルアプリケーションにユーザー認証、認可、ユーザー管理機能を提供するフルマネージドサービスです。User Pools（認証）とIdentity Pools（認可）の2つのコンポーネントで構成されます。

## 主な使用ケース

### 1. User Pool（ユーザー認証）

```bash
# User Pool作成
aws cognito-idp create-user-pool \
    --pool-name my-app-users \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": true
        }
    }' \
    --auto-verified-attributes email \
    --mfa-configuration OPTIONAL \
    --email-configuration '{
        "EmailSendingAccount": "DEVELOPER",
        "SourceArn": "arn:aws:ses:ap-northeast-1:123456789012:identity/noreply@example.com"
    }' \
    --admin-create-user-config '{
        "AllowAdminCreateUserOnly": false
    }'

# App Client作成
aws cognito-idp create-user-pool-client \
    --user-pool-id ap-northeast-1_ABC123 \
    --client-name web-app \
    --generate-secret \
    --refresh-token-validity 30 \
    --access-token-validity 1 \
    --id-token-validity 1 \
    --token-validity-units '{
        "AccessToken": "hours",
        "IdToken": "hours",
        "RefreshToken": "days"
    }' \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
    --supported-identity-providers COGNITO
```

```python
# Python SDK - ユーザー登録
import boto3

client = boto3.client('cognito-idp', region_name='ap-northeast-1')

# サインアップ
response = client.sign_up(
    ClientId='APP_CLIENT_ID',
    Username='user@example.com',
    Password='SecurePass123!',
    UserAttributes=[
        {'Name': 'email', 'Value': 'user@example.com'},
        {'Name': 'name', 'Value': 'John Doe'}
    ]
)

# 確認コード送信（メールで受信）
client.confirm_sign_up(
    ClientId='APP_CLIENT_ID',
    Username='user@example.com',
    ConfirmationCode='123456'
)

# サインイン
auth_response = client.initiate_auth(
    ClientId='APP_CLIENT_ID',
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': 'user@example.com',
        'PASSWORD': 'SecurePass123!'
    }
)

id_token = auth_response['AuthenticationResult']['IdToken']
access_token = auth_response['AuthenticationResult']['AccessToken']
refresh_token = auth_response['AuthenticationResult']['RefreshToken']
```

### 2. ソーシャルログイン

```bash
# Googleプロバイダー追加
aws cognito-idp create-identity-provider \
    --user-pool-id ap-northeast-1_ABC123 \
    --provider-name Google \
    --provider-type Google \
    --provider-details '{
        "client_id": "GOOGLE_CLIENT_ID",
        "client_secret": "GOOGLE_CLIENT_SECRET",
        "authorize_scopes": "email profile openid"
    }' \
    --attribute-mapping '{
        "email": "email",
        "name": "name",
        "username": "sub"
    }'

# App Clientでソーシャルログイン有効化
aws cognito-idp update-user-pool-client \
    --user-pool-id ap-northeast-1_ABC123 \
    --client-id APP_CLIENT_ID \
    --supported-identity-providers Google COGNITO \
    --callback-urls https://myapp.example.com/callback \
    --logout-urls https://myapp.example.com/logout \
    --allowed-o-auth-flows code \
    --allowed-o-auth-scopes email openid profile \
    --allowed-o-auth-flows-user-pool-client
```

### 3. MFA（多要素認証）

```bash
# MFA必須化
aws cognito-idp set-user-pool-mfa-config \
    --user-pool-id ap-northeast-1_ABC123 \
    --software-token-mfa-configuration Enabled=true \
    --mfa-configuration ON
```

```python
# Python SDK - TOTP MFA設定
# ステップ1: 秘密鍵取得
associate_response = client.associate_software_token(
    AccessToken='ACCESS_TOKEN'
)
secret_code = associate_response['SecretCode']

# ステップ2: ユーザーがTOTPアプリ（Google Authenticatorなど）に登録

# ステップ3: 検証
client.verify_software_token(
    AccessToken='ACCESS_TOKEN',
    UserCode='123456'  # TOTPアプリから取得
)

# ステップ4: MFA有効化
client.set_user_mfa_preference(
    SoftwareTokenMfaSettings={'Enabled': True, 'PreferredMfa': True},
    AccessToken='ACCESS_TOKEN'
)

# ログイン時のMFAチャレンジ応答
auth_response = client.initiate_auth(
    ClientId='APP_CLIENT_ID',
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': 'user@example.com',
        'PASSWORD': 'SecurePass123!'
    }
)

if auth_response['ChallengeName'] == 'SOFTWARE_TOKEN_MFA':
    mfa_response = client.respond_to_auth_challenge(
        ClientId='APP_CLIENT_ID',
        ChallengeName='SOFTWARE_TOKEN_MFA',
        Session=auth_response['Session'],
        ChallengeResponses={
            'USERNAME': 'user@example.com',
            'SOFTWARE_TOKEN_MFA_CODE': '123456'
        }
    )
    id_token = mfa_response['AuthenticationResult']['IdToken']
```

### 4. Identity Pool（AWSリソースアクセス）

```bash
# Identity Pool作成
aws cognito-identity create-identity-pool \
    --identity-pool-name my-app-identities \
    --allow-unauthenticated-identities \
    --cognito-identity-providers ProviderName=cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_ABC123,ClientId=APP_CLIENT_ID

# IAMロール設定
aws cognito-identity set-identity-pool-roles \
    --identity-pool-id ap-northeast-1:12345678-1234-1234-1234-123456789012 \
    --roles '{
        "authenticated": "arn:aws:iam::123456789012:role/Cognito_AuthRole",
        "unauthenticated": "arn:aws:iam::123456789012:role/Cognito_UnauthRole"
    }'
```

```python
# Python SDK - Identity Poolで一時クレデンシャル取得
import boto3

cognito_identity = boto3.client('cognito-identity', region_name='ap-northeast-1')

# ステップ1: Identity ID取得
identity_response = cognito_identity.get_id(
    IdentityPoolId='ap-northeast-1:12345678-1234-1234-1234-123456789012',
    Logins={
        'cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_ABC123': id_token
    }
)
identity_id = identity_response['IdentityId']

# ステップ2: 一時クレデンシャル取得
credentials_response = cognito_identity.get_credentials_for_identity(
    IdentityId=identity_id,
    Logins={
        'cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_ABC123': id_token
    }
)

credentials = credentials_response['Credentials']

# ステップ3: AWSサービスにアクセス
s3 = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretKey'],
    aws_session_token=credentials['SessionToken']
)

# S3バケットにアップロード
s3.upload_file('local.txt', 'my-bucket', 'uploads/file.txt')
```

### 5. Lambda Trigger（カスタムワークフロー）

```bash
# Lambda Trigger設定
aws cognito-idp update-user-pool \
    --user-pool-id ap-northeast-1_ABC123 \
    --lambda-config '{
        "PreSignUp": "arn:aws:lambda:ap-northeast-1:123456789012:function:PreSignUpFunction",
        "PostConfirmation": "arn:aws:lambda:ap-northeast-1:123456789012:function:PostConfirmationFunction",
        "PreAuthentication": "arn:aws:lambda:ap-northeast-1:123456789012:function:PreAuthFunction"
    }'
```

```python
# Lambda関数例（PreSignUp）
def lambda_handler(event, context):
    # ドメイン制限
    email = event['request']['userAttributes']['email']
    if not email.endswith('@example.com'):
        raise Exception('Only @example.com emails allowed')

    # 自動確認（メール確認スキップ）
    event['response']['autoConfirmUser'] = True
    event['response']['autoVerifyEmail'] = True

    return event

# Lambda関数例（PostConfirmation）
def lambda_handler(event, context):
    # DynamoDBにユーザー情報保存
    user_id = event['userName']
    email = event['request']['userAttributes']['email']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    table.put_item(Item={'userId': user_id, 'email': email})

    return event
```

### 6. API Gateway統合

```bash
# API Gateway Cognito Authorizer（前述のAPI Gatewayスキル参照）
aws apigateway create-authorizer \
    --rest-api-id API_ID \
    --name CognitoAuth \
    --type COGNITO_USER_POOLS \
    --provider-arns "arn:aws:cognito-idp:ap-northeast-1:123456789012:userpool/ap-northeast-1_ABC123" \
    --identity-source "method.request.header.Authorization"
```

## ベストプラクティス（2025年版）

### 1. パスワードポリシー強化

```bash
aws cognito-idp update-user-pool \
    --user-pool-id ap-northeast-1_ABC123 \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 12,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": true,
            "TemporaryPasswordValidityDays": 1
        }
    }'
```

### 2. Advanced Security（侵害クレデンシャル保護）

```bash
# Advanced Security有効化
aws cognito-idp set-user-pool-mfa-config \
    --user-pool-id ap-northeast-1_ABC123 \
    --user-pool-add-ons '{
        "AdvancedSecurityMode": "ENFORCED"
    }'

# 侵害されたクレデンシャルを自動検出・ブロック
```

### 3. トークン検証

```python
# JWT検証（Python）
import jwt
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

region = 'ap-northeast-1'
user_pool_id = 'ap-northeast-1_ABC123'
app_client_id = 'APP_CLIENT_ID'

keys_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
keys = requests.get(keys_url).json()['keys']

def verify_token(token):
    # ヘッダーからkid取得
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']

    # 対応する公開鍵取得
    key = [k for k in keys if k['kid'] == kid][0]
    public_key = jwk.construct(key)

    # トークン検証
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

    if not public_key.verify(message.encode('utf-8'), decoded_signature):
        raise Exception('Invalid signature')

    # クレーム検証
    claims = jwt.get_unverified_claims(token)
    if claims['aud'] != app_client_id:
        raise Exception('Invalid audience')

    if claims['iss'] != f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}':
        raise Exception('Invalid issuer')

    return claims
```

### 4. User Poolグループ（RBAC）

```bash
# グループ作成
aws cognito-idp create-group \
    --user-pool-id ap-northeast-1_ABC123 \
    --group-name Admins \
    --description "Administrator group" \
    --role-arn "arn:aws:iam::123456789012:role/CognitoAdminRole" \
    --precedence 1

# ユーザーをグループに追加
aws cognito-idp admin-add-user-to-group \
    --user-pool-id ap-northeast-1_ABC123 \
    --username user@example.com \
    --group-name Admins
```

## よくある失敗パターン

### 1. トークン有効期限の未確認

```text
問題: アクセストークン有効期限切れ（1時間）
解決: リフレッシュトークンで自動更新

# リフレッシュトークンで新しいアクセストークン取得
refresh_response = client.initiate_auth(
    ClientId='APP_CLIENT_ID',
    AuthFlow='REFRESH_TOKEN_AUTH',
    AuthParameters={'REFRESH_TOKEN': refresh_token}
)
```

### 2. User Pool vs Identity Pool混同

```text
User Pool: 認証（サインアップ/サインイン）
Identity Pool: 認可（AWSリソースへのアクセス）

典型的なフロー:
1. User Poolで認証 → IDトークン取得
2. IDトークンをIdentity Poolに渡す → 一時AWS認証情報取得
3. S3/DynamoDBなどにアクセス
```

### 3. CSRF対策未実施

```text
問題: state パラメータ未使用
解決: OAuth 2.0フローでstateパラメータ必須

# 認証リクエスト時にランダムなstateを生成・保存
# コールバック時にstateを検証
```

## リソース

- [Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [User Pools vs Identity Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)
- [JWT Verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
