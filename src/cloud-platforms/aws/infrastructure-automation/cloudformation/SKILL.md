---
name: aws-cloudformation
description: AWS CloudFormationを使用してInfrastructure as Code（IaC）を実装し、スタック管理、ドリフト検出、ChangeSetで安全にインフラをプロビジョニングする方法
---

# AWS CloudFormation スキル

## 概要

AWS CloudFormationは、AWSリソースをコードとして定義・管理するInfrastructure as Code（IaC）サービスです。YAML/JSON形式のテンプレートでインフラを宣言的に記述し、自動プロビジョニング、変更管理、ドリフト検出を実現します。

## 主な使用ケース

### 1. 基本的なスタック作成

```yaml
# vpc-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VPC with public and private subnets'

Parameters:
  VpcCIDR:
    Type: String
    Default: 10.0.0.0/16

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCIDR
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: ProductionVPC

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

Outputs:
  VPCId:
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'
```

```bash
# スタック作成
aws cloudformation create-stack \
    --stack-name production-vpc \
    --template-body file://vpc-stack.yaml \
    --parameters ParameterKey=VpcCIDR,ParameterValue=10.0.0.0/16
```

### 2. ChangeSet（変更プレビュー）

```bash
# ChangeSe作成
aws cloudformation create-change-set \
    --stack-name production-vpc \
    --change-set-name update-subnets \
    --template-body file://vpc-stack-updated.yaml \
    --parameters ParameterKey=VpcCIDR,ParameterValue=10.0.0.0/16

# ChangeSet確認
aws cloudformation describe-change-set \
    --stack-name production-vpc \
    --change-set-name update-subnets

# 実行
aws cloudformation execute-change-set \
    --stack-name production-vpc \
    --change-set-name update-subnets
```

### 3. ネストされたスタック

```yaml
# master-stack.yaml
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/templates/vpc-stack.yaml
      Parameters:
        VpcCIDR: 10.0.0.0/16

  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: https://s3.amazonaws.com/templates/app-stack.yaml
      Parameters:
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
```

### 4. ドリフト検出

```bash
# ドリフト検出開始
aws cloudformation detect-stack-drift --stack-name production-vpc

# 結果確認
aws cloudformation describe-stack-drift-detection-status \
    --stack-drift-detection-id DRIFT_DETECTION_ID

# リソースレベルのドリフト詳細
aws cloudformation describe-stack-resource-drifts \
    --stack-name production-vpc
```

## ベストプラクティス（2025年版）

### 1. パラメータとSecrets Managerの統合

```yaml
Parameters:
  DBPassword:
    Type: String
    NoEcho: true

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DBPasswordSecret}::password}}'
```

### 2. スタックポリシー

```json
{
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "Update:Delete",
    "Resource": "LogicalResourceId/ProductionDatabase"
  }]
}
```

## リソース

- [CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
