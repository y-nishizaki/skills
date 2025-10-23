---
name: aws-high-availability
description: AWSで高可用性とディザスタリカバリを実装し、Multi-AZ、Multi-Region、RTO/RPO、フェイルオーバー戦略で事業継続性を確保する方法
---

# AWS High Availability & Disaster Recovery スキル

## 概要

高可用性（HA）とディザスタリカバリ（DR）は、システムの可用性を最大化し、障害時の復旧を保証する設計戦略です。Multi-AZ、Multi-Region構成とRTO/RPO目標を組み合わせて実装します。

## 主な使用ケース

### 1. Multi-AZ構成（高可用性）

```bash
# Multi-AZ RDS
aws rds create-db-instance \
    --db-instance-identifier production-db \
    --db-instance-class db.r6g.xlarge \
    --engine postgres \
    --multi-az \
    --allocated-storage 500 \
    --storage-type gp3 \
    --backup-retention-period 30 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "sun:04:00-sun:05:00"

# Multi-AZ ELB + Auto Scaling
aws elbv2 create-load-balancer \
    --name production-alb \
    --subnets subnet-1a subnet-1c subnet-1d \
    --security-groups sg-abc123 \
    --scheme internet-facing \
    --type application

aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --launch-template LaunchTemplateName=web-template \
    --min-size 3 \
    --max-size 10 \
    --desired-capacity 3 \
    --vpc-zone-identifier "subnet-1a,subnet-1c,subnet-1d" \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --target-group-arns arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:targetgroup/web-tg/abc123
```

### 2. Multi-Region構成（ディザスタリカバリ）

```bash
# Route 53 Health Check
aws route53 create-health-check \
    --caller-reference $(date +%s) \
    --health-check-config '{
        "Type": "HTTPS",
        "ResourcePath": "/health",
        "FullyQualifiedDomainName": "api.example.com",
        "Port": 443,
        "RequestInterval": 30,
        "FailureThreshold": 3
    }' \
    --health-check-tags Key=Name,Value=PrimaryRegionHealthCheck

# Route 53 Failover Routing
cat > primary-record.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.example.com",
      "Type": "A",
      "SetIdentifier": "Primary",
      "Failover": "PRIMARY",
      "HealthCheckId": "abc-123",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "alb-primary.ap-northeast-1.elb.amazonaws.com",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456 \
    --change-batch file://primary-record.json

# セカンダリレコード（ap-southeast-1）
cat > secondary-record.json << 'EOF'
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.example.com",
      "Type": "A",
      "SetIdentifier": "Secondary",
      "Failover": "SECONDARY",
      "AliasTarget": {
        "HostedZoneId": "Z1LMS91P8CMLE5",
        "DNSName": "alb-secondary.ap-southeast-1.elb.amazonaws.com",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456 \
    --change-batch file://secondary-record.json
```

### 3. DR戦略（4つのアプローチ）

```text
# 1. Backup & Restore（RPO: 時間単位、RTO: 時間〜日単位）
コスト: 最低
- S3にバックアップ保存
- 障害時にリストア

# 2. Pilot Light（RPO: 分単位、RTO: 分〜時間単位）
コスト: 低
- データベースのみレプリケーション
- 障害時にアプリケーション起動

# 3. Warm Standby（RPO: 秒単位、RTO: 分単位）
コスト: 中
- 最小構成でアプリケーション常時稼働
- 障害時にスケールアップ

# 4. Multi-Site Active/Active（RPO: ほぼゼロ、RTO: ほぼゼロ）
コスト: 最高
- 両リージョンで全機能稼働
- 常時トラフィック分散
```

### 4. RDS Cross-Region レプリケーション

```bash
# Read Replica作成（別リージョン）
aws rds create-db-instance-read-replica \
    --db-instance-identifier production-db-replica-singapore \
    --source-db-instance-identifier arn:aws:rds:ap-northeast-1:123456789012:db:production-db \
    --db-instance-class db.r6g.xlarge \
    --region ap-southeast-1 \
    --publicly-accessible false \
    --storage-encrypted \
    --kms-key-id alias/rds-replica-key

# Read Replicaを昇格（DR時）
aws rds promote-read-replica \
    --db-instance-identifier production-db-replica-singapore \
    --region ap-southeast-1 \
    --backup-retention-period 30
```

### 5. DynamoDB Global Tables

```bash
# Global Table作成（Multi-Region）
aws dynamodb create-global-table \
    --global-table-name Users \
    --replication-group \
        RegionName=ap-northeast-1 \
        RegionName=ap-southeast-1 \
        RegionName=us-east-1

# レプリケーション確認
aws dynamodb describe-global-table \
    --global-table-name Users
```

### 6. S3 Cross-Region Replication

```bash
# レプリケーションルール作成
cat > replication-config.json << 'EOF'
{
  "Role": "arn:aws:iam::123456789012:role/S3ReplicationRole",
  "Rules": [{
    "ID": "ReplicateAll",
    "Status": "Enabled",
    "Priority": 1,
    "Filter": {},
    "Destination": {
      "Bucket": "arn:aws:s3:::my-bucket-replica-singapore",
      "ReplicationTime": {
        "Status": "Enabled",
        "Time": {"Minutes": 15}
      },
      "Metrics": {
        "Status": "Enabled",
        "EventThreshold": {"Minutes": 15}
      }
    },
    "DeleteMarkerReplication": {"Status": "Enabled"}
  }]
}
EOF

# バケットバージョニング有効化（必須）
aws s3api put-bucket-versioning \
    --bucket my-bucket-primary \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
    --bucket my-bucket-replica-singapore \
    --versioning-configuration Status=Enabled

# レプリケーション設定
aws s3api put-bucket-replication \
    --bucket my-bucket-primary \
    --replication-configuration file://replication-config.json
```

## ベストプラクティス（2025年版）

### 1. RTO/RPO目標設定

```text
ミッションクリティカル:
- RTO: < 1時間
- RPO: < 15分
- 戦略: Warm Standby または Multi-Site

ビジネスクリティカル:
- RTO: < 4時間
- RPO: < 1時間
- 戦略: Pilot Light

一般アプリケーション:
- RTO: < 24時間
- RPO: < 12時間
- 戦略: Backup & Restore
```

### 2. 定期的なDRテスト

```bash
# 四半期毎のDRドリル
# 1. プライマリリージョン停止シミュレーション
# 2. Route 53フェイルオーバー検証
# 3. Read Replica昇格
# 4. アプリケーション疎通確認
# 5. データ整合性確認
# 6. ロールバック

# GameDayイベント実施（年1回以上）
```

### 3. バックアップ戦略（3-2-1ルール）

```text
3: 3つのコピー
2: 2種類の異なるメディア（EBS + S3）
1: 1つはオフサイト（別リージョン）

実装例:
- EBSスナップショット（同一リージョン）
- S3バックアップ（同一リージョン）
- S3 CRR（別リージョン）
```

### 4. 自動フェイルオーバー

```python
# Lambda + Route 53でカスタムヘルスチェック
import boto3
import requests

route53 = boto3.client('route53')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    # アプリケーションヘルスチェック
    try:
        response = requests.get('https://api.example.com/health', timeout=5)
        healthy = response.status_code == 200
    except:
        healthy = False

    # CloudWatchメトリクス送信
    cloudwatch.put_metric_data(
        Namespace='CustomHealthCheck',
        MetricData=[{
            'MetricName': 'ApplicationHealth',
            'Value': 1 if healthy else 0,
            'Unit': 'None'
        }]
    )

    # 3回連続失敗でフェイルオーバー
    if not healthy:
        trigger_failover()

def trigger_failover():
    # Route 53レコード重み付け変更（プライマリ 0、セカンダリ 100）
    route53.change_resource_record_sets(
        HostedZoneId='Z123456',
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'SetIdentifier': 'Primary',
                    'Weight': 0,
                    'AliasTarget': {...}
                }
            }]
        }
    )
```

### 5. データベースバックアップ

```bash
# RDS自動バックアップ + スナップショット
aws rds modify-db-instance \
    --db-instance-identifier production-db \
    --backup-retention-period 35 \
    --preferred-backup-window "03:00-04:00"

# 手動スナップショット（月次）
aws rds create-db-snapshot \
    --db-instance-identifier production-db \
    --db-snapshot-identifier production-db-monthly-$(date +%Y%m)

# クロスリージョンコピー
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:ap-northeast-1:123456789012:snapshot:production-db-monthly-202501 \
    --target-db-snapshot-identifier production-db-monthly-202501-singapore \
    --source-region ap-northeast-1 \
    --region ap-southeast-1 \
    --kms-key-id alias/rds-backup-key
```

### 6. Aurora Global Database

```bash
# Global Database作成（最強DR）
aws rds create-global-cluster \
    --global-cluster-identifier production-global-cluster \
    --engine aurora-postgresql \
    --engine-version 15.4

# プライマリクラスター
aws rds create-db-cluster \
    --db-cluster-identifier production-cluster-tokyo \
    --engine aurora-postgresql \
    --global-cluster-identifier production-global-cluster

# セカンダリクラスター（別リージョン）
aws rds create-db-cluster \
    --db-cluster-identifier production-cluster-singapore \
    --engine aurora-postgresql \
    --global-cluster-identifier production-global-cluster \
    --region ap-southeast-1

# フェイルオーバー（< 1分）
aws rds failover-global-cluster \
    --global-cluster-identifier production-global-cluster \
    --target-db-cluster-identifier production-cluster-singapore
```

## よくある失敗パターン

### 1. DRテスト未実施

```text
問題: 年1回もDRテストせず、実際の障害時に失敗
解決: 四半期毎のDRドリル + 年1回のGameDay

チェックリスト:
□ フェイルオーバー手順書更新
□ 全チームメンバーが手順理解
□ 自動化スクリプト動作確認
□ データ整合性検証
```

### 2. RPO/RTO未定義

```text
問題: ビジネス要件不明確
解決: ステークホルダーと合意

質問例:
- データ損失許容時間は？
- サービス停止許容時間は？
- コスト上限は？
```

### 3. シングルリージョン依存

```text
問題: Multi-AZのみでMulti-Region未実装
解決: リージョン障害を想定

2025年推奨:
- ミッションクリティカル: Multi-Region必須
- ビジネスクリティカル: Pilot Light以上
- 一般: Backup & Restore
```

## リソース

- [Disaster Recovery on AWS](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/)
- [Multi-Region Architecture](https://aws.amazon.com/solutions/implementations/multi-region-application-architecture/)
- [RTO/RPO Calculator](https://calculator.aws/)
