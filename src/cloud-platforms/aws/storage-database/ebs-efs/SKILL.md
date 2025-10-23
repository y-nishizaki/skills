---
name: aws-ebs-efs
description: AWS EBS（Elastic Block Store）とEFS（Elastic File System）を使用してEC2インスタンス用のブロックストレージとファイルシステムを管理する方法
---

# AWS EBS/EFS スキル

## 概要

Amazon EBS（Elastic Block Store）とEFS（Elastic File System）は、EC2インスタンス向けのストレージソリューションです。EBSはブロックレベルストレージでEC2インスタンスに直接アタッチし、EFSは複数のEC2インスタンスから同時アクセス可能なネットワークファイルシステムです。

### 2025年の重要なアップデート

- **EBS gp3**: デフォルト推奨（gp2より20%安く、パフォーマンスが独立調整可能）
- **EBS io2 Block Express**: 最大256,000 IOPS、4,000 MB/秒スループット
- **EFS Intelligent-Tiering**: 自動的にInfrequent Accessクラスに移行
- **EFS Elastic Throughput**: ワークロードに応じて自動スケーリング

## 主な使用ケース

### 1. EBS gp3（汎用SSD）- 2025年デフォルト

ほとんどのワークロードに適した汎用SSDです。

```bash
# gp3ボリュームの作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 100 \
    --volume-type gp3 \
    --iops 3000 \
    --throughput 125 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=web-app-data}]'

# IOPSとスループットを独立に調整（gp3の利点）
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --iops 10000 \
    --throughput 500

# インスタンスにアタッチ
aws ec2 attach-volume \
    --volume-id vol-0123456789abcdef0 \
    --instance-id i-1234567890abcdef0 \
    --device /dev/sdf
```

**gp3の特徴**:
- ベースライン: 3,000 IOPS、125 MB/秒（サイズに依存しない）
- 最大: 16,000 IOPS、1,000 MB/秒
- コスト: $0.08/GB/月（gp2は$0.10）

### 2. EBS io2/io2 Block Express（プロビジョンドIOPS SSD）

高性能データベースやミッションクリティカルなワークロード向けです。

```bash
# io2ボリュームの作成（99.999%の耐久性）
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 500 \
    --volume-type io2 \
    --iops 50000 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=database-prod}]'

# io2 Block Expressの作成（最大256,000 IOPS）
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 1000 \
    --volume-type io2 \
    --iops 100000 \
    --throughput 4000 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=high-perf-db}]'

# マルチアタッチの有効化（複数のEC2から同時アクセス）
aws ec2 modify-volume-attribute \
    --volume-id vol-0123456789abcdef0 \
    --multi-attach-enabled
```

**io2の特徴**:
- 最大64,000 IOPS（標準）、256,000 IOPS（Block Express）
- 99.999%の耐久性（io1は99.9%）
- 500 IOPS/GB（io1は50 IOPS/GB）

### 3. EBS スループット最適化HDD（st1）

ビッグデータ、データウェアハウス、ログ処理向けです。

```bash
# st1ボリュームの作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --size 2000 \
    --volume-type st1 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=bigdata-storage}]'
```

**st1の特徴**:
- 大規模シーケンシャルワークロード向け
- 最大500 IOPS、500 MB/秒
- コスト: $0.045/GB/月（SSDの半額以下）

### 4. EBSスナップショット

バックアップとディザスタリカバリに活用します。

```bash
# スナップショットの作成
aws ec2 create-snapshot \
    --volume-id vol-0123456789abcdef0 \
    --description "Daily backup $(date +%Y-%m-%d)" \
    --tag-specifications 'ResourceType=snapshot,Tags=[{Key=BackupType,Value=daily},{Key=Date,Value=2025-01-22}]'

# スナップショットから新しいボリュームを作成
aws ec2 create-volume \
    --availability-zone ap-northeast-1a \
    --snapshot-id snap-0123456789abcdef0 \
    --volume-type gp3 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=restored-volume}]'

# クロスリージョンコピー（DR）
aws ec2 copy-snapshot \
    --source-region ap-northeast-1 \
    --source-snapshot-id snap-0123456789abcdef0 \
    --destination-region us-west-2 \
    --description "DR copy"

# Data Lifecycle Manager（DLM）で自動バックアップ
aws dlm create-lifecycle-policy \
    --policy-details file://dlm-policy.json

# dlm-policy.json
cat > dlm-policy.json << 'EOF'
{
  "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
  "ResourceTypes": ["VOLUME"],
  "TargetTags": [{"Key": "Backup", "Value": "true"}],
  "Schedules": [{
    "Name": "DailyBackup",
    "CreateRule": {
      "Interval": 24,
      "IntervalUnit": "HOURS",
      "Times": ["03:00"]
    },
    "RetainRule": {
      "Count": 30
    },
    "CopyTags": true
  }]
}
EOF
```

### 5. EFS（Elastic File System）- 共有ファイルストレージ

複数のEC2インスタンスから同時アクセス可能なNFSファイルシステムです。

```bash
# EFSファイルシステムの作成
aws efs create-file-system \
    --performance-mode generalPurpose \
    --throughput-mode elastic \
    --encrypted \
    --tags Key=Name,Value=shared-app-data

# マウントターゲットの作成（各AZ）
aws efs create-mount-target \
    --file-system-id fs-0123456789abcdef0 \
    --subnet-id subnet-12345678 \
    --security-groups sg-0123456789abcdef0

# EC2インスタンスからマウント
sudo mkdir -p /mnt/efs
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport \
    fs-0123456789abcdef0.efs.ap-northeast-1.amazonaws.com:/ /mnt/efs

# /etc/fstabに追加（永続化）
echo "fs-0123456789abcdef0.efs.ap-northeast-1.amazonaws.com:/ /mnt/efs nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0" | sudo tee -a /etc/fstab
```

### 6. EFS Intelligent-Tiering（2025年推奨）

アクセス頻度に基づいて自動的にストレージクラスを最適化します。

```bash
# ライフサイクルポリシーの設定
aws efs put-lifecycle-configuration \
    --file-system-id fs-0123456789abcdef0 \
    --lifecycle-policies file://lifecycle-policy.json

# lifecycle-policy.json
cat > lifecycle-policy.json << 'EOF'
[
  {
    "TransitionToIA": "AFTER_30_DAYS"
  },
  {
    "TransitionToPrimaryStorageClass": "AFTER_1_ACCESS"
  }
]
EOF
```

**コスト削減効果**:
- EFS Standard: $0.30/GB/月
- EFS Infrequent Access: $0.025/GB/月（92%削減）
- 30日間アクセスなし → 自動移行

### 7. EFS Elastic Throughput（2025年推奨）

ワークロードに応じて自動的にスループットをスケーリングします。

```bash
# Elastic Throughputモードに変更
aws efs update-file-system \
    --file-system-id fs-0123456789abcdef0 \
    --throughput-mode elastic

# 従来のProvisioned Throughputモード
aws efs update-file-system \
    --file-system-id fs-0123456789abcdef0 \
    --throughput-mode provisioned \
    --provisioned-throughput-in-mibps 100
```

**Elastic Throughputのメリット**:
- 自動スケーリング: 最大3 GiB/秒（読み取り）、1 GiB/秒（書き込み）
- コスト効率: 使った分だけ課金
- 管理不要: キャパシティプランニング不要

### 8. EBS vs EFS 選択ガイド

```bash
# ユースケース別の選択

# 1. 単一EC2インスタンス用 → EBS
# データベース、アプリケーションサーバー
aws ec2 create-volume --volume-type gp3 --size 100 --availability-zone ap-northeast-1a

# 2. 複数EC2インスタンスで共有 → EFS
# Webサーバーのコンテンツ、共有ファイルストレージ
aws efs create-file-system --performance-mode generalPurpose

# 3. 高IOPS要件 → EBS io2
# ミッションクリティカルなデータベース
aws ec2 create-volume --volume-type io2 --iops 50000 --size 500

# 4. コスト最適化（低頻度アクセス） → EFS IA
# アーカイブ、バックアップ
aws efs put-lifecycle-configuration --lifecycle-policies TransitionToIA=AFTER_30_DAYS
```

## 思考プロセス

EBS/EFSのストレージ戦略を設計する際の段階的な思考プロセスです。

### フェーズ1: ストレージタイプの選択

```python
"""
EBS vs EFS 選択ロジック
"""

def choose_storage_type(requirements):
    """
    要件に基づいて最適なストレージタイプを選択
    """
    # 複数インスタンスから同時アクセスが必要
    if requirements.concurrent_access:
        if requirements.performance_mode == 'max_io':
            return {
                'type': 'EFS',
                'performance_mode': 'maxIO',
                'throughput_mode': 'elastic'
            }
        else:
            return {
                'type': 'EFS',
                'performance_mode': 'generalPurpose',
                'throughput_mode': 'elastic'
            }

    # 単一インスタンス用ブロックストレージ
    if requirements.iops > 16000:
        return {
            'type': 'EBS',
            'volume_type': 'io2',
            'iops': requirements.iops
        }
    elif requirements.workload_type == 'sequential':
        return {
            'type': 'EBS',
            'volume_type': 'st1'  # Throughput Optimized HDD
        }
    else:
        return {
            'type': 'EBS',
            'volume_type': 'gp3',
            'iops': 3000,
            'throughput': 125
        }

# 使用例
class Requirements:
    concurrent_access = False
    iops = 5000
    workload_type = 'random'
    performance_mode = 'general_purpose'

requirements = Requirements()
storage = choose_storage_type(requirements)
print(f"推奨ストレージ: {storage}")
# 出力: {'type': 'EBS', 'volume_type': 'gp3', 'iops': 3000, 'throughput': 125}
```

### フェーズ2: EBSボリュームのサイジング

```python
"""
EBSボリュームのサイジングと最適化
"""

def size_ebs_volume(workload_characteristics):
    """
    ワークロード特性に基づいてEBSボリュームをサイジング
    """
    # データベースワークロード
    if workload_characteristics.workload_type == 'database':
        # IOPS要件を満たす最小サイズを計算
        if workload_characteristics.required_iops > 16000:
            # io2が必要
            min_size_for_iops = workload_characteristics.required_iops / 500  # 500 IOPS/GB
            recommended_size = max(
                min_size_for_iops,
                workload_characteristics.data_size_gb * 1.5  # 50%のバッファ
            )
            return {
                'volume_type': 'io2',
                'size_gb': int(recommended_size),
                'iops': workload_characteristics.required_iops,
                'cost_per_month': recommended_size * 0.125 + workload_characteristics.required_iops * 0.065
            }
        else:
            # gp3で十分
            return {
                'volume_type': 'gp3',
                'size_gb': int(workload_characteristics.data_size_gb * 1.5),
                'iops': min(workload_characteristics.required_iops, 16000),
                'throughput': min(workload_characteristics.required_throughput_mbps, 1000),
                'cost_per_month': workload_characteristics.data_size_gb * 1.5 * 0.08
            }

    # ビッグデータワークロード
    elif workload_characteristics.workload_type == 'bigdata':
        return {
            'volume_type': 'st1',
            'size_gb': workload_characteristics.data_size_gb,
            'max_throughput_mbps': 500,
            'cost_per_month': workload_characteristics.data_size_gb * 0.045
        }

    # 一般的なワークロード
    else:
        return {
            'volume_type': 'gp3',
            'size_gb': workload_characteristics.data_size_gb,
            'iops': 3000,
            'throughput': 125,
            'cost_per_month': workload_characteristics.data_size_gb * 0.08
        }

# 使用例
class WorkloadCharacteristics:
    workload_type = 'database'
    required_iops = 25000
    required_throughput_mbps = 500
    data_size_gb = 500

workload = WorkloadCharacteristics()
volume_config = size_ebs_volume(workload)
print(f"推奨ボリューム構成: {volume_config}")
```

### フェーズ3: バックアップ戦略

```bash
# DLMでEBSスナップショットを自動化
cat > dlm-comprehensive-policy.json << 'EOF'
{
  "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
  "Description": "Comprehensive backup strategy",
  "State": "ENABLED",
  "ResourceTypes": ["VOLUME"],
  "TargetTags": [{"Key": "Backup", "Value": "true"}],
  "Schedules": [
    {
      "Name": "HourlyBackup",
      "CreateRule": {
        "Interval": 1,
        "IntervalUnit": "HOURS"
      },
      "RetainRule": {
        "Count": 24
      },
      "TagsToAdd": [{"Key": "Type", "Value": "Hourly"}],
      "CopyTags": true
    },
    {
      "Name": "DailyBackup",
      "CreateRule": {
        "Interval": 24,
        "IntervalUnit": "HOURS",
        "Times": ["03:00"]
      },
      "RetainRule": {
        "Count": 7
      },
      "TagsToAdd": [{"Key": "Type", "Value": "Daily"}],
      "CopyTags": true,
      "CrossRegionCopyRules": [{
        "TargetRegion": "us-west-2",
        "Encrypted": true,
        "RetainRule": {
          "Interval": 7,
          "IntervalUnit": "DAYS"
        }
      }]
    },
    {
      "Name": "WeeklyBackup",
      "CreateRule": {
        "CronExpression": "cron(0 3 ? * SUN *)"
      },
      "RetainRule": {
        "Count": 4
      },
      "TagsToAdd": [{"Key": "Type", "Value": "Weekly"}],
      "CopyTags": true
    }
  ]
}
EOF

aws dlm create-lifecycle-policy \
    --execution-role-arn arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole \
    --description "Comprehensive backup strategy" \
    --state ENABLED \
    --policy-details file://dlm-comprehensive-policy.json
```

### フェーズ4: パフォーマンス監視

```bash
# CloudWatchメトリクスでEBSパフォーマンスを監視
aws cloudwatch get-metric-statistics \
    --namespace AWS/EBS \
    --metric-name VolumeReadOps \
    --dimensions Name=VolumeId,Value=vol-0123456789abcdef0 \
    --start-time 2025-01-21T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 300 \
    --statistics Sum

# バーストバランスの監視（gp2のみ）
aws cloudwatch get-metric-statistics \
    --namespace AWS/EBS \
    --metric-name BurstBalance \
    --dimensions Name=VolumeId,Value=vol-0123456789abcdef0 \
    --start-time 2025-01-21T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 300 \
    --statistics Average

# アラームの設定
aws cloudwatch put-metric-alarm \
    --alarm-name ebs-low-burst-balance \
    --alarm-description "EBS burst balance is low" \
    --metric-name BurstBalance \
    --namespace AWS/EBS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 20 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=VolumeId,Value=vol-0123456789abcdef0
```

## ベストプラクティス（2025年版）

### 1. gp3をデフォルトに

**推奨**: 新規ボリュームはすべてgp3を使用

```bash
# gp3の利点
# 1. gp2より20%安い
# 2. IOPSとスループットを独立に調整可能
# 3. 3,000 IOPS、125 MB/秒のベースライン（サイズに依存しない）

# gp2からgp3への移行
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --volume-type gp3
```

**コスト比較**:
- 100 GB、3,000 IOPS
  - gp2: $10/月
  - gp3: $8/月（20%削減）

### 2. EBS暗号化の有効化

```bash
# アカウントレベルでデフォルト暗号化を有効化
aws ec2 enable-ebs-encryption-by-default --region ap-northeast-1

# デフォルトKMSキーの設定
aws ec2 modify-ebs-default-kms-key-id \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012

# 既存ボリュームのスナップショットを暗号化してコピー
aws ec2 copy-snapshot \
    --source-region ap-northeast-1 \
    --source-snapshot-id snap-0123456789abcdef0 \
    --encrypted \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

### 3. EBSスナップショットのライフサイクル管理

```python
"""
スナップショットコスト最適化スクリプト
"""
import boto3
from datetime import datetime, timedelta

def cleanup_old_snapshots(retention_days=30):
    """
    古いスナップショットを削除してコストを削減
    """
    ec2 = boto3.client('ec2')

    # すべてのスナップショットを取得
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for snapshot in snapshots:
        snapshot_time = snapshot['StartTime'].replace(tzinfo=None)

        # DLMで管理されているスナップショットはスキップ
        if any(tag['Key'] == 'aws:dlm:lifecycle-policy-id' for tag in snapshot.get('Tags', [])):
            continue

        # 古いスナップショットを削除
        if snapshot_time < cutoff_date:
            print(f"削除: {snapshot['SnapshotId']} (作成日: {snapshot_time})")
            try:
                ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            except Exception as e:
                print(f"エラー: {e}")

# 使用例
cleanup_old_snapshots(retention_days=90)
```

### 4. EFSのコスト最適化

```bash
# Intelligent-Tieringの有効化
aws efs put-lifecycle-configuration \
    --file-system-id fs-0123456789abcdef0 \
    --lifecycle-policies \
        TransitionToIA=AFTER_30_DAYS \
        TransitionToPrimaryStorageClass=AFTER_1_ACCESS

# アクセスポイントで細かいアクセス制御
aws efs create-access-point \
    --file-system-id fs-0123456789abcdef0 \
    --posix-user Uid=1001,Gid=1001 \
    --root-directory Path=/data,CreationInfo={OwnerUid=1001,OwnerGid=1001,Permissions=755} \
    --tags Key=Name,Value=app-data-access-point
```

## よくある落とし穴と対策

### 1. gp2のバーストバランス枯渇

**症状**: 小さいボリュームでパフォーマンスが突然低下

**原因**: gp2のバーストクレジットが枯渇

**対策**:

```bash
# gp3に移行（バーストの概念なし）
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --volume-type gp3 \
    --iops 3000
```

### 2. EBSボリュームのサイズ不足

**症状**: ディスク容量不足

**対策**:

```bash
# ボリュームサイズの拡張（ダウンタイムなし）
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --size 200

# ファイルシステムの拡張（EC2インスタンス内）
sudo growpart /dev/xvdf 1
sudo resize2fs /dev/xvdf1  # ext4の場合
sudo xfs_growfs /mnt/data  # XFSの場合
```

### 3. EFSパフォーマンスの低下

**症状**: EFSのスループットが期待より低い

**原因**: Provisioned Throughputモードで容量不足

**対策**:

```bash
# Elastic Throughputモードに変更
aws efs update-file-system \
    --file-system-id fs-0123456789abcdef0 \
    --throughput-mode elastic
```

### 4. スナップショットコストの肥大化

**症状**: スナップショットコストが予想外に高い

**原因**: 古いスナップショットが削除されていない

**対策**: DLMで自動ライフサイクル管理（既出）

## 判断ポイント

### EBSボリュームタイプ選択マトリクス

| ワークロード | 推奨ボリュームタイプ | IOPS | スループット | コスト（GB/月） |
|------------|------------------|------|------------|----------------|
| 汎用（デフォルト） | **gp3** | 3,000-16,000 | 125-1,000 MB/s | $0.08 |
| データベース（高IOPS） | **io2** | 最大64,000 | 最大1,000 MB/s | $0.125 + IOPS課金 |
| データベース（超高IOPS） | **io2 Block Express** | 最大256,000 | 最大4,000 MB/s | $0.125 + IOPS課金 |
| ビッグデータ | **st1** | 最大500 | 最大500 MB/s | $0.045 |
| アーカイブ | **sc1** | 最大250 | 最大250 MB/s | $0.015 |
| ブート | **gp3** | 3,000 | 125 MB/s | $0.08 |

### EBS vs EFS 選択基準

| 要件 | EBS | EFS |
|-----|-----|-----|
| 同時アクセス | 単一インスタンス（io2 Multi-Attachは例外） | 数千の同時接続 |
| パフォーマンス | 最大256,000 IOPS | スケーラブル（最大3 GiB/秒） |
| 可用性 | 単一AZ | 複数AZ |
| コスト（GB/月） | $0.08（gp3） | $0.30（Standard）、$0.025（IA） |
| ユースケース | データベース、ブート | Webサーバー、共有ストレージ |

## 検証ポイント

### 1. EBSパフォーマンステスト

```bash
# fioでIOPSベンチマーク
sudo fio --name=randread --ioengine=libaio --iodepth=32 --rw=randread \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 --group_reporting \
    --filename=/mnt/ebs/testfile

# スループットベンチマーク
sudo fio --name=seqread --ioengine=libaio --iodepth=32 --rw=read \
    --bs=128k --direct=1 --size=1G --numjobs=4 --runtime=60 --group_reporting \
    --filename=/mnt/ebs/testfile
```

### 2. EFSパフォーマンステスト

```bash
# NFSマウントオプションの確認
mount | grep nfs4

# 期待値:
# rsize=1048576,wsize=1048576

# パフォーマンステスト
dd if=/dev/zero of=/mnt/efs/testfile bs=1M count=1000 oflag=direct
```

## 他のスキルとの統合

### EC2スキルとの統合

```bash
# Launch Templateで EBSを自動設定
cat > launch-template.json << 'EOF'
{
  "BlockDeviceMappings": [
    {
      "DeviceName": "/dev/xvda",
      "Ebs": {
        "VolumeType": "gp3",
        "VolumeSize": 30,
        "Iops": 3000,
        "Throughput": 125,
        "DeleteOnTermination": true,
        "Encrypted": true
      }
    },
    {
      "DeviceName": "/dev/sdf",
      "Ebs": {
        "VolumeType": "gp3",
        "VolumeSize": 100,
        "DeleteOnTermination": false,
        "Encrypted": true
      }
    }
  ]
}
EOF
```

### Auto Scalingスキルとの統合

```bash
# EFSを使用してAuto Scalingグループ間でデータ共有
# User Dataでマウント
cat > user-data.sh << 'EOF'
#!/bin/bash
yum install -y amazon-efs-utils
mkdir -p /mnt/efs
mount -t efs -o tls fs-0123456789abcdef0:/ /mnt/efs
echo "fs-0123456789abcdef0:/ /mnt/efs efs _netdev,tls 0 0" >> /etc/fstab
EOF
```

## リソース

### 公式ドキュメント

- [Amazon EBS Documentation](https://docs.aws.amazon.com/ebs/)
- [Amazon EFS Documentation](https://docs.aws.amazon.com/efs/)
- [EBS Volume Types](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html)
- [Data Lifecycle Manager](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/snapshot-lifecycle.html)

### ベストプラクティス

- [EBS Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-best-practices.html)
- [EFS Best Practices](https://docs.aws.amazon.com/efs/latest/ug/best-practices.html)

### ツールとライブラリ

- [AWS CLI EBS Commands](https://docs.aws.amazon.com/cli/latest/reference/ec2/index.html)
- [Boto3 EBS Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
