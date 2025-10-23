---
name: "incident-response"
description: >
  インシデント対応計画の策定と実施を支援します。検知・分析・封じ込め・根絶・回復・教訓化の
  インシデント対応ライフサイクル、CSIRT運用、報告フロー設計、プレイブック作成など、
  セキュリティインシデントの効果的な管理に使用します。
  キーワード - インシデント対応、CSIRT、プレイブック、封じ込め、根絶、事後分析。
version: 1.0.0
---

# インシデント対応計画スキル

## 目的

このスキルは、セキュリティインシデントの効果的な対応と管理を支援します。
NIST、SANS等のフレームワークに基づき、検知から復旧、教訓化までの
一連のプロセスを実装するための実践的知識を含みます。

## インシデント対応ライフサイクル

### NISTインシデント対応フレームワーク

**1. 準備（Preparation）**
- チーム編成
- ツール整備
- プレイブック作成
- トレーニング

**2. 検知と分析（Detection & Analysis）**
- アラート監視
- 初期トリアージ
- 影響範囲特定
- 深度調査

**3. 封じ込め、根絶、復旧（Containment, Eradication & Recovery）**
- 短期封じ込め
- 長期封じ込め
- 脅威の根絶
- システム復旧

**4. 事後活動（Post-Incident Activity）**
- 教訓抽出
- プロセス改善
- 報告書作成

## CSIRT構築

### 組織構造

```
インシデント対応マネージャー
├─ Tier 1 (トリアージ)
├─ Tier 2 (分析)
├─ Tier 3 (専門家)
└─ フォレンジック担当
```

### 役割と責任

**インシデントマネージャー:**
- 全体統制
- 意思決定
- エスカレーション

**アナリスト:**
- ログ分析
- マルウェア解析
- 影響評価

**フォレンジック:**
- 証拠保全
- 詳細調査
- 法的対応

**コミュニケーター:**
- 内部報告
- 外部通知
- メディア対応

## インシデント分類

### 重要度レベル

**P1 - 致命的（Critical）:**
- 基幹システム停止
- 大規模データ漏洩
- ランサムウェア感染
- 対応時間: 即座（15分以内）

**P2 - 高（High）:**
- 重要システムへの侵害
- マルウェア検出
- 不正アクセス
- 対応時間: 1時間以内

**P3 - 中（Medium）:**
- 限定的なセキュリティ違反
- フィッシング成功
- 対応時間: 4時間以内

**P4 - 低（Low）:**
- ポリシー違反
- スキャン活動検出
- 対応時間: 24時間以内

### インシデントタイプ

- マルウェア感染
- 不正アクセス
- データ漏洩
- DoS/DDoS攻撃
- フィッシング
- 内部不正
- 物理セキュリティ侵害

## プレイブック

### ランサムウェア対応プレイブック

```markdown
# ランサムウェアインシデント対応プレイブック

## 1. 検知

**指標:**
- ファイル暗号化
- 身代金要求メッセージ
- .encrypted, .locked等の拡張子

**初期対応（15分以内）:**
1. 影響範囲の特定
2. 感染システムのネットワーク隔離
3. インシデントマネージャーへ報告
4. P1インシデント宣言

## 2. 封じ込め

**短期封じ込め（1時間以内）:**
- [ ] 感染システムをネットワークから切断
- [ ] バックアップシステムを隔離
- [ ] 関連アカウントの無効化
- [ ] ファイル共有の停止

**長期封じ込め（4時間以内）:**
- [ ] 感染範囲の完全特定
- [ ] セグメンテーション強化
- [ ] 監視強化
- [ ] パッチ適用

## 3. 根絶

**根絶手順（24時間以内）:**
- [ ] マルウェア特定と削除
- [ ] システムクリーンインストール
- [ ] 永続化メカニズムの除去
- [ ] 脆弱性の修正

## 4. 復旧

**復旧手順:**
- [ ] バックアップからのリストア
- [ ] システム機能検証
- [ ] セキュリティ監視強化
- [ ] 段階的サービス再開

## 5. 教訓

**事後活動:**
- [ ] タイムライン作成
- [ ] 根本原因分析
- [ ] 改善事項リスト
- [ ] プレイブック更新

## チェックリスト

**即時:**
- [ ] インシデント報告
- [ ] 初期封じ込め
- [ ] 証拠保全
- [ ] ステークホルダー通知

**短期:**
- [ ] フォレンジック調査
- [ ] 完全な封じ込め
- [ ] コミュニケーション計画

**長期:**
- [ ] システム復旧
- [ ] セキュリティ強化
- [ ] 教訓の文書化
```

### データ漏洩対応プレイブック

```markdown
# データ漏洩インシデント対応

## 1. 検知と確認

**検証事項:**
- [ ] 漏洩の事実確認
- [ ] 漏洩データの種類
- [ ] 漏洩データ量
- [ ] 漏洩経路

## 2. 法的要件の確認

**GDPR（72時間ルール）:**
- 個人データ漏洩の場合
- 監督機関への通知
- 本人への通知（高リスク時）

**日本（個人情報保護法）:**
- 要配慮個人情報の漏洩
- 個人情報保護委員会への報告
- 本人への通知

## 3. 封じ込め

- [ ] 漏洩経路の遮断
- [ ] 認証情報のリセット
- [ ] アクセス制御の強化
- [ ] 監視の強化

## 4. 影響評価

**評価事項:**
- 影響を受ける個人数
- データの機密性
- 悪用の可能性
- ビジネスインパクト

## 5. 通知

**内部:**
- 経営層
- 法務部
- 広報部
- 該当部門

**外部:**
- 監督機関（必要に応じて）
- 影響を受ける個人
- パートナー/顧客
- メディア（必要に応じて）

## 6. 復旧と改善

- [ ] セキュリティ対策の強化
- [ ] 再発防止策
- [ ] ポリシー見直し
- [ ] トレーニング実施
```

## インシデント報告

### 初期報告テンプレート

```
件名: [P1/P2/P3/P4] インシデント報告 - [概要]

1. インシデント概要
   - 発生日時: 2024-01-15 14:30 JST
   - 検知日時: 2024-01-15 14:45 JST
   - インシデント種別: ランサムウェア
   - 重要度: P1

2. 影響範囲
   - 影響システム: Fileサーバー3台
   - 影響ユーザー: 約200名
   - 業務影響: ファイル共有停止

3. 現在の状況
   - 感染システムを隔離完了
   - バックアップ確認中
   - フォレンジック調査準備中

4. 次のアクション
   - システムクリーンインストール
   - バックアップからの復旧
   - 脆弱性修正

5. 推定復旧時間
   - 24時間以内

報告者: セキュリティチーム 山田太郎
次回更新: 4時間後
```

### 最終報告テンプレート

```markdown
# インシデント最終報告書

## エグゼクティブサマリー
[簡潔な概要、ビジネスインパクト、対応結果]

## 1. インシデント詳細

### 1.1 基本情報
- インシデント ID: INC-2024-001
- インシデント種別: ランサムウェア
- 重要度: P1
- 発生日時: 2024-01-15 14:30
- 検知日時: 2024-01-15 14:45
- 復旧完了日時: 2024-01-17 10:00

### 1.2 タイムライン
| 日時 | イベント | 対応者 |
|------|---------|--------|
| 14:30 | 感染開始 | - |
| 14:45 | アラート検知 | SOC |
| 15:00 | 封じ込め完了 | IR チーム |
| 18:00 | 根本原因特定 | フォレンジック |

## 2. 影響評価
- 影響システム: 3台
- データ損失: なし（バックアップから復旧）
- ダウンタイム: 43.5時間
- 推定コスト: $X

## 3. 根本原因
- 脆弱性: CVE-2024-XXXXX
- 初期侵入: フィッシングメール
- 攻撃チェーン: [詳細]

## 4. 対応アクション
[実施した対応の詳細]

## 5. 教訓
### うまくいったこと
- 迅速な検知と隔離
- バックアップが有効だった

### 改善が必要なこと
- パッチ適用の遅れ
- セキュリティ意識向上必要

## 6. 改善計画
1. パッチ管理プロセスの見直し
2. セキュリティトレーニング強化
3. バックアップ戦略の改善
4. EDRの導入検討

## 7. 添付資料
- フォレンジック報告書
- IoC リスト
- タイムライン詳細
```

## エスカレーション

### エスカレーションマトリックス

| 重要度 | 通知先 | 通知タイミング |
|-------|--------|--------------|
| P1 | CEO, CISO, CTO | 即座 |
| P2 | CISO, CTO | 1時間以内 |
| P3 | セキュリティマネージャー | 4時間以内 |
| P4 | チームリーダー | 24時間以内 |

### 外部連絡

**法執行機関:**
- サイバー犯罪の場合
- データ窃取・破壊

**監督機関:**
- 個人データ漏洩（GDPR 72時間）
- 重大なコンプライアンス違反

**JPCERT/CC:**
- 重大なサイバー攻撃
- 脅威情報共有

## ツールとリソース

### 必須ツール

**通信:**
- 専用チャットルーム
- 緊急連絡先リスト
- ビデオ会議

**技術:**
- SIEM
- EDR
- フォレンジックツール
- Sandboxこのスキルは防御的セキュリティ分析と教育目的にのみ使用してください。

## このスキルを使用する場合

- クラウドセキュリティの設計や実装を求めた場合
- AWS、Azure、GCPのセキュリティ設定が必要な場合
- クラウドコンプライアンス（CIS、NIST）への対応が必要な場合
- クラウドセキュリティツール（CSPM、CWPP）の導入を検討している場合
- ゼロトラストアーキテクチャをクラウドで実装したい場合

## クラウドセキュリティの基礎

### 責任共有モデル

**クラウドプロバイダーの責任:**
- 物理セキュリティ
- ハードウェア
- ネットワークインフラ
- ハイパーバイザー

**顧客の責任:**
- データ
- アクセス管理
- アプリケーション
- OS（IaaSの場合）

## AWS セキュリティ

### IAM（Identity and Access Management）

**ベストプラクティス:**

```json
// 最小権限ポリシー例
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

**MFA強制:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### AWS Security Services

**GuardDuty（脅威検出）:**
```bash
# 有効化
aws guardduty create-detector --enable

# 検出結果取得
aws guardduty list-findings --detector-id <detector-id>
```

**SecurityHub（統合セキュリティ管理）:**
```bash
# 有効化
aws securityhub enable-security-hub

# CIS Benchmark有効化
aws securityhub batch-enable-standards \
  --standards-subscription-requests StandardsArn=arn:aws:securityhub:us-east-1::standards/cis-aws-foundations-benchmark/v/1.2.0
```

**CloudTrail（監査ログ）:**
```bash
# トレイル作成
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-bucket \
  --is-multi-region-trail \
  --enable-log-file-validation

# ロギング開始
aws cloudtrail start-logging --name my-trail
```

### S3 セキュリティ

**バケットポリシー:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

**パブリックアクセスブロック:**
```bash
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

## Azure セキュリティ

### Azure AD とRBAC

**カスタムロール:**
```json
{
  "Name": "Read Only Security Admin",
  "IsCustom": true,
  "Description": "Can read security settings",
  "Actions": [
    "Microsoft.Security/*/read",
    "Microsoft.Network/*/read"
  ],
  "NotActions": [],
  "AssignableScopes": [
    "/subscriptions/{subscription-id}"
  ]
}
```

**Conditional Access:**
```
ポリシー: すべての管理者にMFA要求
条件:
  - ユーザー: すべての管理者
  - アプリ: すべてのクラウドアプリ
  - 場所: 任意
アクセス制御:
  - 多要素認証を要求する
```

### Azure Security Center

**Azure Defender有効化:**
```powershell
# Azure Defender for Servers
Set-AzSecurityPricing -Name "VirtualMachines" -PricingTier "Standard"

# Azure Defender for Storage
Set-AzSecurityPricing -Name "StorageAccounts" -PricingTier "Standard"
```

### Key Vault

**シークレット管理:**
```bash
# Key Vault作成
az keyvault create \
  --name my-keyvault \
  --resource-group my-rg \
  --location eastus \
  --enable-soft-delete \
  --enable-purge-protection

# シークレット追加
az keyvault secret set \
  --vault-name my-keyvault \
  --name db-password \
  --value "SecureP@ssw0rd"
```

## GCP セキュリティ

### IAM

**サービスアカウント:**
```bash
# サービスアカウント作成
gcloud iam service-accounts create my-sa \
  --display-name "My Service Account"

# 役割付与
gcloud projects add-iam-policy-binding my-project \
  --member "serviceAccount:my-sa@my-project.iam.gserviceaccount.com" \
  --role "roles/storage.objectViewer"
```

### Security Command Center

**有効化:**
```bash
# セキュリティヘルスアナリティクス有効化
gcloud scc settings services enable \
  --organization=ORGANIZATION_ID \
  --service=SECURITY_HEALTH_ANALYTICS
```

## コンテナセキュリティ

### Kubernetes セキュリティ

**Pod Security Policy:**
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'secret'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

**Network Policy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

### イメージスキャン

**Trivy:**
```bash
# コンテナイメージスキャン
trivy image nginx:latest

# 深刻度でフィルタ
trivy image --severity HIGH,CRITICAL nginx:latest
```

## クラウドセキュリティツール

### CSPM（Cloud Security Posture Management）

**主要ツール:**
- Prisma Cloud (Palo Alto)
- CloudGuard (Check Point)
- AWS Security Hub
- Azure Security Center
- Google SCC

**チェック項目:**
- 設定ミス検出
- CIS Benchmark準拠
- コンプライアンス監視
- リスクスコアリング

### CWPP（Cloud Workload Protection Platform）

**機能:**
- ランタイム保護
- 脆弱性管理
- コンプライアンス
- 脅威検出

## IaC セキュリティ

### Terraform セキュリティ

**セキュアな設定:**
```hcl
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  public_access_block {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }

  logging {
    target_bucket = "log-bucket"
    target_prefix = "s3-logs/"
  }
}
```

**IaCスキャン:**
```bash
# Checkov
checkov -d /path/to/terraform

# tfsec
tfsec /path/to/terraform

# Terrascan
terrascan scan -t terraform
```

## ゼロトラストアーキテクチャ

### BeyondCorp モデル

**原則:**
1. デバイス/ユーザー認証
2. コンテキストベースアクセス
3. 暗号化通信
4. 最小権限
5. 継続的検証

**実装:**
- Identity-Aware Proxy (IAP)
- Device Trust
- BinaryAuthorization
- VPC Service Controls

## コンプライアンス

### CIS Benchmarks

**AWS CIS Benchmark主要項目:**
- 1.1 ルートアカウントMFA
- 1.2 ルートアカウント使用禁止
- 2.1 CloudTrail有効化
- 2.2 S3バケット暗号化
- 3.1 VPC Flow Logs有効化
- 4.1 セキュリティグループ制限

### NIST準拠

**CSF カテゴリマッピング:**
- ID: Asset Management, Risk Assessment
- PR: Data Security, Access Control
- DE: Continuous Monitoring, Detection Processes
- RS: Response Planning, Communications
- RC: Recovery Planning, Improvements

## ベストプラクティス

1. **最小権限原則**
   - 必要最小限のアクセス
   - 定期的なレビュー

2. **多層防御**
   - ネットワーク層
   - アプリケーション層
   - データ層

3. **暗号化**
   - 保存時暗号化
   - 通信時暗号化
   - 鍵管理（KMS）

4. **監視とロギング**
   - すべてのAPIコール記録
   - リアルタイムアラート
   - ログの集中管理

5. **自動化**
   - IaCでの構成管理
   - 自動スキャン
   - 自動修復

## 参考リソース

- AWS Well-Architected Framework - Security Pillar
- Azure Security Benchmark
- Google Cloud Security Best Practices
- CIS Cloud Benchmarks

## 注意事項

- 定期的なセキュリティレビュー
- コスト最適化とのバランス
- マルチクラウド戦略の考慮
- ベンダーロックインリスク
