---
name: aws-direct-connect-vpn
description: AWS Direct ConnectとVPNを使用してオンプレミスとAWSを接続し、Site-to-Site VPN、Client VPN、ハイブリッド接続を実装する方法
---

# AWS Direct Connect / VPN スキル

## 概要

AWS Direct ConnectとVPNは、オンプレミス環境とAWSクラウドを接続するハイブリッドネットワークソリューションです。このスキルでは、Direct Connect、Site-to-Site VPN、Client VPNを活用して、セキュアで高性能なハイブリッド接続を構築します。

### 2025年の重要なアップデート

- **Direct Connect + VPN**: IPsec暗号化とDirect Connectの組み合わせ
- **Transit Gateway**: 複数VPCとオンプレミスの統合接続
- **Client VPN**: リモートワーカー向けマネージドVPN
- **料金**: Direct Connect（ポート料金 + データ転送）、Site-to-Site VPN（$0.05/時 + データ転送）

## 主な使用ケース

### 1. Site-to-Site VPN（基本）

オンプレミスとVPCをVPNで接続します。

```bash
# Customer Gatewayの作成（オンプレミス側）
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.1 \
    --bgp-asn 65000 \
    --tag-specifications 'ResourceType=customer-gateway,Tags=[{Key=Name,Value=on-premises-cgw}]'

CGW_ID=$(aws ec2 describe-customer-gateways --filters "Name=tag:Name,Values=on-premises-cgw" --query 'CustomerGateways[0].CustomerGatewayId' --output text)

# Virtual Private Gatewayの作成（AWS側）
aws ec2 create-vpn-gateway \
    --type ipsec.1 \
    --amazon-side-asn 64512 \
    --tag-specifications 'ResourceType=vpn-gateway,Tags=[{Key=Name,Value=production-vgw}]'

VGW_ID=$(aws ec2 describe-vpn-gateways --filters "Name=tag:Name,Values=production-vgw" --query 'VpnGateways[0].VpnGatewayId' --output text)

# VPCにアタッチ
aws ec2 attach-vpn-gateway \
    --vpn-gateway-id $VGW_ID \
    --vpc-id $VPC_ID

# VPN接続の作成
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id $CGW_ID \
    --vpn-gateway-id $VGW_ID \
    --options TunnelOptions='[{TunnelInsideCidr=169.254.10.0/30,PreSharedKey=SecurePreSharedKey123!},{TunnelInsideCidr=169.254.11.0/30,PreSharedKey=SecurePreSharedKey456!}]' \
    --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=production-vpn}]'

# ルートプロパゲーションの有効化
ROUTE_TABLE_ID=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --query 'RouteTables[0].RouteTableId' --output text)

aws ec2 enable-vgw-route-propagation \
    --route-table-id $ROUTE_TABLE_ID \
    --gateway-id $VGW_ID
```

### 2. Transit Gateway + VPN（推奨）

複数VPCとオンプレミスを統合接続します。

```bash
# Transit Gatewayの作成
aws ec2 create-transit-gateway \
    --description "Central hub for hybrid connectivity" \
    --options \
        AmazonSideAsn=64512,\
        VpnEcmpSupport=enable,\
        DefaultRouteTableAssociation=enable \
    --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=central-tgw}]'

TGW_ID=$(aws ec2 describe-transit-gateways --filters "Name=tag:Name,Values=central-tgw" --query 'TransitGateways[0].TransitGatewayId' --output text)

# VPCをアタッチ
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id $TGW_ID \
    --vpc-id $VPC_ID \
    --subnet-ids $PRIVATE_SUBNET_1A $PRIVATE_SUBNET_1C

# Customer Gatewayの作成
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.1 \
    --bgp-asn 65000

CGW_ID=$(aws ec2 describe-customer-gateways --query 'CustomerGateways[0].CustomerGatewayId' --output text)

# Transit GatewayにVPN接続
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id $CGW_ID \
    --transit-gateway-id $TGW_ID \
    --options StaticRoutesOnly=false,TunnelOptions='[{TunnelInsideCidr=169.254.10.0/30},{TunnelInsideCidr=169.254.11.0/30}]'
```

**Transit Gateway + VPNのメリット**:
- 複数VPCを一元管理
- ECMP（Equal-Cost Multi-Path）で最大50 Gbpsスループット
- ルーティング管理の簡素化

### 3. Direct Connect（専用線接続）

高帯域幅、低レイテンシの専用接続を確立します。

```bash
# Direct Connect接続の作成（AWSコンソールまたはパートナー経由）
# ポートスピード: 1 Gbps, 10 Gbps, 100 Gbps

# Virtual Interfaceの作成（プライベートVIF）
aws directconnect create-private-virtual-interface \
    --connection-id dxcon-abc12345 \
    --new-private-virtual-interface file://private-vif.json

# private-vif.json
cat > private-vif.json << 'EOF'
{
  "virtualInterfaceName": "production-vif",
  "vlan": 100,
  "asn": 65000,
  "amazonAddress": "169.254.10.1/30",
  "customerAddress": "169.254.10.2/30",
  "virtualGatewayId": "vgw-12345678"
}
EOF

# Direct Connect Gateway（複数リージョン接続）
aws directconnect create-direct-connect-gateway \
    --direct-connect-gateway-name global-dxgw \
    --amazon-side-asn 64512

DXGW_ID=$(aws directconnect describe-direct-connect-gateways --query 'directConnectGateways[0].directConnectGatewayId' --output text)

# Virtual Private Gatewayと関連付け
aws directconnect create-direct-connect-gateway-association \
    --direct-connect-gateway-id $DXGW_ID \
    --virtual-gateway-id $VGW_ID
```

### 4. Direct Connect + VPN（暗号化）

Direct Connect経由でIPsec VPNを確立します。

```bash
# Transit Gateway経由でDirect Connect + VPNを組み合わせ
# 1. Direct Connect GatewayをTransit Gatewayに接続
aws directconnect create-direct-connect-gateway-association \
    --direct-connect-gateway-id $DXGW_ID \
    --gateway-id $TGW_ID \
    --add-allowed-prefixes-to-direct-connect-gateway Cidr=10.0.0.0/16

# 2. Transit Gateway経由でVPN接続を追加（暗号化用）
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id $CGW_ID \
    --transit-gateway-id $TGW_ID \
    --options StaticRoutesOnly=false
```

**Direct Connect + VPNのメリット**:
- Direct Connectの高帯域幅 + VPNの暗号化
- 金融・医療など規制業界のコンプライアンス要件に対応

### 5. Client VPN（リモートアクセス）

リモートワーカーがVPCにアクセスします。

```bash
# サーバー証明書の作成（ACM）
aws acm import-certificate \
    --certificate fileb://server-cert.pem \
    --private-key fileb://server-key.pem \
    --certificate-chain fileb://ca-cert.pem

SERVER_CERT_ARN=$(aws acm list-certificates --query 'CertificateSummaryList[0].CertificateArn' --output text)

# Client VPN Endpointの作成
aws ec2 create-client-vpn-endpoint \
    --client-cidr-block 10.100.0.0/16 \
    --server-certificate-arn $SERVER_CERT_ARN \
    --authentication-options Type=certificate-authentication,MutualAuthentication={ClientRootCertificateChainArn=$CLIENT_CERT_ARN} \
    --connection-log-options Enabled=true,CloudwatchLogGroup=/aws/clientvpn,CloudwatchLogStream=connections \
    --vpc-id $VPC_ID \
    --security-group-ids $CLIENT_VPN_SG \
    --tag-specifications 'ResourceType=client-vpn-endpoint,Tags=[{Key=Name,Value=remote-access-vpn}]'

CLIENT_VPN_ID=$(aws ec2 describe-client-vpn-endpoints --filters "Name=tag:Name,Values=remote-access-vpn" --query 'ClientVpnEndpoints[0].ClientVpnEndpointId' --output text)

# サブネットに関連付け
aws ec2 associate-client-vpn-target-network \
    --client-vpn-endpoint-id $CLIENT_VPN_ID \
    --subnet-id $PRIVATE_SUBNET_1A

# 認可ルールの追加
aws ec2 authorize-client-vpn-ingress \
    --client-vpn-endpoint-id $CLIENT_VPN_ID \
    --target-network-cidr 10.0.0.0/16 \
    --authorize-all-groups
```

### 6. 高可用性構成（Direct Connect）

冗長構成でSLAを保証します。

```bash
# 2つのDirect Connect接続（異なるロケーション）
# - Primary: 東京
# - Secondary: 大阪

# BGPで自動フェイルオーバー
# AS_PATHプリペンドでプライマリを優先

# VPN（バックアップ）
# Direct Connect障害時のフェイルオーバー用
```

**高可用性のベストプラクティス**:
- 2つのDirect Connect接続（異なるロケーション）
- Site-to-Site VPNをバックアップとして
- BGPによる自動フェイルオーバー

## ベストプラクティス（2025年版）

### 1. Transit Gatewayを中央ハブに

```bash
# 複数VPC + オンプレミスの統合管理
# VPN ECMPで50 Gbpsスループット
```

### 2. Direct Connect + VPNで暗号化

```bash
# コンプライアンス要件対応
# IPsec暗号化 + 専用線の低レイテンシ
```

### 3. 冗長構成必須

```bash
# プライマリ + セカンダリDirect Connect
# VPNをバックアップとして
```

### 4. Client VPNで証明書認証

```bash
# ユーザー名/パスワードより安全
# 多要素認証（MFA）と組み合わせ
```

## よくある落とし穴と対策

### 1. Direct Connectの単一障害点

**症状**: Direct Connect障害時に接続不可

**対策**: 冗長構成 + VPNバックアップ

### 2. MTUサイズの不一致

**症状**: 大きいパケットが転送されない

**対策**: MTU 1500バイト以下に設定

### 3. BGP設定ミス

**症状**: ルーティングが正しく動作しない

**対策**: AS_PATH、Local Preferenceを適切に設定

## 判断ポイント

### Site-to-Site VPN vs Direct Connect

| 要件 | Site-to-Site VPN | Direct Connect |
|-----|-----------------|----------------|
| 帯域幅 | 最大1.25 Gbps | 1/10/100 Gbps |
| レイテンシ | インターネット経由 | 専用線（低レイテンシ） |
| セットアップ | 数分 | 数週間～数ヶ月 |
| コスト | 低（$0.05/時） | 高（ポート料金） |
| 用途 | 開発/テスト、バックアップ | 本番、大容量転送 |

### Client VPN vs Site-to-Site VPN

| 用途 | Client VPN | Site-to-Site VPN |
|-----|-----------|-----------------|
| 接続元 | 個人PC/ノートPC | オンプレミス拠点 |
| ユーザー数 | 多数（スケーラブル） | 固定 |
| 認証 | 証明書、AD | IPsec Pre-Shared Key |
| 用途 | リモートワーク | データセンター接続 |

## リソース

### 公式ドキュメント

- [Direct Connect Documentation](https://docs.aws.amazon.com/directconnect/)
- [Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/)
- [Client VPN](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/)
- [Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/)
