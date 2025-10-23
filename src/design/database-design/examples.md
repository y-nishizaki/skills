# データベース設計: 実装例とパターン

このドキュメントでは、データベース設計スキルで説明されている設計パターンと最適化手法の具体例を示します。

## E-Commerce データベース設計例

### 正規化されたスキーマ

```sql
-- ユーザーテーブル
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- 商品カテゴリー
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT,
    slug VARCHAR(100) UNIQUE,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_parent (parent_id),
    INDEX idx_slug (slug)
);

-- 商品テーブル
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    category_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_category (category_id),
    INDEX idx_slug (slug),
    INDEX idx_active (is_active),
    INDEX idx_price (price)
);

-- 注文テーブル
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_created_at (created_at)
);

-- 注文詳細テーブル
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
);
```

## パフォーマンス最適化の例

### カバリングインデックス

```sql
-- クエリ: ユーザーの最近の注文リスト
SELECT id, status, total, created_at
FROM orders
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 10;

-- カバリングインデックス（テーブルアクセス不要）
CREATE INDEX idx_user_orders_covering
ON orders(user_id, created_at DESC)
INCLUDE (id, status, total);
```

### パーティショニング

```sql
-- 日付ベースのパーティショニング
CREATE TABLE orders_partitioned (
    id SERIAL,
    user_id INT NOT NULL,
    status VARCHAR(20),
    total DECIMAL(10,2),
    created_at DATE NOT NULL
)
PARTITION BY RANGE (created_at);

-- 月ごとのパーティション
CREATE TABLE orders_2025_01 PARTITION OF orders_partitioned
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE orders_2025_02 PARTITION OF orders_partitioned
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

## マイグレーション例

### カラム追加

```sql
-- ゼロダウンタイムマイグレーション

-- 1. 新カラム追加（NULL許可）
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 2. デフォルト値設定（既存データ）
UPDATE users SET phone = '' WHERE phone IS NULL;

-- 3. NOT NULL制約追加
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;

-- 4. インデックス追加
CREATE INDEX idx_phone ON users(phone);
```

詳細な設計プロセスについては、[SKILL.md](SKILL.md) を参照してください。
