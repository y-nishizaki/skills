---
name: "AWS IAM (Identity and Access Management)"
description: "AWSリソースへのアクセス管理とセキュリティ。ユーザー、グループ、ロール、ポリシー、MFA、最小権限の原則、ベストプラクティスに基づいたIAM設計の思考プロセスを提供"
---

# AWS IAM (Identity and Access Management)

## このスキルを使う場面

- AWSリソースへのアクセス制御の設計
- セキュアな認証・認可の実装
- 最小権限の原則に基づいた権限設計
- IAMポリシーの作成・管理
- マルチアカウント環境のアクセス管理
- セキュリティ監査とコンプライアンス対応

## IAMとは

AWS Identity and Access Management (IAM)は、AWSリソースへのアクセスを安全に管理するためのサービス。ユーザー、グループ、ロールを使用してAWSサービスとリソースへのアクセスを制御し、きめ細かい権限管理を実現する。

### IAMの主要機能

**認証（Authentication）:**

- ユーザーやサービスの身元を確認
- MFA（多要素認証）によるセキュリティ強化
- 一時的な認証情報（STS）の発行

**認可（Authorization）:**

- アクセス権限の定義と管理
- ポリシーベースの権限制御
- リソースレベルでの細かい制御

**監査（Auditing）:**

- アクセスログの記録（CloudTrail）
- 権限の使用状況の分析
- 未使用の認証情報の特定

## IAMの主要コンポーネント

### ユーザー（Users）

個人またはアプリケーションを表すIAMエンティティ。

**特徴:**

- 長期的な認証情報（パスワード、アクセスキー）
- 個別の権限設定が可能
- MFAを設定可能

**2025年のベストプラクティス:**

AWSは、IAMユーザーを直接作成するのではなく、IDプロバイダー（IdP）を使用してフェデレーション経由でアクセスすることを推奨。既存の認証情報（Active Directory、Okta、Azure ADなど）を使用してAWSリソースにアクセス。

**使用場面:**

- ルートアカウント以外の管理者アクセス
- CLIやSDKからのプログラマティックアクセス（非推奨、ロールを推奨）
- フェデレーションが利用できない場合の代替

```bash
# IAMユーザーの作成（レガシー、推奨されない）
aws iam create-user --user-name john-doe

# パスワードポリシーの設定
aws iam update-account-password-policy \
    --minimum-password-length 14 \
    --require-symbols \
    --require-numbers \
    --require-uppercase-characters \
    --require-lowercase-characters \
    --allow-users-to-change-password \
    --max-password-age 90 \
    --password-reuse-prevention 5
```

### グループ（Groups）

複数のユーザーをまとめて管理するためのコレクション。

**特徴:**

- ポリシーをグループに適用
- ユーザーを複数のグループに所属可能
- 権限管理の簡素化

**使用場面:**

- 部門別の権限管理（開発チーム、運用チームなど）
- 役割別の権限管理（管理者、閲覧者など）
- プロジェクト別の権限管理

```bash
# IAMグループの作成
aws iam create-group --group-name Developers

# グループにユーザーを追加
aws iam add-user-to-group \
    --user-name john-doe \
    --group-name Developers

# グループにポリシーをアタッチ
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

### ロール（Roles）

一時的な権限を付与するためのIAMエンティティ。

**特徴:**

- 一時的な認証情報（セキュリティトークン）
- クロスアカウントアクセス
- AWSサービスへの権限委任

**2025年のベストプラクティス:**

AWSは、ワークロードが一時的な認証情報を持つIAMロールを使用してAWSにアクセスすることを要求。長期的なアクセスキーの使用を避ける。

**使用場面:**

- EC2インスタンスからのAWSサービスアクセス
- Lambda関数の実行
- クロスアカウントアクセス
- フェデレーション認証

```bash
# IAMロールの作成
aws iam create-role \
    --role-name EC2-S3-ReadOnly \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "ec2.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'

# ロールにポリシーをアタッチ
aws iam attach-role-policy \
    --role-name EC2-S3-ReadOnly \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# インスタンスプロファイルの作成と関連付け
aws iam create-instance-profile --instance-profile-name EC2-S3-Profile
aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-S3-Profile \
    --role-name EC2-S3-ReadOnly
```

### ポリシー（Policies）

権限を定義するJSON形式のドキュメント。

**ポリシーの種類:**

**1. アイデンティティベースポリシー（Identity-based policies）:**

ユーザー、グループ、ロールにアタッチ。

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ]
  }]
}
```

**2. リソースベースポリシー（Resource-based policies）:**

リソース（S3バケット、SQSキューなど）に直接アタッチ。

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123456789012:user/john-doe"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

**3. アクセス許可の境界（Permissions boundaries）:**

IAMエンティティが持つことができる最大権限を定義。

**4. サービスコントロールポリシー（SCPs）:**

AWS Organizations内のアカウント全体に適用される権限ガードレール。

**5. アクセス制御リスト（ACLs）:**

レガシーなアクセス制御メカニズム（S3など）。

**6. セッションポリシー（Session policies）:**

一時的な認証情報を取得する際に適用。

## IAMベストプラクティス（2025年版）

### 1. ルートアカウントの保護

ルートアカウントは最高権限を持つため、厳重に保護する必要がある。

**ベストプラクティス:**

- [ ] ルートアカウントでMFAを有効化
- [ ] ルートアカウントのアクセスキーを削除
- [ ] ルートアカウントは初期設定とアカウント管理のみに使用
- [ ] 日常的な管理作業にはIAMユーザーやロールを使用

```bash
# MFAデバイスの有効化確認
aws iam get-account-summary | grep "AccountMFAEnabled"
```

### 2. フェデレーション認証の使用

IAMユーザーを直接作成する代わりに、IDプロバイダー（IdP）を使用。

**メリット:**

- 既存の認証情報を活用
- 中央集権的なアクセス管理
- 一時的な認証情報の使用
- パスワード管理の簡素化

**フェデレーション方式:**

- SAML 2.0フェデレーション（Active Directory、Okta など）
- Web IDフェデレーション（Google、Facebook、Amazon など）
- AWS Single Sign-On（AWS SSO）

```bash
# SAML IDプロバイダーの作成
aws iam create-saml-provider \
    --saml-metadata-document file://metadata.xml \
    --name MyIdP
```

### 3. MFA（多要素認証）の必須化

すべてのユーザーと重要なロールにMFAを設定。

**MFAデバイスの種類:**

- 仮想MFAデバイス（Google Authenticator、Authyなど）
- ハードウェアMFAデバイス（YubiKey、Gemaltoなど）
- U2Fセキュリティキー

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
  }]
}
```

### 4. 最小権限の原則

必要最小限の権限のみを付与。

**アプローチ:**

- IAM Access Analyzerでアクセスパターンを分析
- CloudTrailログから実際の使用状況を確認
- 段階的に権限を追加（最初は狭く、必要に応じて拡大）

```bash
# IAM Access Analyzerの有効化
aws accessanalyzer create-analyzer \
    --analyzer-name my-analyzer \
    --type ACCOUNT

# アクセスログからポリシーを生成
aws accessanalyzer generate-finding-policy \
    --finding-id <finding-id> \
    --analyzer-arn <analyzer-arn>
```

### 5. 属性ベースのアクセス制御（ABAC）

ユーザー属性（部門、役職、チーム名など）に基づいて権限を付与。

**メリット:**

- スケーラブルな権限管理
- 自動化されたプロビジョニング
- ポリシー数の削減

**RBAC（ロールベース）とABACの組み合わせ:**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "arn:aws:s3:::${aws:PrincipalTag/Department}/*",
    "Condition": {
      "StringEquals": {
        "s3:ExistingObjectTag/Department": "${aws:PrincipalTag/Department}"
      }
    }
  }]
}
```

### 6. 定期的な権限レビュー

未使用の権限とユーザーを定期的に確認し、削除。

**レビュー項目:**

- 90日間使用されていない認証情報
- 未使用のIAMロールとポリシー
- 過剰な権限を持つエンティティ
- パブリックアクセスやクロスアカウントアクセス

```bash
# 認証情報レポートの生成
aws iam generate-credential-report
aws iam get-credential-report --output text --query Content | base64 -d

# 最終アクセス情報の確認
aws iam get-user --user-name john-doe \
  --query 'User.PasswordLastUsed'
```

### 7. AWS Organizationsでのガードレール設定

サービスコントロールポリシー（SCP）を使用して、アカウント全体の権限を制限。

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": [
      "ec2:RunInstances"
    ],
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "StringNotEquals": {
        "ec2:InstanceType": [
          "t2.micro",
          "t2.small",
          "t3.micro",
          "t3.small"
        ]
      }
    }
  }]
}
```

## 思考プロセス

### フェーズ1: IAM戦略の決定

**ステップ1: 認証戦略の選択**

組織の規模と要件に基づいて認証戦略を選択:

**小規模組織（〜10ユーザー）:**

- [ ] IAMユーザーとグループ（シンプル）
- [ ] MFA必須
- [ ] 定期的なパスワード変更

**中〜大規模組織（10+ユーザー）:**

- [ ] フェデレーション認証（推奨）
- [ ] AWS SSO
- [ ] 既存のIDプロバイダーと統合
- [ ] MFA必須

**エンタープライズ:**

- [ ] SAML 2.0フェデレーション
- [ ] マルチアカウント戦略（AWS Organizations）
- [ ] 属性ベースのアクセス制御（ABAC）
- [ ] ジャストインタイム（JIT）アクセス

**ステップ2: ロールベース vs 属性ベース**

**ロールベースアクセス制御（RBAC）:**

- 定義済みの役割（管理者、開発者、閲覧者など）
- シンプルで理解しやすい
- 役割の数が増えると管理が複雑化

**属性ベースアクセス制御（ABAC）:**

- ユーザー属性に基づく動的な権限付与
- スケーラブル
- 初期設定が複雑

**移行条件:**

- [ ] 認証戦略を決定した
- [ ] RBACとABACの使い分けを決定した
- [ ] IDプロバイダーを選択した（該当する場合）

### フェーズ2: IAMポリシー設計

**ステップ1: 最小権限の原則を適用**

必要な権限を特定し、段階的にアクセスを許可:

```bash
# ステップ1: 読み取り専用から開始
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": "arn:aws:s3:::my-bucket/*"
}

# ステップ2: 必要に応じて書き込み権限を追加
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::my-bucket/*"
}
```

**ステップ2: ポリシーの種類を選択**

**AWS管理ポリシー:**

- すぐに使える標準的な権限セット
- AWSが更新を管理
- カスタマイズ不可

```bash
# AWS管理ポリシーの例
arn:aws:iam::aws:policy/ReadOnlyAccess
arn:aws:iam::aws:policy/PowerUserAccess
arn:aws:iam::aws:policy/AdministratorAccess
```

**カスタマー管理ポリシー:**

- 組織固有の要件に対応
- 完全なカスタマイズが可能
- 自分で管理する必要がある

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:Describe*",
      "ec2:StartInstances",
      "ec2:StopInstances"
    ],
    "Resource": "*",
    "Condition": {
      "StringEquals": {
        "ec2:ResourceTag/Environment": "Development"
      }
    }
  }]
}
```

**インラインポリシー:**

- 特定のユーザー、グループ、ロールに直接アタッチ
- 一対一の関係
- 一般的には推奨されない

**ステップ3: 条件付きアクセスの実装**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*",
    "Condition": {
      "IpAddress": {
        "aws:SourceIp": ["192.0.2.0/24"]
      },
      "DateGreaterThan": {
        "aws:CurrentTime": "2025-01-01T00:00:00Z"
      },
      "DateLessThan": {
        "aws:CurrentTime": "2025-12-31T23:59:59Z"
      }
    }
  }]
}
```

**移行条件:**

- [ ] 必要な権限を特定した
- [ ] ポリシーの種類を選択した
- [ ] 条件付きアクセスを設計した
- [ ] ポリシーをテストした

### フェーズ3: ロールとフェデレーション設定

**ステップ1: サービスロールの作成**

EC2、Lambda、ECSなどのAWSサービス用のロール:

```bash
# Lambda実行ロールの作成
aws iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'

# 基本実行権限を付与
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

**ステップ2: クロスアカウントロールの設定**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::123456789012:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "unique-external-id"
      }
    }
  }]
}
```

**ステップ3: フェデレーションの設定**

**AWS SSOの設定:**

```bash
# AWS SSOの有効化（AWSコンソールから実施）
# 1. AWS Organizations を設定
# 2. AWS SSO を有効化
# 3. IDソースを設定（AWS SSO Directory、Active Directory、外部IdP）
# 4. 権限セットを作成
# 5. ユーザーとグループに権限を割り当て
```

**SAMLフェデレーションの設定:**

```bash
# SAML IDプロバイダーの作成
aws iam create-saml-provider \
    --saml-metadata-document file://metadata.xml \
    --name CorporateIdP

# フェデレーションロールの作成
aws iam create-role \
    --role-name Federated-Admin \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {
          "Federated": "arn:aws:iam::123456789012:saml-provider/CorporateIdP"
        },
        "Action": "sts:AssumeRoleWithSAML",
        "Condition": {
          "StringEquals": {
            "SAML:aud": "https://signin.aws.amazon.com/saml"
          }
        }
      }]
    }'
```

**移行条件:**

- [ ] サービスロールを作成した
- [ ] クロスアカウントアクセスを設定した（該当する場合）
- [ ] フェデレーションを設定した（該当する場合）
- [ ] ロールのアクセスをテストした

### フェーズ4: セキュリティ強化

**ステップ1: MFAの強制**

すべての人的アクセスにMFAを要求:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyAllExceptListedIfNoMFA",
    "Effect": "Deny",
    "NotAction": [
      "iam:CreateVirtualMFADevice",
      "iam:EnableMFADevice",
      "iam:GetUser",
      "iam:ListMFADevices",
      "iam:ListVirtualMFADevices",
      "iam:ResyncMFADevice",
      "sts:GetSessionToken"
    ],
    "Resource": "*",
    "Condition": {
      "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
  }]
}
```

**ステップ2: アクセスキーのローテーション**

```bash
# アクセスキーの作成
aws iam create-access-key --user-name john-doe

# 古いアクセスキーの無効化
aws iam update-access-key \
    --user-name john-doe \
    --access-key-id AKIAIOSFODNN7EXAMPLE \
    --status Inactive

# アクセスキーの削除
aws iam delete-access-key \
    --user-name john-doe \
    --access-key-id AKIAIOSFODNN7EXAMPLE
```

**ステップ3: 権限境界の設定**

IAMエンティティが持つことができる最大権限を制限:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:*",
      "ec2:*",
      "rds:*"
    ],
    "Resource": "*"
  }]
}
```

```bash
# 権限境界を設定
aws iam put-user-permissions-boundary \
    --user-name john-doe \
    --permissions-boundary arn:aws:iam::123456789012:policy/MaxPermissions
```

**移行条件:**

- [ ] MFAを強制した
- [ ] アクセスキーのローテーション計画を立てた
- [ ] 権限境界を設定した（該当する場合）
- [ ] セキュリティ設定をテストした

### フェーズ5: 監視と監査

**ステップ1: CloudTrailによるログ記録**

```bash
# CloudTrailの有効化
aws cloudtrail create-trail \
    --name my-trail \
    --s3-bucket-name my-cloudtrail-bucket

aws cloudtrail start-logging --name my-trail
```

**ステップ2: IAM Access Analyzerの有効化**

```bash
# Access Analyzerの作成
aws accessanalyzer create-analyzer \
    --analyzer-name account-analyzer \
    --type ACCOUNT

# 検出結果の確認
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/account-analyzer
```

**ステップ3: 定期的な認証情報レポート**

```bash
# 認証情報レポートの生成と取得
aws iam generate-credential-report
aws iam get-credential-report > credentials.csv

# 90日以上使用されていない認証情報を確認
# csvファイルを分析して、古い認証情報を特定
```

**移行条件:**

- [ ] CloudTrailを有効化した
- [ ] Access Analyzerを有効化した
- [ ] 定期的なレビュープロセスを確立した
- [ ] アラートを設定した

## 判断のポイント

### 認証方式の選択

| 方式 | 適用場面 | メリット | デメリット |
|-----|---------|---------|----------|
| IAMユーザー | 小規模、レガシー | シンプル | スケールしない |
| フェデレーション | 中〜大規模 | 中央管理、既存IdP活用 | 初期設定が複雑 |
| AWS SSO | エンタープライズ | 統合管理、使いやすい | AWS Organizationsが必要 |

### ポリシータイプの選択

| タイプ | 使用場面 | メリット | デメリット |
|-------|---------|---------|----------|
| AWS管理 | 標準的な権限 | すぐ使える、AWSが更新 | カスタマイズ不可 |
| カスタマー管理 | 組織固有の要件 | 柔軟性が高い | 管理が必要 |
| インライン | 一対一の関係 | シンプル | 再利用不可 |

## よくある落とし穴

1. **ルートアカウントの日常的な使用**
   - ❌ ルートアカウントで作業
   - ✅ IAMユーザーまたはフェデレーション認証を使用

2. **過剰な権限付与**
   - ❌ 最初からAdministratorAccessを付与
   - ✅ 最小権限から始めて、必要に応じて拡大

3. **長期的なアクセスキーの使用**
   - ❌ アクセスキーを永久に使用
   - ✅ IAMロールと一時的な認証情報を使用

4. **MFAの未設定**
   - ❌ パスワードのみで保護
   - ✅ すべての人的アクセスにMFAを必須化

5. **未使用の認証情報の放置**
   - ❌ 退職者のアカウントを放置
   - ✅ 定期的に認証情報をレビューし、削除

6. **ポリシーの複雑化**
   - ❌ 巨大で複雑なポリシー
   - ✅ シンプルで理解しやすいポリシーに分割

## 検証ポイント

### セキュリティ基準

- [ ] ルートアカウントでMFAを有効化した
- [ ] ルートアカウントのアクセスキーを削除した
- [ ] すべてのユーザーにMFAを設定した
- [ ] パスワードポリシーを設定した
- [ ] 最小権限の原則を適用した

### 認証・認可

- [ ] 適切な認証方式を選択した
- [ ] フェデレーションを設定した（該当する場合）
- [ ] ロールベースアクセスを実装した
- [ ] ポリシーをテストした

### 監視・監査

- [ ] CloudTrailを有効化した
- [ ] Access Analyzerを有効化した
- [ ] 定期的な認証情報レビューを設定した
- [ ] アラートを設定した

## 他スキルとの連携

### iam + organizations

IAMとマルチアカウント管理の組み合わせ:

1. iamでアクセス制御を設計
2. organizationsでSCPを設定
3. アカウント全体のガードレールを実装

### iam + cloudtrail

IAMとログ監査の組み合わせ:

1. iamで権限を設定
2. cloudtrailでアクセスログを記録
3. セキュリティ監査を実施

### iam + well-architected

IAMとセキュリティベストプラクティスの組み合わせ:

1. well-architectedでセキュリティ原則を理解
2. iamで具体的な実装を行う
3. セキュアなアーキテクチャを構築

## リソース

### 公式ドキュメント

- [AWS IAM Documentation](https://docs.aws.amazon.com/iam/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)

### セキュリティガイド

- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- [AWS Organizations SCPs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)

### ツール

- [AWS IAM Policy Simulator](https://policysim.aws.amazon.com/)
- [IAM Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)
