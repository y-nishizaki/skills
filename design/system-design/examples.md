# システム設計: 設計パターンと実装例

このドキュメントでは、システム設計スキルで説明されている各種アーキテクチャパターン、設計手法、トレードオフの具体例を示します。

## 目次

- [アーキテクチャスタイルの比較](#アーキテクチャスタイルの比較)
- [トレードオフの記録例](#トレードオフの記録例)
- [スケーラビリティパターン](#スケーラビリティパターン)
- [データ設計の例](#データ設計の例)
- [信頼性パターン](#信頼性パターン)

## アーキテクチャスタイルの比較

### 例1: モノリシック vs マイクロサービス

**シナリオ:** ECサイトの構築

#### モノリシックアーキテクチャ

```
┌─────────────────────────────────┐
│   Single Application            │
│  ┌─────────────────────────┐   │
│  │  UI Layer               │   │
│  ├─────────────────────────┤   │
│  │  Business Logic         │   │
│  │  - User Management      │   │
│  │  - Product Catalog      │   │
│  │  - Shopping Cart        │   │
│  │  - Order Processing     │   │
│  │  - Payment              │   │
│  ├─────────────────────────┤   │
│  │  Data Access Layer      │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
         │
         ▼
   ┌─────────┐
   │Database │
   └─────────┘
```

**メリット:**

- シンプルな開発・デプロイ
- トランザクション管理が容易
- デバッグがしやすい
- 小規模チームに適している

**デメリット:**

- スケールが困難（全体をスケール）
- 技術スタックの変更が困難
- 大規模チームでの並行開発が難しい
- デプロイリスクが高い（全体を再デプロイ）

**適用ケース:**

- チーム人数: 1-10名
- トラフィック: 〜1,000 req/s
- 変更頻度: 低-中
- 初期開発スピード重視

#### マイクロサービスアーキテクチャ

```
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ User   │  │Product │  │ Cart   │  │Payment │
│Service │  │Service │  │Service │  │Service │
└────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘
     │           │           │           │
     ▼           ▼           ▼           ▼
  ┌────┐      ┌────┐      ┌────┐      ┌────┐
  │ DB │      │ DB │      │ DB │      │ DB │
  └────┘      └────┘      └────┘      └────┘

           ┌──────────────┐
           │ API Gateway  │
           └──────────────┘
```

**メリット:**

- 独立したスケーリング
- 技術スタックの柔軟性
- チーム独立性（Conway's Law）
- 部分的デプロイ（リスク分散）

**デメリット:**

- 複雑性の増加（運用・監視）
- 分散トランザクションの難しさ
- ネットワークオーバーヘッド
- データ整合性の管理が困難

**適用ケース:**

- チーム人数: 複数チーム（各5-10名）
- トラフィック: 変動が大きい、または高負荷
- 変更頻度: 高
- スケーラビリティ重視

### 例2: レイヤードアーキテクチャ

**典型的な3層構造:**

```
┌──────────────────────────┐
│   Presentation Layer     │  ← ユーザーインターフェース
│   (UI/API)               │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   Business Logic Layer   │  ← ビジネスルール・ロジック
│   (Services/Domain)      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   Data Access Layer      │  ← データ永続化
│   (Repository/ORM)       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│      Database            │
└──────────────────────────┘
```

**依存関係のルール:**

- 上位層は下位層に依存できる
- 下位層は上位層に依存してはいけない
- 各層は隣接する層とのみ通信

**メリット:**

- 関心の分離が明確
- テストしやすい
- 変更の影響範囲が限定的

**デメリット:**

- パフォーマンスオーバーヘッド
- 過度な抽象化の可能性

## トレードオフの記録例

### 例: キャッシュ戦略の決定

**決定内容:** Redis をキャッシュレイヤーとして導入

**検討した選択肢:**

1. **Redis（選択）**
2. Memcached
3. アプリケーション内メモリキャッシュ

**選択理由:**

- データ構造が豊富（リスト、セット、ハッシュ等）
- 永続化オプションあり（障害時の復旧）
- クラスタリングサポート（スケーラビリティ）
- 成熟したエコシステム

**トレードオフ:**

| 側面 | メリット | デメリット |
|------|---------|-----------|
| **パフォーマンス** | 高速（メモリベース）| ネットワークレイテンシ |
| **複雑性** | 単一技術で多機能 | 設定・運用の学習コスト |
| **コスト** | オープンソース | メモリコスト |
| **スケーラビリティ** | クラスタリング可能 | シャーディング戦略が必要 |

**前提条件:**

- 読み取りが書き込みの10倍以上
- データサイズ: 平均1KB、最大10MB
- キャッシュヒット率目標: 80%以上
- レスポンスタイム要件: 100ms以下

**再検討の条件:**

- キャッシュヒット率が50%以下に低下
- 読み書き比率が変化（1:1に近づく）
- メモリコストが予算の30%を超える
- 別の要件（地理的分散等）が発生

## スケーラビリティパターン

### パターン1: 水平スケーリング（スケールアウト）

**アーキテクチャ:**

```
         ┌─────────────┐
         │Load Balancer│
         └──────┬──────┘
                │
      ┌─────────┼─────────┐
      │         │         │
      ▼         ▼         ▼
   ┌────┐   ┌────┐   ┌────┐
   │App1│   │App2│   │App3│  ← ステートレス
   └────┘   └────┘   └────┘
      │         │         │
      └─────────┼─────────┘
                │
                ▼
           ┌────────┐
           │Database│
           └────────┘
```

**重要なポイント:**

1. **ステートレス設計**
   - セッション情報を外部ストア（Redis等）に保存
   - サーバー間で状態を共有しない

2. **ロードバランシング戦略**
   - ラウンドロビン: 均等に分散
   - 最小コネクション: 負荷に応じて分散
   - IPハッシュ: 同じクライアントを同じサーバーへ

3. **データベース対策**
   - 読み取りレプリカ（リードレプリカ）
   - コネクションプーリング
   - クエリキャッシング

### パターン2: データベースシャーディング

**水平分割（シャーディング）:**

```
Application Layer
       │
       ▼
  Shard Router
       │
   ┌───┼───┐
   │   │   │
   ▼   ▼   ▼
┌────┬────┬────┐
│Shard│Shard│Shard│
│  1 │  2 │  3 │
│    │    │    │
│User│User│User│
│1-  │100K│200K│
│100K│-   │-   │
│    │200K│300K│
└────┴────┴────┘
```

**シャーディングキーの選択:**

- ユーザーID: ユーザーデータの分散
- 地理的リージョン: 地域ごとの分散
- 日付: 時系列データの分散

**実装例（ユーザーIDベース）:**

```python
def get_shard(user_id, num_shards=3):
    """ユーザーIDからシャードを決定"""
    return user_id % num_shards

# 使用例
user_id = 12345
shard_id = get_shard(user_id)
db = get_database_connection(shard_id)
```

**メリット:**

- データサイズの分散
- 書き込みの分散
- 独立したスケーリング

**デメリット:**

- JOIN が困難（複数シャード間）
- リバランスが困難
- 複雑性の増加

### パターン3: キャッシュによるスケーリング

**多層キャッシュ戦略:**

```
Client
  │
  ▼
┌──────────────┐
│Browser Cache │ ← 1st Level (最速)
└──────────────┘
  │
  ▼
┌──────────────┐
│   CDN        │ ← 2nd Level (静的コンテンツ)
└──────────────┘
  │
  ▼
┌──────────────┐
│Redis/Memcache│ ← 3rd Level (動的データ)
└──────────────┘
  │
  ▼
┌──────────────┐
│  Database    │ ← 最終データソース
└──────────────┘
```

**キャッシュパターン:**

1. **Cache-Aside (Lazy Loading)**

```python
def get_user(user_id):
    # キャッシュを確認
    user = cache.get(f"user:{user_id}")
    if user:
        return user

    # キャッシュミス時、DBから取得
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # キャッシュに保存
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

2. **Write-Through**

```python
def update_user(user_id, data):
    # DBを更新
    db.update("UPDATE users SET ... WHERE id = ?", data, user_id)

    # キャッシュも同時に更新
    cache.set(f"user:{user_id}", data, ttl=3600)
```

3. **Write-Behind (Write-Back)**

```python
def update_user(user_id, data):
    # キャッシュを即座に更新
    cache.set(f"user:{user_id}", data, ttl=3600)

    # DB更新は非同期で実行
    queue.enqueue(db_update_task, user_id, data)
```

## データ設計の例

### 例: E-Commerceのデータモデル

**正規化されたリレーショナルモデル:**

```sql
-- ユーザーテーブル
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 商品テーブル
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    category_id INT REFERENCES categories(id)
);

-- 注文テーブル
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total_amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 注文詳細テーブル
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL
);
```

**非正規化（NoSQLモデル - MongoDB例）:**

```javascript
// 注文ドキュメント（埋め込み形式）
{
  "_id": "order_12345",
  "user": {
    "id": "user_001",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "items": [
    {
      "product_id": "prod_001",
      "product_name": "Laptop",
      "price": 1299.99,
      "quantity": 1
    },
    {
      "product_id": "prod_002",
      "product_name": "Mouse",
      "price": 29.99,
      "quantity": 2
    }
  ],
  "total_amount": 1359.97,
  "status": "completed",
  "created_at": ISODate("2025-01-15T10:30:00Z")
}
```

**選択基準:**

| 要件 | リレーショナル | NoSQL |
|------|--------------|-------|
| データ整合性（ACID） | ✅ 強い | ⚠️ 弱い（結果整合性） |
| 複雑なクエリ | ✅ SQL | ⚠️ 限定的 |
| スケーラビリティ | ⚠️ 垂直が主 | ✅ 水平スケール容易 |
| スキーマ変更 | ⚠️ マイグレーション必要 | ✅ 柔軟 |
| JOIN操作 | ✅ 効率的 | ❌ 困難 |

## 信頼性パターン

### パターン1: サーキットブレーカー

**概念:**

障害サービスへの連続的な呼び出しを防ぎ、システム全体の障害を防ぐ。

**状態遷移:**

```
     正常
      │
  ┌───▼───┐
  │Closed │ ← 通常状態（リクエスト通過）
  └───┬───┘
      │ 障害頻発
      ▼
  ┌───────┐
  │ Open  │ ← 遮断状態（リクエスト拒否）
  └───┬───┘
      │ 一定時間経過
      ▼
  ┌───────────┐
  │Half-Open  │ ← 試行状態（一部リクエスト許可）
  └─┬─────┬───┘
    │成功  │失敗
    │      └──→ Open
    ▼
  Closed
```

**実装例:**

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException()

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### パターン2: リトライ戦略

**指数バックオフ:**

```python
import time

def exponential_backoff_retry(func, max_retries=5, base_delay=1):
    """指数バックオフでリトライ"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e

            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s, 8s, 16s...
            # ジッター追加（同時リトライの分散）
            jitter = random.uniform(0, delay * 0.1)
            time.sleep(delay + jitter)
```

**リトライすべきエラー vs すべきでないエラー:**

| エラー種別 | リトライ | 理由 |
|-----------|---------|------|
| ネットワークタイムアウト | ✅ | 一時的な可能性 |
| 503 Service Unavailable | ✅ | サービス復旧待ち |
| 500 Internal Server Error | ✅ | 一時的な可能性 |
| 429 Too Many Requests | ✅ | レート制限（待機後） |
| 400 Bad Request | ❌ | クライアントエラー |
| 401 Unauthorized | ❌ | 認証エラー |
| 404 Not Found | ❌ | リソース不存在 |

### パターン3: バルクヘッド

**概念:**

障害を分離し、システム全体への影響を防ぐ。

**実装例（接続プール分離）:**

```
┌──────────────────────┐
│  Application         │
│  ┌────────────────┐  │
│  │Critical Path   │  │
│  │Connection Pool │  │ ← 重要機能専用（20接続）
│  │(20 connections)│  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │Non-Critical    │  │
│  │Connection Pool │  │ ← 非重要機能用（10接続）
│  │(10 connections)│  │
│  └────────────────┘  │
└──────────────────────┘
```

**メリット:**

- 非重要機能の障害が重要機能に影響しない
- リソース枯渇を防ぐ
- 段階的な劣化（Graceful Degradation）

## まとめ

システム設計の重要原則:

1. **要件に基づく設計** - トレンドではなく要件で判断
2. **シンプルさ優先** - 必要になってから複雑化
3. **トレードオフの明示** - 決定の理由と前提条件を記録
4. **段階的な進化** - 小さく始めて成長に応じて拡張
5. **計測と検証** - 設計判断をデータで検証

詳細な設計プロセスについては、[SKILL.md](SKILL.md) を参照してください。
