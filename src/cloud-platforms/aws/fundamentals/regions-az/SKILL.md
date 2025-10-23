---
name: "AWS リージョンとアベイラビリティゾーン"
description: "AWSグローバルインフラストラクチャ（リージョン、AZ、エッジロケーション）の理解と設計。リージョン選択、マルチAZ構成、高可用性設計、レイテンシ最適化に関する思考プロセスを提供"
---

# AWS リージョンとアベイラビリティゾーン

## このスキルを使う場面

- リージョンの選択
- マルチAZ構成の設計
- 高可用性アーキテクチャの構築
- グローバル展開の計画
- ディザスタリカバリ戦略の立案
- レイテンシ最適化

## AWSグローバルインフラストラクチャとは

AWSは世界中に分散された物理インフラストラクチャを提供し、ユーザーはアプリケーションとデータを最適な場所に配置できる。このインフラストラクチャは、リージョン、アベイラビリティゾーン（AZ）、エッジロケーションの3つの主要コンポーネントで構成される。

### グローバルインフラストラクチャの階層構造

```
AWS グローバルインフラストラクチャ
├── リージョン (Regions)
│   ├── アベイラビリティゾーン 1 (AZ-1)
│   │   ├── データセンター 1
│   │   └── データセンター 2
│   ├── アベイラビリティゾーン 2 (AZ-2)
│   │   ├── データセンター 3
│   │   └── データセンター 4
│   └── アベイラビリティゾーン 3 (AZ-3)
│       ├── データセンター 5
│       └── データセンター 6
└── エッジロケーション (Edge Locations)
    ├── CloudFront CDN
    ├── Route 53 DNS
    └── AWS Global Accelerator
```

## リージョン（Regions）

リージョンは、AWSがデータセンターを運用する地理的なエリア。各リージョンは完全に独立しており、物理的に分離されている。

### リージョンの特徴

**完全な独立性:**

- 各リージョンは他のリージョンから完全に分離
- 障害の影響が他リージョンに波及しない
- リージョン間のデータ転送は明示的に実行する必要がある

**複数のAZで構成:**

- 各リージョンは最低3つのAZを持つ（2025年時点）
- 高可用性とフォールトトレランスを実現

**独立したサービス:**

- 各リージョンで独立したサービスエンドポイント
- リージョンごとに異なるサービス提供状況

### 主要リージョン（2025年時点）

**北米:**

- `us-east-1` - バージニア北部（最も古いリージョン、最も多くのサービス）
- `us-east-2` - オハイオ
- `us-west-1` - カリフォルニア北部
- `us-west-2` - オレゴン

**アジア太平洋:**

- `ap-northeast-1` - 東京
- `ap-northeast-2` - ソウル
- `ap-northeast-3` - 大阪（ローカルリージョン）
- `ap-southeast-1` - シンガポール
- `ap-south-1` - ムンバイ

**ヨーロッパ:**

- `eu-west-1` - アイルランド
- `eu-central-1` - フランクフルト
- `eu-north-1` - ストックホルム

**その他:**

- `sa-east-1` - サンパウロ
- `me-south-1` - バーレーン
- `af-south-1` - ケープタウン

### リージョン選択の要因

**1. 地理的な近接性（レイテンシ）:**

ユーザーに最も近いリージョンを選択することで、ネットワークレイテンシを最小化。

- エンドユーザーの地理的位置
- APIレスポンスタイムの要件
- リアルタイム処理の必要性

**2. データ主権と規制要件:**

特定の国や地域の法規制により、データの保存場所が制限される場合がある。

- GDPR（欧州一般データ保護規則）
- 個人情報保護法（日本）
- HIPAA（米国医療保険の相互運用性と説明責任に関する法律）
- 金融規制

**3. サービスの可用性:**

すべてのAWSサービスがすべてのリージョンで利用できるわけではない。

- 新しいサービスは通常、`us-east-1`で最初にリリース
- 特定のサービスが必要な場合、そのサービスが利用可能なリージョンを選択
- リージョンごとのサービス可用性を事前に確認

**4. コスト:**

リージョンによって料金が異なる。

- `us-east-1`が通常最も安価
- アジア太平洋リージョンは比較的高価
- データ転送料金もリージョン間で異なる

**5. ディザスタリカバリ（DR）:**

複数リージョンを使用することで、リージョン全体の障害に対応。

- プライマリリージョンとセカンダリリージョンの選択
- リージョン間のデータレプリケーション
- フェイルオーバー戦略

## アベイラビリティゾーン（Availability Zones, AZ）

アベイラビリティゾーンは、リージョン内の1つ以上の独立したデータセンター群。各AZは物理的に分離され、冗長な電源、ネットワーキング、接続性を持つ。

### AZの特徴

**物理的な分離:**

- 各AZは物理的に異なる場所に配置
- 洪水、火災、竜巻などの自然災害の影響を最小化
- 一般的に数km〜数十km離れている

**独立した電源とネットワーク:**

- 冗長な電源供給
- 独立した冷却システム
- 独立したネットワーク接続

**低レイテンシの相互接続:**

- AZ間は専用の高速ネットワークで接続
- 通常1〜2ミリ秒のレイテンシ
- 同期レプリケーションに適した速度

**複数のデータセンター:**

- 各AZは1つ以上のデータセンターで構成
- 単一データセンターの障害に対して耐性がある

### AZの命名規則

各AZは、リージョンコードに続いて小文字のアルファベットで識別される:

```
# 例：東京リージョン（ap-northeast-1）
ap-northeast-1a
ap-northeast-1c
ap-northeast-1d

# 注意：AZ IDとAZ名は異なる
# AZ名（ap-northeast-1a）はアカウントごとにランダムに割り当てられる
# AZ ID（apne1-az1）は物理的なAZを一意に識別
```

### マルチAZ構成の重要性

単一AZ障害から保護し、高可用性を実現するため、複数のAZにリソースを分散させることが重要。

**マルチAZ構成のメリット:**

- 単一AZ障害時の自動フェイルオーバー
- 高可用性とフォールトトレランス
- メンテナンス中のサービス継続
- RPO（Recovery Point Objective）とRTO（Recovery Time Objective）の最小化

## エッジロケーション（Edge Locations）

エッジロケーションは、CDN（Content Delivery Network）サービスであるCloudFrontや、DNS
サービスであるRoute 53で使用されるキャッシュサーバーの配置場所。

### エッジロケーションの特徴

**グローバル配置:**

- 世界中に400以上のエッジロケーション（2025年時点）
- リージョンよりもはるかに多くの場所に配置
- ユーザーに最も近い場所からコンテンツを配信

**使用されるサービス:**

- Amazon CloudFront（CDN）
- Amazon Route 53（DNS）
- AWS Global Accelerator（ネットワーク最適化）
- AWS WAF（Webアプリケーションファイアウォール）

**キャッシング:**

- 静的コンテンツ（画像、CSS、JavaScriptなど）をキャッシュ
- オリジンサーバーへの負荷を軽減
- レイテンシの大幅な削減

## 思考プロセス

### フェーズ1: リージョン選択

**ステップ1: 要件の整理**

リージョン選択に影響する要件を整理する:

- [ ] エンドユーザーの地理的位置
- [ ] データ主権・規制要件
- [ ] 必要なAWSサービス
- [ ] 予算制約
- [ ] レイテンシ要件
- [ ] ディザスタリカバリ要件

**ステップ2: 候補リージョンの選定**

要件に基づいて候補リージョンを選定:

**レイテンシ優先の場合:**

```bash
# エンドユーザーの位置に基づいて選択
# 日本のユーザー → ap-northeast-1（東京）
# 米国のユーザー → us-east-1 or us-west-2
# 欧州のユーザー → eu-west-1 or eu-central-1

# レイテンシ測定
curl -o /dev/null -s -w '%{time_total}\n' \
  https://s3.ap-northeast-1.amazonaws.com/
```

**コスト優先の場合:**

```bash
# AWS Simple Monthly Calculatorで各リージョンの料金を比較
# 一般的に us-east-1 が最も安価
# 次に us-west-2, eu-west-1
```

**データ主権優先の場合:**

- GDPR対応 → EU内のリージョン（eu-west-1, eu-central-1など）
- 日本の個人情報 → ap-northeast-1（東京）
- 中国 → cn-north-1, cn-northwest-1（特別な要件あり）

**ステップ3: サービス可用性の確認**

```bash
# 必要なサービスがリージョンで利用可能か確認
aws ec2 describe-regions --all-regions

# 特定のサービスの可用性を確認
# https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/
```

**移行条件:**

- [ ] 候補リージョンを3つ以下に絞り込んだ
- [ ] サービス可用性を確認した
- [ ] コスト試算を実施した
- [ ] レイテンシを測定した

### フェーズ2: マルチAZ設計

**ステップ1: 高可用性要件の定義**

- [ ] 目標SLA（Service Level Agreement）
- [ ] 許容ダウンタイム
- [ ] RPO（Recovery Point Objective）
- [ ] RTO（Recovery Time Objective）

**ステップ2: マルチAZ配置戦略**

**最小構成（2 AZ）:**

コスト重視だが、高可用性も必要な場合:

```yaml
# 2 AZ構成の例
Resources:
  # AZ-1のリソース
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24

  # AZ-2のリソース
  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
```

**推奨構成（3 AZ）:**

本番環境での標準構成:

```yaml
# 3 AZ構成の例
Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24

  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24

  Subnet3:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: !Select [2, !GetAZs '']
      CidrBlock: 10.0.3.0/24
```

**ステップ3: ロードバランサーの配置**

マルチAZ構成では、Application Load Balancer（ALB）やNetwork Load Balancer（NLB）を使用してトラフィックを分散:

```bash
# ALBの作成（マルチAZ）
aws elbv2 create-load-balancer \
    --name my-alb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-12345678 \
    --scheme internet-facing \
    --type application
```

**ステップ4: データベースのマルチAZ配置**

**RDSマルチAZ:**

```bash
# RDS Multi-AZの有効化
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --multi-az \
    --allocated-storage 100 \
    --master-username admin \
    --master-user-password password123
```

**移行条件:**

- [ ] 使用するAZ数を決定した（最低2、推奨3）
- [ ] ロードバランサーを配置した
- [ ] データベースのマルチAZ設定を完了した
- [ ] ヘルスチェックを設定した

### フェーズ3: マルチリージョン設計（オプション）

**ステップ1: マルチリージョンの必要性を判断**

マルチリージョンが必要な場合:

- [ ] グローバルなユーザーベース
- [ ] リージョン全体の障害に対する保護
- [ ] 非常に厳しいRTO/RPO要件
- [ ] データレジデンシー要件（複数の地域）

**ステップ2: マルチリージョン戦略の選択**

**アクティブ-パッシブ構成:**

- プライマリリージョンで本番稼働
- セカンダリリージョンはDR用途
- コストを抑えつつ、DR対応

```bash
# Route 53でフェイルオーバールーティング
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
      "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "example.com",
          "Type": "A",
          "SetIdentifier": "Primary",
          "Failover": "PRIMARY",
          "AliasTarget": {
            "HostedZoneId": "Z32O12XQLNTSW2",
            "DNSName": "primary-alb.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }]
    }'
```

**アクティブ-アクティブ構成:**

- 複数のリージョンで同時に本番稼働
- 最高の可用性とパフォーマンス
- 運用コストが高い

```bash
# Route 53で地理的ルーティング
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch '{
      "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "example.com",
          "Type": "A",
          "SetIdentifier": "Asia",
          "GeoLocation": {"ContinentCode": "AS"},
          "AliasTarget": {
            "HostedZoneId": "Z2M4EHUR26P7ZW",
            "DNSName": "asia-alb.ap-northeast-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }]
    }'
```

**ステップ3: クロスリージョンレプリケーション**

**S3クロスリージョンレプリケーション:**

```json
{
  "Role": "arn:aws:iam::123456789012:role/s3-replication-role",
  "Rules": [{
    "Status": "Enabled",
    "Priority": 1,
    "DeleteMarkerReplication": { "Status": "Enabled" },
    "Filter" : { "Prefix": ""},
    "Destination": {
      "Bucket": "arn:aws:s3:::destination-bucket",
      "ReplicationTime": {
        "Status": "Enabled",
        "Time": { "Minutes": 15 }
      },
      "Metrics": {
        "Status": "Enabled",
        "EventThreshold": { "Minutes": 15 }
      }
    }
  }]
}
```

**RDSクロスリージョンリードレプリカ:**

```bash
# クロスリージョンリードレプリカの作成
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica \
    --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:mydb \
    --region ap-northeast-1
```

**移行条件:**

- [ ] マルチリージョン戦略を決定した
- [ ] Route 53でDNSルーティングを設定した
- [ ] クロスリージョンレプリケーションを設定した
- [ ] フェイルオーバーテストを実施した

### フェーズ4: エッジロケーション活用

**ステップ1: CloudFrontディストリビューションの作成**

```bash
# CloudFrontディストリビューションの作成
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "my-distribution",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "myS3Origin",
      "DomainName": "mybucket.s3.amazonaws.com",
      "S3OriginConfig": {
        "OriginAccessIdentity": ""
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "myS3Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "MinTTL": 0
  },
  "Enabled": true
}'
```

**ステップ2: レイテンシ測定**

```bash
# CloudFront経由のレイテンシ測定
curl -o /dev/null -s -w 'Total: %{time_total}s\n' \
  https://d111111abcdef8.cloudfront.net/image.jpg

# オリジンへの直接アクセスのレイテンシ
curl -o /dev/null -s -w 'Total: %{time_total}s\n' \
  https://mybucket.s3.amazonaws.com/image.jpg
```

**移行条件:**

- [ ] CloudFrontディストリビューションを作成した
- [ ] キャッシュ動作を設定した
- [ ] レイテンシ改善を確認した
- [ ] コスト削減を確認した

## 判断のポイント

### リージョン選択の判断基準

| 要因 | 重要度 | 考慮事項 |
|-----|-------|---------|
| レイテンシ | 高 | ユーザーに近いリージョンを選択 |
| データ主権 | 高 | 法規制要件を満たすリージョン |
| サービス可用性 | 中 | 必要なサービスが利用可能か |
| コスト | 中 | リージョンによる価格差 |
| DR要件 | 高 | セカンダリリージョンの選択 |

### AZ数の選択

| 構成 | 可用性 | コスト | 使用場面 |
|-----|-------|-------|---------|
| 1 AZ | 低 | 低 | 開発・テスト環境のみ |
| 2 AZ | 中 | 中 | 小規模本番環境 |
| 3+ AZ | 高 | 高 | 本番環境（推奨） |

### マルチリージョン戦略の選択

| 戦略 | 可用性 | コスト | 複雑性 | 使用場面 |
|-----|-------|-------|-------|---------|
| シングルリージョン | 中 | 低 | 低 | 単一地域のサービス |
| アクティブ-パッシブ | 高 | 中 | 中 | DR要件がある場合 |
| アクティブ-アクティブ | 最高 | 高 | 高 | グローバルサービス |

## よくある落とし穴

1. **シングルAZ構成**
   - ❌ 本番環境でシングルAZ
   - ✅ 最低でも2 AZ、推奨は3 AZ

2. **AZ名とAZ IDの混同**
   - ❌ AZ名（ap-northeast-1a）が物理的なAZと一致すると仮定
   - ✅ AZ ID（apne1-az1）を使用して物理的なAZを特定

3. **クロスAZデータ転送コストの見落とし**
   - ❌ AZ間のデータ転送は無料と仮定
   - ✅ クロスAZデータ転送には料金が発生することを考慮

4. **すべてのサービスがマルチAZ対応と仮定**
   - ❌ すべてのサービスが自動的にマルチAZ
   - ✅ サービスごとにマルチAZ設定を確認・有効化

5. **リージョン間レプリケーションの遅延を考慮しない**
   - ❌ リージョン間レプリケーションが即座に完了すると仮定
   - ✅ レプリケーション遅延を考慮したRPO/RTO設計

6. **グローバルサービスとリージョナルサービスの混同**
   - ❌ すべてのサービスがグローバルと仮定
   - ✅ サービスがグローバルかリージョナルかを確認

## 高可用性設計のベストプラクティス

### EC2インスタンスのマルチAZ配置

```bash
# Auto Scalingグループでマルチ AZ配置
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name my-asg \
    --launch-template LaunchTemplateName=my-template \
    --min-size 3 \
    --max-size 9 \
    --desired-capacity 3 \
    --vpc-zone-identifier "subnet-az1,subnet-az2,subnet-az3" \
    --target-group-arns arn:aws:elasticloadbalancing:region:account-id:targetgroup/my-targets/12345
```

### データベースの高可用性

**RDS Multi-AZ:**

- 自動フェイルオーバー（60〜120秒）
- 同期レプリケーション
- 自動バックアップ

**Aurora Multi-Master:**

- 複数のライトノード
- リージョン内の高可用性
- サブ秒のフェイルオーバー

### ストレージの冗長性

**S3:**

- 自動的に最低3つのAZにレプリケート
- 99.999999999%（11 9's）の耐久性
- 99.99%の可用性

**EFS:**

- 自動的に複数のAZに分散
- リージョナルサービス
- マルチAZ構成が標準

## 検証ポイント

### リージョン選択

- [ ] エンドユーザーの位置を考慮した
- [ ] データ主権要件を確認した
- [ ] 必要なサービスが利用可能か確認した
- [ ] コスト試算を実施した
- [ ] レイテンシをテストした

### マルチAZ設計

- [ ] 最低2つのAZを使用する設計にした
- [ ] ロードバランサーをマルチAZ配置した
- [ ] データベースのマルチAZ設定を有効化した
- [ ] ヘルスチェックを設定した
- [ ] 自動フェイルオーバーをテストした

### マルチリージョン設計（該当する場合）

- [ ] セカンダリリージョンを選択した
- [ ] クロスリージョンレプリケーションを設定した
- [ ] Route 53でDNSフェイルオーバーを設定した
- [ ] フェイルオーバーテストを実施した

### エッジロケーション活用（該当する場合）

- [ ] CloudFrontディストリビューションを作成した
- [ ] キャッシュ戦略を定義した
- [ ] レイテンシ改善を測定した

## 他スキルとの連携

### regions-az + vpc

リージョン・AZ選択とネットワーク設計の組み合わせ:

1. regions-azでリージョンとAZ配置を決定
2. vpcで各AZにサブネットを配置
3. マルチAZ VPC構成を実現

### regions-az + high-availability

リージョン・AZ知識と高可用性設計の組み合わせ:

1. regions-azでマルチAZ構成を設計
2. high-availabilityで自動フェイルオーバーを実装
3. 高可用性アーキテクチャを構築

### regions-az + cost-optimization

リージョン選択とコスト最適化の組み合わせ:

1. regions-azでコスト効率の良いリージョンを選択
2. cost-optimizationでリザーブドインスタンスを活用
3. コスト最適化されたマルチAZ構成を実現

## リソース

### 公式ドキュメント

- [AWS Global Infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/)
- [Regions and Availability Zones](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/)
- [AWS Regional Services](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)

### ベストプラクティス

- [AWS Well-Architected Framework - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Multi-Region Application Architecture](https://aws.amazon.com/solutions/implementations/multi-region-application-architecture/)
