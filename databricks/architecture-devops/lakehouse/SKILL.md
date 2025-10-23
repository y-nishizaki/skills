---
name: "Databricks Lakehouseアーキテクチャ"
description: "Lakehouseアーキテクチャの理解。データレイク+ウェアハウス統合、メダリオンアーキテクチャ、Delta Lake、Unity Catalog"
---

# Databricks Lakehouseアーキテクチャ

## Lakehouse概念

**データレイク + データウェアハウス = Lakehouse**

### 従来アーキテクチャの課題

**データレイク**:
- ✅ 大容量・低コスト
- ❌ ACIDトランザクションなし
- ❌ クエリパフォーマンス低い

**データウェアハウス**:
- ✅ 高速クエリ
- ✅ ACIDトランザクション
- ❌ 高コスト
- ❌ スケーラビリティ制限

**Lakehouse**:
- ✅ 両方の利点を統合
- ✅ Delta Lakeで信頼性
- ✅ Unity Catalogでガバナンス

## メダリオンアーキテクチャ

```
Raw Data → Bronze → Silver → Gold → BI/ML
           (生)    (整形)   (集計)
```

### Bronze層

```python
# 生データ保存
@dlt.table
def bronze_events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/mnt/raw/")
```

**特徴**:
- ソースデータをそのまま保存
- 監査トレール
- データリプレイ可能

### Silver層

```python
# クレンジング・統合
@dlt.table
@dlt.expect_or_drop("valid_user", "user_id IS NOT NULL")
def silver_events():
    return dlt.read_stream("bronze_events") \
        .filter(col("status") == "active") \
        .withColumn("processed_at", current_timestamp())
```

**特徴**:
- 重複削除
- データ品質検証
- 型変換・標準化

### Gold層

```python
# ビジネス集計
@dlt.table
def gold_daily_metrics():
    return dlt.read("silver_events") \
        .groupBy("date", "category") \
        .agg(count("*").alias("event_count"))
```

**特徴**:
- ビジネスレベル集計
- ダッシュボード用
- ML特徴量

## Delta Lake統合

```sql
-- ACID トランザクション
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- タイムトラベル
SELECT * FROM my_table VERSION AS OF 10;
SELECT * FROM my_table TIMESTAMP AS OF '2025-01-01';
```

## Unity Catalog統合

```sql
-- 3層ネームスペース
CREATE CATALOG lakehouse;
CREATE SCHEMA lakehouse.bronze;
CREATE SCHEMA lakehouse.silver;
CREATE SCHEMA lakehouse.gold;

-- アクセス制御
GRANT SELECT ON SCHEMA lakehouse.gold TO analysts;
GRANT ALL PRIVILEGES ON SCHEMA lakehouse.bronze TO engineers;
```

## ベストプラクティス

1. **メダリオン採用** - データ品質段階的向上
2. **Delta Lake使用** - 全テーブルDelta形式
3. **Unity Catalog** - 統合ガバナンス
4. **増分処理** - ストリーミング/CDC活用
5. **自動化** - DLTパイプラインで宣言的定義

## まとめ

Lakehouseは、データレイクの柔軟性・コスト効率とデータウェアハウスの信頼性・パフォーマンスを統合。メダリオンアーキテクチャ、Delta Lake、Unity Catalogで、モダンデータプラットフォームを実現。
