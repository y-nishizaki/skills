---
name: "Databricks Unity Catalog"
description: "Unity Catalogによる統合データガバナンス。RBAC、アクセス制御、メタデータ管理、リネージ追跡、監査ログ"
---

# Databricks Unity Catalog

## このスキルを使う場面

- データガバナンスを強化したい
- アクセス制御を一元管理したい
- データリネージを追跡したい
- ワークスペース間でデータ共有したい
- コンプライアンス要件を満たしたい

## 3層ネームスペース

```
catalog.schema.table
  ↓      ↓      ↓
 main  finance customers
```

```sql
-- カタログ作成
CREATE CATALOG sales_data;

-- スキーマ作成
CREATE SCHEMA sales_data.staging;

-- テーブル作成
CREATE TABLE sales_data.staging.orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2)
) USING DELTA
LOCATION 's3://bucket/sales/orders/';
```

## RBAC (Role-Based Access Control)

### グループ管理

```sql
-- アカウントレベルでグループ作成
CREATE GROUP finance_admins;
CREATE GROUP finance_users;
CREATE GROUP finance_readonly;

-- ユーザー追加
ALTER GROUP finance_users ADD USER 'user@example.com';
```

### 権限付与

```sql
-- カタログレベル
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG sales_data TO finance_admins;
GRANT USE CATALOG, USE SCHEMA ON CATALOG sales_data TO finance_users;

-- スキーマレベル
GRANT CREATE TABLE, USE SCHEMA ON SCHEMA sales_data.staging TO finance_admins;
GRANT SELECT, USE SCHEMA ON SCHEMA sales_data.staging TO finance_readonly;

-- テーブルレベル
GRANT SELECT, MODIFY ON TABLE sales_data.staging.orders TO finance_users;
GRANT SELECT ON TABLE sales_data.staging.orders TO finance_readonly;

-- 列レベル
GRANT SELECT (order_id, amount) ON TABLE sales_data.staging.orders TO analyst_group;
```

### 動的ビュー (Row/Column Level Security)

```sql
-- 行レベルセキュリティ
CREATE VIEW sales_data.staging.orders_filtered AS
SELECT * FROM sales_data.staging.orders
WHERE
    CASE
        WHEN is_member('finance_admins') THEN TRUE
        WHEN is_member('regional_managers') THEN region = current_user_region()
        ELSE FALSE
    END;

-- 列レベルマスキング
CREATE VIEW sales_data.staging.customers_masked AS
SELECT
    customer_id,
    name,
    CASE
        WHEN is_member('pii_viewers') THEN email
        ELSE '***@***.***'
    END AS email,
    city
FROM sales_data.staging.customers;
```

## オーナーシップ

```sql
-- オーナーシップをグループに設定
ALTER CATALOG sales_data OWNER TO finance_admins;
ALTER SCHEMA sales_data.staging OWNER TO finance_admins;
ALTER TABLE sales_data.staging.orders OWNER TO finance_data_owners;
```

## データリネージ

```python
# Unity CatalogのリネージはUIで自動表示
# 以下のAPIで取得可能

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# テーブルのリネージ情報
lineage = w.lineage.get_table_lineage(
    table_name="sales_data.staging.orders"
)

# 上流・下流の依存関係確認
upstream_tables = lineage.upstream_tables
downstream_tables = lineage.downstream_tables
```

## メタデータ管理

```sql
-- テーブル説明
COMMENT ON TABLE sales_data.staging.orders IS 'Daily orders from e-commerce platform';

-- 列説明
ALTER TABLE sales_data.staging.orders ALTER COLUMN amount COMMENT 'Order amount in USD';

-- カスタムタグ
ALTER TABLE sales_data.staging.orders SET TAGS ('pii' = 'true', 'retention' = '7years');

-- メタデータ検索
SHOW TABLES IN sales_data.staging;
DESCRIBE EXTENDED sales_data.staging.orders;
```

## 監査ログ

```sql
-- システムテーブルで監査ログ確認
SELECT
    event_time,
    user_identity,
    action_name,
    request_params.full_name_arg as table_name
FROM system.access.audit
WHERE action_name IN ('createTable', 'readTable', 'modifyTable')
    AND event_date >= current_date() - INTERVAL 7 DAYS
ORDER BY event_time DESC;
```

## Delta Sharing (外部共有)

```sql
-- 共有の作成
CREATE SHARE my_share;

-- テーブルを共有に追加
ALTER SHARE my_share ADD TABLE sales_data.staging.orders;

-- 受信者に付与
GRANT SELECT ON SHARE my_share TO RECIPIENT `partner@external.com`;
```

## ベストプラクティス

1. **グループベースRBAC** - 個人でなくグループに権限付与
2. **カタログレベルオーナーシップ** - 責任を明確化
3. **最小権限の原則** - 必要最小限のアクセスのみ
4. **定期的な監査** - システムテーブルで権限レビュー
5. **タグ付け** - メタデータでデータ分類

## まとめ

Unity Catalogは3層ネームスペース、RBAC、リネージ、監査ログで統合データガバナンスを実現。ワークスペース間の共有とDelta Sharingで、セキュアなデータコラボレーションが可能。
