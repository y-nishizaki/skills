---
name: aws-route53
description: AWS Route 53を使用してDNS管理、ルーティングポリシー、ヘルスチェック、フェイルオーバーを実装し、高可用性なアプリケーションを構築する方法
---

# AWS Route 53 スキル

## 概要

Amazon Route 53は、高可用性でスケーラブルなDNSウェブサービスです。このスキルでは、ホストゾーン、各種ルーティングポリシー、ヘルスチェックを活用して、グローバルなアプリケーション配信を最適化します。

### 2025年の重要なアップデート

- **ルーティングポリシー**: 7種類（Simple, Weighted, Latency, Failover, Geolocation, Geoproximity, Multivalue）
- **ヘルスチェック**: 自動フェイルオーバー
- **プライベートホストゾーン**: VPC内DNS
- **料金**: $0.50/ホストゾーン/月、$0.40/100万クエリ

## 主な使用ケース

### 1. ホストゾーンの作成

パブリックホストゾーンでドメインを管理します。

```bash
# パブリックホストゾーンの作成
aws route53 create-hosted-zone \
    --name example.com \
    --caller-reference $(date +%s) \
    --hosted-zone-config Comment="Production domain"

HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name example.com --query 'HostedZones[0].Id' --output text)

# Aレコードの作成
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file://a-record.json

# a-record.json
cat > a-record.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "www.example.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "203.0.113.1"}]
    }
  }]
}
EOF
```

### 2. エイリアスレコード（AWS リソース）

ALBやCloudFrontへのエイリアスレコードを作成します。

```bash
# ALBへのエイリアスレコード
cat > alb-alias.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "app.example.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z14GRHDCWA56QT",
        "DNSName": "my-alb-1234567890.ap-northeast-1.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file://alb-alias.json
```

### 3. Weightedルーティング（カナリアデプロイ）

トラフィックを重み付けで分散します。

```bash
# バージョン1（90%のトラフィック）
cat > weighted-v1.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.example.com",
      "Type": "A",
      "SetIdentifier": "Version-1",
      "Weight": 90,
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.1"}]
    }
  }]
}
EOF

# バージョン2（10%のトラフィック）
cat > weighted-v2.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.example.com",
      "Type": "A",
      "SetIdentifier": "Version-2",
      "Weight": 10,
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.2"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://weighted-v1.json
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://weighted-v2.json
```

### 4. Latencyルーティング（グローバル展開）

ユーザーに最も近いリージョンに誘導します。

```bash
# 東京リージョン
cat > latency-tokyo.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "global.example.com",
      "Type": "A",
      "SetIdentifier": "Tokyo",
      "Region": "ap-northeast-1",
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.10"}]
    }
  }]
}
EOF

# バージニアリージョン
cat > latency-virginia.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "global.example.com",
      "Type": "A",
      "SetIdentifier": "Virginia",
      "Region": "us-east-1",
      "TTL": 60,
      "ResourceRecords": [{"Value": "198.51.100.10"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://latency-tokyo.json
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://latency-virginia.json
```

### 5. Failoverルーティング + ヘルスチェック

ヘルスチェックで自動フェイルオーバーを実現します。

```bash
# ヘルスチェックの作成
aws route53 create-health-check \
    --health-check-config file://health-check.json \
    --caller-reference $(date +%s)

# health-check.json
cat > health-check.json << 'EOF'
{
  "IPAddress": "203.0.113.1",
  "Port": 443,
  "Type": "HTTPS",
  "ResourcePath": "/health",
  "RequestInterval": 30,
  "FailureThreshold": 3
}
EOF

HEALTH_CHECK_ID=$(aws route53 list-health-checks --query 'HealthChecks[0].Id' --output text)

# プライマリレコード
cat > failover-primary.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "app.example.com",
      "Type": "A",
      "SetIdentifier": "Primary",
      "Failover": "PRIMARY",
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.1"}],
      "HealthCheckId": "HEALTH_CHECK_ID_HERE"
    }
  }]
}
EOF

# セカンダリレコード
cat > failover-secondary.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "app.example.com",
      "Type": "A",
      "SetIdentifier": "Secondary",
      "Failover": "SECONDARY",
      "TTL": 60,
      "ResourceRecords": [{"Value": "198.51.100.1"}]
    }
  }]
}
EOF
```

### 6. Geolocationルーティング

地理的な場所に基づいてルーティングします。

```bash
# 日本からのアクセス
cat > geo-japan.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "content.example.com",
      "Type": "A",
      "SetIdentifier": "Japan",
      "GeoLocation": {"CountryCode": "JP"},
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.10"}]
    }
  }]
}
EOF

# 米国からのアクセス
cat > geo-us.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "content.example.com",
      "Type": "A",
      "SetIdentifier": "US",
      "GeoLocation": {"CountryCode": "US"},
      "TTL": 60,
      "ResourceRecords": [{"Value": "198.51.100.10"}]
    }
  }]
}
EOF

# デフォルト（その他の地域）
cat > geo-default.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "content.example.com",
      "Type": "A",
      "SetIdentifier": "Default",
      "GeoLocation": {"ContinentCode": "EU"},
      "TTL": 60,
      "ResourceRecords": [{"Value": "192.0.2.10"}]
    }
  }]
}
EOF
```

### 7. プライベートホストゾーン

VPC内でのDNS解決に使用します。

```bash
# プライベートホストゾーンの作成
aws route53 create-hosted-zone \
    --name internal.example.com \
    --vpc VPCRegion=ap-northeast-1,VPCId=$VPC_ID \
    --caller-reference $(date +%s) \
    --hosted-zone-config PrivateZone=true,Comment="Internal DNS"

# プライベートAレコード
cat > private-record.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "db.internal.example.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "10.0.1.100"}]
    }
  }]
}
EOF

PRIVATE_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name internal.example.com --query 'HostedZones[0].Id' --output text)

aws route53 change-resource-record-sets \
    --hosted-zone-id $PRIVATE_ZONE_ID \
    --change-batch file://private-record.json
```

## ベストプラクティス（2025年版）

### 1. エイリアスレコードを使用

```bash
# 理由:
# - 料金無料（Aレコードクエリは課金対象）
# - AWSリソースのIPアドレス変更に自動対応
# - Zone Apex（example.com）でも使用可能
```

### 2. ヘルスチェックでフェイルオーバー

```bash
# 本番環境では必須
# プライマリが障害時に自動的にセカンダリへ
```

### 3. TTLを適切に設定

```bash
# 変更頻度が高い: TTL 60秒
# 安定したレコード: TTL 300-3600秒
```

### 4. 複数のルーティングポリシーを組み合わせ

```bash
# 例: Latency + Failover
# 各リージョンでフェイルオーバー構成
```

## よくある落とし穴と対策

### 1. TTLの設定ミス

**症状**: DNS変更が反映されない

**対策**: 変更前にTTLを短くしておく（例: 60秒）

### 2. ヘルスチェックのパス設定ミス

**症状**: 正常なサーバーが異常判定される

**対策**: `/health` エンドポイントを実装

### 3. プライベートホストゾーンの未設定

**症状**: VPC内でドメイン名解決できない

**対策**: プライベートホストゾーン作成

## ルーティングポリシー選択マトリクス

| ユースケース | 推奨ポリシー |
|------------|------------|
| シンプルなDNS | Simple |
| カナリアデプロイ | Weighted |
| グローバル展開 | Latency |
| DR構成 | Failover |
| 地域別コンテンツ | Geolocation |
| 複数のIPで負荷分散 | Multivalue |

## リソース

### 公式ドキュメント

- [Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [Routing Policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Health Checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
