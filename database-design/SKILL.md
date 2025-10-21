---
name: "データベース設計"
description: "データベース設計とスキーマ最適化。データベース、スキーマ、DB設計、マイグレーション、インデックスに関する依頼に対応"
---

# データベース設計: データモデリングと最適化の思考プロセス

## このスキルを使う場面

- 新規データベースの設計
- 既存スキーマの最適化
- マイグレーション戦略の策定
- パフォーマンス問題の解決
- データ整合性の確保
- スケーラビリティの改善

## 思考プロセス

### フェーズ1: 要件分析とデータモデリング

**ステップ1: ビジネス要件の理解**

何を保存するか明確にする:

**データの理解:**

- [ ] エンティティ（ユーザー、商品、注文等）
- [ ] 属性（名前、価格、数量等）
- [ ] 関係性（1対1、1対多、多対多）
- [ ] ライフサイクル（作成、更新、削除）

**アクセスパターン:**

- [ ] 読み取り vs 書き込みの比率
- [ ] よく実行されるクエリ
- [ ] データの検索条件
- [ ] ソート・フィルタリング要件

**非機能要件:**

- [ ] データ量の見積もり
- [ ] トラフィック予測
- [ ] レスポンスタイム要件
- [ ] 可用性要件
- [ ] データ保持期間

**ステップ2: 概念データモデルの作成**

ER図で表現:

```
[User] ──< has many >── [Order] ──< contains >── [OrderItem]
  |                         |                         |
  |                         |                         v
  |                         |                    [Product]
  v                         v
[Address]               [Payment]
```

**関係性の特定:**

- **1対1**: ユーザーとプロフィール
- **1対多**: ユーザーと注文
- **多対多**: 商品とカテゴリー（中間テーブル必要）

**移行条件:**

- [ ] エンティティを特定した
- [ ] 関係性を定義した
- [ ] アクセスパターンを理解した

### フェーズ2: 論理設計と正規化

**ステップ1: 正規化の適用**

**第1正規形（1NF）:**

- 各カラムは単一の値
- 繰り返しグループがない

```sql
-- 非正規化（悪い例）
CREATE TABLE orders (
    id INT,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- "Product1, Product2, Product3"
);

-- 1NF（良い例）
CREATE TABLE orders (
    id INT,
    customer_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_name VARCHAR(100)
);
```

**第2正規形（2NF）:**

- 1NFを満たす
- 部分関数従属性がない

**第3正規形（3NF）:**

- 2NFを満たす
- 推移的関数従属性がない

```sql
-- 3NF違反（悪い例）
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100),  -- 推移的従属
    department_location VARCHAR(100)  -- 推移的従属
);

-- 3NF（良い例）
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100)
);
```

**ステップ2: 非正規化の検討**

パフォーマンスのための戦略的非正規化:

**非正規化すべき場合:**

- 頻繁なJOINがボトルネック
- 読み取りが圧倒的に多い
- 計算コストが高い
- リアルタイム性が重要

```sql
-- 正規化（JOIN必要）
SELECT o.id, u.name, SUM(oi.price * oi.quantity) as total
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, u.name;

-- 非正規化（高速）
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    user_name VARCHAR(100),  -- 非正規化
    total_amount DECIMAL(10,2),  -- 非正規化（事前計算）
    created_at TIMESTAMP
);
```

**移行条件:**

- [ ] 正規化を適用した
- [ ] 非正規化の必要性を評価した
- [ ] トレードオフを理解した

### フェーズ3: 物理設計とインデックス戦略

**ステップ1: データ型の選択**

適切なデータ型でストレージとパフォーマンスを最適化:

```sql
-- 悪い例
CREATE TABLE users (
    id VARCHAR(255),  -- INT で十分
    age VARCHAR(10),  -- INT で十分
    price VARCHAR(20),  -- DECIMAL で十分
    is_active VARCHAR(5),  -- BOOLEAN で十分
    data TEXT  -- JSONならJSON型
);

-- 良い例
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    age TINYINT UNSIGNED,  -- 0-255
    price DECIMAL(10,2),
    is_active BOOLEAN,
    data JSON
);
```

**データ型選択のガイドライン:**

- 整数: TINYINT < SMALLINT < INT < BIGINT
- 文字列: CHAR（固定長）vs VARCHAR（可変長）
- 日時: DATE, DATETIME, TIMESTAMP
- 真偽値: BOOLEAN
- JSON: JSON型（MySQL 5.7+, PostgreSQL 9.2+）

**ステップ2: インデックス設計**

クエリパフォーマンスの最適化:

**基本原則:**

- PRIMARY KEY は自動的にインデックス
- FOREIGN KEY にインデックス
- WHERE, JOIN, ORDER BY で使用するカラム
- カーディナリティが高いカラム

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE,  -- 自動でインデックス
    username VARCHAR(50),
    created_at TIMESTAMP,
    INDEX idx_username (username),  -- 検索用
    INDEX idx_created_at (created_at)  -- ソート用
);

-- 複合インデックス
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    INDEX idx_user_status (user_id, status),  -- 複合インデックス
    INDEX idx_status_created (status, created_at)
);
```

**複合インデックスの順序:**

```sql
-- WHERE user_id = ? AND status = ?
INDEX (user_id, status)  -- この順序が重要

-- 以下のクエリで使用可能:
-- WHERE user_id = ?
-- WHERE user_id = ? AND status = ?

-- 以下では使用不可:
-- WHERE status = ?  (先頭カラムが条件にない)
```

**カバリングインデックス:**

```sql
-- クエリ: SELECT id, user_id, total FROM orders WHERE user_id = ?

-- 通常のインデックス
INDEX idx_user (user_id);

-- カバリングインデックス（テーブルアクセス不要）
INDEX idx_user_covering (user_id, id, total);
```

**移行条件:**

- [ ] データ型を最適化した
- [ ] 必要なインデックスを作成した
- [ ] クエリパフォーマンスを確認した

### フェーズ4: 制約と整合性

**ステップ1: 制約の定義**

データ整合性の保証:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled'),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**制約の種類:**

- **NOT NULL**: 必須フィールド
- **UNIQUE**: 重複禁止
- **PRIMARY KEY**: 主キー
- **FOREIGN KEY**: 外部キー
- **CHECK**: 値の範囲制限
- **DEFAULT**: デフォルト値

**ステップ2: 参照整合性**

外部キーの設定:

```sql
-- ON DELETE / ON UPDATE オプション

-- CASCADE: 親削除時に子も削除
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- SET NULL: 親削除時に子をNULLに
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL

-- RESTRICT: 子が存在する場合、親の削除を拒否
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
```

**移行条件:**

- [ ] 制約を定義した
- [ ] 参照整合性を確保した
- [ ] ビジネスルールを反映した

### フェーズ5: スケーラビリティとパーティショニング

**ステップ1: 垂直パーティショニング**

テーブルをカラムで分割:

```sql
-- 元のテーブル（大きすぎる）
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100),
    bio TEXT,  -- 大きなデータ
    avatar BLOB,  -- さらに大きなデータ
    settings JSON
);

-- 垂直分割
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100)
);

CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    avatar BLOB,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE user_settings (
    user_id INT PRIMARY KEY,
    settings JSON,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**ステップ2: 水平パーティショニング（シャーディング）**

テーブルを行で分割:

```sql
-- 日付ベースのパーティショニング
CREATE TABLE orders (
    id INT,
    user_id INT,
    created_at DATE,
    total DECIMAL(10,2)
)
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026)
);

-- ハッシュベースのパーティショニング
CREATE TABLE users (
    id INT,
    email VARCHAR(255),
    name VARCHAR(100)
)
PARTITION BY HASH(id)
PARTITIONS 4;
```

**移行条件:**

- [ ] スケーラビリティ要件を満たした
- [ ] パーティショニング戦略を決定した

### フェーズ6: マイグレーション戦略

**ステップ1: マイグレーションスクリプトの作成**

安全な変更管理:

```sql
-- マイグレーション: 20250121_add_user_status.sql
-- UP
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
CREATE INDEX idx_status ON users(status);

-- DOWN
DROP INDEX idx_status ON users;
ALTER TABLE users DROP COLUMN status;
```

**ステップ2: ゼロダウンタイムマイグレーション**

```sql
-- 1. 新カラム追加（NULL許可）
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- 2. アプリケーションで両方に書き込み
-- （アプリケーションデプロイ）

-- 3. データ移行
UPDATE users SET new_email = email WHERE new_email IS NULL;

-- 4. NOT NULL制約追加
ALTER TABLE users MODIFY new_email VARCHAR(255) NOT NULL;

-- 5. 古いカラム削除
-- （アプリケーション更新後）
ALTER TABLE users DROP COLUMN email;

-- 6. カラム名変更
ALTER TABLE users RENAME COLUMN new_email TO email;
```

**移行条件:**

- [ ] マイグレーション計画を作成した
- [ ] ロールバック手順を準備した
- [ ] ダウンタイムを最小化した

## 判断のポイント

### RDB vs NoSQL の選択

**RDB（MySQL, PostgreSQL）を選ぶ場合:**

- トランザクションが重要
- 複雑なJOIN・集計
- スキーマが安定
- データ整合性が最優先

**NoSQL（MongoDB, DynamoDB）を選ぶ場合:**

- 柔軟なスキーマ
- 水平スケーリングが必要
- 単純なクエリが主
- 読み取り性能重視

### 正規化 vs 非正規化

**正規化:**

- データ整合性重視
- 書き込みが多い
- ストレージ効率

**非正規化:**

- 読み取りパフォーマンス
- 集計・JOIN削減
- キャッシュ的な使い方

## よくある落とし穴

1. **過度な正規化**
   - ❌ JOIN地獄
   - ✅ バランスの取れた設計

2. **インデックスの過剰作成**
   - ❌ 書き込み性能低下
   - ✅ 必要なインデックスのみ

3. **VARCHAR(255)の乱用**
   - ❌ 無駄なストレージ
   - ✅ 適切なサイズ指定

4. **NULLの扱い**
   - ❌ 3値論理の複雑さ
   - ✅ NOT NULL + DEFAULT値

5. **タイムスタンプの欠如**
   - ❌ 監査不可
   - ✅ created_at, updated_at

## 検証ポイント

### 設計段階

- [ ] ER図を作成した
- [ ] 正規化を適用した
- [ ] インデックス戦略を決定した
- [ ] 制約を定義した

### 実装段階

- [ ] マイグレーションスクリプト作成
- [ ] テストデータ投入
- [ ] パフォーマンステスト

### 運用段階

- [ ] スロークエリ監視
- [ ] インデックス効率確認
- [ ] ディスク使用量監視

## 他スキルとの連携

### database-design → api-design

APIとDB設計の整合:

1. database-designでスキーマ設計
2. api-designでエンドポイント設計
3. データモデルとAPI仕様の一貫性

### database-design + performance-optimization

DB最適化:

1. database-designでスキーマ確認
2. performance-optimizationでクエリ最適化
3. インデックス・パーティショニング適用

### database-design → migration-assistant

DBマイグレーション:

1. database-designで新スキーマ設計
2. migration-assistantで移行計画
3. 段階的なデータ移行

## データベース設計のベストプラクティス

### 命名規則

```sql
-- テーブル名: 複数形、スネークケース
CREATE TABLE user_orders;

-- カラム名: スネークケース
CREATE TABLE users (
    id INT,
    first_name VARCHAR(50),
    created_at TIMESTAMP
);

-- インデックス名: idx_テーブル名_カラム名
CREATE INDEX idx_users_email ON users(email);

-- 外部キー名: fk_テーブル名_参照テーブル名
CONSTRAINT fk_orders_users FOREIGN KEY (user_id) REFERENCES users(id)
```

### ソフトデリート

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    deleted_at TIMESTAMP NULL,
    INDEX idx_deleted_at (deleted_at)
);

-- 有効なユーザーのみ取得
SELECT * FROM users WHERE deleted_at IS NULL;
```

### 監査ログ

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT
);
```
