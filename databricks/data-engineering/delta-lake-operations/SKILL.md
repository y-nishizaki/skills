---
name: "Databricks Delta Lake運用"
description: "Delta Lakeの運用・最適化。OPTIMIZE、VACUUM、Z-ORDER、統計収集、パフォーマンス監視、メンテナンスベストプラクティス。基本操作は別スキル参照"
---

# Databricks Delta Lake運用

## このスキルを使う場面

- Delta Lakeテーブルの最適化が必要
- Small File Problemを解決したい
- ストレージコストを削減したい
- クエリパフォーマンスを向上させたい
- 定期メンテナンスを自動化したい
- データスキッピング効率を最大化したい

**このスキルでカバーする範囲:**
- 運用・メンテナンスコマンド
- パフォーマンス最適化
- モニタリングとトラブルシューティング

**基本操作については:**
`databricks/fundamentals/delta-lake-basics/SKILL.md` を参照

## 主要な運用コマンド

### OPTIMIZE (ファイル圧縮)

Small file problemを解決し、パフォーマンスを向上：

```sql
-- 基本的な最適化
OPTIMIZE my_table;

-- パーティション指定
OPTIMIZE my_table WHERE date = '2025-01-01';

-- Z-ORDER による多次元クラスタリング
OPTIMIZE my_table ZORDER BY (user_id, timestamp);

-- パス指定
OPTIMIZE delta.`/path/to/delta-table`;
```

**効果:**
- 小さなファイルを結合して128MB-1GB の最適サイズに
- 読み込みパフォーマンス向上
- データスキッピング効率化
- クエリ時間短縮

**実行タイミング:**
- 大量の小さな書き込み後
- データ取り込み処理後
- 定期的なメンテナンス（日次・週次）

### Z-ORDER クラスタリング

頻繁にフィルタされる列でデータをクラスタリング：

```python
# Z-ORDERで最適化（複数列）
spark.sql("""
    OPTIMIZE my_table
    ZORDER BY (customer_id, order_date)
""")
```

**Z-ORDER のメリット:**
- 複数列でのデータスキッピング向上
- フィルタクエリの高速化
- I/O削減

**使用推奨列:**
- カーディナリティの高い列（例: user_id, customer_id）
- WHERE句で頻繁に使われる列
- 結合キー
- 最大4列程度を推奨

**非推奨列:**
- 低カーディナリティ列（例: gender, status）
- 常に一緒にクエリされない列

### VACUUM（古いファイルの削除）

タイムトラベルで不要になった古いデータファイルを削除：

```sql
-- デフォルト保持期間 (7日)
VACUUM my_table;

-- カスタム保持期間
VACUUM my_table RETAIN 168 HOURS;  -- 7日

-- DRY RUN (削除対象を確認)
VACUUM my_table DRY RUN;
```

**Python API:**

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")
delta_table.vacuum(168)  # 168時間（7日）
```

**注意:**
- タイムトラベルとのトレードオフ
- 保持期間外のバージョンは復元不可
- 実行前に必ずDRY RUNで確認
- コンプライアンス要件を考慮

**実行タイミング:**
- 月次または週次
- ストレージコストが気になる場合
- 監査要件を満たしつつ不要データを削除

### ANALYZE TABLE (統計収集)

テーブル統計を収集してクエリ最適化：

```sql
-- テーブル統計
ANALYZE TABLE my_table COMPUTE STATISTICS;

-- 列統計
ANALYZE TABLE my_table COMPUTE STATISTICS FOR ALL COLUMNS;

-- 特定列のみ
ANALYZE TABLE my_table COMPUTE STATISTICS FOR COLUMNS id, name, age;
```

**実行タイミング:**
- 大きなデータ変更後
- テーブルサイズが大きく変わった後
- クエリパフォーマンスが悪化した場合

## データスキッピング

### 自動統計収集

Delta Lakeは最初の32列について自動的に統計を収集：

- 最小値（min）
- 最大値（max）
- NULL数（nullCount）
- レコード数（count）

```python
# 統計は自動的に収集される（設定不要）
# クエリ時に自動的にデータスキッピング

# 統計情報を確認
spark.sql("DESCRIBE DETAIL my_table").show()
```

### データスキッピングの効果確認

```python
# クエリ実行前にメトリクスを有効化
spark.conf.set("spark.databricks.delta.stats.skipping", "true")

# クエリ実行
df = spark.sql("SELECT * FROM my_table WHERE user_id = 12345")

# スキップされたファイル数を確認
# Spark UIでメトリクスを確認
```

### Z-ORDERとデータスキッピング

Z-ORDERは、複数列に対するデータスキッピングを最適化：

```python
# 例: user_id と timestamp でよくフィルタする場合
spark.sql("OPTIMIZE my_table ZORDER BY (user_id, timestamp)")

# クエリ時に効果を発揮
spark.sql("""
    SELECT * FROM my_table
    WHERE user_id = 12345
      AND timestamp BETWEEN '2025-01-01' AND '2025-01-31'
""")
# Z-ORDERにより、関係ないファイルを大幅にスキップ
```

## 自動最適化の設定

### Auto Optimize の有効化

```sql
-- テーブルレベルで自動最適化を有効化
ALTER TABLE my_table SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

**Auto Optimize の2つのモード:**

1. **Optimized Writes**
   - 書き込み時に最適なファイルサイズに調整
   - 小さなファイルの生成を防止

2. **Auto Compaction**
   - 小さなファイルを自動的に結合
   - バックグラウンドで実行

**推奨:**
新規テーブルはデフォルトで有効化

## 定期メンテナンススケジュール

### 日次メンテナンス

```python
# OPTIMIZEの実行（当日分のみ）
spark.sql("OPTIMIZE my_table WHERE date = current_date()")
```

### 週次メンテナンス

```python
# OPTIMIZE + Z-ORDER（全体またはパーティション）
spark.sql("OPTIMIZE my_table ZORDER BY (customer_id, order_date)")
```

### 月次メンテナンス

```python
# VACUUM実行
spark.sql("VACUUM my_table RETAIN 168 HOURS")

# 統計収集
spark.sql("ANALYZE TABLE my_table COMPUTE STATISTICS FOR ALL COLUMNS")
```

### ワークフローの自動化例

```python
from datetime import datetime

def daily_maintenance():
    """日次メンテナンス"""
    tables = ["sales", "customers", "products"]

    for table in tables:
        # 当日分を最適化
        spark.sql(f"""
            OPTIMIZE {table}
            WHERE date = current_date()
        """)
        print(f"✓ {table}: 日次OPTIMIZE完了")

def weekly_maintenance():
    """週次メンテナンス"""
    # 重要テーブルのZ-ORDER最適化
    spark.sql("OPTIMIZE sales ZORDER BY (customer_id, order_date)")
    spark.sql("OPTIMIZE page_views ZORDER BY (user_id, timestamp)")
    print("✓ 週次OPTIMIZE完了")

def monthly_maintenance():
    """月次メンテナンス"""
    tables = ["sales", "customers", "products", "page_views"]

    for table in tables:
        # VACUUM（7日より古いファイルを削除）
        spark.sql(f"VACUUM {table} RETAIN 168 HOURS")
        print(f"✓ {table}: VACUUM完了")

        # 統計収集
        spark.sql(f"ANALYZE TABLE {table} COMPUTE STATISTICS FOR ALL COLUMNS")
        print(f"✓ {table}: 統計収集完了")

# 実行
if datetime.now().day == 1:  # 月初
    monthly_maintenance()
elif datetime.now().weekday() == 0:  # 月曜日
    weekly_maintenance()
else:
    daily_maintenance()
```

## パフォーマンス監視

### テーブル詳細の確認

```sql
-- テーブル詳細
DESCRIBE DETAIL my_table;
```

**確認項目:**
- `numFiles`: ファイル数（多すぎる場合はOPTIMIZE必要）
- `sizeInBytes`: テーブルサイズ
- `minReaderVersion`, `minWriterVersion`: Delta Lake バージョン

### ファイル数とサイズの監視

```python
# テーブル詳細を取得
detail = spark.sql("DESCRIBE DETAIL my_table").collect()[0]

num_files = detail['numFiles']
size_gb = detail['sizeInBytes'] / (1024**3)

print(f"ファイル数: {num_files}")
print(f"テーブルサイズ: {size_gb:.2f} GB")

# Small File Problem の検出
if num_files > 10000:
    print("⚠️ 警告: ファイル数が多すぎます。OPTIMIZE を実行してください。")

avg_file_size_mb = (detail['sizeInBytes'] / num_files) / (1024**2)
if avg_file_size_mb < 100:
    print(f"⚠️ 警告: 平均ファイルサイズが小さい ({avg_file_size_mb:.2f} MB)")
```

### バージョン履歴の監視

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")

# 最近のバージョン履歴
history_df = delta_table.history(20)
history_df.select("version", "timestamp", "operation", "operationMetrics").show()

# 各操作の頻度を確認
history_df.groupBy("operation").count().show()
```

### クエリパフォーマンスの測定

```python
import time

# クエリ前
start_time = time.time()

# クエリ実行
df = spark.sql("""
    SELECT customer_id, SUM(amount) as total
    FROM sales
    WHERE date BETWEEN '2025-01-01' AND '2025-01-31'
    GROUP BY customer_id
""")

# 結果を取得（実際に実行される）
result = df.collect()

# クエリ後
elapsed_time = time.time() - start_time
print(f"クエリ実行時間: {elapsed_time:.2f} 秒")

# Spark UIで詳細なメトリクスを確認
```

## よくある課題と解決策

### 課題1: Small File Problem

**問題:**
頻繁な小さな書き込みで多数のファイルが生成される

**症状:**
- クエリが遅い
- `DESCRIBE DETAIL` でファイル数が数千～数万
- 平均ファイルサイズが100MB未満

**解決策:**

```python
# 即座の対応: OPTIMIZE実行
spark.sql("OPTIMIZE my_table")

# 予防策: Auto Optimizeを有効化
spark.sql("""
    ALTER TABLE my_table
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# 定期的なOPTIMIZE
# Databricks Jobsで日次・週次スケジュール設定
```

### 課題2: クエリが遅い

**問題:**
特定のフィルタクエリのパフォーマンスが悪い

**診断:**

```python
# 1. ファイル数を確認
spark.sql("DESCRIBE DETAIL my_table").show()

# 2. Z-ORDER状況を確認
history_df = delta_table.history()
history_df.filter("operation = 'OPTIMIZE'").show()
```

**解決策:**

```python
# よく使うフィルタ列でZ-ORDER
spark.sql("""
    OPTIMIZE my_table
    ZORDER BY (frequently_filtered_column1, frequently_filtered_column2)
""")

# パーティション戦略の見直し
# 既存テーブルの場合: 新しいパーティション戦略で再作成
```

### 課題3: ストレージコストが高い

**問題:**
古いバージョンのファイルが蓄積してストレージコストが増加

**診断:**

```python
# トランザクションログのバージョン数を確認
history_df = delta_table.history()
version_count = history_df.count()
print(f"バージョン数: {version_count}")
```

**解決策:**

```python
# VACUUM実行（保持期間を短く設定）
# ⚠️ タイムトラベル要件を確認してから実行
spark.sql("VACUUM my_table RETAIN 168 HOURS")  # 7日

# ログ保持期間の調整（必要に応じて）
spark.sql("""
    ALTER TABLE my_table
    SET TBLPROPERTIES ('delta.logRetentionDuration' = '7 days')
""")
```

### 課題4: メタデータの肥大化

**問題:**
トランザクションログが大きくなりすぎる

**症状:**
- メタデータ操作が遅い
- `_delta_log` ディレクトリが数GB

**解決策:**

```python
# チェックポイントを手動作成
spark.sql("ALTER TABLE my_table CREATE CHECKPOINT")

# ログ保持期間を短縮（注意: タイムトラベルに影響）
spark.sql("""
    ALTER TABLE my_table
    SET TBLPROPERTIES ('delta.logRetentionDuration' = '7 days')
""")

# VACUUM実行（古いログファイルも削除される）
spark.sql("VACUUM my_table")
```

## ベストプラクティス

### 運用の基本原則

1. **定期的なOPTIMIZE** - 週次でZ-ORDER含む
2. **適切なVACUUM保持期間** - コンプライアンス要件を考慮（通常7日）
3. **Auto Optimize有効化** - 新規テーブルはデフォルトで有効化
4. **統計の更新** - 大きなデータ変更後に実行
5. **パーティション戦略** - 1パーティション1GB以上を維持

### パーティション戦略

```python
# 推奨: 日付パーティション（時系列データ）
df.write.format("delta") \
    .partitionBy("date") \
    .save("/path/to/table")

# パーティション数の目標
# - 総パーティション数: < 数千
# - 1パーティションあたりのサイズ: > 1GB
```

### コスト最適化

1. **ストレージ最適化**
   - 定期的なVACUUM実行
   - 圧縮設定の最適化
   - 不要なパーティションの削除

2. **コンピュート最適化**
   - OPTIMIZEでファイル数削減
   - Z-ORDERでI/O削減
   - キャッシングの活用

### モニタリング体制

```python
def monitoring_dashboard():
    """テーブル健全性ダッシュボード"""
    tables = ["sales", "customers", "products"]

    for table in tables:
        detail = spark.sql(f"DESCRIBE DETAIL {table}").collect()[0]

        num_files = detail['numFiles']
        size_gb = detail['sizeInBytes'] / (1024**3)
        avg_file_mb = (detail['sizeInBytes'] / num_files) / (1024**2) if num_files > 0 else 0

        print(f"\n{'='*50}")
        print(f"テーブル: {table}")
        print(f"ファイル数: {num_files:,}")
        print(f"サイズ: {size_gb:.2f} GB")
        print(f"平均ファイルサイズ: {avg_file_mb:.2f} MB")

        # 健全性チェック
        if num_files > 10000:
            print("⚠️ アクション必要: OPTIMIZE実行")
        elif avg_file_mb < 100:
            print("⚠️ アクション必要: ファイルサイズが小さい")
        else:
            print("✓ 健全")

monitoring_dashboard()
```

## 検証ポイント

### 運用検証

- [ ] OPTIMIZE実行後にファイル数が減少したか確認した
- [ ] Z-ORDERによるクエリパフォーマンス改善を測定した
- [ ] VACUUM後にストレージサイズが削減されたか確認した
- [ ] Auto Optimizeが正しく動作しているか確認した

### パフォーマンス検証

- [ ] データスキッピングが機能しているか確認した
- [ ] クエリ時間を測定・比較した
- [ ] Spark UIでメトリクスを確認した

## まとめ

Delta Lakeの運用は、以下の3つの定期メンテナンスが鍵：

1. **OPTIMIZE**: ファイル数削減とパフォーマンス向上
2. **VACUUM**: ストレージコスト削減
3. **ANALYZE TABLE**: クエリ最適化のための統計収集

**推奨スケジュール:**
- 日次: OPTIMIZE（増分分のみ）
- 週次: OPTIMIZE + Z-ORDER（全体）
- 月次: VACUUM + ANALYZE TABLE

Auto Optimizeを活用し、継続的な監視を怠らないことで、高パフォーマンスなLakehouseを維持できる。

**関連スキル:**
- `databricks/fundamentals/delta-lake-basics/SKILL.md` - 基本操作
- `databricks/infrastructure/performance-tuning/SKILL.md` - 全体的なパフォーマンスチューニング（該当する場合）
