---
name: aws-auto-scaling
description: AWS Auto Scalingを使用して、需要の変動に応じて自動的にEC2インスタンスやその他のリソースをスケーリングする方法
---

# AWS Auto Scaling スキル

## 概要

AWS Auto Scalingは、アプリケーションの需要に応じてコンピューティングリソースを自動的に調整するサービスです。このスキルでは、EC2 Auto Scaling、Application Auto Scaling、予測スケーリング（Predictive Scaling）を活用し、可用性を最大化しながらコストを最適化する方法を学びます。

### 対象となるサービス

- **EC2 Auto Scaling**: EC2インスタンスの自動スケーリング
- **Application Auto Scaling**: ECS、DynamoDB、Aurora、Lambda、AppStreamなどの自動スケーリング
- **AWS Auto Scaling**: 複数のサービスを横断したスケーリング計画

## 主な使用ケース

### 1. Webアプリケーションの需要変動対応

トラフィックの増減に応じてEC2インスタンス数を自動調整します。

```bash
# Auto Scaling グループの作成
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-app-asg \
    --launch-template LaunchTemplateName=web-app-template,Version='$Latest' \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 3 \
    --vpc-zone-identifier "subnet-12345678,subnet-87654321" \
    --target-group-arns arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:targetgroup/web-app-tg/abcdef1234567890 \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --tags "Key=Environment,Value=production,PropagateAtLaunch=true"
```

### 2. ターゲット追跡スケーリング

特定のメトリクス（CPU使用率、ネットワークトラフィックなど）を目標値に維持します。

```bash
# CPU使用率を50%に維持するターゲット追跡ポリシー
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name cpu-target-tracking-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration file://target-tracking-config.json

# target-tracking-config.json
cat > target-tracking-config.json << 'EOF'
{
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "TargetValue": 50.0
}
EOF
```

### 3. 予測スケーリング（2025年推奨）

過去のトラフィックパターンを学習し、需要を予測して事前にスケーリングします。

```bash
# 予測スケーリングポリシーの作成
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name predictive-scaling-policy \
    --policy-type PredictiveScaling \
    --predictive-scaling-configuration file://predictive-config.json

# predictive-config.json
cat > predictive-config.json << 'EOF'
{
  "MetricSpecifications": [
    {
      "TargetValue": 50.0,
      "PredefinedMetricPairSpecification": {
        "PredefinedMetricType": "ASGCPUUtilization"
      }
    }
  ],
  "Mode": "ForecastAndScale",
  "SchedulingBufferTime": 600
}
EOF
```

### 4. スケジュールベースのスケーリング

予測可能な需要パターン（営業時間、週末など）に対応します。

```bash
# 平日朝8時にスケールアウト
aws autoscaling put-scheduled-action \
    --auto-scaling-group-name web-app-asg \
    --scheduled-action-name scale-out-business-hours \
    --recurrence "0 8 * * MON-FRI" \
    --desired-capacity 10 \
    --time-zone "Asia/Tokyo"

# 平日夜20時にスケールイン
aws autoscaling put-scheduled-action \
    --auto-scaling-group-name web-app-asg \
    --scheduled-action-name scale-in-after-hours \
    --recurrence "0 20 * * MON-FRI" \
    --desired-capacity 3 \
    --time-zone "Asia/Tokyo"
```

### 5. Application Auto Scaling（DynamoDB）

DynamoDBテーブルの読み書きキャパシティを自動調整します。

```bash
# DynamoDBテーブルをスケーラブルターゲットとして登録
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id table/users \
    --scalable-dimension dynamodb:table:ReadCapacityUnits \
    --min-capacity 5 \
    --max-capacity 100

# ターゲット追跡ポリシーの作成
aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id table/users \
    --scalable-dimension dynamodb:table:ReadCapacityUnits \
    --policy-name read-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://dynamodb-scaling-config.json

# dynamodb-scaling-config.json
cat > dynamodb-scaling-config.json << 'EOF'
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "DynamoDBReadCapacityUtilization"
  },
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 60
}
EOF
```

## 思考プロセス

Auto Scalingを設計・実装する際の段階的な思考プロセスです。

### フェーズ1: 要件分析

```markdown
## チェックリスト

### トラフィックパターンの分析
- [ ] 過去のトラフィックデータを収集（最低2週間、理想的には1ヶ月以上）
- [ ] ピーク時間帯を特定（日次、週次、月次）
- [ ] 予測可能なパターン vs 予測不可能なスパイク
- [ ] トラフィック増加の速度（急激 vs 緩やか）

### パフォーマンス要件
- [ ] 許容可能なレスポンスタイム
- [ ] 最小必要なインスタンス数（可用性）
- [ ] 最大許容インスタンス数（コスト）
- [ ] スケールアウト/インの許容時間

### コスト制約
- [ ] 月間予算の上限
- [ ] Spot Instancesの利用可否
- [ ] リザーブドインスタンス/Savings Plansとの併用

### 依存関係
- [ ] データベースのスケーリング能力
- [ ] 外部APIの制限
- [ ] セッション管理方式（sticky session vs stateless）
```

### フェーズ2: スケーリング戦略の選択

#### 2025年推奨アプローチ：ハイブリッド戦略

```python
"""
Auto Scalingの戦略選択ロジック
"""

def choose_scaling_strategy(workload_characteristics):
    """
    ワークロードの特性に基づいて最適なスケーリング戦略を選択
    """
    strategies = []

    # 1. 予測可能なパターンがある場合
    if workload_characteristics.has_predictable_pattern:
        if workload_characteristics.historical_data_days >= 14:
            strategies.append({
                'type': 'Predictive Scaling',
                'config': {
                    'mode': 'ForecastAndScale',
                    'scheduling_buffer_time': 600  # 10分前に準備
                }
            })
        else:
            strategies.append({
                'type': 'Scheduled Scaling',
                'config': {
                    'cron_expressions': workload_characteristics.peak_times
                }
            })

    # 2. ベースライン（常に必要）
    strategies.append({
        'type': 'Target Tracking',
        'config': {
            'metric': 'ASGAverageCPUUtilization',
            'target_value': 50.0,
            'enable_detailed_monitoring': True  # 1分間隔
        }
    })

    # 3. 急激なスパイク対応
    if workload_characteristics.has_sudden_spikes:
        strategies.append({
            'type': 'Step Scaling',
            'config': {
                'metric': 'RequestCountPerTarget',
                'step_adjustments': [
                    {'lower_bound': 0, 'upper_bound': 100, 'adjustment': 1},
                    {'lower_bound': 100, 'upper_bound': 200, 'adjustment': 2},
                    {'lower_bound': 200, 'adjustment': 3}
                ]
            }
        })

    return strategies

# 使用例
workload = {
    'has_predictable_pattern': True,
    'historical_data_days': 30,
    'has_sudden_spikes': False,
    'peak_times': ['0 8 * * MON-FRI', '0 20 * * MON-FRI']
}

strategies = choose_scaling_strategy(workload)
print(f"推奨戦略: {strategies}")
```

### フェーズ3: Launch Templateの設計

```bash
# 2025年ベストプラクティスに準拠したLaunch Template
aws ec2 create-launch-template \
    --launch-template-name web-app-template-v2 \
    --version-description "2025 best practices" \
    --launch-template-data file://launch-template.json

# launch-template.json
cat > launch-template.json << 'EOF'
{
  "ImageId": "ami-0ab3e16f9c414dee7",
  "InstanceType": "t3.medium",
  "IamInstanceProfile": {
    "Arn": "arn:aws:iam::123456789012:instance-profile/WebAppInstanceProfile"
  },
  "SecurityGroupIds": ["sg-0123456789abcdef0"],
  "UserData": "IyEvYmluL2Jhc2gKYXB0IHVwZGF0ZSAmJiBhcHQgaW5zdGFsbCAteSBuZ2lueAo=",
  "MetadataOptions": {
    "HttpTokens": "required",
    "HttpPutResponseHopLimit": 1,
    "HttpEndpoint": "enabled"
  },
  "Monitoring": {
    "Enabled": true
  },
  "TagSpecifications": [
    {
      "ResourceType": "instance",
      "Tags": [
        {"Key": "Name", "Value": "web-app-instance"},
        {"Key": "ManagedBy", "Value": "AutoScaling"},
        {"Key": "Environment", "Value": "production"}
      ]
    },
    {
      "ResourceType": "volume",
      "Tags": [
        {"Key": "Name", "Value": "web-app-volume"}
      ]
    }
  ]
}
EOF
```

### フェーズ4: メトリクスとアラームの設定

```bash
# カスタムメトリクスに基づくターゲット追跡
# 例: アクティブな接続数を100に維持
cat > custom-metric-config.json << 'EOF'
{
  "CustomizedMetricSpecification": {
    "MetricName": "ActiveConnections",
    "Namespace": "WebApp/Metrics",
    "Statistic": "Average",
    "Dimensions": [
      {
        "Name": "AutoScalingGroupName",
        "Value": "web-app-asg"
      }
    ]
  },
  "TargetValue": 100.0
}
EOF

aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name active-connections-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration file://custom-metric-config.json

# CloudWatchアラームで異常を監視
aws cloudwatch put-metric-alarm \
    --alarm-name asg-stuck-scaling-out \
    --alarm-description "Auto Scaling group stuck at max capacity" \
    --metric-name GroupDesiredCapacity \
    --namespace AWS/AutoScaling \
    --statistic Average \
    --period 300 \
    --evaluation-periods 3 \
    --threshold 9 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=AutoScalingGroupName,Value=web-app-asg \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:ops-alerts
```

### フェーズ5: テストと調整

```python
"""
Auto Scalingのロードテストスクリプト
"""
import boto3
import time
from datetime import datetime

def monitor_scaling_behavior(asg_name, duration_minutes=30):
    """
    Auto Scalingの動作を監視し、適切にスケールしているか確認
    """
    autoscaling = boto3.client('autoscaling')
    cloudwatch = boto3.client('cloudwatch')

    start_time = datetime.utcnow()
    metrics = []

    for _ in range(duration_minutes):
        # 現在の状態を取得
        response = autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        asg = response['AutoScalingGroups'][0]

        # メトリクスを記録
        metric = {
            'timestamp': datetime.utcnow(),
            'desired_capacity': asg['DesiredCapacity'],
            'current_capacity': len(asg['Instances']),
            'instances_in_service': len([i for i in asg['Instances']
                                        if i['LifecycleState'] == 'InService'])
        }
        metrics.append(metric)

        print(f"[{metric['timestamp']}] Desired: {metric['desired_capacity']}, "
              f"Current: {metric['current_capacity']}, "
              f"InService: {metric['instances_in_service']}")

        time.sleep(60)

    # 分析
    analyze_scaling_performance(metrics)

    return metrics

def analyze_scaling_performance(metrics):
    """
    スケーリング性能を分析
    """
    print("\n=== スケーリング性能分析 ===")

    # 平均スケールアウト時間
    scale_out_times = []
    for i in range(1, len(metrics)):
        if metrics[i]['desired_capacity'] > metrics[i-1]['desired_capacity']:
            # スケールアウト開始
            for j in range(i, len(metrics)):
                if metrics[j]['instances_in_service'] >= metrics[j]['desired_capacity']:
                    duration = (metrics[j]['timestamp'] - metrics[i]['timestamp']).total_seconds()
                    scale_out_times.append(duration)
                    print(f"スケールアウト所要時間: {duration}秒")
                    break

    if scale_out_times:
        avg_scale_out = sum(scale_out_times) / len(scale_out_times)
        print(f"平均スケールアウト時間: {avg_scale_out:.1f}秒")

        if avg_scale_out > 300:
            print("⚠️ 警告: スケールアウトが遅い（5分以上）")
            print("  対策: ウォームプール、より高速なAMI、事前ウォーミング")

    # キャパシティの安定性
    capacity_changes = sum(1 for i in range(1, len(metrics))
                          if metrics[i]['desired_capacity'] != metrics[i-1]['desired_capacity'])

    print(f"キャパシティ変更回数: {capacity_changes}")

    if capacity_changes > len(metrics) * 0.3:
        print("⚠️ 警告: 頻繁なスケーリング（フラッピング）")
        print("  対策: クールダウン期間の延長、ターゲット値の調整")

# 使用例
if __name__ == '__main__':
    metrics = monitor_scaling_behavior('web-app-asg', duration_minutes=30)
```

## ベストプラクティス（2025年版）

### 1. ハイブリッドスケーリング戦略

**推奨**: 予測スケーリング + ターゲット追跡の組み合わせ

```bash
# 1. 予測スケーリングで事前準備（週次・日次パターン）
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name predictive-scaling \
    --policy-type PredictiveScaling \
    --predictive-scaling-configuration '{
        "MetricSpecifications": [{
            "TargetValue": 50.0,
            "PredefinedMetricPairSpecification": {
                "PredefinedMetricType": "ASGCPUUtilization"
            }
        }],
        "Mode": "ForecastAndScale",
        "SchedulingBufferTime": 600
    }'

# 2. ターゲット追跡で予期しない変動に対応
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name cpu-target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0
    }'
```

**理由**:
- 予測スケーリングは過去14日間のデータから今後2日間を予測
- ターゲット追跡は予測外のスパイクに即座に対応
- 組み合わせることで、コスト効率と可用性を両立

### 2. 詳細モニタリングの有効化

```bash
# Launch Templateで詳細モニタリングを有効化
aws ec2 modify-launch-template \
    --launch-template-id lt-0123456789abcdef0 \
    --default-version '$Latest' \
    --launch-template-data '{
        "Monitoring": {"Enabled": true}
    }'
```

**重要性**:
- デフォルトの5分間隔 → 1分間隔に変更
- より迅速なスケーリング判断が可能
- 追加コスト: $2.10/月/インスタンス（低コスト）

### 3. ウォームプール（Warm Pool）の活用

```bash
# ウォームプールの設定（2025年推奨）
aws autoscaling put-warm-pool \
    --auto-scaling-group-name web-app-asg \
    --max-group-prepared-capacity 5 \
    --min-size 2 \
    --pool-state Stopped \
    --instance-reuse-policy '{
        "ReuseOnScaleIn": true
    }'
```

**メリット**:
- インスタンス起動時間を大幅短縮（数分 → 数秒）
- Stopped状態ならEBSコストのみ（EC2コストなし）
- スケールイン時にインスタンスをプールに戻して再利用

### 4. 複数メトリクスの活用

```bash
# ALBのリクエスト数とCPU使用率の両方を監視
# メトリクス1: ALBターゲットあたりのリクエスト数
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name alb-request-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ALBRequestCountPerTarget",
            "ResourceLabel": "app/my-alb/50dc6c495c0c9188/targetgroup/my-tg/cbf133c568e0d028"
        },
        "TargetValue": 1000.0
    }'

# メトリクス2: CPU使用率
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name cpu-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0
    }'
```

**ポイント**: どちらかの条件を満たせばスケールアウト（論理OR）

### 5. インスタンスタイプの柔軟性

```bash
# 複数のインスタンスタイプとAZを指定
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-app-asg \
    --mixed-instances-policy file://mixed-instances-policy.json \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 3

# mixed-instances-policy.json
cat > mixed-instances-policy.json << 'EOF'
{
  "LaunchTemplate": {
    "LaunchTemplateSpecification": {
      "LaunchTemplateName": "web-app-template",
      "Version": "$Latest"
    },
    "Overrides": [
      {"InstanceType": "t3.medium", "WeightedCapacity": "1"},
      {"InstanceType": "t3a.medium", "WeightedCapacity": "1"},
      {"InstanceType": "t3.large", "WeightedCapacity": "2"}
    ]
  },
  "InstancesDistribution": {
    "OnDemandBaseCapacity": 2,
    "OnDemandPercentageAboveBaseCapacity": 50,
    "SpotAllocationStrategy": "price-capacity-optimized"
  }
}
EOF
```

**メリット**:
- Spot Instancesで最大90%コスト削減
- キャパシティ不足のリスク軽減
- 複数のインスタンスファミリーで可用性向上

### 6. ライフサイクルフックの活用

```bash
# スケールアウト時のライフサイクルフック（アプリケーション準備）
aws autoscaling put-lifecycle-hook \
    --lifecycle-hook-name instance-launching-hook \
    --auto-scaling-group-name web-app-asg \
    --lifecycle-transition autoscaling:EC2_INSTANCE_LAUNCHING \
    --default-result CONTINUE \
    --heartbeat-timeout 300 \
    --notification-target-arn arn:aws:sns:ap-northeast-1:123456789012:asg-lifecycle

# スケールイン時のライフサイクルフック（グレースフルシャットダウン）
aws autoscaling put-lifecycle-hook \
    --lifecycle-hook-name instance-terminating-hook \
    --auto-scaling-group-name web-app-asg \
    --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
    --default-result CONTINUE \
    --heartbeat-timeout 300 \
    --notification-target-arn arn:aws:sns:ap-northeast-1:123456789012:asg-lifecycle
```

**用途**:
- インスタンス起動時にアプリケーションのウォームアップ
- キャッシュの事前ロード
- 終了時の接続ドレイニング、ログの退避

## よくある落とし穴と対策

### 1. フラッピング（頻繁なスケールイン/アウト）

**症状**: 数分おきにインスタンスが追加・削除される

**原因**:
- ターゲット値が厳しすぎる
- クールダウン期間が短い
- メトリクスの粒度が細かすぎる

**対策**:

```bash
# スケールインのクールダウン期間を延長
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name cpu-tracking-stable \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0,
        "ScaleInCooldown": 600,
        "ScaleOutCooldown": 180
    }'
```

**ポイント**: スケールインは慎重に（600秒）、スケールアウトは迅速に（180秒）

### 2. 予測スケーリングの初期設定ミス

**症状**: 予測スケーリングが期待通りに機能しない

**原因**:
- Auto Scaling作成直後に設定（24時間のデータ不足）
- Mode設定の誤解（ForecastOnly vs ForecastAndScale）

**対策**:

```bash
# 1. まずForecastOnlyモードで様子を見る（1週間）
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name predictive-test \
    --policy-type PredictiveScaling \
    --predictive-scaling-configuration '{
        "MetricSpecifications": [{
            "TargetValue": 50.0,
            "PredefinedMetricPairSpecification": {
                "PredefinedMetricType": "ASGCPUUtilization"
            }
        }],
        "Mode": "ForecastOnly"
    }'

# 2. CloudWatchで予測精度を確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/AutoScaling \
    --metric-name PredictiveScalingLoadForecast \
    --dimensions Name=AutoScalingGroupName,Value=web-app-asg \
    --start-time 2025-01-15T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 3600 \
    --statistics Average

# 3. 精度が良ければForecastAndScaleに変更
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name predictive-active \
    --policy-type PredictiveScaling \
    --predictive-scaling-configuration '{
        "MetricSpecifications": [{
            "TargetValue": 50.0,
            "PredefinedMetricPairSpecification": {
                "PredefinedMetricType": "ASGCPUUtilization"
            }
        }],
        "Mode": "ForecastAndScale",
        "SchedulingBufferTime": 600
    }'
```

### 3. データベースがボトルネックに

**症状**: EC2はスケールするがアプリケーション全体のパフォーマンスが改善しない

**原因**: RDSやDynamoDBのキャパシティがボトルネック

**対策**:

```bash
# DynamoDBのAuto Scalingも同時に設定
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id table/users \
    --scalable-dimension dynamodb:table:ReadCapacityUnits \
    --min-capacity 5 \
    --max-capacity 1000

aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id table/users \
    --scalable-dimension dynamodb:table:ReadCapacityUnits \
    --policy-name dynamodb-read-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "DynamoDBReadCapacityUtilization"
        }
    }'

# RDSの場合はRead Replicaの追加を検討
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-read-replica-1 \
    --source-db-instance-identifier mydb \
    --db-instance-class db.r6g.large \
    --availability-zone ap-northeast-1c
```

### 4. セッション管理の問題

**症状**: ユーザーがスケールイン時にログアウトされる

**原因**: セッションがローカルインスタンスに保存されている

**対策**:

```python
"""
セッションをElastiCacheで管理（ステートレス化）
"""
from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)

# ElastiCache Redisでセッション管理
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(
    'redis://my-elasticache.abc123.0001.apne1.cache.amazonaws.com:6379'
)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = 'your-secret-key'

Session(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return f'Welcome back, user {session["user_id"]}'
    else:
        session['user_id'] = generate_user_id()
        return f'New session created: {session["user_id"]}'
```

**代替案**: ALBのSticky Sessions

```bash
# ALBターゲットグループでSticky Sessionsを有効化
aws elbv2 modify-target-group-attributes \
    --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:targetgroup/web-app-tg/abcdef1234567890 \
    --attributes \
        Key=stickiness.enabled,Value=true \
        Key=stickiness.type,Value=lb_cookie \
        Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

**注意**: Sticky Sessionsはスケールインのリスクがあるため、可能な限りステートレス化を推奨

### 5. バーストパフォーマンスインスタンス（T3/T4g）のクレジット枯渇

**症状**: スケーリング後もパフォーマンスが低い

**原因**: T3/T4gインスタンスのCPUクレジットが枯渇

**対策**:

```bash
# CPUクレジット残高を監視
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUCreditBalance \
    --dimensions Name=AutoScalingGroupName,Value=web-app-asg \
    --start-time 2025-01-20T00:00:00Z \
    --end-time 2025-01-21T00:00:00Z \
    --period 300 \
    --statistics Average

# アラームを設定
aws cloudwatch put-metric-alarm \
    --alarm-name asg-cpu-credit-low \
    --alarm-description "T3 instances running low on CPU credits" \
    --metric-name CPUCreditBalance \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 100 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=AutoScalingGroupName,Value=web-app-asg

# 解決策: Unlimitedモードまたは別のインスタンスファミリーへ変更
aws ec2 modify-instance-credit-specification \
    --instance-credit-specification '[
        {
            "InstanceId": "i-1234567890abcdef0",
            "CpuCredits": "unlimited"
        }
    ]'
```

**長期的解決**: 持続的な高負荷ならM/C/Rファミリーに変更

## 判断ポイント

### スケーリング戦略の選択マトリクス

| トラフィックパターン | 推奨戦略 | 代替戦略 |
|-------------------|---------|---------|
| 予測可能（日次/週次） | **予測スケーリング** + ターゲット追跡 | スケジュールスケーリング |
| 予測不可能（ランダム） | **ターゲット追跡** + ステップスケーリング | ターゲット追跡のみ |
| 急激なスパイク | **ステップスケーリング** + ウォームプール | ターゲット追跡（低い目標値） |
| 営業時間のみ | **スケジュールスケーリング** | 予測スケーリング |
| イベント駆動 | **イベントブリッジ + Lambda** → SetDesiredCapacity | ステップスケーリング |

### ターゲット値の選び方

```python
"""
ワークロードタイプ別の推奨ターゲット値
"""

RECOMMENDED_TARGET_VALUES = {
    'web_application': {
        'cpu': 50.0,  # バランス型
        'alb_request_count': 1000,  # インスタンスあたり
        'network_in': 5_000_000  # 5 MB/s
    },
    'api_backend': {
        'cpu': 40.0,  # より低く設定（レイテンシ重視）
        'alb_request_count': 500,
        'response_time': 200  # ミリ秒
    },
    'batch_processing': {
        'cpu': 70.0,  # より高く設定（コスト重視）
        'queue_depth': 100  # SQSキューの深さ
    },
    'data_streaming': {
        'network_out': 10_000_000,  # 10 MB/s
        'active_connections': 1000
    }
}

def get_recommended_target(workload_type, metric):
    """
    ワークロードタイプとメトリクスに基づいて推奨ターゲット値を取得
    """
    return RECOMMENDED_TARGET_VALUES.get(workload_type, {}).get(metric)

# 使用例
target_cpu = get_recommended_target('api_backend', 'cpu')
print(f"API Backend の推奨CPU目標値: {target_cpu}%")
```

### インスタンスミックスの判断

```bash
# コスト重視（Spotの比率を高く）
cat > cost-optimized-mix.json << 'EOF'
{
  "InstancesDistribution": {
    "OnDemandBaseCapacity": 2,
    "OnDemandPercentageAboveBaseCapacity": 20,
    "SpotAllocationStrategy": "price-capacity-optimized"
  }
}
EOF

# 可用性重視（On-Demandの比率を高く）
cat > availability-optimized-mix.json << 'EOF'
{
  "InstancesDistribution": {
    "OnDemandBaseCapacity": 5,
    "OnDemandPercentageAboveBaseCapacity": 80,
    "SpotAllocationStrategy": "capacity-optimized"
  }
}
EOF

# バランス型
cat > balanced-mix.json << 'EOF'
{
  "InstancesDistribution": {
    "OnDemandBaseCapacity": 3,
    "OnDemandPercentageAboveBaseCapacity": 50,
    "SpotAllocationStrategy": "price-capacity-optimized"
  }
}
EOF
```

### スケールイン保護の判断

```bash
# 重要なインスタンスをスケールインから保護
# ユースケース: マスターノード、データ収集中のインスタンス

aws autoscaling set-instance-protection \
    --instance-ids i-1234567890abcdef0 \
    --auto-scaling-group-name web-app-asg \
    --protected-from-scale-in

# 一時的な保護（処理完了後に解除）
# Lambda関数で自動化
cat > protect_instance.py << 'EOF'
import boto3

def lambda_handler(event, context):
    """
    長時間実行タスクの開始時にインスタンスを保護
    """
    instance_id = event['instance_id']
    asg_name = event['asg_name']

    autoscaling = boto3.client('autoscaling')

    # 保護を有効化
    autoscaling.set_instance_protection(
        InstanceIds=[instance_id],
        AutoScalingGroupName=asg_name,
        ProtectedFromScaleIn=True
    )

    # DynamoDBにタスクIDと共に記録
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('protected-instances')
    table.put_item(Item={
        'instance_id': instance_id,
        'task_id': event['task_id'],
        'protection_start': context.get_remaining_time_in_millis()
    })

    return {'statusCode': 200, 'message': 'Instance protected'}
EOF
```

## 検証ポイント

### 1. スケーリング速度のテスト

```bash
# ロードテストツール（Apache Bench）でトラフィック増加をシミュレート
ab -n 100000 -c 100 https://your-app.example.com/

# スケーリングアクティビティを監視
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name web-app-asg \
    --max-records 10 \
    --output table

# 期待値:
# - スケールアウト開始までの時間: 1-3分
# - InService状態までの時間: 3-5分（ウォームプールなし）、30秒-1分（ウォームプール使用）
```

### 2. 予測スケーリングの精度確認

```python
"""
予測スケーリングの精度を評価
"""
import boto3
from datetime import datetime, timedelta
import pandas as pd

def evaluate_predictive_scaling_accuracy(asg_name, days=7):
    """
    予測スケーリングの精度を評価
    """
    cloudwatch = boto3.client('cloudwatch')

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    # 実際の負荷を取得
    actual_load = cloudwatch.get_metric_statistics(
        Namespace='AWS/AutoScaling',
        MetricName='GroupDesiredCapacity',
        Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    # 予測値を取得
    predicted_load = cloudwatch.get_metric_statistics(
        Namespace='AWS/AutoScaling',
        MetricName='PredictiveScalingLoadForecast',
        Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    # データフレームに変換
    actual_df = pd.DataFrame(actual_load['Datapoints'])
    predicted_df = pd.DataFrame(predicted_load['Datapoints'])

    # マージして比較
    merged = pd.merge(
        actual_df[['Timestamp', 'Average']].rename(columns={'Average': 'Actual'}),
        predicted_df[['Timestamp', 'Average']].rename(columns={'Average': 'Predicted'}),
        on='Timestamp'
    )

    # 精度メトリクスを計算
    merged['Error'] = merged['Actual'] - merged['Predicted']
    merged['AbsError'] = merged['Error'].abs()
    merged['PercentError'] = (merged['AbsError'] / merged['Actual']) * 100

    print("=== 予測スケーリング精度評価 ===")
    print(f"平均絶対誤差 (MAE): {merged['AbsError'].mean():.2f} インスタンス")
    print(f"平均パーセント誤差 (MAPE): {merged['PercentError'].mean():.2f}%")
    print(f"最大誤差: {merged['AbsError'].max():.2f} インスタンス")

    # 判定基準
    if merged['PercentError'].mean() < 10:
        print("✅ 優秀: 予測精度が高い（10%未満）")
    elif merged['PercentError'].mean() < 20:
        print("⚠️  良好: 予測精度は許容範囲（10-20%）")
    else:
        print("❌ 要改善: 予測精度が低い（20%以上）")
        print("   対策: ターゲット値の調整、より長い履歴データの蓄積")

    return merged

# 使用例
if __name__ == '__main__':
    df = evaluate_predictive_scaling_accuracy('web-app-asg', days=14)
```

### 3. コスト効率の検証

```bash
# Cost Explorerで過去30日間のAuto Scalingコストを確認
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=TAG,Key=aws:autoscaling:groupName \
    --filter file://cost-filter.json

# cost-filter.json
cat > cost-filter.json << 'EOF'
{
  "Tags": {
    "Key": "aws:autoscaling:groupName",
    "Values": ["web-app-asg"]
  }
}
EOF

# Spot Instancesの節約額を計算
aws ec2 describe-spot-price-history \
    --instance-types t3.medium \
    --start-time 2025-01-01T00:00:00 \
    --end-time 2025-01-31T23:59:59 \
    --product-descriptions "Linux/UNIX" \
    --query 'SpotPriceHistory[*].[Timestamp,SpotPrice]' \
    --output table
```

### 4. ヘルスチェックの妥当性

```bash
# ELBヘルスチェックの設定確認
aws elbv2 describe-target-health \
    --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:targetgroup/web-app-tg/abcdef1234567890

# 不健全なインスタンスの詳細を確認
aws autoscaling describe-auto-scaling-instances \
    --query 'AutoScalingInstances[?HealthStatus==`UNHEALTHY`]' \
    --output table

# ヘルスチェック猶予期間の適切性を検証
# 期待値: アプリケーション起動時間 + 30-60秒のバッファ
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names web-app-asg \
    --query 'AutoScalingGroups[0].HealthCheckGracePeriod'
```

### 5. 接続ドレイニングの確認

```bash
# ALBのターゲットグループ設定を確認
aws elbv2 describe-target-group-attributes \
    --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:targetgroup/web-app-tg/abcdef1234567890 \
    --query 'Attributes[?Key==`deregistration_delay.timeout_seconds`]'

# 推奨値: 30-300秒（アプリケーションの接続処理時間による）

# ライフサイクルフックのタイムアウトと整合性を確認
aws autoscaling describe-lifecycle-hooks \
    --auto-scaling-group-name web-app-asg \
    --query 'LifecycleHooks[?LifecycleTransition==`autoscaling:EC2_INSTANCE_TERMINATING`]'
```

## 他のスキルとの統合

### CloudWatchスキルとの統合

```bash
# カスタムメトリクスをCloudWatchに送信
aws cloudwatch put-metric-data \
    --namespace WebApp/Metrics \
    --metric-name ActiveConnections \
    --value 150 \
    --dimensions AutoScalingGroupName=web-app-asg,InstanceId=i-1234567890abcdef0

# このメトリクスをAuto Scalingで使用
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-app-asg \
    --policy-name custom-metric-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "CustomizedMetricSpecification": {
            "MetricName": "ActiveConnections",
            "Namespace": "WebApp/Metrics",
            "Statistic": "Average"
        },
        "TargetValue": 100.0
    }'
```

### Lambda スキルとの統合

```python
"""
Lambda関数でカスタムスケーリングロジックを実装
例: ビジネスメトリクス（注文数、同時ユーザー数）に基づくスケーリング
"""
import boto3
import os

def lambda_handler(event, context):
    """
    CloudWatch Eventから定期的に呼ばれる（例: 1分ごと）
    ビジネスメトリクスに基づいてAuto Scalingを調整
    """
    autoscaling = boto3.client('autoscaling')
    cloudwatch = boto3.client('cloudwatch')

    asg_name = os.environ['ASG_NAME']

    # カスタムメトリクスを取得（例: アクティブユーザー数）
    response = cloudwatch.get_metric_statistics(
        Namespace='WebApp/Business',
        MetricName='ActiveUsers',
        StartTime=datetime.utcnow() - timedelta(minutes=5),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )

    if response['Datapoints']:
        active_users = response['Datapoints'][0]['Average']

        # ビジネスルール: 1インスタンスあたり1000ユーザー
        required_capacity = max(2, int(active_users / 1000) + 1)

        # Desired Capacityを更新
        autoscaling.set_desired_capacity(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=required_capacity,
            HonorCooldown=True
        )

        print(f"Active users: {active_users}, Set capacity to: {required_capacity}")

    return {'statusCode': 200}
```

### EventBridge スキルとの統合

```bash
# 特定のイベント（マーケティングキャンペーン開始など）でスケールアウト
aws events put-rule \
    --name marketing-campaign-start \
    --event-pattern '{
        "source": ["custom.marketing"],
        "detail-type": ["Campaign Started"],
        "detail": {
            "campaign-type": ["flash-sale"]
        }
    }'

aws events put-targets \
    --rule marketing-campaign-start \
    --targets '[
        {
            "Id": "1",
            "Arn": "arn:aws:lambda:ap-northeast-1:123456789012:function:scale-out-for-campaign",
            "Input": "{\"asg_name\": \"web-app-asg\", \"target_capacity\": 20}"
        }
    ]'
```

### Systems Manager スキルとの統合

```bash
# Systems Manager Automationでスケーリング後の設定を自動化
aws ssm create-document \
    --name ConfigureNewWebInstance \
    --document-type Automation \
    --content file://automation-doc.json

# automation-doc.json
cat > automation-doc.json << 'EOF'
{
  "schemaVersion": "0.3",
  "description": "Configure newly launched web instances",
  "parameters": {
    "InstanceId": {
      "type": "String",
      "description": "Instance ID to configure"
    }
  },
  "mainSteps": [
    {
      "name": "waitForInstanceRunning",
      "action": "aws:waitForAwsResourceProperty",
      "inputs": {
        "Service": "ec2",
        "Api": "DescribeInstances",
        "InstanceIds": ["{{ InstanceId }}"],
        "PropertySelector": "$.Reservations[0].Instances[0].State.Name",
        "DesiredValues": ["running"]
      }
    },
    {
      "name": "runConfigurationCommands",
      "action": "aws:runCommand",
      "inputs": {
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": ["{{ InstanceId }}"],
        "Parameters": {
          "commands": [
            "yum update -y",
            "systemctl restart nginx",
            "aws s3 cp s3://config-bucket/app-config.json /etc/app/config.json"
          ]
        }
      }
    }
  ]
}
EOF
```

## リソース

### 公式ドキュメント

- [AWS Auto Scaling Documentation](https://docs.aws.amazon.com/autoscaling/)
- [EC2 Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/)
- [Application Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/application/userguide/)
- [Predictive Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-predictive-scaling.html)
- [Target Tracking Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)

### ベストプラクティスガイド

- [Scaling Plans Best Practices](https://docs.aws.amazon.com/autoscaling/plans/userguide/best-practices-for-scaling-plans.html)
- [AWS Well-Architected Framework - Performance Efficiency](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/)
- [Cost Optimization with Auto Scaling](https://aws.amazon.com/blogs/compute/cost-optimization-for-kubernetes-on-aws/)

### ツールとライブラリ

- [AWS CLI Auto Scaling Commands](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/index.html)
- [Boto3 Auto Scaling Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/autoscaling.html)
- [Terraform AWS Auto Scaling](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group)
- [CDK Auto Scaling Module](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_autoscaling-readme.html)

### モニタリングとトラブルシューティング

- [CloudWatch Metrics for Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-monitoring-features.html)
- [Troubleshooting Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/CHAP_Troubleshooting.html)
- [Auto Scaling Activity History](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-verify-scaling-activity.html)

### 学習リソース

- [AWS Auto Scaling Workshop](https://catalog.workshops.aws/well-architected-cost-optimization/)
- [AWS Skill Builder - Auto Scaling](https://explore.skillbuilder.aws/learn)
- [YouTube: AWS Auto Scaling Deep Dive](https://www.youtube.com/results?search_query=aws+auto+scaling+deep+dive)
