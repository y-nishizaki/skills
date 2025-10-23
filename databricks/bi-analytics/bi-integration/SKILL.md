---
name: "Databricks BIツール統合"
description: "Power BI、Tableau、Looker等のBIツール統合。JDBC/ODBC接続、パフォーマンス最適化、セキュリティ設定"
---

# Databricks BIツール統合

## Power BI連携

### 接続設定

```
サーバー: adb-1234567890.azuredatabricks.net
HTTP Path: /sql/1.0/warehouses/abc123
認証: Azure Active Directory
```

### DirectQuery vs Import

**DirectQuery (推奨)**:
- リアルタイムデータ
- Databricksでクエリ実行
- Unity Catalogのアクセス制御適用

**Import**:
- Power BIにデータコピー
- 高速だがリアルタイム性なし

### パフォーマンス最適化

```sql
-- 集計テーブル作成 (Gold層)
CREATE OR REPLACE TABLE gold.sales_summary AS
SELECT
    date,
    region,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as order_count
FROM silver.sales
GROUP BY date, region, product_category;

-- Power BIはこの集計テーブルを使用
```

## Tableau連携

### JDBC接続

```
Server: your-workspace.cloud.databricks.com
Port: 443
HTTP Path: /sql/1.0/warehouses/abc123
Authentication: Personal Access Token
```

### ライブ接続 vs 抽出

**ライブ接続**:
- Databricksに直接クエリ
- 常に最新データ

**抽出 (Extract)**:
- Tableauにデータキャッシュ
- オフライン分析可能

## Looker連携

```looker
# looker.model
connection: "databricks"

explore: sales {
  from: silver.sales
  join: customers {
    sql_on: ${sales.customer_id} = ${customers.id} ;;
  }
}
```

## セキュリティ

### Personal Access Token

```python
# トークン作成
# Settings -> User Settings -> Access Tokens

# 権限スコープ:
# - sql/query: クエリ実行のみ
# - all: 全権限
```

### Unity Catalog統合

```sql
-- BIユーザーグループに権限付与
GRANT SELECT ON SCHEMA gold TO bi_users;

-- 行レベルセキュリティ
CREATE VIEW sales_filtered AS
SELECT * FROM sales
WHERE region IN (SELECT region FROM user_regions WHERE user = current_user());
```

## ベストプラクティス

1. **集計テーブル使用** - Gold層で事前集計
2. **適切な接続モード** - リアルタイム性要件に応じて選択
3. **Unity Catalog活用** - 一元的なアクセス制御
4. **Photonウェアハウス** - BIクエリを高速化

## まとめ

Databricksは主要BIツールと標準接続をサポート。Unity CatalogとPhotonで、セキュアかつ高速なBI分析を実現。
