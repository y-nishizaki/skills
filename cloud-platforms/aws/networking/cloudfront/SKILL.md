---
name: aws-cloudfront
description: AWS CloudFrontを使用してグローバルCDNを構築し、Origin Shield、キャッシュ動作、Lambda@Edgeを活用してコンテンツ配信を最適化する方法
---

# AWS CloudFront スキル

## 概要

Amazon CloudFrontは、低レイテンシでコンテンツを配信するグローバルCDN（Content Delivery Network）サービスです。450以上のエッジロケーション、Origin Shield、Lambda@Edgeを活用して、高速かつセキュアなコンテンツ配信を実現します。

### 2025年の重要なアップデート

- **Origin Shield**: 57%のオリジン負荷削減
- **Cache Policies**: 再利用可能なキャッシュ設定
- **CloudFront Functions**: エッジでの軽量処理（$0.10/100万リクエスト）
- **料金**: リージョン別、最安$0.085/GB（米国/欧州）

## 主な使用ケース

### 1. S3静的サイトの配信

S3バケットをオリジンとしてWebサイトを配信します。

```bash
# CloudFrontディストリビューションの作成
aws cloudfront create-distribution \
    --distribution-config file://distribution-config.json

# distribution-config.json
cat > distribution-config.json << 'EOF'
{
  "CallerReference": "static-site-2025-01-22",
  "Comment": "Static website distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "S3-my-static-site",
      "DomainName": "my-static-site.s3.ap-northeast-1.amazonaws.com",
      "S3OriginConfig": {
        "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEFG1234567"
      }
    }]
  },
  "DefaultRootObject": "index.html",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-my-static-site",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "Compress": true
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/12345678",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Aliases": {
    "Quantity": 1,
    "Items": ["www.example.com"]
  }
}
EOF

# Origin Access Identity（OAI）の作成
aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config \
        CallerReference="$(date +%s)",Comment="OAI for my-static-site"

# S3バケットポリシー（CloudFrontのみアクセス許可）
cat > s3-bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontOAI",
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ABCDEFG1234567"
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-static-site/*"
  }]
}
EOF

aws s3api put-bucket-policy \
    --bucket my-static-site \
    --policy file://s3-bucket-policy.json
```

### 2. Origin Shield（高負荷対策）

オリジンの負荷を最大57%削減します。

```bash
# Origin Shieldを有効化
cat > origin-shield-config.json << 'EOF'
{
  "CallerReference": "api-distribution-2025",
  "Comment": "API distribution with Origin Shield",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "ALB-Origin",
      "DomainName": "api-alb-123456.ap-northeast-1.elb.amazonaws.com",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "https-only",
        "OriginSslProtocols": {
          "Quantity": 1,
          "Items": ["TLSv1.2"]
        }
      },
      "OriginShield": {
        "Enabled": true,
        "OriginShieldRegion": "ap-northeast-1"
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "ALB-Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    },
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  }
}
EOF

aws cloudfront create-distribution --distribution-config file://origin-shield-config.json
```

**Origin Shieldの効果**:
- オリジン負荷: 57%削減
- レイテンシ: 67%改善（P90）
- コスト: わずかな追加料金（$0.01/10,000リクエスト）

### 3. キャッシュポリシー（再利用可能）

カスタムキャッシュポリシーを作成します。

```bash
# キャッシュポリシーの作成
aws cloudfront create-cache-policy \
    --cache-policy-config file://cache-policy.json

# cache-policy.json
cat > cache-policy.json << 'EOF'
{
  "Name": "CustomCachePolicy",
  "Comment": "Cache policy for dynamic content",
  "DefaultTTL": 86400,
  "MaxTTL": 31536000,
  "MinTTL": 1,
  "ParametersInCacheKeyAndForwardedToOrigin": {
    "EnableAcceptEncodingGzip": true,
    "EnableAcceptEncodingBrotli": true,
    "QueryStringsConfig": {
      "QueryStringBehavior": "whitelist",
      "QueryStrings": {
        "Quantity": 2,
        "Items": ["page", "sort"]
      }
    },
    "HeadersConfig": {
      "HeaderBehavior": "whitelist",
      "Headers": {
        "Quantity": 1,
        "Items": ["CloudFront-Viewer-Country"]
      }
    },
    "CookiesConfig": {
      "CookieBehavior": "none"
    }
  }
}
EOF
```

### 4. CloudFront Functions（エッジ処理）

リクエスト/レスポンスをエッジで変更します。

```javascript
// CloudFront Function（リダイレクト）
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // URLを正規化（末尾のスラッシュを削除）
    if (uri.endsWith('/') && uri !== '/') {
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                'location': { value: uri.slice(0, -1) }
            }
        };
    }

    // index.htmlを追加
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
    } else if (!uri.includes('.')) {
        request.uri += '/index.html';
    }

    return request;
}
```

```bash
# CloudFront Functionの作成
aws cloudfront create-function \
    --name url-rewrite \
    --function-config Comment="URL rewrite function",Runtime=cloudfront-js-1.0 \
    --function-code fileb://url-rewrite.js

# ディストリビューションに関連付け
aws cloudfront update-distribution \
    --id E1234567890ABC \
    --distribution-config file://distribution-with-function.json
```

### 5. Lambda@Edge（複雑な処理）

認証、A/Bテスト、画像リサイズなど。

```python
"""
Lambda@Edge: 認証チェック
"""
import base64

def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # Basic認証チェック
    auth_header = headers.get('authorization', [{}])[0].get('value', '')

    if not auth_header.startswith('Basic '):
        return {
            'status': '401',
            'statusDescription': 'Unauthorized',
            'headers': {
                'www-authenticate': [{
                    'key': 'WWW-Authenticate',
                    'value': 'Basic realm="Secure Area"'
                }]
            }
        }

    # 認証情報の検証
    encoded_credentials = auth_header.split(' ')[1]
    credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = credentials.split(':')

    if username == 'admin' and password == 'SecurePassword123!':
        return request  # 認証成功、リクエストを続行
    else:
        return {
            'status': '401',
            'statusDescription': 'Unauthorized'
        }
```

### 6. 複数オリジンとパスパターン

異なるパスで異なるオリジンを使用します。

```json
{
  "Origins": {
    "Quantity": 2,
    "Items": [
      {
        "Id": "S3-static-content",
        "DomainName": "static.s3.amazonaws.com"
      },
      {
        "Id": "ALB-api",
        "DomainName": "api.example.com"
      }
    ]
  },
  "CacheBehaviors": {
    "Quantity": 1,
    "Items": [{
      "PathPattern": "/api/*",
      "TargetOriginId": "ALB-api",
      "ViewerProtocolPolicy": "https-only",
      "AllowedMethods": {
        "Quantity": 7,
        "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      },
      "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    }]
  }
}
```

### 7. 無効化（キャッシュクリア）

特定のオブジェクトのキャッシュをクリアします。

```bash
# 無効化リクエストの作成
aws cloudfront create-invalidation \
    --distribution-id E1234567890ABC \
    --paths "/*"

# 特定のパスのみ
aws cloudfront create-invalidation \
    --distribution-id E1234567890ABC \
    --paths "/images/*" "/css/style.css"
```

**注意**: 無効化は1000パス/月まで無料、超過分は$0.005/パス

## ベストプラクティス（2025年版）

### 1. Origin Shieldを有効化

```bash
# 高トラフィックサイトでは必須
# オリジン負荷を大幅削減
```

### 2. Brotli圧縮を有効化

```bash
# Gzipより20-30%高い圧縮率
"EnableAcceptEncodingBrotli": true
```

### 3. キャッシュポリシーを再利用

```bash
# 複数のディストリビューションで同じポリシーを使用
# 管理が容易
```

### 4. CloudFront Functionsを活用

```bash
# Lambda@Edgeより10倍安い
# 軽量な処理（URL書き換え、ヘッダー追加など）
```

### 5. TTLを適切に設定

```bash
# 静的コンテンツ: 1年（31536000秒）
# 動的コンテンツ: 1分～1時間
```

## よくある落とし穴と対策

### 1. キャッシュヒット率が低い

**症状**: オリジンへのリクエストが多い

**対策**: クエリ文字列、ヘッダー、Cookieの転送を最小化

### 2. 無効化コストの増加

**症状**: 頻繁な無効化で高額請求

**対策**: バージョニング（`/v1/app.js` → `/v2/app.js`）

### 3. Origin Shieldのリージョン選択ミス

**症状**: レイテンシ改善なし

**対策**: オリジンと同じリージョンを選択

## 判断ポイント

### CloudFront Functions vs Lambda@Edge

| 機能 | CloudFront Functions | Lambda@Edge |
|-----|---------------------|-------------|
| 実行場所 | すべてのエッジ | リージョナルエッジ |
| 実行時間 | <1ms | 最大5秒 |
| メモリ | 2 MB | 最大10 GB |
| 料金 | $0.10/100万 | $0.60/100万 |
| 用途 | 軽量処理 | 複雑な処理 |

## リソース

### 公式ドキュメント

- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Origin Shield](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html)
- [CloudFront Functions](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html)
