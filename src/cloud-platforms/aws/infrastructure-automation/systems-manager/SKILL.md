---
name: aws-systems-manager
description: AWS Systems Managerを使用してParameter Store、Session Manager、パッチ管理、Run Commandでインフラ運用を自動化する方法
---

# AWS Systems Manager スキル

## 概要

AWS Systems Managerは、AWS上のインフラを大規模に可視化・制御するための統合管理サービスです。Parameter Store、Session Manager、Patch Manager、Run Commandなどの機能を提供し、運用を自動化します。

## 主な使用ケース

### 1. Parameter Store（設定管理）

```bash
# パラメータ作成（平文）
aws ssm put-parameter \
    --name /app/database/host \
    --value "db.example.com" \
    --type String \
    --tags Key=Environment,Value=Production

# パラメータ作成（暗号化）
aws ssm put-parameter \
    --name /app/database/password \
    --value "SecurePassword123!" \
    --type SecureString \
    --key-id alias/app-key

# パラメータ取得
aws ssm get-parameter \
    --name /app/database/password \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text

# パスによる一括取得
aws ssm get-parameters-by-path \
    --path /app/database/ \
    --recursive \
    --with-decryption
```

```python
# アプリケーションでの使用
import boto3

ssm = boto3.client('ssm')

# パラメータ取得
response = ssm.get_parameter(
    Name='/app/database/password',
    WithDecryption=True
)
db_password = response['Parameter']['Value']
```

### 2. Session Manager（SSHレス接続）

```bash
# Session Manager経由でEC2に接続
aws ssm start-session --target i-1234567890abcdef0

# ポートフォワーディング（RDS接続など）
aws ssm start-session \
    --target i-1234567890abcdef0 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{
        "host":["db.example.com"],
        "portNumber":["3306"],
        "localPortNumber":["13306"]
    }'

# セッション履歴はCloudWatch Logsに記録
```

### 3. Run Command（コマンド実行）

```bash
# EC2インスタンスでコマンド実行
aws ssm send-command \
    --document-name "AWS-RunShellScript" \
    --targets "Key=tag:Environment,Values=Production" \
    --parameters 'commands=["yum update -y","systemctl restart nginx"]' \
    --comment "Update and restart nginx"

# コマンド結果確認
COMMAND_ID=$(aws ssm send-command --document-name "AWS-RunShellScript" --targets "Key=instanceids,Values=i-1234567890abcdef0" --parameters 'commands=["uptime"]' --query 'Command.CommandId' --output text)

aws ssm get-command-invocation \
    --command-id $COMMAND_ID \
    --instance-id i-1234567890abcdef0
```

### 4. Patch Manager（パッチ管理）

```bash
# パッチベースラインの作成
aws ssm create-patch-baseline \
    --name "ProductionBaseline" \
    --operating-system AMAZON_LINUX_2023 \
    --approval-rules '{
        "PatchRules": [{
            "PatchFilterGroup": {
                "PatchFilters": [{
                    "Key": "CLASSIFICATION",
                    "Values": ["Security","Bugfix"]
                }]
            },
            "ApproveAfterDays": 7,
            "ComplianceLevel": "CRITICAL"
        }]
    }'

# メンテナンスウィンドウの作成
aws ssm create-maintenance-window \
    --name "ProductionPatchWindow" \
    --schedule "cron(0 2 ? * SUN *)" \
    --duration 4 \
    --cutoff 1 \
    --allow-unassociated-targets

# パッチタスクの登録
aws ssm register-task-with-maintenance-window \
    --window-id mw-0123456789abcdef0 \
    --task-type RUN_COMMAND \
    --task-arn AWS-RunPatchBaseline \
    --targets "Key=tag:PatchGroup,Values=Production" \
    --priority 1 \
    --max-concurrency 10 \
    --max-errors 1
```

### 5. State Manager（設定管理）

```bash
# 関連付けの作成（CloudWatch Agentの自動インストール）
aws ssm create-association \
    --name "AWS-ConfigureAWSPackage" \
    --targets "Key=tag:Environment,Values=Production" \
    --parameters '{
        "action": ["Install"],
        "name": ["AmazonCloudWatchAgent"],
        "version": ["latest"]
    }' \
    --schedule-expression "rate(30 days)"
```

### 6. Automation（運用自動化）

```bash
# AMI作成の自動化
aws ssm start-automation-execution \
    --document-name "AWS-CreateImage" \
    --parameters '{
        "InstanceId": ["i-1234567890abcdef0"],
        "NoReboot": ["true"],
        "ImageName": ["backup-$(date +%Y%m%d)"]
    }'

# 実行状況確認
EXECUTION_ID=$(aws ssm start-automation-execution --document-name "AWS-CreateImage" --parameters '{"InstanceId":["i-1234567890abcdef0"]}' --query 'AutomationExecutionId' --output text)

aws ssm get-automation-execution \
    --automation-execution-id $EXECUTION_ID
```

## ベストプラクティス（2025年版）

### 1. Parameter Storeの階層構造

```bash
# 環境別・アプリケーション別に整理
/production/app1/database/host
/production/app1/database/password
/production/app2/api/key
/staging/app1/database/host
```

### 2. Session Manager接続ログ

```json
{
  "schemaVersion": "1.0",
  "description": "Session Manager Configuration",
  "sessionType": "Standard_Stream",
  "inputs": {
    "s3BucketName": "session-logs-bucket",
    "s3KeyPrefix": "sessions/",
    "cloudWatchLogGroupName": "/aws/ssm/sessions",
    "cloudWatchEncryptionEnabled": true,
    "kmsKeyId": "alias/session-logs-key"
  }
}
```

### 3. Run Command + SNS通知

```bash
# コマンド完了時にSNS通知
aws ssm send-command \
    --document-name "AWS-RunShellScript" \
    --targets "Key=tag:Environment,Values=Production" \
    --parameters 'commands=["yum update -y"]' \
    --notification-config '{
        "NotificationArn": "arn:aws:sns:ap-northeast-1:123456789012:ops-notifications",
        "NotificationEvents": ["Success","Failed"],
        "NotificationType": "Command"
    }'
```

## リソース

- [Systems Manager Documentation](https://docs.aws.amazon.com/systems-manager/)
- [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
