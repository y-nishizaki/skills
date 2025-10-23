---
name: aws-vpc
description: AWS VPC（Virtual Private Cloud）を使用してプライベートネットワークを構築し、サブネット、ルートテーブル、NAT Gateway、Transit Gatewayを活用してセキュアでスケーラブルなネットワークを設計する方法
---

# AWS VPC スキル

## 概要

Amazon VPC（Virtual Private Cloud）は、AWS クラウド内に論理的に分離されたプライベートネットワーク空間を提供します。このスキルでは、サブネット設計、NAT Gateway、Transit Gateway、PrivateLinkを活用して、セキュアでスケーラブルなネットワークアーキテクチャを構築する方法を学びます。

### 2025年の重要なアップデート

- **NAT Gateway**: AZごとに1つ配置（高可用性）
- **Transit Gateway**: マルチVPC接続の標準
- **PrivateLink**: サービス間通信のセキュアな接続
- **IPv6サポート**: デュアルスタック推奨

## 主な使用ケース

### 1. 基本的なVPC構成（パブリック + プライベートサブネット）

高可用性を考慮した2-AZ構成です。

```bash
# VPCの作成（CIDR: 10.0.0.0/16）
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=production-vpc}]'

VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=production-vpc" --query 'Vpcs[0].VpcId' --output text)

# DNS解決の有効化
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

# パブリックサブネット（AZ-1a）
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ap-northeast-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1a}]'

# パブリックサブネット（AZ-1c）
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ap-northeast-1c \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1c}]'

# プライベートサブネット（AZ-1a、/21で大きめ）
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.8.0/21 \
    --availability-zone ap-northeast-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1a}]'

# プライベートサブネット（AZ-1c）
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.16.0/21 \
    --availability-zone ap-northeast-1c \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1c}]'

# インターネットゲートウェイの作成とアタッチ
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=production-igw}]'

IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=tag:Name,Values=production-igw" --query 'InternetGateways[0].InternetGatewayId' --output text)

aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
```

**サブネッティングの推奨**:
- パブリック: /24 （256アドレス）
- プライベート: /21 （2048アドレス）- EC2、ECS、Lambda、RDS用

### 2. NAT Gateway（高可用性構成）

各AZにNAT Gatewayを配置します。

```bash
# Elastic IPの割り当て（NAT Gateway用、AZ-1a）
aws ec2 allocate-address --domain vpc \
    --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=nat-eip-1a}]'

EIP_1A=$(aws ec2 describe-addresses --filters "Name=tag:Name,Values=nat-eip-1a" --query 'Addresses[0].AllocationId' --output text)

# NAT Gatewayの作成（AZ-1a）
PUBLIC_SUBNET_1A=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=public-subnet-1a" --query 'Subnets[0].SubnetId' --output text)

aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1A \
    --allocation-id $EIP_1A \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=nat-gw-1a}]'

# 同様にAZ-1c用も作成
aws ec2 allocate-address --domain vpc \
    --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=nat-eip-1c}]'

EIP_1C=$(aws ec2 describe-addresses --filters "Name=tag:Name,Values=nat-eip-1c" --query 'Addresses[0].AllocationId' --output text)

PUBLIC_SUBNET_1C=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=public-subnet-1c" --query 'Subnets[0].SubnetId' --output text)

aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1C \
    --allocation-id $EIP_1C \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=nat-gw-1c}]'
```

**NAT Gateway配置の理由**:
- AZごとに1つ → 障害時の影響範囲を限定
- クロスAZデータ転送料金の削減
- 帯域幅の向上（NAT Gatewayは最大45 Gbps）

### 3. ルートテーブルの設定

パブリックとプライベートで別々のルートテーブルを作成します。

```bash
# パブリックサブネット用ルートテーブル
aws ec2 create-route-table --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]'

PUBLIC_RT=$(aws ec2 describe-route-tables --filters "Name=tag:Name,Values=public-rt" --query 'RouteTables[0].RouteTableId' --output text)

# インターネットゲートウェイへのルート追加
aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# パブリックサブネットに関連付け
PUBLIC_SUBNET_1A=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=public-subnet-1a" --query 'Subnets[0].SubnetId' --output text)
PUBLIC_SUBNET_1C=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=public-subnet-1c" --query 'Subnets[0].SubnetId' --output text)

aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1A
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1C

# プライベートサブネット用ルートテーブル（AZ-1a）
aws ec2 create-route-table --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt-1a}]'

PRIVATE_RT_1A=$(aws ec2 describe-route-tables --filters "Name=tag:Name,Values=private-rt-1a" --query 'RouteTables[0].RouteTableId' --output text)

# NAT Gatewayへのルート追加
NAT_GW_1A=$(aws ec2 describe-nat-gateways --filter "Name=tag:Name,Values=nat-gw-1a" --query 'NatGateways[0].NatGatewayId' --output text)

aws ec2 create-route \
    --route-table-id $PRIVATE_RT_1A \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW_1A

# プライベートサブネット（AZ-1a）に関連付け
PRIVATE_SUBNET_1A=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=private-subnet-1a" --query 'Subnets[0].SubnetId' --output text)

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1A --subnet-id $PRIVATE_SUBNET_1A

# 同様にAZ-1c用も作成...
```

### 4. VPCエンドポイント（PrivateLink）

S3やDynamoDBへのアクセスをインターネット経由せずに行います。

```bash
# S3用ゲートウェイエンドポイント（無料）
aws ec2 create-vpc-endpoint \
    --vpc-id $VPC_ID \
    --service-name com.amazonaws.ap-northeast-1.s3 \
    --route-table-ids $PRIVATE_RT_1A $PRIVATE_RT_1C \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=s3-endpoint}]'

# DynamoDB用ゲートウェイエンドポイント（無料）
aws ec2 create-vpc-endpoint \
    --vpc-id $VPC_ID \
    --service-name com.amazonaws.ap-northeast-1.dynamodb \
    --route-table-ids $PRIVATE_RT_1A $PRIVATE_RT_1C \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=dynamodb-endpoint}]'

# ECR用インターフェースエンドポイント（有料）
aws ec2 create-vpc-endpoint \
    --vpc-id $VPC_ID \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.ap-northeast-1.ecr.api \
    --subnet-ids $PRIVATE_SUBNET_1A $PRIVATE_SUBNET_1C \
    --security-group-ids $VPC_ENDPOINT_SG \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=ecr-api-endpoint}]'
```

**VPCエンドポイントのメリット**:
- データ転送料金の削減（インターネット経由不要）
- セキュリティ向上（トラフィックがAWSネットワーク内に留まる）
- パフォーマンス向上（レイテンシ削減）

### 5. Transit Gateway（マルチVPC接続）

複数のVPCとオンプレミスを接続します。

```bash
# Transit Gatewayの作成
aws ec2 create-transit-gateway \
    --description "Central hub for multi-VPC connectivity" \
    --options \
        AmazonSideAsn=64512,\
        DefaultRouteTableAssociation=enable,\
        DefaultRouteTablePropagation=enable,\
        VpnEcmpSupport=enable,\
        DnsSupport=enable \
    --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=central-tgw}]'

TGW_ID=$(aws ec2 describe-transit-gateways --filters "Name=tag:Name,Values=central-tgw" --query 'TransitGateways[0].TransitGatewayId' --output text)

# VPCをTransit Gatewayにアタッチ
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id $TGW_ID \
    --vpc-id $VPC_ID \
    --subnet-ids $PRIVATE_SUBNET_1A $PRIVATE_SUBNET_1C \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=production-vpc-attachment}]'

# プライベートサブネットのルートテーブルにTransit Gatewayへのルートを追加
# 例: 他のVPC（10.1.0.0/16）へのルート
aws ec2 create-route \
    --route-table-id $PRIVATE_RT_1A \
    --destination-cidr-block 10.1.0.0/16 \
    --transit-gateway-id $TGW_ID
```

### 6. VPCピアリング（シンプルなVPC間接続）

2つのVPC間で直接接続します。

```bash
# VPCピアリング接続の作成
aws ec2 create-vpc-peering-connection \
    --vpc-id $VPC_ID \
    --peer-vpc-id vpc-0987654321 \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=prod-to-dev-peering}]'

PEERING_ID=$(aws ec2 describe-vpc-peering-connections --filters "Name=tag:Name,Values=prod-to-dev-peering" --query 'VpcPeeringConnections[0].VpcPeeringConnectionId' --output text)

# ピアリング接続を承認
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PEERING_ID

# ルートテーブルに追加
aws ec2 create-route \
    --route-table-id $PRIVATE_RT_1A \
    --destination-cidr-block 10.1.0.0/16 \
    --vpc-peering-connection-id $PEERING_ID
```

**VPCピアリング vs Transit Gateway**:
- ピアリング: 1対1接続、シンプル、低コスト
- Transit Gateway: ハブ&スポーク、多対多接続、管理容易

### 7. VPC Flow Logs

ネットワークトラフィックを監視します。

```bash
# CloudWatch Logsにフローログを送信
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids $VPC_ID \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs \
    --deliver-logs-permission-arn arn:aws:iam::123456789012:role/VPCFlowLogsRole \
    --tag-specifications 'ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=production-vpc-flowlogs}]'

# S3にフローログを送信（コスト効率が良い）
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids $VPC_ID \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination arn:aws:s3:::vpc-flow-logs-bucket \
    --tag-specifications 'ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=production-vpc-flowlogs-s3}]'
```

### 8. IPv6サポート

デュアルスタック構成を実装します。

```bash
# VPCにIPv6 CIDRブロックを関連付け
aws ec2 associate-vpc-cidr-block \
    --vpc-id $VPC_ID \
    --amazon-provided-ipv6-cidr-block

# サブネットにIPv6 CIDRを割り当て
aws ec2 associate-subnet-cidr-block \
    --subnet-id $PUBLIC_SUBNET_1A \
    --ipv6-cidr-block 2600:1f14:1234:5600::/64

# ルートテーブルにIPv6ルートを追加
aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-ipv6-cidr-block ::/0 \
    --gateway-id $IGW_ID
```

## 思考プロセス

VPCネットワークを設計する際の段階的な思考プロセスです。

### フェーズ1: CIDR設計

```python
"""
VPC CIDR設計ツール
"""

def design_vpc_cidr(requirements):
    """
    要件に基づいてVPC CIDRを設計
    """
    # 推奨CIDR範囲
    # - 小規模: /24 (256アドレス)
    # - 中規模: /20 (4096アドレス)
    # - 大規模: /16 (65536アドレス)

    if requirements.expected_instances < 100:
        return {
            'vpc_cidr': '10.0.0.0/24',
            'public_subnets': ['10.0.0.0/26', '10.0.0.64/26'],
            'private_subnets': ['10.0.0.128/26', '10.0.0.192/26']
        }
    elif requirements.expected_instances < 1000:
        return {
            'vpc_cidr': '10.0.0.0/20',
            'public_subnets': ['10.0.0.0/24', '10.0.1.0/24'],
            'private_subnets': ['10.0.8.0/21', '10.0.16.0/21']  # 大きめ
        }
    else:
        return {
            'vpc_cidr': '10.0.0.0/16',
            'public_subnets': ['10.0.1.0/24', '10.0.2.0/24'],
            'private_subnets': ['10.0.8.0/21', '10.0.16.0/21', '10.0.24.0/21', '10.0.32.0/21']
        }

# 使用例
class Requirements:
    expected_instances = 500

requirements = Requirements()
cidr_design = design_vpc_cidr(requirements)
print(f"推奨CIDR設計: {cidr_design}")
```

### フェーズ2: 高可用性設計

```bash
# 高可用性の原則
# 1. 最低2つのAZ
# 2. 各AZにパブリック+プライベートサブネット
# 3. 各AZにNAT Gateway
# 4. マルチAZのロードバランサー
# 5. マルチAZのRDS/Aurora
```

### フェーズ3: コスト最適化

```python
"""
VPCコスト最適化チェックリスト
"""

def optimize_vpc_costs(current_config):
    """
    現在の構成からコスト最適化の提案を生成
    """
    recommendations = []

    # 1. NAT Gatewayの最適化
    if current_config.nat_gateway_count > current_config.az_count:
        recommendations.append({
            'action': 'NAT Gatewayを各AZに1つに削減',
            'savings': f'${(current_config.nat_gateway_count - current_config.az_count) * 32} /月'
        })

    # 2. VPCエンドポイントの活用
    if current_config.s3_data_transfer_gb > 100:
        recommendations.append({
            'action': 'S3ゲートウェイエンドポイントを作成',
            'savings': f'${current_config.s3_data_transfer_gb * 0.09} /月',
            'reason': 'インターネット経由のデータ転送料金を削減'
        })

    # 3. 不要なElastic IPの削除
    if current_config.unused_eip_count > 0:
        recommendations.append({
            'action': '未使用のElastic IPを削除',
            'savings': f'${current_config.unused_eip_count * 3.6} /月'
        })

    return recommendations

# 使用例
class CurrentConfig:
    nat_gateway_count = 4
    az_count = 2
    s3_data_transfer_gb = 500
    unused_eip_count = 3

config = CurrentConfig()
optimizations = optimize_vpc_costs(config)
for opt in optimizations:
    print(f"最適化提案: {opt}")
```

## ベストプラクティス（2025年版）

### 1. 各AZにNAT Gateway配置

```bash
# 理由:
# - AZ障害時の影響範囲を限定
# - クロスAZデータ転送料金の削減（$0.01/GB）
# - トラフィックを同一AZ内に保持
```

### 2. プライベートサブネットは/21

```bash
# EC2、ECS、Lambda、RDSなど多くのリソースを配置
# 2048アドレス確保で将来の拡張に対応
```

### 3. Transit Gatewayでハブ&スポーク

```bash
# 3つ以上のVPC接続ならTransit Gateway推奨
# ピアリングは管理が複雑化（フルメッシュ）
```

### 4. VPC Flow Logsは S3に

```bash
# CloudWatch Logsより90%安い
# Athenaで分析可能
```

### 5. VPCエンドポイント活用

```bash
# S3、DynamoDBはゲートウェイエンドポイント（無料）
# ECR、SecretsManagerはインターフェースエンドポイント（有料だが必要）
```

## よくある落とし穴と対策

### 1. 単一NAT Gatewayによる単一障害点

**症状**: NAT Gateway障害時、全プライベートサブネットがインターネットアクセス不可

**対策**: 各AZにNAT Gateway配置（既出）

### 2. CIDRブロックの枯渇

**症状**: サブネットのIPアドレスが不足

**対策**:

```bash
# セカンダリCIDRブロックの追加
aws ec2 associate-vpc-cidr-block \
    --vpc-id $VPC_ID \
    --cidr-block 10.1.0.0/16
```

### 3. VPCエンドポイントの未使用

**症状**: S3への大量データ転送で高額請求

**対策**: ゲートウェイエンドポイント作成（無料）

### 4. VPC Flow Logsのコスト

**症状**: CloudWatch Logsで高額請求

**対策**: S3に保存してコスト削減

## 判断ポイント

### VPCピアリング vs Transit Gateway

| 要件 | VPCピアリング | Transit Gateway |
|-----|-------------|----------------|
| VPC接続数 | 2-3個 | 4個以上 |
| トランジットルーティング | 不可 | 可能 |
| オンプレミス接続 | 不可 | 可能（VPN/Direct Connect） |
| コスト | 低（データ転送のみ） | 高（アタッチメント料金） |
| 管理 | 複雑（フルメッシュ） | シンプル（ハブ&スポーク） |

### NAT Gateway vs NAT Instance

| 要件 | NAT Gateway | NAT Instance |
|-----|------------|-------------|
| 管理 | マネージド | 自己管理 |
| 可用性 | AZ冗長 | 手動構成必要 |
| 帯域幅 | 最大45 Gbps | インスタンス依存 |
| コスト | $32/月 + データ転送 | インスタンス料金 + データ転送 |
| 推奨 | **2025年推奨** | 非推奨 |

## 検証ポイント

### 1. 接続性テスト

```bash
# パブリックサブネットからインターネット接続確認
# EC2インスタンスで
curl -I https://www.google.com

# プライベートサブネットからNAT Gateway経由の接続確認
curl -I https://www.google.com

# VPCエンドポイント経由のS3アクセス確認
aws s3 ls s3://my-bucket/
```

### 2. ルーティング検証

```bash
# ルートテーブルの確認
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID"

# 有効なルートの確認
aws ec2 describe-route-tables \
    --route-table-ids $PRIVATE_RT_1A \
    --query 'RouteTables[0].Routes'
```

### 3. コスト分析

```bash
# Cost Explorerで以下を確認
# - NAT Gatewayデータ処理料金
# - データ転送料金（クロスAZ、インターネット）
# - VPCエンドポイント料金
```

## 他のスキルとの統合

### EC2スキルとの統合

```bash
# VPC内にEC2インスタンス起動
# パブリックサブネット: パブリックIP自動割り当て
# プライベートサブネット: NAT Gateway経由でインターネットアクセス
```

### RDSスキルとの統合

```bash
# プライベートサブネットにRDS配置
# DBサブネットグループ作成（マルチAZ）
```

### Lambdaスキルとの統合

```bash
# LambdaをVPC内に配置
# VPCエンドポイント経由でS3/DynamoDBアクセス
```

## リソース

### 公式ドキュメント

- [Amazon VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/)
- [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/)

### ツールとライブラリ

- [AWS CLI VPC Commands](https://docs.aws.amazon.com/cli/latest/reference/ec2/)
- [Boto3 VPC Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
