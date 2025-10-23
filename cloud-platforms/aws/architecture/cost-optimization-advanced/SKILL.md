---
name: aws-cost-optimization-advanced
description: FinOpsプラクティスを実践し、Savings Plans、Reserved Instances、Spot Instances、リソースライトサイジング、タグ戦略で30-40%のコスト削減を実現する方法
---

# AWS Cost Optimization Advanced スキル

## 概要

FinOps（Financial Operations）は、クラウドコストの可視化、最適化、ガバナンスを通じて、ビジネス価値を最大化する実践手法です。AWS Cost Explorer、Budgets、Savings Plansを活用して30-40%のコスト削減を実現します。

## 主な使用ケース

### 1. Savings Plans（2025年推奨）

```bash
# Compute Savings Plans（最大66%削減、最も柔軟）
aws savingsplans create-savings-plan \
    --savings-plan-type ComputeSavingsPlans \
    --commitment 100.0 \
    --upfront-payment-amount 0 \
    --savings-plan-offering-id OFFERING_ID \
    --tags Key=Team,Value=Engineering

# EC2 Instance Savings Plans（最大72%削減）
aws savingsplans create-savings-plan \
    --savings-plan-type EC2InstanceSavingsPlans \
    --commitment 200.0 \
    --upfront-payment-amount 0 \
    --savings-plan-offering-id OFFERING_ID

# Savings Plans推奨取得
aws ce get-savings-plans-purchase-recommendation \
    --lookback-period-in-days SIXTY_DAYS \
    --term-in-years ONE_YEAR \
    --payment-option NO_UPFRONT \
    --savings-plans-type COMPUTE_SP
```

### 2. Reserved Instances（特定ワークロード）

```bash
# RI推奨取得
aws ce get-reservation-purchase-recommendation \
    --service "Amazon Elastic Compute Cloud - Compute" \
    --lookback-period-in-days SIXTY_DAYS \
    --term-in-years ONE_YEAR \
    --payment-option NO_UPFRONT

# Standard RI購入（最大75%削減、柔軟性低）
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id abc-123 \
    --instance-count 10

# Convertible RI購入（最大54%削減、インスタンスタイプ変更可能）
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id def-456 \
    --instance-count 5

# RI使用率モニタリング
aws ce get-reservation-utilization \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY
```

### 3. Spot Instances（最大90%削減）

```bash
# Spot Fleet作成
aws ec2 request-spot-fleet \
    --spot-fleet-request-config '{
        "IamFleetRole": "arn:aws:iam::123456789012:role/SpotFleetRole",
        "AllocationStrategy": "price-capacity-optimized",
        "TargetCapacity": 10,
        "SpotPrice": "0.05",
        "LaunchSpecifications": [{
            "ImageId": "ami-abc123",
            "InstanceType": "t3.medium",
            "KeyName": "my-key",
            "SpotPrice": "0.05"
        }, {
            "ImageId": "ami-abc123",
            "InstanceType": "t3a.medium",
            "KeyName": "my-key",
            "SpotPrice": "0.045"
        }]
    }'

# Auto Scaling + Spot
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-asg-spot \
    --mixed-instances-policy '{
        "InstancesDistribution": {
            "OnDemandBaseCapacity": 2,
            "OnDemandPercentageAboveBaseCapacity": 20,
            "SpotAllocationStrategy": "price-capacity-optimized"
        },
        "LaunchTemplate": {
            "LaunchTemplateSpecification": {
                "LaunchTemplateId": "lt-abc123",
                "Version": "$Latest"
            },
            "Overrides": [
                {"InstanceType": "t3.medium"},
                {"InstanceType": "t3a.medium"},
                {"InstanceType": "t2.medium"}
            ]
        }
    }' \
    --min-size 2 \
    --max-size 20 \
    --desired-capacity 5 \
    --vpc-zone-identifier "subnet-1,subnet-2,subnet-3"
```

### 4. Cost Allocation Tags（コスト配分）

```bash
# タグ付けポリシー作成
cat > tag-policy.json << 'EOF'
{
  "tags": {
    "Environment": {
      "tag_key": {
        "@@assign": "Environment"
      },
      "tag_value": {
        "@@assign": ["Production", "Staging", "Development"]
      },
      "enforced_for": {
        "@@assign": ["ec2:instance", "rds:db", "s3:bucket"]
      }
    },
    "CostCenter": {
      "tag_key": {
        "@@assign": "CostCenter"
      },
      "enforced_for": {
        "@@assign": ["*"]
      }
    }
  }
}
EOF

# Organizations Tag Policy適用
aws organizations create-policy \
    --content file://tag-policy.json \
    --description "Mandatory cost allocation tags" \
    --name CostAllocationTagPolicy \
    --type TAG_POLICY

# Cost Allocation Tags有効化
aws ce update-cost-allocation-tags-status \
    --cost-allocation-tags-status '[
        {"TagKey": "Environment", "Status": "Active"},
        {"TagKey": "CostCenter", "Status": "Active"},
        {"TagKey": "Project", "Status": "Active"},
        {"TagKey": "Owner", "Status": "Active"}
    ]'
```

### 5. コスト異常検出

```bash
# Cost Anomaly Monitor作成
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "HighCostAnomaly",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'

# アラートサブスクリプション
aws ce create-anomaly-subscription \
    --anomaly-subscription '{
        "SubscriptionName": "DailyCostAlert",
        "Threshold": 100.0,
        "Frequency": "DAILY",
        "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/abc-123"],
        "Subscribers": [{
            "Type": "EMAIL",
            "Address": "finance@example.com"
        }, {
            "Type": "SNS",
            "Address": "arn:aws:sns:ap-northeast-1:123456789012:cost-alerts"
        }]
    }'
```

### 6. Rightsizing（適正サイジング）

```bash
# Rightsizing推奨取得
aws ce get-rightsizing-recommendation \
    --service "AmazonEC2" \
    --configuration '{
        "RecommendationTarget": "SAME_INSTANCE_FAMILY",
        "BenefitsConsidered": true
    }'

# Compute Optimizer推奨
aws compute-optimizer get-ec2-instance-recommendations \
    --instance-arns \
        "arn:aws:ec2:ap-northeast-1:123456789012:instance/i-abc123" \
        "arn:aws:ec2:ap-northeast-1:123456789012:instance/i-def456"

# Lambda Rightsizing
aws compute-optimizer get-lambda-function-recommendations \
    --function-arns \
        "arn:aws:lambda:ap-northeast-1:123456789012:function:my-function"
```

## ベストプラクティス（2025年版）

### 1. ハイブリッド購入戦略

```text
# 推奨配分（70-20-10ルール）

70%: On-Demand
- 変動ワークロード
- 新規プロジェクト
- 短期間利用

20%: Savings Plans / RI
- 安定ワークロード
- ベースライン容量
- 1-3年継続確実

10%: Spot Instances
- バッチ処理
- ステートレスアプリ
- 中断許容可能

期待削減効果: 30-40%
```

### 2. Savings Plans vs Reserved Instances

```text
Savings Plans推奨ケース（2025年デフォルト）:
✓ Lambda/Fargate含む
✓ インスタンスタイプ柔軟性必要
✓ リージョン間移動可能性
✓ 管理簡素化

Reserved Instances推奨ケース:
✓ EC2のみ
✓ 固定インスタンスタイプ
✓ 最大割引率必要（Standard RI）
✓ キャパシティ予約必要

2025年推奨:
1. Savings Plansメイン
2. RIは特定ワークロードのみ
3. 組み合わせで最適化
```

### 3. タグ戦略

```json
// 必須タグ（Organizations Tag Policy）
{
  "Environment": ["Production", "Staging", "Development"],
  "CostCenter": "CC-XXXX",
  "Project": "project-name",
  "Owner": "team-name"
}

// 推奨タグ
{
  "Application": "app-name",
  "ManagedBy": "Terraform",
  "BackupPolicy": "Daily",
  "DataClassification": "Confidential"
}
```

### 4. FinOps組織体制

```text
# 3チームモデル

1. Finance Team（予算管理）
   - 予算設定
   - コスト配分
   - レポーティング

2. Engineering Team（最適化）
   - Rightsizing実施
   - Spot活用
   - アーキテクチャ改善

3. FinOps Team（調整役）
   - コスト可視化
   - 推奨事項提供
   - チーム間調整

月次レビュー必須
```

### 5. 自動化によるコスト削減

```python
# Lambda - 営業時間外のEC2自動停止
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # 平日 19:00-9:00、土日全日
    now = datetime.now()
    is_weekend = now.weekday() >= 5
    is_night = now.hour < 9 or now.hour >= 19

    if is_weekend or is_night:
        # Dev/Staging環境のインスタンス停止
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['Development', 'Staging']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )

        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if instance_ids:
            ec2.stop_instances(InstanceIds=instance_ids)
            print(f'Stopped {len(instance_ids)} instances')

# 月次削減効果: 約30%（非本番環境）
```

### 6. S3 Intelligent-Tiering（自動階層化）

```bash
# Intelligent-Tiering有効化
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket my-bucket \
    --id default-config \
    --intelligent-tiering-configuration '{
        "Id": "default-config",
        "Status": "Enabled",
        "Tierings": [
            {
                "Days": 90,
                "AccessTier": "ARCHIVE_ACCESS"
            },
            {
                "Days": 180,
                "AccessTier": "DEEP_ARCHIVE_ACCESS"
            }
        ]
    }'

# 削減効果:
# - Frequent Access → Infrequent Access (40%削減)
# - Infrequent → Archive (75%削減)
# - Archive → Deep Archive (95%削減)
```

## よくある失敗パターン

### 1. RI/SP過剰購入

```text
問題: 3年RIを大量購入後、ワークロード縮小
解決: 段階的購入

推奨アプローチ:
1. 6ヶ月間の実績データ分析
2. 1年No-Upfront Savings Plans開始
3. 四半期毎に見直し
4. 確実な部分のみ3年コミット
```

### 2. タグ未整備

```text
問題: コスト配分不可
解決: Tag Policyで強制

# 必須タグなしでリソース作成禁止（SCP）
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": ["ec2:RunInstances", "rds:CreateDBInstance"],
    "Resource": "*",
    "Condition": {
      "StringNotLike": {
        "aws:RequestTag/CostCenter": "*"
      }
    }
  }]
}
```

### 3. 未使用リソース放置

```bash
# 未使用EBS Volume検出
aws ec2 describe-volumes \
    --filters Name=status,Values=available \
    --query 'Volumes[*].[VolumeId,Size,VolumeType]' \
    --output table

# 未使用Elastic IP検出
aws ec2 describe-addresses \
    --filters Name=association-id,Values= \
    --query 'Addresses[*].[PublicIp,AllocationId]' \
    --output table

# 月次クリーンアップ推奨（削減効果: 5-10%）
```

## リソース

- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
- [Savings Plans Documentation](https://docs.aws.amazon.com/savingsplans/)
- [FinOps Foundation](https://www.finops.org/)
