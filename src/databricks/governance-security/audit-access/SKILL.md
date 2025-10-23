---
name: "Databricks監査ログ・アクセス権限設計"
description: "監査ログ分析とアクセス権限設計。システムテーブル、セキュリティベストプラクティス、コンプライアンス、権限レビュー"
---

# Databricks監査ログ・アクセス権限設計

## このスキルを使う場面

- 監査ログを分析したい
- アクセス権限を設計・レビューしたい
- コンプライアンス要件を満たしたい
- セキュリティインシデントを調査したい

## システムテーブルによる監査

### アクセス監査

```sql
-- テーブルアクセス履歴
SELECT
    event_time,
    user_identity.email as user,
    action_name,
    request_params.full_name_arg as resource,
    response.status_code
FROM system.access.audit
WHERE action_name IN ('createTable', 'readTable', 'deleteTable')
    AND event_date >= current_date() - INTERVAL 30 DAYS
ORDER BY event_time DESC;

-- 失敗したアクセス試行
SELECT
    event_time,
    user_identity.email,
    action_name,
    request_params,
    response.error_message
FROM system.access.audit
WHERE response.status_code >= 400
    AND event_date >= current_date() - INTERVAL 7 DAYS;
```

### 権限変更履歴

```sql
SELECT
    event_time,
    user_identity.email as granter,
    action_name,
    request_params.securable_full_name as object,
    request_params.changes
FROM system.access.audit
WHERE action_name IN ('grant', 'revoke')
ORDER BY event_time DESC;
```

## アクセス権限設計

### 役割ベース設計

```sql
-- データエンジニア向け
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG data_eng TO data_engineers;
GRANT ALL PRIVILEGES ON SCHEMA data_eng.bronze TO data_engineers;
GRANT ALL PRIVILEGES ON SCHEMA data_eng.silver TO data_engineers;
GRANT ALL PRIVILEGES ON SCHEMA data_eng.gold TO data_engineers;

-- データアナリスト向け
GRANT USE CATALOG, USE SCHEMA ON CATALOG data_eng TO data_analysts;
GRANT SELECT ON SCHEMA data_eng.gold TO data_analysts;

-- データサイエンティスト向け
GRANT USE CATALOG, USE SCHEMA ON CATALOG data_eng TO data_scientists;
GRANT SELECT ON SCHEMA data_eng.silver TO data_scientists;
GRANT SELECT ON SCHEMA data_eng.gold TO data_scientists;
GRANT CREATE TABLE ON SCHEMA ml.experiments TO data_scientists;
```

### 環境分離

```sql
-- 開発環境
CREATE CATALOG dev;
GRANT ALL PRIVILEGES ON CATALOG dev TO developers;

-- ステージング環境
CREATE CATALOG staging;
GRANT SELECT ON CATALOG staging TO developers;
GRANT ALL PRIVILEGES ON CATALOG staging TO staging_admins;

-- 本番環境
CREATE CATALOG prod;
GRANT SELECT ON CATALOG prod TO data_analysts;
GRANT ALL PRIVILEGES ON CATALOG prod TO prod_admins;
```

## セキュリティベストプラクティス

### 最小権限の原則

```sql
-- ❌ 過剰な権限
GRANT ALL PRIVILEGES ON CATALOG sales TO analytics_team;

-- ✅ 必要最小限
GRANT USE CATALOG ON CATALOG sales TO analytics_team;
GRANT USE SCHEMA ON SCHEMA sales.reports TO analytics_team;
GRANT SELECT ON TABLE sales.reports.monthly_summary TO analytics_team;
```

### PIIデータの保護

```sql
-- マスキングビュー
CREATE VIEW customers_masked AS
SELECT
    customer_id,
    name,
    CASE
        WHEN is_member('pii_admins') THEN email
        ELSE regexp_replace(email, '(.{3}).*(@.*)', '$1***$2')
    END AS email,
    city
FROM customers;

GRANT SELECT ON customers_masked TO customer_service;
```

## 定期監査レポート

```python
# 監査レポート生成
def generate_audit_report(days=30):
    query = f"""
    SELECT
        user_identity.email as user,
        action_name,
        COUNT(*) as action_count,
        MAX(event_time) as last_access
    FROM system.access.audit
    WHERE event_date >= current_date() - INTERVAL {days} DAYS
    GROUP BY user_identity.email, action_name
    ORDER BY action_count DESC
    """
    
    df = spark.sql(query)
    df.write.format("delta").mode("overwrite").save("/mnt/audit-reports/")
    
    # アラート: 異常なアクセスパターン
    suspicious = df.filter(col("action_count") > 10000)
    if suspicious.count() > 0:
        send_alert("Suspicious access pattern detected", suspicious)

# 定期実行
generate_audit_report(30)
```

## コンプライアンス

### GDPR対応

```sql
-- データ削除リクエスト対応
DELETE FROM customers WHERE customer_id = 12345;

-- 削除履歴記録
INSERT INTO deletion_log
VALUES (12345, current_timestamp(), current_user());

-- アクセス履歴の確認
SELECT * FROM system.access.audit
WHERE request_params.full_name_arg LIKE '%customers%'
    AND user_identity.email = 'user@example.com';
```

## まとめ

システムテーブルによる監査ログ分析と、役割ベースの権限設計により、セキュアでコンプライアンスに準拠したデータガバナンスを実現。定期的な権限レビューと監査レポートで、継続的な改善を行う。
