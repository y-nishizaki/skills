---
name: "Databricks Delta Lake運用"
description: "Delta Lakeの運用管理。OPTIMIZE、VACUUM、Z-ORDER、統計収集、パフォーマンス監視、メンテナンスベストプラクティス"
---

# Databricks Delta Lake運用

## このスキルを使う場面

- Delta Lakeテーブルの最適化が必要
- Small File Problemを解決したい
- ストレージコストを削減したい
- クエリパフォーマンスを向上させたい
- 定期メンテナンスを自動化したい

## 主要な運用コマンド

### OPTIMIZE (ファイル圧縮)

```sql
-- 基本的な最適化
OPTIMIZE my_table;

-- パーティション指定
OPTIMIZE my_table WHERE date = '2025-01-01';

-- Z-ORDER による多次元クラスタリング
OPTIMIZE my_table ZORDER BY (user_id, timestamp);
```

**効果**:
- 小さなファイルを結合して128MB-1GB の最適サイズに
- 読み込みパフォーマンス向上
- データスキッピング効率化

### VACUUM (古いファイル削除)

```sql
-- デフォルト保持期間 (7日)
VACUUM my_table;

-- カスタム保持期間
VACUUM my_table RETAIN 168 HOURS;

-- DRY RUN (削除対象を確認)
VACUUM my_table DRY RUN;
```

**注意**:
- タイムトラベルとのトレードオフ
- 保持期間外のバージョンは復元不可
- 実行前に必ずDRY RUNで確認

### ANALYZE TABLE (統計収集)

```sql
-- テーブル統計
ANALYZE TABLE my_table COMPUTE STATISTICS;

-- 列統計
ANALYZE TABLE my_table COMPUTE STATISTICS FOR ALL COLUMNS;

-- 特定列のみ
ANALYZE TABLE my_table COMPUTE STATISTICS FOR COLUMNS id, name, age;
```

## 定期メンテナンススケジュール

### 日次

```python
# OPTIMIZEの実行
spark.sql("OPTIMIZE my_table WHERE date = current_date()")
```

### 週次

```python
# OPTIMIZE + Z-ORDER
spark.sql("OPTIMIZE my_table ZORDER BY (customer_id, order_date)")
```

### 月次

```python
# VACUUM実行
spark.sql("VACUUM my_table RETAIN 168 HOURS")

# 統計収集
spark.sql("ANALYZE TABLE my_table COMPUTE STATISTICS FOR ALL COLUMNS")
```

## 自動最適化の設定

```sql
-- テーブルレベルで自動最適化を有効化
ALTER TABLE my_table SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

**Auto Optimize の2つのモード**:
- **Optimized Writes**: 書き込み時に最適なファイルサイズに調整
- **Auto Compaction**: 小さなファイルを自動的に結合

## パフォーマンス監視

```sql
-- テーブル詳細
DESCRIBE DETAIL my_table;

-- ファイル数・サイズ確認
SELECT COUNT(*), AVG(size_in_bytes), MIN(size_in_bytes), MAX(size_in_bytes)
FROM (
  SELECT input_file_name() as file, COUNT(*) as rows
  FROM my_table
  GROUP BY input_file_name()
) t
JOIN delta.`/path/to/table/_delta_log/` ON ...;
```

## ベストプラクティス

1. **定期的なOPTIMIZE** - 週次でZ-ORDER含む
2. **適切なVACUUM保持期間** - コンプライアンス要件を考慮
3. **Auto Optimize有効化** - 新規テーブルはデフォルトで有効化
4. **統計の更新** - 大きなデータ変更後に実行
5. **パーティション戦略** - 1パーティション1GB以上を維持

## まとめ

Delta Lakeの運用は、OPTIMIZE、VACUUM、ANALYZE TABLEの3つの定期メンテナンスが鍵。Auto Optimizeを活用し、監視を怠らないことで、高パフォーマンスなLakehouseを維持できる。
