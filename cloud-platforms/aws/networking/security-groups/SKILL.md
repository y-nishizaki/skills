---
name: aws-security-groups
description: AWS Security GroupsとNetwork ACLsを使用してステートフル/ステートレスなファイアウォールルールを設定し、VPCリソースへのトラフィックを制御する方法
---

# AWS Security Groups スキル

## 概要

Security GroupsとNetwork ACLs（NACLs）は、VPC内のリソースへのトラフィックを制御するファイアウォール機能です。Security Groupsはステートフル、NACLsはステートレスという重要な違いがあり、適切に組み合わせることで多層防御を実現します。

### 2025年の重要なポイント

- **Security Groups**: ステートフル（リターントラフィック自動許可）
- **NACLs**: ステートレス（明示的に許可が必要）
- **最小権限の原則**: 必要最小限のルールのみ
- **参照による接続**: Security Group IDで相互参照

## 主な使用ケース

### 1. 基本的なSecurity Group設定

Webサーバー用のSecurity Groupを作成します。

```bash
# Security Groupの作成
aws ec2 create-security-group \
    --group-name web-server-sg \
    --description "Security group for web servers" \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=web-server-sg}]'

WEB_SG=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=web-server-sg" --query 'SecurityGroups[0].GroupId' --output text)

# HTTPSインバウンドルール（0.0.0.0/0から）
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# HTTPインバウンドルール
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# SSHアクセス（特定IPのみ）
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --protocol tcp \
    --port 22 \
    --cidr 203.0.113.0/24
```

### 2. Security Group参照（推奨パターン）

他のSecurity Groupを参照して接続を許可します。

```bash
# アプリケーションサーバーSG
aws ec2 create-security-group \
    --group-name app-server-sg \
    --description "Security group for application servers" \
    --vpc-id $VPC_ID

APP_SG=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=app-server-sg" --query 'SecurityGroups[0].GroupId' --output text)

# WebサーバーSGからのトラフィックのみ許可
aws ec2 authorize-security-group-ingress \
    --group-id $APP_SG \
    --protocol tcp \
    --port 8080 \
    --source-group $WEB_SG

# データベースSG
aws ec2 create-security-group \
    --group-name database-sg \
    --description "Security group for databases" \
    --vpc-id $VPC_ID

DB_SG=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=database-sg" --query 'SecurityGroups[0].GroupId' --output text)

# アプリケーションサーバーSGからのみMySQL接続許可
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG \
    --protocol tcp \
    --port 3306 \
    --source-group $APP_SG
```

**Security Group参照のメリット**:
- IPアドレス管理不要
- スケールアウト時も自動対応
- セキュリティ向上

### 3. Network ACLs（サブネットレベル）

ステートレスなファイアウォールでサブネットを保護します。

```bash
# Network ACLの作成
aws ec2 create-network-acl \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=public-nacl}]'

NACL_ID=$(aws ec2 describe-network-acls --filters "Name=tag:Name,Values=public-nacl" --query 'NetworkAcls[0].NetworkAclId' --output text)

# インバウンドルール: HTTPS許可
aws ec2 create-network-acl-entry \
    --network-acl-id $NACL_ID \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=443,To=443 \
    --cidr-block 0.0.0.0/0 \
    --egress false \
    --rule-action allow

# インバウンドルール: HTTP許可
aws ec2 create-network-acl-entry \
    --network-acl-id $NACL_ID \
    --rule-number 110 \
    --protocol tcp \
    --port-range From=80,To=80 \
    --cidr-block 0.0.0.0/0 \
    --egress false \
    --rule-action allow

# インバウンドルール: エフェメラルポート許可（リターントラフィック用）
aws ec2 create-network-acl-entry \
    --network-acl-id $NACL_ID \
    --rule-number 120 \
    --protocol tcp \
    --port-range From=1024,To=65535 \
    --cidr-block 0.0.0.0/0 \
    --egress false \
    --rule-action allow

# アウトバウンドルール: すべて許可
aws ec2 create-network-acl-entry \
    --network-acl-id $NACL_ID \
    --rule-number 100 \
    --protocol -1 \
    --cidr-block 0.0.0.0/0 \
    --egress true \
    --rule-action allow

# サブネットに関連付け
aws ec2 replace-network-acl-association \
    --association-id $EXISTING_ASSOC_ID \
    --network-acl-id $NACL_ID
```

**重要**: NACLsはステートレスなので、リターントラフィック用にエフェメラルポート（1024-65535）を許可する必要があります。

### 4. 拒否ルール（NACLsのみ）

特定のIPをブロックします。

```bash
# 悪意のあるIPをブロック（Security Groupsでは不可能）
aws ec2 create-network-acl-entry \
    --network-acl-id $NACL_ID \
    --rule-number 50 \
    --protocol -1 \
    --cidr-block 198.51.100.0/24 \
    --egress false \
    --rule-action deny

# ルール番号が小さいほど優先度が高い
# ルール50（deny）→ ルール100（allow）の順で評価
```

### 5. セキュリティグループのチェーニング

3層アーキテクチャでの使用例です。

```python
"""
3層アーキテクチャのSecurity Groups
"""
import boto3

ec2 = boto3.client('ec2')
vpc_id = 'vpc-12345678'

# 1. ALB Security Group
alb_sg = ec2.create_security_group(
    GroupName='alb-sg',
    Description='Security group for ALB',
    VpcId=vpc_id
)
alb_sg_id = alb_sg['GroupId']

# インターネットからHTTPS
ec2.authorize_security_group_ingress(
    GroupId=alb_sg_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 443,
        'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]
)

# 2. Web Server Security Group
web_sg = ec2.create_security_group(
    GroupName='web-server-sg',
    Description='Security group for web servers',
    VpcId=vpc_id
)
web_sg_id = web_sg['GroupId']

# ALBからのみアクセス許可
ec2.authorize_security_group_ingress(
    GroupId=web_sg_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 80,
        'ToPort': 80,
        'UserIdGroupPairs': [{'GroupId': alb_sg_id}]
    }]
)

# 3. Application Server Security Group
app_sg = ec2.create_security_group(
    GroupName='app-server-sg',
    Description='Security group for app servers',
    VpcId=vpc_id
)
app_sg_id = app_sg['GroupId']

# WebサーバーからのみAPI呼び出し許可
ec2.authorize_security_group_ingress(
    GroupId=app_sg_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 8080,
        'ToPort': 8080,
        'UserIdGroupPairs': [{'GroupId': web_sg_id}]
    }]
)

# 4. Database Security Group
db_sg = ec2.create_security_group(
    GroupName='database-sg',
    Description='Security group for databases',
    VpcId=vpc_id
)
db_sg_id = db_sg['GroupId']

# アプリケーションサーバーからのみDB接続許可
ec2.authorize_security_group_ingress(
    GroupId=db_sg_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 3306,
        'ToPort': 3306,
        'UserIdGroupPairs': [{'GroupId': app_sg_id}]
    }]
)

print(f"3層アーキテクチャのSecurity Groups作成完了")
print(f"ALB SG: {alb_sg_id}")
print(f"Web SG: {web_sg_id}")
print(f"App SG: {app_sg_id}")
print(f"DB SG: {db_sg_id}")
```

## ベストプラクティス（2025年版）

### 1. 最小権限の原則

```bash
# 悪い例: すべて許可
--cidr 0.0.0.0/0 --protocol -1

# 良い例: 必要なポートのみ
--cidr 203.0.113.0/24 --protocol tcp --port 443
```

### 2. Security Group参照を活用

```bash
# IPアドレスではなくSecurity Group IDで参照
--source-group $APP_SG
```

### 3. 説明を必ず記載

```bash
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG \
    --ip-permissions '[{
        "IpProtocol": "tcp",
        "FromPort": 443,
        "ToPort": 443,
        "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS from internet"}]
    }]'
```

### 4. NACLsはサブネットレベルの追加防御層として

```bash
# Security Groups: インスタンスレベル（細かい制御）
# NACLs: サブネットレベル（ブロードな制御、拒否ルール）
```

### 5. 定期的な監査

```python
"""
未使用Security Groupsの検出
"""
import boto3

ec2 = boto3.client('ec2')

# すべてのSecurity Groupsを取得
all_sgs = ec2.describe_security_groups()['SecurityGroups']

# 使用中のSecurity Groupsを取得
used_sgs = set()

# EC2インスタンスが使用しているSG
instances = ec2.describe_instances()
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        for sg in instance['SecurityGroups']:
            used_sgs.add(sg['GroupId'])

# 未使用SGを特定
for sg in all_sgs:
    if sg['GroupId'] not in used_sgs and sg['GroupName'] != 'default':
        print(f"未使用SG: {sg['GroupId']} ({sg['GroupName']})")
```

## よくある落とし穴と対策

### 1. NACLsでリターントラフィックを忘れる

**症状**: アウトバウンド通信が失敗

**対策**: エフェメラルポート（1024-65535）を許可

### 2. Security Groupsで0.0.0.0/0を多用

**症状**: セキュリティリスク

**対策**: 必要なIPレンジのみ許可、または他のSGを参照

### 3. Security Groupsの数が多すぎる

**症状**: 管理が複雑化

**対策**: 1リソースあたり最大5個に制限、再利用を推進

## 判断ポイント

### Security Groups vs NACLs

| 特徴 | Security Groups | Network ACLs |
|-----|----------------|--------------|
| レベル | インスタンス | サブネット |
| ステート | ステートフル | ステートレス |
| ルール | 許可のみ | 許可と拒否 |
| 評価 | すべてのルール | 番号順 |
| 適用 | 明示的に指定 | サブネット内すべて |

### 使い分け

- **Security Groups**: きめ細かいアクセス制御（推奨メイン）
- **NACLs**: サブネットレベルの追加防御、特定IPのブロック

## リソース

### 公式ドキュメント

- [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [Security Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
