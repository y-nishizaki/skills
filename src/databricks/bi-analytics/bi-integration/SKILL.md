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

**接続手順**:
1. Power BI Desktop起動
2. データ取得 -> Azure -> Azure Databricks
3. サーバーホスト名とHTTP Path入力
4. AAD認証でサインイン
5. Unity Catalogからテーブル選択

**接続方法の比較**:

| 接続方法 | 認証 | セットアップ | セキュリティ | 用途 |
|---------|------|------------|------------|------|
| Azure AD | AAD | 簡単 | 高（SSO） | エンタープライズ推奨 |
| Personal Access Token | トークン | 中 | 中 | 開発・テスト |
| Service Principal | OAuth | 複雑 | 高 | 自動化・本番 |

### DirectQuery vs Import

**DirectQuery (推奨)**:
- リアルタイムデータ
- Databricksでクエリ実行
- Unity Catalogのアクセス制御適用
- 大規模データセット対応

**Import**:
- Power BIにデータコピー
- 高速だがリアルタイム性なし
- 1GBサイズ制限（Premium: 10GB）
- スケジュールリフレッシュ必要

**使い分けガイドライン**:
```
DirectQuery使用:
- データサイズ > 10GB
- リアルタイム性必要
- 頻繁な更新
- 行レベルセキュリティ必須

Import使用:
- データサイズ < 1GB
- 静的データ
- オフラインアクセス必要
- 高速なビジュアル操作
```

### パフォーマンス最適化

```sql
-- 集計テーブル作成 (Gold層)
CREATE OR REPLACE TABLE gold.sales_summary AS
SELECT
    date,
    region,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as order_count,
    AVG(amount) as avg_order_value
FROM silver.sales
GROUP BY date, region, product_category;

-- Power BIはこの集計テーブルを使用

-- インデックス最適化（Z-ORDER）
OPTIMIZE gold.sales_summary
ZORDER BY (date, region);

-- 統計情報更新
ANALYZE TABLE gold.sales_summary COMPUTE STATISTICS;
```

**DirectQueryパフォーマンステクニック**:

```dax
// 1. メジャーでサーバー側集計活用
Total Sales = SUM('sales_summary'[total_sales])

// 2. 計算列ではなくメジャー使用
// ❌ 悪い例: 計算列
Average = [total_sales] / [order_count]

// ✅ 良い例: メジャー
Average Order Value =
DIVIDE(SUM('sales'[total_sales]), SUM('sales'[order_count]))

// 3. フィルタコンテキスト最適化
Sales by Region =
CALCULATE(
    [Total Sales],
    KEEPFILTERS('dimension'[region])
)
```

### Power BI Service統合

```python
# Python スクリプトでリフレッシュ自動化
from databricks.sdk import WorkspaceClient
import requests

# Databricksでデータ更新
w = WorkspaceClient()
job_run = w.jobs.run_now(job_id=123)

# Power BI データセットリフレッシュトリガー
pbi_refresh_url = "https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
headers = {"Authorization": f"Bearer {access_token}"}
requests.post(pbi_refresh_url, headers=headers)
```

## Tableau連携

### JDBC接続

```
Server: your-workspace.cloud.databricks.com
Port: 443
HTTP Path: /sql/1.0/warehouses/abc123
Authentication: Personal Access Token
```

**Tableau Desktop接続手順**:
1. Databricksコネクタ選択
2. サーバー、HTTP Path入力
3. Personal Access Token認証
4. Unity Catalogからスキーマ選択

**Sparkle.jar配置** (カスタムコネクタ):
```bash
# Tableau用Spark ODBCドライバー
# Windows: C:\Program Files\Tableau\Drivers
# Mac: ~/Library/Tableau/Drivers

# SimbaSparkODBC.dmg インストール
```

### ライブ接続 vs 抽出

**ライブ接続**:
- Databricksに直接クエリ
- 常に最新データ
- パフォーマンスはウェアハウスに依存
- 行レベルセキュリティ適用

**抽出 (Extract)**:
- Tableauにデータキャッシュ
- オフライン分析可能
- 高速なビジュアル操作
- 増分リフレッシュ対応

**抽出最適化**:
```sql
-- 増分リフレッシュ用クエリ
SELECT *
FROM sales
WHERE updated_at >= :last_refresh_time;

-- 集計済みデータで抽出サイズ削減
CREATE OR REPLACE VIEW tableau_sales_extract AS
SELECT
    DATE_TRUNC('day', order_date) as date,
    customer_segment,
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales
GROUP BY 1, 2, 3;
```

### カスタムSQL活用

```sql
-- Tableau カスタムSQL
-- パラメーター活用
SELECT
    order_date,
    region,
    SUM(amount) as total_sales
FROM sales
WHERE order_date >= <Parameters.Start Date>
    AND order_date <= <Parameters.End Date>
    AND region IN (<Parameters.Region>)
GROUP BY order_date, region;

-- 初期SQLで接続設定
SET spark.sql.adaptive.enabled = true;
SET spark.databricks.delta.preview.enabled = true;

SELECT * FROM optimized_view;
```

### Tableau Server統合

```python
# Tableau Server 自動パブリッシュ
import tableauserverclient as TSC

# 接続
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name="automation",
    personal_access_token="token",
    site_id="site"
)
server = TSC.Server("https://tableau.company.com")

# Workbook パブリッシュ
with server.auth.sign_in(tableau_auth):
    wb = TSC.WorkbookItem(project_id="project123")
    wb = server.workbooks.publish(
        wb,
        "dashboard.twbx",
        mode="Overwrite"
    )
```

## Looker連携

### LookML モデル定義

```looker
# looker.model
connection: "databricks"

# Unity Catalog 3層構造対応
include: "/views/*.view.lkml"

explore: sales {
  from: sales
  sql_table_name: catalog.schema.sales ;;

  join: customers {
    type: left_outer
    sql_on: ${sales.customer_id} = ${customers.id} ;;
    relationship: many_to_one
  }

  join: products {
    type: left_outer
    sql_on: ${sales.product_id} = ${products.id} ;;
    relationship: many_to_one
  }
}
```

### ビュー定義

```looker
# views/sales.view.lkml
view: sales {
  sql_table_name: production.silver.sales ;;

  # ディメンション
  dimension: order_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.order_id ;;
  }

  dimension_group: order_date {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${TABLE}.order_date ;;
  }

  dimension: customer_id {
    type: string
    sql: ${TABLE}.customer_id ;;
  }

  # メジャー
  measure: total_sales {
    type: sum
    sql: ${TABLE}.amount ;;
    value_format_name: usd
  }

  measure: order_count {
    type: count
    drill_fields: [order_id, customer_id, amount]
  }

  measure: average_order_value {
    type: average
    sql: ${TABLE}.amount ;;
    value_format_name: usd_0
  }

  # 計算フィールド
  measure: revenue_per_customer {
    type: number
    sql: ${total_sales} / NULLIF(${customer_count}, 0) ;;
  }
}
```

### PDT（Persistent Derived Tables）

```looker
# 永続的派生テーブル
view: sales_daily_summary {
  derived_table: {
    sql_trigger_value: SELECT CURRENT_DATE() ;;
    indexes: ["date", "region"]
    sql:
      SELECT
        DATE(order_date) as date,
        region,
        product_category,
        SUM(amount) as total_sales,
        COUNT(*) as order_count,
        COUNT(DISTINCT customer_id) as unique_customers
      FROM ${sales.SQL_TABLE_NAME}
      GROUP BY 1, 2, 3
    ;;
  }

  dimension: date {
    type: date
    sql: ${TABLE}.date ;;
  }

  measure: total_sales {
    type: sum
    sql: ${TABLE}.total_sales ;;
  }
}
```

## その他BIツール統合

### Qlik Sense

```
# ODBC接続設定
Driver: Simba Spark ODBC Driver
Host: your-workspace.cloud.databricks.com
Port: 443
HTTPPath: /sql/1.0/warehouses/abc123
AuthMech: 3
UID: token
PWD: <personal-access-token>
```

### Metabase

```yaml
# Metabase設定
database-type: spark
host: your-workspace.cloud.databricks.com
port: 443
dbname: default
user: token
password: <personal-access-token>
additional-options:
  httpPath: /sql/1.0/warehouses/abc123
  ssl: 1
  AuthMech: 3
```

### Apache Superset

```python
# SQLAlchemy接続文字列
from sqlalchemy import create_engine

connection_string = (
    "databricks://token:<access-token>@"
    "your-workspace.cloud.databricks.com:443/default"
    "?http_path=/sql/1.0/warehouses/abc123"
)

engine = create_engine(connection_string)
```

## セキュリティ

### Personal Access Token

```python
# トークン作成
# Settings -> User Settings -> Access Tokens

# 権限スコープ:
# - sql/query: クエリ実行のみ
# - all: 全権限

# トークンライフタイム設定
# 推奨: 90日（自動ローテーション設定）

# トークンのベストプラクティス:
# 1. 環境変数で管理
import os
token = os.getenv("DATABRICKS_TOKEN")

# 2. Secrets Manager使用（本番）
# Azure Key Vault / AWS Secrets Manager

# 3. 定期的なローテーション
```

### Service Principal認証

```python
# Azure Service Principal（推奨）
# アプリケーション自動化用

# 設定:
# 1. Azure ADでService Principal作成
# 2. Databricks Workspace権限付与
# 3. Unity Catalog権限設定

# OAuth2認証フロー
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    client_secret="<client-secret>"
)

# Databricks SDK
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host="https://your-workspace.cloud.databricks.com",
    azure_client_id="<client-id>",
    azure_client_secret="<client-secret>",
    azure_tenant_id="<tenant-id>"
)
```

### Unity Catalog統合

```sql
-- BIユーザーグループに権限付与
CREATE GROUP bi_users;
CREATE GROUP bi_power_users;

-- 基本読み取り権限
GRANT USE CATALOG production TO bi_users;
GRANT USE SCHEMA production.gold TO bi_users;
GRANT SELECT ON SCHEMA production.gold TO bi_users;

-- パワーユーザー権限
GRANT SELECT ON SCHEMA production.silver TO bi_power_users;

-- 行レベルセキュリティ
CREATE FUNCTION filter_by_region(user_name STRING, user_region STRING)
RETURNS BOOLEAN
RETURN user_region IN (
    SELECT region FROM user_permissions WHERE user = user_name
);

CREATE VIEW sales_filtered AS
SELECT *
FROM sales
WHERE filter_by_region(current_user(), region);

-- 列レベルセキュリティ（マスキング）
CREATE FUNCTION mask_email(email STRING, user_name STRING)
RETURNS STRING
RETURN CASE
    WHEN is_account_group_member(user_name, 'admins') THEN email
    ELSE CONCAT(LEFT(email, 3), '***@***')
END;

CREATE VIEW customers_masked AS
SELECT
    customer_id,
    customer_name,
    mask_email(email, current_user()) as email
FROM customers;
```

### 監査ログ

```sql
-- BI接続の監査
SELECT
    user_identity.email as user,
    request_params.sql_warehouse_id,
    request_params.statement_text,
    response.result,
    event_time
FROM system.access.audit
WHERE action_name = 'executeStatement'
    AND event_time >= current_date() - INTERVAL 7 DAYS
    AND request_params.sql_warehouse_id = '<warehouse-id>'
ORDER BY event_time DESC;

-- 異常アクセス検出
SELECT
    user_identity.email,
    COUNT(*) as query_count,
    COUNT(DISTINCT request_params.table_name) as unique_tables
FROM system.access.audit
WHERE action_name = 'executeStatement'
    AND event_time >= current_timestamp() - INTERVAL 1 HOUR
GROUP BY user_identity.email
HAVING query_count > 100;  -- 1時間に100クエリ以上
```

## パフォーマンス最適化

### 集計層設計

```sql
-- Gold層: BI専用集計テーブル
-- 日次集計
CREATE OR REPLACE TABLE gold.sales_daily AS
SELECT
    date,
    region,
    product_category,
    customer_segment,
    SUM(amount) as total_sales,
    COUNT(*) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(amount) as avg_order_value
FROM silver.sales
GROUP BY ALL;

-- 月次集計
CREATE OR REPLACE TABLE gold.sales_monthly AS
SELECT
    DATE_TRUNC('month', date) as month,
    region,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as order_count
FROM silver.sales
GROUP BY ALL;

-- マテリアライズドビュー（自動更新）
CREATE MATERIALIZED VIEW gold.sales_realtime AS
SELECT
    DATE_TRUNC('hour', order_timestamp) as hour,
    region,
    SUM(amount) as total_sales
FROM silver.sales_stream
GROUP BY ALL;
```

### キャッシュ戦略

```sql
-- 頻繁アクセステーブルをキャッシュ
CACHE SELECT * FROM gold.sales_summary;

-- BIクエリ用ビュー
CREATE VIEW bi_optimized_sales AS
SELECT
    s.*,
    c.customer_name,
    c.segment,
    p.product_name,
    p.category
FROM gold.sales_summary s
JOIN gold.dim_customers c ON s.customer_id = c.id
JOIN gold.dim_products p ON s.product_id = p.id;

-- Query History分析で頻出パターン特定
SELECT
    statement_text,
    COUNT(*) as frequency,
    AVG(total_duration_ms) as avg_duration_ms
FROM system.query.history
WHERE warehouse_id = '<warehouse-id>'
    AND start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY statement_text
ORDER BY frequency DESC
LIMIT 20;
```

### SQLウェアハウス設定

```json
{
  "name": "BI Analytics Warehouse",
  "cluster_size": "Large",
  "min_num_clusters": 2,
  "max_num_clusters": 10,
  "auto_stop_mins": 30,
  "enable_photon": true,
  "enable_serverless_compute": true,
  "spot_instance_policy": "RELIABILITY_OPTIMIZED",
  "tags": {
    "purpose": "bi-analytics",
    "cost-center": "analytics"
  }
}
```

## トラブルシューティング

### 接続エラー

```python
# 診断チェックリスト
# 1. ネットワーク接続確認
import socket
try:
    socket.create_connection(("your-workspace.cloud.databricks.com", 443), timeout=5)
    print("✓ Network OK")
except:
    print("✗ Network Error")

# 2. 認証確認
import requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://your-workspace.cloud.databricks.com/api/2.0/clusters/list",
    headers=headers
)
print(f"Auth: {response.status_code}")

# 3. ウェアハウス稼働確認
w = WorkspaceClient()
warehouse = w.warehouses.get(id="warehouse-id")
print(f"Status: {warehouse.state}")
```

### パフォーマンス問題

```sql
-- BIツールからの遅いクエリ特定
SELECT
    query_id,
    LEFT(statement_text, 100) as query_preview,
    user_name,
    total_duration_ms / 1000 as duration_sec,
    rows_produced,
    read_bytes / 1024 / 1024 as mb_read
FROM system.query.history
WHERE warehouse_id = '<bi-warehouse-id>'
    AND start_time >= current_date() - INTERVAL 1 DAYS
    AND total_duration_ms > 10000
ORDER BY total_duration_ms DESC
LIMIT 20;

-- 解決策
-- 1. 集計テーブル作成
-- 2. Z-ORDER最適化
-- 3. パーティショニング見直し
```

## ベストプラクティス

1. **集計テーブル使用** - Gold層で事前集計
   - 日次/月次サマリー
   - ディメンション結合済み
   - Z-ORDER最適化

2. **適切な接続モード** - リアルタイム性要件に応じて選択
   - リアルタイム: DirectQuery/Live
   - バッチ: Import/Extract

3. **Unity Catalog活用** - 一元的なアクセス制御
   - グループベース権限管理
   - 行/列レベルセキュリティ
   - 監査ログ確認

4. **Photonウェアハウス** - BIクエリを高速化
   - 集計クエリ: 3-8x高速化
   - JOIN: 5-12x高速化

5. **キャパシティ計画**
   - ピーク時間帯の同時ユーザー数測定
   - ウェアハウスサイズ適切化
   - Auto-scaling設定

6. **モニタリング**
   - Query History定期レビュー
   - 遅いクエリの最適化
   - コスト分析

## まとめ

Databricksは主要BIツールと標準接続をサポート。Unity CatalogとPhotonで、セキュアかつ高速なBI分析を実現。適切な集計層設計とセキュリティ設定で、エンタープライズグレードのBI環境を構築。
