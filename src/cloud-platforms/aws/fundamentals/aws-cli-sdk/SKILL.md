---
name: "AWS CLI / SDK"
description: "AWS CLIとSDKを使ったAWSリソースの管理と自動化。インストール、設定、基本コマンド、プログラマティックアクセス、ベストプラクティス、CI/CD統合に関する思考プロセスを提供"
---

# AWS CLI / SDK

## このスキルを使う場面

- AWSリソースのコマンドライン管理
- インフラ自動化スクリプトの作成
- CI/CDパイプラインでのAWS操作
- プログラマティックなリソース管理
- バッチ処理とタスク自動化
- AWSサービスのテストと検証

## AWS CLIとは

AWS Command Line Interface (CLI)は、コマンドラインからAWSサービスを管理するための統一されたツール。コマンドラインシェルからAWSサービスと対話し、スクリプトによる自動化を実現する。

### AWS CLIの主要機能

**統一されたインターフェース:**

- すべてのAWSサービスを一貫したコマンド体系で操作
- サービス間の統合が容易
- 学習コストの削減

**スクリプト自動化:**

- シェルスクリプトでAWS操作を自動化
- 繰り返しタスクの効率化
- バッチ処理の実装

**マルチプラットフォーム対応:**

- Windows、macOS、Linux対応
- Docker環境での実行
- CI/CDツールとの統合

## AWS SDKとは

AWS Software Development Kits (SDKs)は、プログラミング言語固有のAWS APIラッパー。アプリケーションからAWSサービスをプログラマティックに操作する。

### 主要なSDK

- **AWS SDK for Python (Boto3)** - Python
- **AWS SDK for JavaScript** - Node.js/ブラウザ
- **AWS SDK for Java** - Java
- **AWS SDK for .NET** - C#/.NET
- **AWS SDK for Go** - Go
- **AWS SDK for Ruby** - Ruby
- **AWS SDK for PHP** - PHP

## 思考プロセス

### フェーズ1: AWS CLIのインストールと設定

**ステップ1: AWS CLIのインストール**

**Linux:**

```bash
# AWS CLI v2のインストール
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# インストール確認
aws --version
```

**macOS:**

```bash
# Homebrewを使用
brew install awscli

# または公式インストーラー
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# インストール確認
aws --version
```

**Windows:**

```powershell
# MSIインストーラーをダウンロードして実行
# https://awscli.amazonaws.com/AWSCLIV2.msi

# インストール確認
aws --version
```

**Docker:**

```bash
# AWS CLI v2のDockerイメージ
docker pull amazon/aws-cli:latest

# コンテナで実行
docker run --rm -it amazon/aws-cli --version
```

**ステップ2: 認証情報の設定**

**IAMユーザーのアクセスキーを使用（レガシー、推奨されない）:**

```bash
# 基本設定
aws configure

# プロンプトに応答
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

**名前付きプロファイルの使用（推奨）:**

```bash
# プロファイルを指定して設定
aws configure --profile production
aws configure --profile development

# プロファイルを使用
aws s3 ls --profile production

# 環境変数でプロファイルを指定
export AWS_PROFILE=production
aws s3 ls
```

**IAMロールの使用（EC2インスタンス上、推奨）:**

```bash
# EC2インスタンスでIAMロールを使用する場合、設定不要
# インスタンスプロファイルから自動的に一時的な認証情報を取得

# 認証情報の確認
aws sts get-caller-identity
```

**SSOの使用（2025年推奨）:**

```bash
# AWS SSOの設定
aws configure sso

# プロンプトに応答
SSO start URL [None]: https://my-sso-portal.awsapps.com/start
SSO region [None]: us-east-1
# ブラウザで認証

# SSOプロファイルを使用
aws s3 ls --profile my-sso-profile

# SSOログイン
aws sso login --profile my-sso-profile
```

**ステップ3: 設定ファイルの確認**

```bash
# 認証情報ファイルの場所
# Linux/macOS: ~/.aws/credentials
# Windows: C:\Users\USERNAME\.aws\credentials

cat ~/.aws/credentials
```

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[production]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

```bash
# 設定ファイルの場所
# Linux/macOS: ~/.aws/config
# Windows: C:\Users\USERNAME\.aws\config

cat ~/.aws/config
```

```ini
[default]
region = ap-northeast-1
output = json

[profile production]
region = us-east-1
output = json
role_arn = arn:aws:iam::123456789012:role/ProductionRole
source_profile = default
```

**移行条件:**

- [ ] AWS CLIをインストールした
- [ ] 認証情報を設定した
- [ ] 接続をテストした
- [ ] 複数のプロファイルを設定した（該当する場合）

### フェーズ2: 基本コマンドの習得

**ステップ1: 共通オプションの理解**

```bash
# ヘルプの表示
aws help
aws s3 help
aws s3 ls help

# 出力形式の指定
aws ec2 describe-instances --output json
aws ec2 describe-instances --output table
aws ec2 describe-instances --output text
aws ec2 describe-instances --output yaml

# リージョンの指定
aws ec2 describe-instances --region us-east-1

# クエリによるフィルタリング
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]' \
    --output table
```

**ステップ2: 主要サービスのコマンド**

**S3操作:**

```bash
# バケット一覧
aws s3 ls

# バケットの内容表示
aws s3 ls s3://my-bucket/

# ファイルのアップロード
aws s3 cp local-file.txt s3://my-bucket/
aws s3 cp local-directory/ s3://my-bucket/directory/ --recursive

# ファイルのダウンロード
aws s3 cp s3://my-bucket/remote-file.txt ./
aws s3 sync s3://my-bucket/ ./local-directory/

# バケットの作成・削除
aws s3 mb s3://new-bucket
aws s3 rb s3://old-bucket --force
```

**EC2操作:**

```bash
# インスタンス一覧
aws ec2 describe-instances

# インスタンスの起動
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --key-name my-key-pair \
    --security-group-ids sg-903004f8 \
    --subnet-id subnet-6e7f829e

# インスタンスの停止・起動・終了
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# AMI一覧
aws ec2 describe-images \
    --owners self \
    --filters "Name=name,Values=my-ami-*"
```

**IAM操作:**

```bash
# ユーザー一覧
aws iam list-users

# ユーザーの作成
aws iam create-user --user-name new-user

# グループの作成とユーザーの追加
aws iam create-group --group-name developers
aws iam add-user-to-group --user-name new-user --group-name developers

# ポリシーのアタッチ
aws iam attach-user-policy \
    --user-name new-user \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

**Lambda操作:**

```bash
# 関数一覧
aws lambda list-functions

# 関数の呼び出し
aws lambda invoke \
    --function-name my-function \
    --payload '{"key1":"value1"}' \
    response.json

# 関数の更新
aws lambda update-function-code \
    --function-name my-function \
    --zip-file fileb://function.zip
```

**ステップ3: 高度なクエリとフィルタリング**

**JMESPathクエリ:**

```bash
# 特定のフィールドのみ抽出
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress]' \
    --output table

# 条件付きフィルタ
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[?State.Name==`running`].InstanceId' \
    --output text

# 複雑なクエリ
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name,IP:PublicIpAddress}' \
    --output table
```

**フィルターオプション:**

```bash
# EC2インスタンスのフィルタリング
aws ec2 describe-instances \
    --filters "Name=instance-type,Values=t2.micro" \
              "Name=instance-state-name,Values=running"

# タグによるフィルタリング
aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=production"
```

**移行条件:**

- [ ] 基本コマンドを習得した
- [ ] クエリとフィルタリングを理解した
- [ ] 各サービスの主要な操作を実行できる

### フェーズ3: スクリプトと自動化

**ステップ1: シェルスクリプトの作成**

```bash
#!/bin/bash
# EC2インスタンスのバックアップスクリプト

INSTANCE_ID="i-1234567890abcdef0"
DESCRIPTION="Automated backup $(date +%Y-%m-%d-%H-%M)"

# AMIの作成
AMI_ID=$(aws ec2 create-image \
    --instance-id $INSTANCE_ID \
    --name "backup-$INSTANCE_ID-$(date +%Y%m%d)" \
    --description "$DESCRIPTION" \
    --no-reboot \
    --query 'ImageId' \
    --output text)

echo "Created AMI: $AMI_ID"

# タグの追加
aws ec2 create-tags \
    --resources $AMI_ID \
    --tags Key=Type,Value=Backup Key=Date,Value=$(date +%Y-%m-%d)

# 古いAMIの削除（30日以上前）
OLD_AMIS=$(aws ec2 describe-images \
    --owners self \
    --filters "Name=name,Values=backup-$INSTANCE_ID-*" \
    --query "Images[?CreationDate<'$(date -d '30 days ago' +%Y-%m-%d)'].ImageId" \
    --output text)

for AMI in $OLD_AMIS; do
    echo "Deleting old AMI: $AMI"
    aws ec2 deregister-image --image-id $AMI
done
```

**ステップ2: エラーハンドリング**

```bash
#!/bin/bash
set -e  # エラーで終了
set -u  # 未定義変数でエラー
set -o pipefail  # パイプラインのエラーを検出

# エラーハンドリング関数
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# コマンド実行
aws s3 cp file.txt s3://my-bucket/ || error_exit "Failed to upload file"

# 戻り値のチェック
if aws ec2 describe-instances --instance-ids i-1234567890abcdef0 > /dev/null 2>&1; then
    echo "Instance exists"
else
    echo "Instance not found"
fi
```

**ステップ3: 環境変数の活用**

```bash
# 認証情報
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=ap-northeast-1

# プロファイル
export AWS_PROFILE=production

# デバッグモード
export AWS_DEBUG=true

# リトライ設定
export AWS_MAX_ATTEMPTS=3
export AWS_RETRY_MODE=adaptive
```

**移行条件:**

- [ ] 基本的なスクリプトを作成した
- [ ] エラーハンドリングを実装した
- [ ] 環境変数を理解した
- [ ] 実際のユースケースで動作確認した

### フェーズ4: CI/CDとの統合

**ステップ1: GitLab CIでの使用**

```yaml
# .gitlab-ci.yml
deploy:
  image: amazon/aws-cli:latest
  stage: deploy
  script:
    - aws s3 sync ./dist s3://my-website-bucket/ --delete
    - aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
  environment:
    name: production
  only:
    - main
```

**ステップ2: GitHub Actionsでの使用**

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: ap-northeast-1

      - name: Deploy to S3
        run: |
          aws s3 sync ./dist s3://my-website-bucket/ --delete

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id E1234567890ABC \
            --paths "/*"
```

**ステップ3: Jenkinsでの使用**

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-northeast-1'
        AWS_CREDENTIALS = credentials('aws-credentials-id')
    }

    stages {
        stage('Deploy') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials-id', region: 'ap-northeast-1') {
                        sh 'aws s3 sync ./dist s3://my-website-bucket/ --delete'
                        sh 'aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"'
                    }
                }
            }
        }
    }
}
```

**移行条件:**

- [ ] CI/CDツールと統合した
- [ ] セキュアな認証情報管理を実装した
- [ ] デプロイプロセスを自動化した
- [ ] ロールバック戦略を定義した

### フェーズ5: SDKの使用

**ステップ1: Boto3 (Python)の基本**

```python
import boto3
from botocore.exceptions import ClientError

# クライアントの作成
s3 = boto3.client('s3')
ec2 = boto3.client('ec2', region_name='ap-northeast-1')

# リソースの作成（高レベルAPI）
s3_resource = boto3.resource('s3')

# S3操作
try:
    # バケット一覧
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"Bucket: {bucket['Name']}")

    # ファイルのアップロード
    s3.upload_file('local-file.txt', 'my-bucket', 'remote-file.txt')

    # ファイルのダウンロード
    s3.download_file('my-bucket', 'remote-file.txt', 'downloaded-file.txt')

except ClientError as e:
    print(f"Error: {e}")

# EC2操作
try:
    # インスタンス一覧
    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            print(f"Instance ID: {instance['InstanceId']}, State: {instance['State']['Name']}")

    # インスタンスの起動
    response = ec2.run_instances(
        ImageId='ami-0c55b159cbfafe1f0',
        InstanceType='t3.micro',
        MinCount=1,
        MaxCount=1
    )

except ClientError as e:
    print(f"Error: {e}")
```

**ステップ2: Node.js SDKの基本**

```javascript
const AWS = require('aws-sdk');

// クライアントの作成
const s3 = new AWS.S3();
const ec2 = new AWS.EC2({region: 'ap-northeast-1'});

// S3操作
async function listBuckets() {
    try {
        const data = await s3.listBuckets().promise();
        console.log('Buckets:', data.Buckets);
    } catch (err) {
        console.error('Error:', err);
    }
}

// ファイルのアップロード
async function uploadFile() {
    const params = {
        Bucket: 'my-bucket',
        Key: 'remote-file.txt',
        Body: fs.createReadStream('local-file.txt')
    };

    try {
        const data = await s3.upload(params).promise();
        console.log('Upload successful:', data.Location);
    } catch (err) {
        console.error('Error:', err);
    }
}

// EC2操作
async function listInstances() {
    try {
        const data = await ec2.describeInstances().promise();
        data.Reservations.forEach(reservation => {
            reservation.Instances.forEach(instance => {
                console.log(`Instance ID: ${instance.InstanceId}, State: ${instance.State.Name}`);
            });
        });
    } catch (err) {
        console.error('Error:', err);
    }
}
```

**移行条件:**

- [ ] SDKをインストールした
- [ ] 基本的な操作を実装した
- [ ] エラーハンドリングを実装した
- [ ] 本番環境で動作確認した

## ベストプラクティス

### セキュリティ

**1. IAMロールの使用（推奨）:**

EC2インスタンス、Lambda、ECSなどでIAMロールを使用:

```bash
# EC2インスタンスにIAMロールを設定
aws ec2 associate-iam-instance-profile \
    --instance-id i-1234567890abcdef0 \
    --iam-instance-profile Name=EC2-S3-Access-Role

# アクセスキー不要でAWS CLIを使用可能
aws s3 ls
```

**2. 認証情報を

コードに埋め込まない:**

- ❌ スクリプトにアクセスキーをハードコード
- ✅ 環境変数、設定ファイル、IAMロールを使用

**3. 名前付きプロファイルの使用:**

複数のAWSアカウントや環境を管理:

```bash
# 本番環境用プロファイル
aws s3 ls --profile production

# 開発環境用プロファイル
aws s3 ls --profile development
```

**4. MFAが必要なプロファイル:**

```ini
[profile mfa]
role_arn = arn:aws:iam::123456789012:role/AdminRole
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/user
```

### パフォーマンス

**1. ページネーション:**

大量のデータを効率的に取得:

```bash
# 自動ページネーション
aws s3api list-objects --bucket my-bucket --max-items 1000

# マニュアルページネーション
aws s3api list-objects --bucket my-bucket --max-items 100 --starting-token <token>
```

**2. 並列実行:**

```bash
# 複数のコマンドを並列実行
aws ec2 describe-instances &
aws s3 ls &
aws lambda list-functions &
wait
```

**3. リトライ設定:**

```bash
# 最大リトライ回数
export AWS_MAX_ATTEMPTS=5

# リトライモード
export AWS_RETRY_MODE=adaptive
```

### デバッグ

**1. デバッグモード:**

```bash
# 詳細ログの有効化
aws s3 ls --debug

# HTTPリクエスト/レスポンスの表示
export AWS_DEBUG=true
aws s3 ls
```

**2. DryRun:**

実際に実行せずにコマンドを検証:

```bash
# EC2インスタンスの起動をシミュレート
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --dry-run
```

## よくある落とし穴

1. **認証情報の管理ミス**
   - ❌ コードにアクセスキーを埋め込む
   - ✅ IAMロール、環境変数、プロファイルを使用

2. **リージョンの指定忘れ**
   - ❌ デフォルトリージョンに依存
   - ✅ 明示的にリージョンを指定

3. **エラーハンドリングの欠如**
   - ❌ エラーを無視
   - ✅ 適切なエラーハンドリングを実装

4. **ページネーションの見落とし**
   - ❌ 大量データで最初の1000件のみ取得
   - ✅ ページネーションを使用

5. **プロファイルの混同**
   - ❌ 本番環境で開発用プロファイルを使用
   - ✅ プロファイルを明示的に指定

6. **Python 3.8のサポート終了**
   - ❌ 古いPythonバージョンでAWS CLIを実行
   - ✅ Python 3.9以降を使用（2025年4月22日以降）

## 検証ポイント

### インストールと設定

- [ ] AWS CLIをインストールした
- [ ] 認証情報を設定した
- [ ] 複数のプロファイルを設定した
- [ ] 接続をテストした

### 基本操作

- [ ] 主要なサービスの操作を習得した
- [ ] クエリとフィルタリングを使用できる
- [ ] 出力形式を変更できる

### 自動化

- [ ] シェルスクリプトを作成した
- [ ] エラーハンドリングを実装した
- [ ] CI/CDツールと統合した

### セキュリティ

- [ ] IAMロールを使用している
- [ ] 認証情報をセキュアに管理している
- [ ] 最小権限の原則を適用している

## 他スキルとの連携

### aws-cli-sdk + iam

CLI/SDKとIAMの組み合わせ:

1. iamで適切な権限を設計
2. aws-cli-sdkでプログラマティックアクセスを実装
3. セキュアな自動化を実現

### aws-cli-sdk + cloudformation

CLI/SDKとIaCの組み合わせ:

1. cloudformationでインフラをコード化
2. aws-cli-sdkでスタックのデプロイを自動化
3. CI/CDパイプラインを構築

### aws-cli-sdk + lambda

CLI/SDKとサーバーレスの組み合わせ:

1. aws-cli-sdkでLambda関数をデプロイ
2. lambdaで自動化処理を実装
3. イベント駆動アーキテクチャを構築

## リソース

### 公式ドキュメント

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/index.html)
- [AWS SDKs](https://aws.amazon.com/tools/)

### SDK別ドキュメント

- [Boto3 (Python)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS SDK for JavaScript](https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/)
- [AWS SDK for Java](https://docs.aws.amazon.com/sdk-for-java/)

### 学習リソース

- [AWS CLI Tutorial](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-tutorial.html)
- [AWS CLI Best Practices](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-best-practices.html)
