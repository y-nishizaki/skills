---
name: aws-elastic-beanstalk
description: AWS Elastic Beanstalkを使用してWebアプリケーションを簡単にデプロイし、Blue/Green、Immutable、Rolling deploymentで本番環境を運用する方法
---

# AWS Elastic Beanstalk スキル

## 概要

AWS Elastic Beanstalkは、WebアプリケーションとサービスをAWSに簡単にデプロイ・スケールできるPaaS（Platform as a Service）です。Java、.NET、Node.js、Python、Ruby、Go、PHPをサポートし、インフラ管理を自動化します。

## 主な使用ケース

### 1. アプリケーション作成とデプロイ

```bash
# EB CLI インストール
pip install awsebcli

# プロジェクト初期化
cd my-app
eb init

# 環境作成とデプロイ
eb create production-env \
    --instance-type t3.medium \
    --platform "Python 3.11 running on 64bit Amazon Linux 2023" \
    --envvars "DB_HOST=db.example.com,DB_NAME=mydb"

# アプリケーションデプロイ
eb deploy

# 環境確認
eb status

# アプリケーションを開く
eb open

# ログ確認
eb logs

# SSH接続
eb ssh
```

### 2. .ebextensions（カスタマイズ）

```yaml
# .ebextensions/01-packages.config
packages:
  yum:
    git: []
    postgresql-devel: []

option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium
    EC2KeyName: my-keypair
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
    LoadBalancerType: application

# .ebextensions/02-cloudwatch-logs.config
files:
  "/opt/aws/amazon-cloudwatch-agent/etc/config.json":
    mode: "000600"
    owner: root
    group: root
    content: |
      {
        "logs": {
          "logs_collected": {
            "files": {
              "collect_list": [{
                "file_path": "/var/log/eb-engine.log",
                "log_group_name": "/aws/elasticbeanstalk/production/eb-engine",
                "log_stream_name": "{instance_id}"
              }]
            }
          }
        }
      }

commands:
  01_start_cloudwatch_agent:
    command: |
      /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
        -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 3. デプロイメントポリシー

```bash
# All-at-once（最速、ダウンタイムあり）
eb config set --deployment-policy AllAtOnce

# Rolling（バッチ単位、一部ダウン）
eb config set --deployment-policy Rolling \
    --deployment-batch-size 30 \
    --deployment-batch-size-type Percentage

# Rolling with additional batch（キャパシティ維持）
eb config set --deployment-policy RollingWithAdditionalBatch \
    --deployment-batch-size 2

# Immutable（新インスタンス、最も安全）
eb config set --deployment-policy Immutable

# Traffic splitting（カナリアデプロイ）
eb config set --deployment-policy TrafficSplitting \
    --traffic-split-evaluation-time 5 \
    --traffic-split-percentage 20
```

```yaml
# .ebextensions/03-deployment.config
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: Immutable
    HealthCheckSuccessThreshold: Ok
    Timeout: "600"
  aws:elasticbeanstalk:application:environment:
    DEPLOYMENT_MODE: production
```

### 4. Blue/Green Deployment

```bash
# ステップ1: Greenenv作成（クローン）
eb clone production-env --clone-name green-env

# ステップ2: Greenにデプロイ
eb use green-env
eb deploy

# ステップ3: テスト
eb open

# ステップ4: CNAMEスワップ（トラフィック切り替え）
eb swap production-env --destination-name green-env

# ステップ5: 確認後、旧環境削除
eb terminate production-env --force
```

### 5. Auto Scaling設定

```yaml
# .ebextensions/04-autoscaling.config
option_settings:
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Statistic: Average
    Unit: Percent
    UpperThreshold: 70
    UpperBreachScaleIncrement: 2
    LowerThreshold: 30
    LowerBreachScaleIncrement: -1
```

### 6. 環境変数とシークレット

```bash
# 環境変数設定
eb setenv DB_HOST=db.example.com \
    DB_PORT=5432 \
    DB_NAME=production

# Secrets Manager統合
eb setenv DB_PASSWORD="{{resolve:secretsmanager:prod/db/password:SecretString:password}}"
```

```python
# Pythonアプリケーションで使用
import os

db_host = os.environ.get('DB_HOST')
db_password = os.environ.get('DB_PASSWORD')
```

### 7. RDS統合

```bash
# RDS作成（Elastic Beanstalk管理外、推奨）
aws rds create-db-instance \
    --db-instance-identifier production-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --master-username admin \
    --master-user-password SecurePass123! \
    --allocated-storage 100 \
    --vpc-security-group-ids sg-abc123

# Elastic Beanstalk環境変数に設定
eb setenv RDS_HOSTNAME=production-db.abc123.ap-northeast-1.rds.amazonaws.com \
    RDS_PORT=5432 \
    RDS_DB_NAME=mydb \
    RDS_USERNAME=admin \
    RDS_PASSWORD="{{resolve:secretsmanager:prod/rds:SecretString:password}}"
```

## ベストプラクティス（2025年版）

### 1. デプロイメントポリシー選択

```text
開発環境: All-at-once（最速）
ステージング: Rolling（コスト削減）
本番環境: Immutable または Traffic Splitting（最も安全）

Traffic Splitting推奨ケース:
- 新機能のカナリアテスト
- パフォーマンス影響を段階的に確認
- 自動ロールバック機能活用
```

### 2. ヘルスチェック設定

```yaml
# .ebextensions/05-healthcheck.config
option_settings:
  aws:elasticbeanstalk:application:
    Application Healthcheck URL: /health
  aws:elb:healthcheck:
    HealthyThreshold: "3"
    UnhealthyThreshold: "5"
    Interval: "30"
    Timeout: "5"
```

```python
# Flaskアプリケーション例
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    # データベース接続確認など
    try:
        db.execute('SELECT 1')
        return jsonify({'status': 'healthy'}), 200
    except:
        return jsonify({'status': 'unhealthy'}), 503
```

### 3. CloudWatch Logs統合

```yaml
# .ebextensions/06-cloudwatch-logs.config
option_settings:
  aws:elasticbeanstalk:cloudwatch:logs:
    StreamLogs: true
    DeleteOnTerminate: false
    RetentionInDays: 30
  aws:elasticbeanstalk:cloudwatch:logs:health:
    HealthStreamingEnabled: true
    DeleteOnTerminate: false
    RetentionInDays: 7
```

### 4. マルチAZ RDS（本番環境）

```bash
# RDS Multi-AZ
aws rds create-db-instance \
    --multi-az \
    --backup-retention-period 30 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "sun:04:00-sun:05:00"
```

### 5. HTTPSリダイレクト

```yaml
# .ebextensions/07-https-redirect.config
files:
  "/etc/httpd/conf.d/ssl_rewrite.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      RewriteEngine On
      RewriteCond %{HTTP:X-Forwarded-Proto} !https
      RewriteCond %{REQUEST_URI} !^/health
      RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

### 6. コスト最適化

```bash
# Spot Instances使用（70%コスト削減）
eb config set --instance-types t3.medium,t3a.medium \
    --enable-spot \
    --spot-max-price 0.05
```

## よくある失敗パターン

### 1. RDSを環境内に作成

```text
問題: Elastic Beanstalk環境削除時にRDSも削除される
解決: RDSは独立して作成し、環境変数で接続

# 悪い例: eb create時に--database オプション（NG）
# 良い例: 独立したRDS + 環境変数設定（OK）
```

### 2. .ebignore未設定

```bash
# .ebignore（デプロイ対象外ファイル）
.git/
.gitignore
*.pyc
__pycache__/
venv/
*.log
.env

# デプロイサイズ削減 → デプロイ時間短縮
```

### 3. デプロイタイムアウト

```yaml
# タイムアウト延長
option_settings:
  aws:elasticbeanstalk:command:
    Timeout: "900"  # 15分（デフォルト600秒）
```

### 4. ログ永続化未設定

```text
問題: インスタンス終了時にログ消失
解決: CloudWatch Logs統合またはS3保存

option_settings:
  aws:elasticbeanstalk:hostmanager:
    LogPublicationControl: true
```

## リソース

- [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Deployment Policies](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.rolling-version-deploy.html)
- [.ebextensions Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/ebextensions.html)
