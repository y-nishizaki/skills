---
name: aws-codepipeline
description: AWS CodePipelineを使用してCI/CDパイプラインを構築し、CodeCommit、CodeBuild、CodeDeployと統合して自動デプロイメントを実現する方法
---

# AWS CodePipeline スキル

## 概要

AWS CodePipelineは、継続的インテグレーション/継続的デリバリー（CI/CD）を自動化するフルマネージドサービスです。コード変更から本番環境へのデプロイまでのリリースプロセスを自動化し、迅速かつ信頼性の高いアプリケーション更新を実現します。

## 主な使用ケース

### 1. 基本的なパイプライン作成

```bash
# パイプライン作成（JSON定義）
cat > pipeline.json << 'EOF'
{
  "pipeline": {
    "name": "MyAppPipeline",
    "roleArn": "arn:aws:iam::123456789012:role/CodePipelineServiceRole",
    "artifactStore": {
      "type": "S3",
      "location": "my-pipeline-artifacts"
    },
    "stages": [
      {
        "name": "Source",
        "actions": [{
          "name": "SourceAction",
          "actionTypeId": {
            "category": "Source",
            "owner": "AWS",
            "provider": "CodeCommit",
            "version": "1"
          },
          "configuration": {
            "RepositoryName": "my-app-repo",
            "BranchName": "main"
          },
          "outputArtifacts": [{"name": "SourceOutput"}]
        }]
      },
      {
        "name": "Build",
        "actions": [{
          "name": "BuildAction",
          "actionTypeId": {
            "category": "Build",
            "owner": "AWS",
            "provider": "CodeBuild",
            "version": "1"
          },
          "configuration": {
            "ProjectName": "my-build-project"
          },
          "inputArtifacts": [{"name": "SourceOutput"}],
          "outputArtifacts": [{"name": "BuildOutput"}]
        }]
      },
      {
        "name": "Deploy",
        "actions": [{
          "name": "DeployAction",
          "actionTypeId": {
            "category": "Deploy",
            "owner": "AWS",
            "provider": "ECS",
            "version": "1"
          },
          "configuration": {
            "ClusterName": "production-cluster",
            "ServiceName": "web-service",
            "FileName": "imagedefinitions.json"
          },
          "inputArtifacts": [{"name": "BuildOutput"}]
        }]
      }
    ]
  }
}
EOF

aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

### 2. CodeBuildプロジェクト（ビルドステージ）

```yaml
# buildspec.yml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}

  build:
    commands:
      - echo Build started on `date`
      - echo Running tests...
      - npm install
      - npm test
      - echo Building Docker image...
      - docker build -t $ECR_REPOSITORY_URI:latest .
      - docker tag $ECR_REPOSITORY_URI:latest $ECR_REPOSITORY_URI:$IMAGE_TAG

  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing Docker image...
      - docker push $ECR_REPOSITORY_URI:latest
      - docker push $ECR_REPOSITORY_URI:$IMAGE_TAG
      - echo Writing image definitions file...
      - printf '[{"name":"web-container","imageUri":"%s"}]' $ECR_REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
    - '**/*'

cache:
  paths:
    - '/root/.npm/**/*'
```

```bash
# CodeBuildプロジェクト作成
aws codebuild create-project \
    --name my-build-project \
    --source type=CODEPIPELINE \
    --artifacts type=CODEPIPELINE \
    --environment '{
        "type": "LINUX_CONTAINER",
        "image": "aws/codebuild/standard:7.0",
        "computeType": "BUILD_GENERAL1_SMALL",
        "environmentVariables": [
            {"name": "AWS_ACCOUNT_ID", "value": "123456789012"},
            {"name": "ECR_REPOSITORY_URI", "value": "123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/my-app"}
        ],
        "privilegedMode": true
    }' \
    --service-role arn:aws:iam::123456789012:role/CodeBuildServiceRole
```

### 3. CodeDeploy（EC2/ECS/Lambda）

```bash
# CodeDeploy Application作成（ECS）
aws deploy create-application \
    --application-name my-ecs-app \
    --compute-platform ECS

# Deployment Group作成
aws deploy create-deployment-group \
    --application-name my-ecs-app \
    --deployment-group-name production \
    --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
    --ecs-services clusterName=production-cluster,serviceName=web-service \
    --load-balancer-info '{
        "targetGroupPairInfoList": [{
            "targetGroups": [
                {"name": "blue-tg"},
                {"name": "green-tg"}
            ],
            "prodTrafficRoute": {
                "listenerArns": ["arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:listener/app/my-alb/abc123/def456"]
            }
        }]
    }' \
    --blue-green-deployment-configuration '{
        "terminateBlueInstancesOnDeploymentSuccess": {
            "action": "TERMINATE",
            "terminationWaitTimeInMinutes": 5
        },
        "deploymentReadyOption": {
            "actionOnTimeout": "CONTINUE_DEPLOYMENT"
        }
    }' \
    --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL
```

```yaml
# appspec.yml（ECS Blue/Green）
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: "arn:aws:ecs:ap-northeast-1:123456789012:task-definition/web-task:123"
        LoadBalancerInfo:
          ContainerName: "web-container"
          ContainerPort: 80
        PlatformVersion: "LATEST"

Hooks:
  - BeforeInstall: "LambdaFunctionToValidateBeforeInstall"
  - AfterInstall: "LambdaFunctionToValidateAfterInstall"
  - AfterAllowTestTraffic: "LambdaFunctionToValidateAfterTestTrafficStarts"
  - BeforeAllowTraffic: "LambdaFunctionToValidateBeforeAllowingProductionTraffic"
  - AfterAllowTraffic: "LambdaFunctionToValidateAfterAllowingProductionTraffic"
```

### 4. 承認アクション（手動承認）

```bash
# 承認ステージ追加
aws codepipeline update-pipeline --cli-input-json '{
  "pipeline": {
    "name": "MyAppPipeline",
    "stages": [
      {
        "name": "ManualApproval",
        "actions": [{
          "name": "ApproveDeployment",
          "actionTypeId": {
            "category": "Approval",
            "owner": "AWS",
            "provider": "Manual",
            "version": "1"
          },
          "configuration": {
            "NotificationArn": "arn:aws:sns:ap-northeast-1:123456789012:pipeline-approvals",
            "CustomData": "Please review the staging deployment before approving."
          }
        }]
      }
    ]
  }
}'

# 承認/拒否
aws codepipeline put-approval-result \
    --pipeline-name MyAppPipeline \
    --stage-name ManualApproval \
    --action-name ApproveDeployment \
    --result '{
        "summary": "Looks good, deploying to production",
        "status": "Approved"
    }' \
    --token APPROVAL_TOKEN
```

### 5. GitHub統合

```bash
# GitHub v2ソース（推奨、Webhook自動作成）
aws codepipeline create-pipeline --cli-input-json '{
  "pipeline": {
    "name": "GitHubPipeline",
    "stages": [
      {
        "name": "Source",
        "actions": [{
          "name": "GitHubSource",
          "actionTypeId": {
            "category": "Source",
            "owner": "AWS",
            "provider": "CodeStarSourceConnection",
            "version": "1"
          },
          "configuration": {
            "ConnectionArn": "arn:aws:codestar-connections:ap-northeast-1:123456789012:connection/abc-123",
            "FullRepositoryId": "myorg/myrepo",
            "BranchName": "main",
            "OutputArtifactFormat": "CODE_ZIP"
          },
          "outputArtifacts": [{"name": "SourceOutput"}]
        }]
      }
    ]
  }
}'

# CodeStar Connection作成（初回のみ）
aws codestar-connections create-connection \
    --provider-type GitHub \
    --connection-name github-connection
```

### 6. CloudWatch Events統合

```bash
# パイプライン失敗時のSNS通知
aws events put-rule \
    --name pipeline-failure \
    --event-pattern '{
        "source": ["aws.codepipeline"],
        "detail-type": ["CodePipeline Pipeline Execution State Change"],
        "detail": {
            "state": ["FAILED"],
            "pipeline": ["MyAppPipeline"]
        }
    }'

aws events put-targets \
    --rule pipeline-failure \
    --targets "Id"="1","Arn"="arn:aws:sns:ap-northeast-1:123456789012:pipeline-alerts"
```

## ベストプラクティス（2025年版）

### 1. マルチアカウント戦略

```text
開発環境: Account A
ステージング環境: Account B
本番環境: Account C

各環境で専用のAWSアカウント使用:
- セキュリティ境界明確化
- コスト管理容易化
- IAMポリシー分離

Cross-Account IAMロール設定が必要
```

### 2. アーティファクト暗号化

```bash
# S3バケット暗号化（KMS）
aws codepipeline create-pipeline --cli-input-json '{
  "pipeline": {
    "artifactStore": {
      "type": "S3",
      "location": "my-pipeline-artifacts",
      "encryptionKey": {
        "id": "arn:aws:kms:ap-northeast-1:123456789012:key/abc-123",
        "type": "KMS"
      }
    }
  }
}'
```

### 3. 並列実行（テスト高速化）

```json
{
  "name": "Test",
  "actions": [
    {
      "name": "UnitTests",
      "runOrder": 1,
      "actionTypeId": {
        "category": "Test",
        "owner": "AWS",
        "provider": "CodeBuild"
      }
    },
    {
      "name": "IntegrationTests",
      "runOrder": 1,
      "actionTypeId": {
        "category": "Test",
        "owner": "AWS",
        "provider": "CodeBuild"
      }
    }
  ]
}
```

### 4. Blue/Green Deployment

```yaml
# ECS Blue/Greenでゼロダウンタイム
DeploymentConfiguration:
  DeploymentType: BLUE_GREEN
  BlueGreenDeploymentConfiguration:
    TerminateBlueInstancesOnDeploymentSuccess:
      Action: TERMINATE
      TerminationWaitTimeInMinutes: 5
    DeploymentReadyOption:
      ActionOnTimeout: CONTINUE_DEPLOYMENT
```

### 5. ロールバック戦略

```bash
# 前バージョンに手動ロールバック
PREVIOUS_EXECUTION=$(aws codepipeline list-pipeline-executions \
    --pipeline-name MyAppPipeline \
    --max-items 2 \
    --query 'pipelineExecutionSummaries[1].pipelineExecutionId' \
    --output text)

aws codepipeline start-pipeline-execution \
    --name MyAppPipeline \
    --source-revisions actionName=SourceAction,revisionType=COMMIT_ID,revisionValue=PREVIOUS_COMMIT_SHA
```

## よくある失敗パターン

### 1. IAM権限不足

```text
問題: CodeBuildがECRにプッシュできない
解決: CodeBuildサービスロールにECR権限追加

{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload"
    ],
    "Resource": "*"
  }]
}
```

### 2. アーティファクト保持期間未設定

```bash
# S3ライフサイクルポリシーで90日後削除
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-pipeline-artifacts \
    --lifecycle-configuration '{
        "Rules": [{
            "Id": "DeleteOldArtifacts",
            "Status": "Enabled",
            "Expiration": {"Days": 90}
        }]
    }'
```

### 3. シークレット管理の失敗

```bash
# 環境変数にシークレット直接記載（NG）
# Secrets Manager/Parameter Store使用（OK）

aws codebuild update-project \
    --name my-build-project \
    --environment '{
        "environmentVariables": [{
            "name": "DB_PASSWORD",
            "value": "my-db-password",
            "type": "SECRETS_MANAGER"
        }]
    }'
```

## リソース

- [CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [CI/CD Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-cicd-litmus/cicd-best-practices.html)
- [BuildSpec Reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
