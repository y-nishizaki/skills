---
name: aws-well-architected
description: AWS Well-Architected Frameworkの6つの柱（運用上の優秀性、セキュリティ、信頼性、パフォーマンス効率、コスト最適化、持続可能性）を理解し、ベストプラクティスを適用する方法
---

# AWS Well-Architected Framework スキル

## 概要

AWS Well-Architected Frameworkは、クラウドアーキテクチャのベストプラクティスを体系化した6つの柱から構成されます。このフレームワークを使用して、セキュアで高性能、回復力があり、効率的なインフラストラクチャを構築します。

### 6つの柱（2025年版）

1. **運用上の優秀性** (Operational Excellence)
2. **セキュリティ** (Security)
3. **信頼性** (Reliability)
4. **パフォーマンス効率** (Performance Efficiency)
5. **コスト最適化** (Cost Optimization)
6. **持続可能性** (Sustainability) ← 2021年追加

## 主な使用ケース

### 1. 運用上の優秀性

**設計原則**:
- コードとしての運用（IaC）
- 小さく頻繁な変更
- 運用手順の定期的な改善
- 障害の予測
- 運用上のすべての障害から学習

```bash
# Infrastructure as Code（CloudFormation）
aws cloudformation create-stack \
    --stack-name production-infrastructure \
    --template-body file://infrastructure.yaml \
    --parameters ParameterKey=Environment,ParameterValue=production

# CloudWatch Logsで運用メトリクス収集
aws logs put-metric-filter \
    --log-group-name /aws/application \
    --filter-name DeploymentMetrics \
    --filter-pattern "[time, deployment_id, status, duration]" \
    --metric-transformations \
        metricName=DeploymentDuration,metricNamespace=Operations,metricValue='$duration'
```

### 2. セキュリティ

**設計原則**:
- 強力なアイデンティティ基盤の実装
- トレーサビリティの有効化
- 全レイヤーでのセキュリティ適用
- セキュリティのベストプラクティスの自動化
- 転送中および保管中のデータ保護

```bash
# IAM最小権限ポリシー
cat > least-privilege-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::my-bucket/app-data/*",
    "Condition": {
      "IpAddress": {
        "aws:SourceIp": "203.0.113.0/24"
      }
    }
  }]
}
EOF

# GuardDutyで脅威検出
aws guardduty create-detector --enable

# Security Hubでコンプライアンスチェック
aws securityhub enable-security-hub \
    --enable-default-standards
```

### 3. 信頼性

**設計原則**:
- 障害から自動的に復旧
- 復旧手順のテスト
- 水平方向のスケーリング
- キャパシティの推測を止める
- 自動化で変更を管理

```bash
# マルチAZ RDS
aws rds create-db-instance \
    --db-instance-identifier production-db \
    --db-instance-class db.r6g.xlarge \
    --engine postgres \
    --multi-az \
    --backup-retention-period 30

# Auto Scaling
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 3 \
    --vpc-zone-identifier "subnet-1,subnet-2,subnet-3"

# Route 53ヘルスチェック + Failover
aws route53 create-health-check \
    --health-check-config IPAddress=203.0.113.1,Port=443,Type=HTTPS,ResourcePath=/health
```

### 4. パフォーマンス効率

**設計原則**:
- 高度なテクノロジーの民主化
- 数分でグローバル展開
- サーバーレスアーキテクチャの使用
- 実験の頻度を上げる
- メカニカルシンパシー

```bash
# CloudFrontでグローバル配信
aws cloudfront create-distribution \
    --origin-domain-name my-app.s3.amazonaws.com \
    --default-root-object index.html

# Lambda@Edgeでエッジコンピューティング
aws lambda publish-version --function-name edge-function

# DynamoDB Auto Scaling
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id table/UserData \
    --scalable-dimension dynamodb:table:ReadCapacityUnits \
    --min-capacity 5 \
    --max-capacity 100
```

### 5. コスト最適化

**設計原則**:
- クラウド財務管理の実装
- 消費モデルの採用
- 全体的な効率の測定
- 未分化な重労働への支出を止める
- 費用の分析と属性

```bash
# Savings Plans
aws savingsplans create-savings-plan \
    --savings-plan-offering-id OFFERING_ID \
    --commitment 100 \
    --upfront-payment-amount 0

# Cost Anomaly Detection
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "HighCostAnomaly",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'

# S3 Intelligent-Tiering
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket my-bucket \
    --id default-config \
    --intelligent-tiering-configuration '{
        "Id": "default-config",
        "Status": "Enabled",
        "Tierings": [{
            "Days": 90,
            "AccessTier": "ARCHIVE_ACCESS"
        }]
    }'
```

### 6. 持続可能性

**設計原則**:
- 影響を理解する
- 持続可能性の目標を確立
- 使用率を最大化
- 新しい効率的なハードウェアとソフトウェアの予測と採用
- マネージドサービスの使用
- ダウンストリームの影響を削減

```bash
# Gravitonインスタンス（60%省エネ）
aws ec2 run-instances \
    --instance-type t4g.medium \
    --image-id ami-0ab3e16f9c414dee7

# Auto Scalingでリソース最適化
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-asg \
    --policy-name target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0
    }'

# S3ライフサイクルで不要データ削除
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration '{
        "Rules": [{
            "Id": "DeleteOldData",
            "Status": "Enabled",
            "Expiration": {"Days": 90}
        }]
    }'
```

## Well-Architected Toolの使用

```bash
# ワークロードの作成
aws wellarchitected create-workload \
    --workload-name "Production Web Application" \
    --description "E-commerce platform" \
    --environment PRODUCTION \
    --review-owner "architect@example.com" \
    --lenses "wellarchitected"

# レビューの実施
aws wellarchitected create-milestone \
    --workload-id WORKLOAD_ID \
    --milestone-name "Initial Review"
```

## ベストプラクティスチェックリスト

### 運用上の優秀性
- [ ] IaCでインフラ管理
- [ ] CI/CDパイプライン実装
- [ ] ランブック/プレイブック整備
- [ ] CloudWatchで監視・アラート
- [ ] 定期的なポストモーテム実施

### セキュリティ
- [ ] IAM最小権限原則
- [ ] MFA有効化
- [ ] CloudTrailで監査ログ
- [ ] データ暗号化（転送中・保管中）
- [ ] セキュリティグループで最小アクセス

### 信頼性
- [ ] マルチAZ構成
- [ ] 自動バックアップ
- [ ] ディザスタリカバリ計画
- [ ] Auto Scaling設定
- [ ] 定期的な障害テスト

### パフォーマンス効率
- [ ] 適切なインスタンスタイプ選択
- [ ] CloudFrontでCDN
- [ ] ElastiCacheでキャッシング
- [ ] RDS Read Replica
- [ ] パフォーマンステスト実施

### コスト最適化
- [ ] Savings Plans/Reserved Instances
- [ ] 未使用リソースの削除
- [ ] Cost Explorerで分析
- [ ] タグ付けでコスト配分
- [ ] S3 Intelligent-Tiering

### 持続可能性
- [ ] Gravitonインスタンス使用
- [ ] Auto Scalingでリソース最適化
- [ ] 不要データの削除
- [ ] リージョン選択（再エネ）
- [ ] サーバーレスアーキテクチャ

## リソース

- [Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Well-Architected Tool](https://aws.amazon.com/well-architected-tool/)
- [Well-Architected Lenses](https://aws.amazon.com/architecture/well-architected/lenses/)
