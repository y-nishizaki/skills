---
name: "SQL基礎"
description: "データベースからのデータ抽出・加工。SELECT、JOIN、GROUP BY、サブクエリなど"
---

# SQL基礎: データ取得の必須スキル

## このスキルを使う場面

- データベースからデータを取得したい
- 複数テーブルを結合したい
- データを集計・要約したい
- 条件に合うデータを抽出したい
- データ分析の前処理をしたい

## 思考プロセス

### フェーズ1: 基本的なデータ取得（SELECT）

```sql
-- すべての列を取得
SELECT * FROM users;

-- 特定の列を取得
SELECT name, age, city FROM users;

-- ユニークな値
SELECT DISTINCT city FROM users;

-- 列に別名
SELECT name AS user_name, age AS user_age FROM users;
```

**WHERE句による条件指定:**

```sql
-- 単一条件
SELECT * FROM users WHERE age >= 20;

-- 複数条件（AND）
SELECT * FROM users WHERE age >= 20 AND city = 'Tokyo';

-- 複数条件（OR）
SELECT * FROM users WHERE city = 'Tokyo' OR city = 'Osaka';

-- IN句
SELECT * FROM users WHERE city IN ('Tokyo', 'Osaka', 'Kyoto');

-- LIKE句（パターンマッチ）
SELECT * FROM users WHERE name LIKE 'A%';  -- Aで始まる

-- BETWEEN句
SELECT * FROM users WHERE age BETWEEN 20 AND 30;

-- IS NULL / IS NOT NULL
SELECT * FROM users WHERE email IS NOT NULL;
```

### フェーズ2: データの並べ替えと制限

```sql
-- ORDER BY（ソート）
SELECT * FROM users ORDER BY age DESC;  -- 降順
SELECT * FROM users ORDER BY city ASC, age DESC;  -- 複数列

-- LIMIT（件数制限）
SELECT * FROM users LIMIT 10;

-- OFFSET（スキップ）
SELECT * FROM users LIMIT 10 OFFSET 20;  -- 21件目から10件
```

### フェーズ3: 集計関数（Aggregation）

```sql
-- COUNT（件数）
SELECT COUNT(*) FROM users;
SELECT COUNT(DISTINCT city) FROM users;

-- SUM（合計）
SELECT SUM(amount) FROM orders;

-- AVG（平均）
SELECT AVG(age) FROM users;

-- MIN / MAX（最小・最大）
SELECT MIN(age), MAX(age) FROM users;

-- GROUP BY（グループ化）
SELECT city, COUNT(*) as user_count
FROM users
GROUP BY city;

SELECT city, AVG(age) as avg_age
FROM users
GROUP BY city
ORDER BY avg_age DESC;

-- HAVING（グループ化後の条件）
SELECT city, COUNT(*) as user_count
FROM users
GROUP BY city
HAVING COUNT(*) >= 10;
```

### フェーズ4: テーブル結合（JOIN）

```sql
-- INNER JOIN（両方に存在するデータ）
SELECT u.name, o.order_date, o.amount
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id;

-- LEFT JOIN（左テーブルのすべて）
SELECT u.name, o.order_date, o.amount
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id;

-- RIGHT JOIN（右テーブルのすべて）
SELECT u.name, o.order_date, o.amount
FROM users u
RIGHT JOIN orders o ON u.user_id = o.user_id;

-- 複数テーブルの結合
SELECT u.name, o.order_date, p.product_name
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
INNER JOIN products p ON o.product_id = p.product_id;
```

### フェーズ5: サブクエリ

```sql
-- WHERE句でのサブクエリ
SELECT * FROM users
WHERE user_id IN (
    SELECT user_id FROM orders WHERE amount > 10000
);

-- FROM句でのサブクエリ
SELECT city, avg_age
FROM (
    SELECT city, AVG(age) as avg_age
    FROM users
    GROUP BY city
) AS city_stats
WHERE avg_age > 30;

-- SELECT句でのサブクエリ
SELECT name, age,
    (SELECT AVG(age) FROM users) as avg_age
FROM users;
```

### フェーズ6: ウィンドウ関数

```sql
-- ROW_NUMBER（行番号）
SELECT name, age,
    ROW_NUMBER() OVER (ORDER BY age DESC) as rank
FROM users;

-- RANK（ランキング）
SELECT name, age,
    RANK() OVER (ORDER BY age DESC) as rank
FROM users;

-- パーティション付きウィンドウ
SELECT name, city, age,
    ROW_NUMBER() OVER (PARTITION BY city ORDER BY age DESC) as city_rank
FROM users;

-- 累積合計
SELECT order_date, amount,
    SUM(amount) OVER (ORDER BY order_date) as cumulative_sum
FROM orders;

-- 移動平均
SELECT order_date, amount,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7days
FROM orders;
```

### フェーズ7: 実務的なクエリ

**日付処理:**

```sql
-- 日付抽出
SELECT DATE(created_at) as date, COUNT(*) as daily_count
FROM orders
GROUP BY DATE(created_at);

-- 期間指定
SELECT * FROM orders
WHERE created_at >= '2025-01-01'
AND created_at < '2025-02-01';

-- 曜日・月
SELECT DAYOFWEEK(order_date) as day, COUNT(*) as count
FROM orders
GROUP BY DAYOFWEEK(order_date);
```

**CASE式（条件分岐）:**

```sql
SELECT name, age,
    CASE
        WHEN age < 20 THEN '10代'
        WHEN age < 30 THEN '20代'
        WHEN age < 40 THEN '30代'
        ELSE '40代以上'
    END as age_group
FROM users;
```

**文字列操作:**

```sql
-- CONCAT（結合）
SELECT CONCAT(last_name, ' ', first_name) as full_name
FROM users;

-- SUBSTRING（部分文字列）
SELECT SUBSTRING(phone, 1, 3) as area_code
FROM users;

-- UPPER / LOWER（大文字・小文字）
SELECT UPPER(name) as name_upper FROM users;
```

## 判断のポイント

### JOINの選択

**INNER JOIN:**

- 両方に存在するデータのみ
- マスタとトランザクションの結合

**LEFT JOIN:**

- 左テーブルの全データを保持
- 欠損を許容する場合

**RIGHT JOIN:**

- 右テーブルの全データを保持
- LEFT JOINの逆

### GROUP BYの使い分け

**単純集計:**

- COUNT, SUM, AVG
- カテゴリ別の統計

**ウィンドウ関数:**

- 行ごとの計算が必要
- ランキング、累積計算
- 元の行を保持

### サブクエリ vs JOIN

**サブクエリ:**

- 可読性が高い
- シンプルな条件

**JOIN:**

- パフォーマンスが良い
- 複雑な結合

## よくある落とし穴

1. **SELECT * の多用**

   - ❌ すべての列を取得
   - ✅ 必要な列のみ

2. **GROUP BYの誤り**

   - ❌ SELECT name, city, COUNT(*)
   - ✅ GROUP BYに非集計列を含める

3. **JOINの重複**

   - ❌ 1対多で重複が発生
   - ✅ DISTINCTまたはサブクエリ

4. **NULLの扱い**

   - ❌ column = NULL
   - ✅ column IS NULL

5. **インデックスの無視**

   - ❌ WHERE句で関数使用
   - ✅ インデックスが効く条件

## 検証ポイント

### 基本スキル

- [ ] SELECT, WHERE, ORDER BYを使える
- [ ] 集計関数を使える
- [ ] GROUP BYを理解している

### 応用スキル

- [ ] JOINを適切に使える
- [ ] サブクエリを書ける
- [ ] ウィンドウ関数を使える

### パフォーマンス

- [ ] EXPLAINで実行計画を確認できる
- [ ] インデックスを意識している
- [ ] 不要なデータを取得していない

## ベストプラクティス

### クエリの可読性

```sql
-- インデント、改行
SELECT
    u.name,
    u.email,
    COUNT(o.order_id) as order_count,
    SUM(o.amount) as total_amount
FROM
    users u
LEFT JOIN
    orders o ON u.user_id = o.user_id
WHERE
    u.created_at >= '2025-01-01'
GROUP BY
    u.user_id, u.name, u.email
HAVING
    COUNT(o.order_id) >= 5
ORDER BY
    total_amount DESC;
```

### パフォーマンス最適化

- インデックスの活用
- 必要な列のみ取得
- 適切なJOINの選択
- EXPLAIN での確認
- クエリキャッシュの活用

### データ品質確認

```sql
-- 重複チェック
SELECT user_id, COUNT(*)
FROM users
GROUP BY user_id
HAVING COUNT(*) > 1;

-- NULL チェック
SELECT COUNT(*) - COUNT(email) as null_count
FROM users;

-- データ範囲確認
SELECT MIN(created_at), MAX(created_at)
FROM orders;
```
