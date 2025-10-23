---
name: "AWS EC2 (Elastic Compute Cloud)"
description: "AWSの仮想サーバーサービス。インスタンスタイプ選択、EBS、AMI、セキュリティグループ、キーペア、スケーリング、コスト最適化に関する思考プロセスを提供"
---

# AWS EC2 (Elastic Compute Cloud)

## このスキルを使う場面

- 仮想サーバーの起動と管理
- インスタンスタイプの選択
- AMI（マシンイメージ）の作成と管理
- EBSボリュームの設定
- セキュリティグループの設定
- Auto Scalingグループの構築
- コスト最適化（Reserved Instances、Spot Instances）

## EC2とは

Amazon Elastic Compute Cloud (EC2)は、AWSクラウド内で仮想サーバー（インスタンス）を提供するサービス。必要に応じてコンピューティング容量を拡張・縮小でき、初期投資なしで数分でサーバーを起動できる。

### EC2の主要機能

**柔軟なインスタンスタイプ:**

- 600種類以上のインスタンスタイプ（2025年時点）
- 用途に応じた最適な構成を選択
- CPU、メモリ、ストレージ、ネットワーク性能のバランス

**複数の料金モデル:**

- オンデマンド：時間単位の従量課金
- Reserved Instances：1〜3年の予約で最大75%割引
- Savings Plans：柔軟なコミットメントで最大72%割引
- Spot Instances：未使用キャパシティで最大90%割引

**高い可用性:**

- マルチAZ配置
- Auto Scaling
- Elastic Load Balancing統合

## インスタンスタイプ

### インスタンスファミリーの分類

**汎用（General Purpose）:**

- **T系列（T3, T4g）**: バースト可能、コスト効率が高い
  - Webサーバー、開発環境
  - ベースライン性能＋CPUクレジット

- **M系列（M7i, M8i）**: バランス型
  - アプリケーションサーバー
  - 中規模データベース
  - 2025年のM8i-flexは15%の価格パフォーマンス向上

**コンピュート最適化（Compute Optimized）:**

- **C系列（C7i, C8i）**: 高いCPU性能
  - バッチ処理
  - 科学計算
  - ゲームサーバー

**メモリ最適化（Memory Optimized）:**

- **R系列（R7i, R8i）**: 大容量メモリ
  - インメモリデータベース
  - リアルタイム分析
  - 大規模キャッシュ

- **X系列（X8g）**: 超大容量メモリ
  - SAP HANA
  - Apache Spark

**ストレージ最適化（Storage Optimized）:**

- **I系列**: 高IOPS
  - NoSQLデータベース
  - データウェアハウス

- **D系列**: 高密度ストレージ
  - 分散ファイルシステム
  - MapReduce

**高速コンピューティング（Accelerated Computing）:**

- **P系列**: GPU（機械学習）
- **G系列**: GPU（グラフィックス）
- **Inf系列**: 機械学習推論

### 2025年の新しいインスタンスタイプ

**設定可能な帯域幅:**

M8a, M8g, M8i, C8i, R8i などの新しいインスタンスタイプは、ネットワーク性能とEBS性能の帯域幅の重み付けを設定可能。

```bash
# 帯域幅の設定
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-bandwidth-weighting NetworkOnly
```

## 思考プロセス

### フェーズ1: インスタンスタイプの選択

**ステップ1: ワークロードの分析**

ワークロードの特性を理解する:

- [ ] CPU要件（コア数、クロック速度）
- [ ] メモリ要件
- [ ] ストレージ要件（容量、IOPS）
- [ ] ネットワーク要件（帯域幅）
- [ ] GPU要件（該当する場合）

**ステップ2: インスタンスファミリーの選択**

```bash
# 利用可能なインスタンスタイプを確認
aws ec2 describe-instance-types \
    --filters "Name=current-generation,Values=true" \
    --query 'InstanceTypes[*].[InstanceType,VCpuInfo.DefaultVCpus,MemoryInfo.SizeInMiB]' \
    --output table
```

**ワークロード別の推奨:**

| ワークロード | 推奨インスタンス | 理由 |
|------------|----------------|------|
| Webサーバー | T3, T4g | バースト可能、コスト効率 |
| アプリケーションサーバー | M7i, M8i | バランス型 |
| データベース（小〜中） | M7i, R7i | メモリ重視 |
| データベース（大） | R8i, X8g | 大容量メモリ |
| バッチ処理 | C7i, C8i | CPU重視 |
| 機械学習トレーニング | P4, P5 | GPU |
| 機械学習推論 | Inf2 | 推論最適化 |

**ステップ3: サイズの決定**

小さく始めて、必要に応じてスケール:

```bash
# 小さいサイズから開始
# t3.micro → t3.small → t3.medium → t3.large

# インスタンスタイプの変更
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-type t3.medium
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

**移行条件:**

- [ ] ワークロードを分析した
- [ ] インスタンスファミリーを選択した
- [ ] 初期サイズを決定した
- [ ] コスト試算を実施した

### フェーズ2: インスタンスの起動

**ステップ1: AMIの選択**

```bash
# 最新のAmazon Linux 2023 AMIを取得
aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-*-x86_64" \
              "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text

# Ubuntu 22.04 LTS
aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text
```

**AMI選択のポイント:**

- **HVM AMI推奨**: Enhanced Networkingに対応
- **EBS-backed推奨**: 柔軟性が高い、永続化可能
- **最新のAMI使用**: セキュリティパッチ適用済み

**ステップ2: ネットワーク設定**

```bash
# VPCとサブネットの選択
# パブリックサブネット: インターネットアクセスが必要
# プライベートサブネット: 内部アクセスのみ

aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=vpc-12345678" \
    --query 'Subnets[*].[SubnetId,AvailabilityZone,CidrBlock]' \
    --output table
```

**ステップ3: セキュリティグループの設定**

```bash
# セキュリティグループの作成
aws ec2 create-security-group \
    --group-name web-server-sg \
    --description "Security group for web servers" \
    --vpc-id vpc-12345678

# HTTPSアクセスを許可
aws ec2 authorize-security-group-ingress \
    --group-id sg-903004f8 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# SSHアクセスを許可（特定のIPのみ）
aws ec2 authorize-security-group-ingress \
    --group-id sg-903004f8 \
    --protocol tcp \
    --port 22 \
    --cidr 203.0.113.0/24
```

**セキュリティグループのベストプラクティス:**

- 最小権限の原則（必要最小限のポートのみ開放）
- SSHは特定のIPアドレスのみ許可
- アウトバウンドルールも明示的に設定
- 説明を必ず記載

**ステップ4: インスタンスの起動**

```bash
# EC2インスタンスの起動
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name my-key-pair \
    --security-group-ids sg-903004f8 \
    --subnet-id subnet-6e7f829e \
    --count 1 \
    --monitoring Enabled=true \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=WebServer},{Key=Environment,Value=Production}]' \
    --block-device-mappings '[
      {
        "DeviceName": "/dev/xvda",
        "Ebs": {
          "VolumeSize": 30,
          "VolumeType": "gp3",
          "Iops": 3000,
          "Throughput": 125,
          "DeleteOnTermination": true,
          "Encrypted": true
        }
      }
    ]'
```

**移行条件:**

- [ ] AMIを選択した
- [ ] VPCとサブネットを設定した
- [ ] セキュリティグループを設定した
- [ ] インスタンスを起動した
- [ ] タグを設定した

### フェーズ3: EBSボリュームの管理

**ステップ1: EBSボリュームタイプの選択**

**gp3（汎用SSD、推奨）:**

- 最新世代
- 独立してIOPS・スループットを設定可能
- gp2より20%安価
- ほとんどのワークロードに推奨

```bash
# gp3ボリュームの作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 100 \
    --volume-type gp3 \
    --iops 3000 \
    --throughput 125 \
    --encrypted \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=DataVolume}]'
```

**io2（プロビジョンドIOPS SSD）:**

- ミッションクリティカルなワークロード
- 99.999%の耐久性
- 高いIOPS要件（最大64,000 IOPS）

**st1（スループット最適化HDD）:**

- ビッグデータ
- ログ処理
- 低コスト

**sc1（コールドHDD）:**

- アーカイブ
- 最低コスト

**ステップ2: ボリュームのアタッチ**

```bash
# ボリュームをインスタンスにアタッチ
aws ec2 attach-volume \
    --volume-id vol-1234567890abcdef0 \
    --instance-id i-1234567890abcdef0 \
    --device /dev/sdf

# インスタンス内でマウント
sudo mkfs -t ext4 /dev/xvdf
sudo mkdir /data
sudo mount /dev/xvdf /data

# 永続化（/etc/fstabに追加）
echo '/dev/xvdf /data ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
```

**ステップ3: スナップショットの作成**

```bash
# スナップショットの作成
aws ec2 create-snapshot \
    --volume-id vol-1234567890abcdef0 \
    --description "Daily backup $(date +%Y-%m-%d)" \
    --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Type,Value=Backup}]'

# 古いスナップショットの削除（30日以上前）
aws ec2 describe-snapshots \
    --owner-ids self \
    --filters "Name=volume-id,Values=vol-1234567890abcdef0" \
    --query "Snapshots[?StartTime<'$(date -d '30 days ago' --iso-8601)'].SnapshotId" \
    --output text | xargs -r aws ec2 delete-snapshot --snapshot-id
```

**移行条件:**

- [ ] 適切なEBSボリュームタイプを選択した
- [ ] ボリュームをアタッチした
- [ ] スナップショット戦略を実装した
- [ ] 暗号化を有効化した

### フェーズ4: AMIの作成と管理

**ステップ1: カスタムAMIの作成**

```bash
# インスタンスからAMIを作成
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "WebServer-Golden-$(date +%Y%m%d)" \
    --description "Production web server template" \
    --no-reboot \
    --tag-specifications 'ResourceType=image,Tags=[{Key=Environment,Value=Production}]'
```

**AMI作成のベストプラクティス:**

- **no-reboot推奨**: データ整合性のため（本番環境）
- **定期的な更新**: セキュリティパッチ適用済みAMIを維持
- **タグ付け**: バージョン管理、環境識別
- **古いAMIの削除**: コスト削減

**ステップ2: AMIの共有**

```bash
# 特定のアカウントとAMIを共有
aws ec2 modify-image-attribute \
    --image-id ami-0c55b159cbfafe1f0 \
    --launch-permission "Add=[{UserId=123456789012}]"

# 組織全体と共有（AWS Organizations）
aws ec2 modify-image-attribute \
    --image-id ami-0c55b159cbfafe1f0 \
    --launch-permission "Add=[{OrganizationArn=arn:aws:organizations::123456789012:organization/o-xxxxxxxxxx}]"
```

**ステップ3: クロスリージョンコピー**

```bash
# AMIを別リージョンにコピー
aws ec2 copy-image \
    --source-region ap-northeast-1 \
    --source-image-id ami-0c55b159cbfafe1f0 \
    --region us-east-1 \
    --name "WebServer-Golden-20250101-DR" \
    --encrypted
```

**移行条件:**

- [ ] カスタムAMIを作成した
- [ ] AMI管理プロセスを確立した
- [ ] DR用のクロスリージョンコピーを設定した（該当する場合）

### フェーズ5: コスト最適化

**ステップ1: 適切な料金モデルの選択**

**オンデマンド:**
- 開発・テスト環境
- 短期的なワークロード
- 予測不可能なワークロード

**Reserved Instances:**
- 24/7稼働の本番環境
- 最大75%割引
- 1〜3年のコミットメント

```bash
# RI購入推奨の確認
aws ce get-reservation-purchase-recommendation \
    --service "Amazon Elastic Compute Cloud - Compute" \
    --lookback-period-in-days SIXTY_DAYS \
    --term-in-years ONE_YEAR \
    --payment-option NO_UPFRONT
```

**Savings Plans:**
- 柔軟なコミットメント
- インスタンスタイプ変更可能
- 最大72%割引

**Spot Instances:**
- バッチ処理
- CI/CDワーカー
- ステートレスなワークロード
- 最大90%割引

```bash
# Spotインスタンスの起動
aws ec2 request-spot-instances \
    --spot-price "0.05" \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification '{
      "ImageId": "ami-0c55b159cbfafe1f0",
      "InstanceType": "t3.medium",
      "KeyName": "my-key-pair",
      "SecurityGroupIds": ["sg-903004f8"],
      "SubnetId": "subnet-6e7f829e"
    }'
```

**ステップ2: インスタンスのスケジューリング**

開発環境を夜間・週末に自動停止:

```bash
# Lambda関数で実装（EventBridgeルール）
# 平日夜19:00に停止
aws events put-rule \
    --name stop-dev-instances \
    --schedule-expression "cron(0 19 ? * MON-FRI *)"

# 平日朝9:00に起動
aws events put-rule \
    --name start-dev-instances \
    --schedule-expression "cron(0 9 ? * MON-FRI *)"
```

**ステップ3: 適正サイズ化**

```bash
# Compute Optimizerの推奨を取得
aws compute-optimizer get-ec2-instance-recommendations \
    --instance-arns arn:aws:ec2:region:account-id:instance/i-1234567890abcdef0

# CloudWatchでCPU使用率を確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-31T23:59:59Z \
    --period 3600 \
    --statistics Average,Maximum
```

**移行条件:**

- [ ] 適切な料金モデルを選択した
- [ ] スケジューリングを実装した（該当する場合）
- [ ] 適正サイズ化を実施した
- [ ] コスト削減を測定した

## ベストプラクティス

### セキュリティ

**1. OSとデータの分離:**

```bash
# OS用ボリュームとデータ用ボリュームを分離
# /dev/xvda: OS（削除時に終了）
# /dev/xvdf: データ（削除時に保持）
```

**2. EBS暗号化:**

すべてのEBSボリュームとスナップショットを暗号化:

```bash
# デフォルト暗号化の有効化
aws ec2 enable-ebs-encryption-by-default --region ap-northeast-1

# 暗号化されたボリュームの作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 100 \
    --encrypted \
    --kms-key-id arn:aws:kms:region:account-id:key/key-id
```

**3. 詳細モニタリング:**

```bash
# 詳細モニタリングの有効化（1分間隔）
aws ec2 monitor-instances --instance-ids i-1234567890abcdef0
```

**4. IMDSv2の使用:**

```bash
# IMDSv2を必須化（セキュリティ強化）
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-put-response-hop-limit 1
```

### パフォーマンス

**1. EBS最適化インスタンス:**

最新のインスタンスタイプはデフォルトでEBS最適化:

```bash
# EBS最適化の確認
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0 \
    --query 'Reservations[*].Instances[*].EbsOptimized'
```

**2. Enhanced Networkingの使用:**

HVM AMIを使用し、Enhanced Networking対応のインスタンスタイプを選択。

**3. Placement Groupの活用:**

低レイテンシが必要な場合:

```bash
# Cluster Placement Groupの作成
aws ec2 create-placement-group \
    --group-name low-latency-cluster \
    --strategy cluster

# Placement Group内でインスタンスを起動
aws ec2 run-instances \
    --placement "GroupName=low-latency-cluster"
```

## よくある落とし穴

1. **インスタンスタイプの過剰プロビジョニング**
   - ❌ 最初から大型インスタンスを選択
   - ✅ 小さく始めて、必要に応じてスケール

2. **セキュリティグループの過剰な開放**
   - ❌ 0.0.0.0/0からSSHを許可
   - ✅ 特定のIPアドレスのみ許可

3. **EBSボリュームの暗号化忘れ**
   - ❌ 暗号化なしでボリュームを作成
   - ✅ デフォルト暗号化を有効化

4. **スナップショットの放置**
   - ❌ 古いスナップショットを削除しない
   - ✅ ライフサイクルポリシーで自動削除

5. **タグ付けの欠如**
   - ❌ リソースにタグを付けない
   - ✅ Name、Environment、Projectなどのタグを必ず設定

6. **停止インスタンスの放置**
   - ❌ 停止中のインスタンスを放置（EBS課金継続）
   - ✅ 不要なインスタンスは終了

## 判断のポイント

### インスタンスタイプ選択

| ワークロード | CPU | メモリ | 推奨ファミリー |
|------------|-----|--------|---------------|
| Webサーバー | 低 | 低 | T3, T4g |
| アプリケーションサーバー | 中 | 中 | M7i, M8i |
| データベース | 中 | 高 | R7i, R8i |
| バッチ処理 | 高 | 低 | C7i, C8i |
| 機械学習 | GPU | 高 | P4, P5 |

### EBSボリュームタイプ選択

| 用途 | IOPS要件 | 推奨タイプ |
|-----|---------|----------|
| 汎用（ほとんどのワークロード） | 〜16,000 | gp3 |
| データベース（高性能） | 16,000+ | io2 |
| ビッグデータ | 高スループット | st1 |
| アーカイブ | 低頻度アクセス | sc1 |

### 料金モデル選択

| ワークロード | 稼働パターン | 推奨モデル |
|------------|-------------|----------|
| 本番環境 | 24/7 | Reserved Instances / Savings Plans |
| 開発環境 | 営業時間のみ | オンデマンド + スケジューリング |
| バッチ処理 | 断続的 | Spot Instances |
| 予測不可能 | 変動大 | オンデマンド |

## 検証ポイント

### インスタンス起動

- [ ] 適切なインスタンスタイプを選択した
- [ ] セキュリティグループを適切に設定した
- [ ] タグを設定した
- [ ] 詳細モニタリングを有効化した
- [ ] IMDSv2を有効化した

### ストレージ

- [ ] EBSボリュームを暗号化した
- [ ] 適切なボリュームタイプを選択した
- [ ] スナップショット戦略を実装した
- [ ] OSとデータを分離した

### セキュリティ

- [ ] 最小権限のセキュリティグループ
- [ ] SSHキーペアを安全に管理
- [ ] IAMロールをアタッチ
- [ ] セキュリティパッチを適用

### コスト最適化

- [ ] 適切な料金モデルを選択した
- [ ] 未使用リソースを削減した
- [ ] 適正サイズ化を実施した
- [ ] コスト監視を設定した

## 他スキルとの連携

### ec2 + auto-scaling

EC2とAuto Scalingの組み合わせ:

1. ec2で適切なインスタンスタイプを選択
2. auto-scalingで需要に応じて自動スケール
3. 高可用性とコスト効率を実現

### ec2 + iam

EC2とIAMの組み合わせ:

1. iamでインスタンスロールを作成
2. ec2でIAMロールをアタッチ
3. アクセスキー不要でAWSサービスにアクセス

### ec2 + cloudwatch

EC2とCloudWatchの組み合わせ:

1. ec2で詳細モニタリングを有効化
2. cloudwatchでメトリクスを監視
3. アラームによる自動対応

## リソース

### 公式ドキュメント

- [Amazon EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [EC2 Instance Types](https://aws.amazon.com/ec2/instance-types/)
- [EC2 Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html)

### 料金情報

- [EC2 Pricing](https://aws.amazon.com/ec2/pricing/)
- [Spot Instance Pricing](https://aws.amazon.com/ec2/spot/pricing/)
- [Reserved Instances](https://aws.amazon.com/ec2/pricing/reserved-instances/)

### ツール

- [EC2 Instance Selector](https://github.com/aws/amazon-ec2-instance-selector)
- [AWS Compute Optimizer](https://aws.amazon.com/compute-optimizer/)
