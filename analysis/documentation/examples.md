# ドキュメント作成: 実装例集

このドキュメントでは、ドキュメント作成スキルで説明されている各種ドキュメントの具体的なテンプレートと例を示します。

## 目次

- [README の例](#readmeの例)
- [API ドキュメントの例](#apiドキュメントの例)
- [アーキテクチャドキュメントの例](#アーキテクチャドキュメントの例)
- [チュートリアルの例](#チュートリアルの例)
- [トラブルシューティングガイドの例](#トラブルシューティングガイドの例)
- [コード例のベストプラクティス](#コード例のベストプラクティス)

## README の例

### 基本テンプレート

```markdown
# プロジェクト名

簡潔な説明（1-2 文）。このプロジェクトが何をするか、誰のためのものか。

## 特徴

- 主要な機能 1
- 主要な機能 2
- 主要な機能 3

## クイックスタート

最も基本的な使い方を 3-5 ステップで:

1. インストール: `npm install myproject`
2. 設定ファイル作成: `myproject init`
3. 実行: `myproject start`

## インストール

### 前提条件

- Node.js 16 以上
- npm 7 以上

### インストール手順

\`\`\`bash
npm install myproject
\`\`\`

## 使い方

### 基本的な使い方

\`\`\`javascript
const myproject = require('myproject');

const result = myproject.process({
  input: 'data',
  options: { verbose: true }
});

console.log(result);
\`\`\`

### 設定

設定ファイル `config.json` の例:

\`\`\`json
{
  "port": 3000,
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
\`\`\`

## ドキュメント

詳細なドキュメントは [docs/](docs/) を参照してください:

- [API リファレンス](docs/api.md)
- [設定ガイド](docs/configuration.md)
- [チュートリアル](docs/tutorial.md)

## コントリビューション

コントリビューションを歓迎します！

1. Fork このリポジトリ
2. Feature ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

## サポート

- バグ報告: [Issues](https://github.com/user/project/issues)
- 質問: [Discussions](https://github.com/user/project/discussions)
- メール: support@example.com
```

### 実際の例: データ処理ライブラリの README

```markdown
# DataProcessor

高速かつ柔軟なデータ処理ライブラリ。CSV、JSON、XML などの形式に対応し、
大規模データセットを効率的に処理できます。

## 特徴

- 📊 複数のデータ形式に対応（CSV、JSON、XML、Parquet）
- ⚡ ストリーミング処理で大規模データも高速処理
- 🔧 プラグイン機構で独自の処理を追加可能
- 🧪 型安全な API（TypeScript 完全サポート）

## クイックスタート

\`\`\`bash
# インストール
npm install dataprocessor

# 基本的な使用例
npx dataprocessor process input.csv --output output.json
\`\`\`

## インストール

### 前提条件

- Node.js 18 以上
- メモリ: 最低 2GB（大規模データ処理には 8GB 以上推奨）

### npm でインストール

\`\`\`bash
npm install dataprocessor
\`\`\`

### yarn でインストール

\`\`\`bash
yarn add dataprocessor
\`\`\`

## 使い方

### 基本的な使い方

\`\`\`javascript
const { DataProcessor } = require('dataprocessor');

const processor = new DataProcessor();

// CSV を読み込んで JSON に変換
processor
  .read('input.csv')
  .transform(row => ({
    ...row,
    timestamp: new Date(row.date).toISOString()
  }))
  .write('output.json');
\`\`\`

### フィルタリング

\`\`\`javascript
processor
  .read('sales.csv')
  .filter(row => row.amount > 1000)
  .write('large-sales.json');
\`\`\`

### 集計

\`\`\`javascript
const stats = await processor
  .read('data.csv')
  .aggregate({
    totalSales: row => row.amount,
    avgPrice: { field: 'price', fn: 'average' },
    count: { fn: 'count' }
  });

console.log(stats);
// { totalSales: 15000, avgPrice: 49.99, count: 300 }
\`\`\`

## ドキュメント

- [📖 完全ドキュメント](https://dataprocessor.dev/docs)
- [🎓 チュートリアル](https://dataprocessor.dev/tutorial)
- [📚 API リファレンス](https://dataprocessor.dev/api)
- [🔌 プラグイン開発ガイド](https://dataprocessor.dev/plugins)

## 例

examples/ ディレクトリに様々な使用例があります:

- [基本的な CSV 処理](examples/basic-csv.js)
- [大規模データのストリーミング処理](examples/streaming.js)
- [複数ファイルの結合](examples/merge.js)
- [カスタム変換の作成](examples/custom-transform.js)

## パフォーマンス

10GB の CSV ファイル（1000 万行）の処理:

- 読み込み: 約 30 秒
- 変換・書き込み: 約 45 秒
- メモリ使用量: 約 200MB（ストリーミング処理）

## トラブルシューティング

### メモリ不足エラー

大規模データを処理する際にメモリ不足エラーが発生する場合:

\`\`\`javascript
// ストリーミングモードを使用
processor.read('large-file.csv', { streaming: true })
\`\`\`

### 文字エンコーディングの問題

日本語などが文字化けする場合:

\`\`\`javascript
processor.read('data.csv', { encoding: 'utf-8' })
\`\`\`

詳細は [トラブルシューティングガイド](docs/troubleshooting.md) を参照。

## コントリビューション

バグ報告や機能要望は [Issues](https://github.com/user/dataprocessor/issues) へ。

プルリクエストを歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 作者

DataProcessor チーム (team@dataprocessor.dev)
```

## API ドキュメントの例

### REST API ドキュメントテンプレート

```markdown
# API リファレンス

## 認証

すべての API リクエストには認証が必要です。

\`\`\`http
Authorization: Bearer YOUR_API_KEY
\`\`\`

API キーは [ダッシュボード](https://example.com/dashboard) で取得できます。

## エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/users` | ユーザー一覧を取得 |
| GET | `/api/users/:id` | 特定ユーザーを取得 |
| POST | `/api/users` | 新規ユーザーを作成 |
| PUT | `/api/users/:id` | ユーザー情報を更新 |
| DELETE | `/api/users/:id` | ユーザーを削除 |

## ユーザー一覧の取得

ユーザー一覧を取得します。

### リクエスト

\`\`\`http
GET /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer YOUR_API_KEY
\`\`\`

### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `page` | integer | ❌ | ページ番号（1始まり） | 1 |
| `limit` | integer | ❌ | 1ページあたりの件数（最大100） | 20 |
| `sort` | string | ❌ | ソート順（`created_at`, `-created_at`） | `-created_at` |
| `status` | string | ❌ | ステータスでフィルタ（`active`, `inactive`） | - |

### レスポンス例

\`\`\`json
{
  "data": [
    {
      "id": "user_123",
      "name": "山田太郎",
      "email": "yamada@example.com",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "user_124",
      "name": "佐藤花子",
      "email": "sato@example.com",
      "status": "active",
      "created_at": "2024-01-16T14:20:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}
\`\`\`

### レスポンスフィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `data` | array | ユーザーオブジェクトの配列 |
| `data[].id` | string | ユーザー ID |
| `data[].name` | string | ユーザー名 |
| `data[].email` | string | メールアドレス |
| `data[].status` | string | ステータス（`active` または `inactive`） |
| `data[].created_at` | string | 作成日時（ISO 8601 形式） |
| `pagination` | object | ページネーション情報 |

### ステータスコード

| コード | 説明 |
|-------|------|
| 200 | 成功 |
| 401 | 認証エラー（API キーが無効） |
| 403 | 権限エラー（アクセス権限なし） |
| 429 | レート制限エラー（リクエスト過多） |
| 500 | サーバーエラー |

## ユーザーの作成

新しいユーザーを作成します。

### リクエスト

\`\`\`http
POST /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "name": "田中一郎",
  "email": "tanaka@example.com",
  "password": "secure_password_123"
}
\`\`\`

### リクエストボディ

| フィールド | 型 | 必須 | 説明 | 制約 |
|-----------|-----|------|------|------|
| `name` | string | ✅ | ユーザー名 | 2-50文字 |
| `email` | string | ✅ | メールアドレス | 有効なメールアドレス形式 |
| `password` | string | ✅ | パスワード | 8文字以上、英数字含む |
| `role` | string | ❌ | ロール | `user`, `admin`（デフォルト: `user`） |

### レスポンス例（成功）

\`\`\`json
{
  "id": "user_125",
  "name": "田中一郎",
  "email": "tanaka@example.com",
  "status": "active",
  "role": "user",
  "created_at": "2024-01-20T09:15:00Z"
}
\`\`\`

### レスポンス例（エラー）

\`\`\`json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が無効です",
    "details": [
      {
        "field": "email",
        "message": "このメールアドレスは既に使用されています"
      }
    ]
  }
}
\`\`\`

### ステータスコード

| コード | 説明 |
|-------|------|
| 201 | 作成成功 |
| 400 | バリデーションエラー |
| 401 | 認証エラー |
| 409 | 競合エラー（メールアドレスが既に存在） |
| 500 | サーバーエラー |

## エラーコード一覧

| エラーコード | 説明 | 対処法 |
|-------------|------|--------|
| `INVALID_API_KEY` | API キーが無効 | 正しい API キーを使用してください |
| `VALIDATION_ERROR` | 入力値が無効 | エラー詳細を確認して修正してください |
| `RESOURCE_NOT_FOUND` | リソースが見つからない | ID を確認してください |
| `RATE_LIMIT_EXCEEDED` | レート制限超過 | しばらく待ってから再試行してください |
| `INTERNAL_ERROR` | サーバーエラー | サポートに問い合わせてください |

## レート制限

| プラン | リクエスト数 | 期間 |
|-------|-------------|------|
| Free | 100 | 1時間 |
| Basic | 1,000 | 1時間 |
| Pro | 10,000 | 1時間 |
| Enterprise | 無制限 | - |

レート制限に達した場合、429 ステータスコードが返されます。
レスポンスヘッダーで制限情報を確認できます:

\`\`\`http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 50
X-RateLimit-Reset: 1642675200
\`\`\`

## コード例

### JavaScript (fetch)

\`\`\`javascript
const response = await fetch('https://api.example.com/api/users', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data);
\`\`\`

### Python (requests)

\`\`\`python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/api/users', headers=headers)
data = response.json()
print(data)
\`\`\`

### cURL

\`\`\`bash
curl -X GET 'https://api.example.com/api/users' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json'
\`\`\`
```

## アーキテクチャドキュメントの例

```markdown
# システムアーキテクチャ

## 概要

本システムは、大規模な E コマースプラットフォームのバックエンドです。
マイクロサービスアーキテクチャを採用し、高可用性とスケーラビリティを実現しています。

### 主要な要件

- 秒間 10,000 リクエストの処理
- 99.9% の可用性
- 平均レスポンスタイム 200ms 以下
- 100 万ユーザーのサポート

## システム全体図

```text
┌─────────────┐
│   Client    │
│ (Web/Mobile)│
└──────┬──────┘
       │
       v
┌──────────────────────────────────────────┐
│         Load Balancer (ALB)              │
└──────┬────────────────────────────┬──────┘
       │                            │
       v                            v
┌─────────────┐              ┌─────────────┐
│  API Gateway│              │  API Gateway│
└──────┬──────┘              └──────┬──────┘
       │                            │
       └────────────┬───────────────┘
                    │
    ┌───────────────┼───────────────┬─────────────┐
    │               │               │             │
    v               v               v             v
┌────────┐    ┌──────────┐    ┌─────────┐   ┌────────┐
│ User   │    │ Product  │    │ Order   │   │Payment │
│Service │    │ Service  │    │ Service │   │Service │
└───┬────┘    └─────┬────┘    └────┬────┘   └───┬────┘
    │               │              │            │
    v               v              v            v
┌────────┐    ┌──────────┐    ┌─────────┐   ┌────────┐
│User DB │    │Product DB│    │Order DB │   │Payment │
│(RDS)   │    │ (RDS)    │    │ (RDS)   │   │Gateway │
└────────┘    └──────────┘    └─────────┘   └────────┘

       │               │              │
       └───────────────┼──────────────┘
                       │
                       v
              ┌────────────────┐
              │  Redis Cache   │
              └────────────────┘
                       │
                       v
              ┌────────────────┐
              │  Event Bus     │
              │  (SNS/SQS)     │
              └────────────────┘
```

## コンポーネント詳細

### API Gateway

**責任:**

- リクエストのルーティング
- 認証・認可
- レート制限
- ロギング・モニタリング

**技術:**

- AWS API Gateway
- Lambda Authorizer（JWT 認証）

**スケール:**

- Auto Scaling（CPU 70% で増減）
- 最小: 2 インスタンス
- 最大: 20 インスタンス

### User Service

**責任:**

- ユーザー登録・認証
- プロフィール管理
- セッション管理

**技術:**

- Node.js 18 + Express
- PostgreSQL 14（RDS）
- Redis（セッション）

**API エンドポイント:**

- `POST /users` - ユーザー登録
- `POST /auth/login` - ログイン
- `GET /users/:id` - ユーザー情報取得
- `PUT /users/:id` - ユーザー情報更新

**データベーススキーマ:**

\`\`\`sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
\`\`\`

### Product Service

**責任:**

- 商品情報管理
- 在庫管理
- 検索機能

**技術:**

- Python 3.11 + FastAPI
- PostgreSQL 14（RDS）
- Elasticsearch（検索）

**パフォーマンス最適化:**

- 商品情報を Redis にキャッシュ（TTL: 1時間）
- 検索は Elasticsearch を使用（全文検索）
- データベースには Read Replica を使用

### Order Service

**責任:**

- 注文の作成・管理
- 注文履歴
- 在庫予約

**技術:**

- Java 17 + Spring Boot
- PostgreSQL 14（RDS）
- SQS（非同期処理）

**トランザクション処理:**

注文作成は以下の手順で行われます:

1. 在庫チェック（Product Service）
2. 在庫予約
3. 注文レコード作成
4. 決済処理（Payment Service）
5. 在庫確定

失敗時はロールバック（Saga パターン）

### Payment Service

**責任:**

- 決済処理
- 決済履歴
- 返金処理

**技術:**

- Node.js 18 + Express
- Stripe API（決済ゲートウェイ）
- PostgreSQL 14（RDS）

**セキュリティ:**

- PCI DSS 準拠
- カード情報は保存しない（Stripe に委託）
- すべての通信は TLS 1.3

## データフロー

### 注文フロー

1. **クライアント → API Gateway**
   - ユーザーが商品をカートに追加
   - JWT トークンで認証

2. **API Gateway → Order Service**
   - 注文作成リクエスト
   - ユーザー ID、商品 ID、数量

3. **Order Service → Product Service**
   - 在庫確認
   - REST API 呼び出し

4. **Order Service → Payment Service**
   - 決済処理
   - REST API 呼び出し

5. **Order Service → Event Bus**
   - 注文完了イベント発行
   - 他サービスに通知

6. **Event Bus → Email Service**
   - 注文確認メール送信
   - 非同期処理

## 技術選択とトレードオフ

### マイクロサービス vs モノリシック

**決定:** マイクロサービスアーキテクチャ

**理由:**

- 各サービスを独立してスケール可能
- チームごとに異なる技術スタックを選択可能
- 障害の影響範囲を限定

**トレードオフ:**

- メリット: スケーラビリティ、独立デプロイ、技術的柔軟性
- デメリット: 運用の複雑さ増加、分散トランザクションの難しさ、ネットワークレイテンシ

**前提:** チームが 5 つ以上、各サービスのスケール要件が異なる

**再検討条件:** チームが 3 つ以下になったら、モノリシックへの統合を検討

### PostgreSQL vs DynamoDB

**決定:** PostgreSQL（RDS）

**理由:**

- 複雑なクエリが必要（JOIN、トランザクション）
- ACID 特性が重要（注文データの整合性）
- チームの PostgreSQL 経験豊富

**トレードオフ:**

- メリット: 強い整合性、複雑なクエリ、トランザクション
- デメリット: スケーラビリティに限界、運用コスト高

**前提:** データの整合性がパフォーマンスより重要

**再検討条件:** スケールが Read Replica でも不足したら DynamoDB を検討

## スケーラビリティ設計

### 水平スケール

すべてのサービスはステートレスで設計され、水平スケール可能:

- Auto Scaling Group による自動スケール
- ロードバランサーで負荷分散
- セッション情報は Redis に保存

### データベースのスケール

- Read Replica 3 台（読み取り負荷分散）
- Write はプライマリのみ
- 将来的にはシャーディングも検討

### キャッシュ戦略

Redis を使用した階層的キャッシュ:

- L1: アプリケーションメモリ（数秒）
- L2: Redis（数分〜数時間）
- L3: データベース

## 可用性・信頼性設計

### 冗長化

- すべてのコンポーネントを複数 AZ に配置
- 最低 2 インスタンス（本番環境）
- データベースは Multi-AZ

### 障害対策

- ヘルスチェック（30秒間隔）
- 自動フェイルオーバー
- サーキットブレーカー（連続 3 回失敗で遮断）
- リトライ（最大 3 回、Exponential Backoff）

### モニタリング

- CloudWatch でメトリクス収集
- アラート設定（レスポンスタイム、エラー率）
- 分散トレーシング（X-Ray）
- ログ集約（CloudWatch Logs）

## セキュリティ

### 認証・認可

- JWT トークンベース認証
- API Gateway で検証
- トークン有効期限: 1時間
- リフレッシュトークン: 30日

### ネットワークセキュリティ

- VPC による論理的分離
- セキュリティグループで最小権限
- プライベートサブネットに配置
- NAT Gateway 経由で外部通信

### データ保護

- 転送中: TLS 1.3
- 保存時: RDS 暗号化、S3 暗号化
- 機密情報: AWS Secrets Manager

## デプロイ

### CI/CD パイプライン

1. コードプッシュ → GitHub
2. GitHub Actions でテスト実行
3. Docker イメージビルド → ECR
4. ECS でローリングデプロイ

### デプロイ戦略

- Blue/Green デプロイ
- カナリアリリース（10% → 50% → 100%）
- 問題発生時は即座にロールバック

## 今後の課題

- [ ] GraphQL API の検討
- [ ] サーバーレス化（Lambda）の検討
- [ ] データベースシャーディングの実装
- [ ] マルチリージョン対応

## 参考資料

プロジェクトに応じて、以下のような参考資料へのリンクを追加できます：

```markdown
- [システム要件定義書](requirements.md)
- [API 仕様書](api-spec.md)
- [運用手順書](operations.md)
- [障害対応手順書](incident-response.md)
```

## チュートリアルの例

```markdown
# チュートリアル: 簡単な TODO アプリを作る

## このチュートリアルで学べること

このチュートリアルでは、シンプルな TODO アプリを作成します。
完成後、以下ができるようになります:

- ✅ REST API の作成
- ✅ データベースとの連携
- ✅ CRUD 操作の実装
- ✅ テストの書き方

## 前提条件

このチュートリアルを始める前に、以下が必要です:

- Node.js 18 以上がインストールされている
- npm 9 以上がインストールされている
- 基本的な JavaScript の知識（変数、関数、オブジェクト）
- ターミナルの基本操作ができる

**確認方法:**

\`\`\`bash
node --version  # v18.0.0 以上であることを確認
npm --version   # v9.0.0 以上であることを確認
\`\`\`

## 所要時間

約 30 分

## ステップ 1: プロジェクトのセットアップ

### 1.1 プロジェクトディレクトリの作成

新しいディレクトリを作成し、移動します:

\`\`\`bash
mkdir todo-app
cd todo-app
\`\`\`

### 1.2 package.json の初期化

npm プロジェクトを初期化します:

\`\`\`bash
npm init -y
\`\`\`

**期待される結果:**
`package.json` ファイルが作成されます。

### 1.3 必要なパッケージのインストール

以下のパッケージをインストールします:

\`\`\`bash
npm install express sqlite3
npm install --save-dev nodemon
\`\`\`

- `express`: Web フレームワーク
- `sqlite3`: データベース
- `nodemon`: 開発時の自動リロード

**期待される結果:**
`node_modules/` ディレクトリと `package-lock.json` が作成されます。

### ✅ チェックポイント

\`\`\`bash
ls
\`\`\`

以下のファイルが表示されるはずです:
- `package.json`
- `package-lock.json`
- `node_modules/` (ディレクトリ)

## ステップ 2: データベースのセットアップ

### 2.1 データベースファイルの作成

`db.js` ファイルを作成します:

\`\`\`javascript
// db.js
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./todos.db');

// テーブル作成
db.serialize(() => {
  db.run(\`
    CREATE TABLE IF NOT EXISTS todos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      completed INTEGER DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  \`);
});

module.exports = db;
\`\`\`

**このコードの説明:**

- SQLite データベースを作成
- `todos` テーブルを作成（存在しない場合）
- `id`, `title`, `completed`, `created_at` の4つのカラム

### ✅ チェックポイント

ファイルを作成後、以下のコマンドで構文エラーがないか確認:

\`\`\`bash
node db.js
\`\`\`

エラーが表示されなければ成功です。

## ステップ 3: Express サーバーのセットアップ

### 3.1 サーバーファイルの作成

`server.js` ファイルを作成します:

\`\`\`javascript
// server.js
const express = require('express');
const db = require('./db');

const app = express();
const PORT = 3000;

// JSON ボディパーサー
app.use(express.json());

// ルート
app.get('/', (req, res) => {
  res.json({ message: 'TODO API is running' });
});

// サーバー起動
app.listen(PORT, () => {
  console.log(\`Server is running on http://localhost:\${PORT}\`);
});
\`\`\`

### 3.2 サーバーの起動

\`\`\`bash
node server.js
\`\`\`

**期待される出力:**

\`\`\`
Server is running on http://localhost:3000
\`\`\`

### 3.3 動作確認

別のターミナルを開いて、以下のコマンドを実行:

\`\`\`bash
curl http://localhost:3000
\`\`\`

**期待される出力:**

\`\`\`json
{"message":"TODO API is running"}
\`\`\`

### ✅ チェックポイント

ブラウザで `http://localhost:3000` にアクセスして、JSON が表示されることを確認してください。

## ステップ 4: CRUD 操作の実装

### 4.1 TODO 一覧の取得（READ）

`server.js` に以下を追加:

\`\`\`javascript
// TODO 一覧を取得
app.get('/todos', (req, res) => {
  db.all('SELECT * FROM todos ORDER BY created_at DESC', [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ todos: rows });
  });
});
\`\`\`

**動作確認:**

\`\`\`bash
curl http://localhost:3000/todos
\`\`\`

**期待される出力:**

\`\`\`json
{"todos":[]}
\`\`\`

（まだ TODO がないため、空配列）

### 4.2 TODO の作成（CREATE）

`server.js` に以下を追加:

\`\`\`javascript
// TODO を作成
app.post('/todos', (req, res) => {
  const { title } = req.body;

  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }

  db.run('INSERT INTO todos (title) VALUES (?)', [title], function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(201).json({
      id: this.lastID,
      title: title,
      completed: 0
    });
  });
});
\`\`\`

**動作確認:**

\`\`\`bash
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries"}'
\`\`\`

**期待される出力:**

\`\`\`json
{"id":1,"title":"Buy groceries","completed":0}
\`\`\`

### 4.3 TODO の更新（UPDATE）

`server.js` に以下を追加:

\`\`\`javascript
// TODO を更新（完了状態を切り替え）
app.put('/todos/:id', (req, res) => {
  const { id } = req.params;
  const { completed } = req.body;

  db.run(
    'UPDATE todos SET completed = ? WHERE id = ?',
    [completed ? 1 : 0, id],
    function(err) {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      if (this.changes === 0) {
        return res.status(404).json({ error: 'TODO not found' });
      }
      res.json({ message: 'TODO updated', changes: this.changes });
    }
  );
});
\`\`\`

**動作確認:**

\`\`\`bash
curl -X PUT http://localhost:3000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
\`\`\`

### 4.4 TODO の削除（DELETE）

`server.js` に以下を追加:

\`\`\`javascript
// TODO を削除
app.delete('/todos/:id', (req, res) => {
  const { id } = req.params;

  db.run('DELETE FROM todos WHERE id = ?', [id], function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (this.changes === 0) {
      return res.status(404).json({ error: 'TODO not found' });
    }
    res.json({ message: 'TODO deleted' });
  });
});
\`\`\`

**動作確認:**

\`\`\`bash
curl -X DELETE http://localhost:3000/todos/1
\`\`\`

### ✅ チェックポイント - すべての操作を試す

以下のコマンドを順番に実行して、すべての CRUD 操作が動作することを確認:

\`\`\`bash
# 作成
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Task 1"}'

curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Task 2"}'

# 一覧取得
curl http://localhost:3000/todos

# 更新
curl -X PUT http://localhost:3000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# 削除
curl -X DELETE http://localhost:3000/todos/2

# 確認
curl http://localhost:3000/todos
\`\`\`

## ステップ 5: 開発体験の改善

### 5.1 nodemon の設定

`package.json` の `scripts` に以下を追加:

\`\`\`json
"scripts": {
  "start": "node server.js",
  "dev": "nodemon server.js"
}
\`\`\`

### 5.2 開発モードで起動

\`\`\`bash
npm run dev
\`\`\`

これで、ファイルを変更すると自動的にサーバーが再起動されます。

## 完成！

おめでとうございます！ TODO アプリが完成しました。

### できるようになったこと

- ✅ Express で REST API を作成
- ✅ SQLite データベースと連携
- ✅ CRUD 操作（作成、読み取り、更新、削除）の実装
- ✅ エラーハンドリング
- ✅ 開発環境のセットアップ

## 次のステップ

さらに機能を追加してみましょう:

1. **バリデーション強化**
   - タイトルの長さ制限
   - 特殊文字のチェック

2. **フィルタリング機能**
   - 完了済みの TODO だけ表示
   - 未完了の TODO だけ表示

3. **フロントエンド追加**
   - HTML + JavaScript で UI を作成
   - React や Vue.js を使う

4. **テストの追加**
   - Jest でユニットテスト
   - Supertest で API テスト

## トラブルシューティング

### ポートが既に使用されている

**エラー:**

\`\`\`
Error: listen EADDRINUSE: address already in use :::3000
\`\`\`

**対処法:**

別のポートを使用するか、既存のプロセスを終了してください:

\`\`\`bash
# macOS/Linux
lsof -ti:3000 | xargs kill

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
\`\`\`

### データベースファイルが作成されない

**対処法:**

権限を確認してください:

\`\`\`bash
ls -la todos.db
\`\`\`

権限がない場合:

\`\`\`bash
chmod 644 todos.db
\`\`\`

## 参考資料

- [Express 公式ドキュメント](https://expressjs.com/)
- [SQLite3 ドキュメント](https://github.com/TryGhost/node-sqlite3)
- [REST API 設計ガイド](https://restfulapi.net/)
```

## トラブルシューティングガイドの例

```markdown
# トラブルシューティングガイド

## よくある問題と解決方法

このガイドでは、よく発生する問題とその解決方法を説明します。

## 目次

- [インストール関連](#インストール関連)
- [起動・実行関連](#起動実行関連)
- [パフォーマンス関連](#パフォーマンス関連)
- [エラーメッセージ別対処法](#エラーメッセージ別対処法)

## インストール関連

### 問題: npm install が失敗する

**エラーメッセージ:**

\`\`\`
npm ERR! code EACCES
npm ERR! syscall access
npm ERR! path /usr/local/lib/node_modules
\`\`\`

**原因:** 権限不足

**解決方法:**

1. **推奨: nvm を使用**

   \`\`\`bash
   # nvm のインストール
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

   # Node.js のインストール
   nvm install 18
   nvm use 18
   \`\`\`

2. **代替: sudo を使用（非推奨）**

   \`\`\`bash
   sudo npm install -g mypackage
   \`\`\`

### 問題: バージョンが古い

**症状:** 機能が動作しない、エラーが発生する

**確認方法:**

\`\`\`bash
node --version
npm --version
\`\`\`

**解決方法:**

\`\`\`bash
# Node.js のアップデート
nvm install 18
nvm use 18

# npm のアップデート
npm install -g npm@latest
\`\`\`

## 起動・実行関連

### 問題: サーバーが起動しない

**エラーメッセージ:**

\`\`\`
Error: listen EADDRINUSE: address already in use :::3000
\`\`\`

**原因:** ポートが既に使用されている

**解決方法:**

1. **使用中のプロセスを確認**

   \`\`\`bash
   # macOS/Linux
   lsof -i :3000

   # Windows
   netstat -ano | findstr :3000
   \`\`\`

2. **プロセスを終了**

   \`\`\`bash
   # macOS/Linux
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   \`\`\`

3. **別のポートを使用**

   \`\`\`bash
   PORT=3001 npm start
   \`\`\`

### 問題: 環境変数が読み込まれない

**症状:** データベース接続エラー、API キーエラー

**確認方法:**

\`\`\`bash
echo $DATABASE_URL
\`\`\`

**解決方法:**

1. **`.env` ファイルの確認**

   \`\`\`bash
   cat .env
   \`\`\`

   正しい形式:

   \`\`\`
   DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
   API_KEY=your_api_key_here
   \`\`\`

2. **dotenv の読み込み確認**

   \`\`\`javascript
   require('dotenv').config();
   console.log(process.env.DATABASE_URL);  // デバッグ用
   \`\`\`

## パフォーマンス関連

### 問題: レスポンスが遅い（5秒以上）

**症状:** API リクエストに時間がかかる

**診断方法:**

1. **ネットワーク遅延の確認**

   \`\`\`bash
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/api/users
   \`\`\`

   `curl-format.txt` の内容:

   \`\`\`
   time_total: %{time_total}s
   time_connect: %{time_connect}s
   time_starttransfer: %{time_starttransfer}s
   \`\`\`

2. **データベースクエリの確認**

   \`\`\`javascript
   // ログ出力を追加
   console.time('query');
   const results = await db.query('SELECT * FROM users');
   console.timeEnd('query');
   \`\`\`

**解決方法:**

1. **インデックスの追加**

   \`\`\`sql
   CREATE INDEX idx_users_email ON users(email);
   \`\`\`

2. **キャッシュの導入**

   \`\`\`javascript
   const cache = require('memory-cache');

   app.get('/users', async (req, res) => {
     const cached = cache.get('users');
     if (cached) {
       return res.json(cached);
     }

     const users = await db.query('SELECT * FROM users');
     cache.put('users', users, 60000);  // 60秒キャッシュ
     res.json(users);
   });
   \`\`\`

3. **N+1 問題の解決**

   ❌ **悪い例（N+1）:**

   \`\`\`javascript
   const users = await User.findAll();
   for (const user of users) {
     user.posts = await Post.findAll({ where: { userId: user.id } });
   }
   \`\`\`

   ✅ **良い例（JOIN）:**

   \`\`\`javascript
   const users = await User.findAll({
     include: [Post]
   });
   \`\`\`

### 問題: メモリ不足

**エラーメッセージ:**

\`\`\`
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
\`\`\`

**解決方法:**

1. **メモリ上限を増やす**

   \`\`\`bash
   node --max-old-space-size=4096 server.js
   \`\`\`

2. **メモリリークの確認**

   \`\`\`javascript
   // メモリ使用量をモニタリング
   setInterval(() => {
     const used = process.memoryUsage();
     console.log(\`Memory: \${Math.round(used.heapUsed / 1024 / 1024)} MB\`);
   }, 5000);
   \`\`\`

3. **ストリーミング処理を使用**

   ❌ **悪い例（すべてメモリに読み込む）:**

   \`\`\`javascript
   const data = fs.readFileSync('large-file.json');
   \`\`\`

   ✅ **良い例（ストリーミング）:**

   \`\`\`javascript
   const stream = fs.createReadStream('large-file.json');
   stream.pipe(parser).pipe(processor);
   \`\`\`

## エラーメッセージ別対処法

### ECONNREFUSED

**エラーメッセージ:**

\`\`\`
Error: connect ECONNREFUSED 127.0.0.1:5432
\`\`\`

**原因:** データベースサーバーが起動していない

**解決方法:**

\`\`\`bash
# PostgreSQL の起動
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
net start postgresql-x64-14
\`\`\`

### ENOTFOUND

**エラーメッセージ:**

\`\`\`
Error: getaddrinfo ENOTFOUND api.example.com
\`\`\`

**原因:** DNS 解決失敗、ネットワーク接続問題

**解決方法:**

1. **ネットワーク接続の確認**

   \`\`\`bash
   ping api.example.com
   \`\`\`

2. **DNS キャッシュのクリア**

   \`\`\`bash
   # macOS
   sudo dscacheutil -flushcache

   # Windows
   ipconfig /flushdns
   \`\`\`

3. **URL の確認**

   \`\`\`javascript
   // 環境変数が正しく設定されているか確認
   console.log(process.env.API_URL);
   \`\`\`

### Syntax Error

**エラーメッセージ:**

\`\`\`
SyntaxError: Unexpected token '??'
\`\`\`

**原因:** Node.js のバージョンが古い

**解決方法:**

\`\`\`bash
# Node.js のバージョン確認
node --version

# アップデート
nvm install 18
nvm use 18
\`\`\`

## デバッグ方法

### ロギングの追加

**レベル別ロギング:**

\`\`\`javascript
const logger = {
  debug: (msg) => console.log(\`[DEBUG] \${msg}\`),
  info: (msg) => console.log(\`[INFO] \${msg}\`),
  warn: (msg) => console.warn(\`[WARN] \${msg}\`),
  error: (msg) => console.error(\`[ERROR] \${msg}\`)
};

logger.debug('Request received');
logger.info('User logged in');
logger.warn('Rate limit approaching');
logger.error('Database connection failed');
\`\`\`

### ブレークポイントデバッグ

**VS Code での設定:**

`.vscode/launch.json`:

\`\`\`json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Server",
      "program": "${workspaceFolder}/server.js",
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
\`\`\`

### ネットワークリクエストの確認

\`\`\`bash
# リクエストの詳細を表示
curl -v http://localhost:3000/api/users

# レスポンスヘッダーを表示
curl -I http://localhost:3000/api/users
\`\`\`

## サポートへの問い合わせ

問題が解決しない場合、以下の情報を含めて問い合わせてください:

1. **環境情報**

   \`\`\`bash
   node --version
   npm --version
   uname -a  # OS 情報
   \`\`\`

2. **エラーメッセージ** (完全なスタックトレース)

3. **再現手順**

4. **ログファイル**

5. **試した解決方法**

**問い合わせ先:**

- GitHub Issues: https://github.com/user/project/issues
- Email: support@example.com
- Discord: https://discord.gg/project
```

## コード例のベストプラクティス

### 1. 完全で動作するコード

❌ **悪い例（不完全）:**

```python
# 不完全な例
result = process(data)
```

✅ **良い例（完全）:**

```python
# 必要なインポート
from mymodule import DataProcessor

# データの準備
data = {
    "items": [1, 2, 3, 4, 5],
    "options": {"filter": True}
}

# 処理の実行
processor = DataProcessor()
result = processor.process(data)

# 結果の出力
print(result)  # {'filtered_items': [2, 4], 'count': 2}
```

### 2. コメントで説明を追加

❌ **悪い例（説明なし）:**

```javascript
const result = data.map(x => x * 2).filter(x => x > 10);
```

✅ **良い例（説明あり）:**

```javascript
// 各要素を2倍にする
const doubled = data.map(x => x * 2);

// 10より大きい値だけを残す
const filtered = doubled.filter(x => x > 10);

console.log(filtered);  // [12, 14, 16]
```

### 3. 実用的な例を使用

❌ **悪い例（非現実的）:**

```python
# 意味のない計算
result = add(1, 2)
```

✅ **良い例（実用的）:**

```python
# ユーザー登録の例
from myapp import User, db

# 新規ユーザーを作成
user = User(
    email="alice@example.com",
    name="Alice Smith",
    role="customer"
)

# データベースに保存
db.session.add(user)
db.session.commit()

print(f"User {user.name} created with ID {user.id}")
```

### 4. エラーハンドリングを含める

❌ **悪い例（エラー処理なし）:**

```javascript
const data = JSON.parse(response);
```

✅ **良い例（エラー処理あり）:**

```javascript
try {
  const data = JSON.parse(response);
  console.log('Parsed successfully:', data);
} catch (error) {
  console.error('Failed to parse JSON:', error.message);
  // デフォルト値を使用
  const data = { items: [] };
}
```

### 5. 期待される結果を明示

❌ **悪い例（結果が不明）:**

```python
result = calculate_total(prices)
```

✅ **良い例（結果を明示）:**

```python
prices = [100, 200, 300]
result = calculate_total(prices)

print(result)  # 600
```

## まとめ

各ドキュメントタイプの選択ガイド:

| ドキュメントタイプ | 目的 | 読者 | 詳細度 |
|------------------|------|------|--------|
| README | プロジェクト概要 | 新規ユーザー | 中 |
| API ドキュメント | API 仕様 | 開発者 | 高 |
| アーキテクチャ | 設計理解 | エンジニア | 高 |
| チュートリアル | 学習 | 初心者 | 高 |
| トラブルシューティング | 問題解決 | すべて | 中 |

詳細なドキュメント作成プロセスについては、[SKILL.md](SKILL.md) を参照してください。
