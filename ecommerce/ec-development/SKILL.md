---
name: ec-development
description: ECサイトの開発に必要な技術スキルを提供するスキル。フロントエンド（React/Next.js/Vue.js）、バックエンド（PHP/Python/Node.js）、ECプラットフォーム（Shopify/Magento/WooCommerce）、API連携、決済ゲートウェイ統合、セキュリティ対策などの開発業務に使用される。
license: 完全な条項はLICENSE.txtを参照
---

# EC開発スキル

このスキルは、ECサイト開発に必要な技術的な専門知識とベストプラクティスを提供します。

## スキルの目的

ECサイトの開発において、フロントエンド、バックエンド、プラットフォーム選定、API統合、セキュリティ実装など、技術的な意思決定と実装を支援します。

## 使用タイミング

以下の場合にこのスキルを使用する：

- ECサイトの新規開発を開始する
- 既存ECサイトの技術スタック見直しを行う
- ECプラットフォームの選定を行う
- 決済システムやサードパーティAPIの統合が必要な場合
- セキュリティ対策やコンプライアンス対応が必要な場合
- パフォーマンス最適化を実施する
- 技術的な課題のトラブルシューティングを行う

## フロントエンド開発（2025年技術スタック）

### 主要フレームワークとライブラリ

#### React

最も人気のあるJavaScriptライブラリ。

**特徴:**
- コンポーネントベースのアーキテクチャ
- 仮想DOMによる高速レンダリング
- 豊富なエコシステム
- **React Server Components（2025年）**: サーバーサイドレンダリングの強化

**ECサイトでの用途:**
- 動的な商品フィルタリング
- インタラクティブな商品ページ
- リアルタイムカート更新
- SPA（Single Page Application）

**推奨構成:**
```
- React 18+
- TypeScript
- React Router（ナビゲーション）
- Redux / Zustand（状態管理）
```

#### Next.js

Reactを拡張したフレームワーク。ECサイトに最適。

**特徴:**
- サーバーサイドレンダリング（SSR）
- 静的サイト生成（SSG）
- SEO最適化
- 画像最適化
- APIルート
- ファイルベースルーティング

**ECサイトでの利点:**
- SEO強化による検索エンジンでの可視性向上
- 初回ロード速度の改善
- Core Web Vitals対応

**推奨用途:**
- 商品カタログページ（SSG）
- 動的な商品詳細ページ（SSR）
- ブログ・コンテンツマーケティング

#### Vue.js

シンプルで学習曲線が緩やかなフレームワーク。

**特徴:**
- 段階的な導入が可能
- 直感的なテンプレート構文
- リアクティブなデータバインディング
- 軽量

**ECサイトでの用途:**
- 既存サイトへの部分的な導入
- プロトタイプ開発
- 小〜中規模ECサイト

### スタイリング

#### Tailwind CSS

2025年の主流ユーティリティファーストCSSフレームワーク。

**特徴:**
- ユーティリティクラスベース
- カスタマイズ性が高い
- ファイルサイズの最小化（未使用クラスの削除）
- レスポンシブデザインの迅速な実装

**ECサイトでの利点:**
- 一貫性のあるデザインシステム
- 開発速度の向上
- メンテナンスの容易性

**基本例:**
```jsx
<div className="container mx-auto px-4">
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <ProductCard />
    <ProductCard />
    <ProductCard />
  </div>
</div>
```

#### CSS-in-JS

JavaScriptでスタイルを管理する手法。

**主要ライブラリ:**
- styled-components
- Emotion
- CSS Modules

**利点:**
- スコープ化されたスタイル
- 動的スタイリング
- TypeScript統合

### 基礎技術

#### HTML5

**ECサイトでの重要要素:**
- セマンティックHTML（`<article>`, `<section>`, `<nav>`）
- 構造化データ（Schema.org）
- アクセシビリティ（ARIA属性）

#### CSS3

**重要技術:**
- Flexbox / Grid Layout
- レスポンシブデザイン（メディアクエリ）
- アニメーション
- カスタムプロパティ（CSS変数）

#### TypeScript

**2025年のベストプラクティス:**
- 型安全性によるバグ削減
- IDEサポートの向上
- リファクタリングの容易性
- APIレスポンスの型定義

### パフォーマンス最適化

#### Core Web Vitals対応（2025年必須）

Googleのランキング要素として定着。

**主要指標:**

1. **LCP（Largest Contentful Paint）**
   - 目標: 2.5秒以下
   - 対策: 画像最適化、CDN使用、サーバーレスポンス改善

2. **FID（First Input Delay）**
   - 目標: 100ms以下
   - 対策: JavaScriptの最小化、遅延ロード

3. **CLS（Cumulative Layout Shift）**
   - 目標: 0.1以下
   - 対策: 画像・動画の寸法指定、フォントロード最適化

**実装ツール:**
- Lighthouse
- PageSpeed Insights
- Web Vitals ライブラリ

#### PWA（Progressive Web Apps）

**特徴:**
- オフライン機能
- プッシュ通知
- ホーム画面への追加
- 高速な読み込み速度

**ECサイトでの利点:**
- ネットワーク不安定時も利用可能
- アプリライクな体験
- エンゲージメント向上

#### 画像最適化

- WebP/AVIF形式の使用
- レスポンシブ画像（srcset）
- 遅延ロード（lazy loading）
- 画像CDN（Cloudinary、imgix）

#### コード分割

- ルートベースの分割
- コンポーネント遅延ロード
- Tree Shaking

## バックエンド開発

### 言語・フレームワーク

#### PHP

ECサイトで最も広く使用される言語。

**主要フレームワーク:**

**Laravel:**
- モダンなMVCフレームワーク
- Eloquent ORM
- 認証・認可システム
- キューシステム
- スケジューリング

**WordPress + WooCommerce:**
- 豊富なプラグインエコシステム
- 非エンジニアでも管理可能
- カスタマイズ性

**ECサイトでの実装例:**
```php
// Laravelでの商品モデル
class Product extends Model
{
    protected $fillable = ['name', 'price', 'description', 'stock'];

    public function orders()
    {
        return $this->belongsToMany(Order::class);
    }
}
```

#### Python

データ処理とAI機能に強い。

**主要フレームワーク:**

**Django:**
- フルスタックフレームワーク
- 管理画面標準装備
- ORM
- セキュリティ機能充実

**Flask:**
- 軽量・柔軟
- マイクロサービス向け
- API開発に最適

**ECサイトでの用途:**
- レコメンデーションエンジン
- 価格最適化アルゴリズム
- 在庫予測
- データ分析パイプライン

#### Node.js

JavaScriptのサーバーサイド実行環境。

**主要フレームワーク:**

**Express.js:**
- シンプルで柔軟
- RESTful API構築
- ミドルウェアシステム

**NestJS:**
- TypeScript完全対応
- エンタープライズグレード
- モジュラーアーキテクチャ

**ECサイトでの利点:**
- フロントエンド・バックエンド統一言語
- リアルタイム機能（WebSocket）
- 非同期I/O

### データベース設計

#### リレーショナルデータベース

**PostgreSQL / MySQL:**

基本的なECデータベーススキーマ:

```sql
-- 商品テーブル
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 顧客テーブル
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 注文テーブル
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 注文明細テーブル
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);
```

**インデックス設計:**
- 検索頻度の高いカラム（email、product_id）
- 外部キー
- 複合インデックス（category + price等）

#### ORM

**Prisma（Node.js/TypeScript）:**
- 型安全なデータベースクライアント
- マイグレーション管理
- クエリビルダー

**Drizzle:**
- サーバーレス環境に最適
- 軽量

**Eloquent（Laravel）:**
- アクティブレコードパターン
- リレーションシップの簡単な定義

### API設計

#### RESTful API

**ベストプラクティス:**

1. **リソースベースのURL設計**
```
GET    /api/products          # 商品一覧
GET    /api/products/:id      # 商品詳細
POST   /api/products          # 商品作成
PUT    /api/products/:id      # 商品更新
DELETE /api/products/:id      # 商品削除
```

2. **適切なHTTPステータスコード**
- 200: 成功
- 201: 作成成功
- 400: 不正なリクエスト
- 401: 未認証
- 403: 権限なし
- 404: リソースなし
- 500: サーバーエラー

3. **ページネーション**
```
GET /api/products?page=1&limit=20
```

4. **フィルタリング・ソート**
```
GET /api/products?category=electronics&sort=price_asc
```

#### GraphQL

**2025年の採用トレンド:**

**利点:**
- クライアントが必要なデータのみ取得
- 単一エンドポイント
- 強い型システム

**基本クエリ例:**
```graphql
query {
  product(id: "123") {
    id
    name
    price
    category {
      name
    }
    reviews(limit: 5) {
      rating
      comment
    }
  }
}
```

**ECサイトでの用途:**
- モバイルアプリとWeb間でのデータ統一
- パフォーマンス最適化
- 複雑なデータ関係の取得

### サーバーレスアーキテクチャ

**2025年のトレンド:**

**利点:**
- スケーラビリティ
- コスト削減（使用量課金）
- 運用負荷低減

**主要プラットフォーム:**
- AWS Lambda
- Vercel Functions
- Cloudflare Workers

**ECサイトでの用途:**
- 画像処理
- メール送信
- Webhook処理
- バッチ処理

## ECプラットフォーム

### Shopify

**特徴:**
- SaaS型ECプラットフォーム
- セットアップが容易
- 豊富なテーマとアプリ
- 決済・配送統合済み

**カスタマイズ:**

**Liquid テンプレート言語:**
```liquid
{% for product in collection.products %}
  <div class="product-card">
    <h3>{{ product.title }}</h3>
    <p>{{ product.price | money }}</p>
  </div>
{% endfor %}
```

**Shopify API:**
- Admin API: 商品・注文管理
- Storefront API: カスタムフロントエンド構築
- GraphQL対応

**適している場合:**
- 迅速な立ち上げが必要
- 運用リソースが限定的
- D2Cブランド

### Magento

**特徴:**
- オープンソース（Magento Open Source）
- エンタープライズ版（Adobe Commerce）
- 高度なカスタマイズ性
- B2B機能充実

**技術スタック:**
- PHP
- MySQL
- Elasticsearch
- Redis

**適している場合:**
- 大規模ECサイト
- 複雑なビジネスロジック
- B2B取引
- 豊富な開発リソース

### WooCommerce

**特徴:**
- WordPressプラグイン
- オープンソース・無料
- 豊富な拡張機能
- コンテンツマーケティングとの統合

**技術スタック:**
- PHP
- MySQL
- WordPress

**適している場合:**
- 中小規模ECサイト
- コンテンツ主導のサイト
- WordPress既存サイトへの追加

### EC-CUBE

**特徴:**
- 日本製オープンソース
- 日本の商習慣に対応
- カスタマイズ性が高い

**技術スタック:**
- PHP
- Symfony
- MySQL

**適している場合:**
- 日本市場向け
- 独自のカスタマイズが必要
- オンプレミス運用

### プラットフォーム選定基準

| 基準 | Shopify | Magento | WooCommerce | EC-CUBE |
|------|---------|---------|-------------|---------|
| セットアップ難易度 | 易 | 難 | 中 | 中 |
| カスタマイズ性 | 中 | 高 | 高 | 高 |
| コスト | 月額課金 | 高 | 低〜中 | 低〜中 |
| スケーラビリティ | 高 | 高 | 中 | 中 |
| 技術サポート | 公式 | コミュニティ | コミュニティ | コミュニティ |
| 適正規模 | 小〜大 | 大 | 小〜中 | 小〜中 |

## API連携・決済ゲートウェイ

### 主要決済サービス

#### Stripe

**特徴:**
- 開発者フレンドリー
- 豊富なAPIドキュメント
- グローバル対応
- サブスクリプション対応

**実装例（Node.js）:**
```javascript
const stripe = require('stripe')('sk_test_xxx');

// 支払いインテント作成
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'jpy',
  payment_method_types: ['card'],
});

// クライアントシークレットをフロントエンドへ返す
res.json({ clientSecret: paymentIntent.client_secret });
```

**対応決済手段:**
- クレジットカード
- Apple Pay / Google Pay
- 銀行振込
- コンビニ決済（日本）

#### PayPal

**特徴:**
- 世界的な認知度
- バイヤープロテクション
- 簡単統合

**実装:**
- PayPal Checkout SDK
- REST API

#### Amazon Pay

**特徴:**
- Amazonアカウントで決済
- 高い信頼性
- 配送先情報の自動入力

### Webhook実装

**支払い完了時の処理例:**
```javascript
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];

  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  if (event.type === 'payment_intent.succeeded') {
    const paymentIntent = event.data.object;
    // 注文を確定
    await fulfillOrder(paymentIntent);
  }

  res.json({received: true});
});
```

## セキュリティ・個人情報保護

### SSL/TLS設定

**必須要件:**
- HTTPS通信の強制
- TLS 1.2以上の使用
- 信頼されたCA発行の証明書

**実装:**
```nginx
# Nginxでのリダイレクト設定
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

### PCI DSS準拠

**クレジットカード情報の取り扱い:**

**SAQ（Self-Assessment Questionnaire）レベル:**
- SAQ A: 決済処理を完全にサードパーティに委託（推奨）
- SAQ D: 自社でカード情報を処理

**ベストプラクティス:**
- カード情報を自社サーバーに保存しない
- トークン化の使用（Stripe、PayPalなど）
- iframeやSDKで決済フォームを分離

### GDPR対応（EU向け）

**必須対応:**
1. **同意管理**
   - Cookie使用の同意取得
   - 明示的なオプトイン

2. **データポータビリティ**
   - 顧客データのエクスポート機能

3. **削除権（忘れられる権利）**
   - アカウント削除機能

4. **データ保護責任者（DPO）**
   - 特定条件下で任命

### セキュリティベストプラクティス

#### 認証・認可

**実装:**
- パスワードハッシュ化（bcrypt、Argon2）
- JWT（JSON Web Token）
- セッション管理
- 二要素認証（2FA）

**パスワードハッシュ例（Node.js）:**
```javascript
const bcrypt = require('bcrypt');

// ハッシュ化
const hashedPassword = await bcrypt.hash(password, 10);

// 検証
const isValid = await bcrypt.compare(password, hashedPassword);
```

#### CSRF対策

- CSRFトークンの使用
- SameSite Cookie属性

#### XSS対策

- ユーザー入力のサニタイズ
- エスケープ処理
- Content Security Policy（CSP）ヘッダー

#### SQL インジェクション対策

- プリペアドステートメント使用
- ORMの活用
- 入力バリデーション

#### レート制限

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分
  max: 100 // 100リクエスト/15分
});

app.use('/api/', limiter);
```

## 開発ベストプラクティス

### バージョン管理

**Git戦略:**
- Git Flow / GitHub Flow
- 機能ブランチ
- プルリクエストレビュー

### CI/CD

**自動化パイプライン:**
1. コミット
2. 自動テスト実行
3. ビルド
4. ステージング環境デプロイ
5. 本番デプロイ（承認後）

**主要ツール:**
- GitHub Actions
- GitLab CI/CD
- CircleCI
- Jenkins

### テスト

**テスト種類:**

1. **ユニットテスト**
   - Jest（JavaScript）
   - PHPUnit（PHP）
   - pytest（Python）

2. **統合テスト**
   - API統合
   - データベース連携

3. **E2Eテスト**
   - Playwright
   - Cypress
   - Selenium

### モニタリング

**監視項目:**
- サーバーパフォーマンス
- エラーログ
- トランザクション監視
- ユーザーセッション

**ツール:**
- Sentry（エラートラッキング）
- New Relic / Datadog（APM）
- Google Analytics（ユーザー行動）
- Prometheus + Grafana（メトリクス）

## まとめ

EC開発では以下が重要：

1. **2025年技術スタックの採用**: React/Next.js、TypeScript、Tailwind CSS
2. **Core Web Vitals対応**: SEOとUXの向上
3. **適切なプラットフォーム選定**: ビジネス要件に応じた選択
4. **セキュリティ**: PCI DSS、GDPR、SSL/TLS
5. **スケーラビリティ**: サーバーレス、API設計
6. **パフォーマンス**: 画像最適化、コード分割、PWA

これらの要素を統合し、安全で高速、スケーラブルなECサイトを構築する。
