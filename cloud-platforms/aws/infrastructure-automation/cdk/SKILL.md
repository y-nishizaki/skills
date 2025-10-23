---
name: aws-cdk
description: AWS CDK（Cloud Development Kit）を使用してTypeScript/Pythonでインフラをコード化し、高レベルコンストラクトで効率的にAWSリソースを定義する方法
---

# AWS CDK スキル

## 概要

AWS CDK（Cloud Development Kit）は、TypeScript、Python、Java、C#などのプログラミング言語でAWSインフラを定義できるフレームワークです。高レベルコンストラクトを使用して、少ないコードで複雑なインフラを構築します。

## 主な使用ケース

### 1. CDKアプリの初期化

```bash
# CDKインストール
npm install -g aws-cdk

# プロジェクト初期化（TypeScript）
mkdir my-cdk-app && cd my-cdk-app
cdk init app --language typescript

# プロジェクト初期化（Python）
cdk init app --language python
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. VPCスタック（TypeScript）

```typescript
// lib/vpc-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new ec2.Vpc(this, 'ProductionVPC', {
      maxAzs: 2,
      natGateways: 2,
      subnetConfiguration: [
        {
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 21,
        },
      ],
    });

    new cdk.CfnOutput(this, 'VPCId', {
      value: this.vpc.vpcId,
      exportName: 'ProductionVPCId',
    });
  }
}
```

### 3. RDSスタック（Python）

```python
# lib/database_stack.py
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy,
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.db = rds.DatabaseInstance(
            self, "ProductionDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MEDIUM
            ),
            vpc=vpc,
            multi_az=True,
            allocated_storage=100,
            storage_type=rds.StorageType.GP3,
            backup_retention=cdk.Duration.days(7),
            deletion_protection=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
        )
```

### 4. デプロイメント

```bash
# Synthesize (CloudFormationテンプレート生成)
cdk synth

# 差分確認
cdk diff

# デプロイ
cdk deploy --all

# 特定のスタックのみ
cdk deploy VpcStack

# スタック削除
cdk destroy VpcStack
```

### 5. 高レベルコンストラクト

```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';

// Fargate + ALBを数行で構築
new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'WebApp', {
  cluster: cluster,
  taskImageOptions: {
    image: ecs.ContainerImage.fromRegistry('nginx'),
  },
  desiredCount: 3,
});
```

## ベストプラクティス（2025年版）

### 1. Aspectsで共通設定

```typescript
import { Aspects, Tag } from 'aws-cdk-lib';

Aspects.of(app).add(new Tag('Environment', 'Production'));
Aspects.of(app).add(new Tag('ManagedBy', 'CDK'));
```

### 2. コンテキスト値

```json
// cdk.json
{
  "context": {
    "environment": "production",
    "vpcCidr": "10.0.0.0/16"
  }
}
```

## リソース

- [CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [CDK Workshop](https://cdkworkshop.com/)
- [Construct Hub](https://constructs.dev/)
