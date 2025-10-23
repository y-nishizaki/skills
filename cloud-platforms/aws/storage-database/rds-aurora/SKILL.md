---
name: aws-rds-aurora
description: AWS RDS（Relational Database Service）とAuroraを使用してマネージドリレーショナルデータベースを構築し、高可用性、パフォーマンス、スケーラビリティを実現する方法
---

# AWS RDS/Aurora スキル

## 概要

Amazon RDS（Relational Database Service）は、クラウド上でリレーショナルデータベースを簡単に設定、運用、スケールできるマネージドサービスです。Aurora

はAWS独自の高性能クラウドネイティブデータベースで、MySQL/PostgreSQLと互換性があります。

### 2025年の重要なアップデート

- **Aurora Serverless v2**: プロビジョニングとサーバーレスのベストを統合
- **RDS Blue/Green Deployments**: ダウンタイムなしのメジャーバージョンアップグレード
- **RDS Optimized Reads**: 最大2倍のクエリパフォーマンス向上
- **Aurora Global Database**: RPO<1秒、RTO<1分のグローバルレプリケーション

## 主な使用ケース

### 1. Aurora Serverless v2（2025年推奨）

需要に応じて自動的にスケールする次世代データベースです。

```bash
# Aurora Serverless v2クラスターの作成
aws rds create-db-cluster \
    --db-cluster-identifier production-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.05.2 \
    --master-username admin \
    --master-user-password 'SecurePassword123!' \
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \
    --enable-http-endpoint \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "mon:04:00-mon:05:00" \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --db-subnet-group-name my-db-subnet-group

# Serverless v2インスタンスの追加
aws rds create-db-instance \
    --db-instance-identifier production-cluster-instance-1 \
    --db-instance-class db.serverless \
    --engine aurora-mysql \
    --db-cluster-identifier production-cluster

# リードレプリカの追加（別AZ）
aws rds create-db-instance \
    --db-instance-identifier production-cluster-instance-2 \
    --db-instance-class db.serverless \
    --engine aurora-mysql \
    --db-cluster-identifier production-cluster \
    --availability-zone ap-northeast-1c
```

**Serverless v2の特徴**:
- 0.5 ACU～128 ACUの範囲で自動スケーリング
- プロビジョニングと同じパフォーマンス
- コールドスタートなし（<1秒でスケール）
- コスト効率: 使用した分だけ課金

### 2. Aurora Multi-AZ配置

高可用性を実現するマルチAZ構成です。

```bash
# Multi-AZ Aurora クラスターの作成
aws rds create-db-cluster \
    --db-cluster-identifier ha-cluster \
    --engine aurora-postgresql \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password 'SecurePassword123!' \
    --db-subnet-group-name my-db-subnet-group \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --backup-retention-period 30 \
    --preferred-backup-window "03:00-04:00" \
    --enable-cloudwatch-logs-exports '["postgresql"]' \
    --deletion-protection

# プライマリインスタンス（AZ-1a）
aws rds create-db-instance \
    --db-instance-identifier ha-cluster-writer \
    --db-instance-class db.r6g.xlarge \
    --engine aurora-postgresql \
    --db-cluster-identifier ha-cluster \
    --availability-zone ap-northeast-1a \
    --promotion-tier 0

# レプリカ1（AZ-1c）
aws rds create-db-instance \
    --db-instance-identifier ha-cluster-reader-1 \
    --db-instance-class db.r6g.xlarge \
    --engine aurora-postgresql \
    --db-cluster-identifier ha-cluster \
    --availability-zone ap-northeast-1c \
    --promotion-tier 1

# レプリカ2（AZ-1d）
aws rds create-db-instance \
    --db-instance-identifier ha-cluster-reader-2 \
    --db-instance-class db.r6g.large \
    --engine aurora-postgresql \
    --db-cluster-identifier ha-cluster \
    --availability-zone ap-northeast-1d \
    --promotion-tier 2
```

**Promotion Tier戦略**:
- Tier 0-1: プライマリと同じサイズ（フェイルオーバー候補）
- Tier 2以上: 小さいサイズ（読み取り専用）

### 3. Aurora Global Database

グローバルなディザスタリカバリと低レイテンシアクセスを実現します。

```bash
# プライマリリージョンでGlobal Databaseを作成
aws rds create-global-cluster \
    --global-cluster-identifier global-prod-db \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.05.2

# プライマリクラスターを作成してGlobal Databaseに追加
aws rds create-db-cluster \
    --db-cluster-identifier primary-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.05.2 \
    --global-cluster-identifier global-prod-db \
    --master-username admin \
    --master-user-password 'SecurePassword123!' \
    --db-subnet-group-name primary-subnet-group \
    --vpc-security-group-ids sg-primary

# セカンダリリージョン（DR）にクラスターを追加
aws rds create-db-cluster \
    --db-cluster-identifier secondary-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.05.2 \
    --global-cluster-identifier global-prod-db \
    --db-subnet-group-name secondary-subnet-group \
    --vpc-security-group-ids sg-secondary \
    --region us-west-2

# プライマリリージョンでライターインスタンスを作成
aws rds create-db-instance \
    --db-instance-identifier primary-cluster-writer \
    --db-instance-class db.r6g.2xlarge \
    --engine aurora-mysql \
    --db-cluster-identifier primary-cluster

# セカンダリリージョンでリーダーインスタンスを作成（コスト最適化: Serverless v2）
aws rds create-db-instance \
    --db-instance-identifier secondary-cluster-reader \
    --db-instance-class db.serverless \
    --engine aurora-mysql \
    --db-cluster-identifier secondary-cluster \
    --region us-west-2
```

**Global Databaseの特徴**:
- RPO < 1秒（データ損失最小化）
- RTO < 1分（高速フェイルオーバー）
- 最大5つのセカンダリリージョン
- レプリケーションレイテンシ: 通常1秒未満

### 4. RDS MySQL/PostgreSQL（従来型）

Auroraが不要な場合の標準RDSです。

```bash
# RDS MySQLの作成（Multi-AZ）
aws rds create-db-instance \
    --db-instance-identifier mysql-prod \
    --db-instance-class db.m6g.xlarge \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password 'SecurePassword123!' \
    --allocated-storage 500 \
    --storage-type gp3 \
    --iops 12000 \
    --storage-throughput 500 \
    --multi-az \
    --db-subnet-group-name my-db-subnet-group \
    --vpc-security-group-ids sg-0123456789abcdef0 \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --enabled-cloudwatch-logs-exports '["error","general","slowquery"]' \
    --auto-minor-version-upgrade \
    --publicly-accessible false \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678

# Read Replicaの作成
aws rds create-db-instance-read-replica \
    --db-instance-identifier mysql-prod-replica-1 \
    --source-db-instance-identifier mysql-prod \
    --db-instance-class db.m6g.large \
    --availability-zone ap-northeast-1c
```

### 5. RDS Blue/Green Deployments（2025年推奨）

ダウンタイムなしでメジャーバージョンをアップグレードします。

```bash
# Blue/Green Deploymentの作成
aws rds create-blue-green-deployment \
    --blue-green-deployment-name mysql8-upgrade \
    --source-arn arn:aws:rds:ap-northeast-1:123456789012:db:mysql-prod \
    --target-engine-version 8.0.35 \
    --target-db-parameter-group-name mysql80-params

# グリーン環境の検証後、切り替え
aws rds switchover-blue-green-deployment \
    --blue-green-deployment-identifier bgd-0123456789abcdef \
    --switchover-timeout 300

# 検証完了後、ブルー環境を削除
aws rds delete-blue-green-deployment \
    --blue-green-deployment-identifier bgd-0123456789abcdef \
    --delete-target
```

**Blue/Green Deploymentsのメリット**:
- ダウンタイム: 1分未満
- 検証期間中は両環境が並行稼働
- ロールバックが容易（切り替え前なら即座に）

### 6. RDS Proxy

接続プーリングでスケーラビリティを向上させます。

```bash
# RDS Proxyの作成
aws rds create-db-proxy \
    --db-proxy-name production-proxy \
    --engine-family MYSQL \
    --auth '[{
        "AuthScheme": "SECRETS",
        "SecretArn": "arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:db-credentials",
        "IAMAuth": "DISABLED"
    }]' \
    --role-arn arn:aws:iam::123456789012:role/RDSProxyRole \
    --vpc-subnet-ids subnet-12345678 subnet-87654321 \
    --require-tls \
    --idle-client-timeout 1800

# ターゲットグループの作成
aws rds register-db-proxy-targets \
    --db-proxy-name production-proxy \
    --db-cluster-identifiers production-cluster
```

**RDS Proxyの用途**:
- Lambdaなど頻繁に接続/切断するアプリケーション
- 接続数が多いアプリケーション
- フェイルオーバー時間の短縮（65%削減）

### 7. RDSパフォーマンス監視

Performance Insightsで詳細な分析を行います。

```bash
# Performance Insightsの有効化
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --apply-immediately

# Enhanced Monitoringの有効化
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --monitoring-interval 60 \
    --monitoring-role-arn arn:aws:iam::123456789012:role/rds-monitoring-role \
    --apply-immediately

# スロークエリログの確認
aws rds download-db-log-file-portion \
    --db-instance-identifier mysql-prod \
    --log-file-name slowquery/mysql-slowquery.log \
    --output text
```

### 8. RDSバックアップとリストア

自動バックアップとスナップショットを活用します。

```bash
# 手動スナップショットの作成
aws rds create-db-snapshot \
    --db-instance-identifier mysql-prod \
    --db-snapshot-identifier mysql-prod-manual-$(date +%Y%m%d)

# スナップショットからのリストア
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mysql-prod-restored \
    --db-snapshot-identifier mysql-prod-manual-20250122 \
    --db-instance-class db.m6g.xlarge

# ポイントインタイムリカバリ
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mysql-prod \
    --target-db-instance-identifier mysql-prod-pitr \
    --restore-time 2025-01-22T10:30:00Z

# クロスリージョンスナップショットコピー
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:ap-northeast-1:123456789012:snapshot:mysql-prod-manual-20250122 \
    --target-db-snapshot-identifier mysql-prod-dr-20250122 \
    --region us-west-2 \
    --kms-key-id arn:aws:kms:us-west-2:123456789012:key/87654321
```

## 思考プロセス

RDS/Auroraのデータベース戦略を設計する際の段階的な思考プロセスです。

### フェーズ1: RDS vs Aurora の選択

```python
"""
RDS vs Aurora 選択ロジック
"""

def choose_database_service(requirements):
    """
    要件に基づいてRDS vs Auroraを選択
    """
    # Aurora推奨ケース
    if requirements.high_availability_critical:
        return {
            'service': 'Aurora',
            'reason': 'Multi-AZ自動フェイルオーバー、6コピーレプリケーション'
        }

    if requirements.read_heavy_workload:
        return {
            'service': 'Aurora',
            'reason': '最大15個のリードレプリカ、レプリケーションラグ<10ms'
        }

    if requirements.global_deployment:
        return {
            'service': 'Aurora Global Database',
            'reason': 'グローバルレプリケーション、RPO<1秒、RTO<1分'
        }

    if requirements.unpredictable_workload:
        return {
            'service': 'Aurora Serverless v2',
            'reason': '自動スケーリング、コスト最適化'
        }

    # RDS推奨ケース
    if requirements.specific_engine_version:
        return {
            'service': 'RDS',
            'reason': 'エンジンバージョンの柔軟性が高い'
        }

    if requirements.cost_sensitive and requirements.workload_size == 'small':
        return {
            'service': 'RDS',
            'reason': '小規模ワークロードでコスト効率が良い'
        }

    # デフォルト推奨
    return {
        'service': 'Aurora',
        'reason': '2025年のデフォルト推奨（パフォーマンス、可用性、拡張性）'
    }

# 使用例
class Requirements:
    high_availability_critical = True
    read_heavy_workload = True
    global_deployment = False
    unpredictable_workload = False
    specific_engine_version = False
    cost_sensitive = False
    workload_size = 'medium'

requirements = Requirements()
recommendation = choose_database_service(requirements)
print(f"推奨サービス: {recommendation}")
```

### フェーズ2: インスタンスサイジング

```python
"""
RDS/Auroraインスタンスのサイジング
"""

def size_database_instance(workload_characteristics):
    """
    ワークロード特性に基づいてインスタンスをサイジング
    """
    # メモリ要件を計算
    # ルール: アクティブなデータセット + バッファプール + 接続オーバーヘッド
    active_dataset_gb = workload_characteristics.active_dataset_gb
    buffer_pool_gb = active_dataset_gb * 1.2  # 20%のバッファ
    connection_overhead_gb = workload_characteristics.max_connections * 0.01  # 接続あたり10MB

    total_memory_required = buffer_pool_gb + connection_overhead_gb

    # インスタンスクラスの選択
    instance_classes = {
        'db.t3.medium': {'memory_gb': 4, 'vcpu': 2, 'cost_per_hour': 0.068},
        'db.m6g.large': {'memory_gb': 8, 'vcpu': 2, 'cost_per_hour': 0.182},
        'db.m6g.xlarge': {'memory_gb': 16, 'vcpu': 4, 'cost_per_hour': 0.364},
        'db.m6g.2xlarge': {'memory_gb': 32, 'vcpu': 8, 'cost_per_hour': 0.728},
        'db.r6g.large': {'memory_gb': 16, 'vcpu': 2, 'cost_per_hour': 0.226},
        'db.r6g.xlarge': {'memory_gb': 32, 'vcpu': 4, 'cost_per_hour': 0.452},
        'db.r6g.2xlarge': {'memory_gb': 64, 'vcpu': 8, 'cost_per_hour': 0.904},
    }

    # メモリ要件を満たす最小インスタンス
    for instance_class, specs in instance_classes.items():
        if specs['memory_gb'] >= total_memory_required:
            # CPU要件も確認
            if workload_characteristics.cpu_intensive and specs['vcpu'] < 4:
                continue

            return {
                'instance_class': instance_class,
                'memory_gb': specs['memory_gb'],
                'vcpu': specs['vcpu'],
                'estimated_cost_per_month': specs['cost_per_hour'] * 730,
                'recommendation': f"メモリ要件{total_memory_required:.1f}GBを満たす最小インスタンス"
            }

    # 要件を満たすインスタンスがない場合
    return {
        'instance_class': 'db.r6g.8xlarge',
        'recommendation': 'より大きいインスタンスが必要、またはデータの最適化を検討'
    }

# 使用例
class WorkloadCharacteristics:
    active_dataset_gb = 50
    max_connections = 500
    cpu_intensive = True

workload = WorkloadCharacteristics()
instance_config = size_database_instance(workload)
print(f"推奨インスタンス: {instance_config}")
```

### フェーズ3: 高可用性戦略

```bash
# 高可用性構成の設計マトリクス

# Tier 1: ミッションクリティカル（金融、医療など）
# - Aurora Global Database
# - Multi-AZ: プライマリ + レプリカ2台（別AZ）
# - バックアップ保持期間: 30日
# - PITR有効

# Tier 2: ビジネスクリティカル（ECサイトなど）
# - Aurora Multi-AZ
# - プライマリ + レプリカ1台（別AZ）
# - バックアップ保持期間: 14日
# - PITR有効

# Tier 3: 一般的なワークロード
# - RDS Multi-AZ または Aurora Serverless v2
# - バックアップ保持期間: 7日
# - PITR有効

# Tier 4: 開発/テスト環境
# - RDS Single-AZ
# - バックアップ保持期間: 1日
```

### フェーズ4: パフォーマンス最適化

```sql
-- Performance Insightsで特定したスロークエリの最適化

-- 問題: インデックスなしのフルテーブルスキャン
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 12345;

-- 対策: インデックスの追加
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- 問題: 非効率なJOIN
EXPLAIN ANALYZE
SELECT o.*, c.name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending';

-- 対策: 複合インデックス
CREATE INDEX idx_orders_status_customer ON orders(status, customer_id);

-- 問題: N+1クエリ
-- アプリケーションレベルで修正（ORM設定、Eager Loading）

-- Auroraの並列クエリを活用
SET aurora_parallel_query = ON;
```

### フェーズ5: コスト最適化

```python
"""
RDS/Auroraのコスト最適化戦略
"""

def optimize_database_cost(current_config):
    """
    現在の構成からコスト最適化の提案を生成
    """
    recommendations = []

    # 1. Reserved Instancesの検討
    if current_config.uptime_percentage > 75:
        savings = current_config.monthly_cost * 0.4  # 40%削減
        recommendations.append({
            'action': 'Reserved Instances（1年契約）に変更',
            'savings_per_month': savings,
            'roi_months': 12 / 0.4  # 3ヶ月で回収
        })

    # 2. Aurora Serverless v2への移行
    if current_config.cpu_utilization_avg < 40:
        savings = current_config.monthly_cost * 0.3  # 30%削減
        recommendations.append({
            'action': 'Aurora Serverless v2に移行',
            'savings_per_month': savings,
            'reason': 'CPU使用率が低い'
        })

    # 3. リードレプリカのサイズ最適化
    if current_config.read_replica_count > 0:
        for replica in current_config.read_replicas:
            if replica.cpu_utilization < 30:
                recommendations.append({
                    'action': f'リードレプリカ{replica.id}を小さいインスタンスに変更',
                    'current': replica.instance_class,
                    'recommended': downgrade_instance_class(replica.instance_class),
                    'savings_per_month': calculate_savings(replica.instance_class)
                })

    # 4. ストレージの最適化
    if current_config.storage_type == 'io1' and current_config.iops_utilization < 50:
        recommendations.append({
            'action': 'ストレージタイプをio1からgp3に変更',
            'savings_per_month': calculate_storage_savings(current_config),
            'reason': 'IOPS利用率が低い'
        })

    return recommendations

def downgrade_instance_class(current_class):
    """インスタンスクラスを1段階ダウングレード"""
    downgrade_map = {
        'db.r6g.2xlarge': 'db.r6g.xlarge',
        'db.r6g.xlarge': 'db.r6g.large',
        'db.m6g.2xlarge': 'db.m6g.xlarge',
        'db.m6g.xlarge': 'db.m6g.large',
    }
    return downgrade_map.get(current_class, current_class)
```

## ベストプラクティス（2025年版）

### 1. Aurora Serverless v2をデフォルトに

**推奨**: 可変ワークロードではServerless v2を使用

```bash
# Serverless v2の利点
# 1. プロビジョニングと同じパフォーマンス
# 2. 自動スケーリング（0.5～128 ACU）
# 3. コスト最適化（使用した分だけ課金）
# 4. コールドスタートなし
```

### 2. Multi-AZ必須

```bash
# 本番環境ではMulti-AZ必須
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --multi-az \
    --apply-immediately false  # メンテナンスウィンドウで適用
```

### 3. 自動バックアップとPITR

```bash
# バックアップ保持期間の設定
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --backup-retention-period 30 \
    --apply-immediately

# PITRの実施
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mysql-prod \
    --target-db-instance-identifier mysql-prod-pitr-20250122 \
    --restore-time 2025-01-22T10:00:00Z
```

### 4. Performance Insights有効化

```bash
# すべてのRDS/Auroraインスタンスで有効化
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --apply-immediately
```

### 5. 暗号化必須

```bash
# 新規インスタンスは暗号化必須
aws rds create-db-instance \
    --db-instance-identifier mysql-prod \
    ... \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678

# 既存インスタンスの暗号化（スナップショット経由）
aws rds create-db-snapshot \
    --db-instance-identifier mysql-prod \
    --db-snapshot-identifier mysql-prod-pre-encryption

aws rds copy-db-snapshot \
    --source-db-snapshot-identifier mysql-prod-pre-encryption \
    --target-db-snapshot-identifier mysql-prod-encrypted \
    --kms-key-id arn:aws:kms:ap-northeast-1:123456789012:key/12345678

aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mysql-prod-encrypted \
    --db-snapshot-identifier mysql-prod-encrypted
```

### 6. RDS Proxyの活用

```bash
# Lambdaなど接続数が多い場合はRDS Proxy必須
# 接続プーリングでDB負荷を削減
```

## よくある落とし穴と対策

### 1. バーストバランス枯渇（T3インスタンス）

**症状**: パフォーマンスが突然低下

**原因**: T3インスタンスのCPUクレジットが枯渇

**対策**:

```bash
# M6g/R6gインスタンスに変更
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --db-instance-class db.m6g.large \
    --apply-immediately false
```

### 2. 接続数超過

**症状**: "Too many connections"エラー

**対策**:

```bash
# RDS Proxyを導入
# または max_connections パラメータを増やす

# パラメータグループの作成
aws rds create-db-parameter-group \
    --db-parameter-group-name mysql-high-connections \
    --db-parameter-group-family mysql8.0 \
    --description "Increased max_connections"

# max_connectionsの変更
aws rds modify-db-parameter-group \
    --db-parameter-group-name mysql-high-connections \
    --parameters "ParameterName=max_connections,ParameterValue=500,ApplyMethod=immediate"

# インスタンスに適用
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --db-parameter-group-name mysql-high-connections \
    --apply-immediately false
```

### 3. レプリケーションラグ

**症状**: リードレプリカのデータが古い

**対策**:

```bash
# レプリカのインスタンスクラスを上げる
# またはAuroraに移行（レプリケーションラグ<10ms）
```

### 4. ストレージ不足

**症状**: "out of storage"エラー

**対策**:

```bash
# ストレージの拡張
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --allocated-storage 1000 \
    --apply-immediately

# ストレージ自動スケーリングの有効化
aws rds modify-db-instance \
    --db-instance-identifier mysql-prod \
    --max-allocated-storage 2000 \
    --apply-immediately
```

## 判断ポイント

### RDS vs Aurora 選択マトリクス

| 要件 | RDS | Aurora |
|-----|-----|--------|
| 高可用性 | Multi-AZ（同期レプリケーション） | 6コピー（3 AZ） |
| 読み取りスケール | 最大5個のリードレプリカ | 最大15個のリードレプリカ |
| レプリケーションラグ | 秒単位 | <10ミリ秒 |
| フェイルオーバー時間 | 1-2分 | <30秒 |
| ストレージスケーリング | 手動 | 自動（最大128 TB） |
| パフォーマンス | 標準 | MySQL5倍、PostgreSQL3倍 |
| コスト | 小規模で有利 | 中大規模で有利 |
| グローバル展開 | Read Replica（手動） | Global Database（自動） |

## 検証ポイント

### 1. バックアップリストアテスト

```bash
# 定期的にリストアテストを実施（月1回推奨）
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mysql-restore-test \
    --db-snapshot-identifier mysql-prod-backup-$(date +%Y%m%d)

# データ整合性確認
mysql -h mysql-restore-test.xxx.rds.amazonaws.com -u admin -p << 'EOF'
SELECT COUNT(*) FROM orders;
SELECT MAX(created_at) FROM orders;
EOF

# 不要なテストインスタンスを削除
aws rds delete-db-instance \
    --db-instance-identifier mysql-restore-test \
    --skip-final-snapshot
```

### 2. フェイルオーバーテスト

```bash
# Aurora/RDS Multi-AZのフェイルオーバーテスト
aws rds reboot-db-instance \
    --db-instance-identifier mysql-prod \
    --force-failover

# フェイルオーバー時間を計測
# 期待値: Aurora<30秒、RDS<2分
```

### 3. パフォーマンステスト

```bash
# sysbenchでベンチマーク
sysbench oltp_read_write \
    --mysql-host=mysql-prod.xxx.rds.amazonaws.com \
    --mysql-user=admin \
    --mysql-password=SecurePassword123! \
    --mysql-db=testdb \
    --tables=10 \
    --table-size=100000 \
    prepare

sysbench oltp_read_write \
    --mysql-host=mysql-prod.xxx.rds.amazonaws.com \
    --mysql-user=admin \
    --mysql-password=SecurePassword123! \
    --mysql-db=testdb \
    --tables=10 \
    --table-size=100000 \
    --threads=16 \
    --time=300 \
    run
```

## 他のスキルとの統合

### Lambdaスキルとの統合

```python
"""
Lambda + RDS Proxy
"""
import pymysql
import os

def lambda_handler(event, context):
    """
    RDS Proxy経由でデータベースに接続
    """
    connection = pymysql.connect(
        host=os.environ['DB_PROXY_ENDPOINT'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        connect_timeout=5
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (event['user_id'],))
            result = cursor.fetchone()
            return {'statusCode': 200, 'body': result}
    finally:
        connection.close()
```

### VPCスキルとの統合

```bash
# VPC内にRDS配置
# プライベートサブネット推奨
# セキュリティグループで3306/5432ポートを制限
```

## リソース

### 公式ドキュメント

- [Amazon RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Amazon Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Aurora Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.BestPractices.html)

### ツールとライブラリ

- [AWS CLI RDS Commands](https://docs.aws.amazon.com/cli/latest/reference/rds/)
- [Boto3 RDS Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html)
