---
name: "AWS コスト最適化基礎"
description: "AWSコストの理解と最適化戦略。Savings Plans、Reserved Instances、オンデマンド料金、コスト管理ツール、ベストプラクティスに基づいたコスト最適化の思考プロセスを提供"
---

# AWS コスト最適化基礎

## このスキルを使う場面

- AWSコストの削減
- 料金プランの選択（オンデマンド、Reserved Instances、Savings Plans）
- コスト予測と予算管理
- 未使用リソースの特定と削除
- リソースの適正サイズ化
- コスト配分と部門別課金

## AWSの料金モデル

AWSは従量課金制を採用しており、使用した分だけ料金を支払う。初期投資や長期契約は不要で、必要に応じてスケールアップ・ダウンが可能。

### 主要な料金モデル

**1. オンデマンド（On-Demand）:**

- 使用した時間分だけ課金
- 初期投資不要
- 柔軟性が高い
- 最も高価

**2. Savings Plans:**

- 1年または3年の使用量コミットメント
- 最大72%の割引
- 柔軟性が高い（インスタンスタイプの変更可能）
- 2025年のAWS推奨モデル

**3. Reserved Instances (RI):**

- 1年または3年のインスタンス予約
- 最大75%の割引
- 特定のインスタンスタイプとリージョンに固定
- Savings Plansより割引率が高い場合がある

**4. スポットインスタンス:**

- 未使用のEC2キャパシティを利用
- 最大90%の割引
- 中断される可能性がある
- バッチ処理、データ分析に適している

## Savings Plans vs Reserved Instances

### Savings Plans（2025年推奨）

**特徴:**

- 柔軟性が高い（インスタンスタイプ、OS、リージョン変更可能）
- EC2、Lambda、Fargateに適用可能
- 時間単位のコミットメント（例：$10/時間）
- 自動的に最適な割引を適用

**タイプ:**

**1. Compute Savings Plans:**

- 最も柔軟性が高い
- 約66%の割引
- インスタンスファミリー、サイズ、AZ、リージョン、OS、テナンシーを変更可能
- Lambda、Fargateにも適用

**2. EC2 Instance Savings Plans:**

- EC2に特化
- 最大72%の割引
- 特定のインスタンスファミリーとリージョンに固定
- サイズ、OS、テナンシーは変更可能

```bash
# Savings Plansの推奨を確認
aws ce get-savings-plans-purchase-recommendation \
    --savings-plans-type COMPUTE_SP \
    --term-in-years ONE_YEAR \
    --payment-option NO_UPFRONT \
    --lookback-period-in-days SIXTY_DAYS

# Savings Plansの購入
# （通常はコンソールから実施）
```

### Reserved Instances

**特徴:**

- 最大75%の割引
- 特定のインスタンスタイプとリージョンに固定
- キャパシティ予約が可能
- Marketplace で売買可能

**タイプ:**

**1. Standard Reserved Instances:**

- 最大割引率（最大75%）
- インスタンスタイプ変更不可
- 長期的に安定したワークロードに最適

**2. Convertible Reserved Instances:**

- 最大54%の割引
- インスタンスファミリー変更可能
- 柔軟性が必要な場合に適している

**3. Scheduled Reserved Instances:**

- 特定の時間帯のみ予約
- 定期的なバッチ処理に適している

```bash
# RIの推奨を確認
aws ce get-reservation-purchase-recommendation \
    --service "Amazon Elastic Compute Cloud - Compute" \
    --lookback-period-in-days SIXTY_DAYS \
    --term-in-years ONE_YEAR \
    --payment-option NO_UPFRONT

# RIの購入
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id <offering-id> \
    --instance-count 1
```

### 2025年の選択ガイド

**Savings Plansを選択する場合:**

- [ ] ワークロードが可変（インスタンスタイプの変更が必要）
- [ ] 複数のAWSコンピュートサービスを使用（EC2、Lambda、Fargate）
- [ ] 自動的なコスト最適化が必要
- [ ] 管理を簡素化したい

**Reserved Instancesを選択する場合:**

- [ ] ワークロードが安定（特定のインスタンスタイプで固定）
- [ ] 特定のAZでキャパシティ予約が必要
- [ ] 特定のインスタンス構成が必要
- [ ] 最大割引率を求める

**ハイブリッドアプローチ（推奨）:**

- ベースラインワークロード: Reserved Instances（最大割引）
- 可変ワークロード: Savings Plans（柔軟性）
- バーストトラフィック: オンデマンド
- 中断可能なワークロード: スポットインスタンス

## 思考プロセス

### フェーズ1: 現状分析

**ステップ1: コスト可視化**

```bash
# Cost Explorerで月別コストを確認
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE

# タグ別のコスト分析
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=TAG,Key=Environment
```

**ステップ2: コストドライバーの特定**

主要なコスト発生源を特定:

- [ ] EC2インスタンス
- [ ] データ転送
- [ ] ストレージ（S3、EBS）
- [ ] データベース（RDS、DynamoDB）
- [ ] ネットワーキング

```bash
# サービス別のコスト内訳
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE \
    --filter file://filter.json
```

**ステップ3: 未使用リソースの特定**

```bash
# 停止中のEC2インスタンス
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=stopped" \
    --query 'Reservations[*].Instances[*].[InstanceId,LaunchTime]'

# アタッチされていないEBSボリューム
aws ec2 describe-volumes \
    --filters "Name=status,Values=available" \
    --query 'Volumes[*].[VolumeId,Size,CreateTime]'

# 未使用のElastic IP
aws ec2 describe-addresses \
    --filters "Name=instance-id,Values=" \
    --query 'Addresses[*].[PublicIp,AllocationId]'

# 空のS3バケット
aws s3 ls | while read bucket; do
    bucket_name=$(echo $bucket | awk '{print $3}')
    objects=$(aws s3 ls s3://$bucket_name --recursive | wc -l)
    if [ $objects -eq 0 ]; then
        echo "Empty bucket: $bucket_name"
    fi
done
```

**移行条件:**

- [ ] コストの可視化を実施した
- [ ] 主要なコストドライバーを特定した
- [ ] 未使用リソースをリストアップした
- [ ] 月次コスト傾向を分析した

### フェーズ2: 適正サイズ化（Right-sizing）

**ステップ1: リソース使用率の分析**

```bash
# CloudWatchでEC2インスタンスのCPU使用率を確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-31T23:59:59Z \
    --period 3600 \
    --statistics Average,Maximum
```

**ステップ2: Compute Optimizerの活用**

```bash
# Compute Optimizerの推奨を取得
aws compute-optimizer get-ec2-instance-recommendations \
    --instance-arns arn:aws:ec2:region:account-id:instance/i-1234567890abcdef0

# Auto Scalingグループの推奨
aws compute-optimizer get-auto-scaling-group-recommendations

# EBS ボリュームの推奨
aws compute-optimizer get-ebs-volume-recommendations
```

**ステップ3: 適正サイズ化の実施**

**過剰プロビジョニングの例:**

- CPU使用率が常に10%以下 → 小さいインスタンスタイプに変更
- メモリ使用率が常に30%以下 → メモリ最適化インスタンスから汎用インスタンスに変更
- ストレージIOPSが未使用 → gp3またはgp2に変更

```bash
# インスタンスタイプの変更
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-type t3.medium
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

**移行条件:**

- [ ] リソース使用率を分析した
- [ ] Compute Optimizerの推奨を確認した
- [ ] 適正サイズ化を実施した
- [ ] コスト削減を測定した

### フェーズ3: コミットメント戦略

**ステップ1: ワークロードの分類**

ワークロードを以下のカテゴリーに分類:

**1. ベースラインワークロード（常時稼働）:**

- 24/7稼働
- 安定した使用量
- Reserved Instances またはSavings Plansが適している

**2. 可変ワークロード:**

- 使用量が変動
- インスタンスタイプの変更が必要
- Savings Plans（Compute）が適している

**3. バーストトラフィック:**

- 短時間の高負荷
- 予測不可能
- オンデマンドが適している

**4. バッチ処理・分析:**

- 中断可能
- 時間制約がゆるい
- スポットインスタンスが適している

**ステップ2: コミットメント戦略の設計**

**1年コミットメント vs 3年コミットメント:**

| 期間 | 割引率 | 適用場面 | リスク |
|-----|-------|---------|-------|
| 1年 | 中（〜40%） | 変化が予想される環境 | 低 |
| 3年 | 高（〜75%） | 安定した長期ワークロード | 中 |

**2025年のベストプラクティス:**

- 1年コミットメントを優先（技術変化が速い）
- AI/MLワークロードの増加に対応
- 段階的なコミットメント（一度に全てコミットしない）

**ステップ3: 支払いオプションの選択**

**全前払い（All Upfront）:**

- 最大割引
- キャッシュフローへの影響大
- 確実に長期使用する場合

**一部前払い（Partial Upfront）:**

- 中程度の割引
- バランスが良い
- 一般的な選択肢

**前払いなし（No Upfront）:**

- 最小割引
- キャッシュフロー重視
- 短期的な視点

```bash
# Savings Plansの推奨を確認（前払いオプション別）
aws ce get-savings-plans-purchase-recommendation \
    --savings-plans-type EC2_INSTANCE_SP \
    --term-in-years ONE_YEAR \
    --payment-option ALL_UPFRONT \
    --lookback-period-in-days SIXTY_DAYS
```

**移行条件:**

- [ ] ワークロードを分類した
- [ ] コミットメント戦略を設計した
- [ ] 支払いオプションを選択した
- [ ] 段階的なコミットメント計画を立てた

### フェーズ4: コスト管理の自動化

**ステップ1: 予算とアラートの設定**

```bash
# 予算の作成
aws budgets create-budget \
    --account-id 123456789012 \
    --budget file://budget.json \
    --notifications-with-subscribers file://notifications.json
```

```json
// budget.json
{
  "BudgetName": "Monthly-Budget",
  "BudgetLimit": {
    "Amount": "1000",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

```json
// notifications.json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "admin@example.com"
    }]
  }
]
```

**ステップ2: コスト異常検出**

```bash
# コスト異常モニターの作成
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
      "MonitorName": "ServiceMonitor",
      "MonitorType": "DIMENSIONAL",
      "MonitorDimension": "SERVICE"
    }'

# 異常検出サブスクリプションの作成
aws ce create-anomaly-subscription \
    --anomaly-subscription '{
      "SubscriptionName": "DailySubscription",
      "Threshold": 100,
      "Frequency": "DAILY",
      "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/12345678-1234-1234-1234-123456789012"],
      "Subscribers": [{
        "Type": "EMAIL",
        "Address": "admin@example.com"
      }]
    }'
```

**ステップ3: 自動シャットダウンの実装**

```bash
# Lambda関数で夜間・週末の開発環境を自動停止

# EventBridgeルールの作成（平日夜19:00に停止）
aws events put-rule \
    --name stop-dev-instances \
    --schedule-expression "cron(0 19 ? * MON-FRI *)" \
    --state ENABLED

# Lambda関数をターゲットとして設定
aws events put-targets \
    --rule stop-dev-instances \
    --targets "Id"="1","Arn"="arn:aws:lambda:region:account-id:function:StopDevInstances"
```

**移行条件:**

- [ ] 予算とアラートを設定した
- [ ] コスト異常検出を有効化した
- [ ] 自動シャットダウンを実装した（該当する場合）
- [ ] タグ付け戦略を確立した

### フェーズ5: 継続的な最適化

**ステップ1: 定期的なレビュー**

月次レビュー項目:

- [ ] コスト傾向の分析
- [ ] 未使用リソースの削除
- [ ] Compute Optimizer推奨の確認
- [ ] Savings Plans / RI のカバレッジ確認
- [ ] タグの整合性確認

```bash
# Savings Plans のカバレッジ確認
aws ce get-savings-plans-coverage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --group-by Type=DIMENSION,Key=SERVICE

# Reserved Instances の使用率確認
aws ce get-reservation-utilization \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --group-by Type=DIMENSION,Key=SERVICE
```

**ステップ2: Trusted Advisorの活用**

```bash
# Trusted Advisor チェック結果の取得
aws support describe-trusted-advisor-checks \
    --language en

# コスト最適化カテゴリーのチェック
aws support describe-trusted-advisor-check-result \
    --check-id Qch7DwouX1  # Low Utilization Amazon EC2 Instances
```

**ステップ3: コスト配分タグの活用**

```bash
# コスト配分タグの有効化
aws ce update-cost-allocation-tags-status \
    --cost-allocation-tags-status '[
      {"TagKey":"Environment","Status":"Active"},
      {"TagKey":"Project","Status":"Active"},
      {"TagKey":"Owner","Status":"Active"}
    ]'

# タグ別のコスト確認
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=TAG,Key=Project
```

**移行条件:**

- [ ] 定期的なレビュープロセスを確立した
- [ ] Trusted Advisorの推奨を実装した
- [ ] コスト配分タグを活用している
- [ ] 継続的な改善プロセスを確立した

## 判断のポイント

### Savings Plans vs Reserved Instances

| 要因 | Savings Plans | Reserved Instances |
|-----|--------------|-------------------|
| 柔軟性 | 高（インスタンスタイプ変更可） | 低（固定） |
| 割引率 | 〜72% | 〜75% |
| 適用範囲 | EC2, Lambda, Fargate | EC2のみ |
| 管理難易度 | 低（自動適用） | 中（手動管理） |
| キャパシティ予約 | なし | あり（オプション） |

### コミットメント期間の選択

| 期間 | 使用場面 | メリット | デメリット |
|-----|---------|---------|----------|
| 1年 | 変化が予想される | 柔軟性、低リスク | 割引率が低い |
| 3年 | 安定した長期ワークロード | 最大割引 | 変更が困難 |

### 支払いオプションの選択

| オプション | 割引率 | キャッシュフロー | 適用場面 |
|----------|-------|----------------|---------|
| 全前払い | 最大 | 初期負担大 | 確実な長期使用 |
| 一部前払い | 中 | バランス | 一般的な選択 |
| 前払いなし | 最小 | 負担最小 | キャッシュフロー重視 |

## よくある落とし穴

1. **すべてを最初からコミット**
   - ❌ 全リソースに3年RIを購入
   - ✅ 段階的にコミットメントを増やす

2. **未使用リソースの放置**
   - ❌ 停止中のインスタンスやEBSを放置
   - ✅ 定期的にクリーンアップ

3. **適正サイズ化の見落とし**
   - ❌ 過剰なスペックのインスタンスを使用
   - ✅ Compute Optimizerの推奨を確認

4. **データ転送コストの見落とし**
   - ❌ リージョン間・AZ間の転送を無視
   - ✅ データ転送を最小化する設計

5. **タグ付けの不備**
   - ❌ リソースにタグを付けない
   - ✅ 一貫したタグ付け戦略を実施

6. **2025年の変更点を見落とし**
   - ❌ 古いRI/SP戦略を継続
   - ✅ 2025年6月1日以降の新しいルールに対応

## ベストプラクティス

### コスト最適化の原則

**1. 適正サイズ化:**

使用率を監視し、過剰なリソースを削減

**2. 弾力性の活用:**

Auto Scalingで需要に応じてリソースを調整

**3. 適切な料金モデル:**

ワークロードに合った料金プランを選択

**4. ストレージの最適化:**

S3 Intelligent-Tiering、EBS gp3の活用

**5. 測定と監視:**

Cost Explorer、Budgets、Trusted Advisorの活用

**6. タグ付けとコスト配分:**

リソースに適切なタグを付けてコストを追跡

## 2025年の重要な変更

### Savings PlansとRIの変更（2025年6月1日）

**影響を受ける対象:**

- マネージドサービスプロバイダー（MSP）
- 複数の顧客アカウントでRI/SPを共有しているリセラー

**主な変更:**

- RI/SPの共有ルールの変更
- 新しい管理モデルへの移行が必要

**対応策:**

- AWS Organizationsの活用
- 新しいコスト管理プロセスの確立

## 検証ポイント

### 現状分析

- [ ] コストの可視化を実施した
- [ ] コストドライバーを特定した
- [ ] 未使用リソースをリストアップした

### 最適化実施

- [ ] 適正サイズ化を実施した
- [ ] Savings Plans / RIを購入した
- [ ] 未使用リソースを削除した

### 継続的な管理

- [ ] 予算とアラートを設定した
- [ ] コスト異常検出を有効化した
- [ ] 定期的なレビュープロセスを確立した
- [ ] タグ付け戦略を実装した

## 他スキルとの連携

### cost-optimization + compute

コスト最適化とコンピュートの組み合わせ:

1. cost-optimizationでコミットメント戦略を立案
2. computeで適切なインスタンスタイプを選択
3. コスト効率の高いインフラを構築

### cost-optimization + auto-scaling

コスト最適化と自動スケーリングの組み合わせ:

1. cost-optimizationで需要パターンを分析
2. auto-scalingで動的にリソースを調整
3. 無駄なコストを削減

### cost-optimization + cloudwatch

コスト最適化と監視の組み合わせ:

1. cloudwatchでリソース使用率を監視
2. cost-optimizationで適正サイズ化を実施
3. 継続的なコスト最適化を実現

## リソース

### 公式ドキュメント

- [AWS Pricing](https://aws.amazon.com/pricing/)
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)
- [Savings Plans](https://aws.amazon.com/savingsplans/)
- [Reserved Instances](https://aws.amazon.com/ec2/pricing/reserved-instances/)

### ツール

- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
- [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/)
- [AWS Compute Optimizer](https://aws.amazon.com/compute-optimizer/)
- [AWS Trusted Advisor](https://aws.amazon.com/premiumsupport/technology/trusted-advisor/)

### 学習リソース

- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
- [AWS Well-Architected Framework - Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
