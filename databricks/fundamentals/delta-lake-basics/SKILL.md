---
name: "Databricks Delta Lake基礎"
description: "Delta Lakeの基本概念と操作。ACIDトランザクション、読み書き、UPDATE/DELETE/MERGE、タイムトラベル、スキーマエボリューションをカバー。運用・最適化は別スキル参照"
---

# Databricks Delta Lake基礎

## このスキルを使う場面

- ACIDトランザクションが必要
- データの更新・削除が頻繁に発生する
- UPSERT（MERGE）操作が必要
- タイムトラベル・データバージョン管理が必要
- スキーマエボリューションが必要
- ストリーミングとバッチの統合が必要
- Lakehouseアーキテクチャを構築したい

**このスキルでカバーする範囲:**
- Delta Lakeの概念と基本操作
- データの読み書き、更新、削除

**運用・最適化については:**
`databricks/data-engineering/delta-lake-operations/SKILL.md` を参照

## Delta Lakeの概要

### Delta Lakeとは

Delta Lakeは、Databricks上のテーブルの基盤となる最適化されたストレージレイヤー。Apache Parquetファイルにファイルベースのトランザクションログを追加し、ACIDトランザクションとスケーラブルなメタデータ処理を実現。

**アーキテクチャ:**

```
Delta Lakeテーブル
├── _delta_log/           # トランザクションログ
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   ├── 00000000000000000002.json
│   └── 00000000000000000010.checkpoint.parquet
└── *.parquet            # 実データ（Parquet形式）
```

### Delta LakeとParquetの比較

| 機能 | Parquet | Delta Lake |
|------|---------|-----------|
| カラムナストレージ | ✅ | ✅ |
| 高圧縮率 | ✅ | ✅ |
| 高速読み込み | ✅ | ✅ |
| ACIDトランザクション | ❌ | ✅ |
| UPDATE/DELETE | ❌ | ✅ |
| MERGE（UPSERT） | ❌ | ✅ |
| タイムトラベル | ❌ | ✅ |
| スキーマエボリューション | 限定的 | ✅ |
| データスキッピング | 基本的 | 高度 |
| ストリーミング対応 | 限定的 | ✅ |

### ACIDトランザクションの保証

Delta Lakeは完全なACID保証を提供：

1. **Atomicity（原子性）**: 全て成功するか、全て失敗するか
2. **Consistency（一貫性）**: データは常に整合性のある状態
3. **Isolation（分離性）**: 同時実行でも互いに干渉しない
4. **Durability（永続性）**: コミット後のデータは保証される

## Delta Lakeの読み込み

### 基本的な読み込み

**PySpark での読み込み:**

```python
# Delta形式で読み込み
df = spark.read.format("delta").load("/path/to/delta-table")

# または簡潔な記法
from delta.tables import DeltaTable
df = DeltaTable.forPath(spark, "/path/to/delta-table").toDF()

# テーブル名で読み込み
df = spark.read.format("delta").table("my_table")
df = spark.table("my_table")

# データの確認
df.show()
df.printSchema()
```

**SQL での読み込み:**

```sql
-- Delta テーブルから読み込み
SELECT * FROM my_table;

-- パスから直接読み込み
SELECT * FROM delta.`/path/to/delta-table`;

-- テーブルを作成
CREATE TABLE my_table
USING delta
LOCATION '/path/to/delta-table';
```

### タイムトラベル

過去のバージョンのデータにアクセス：

```python
# バージョン番号で指定
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("/path/to/delta-table")

# タイムスタンプで指定
df = spark.read.format("delta") \
    .option("timestampAsOf", "2025-01-01 00:00:00") \
    .load("/path/to/delta-table")

# SQL構文
spark.sql("""
    SELECT * FROM my_table
    VERSION AS OF 5
""")

spark.sql("""
    SELECT * FROM my_table
    TIMESTAMP AS OF '2025-01-01 00:00:00'
""")
```

**ユースケース:**
- 誤った更新を元に戻す
- 特定時点のデータを再現
- 監査・コンプライアンス対応
- A/Bテスト・比較分析

### バージョン履歴の確認

```python
from delta.tables import DeltaTable

# Delta テーブルのインスタンス
delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")

# 履歴を確認
history_df = delta_table.history()
history_df.select("version", "timestamp", "operation", "operationMetrics").show()

# 最新10件のみ
history_df = delta_table.history(10)
```

## Delta Lakeの書き込み

### 基本的な書き込み

```python
# Delta形式で書き込み
df.write.format("delta").save("/path/to/delta-table")

# 保存モード指定
df.write.format("delta").mode("overwrite").save("/path/to/delta-table")
df.write.format("delta").mode("append").save("/path/to/delta-table")

# テーブルとして保存
df.write.format("delta").mode("overwrite").saveAsTable("my_table")

# SQL構文
df.createOrReplaceTempView("temp_view")
spark.sql("""
    CREATE TABLE my_table
    USING delta
    AS SELECT * FROM temp_view
""")
```

### パーティション分割

```python
# パーティション分割して保存
df.write.format("delta") \
    .partitionBy("date", "country") \
    .save("/path/to/delta-table")

# パーティション上書き（動的パーティション）
df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "date = '2025-01-01'") \
    .save("/path/to/delta-table")
```

## UPDATE/DELETE/MERGE 操作

### UPDATE（更新）

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# Delta テーブルを取得
delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")

# 条件付き更新
delta_table.update(
    condition = col("age") < 18,
    set = {"status": "'minor'"}
)

# 複数列の更新
delta_table.update(
    condition = col("country") == "Japan",
    set = {
        "currency": "'JPY'",
        "timezone": "'Asia/Tokyo'"
    }
)

# SQL構文
spark.sql("""
    UPDATE my_table
    SET status = 'minor'
    WHERE age < 18
""")
```

### DELETE（削除）

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# Delta テーブルを取得
delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")

# 条件付き削除
delta_table.delete(col("status") == "inactive")

# 複数条件
delta_table.delete((col("age") < 18) & (col("consent") == False))

# SQL構文
spark.sql("""
    DELETE FROM my_table
    WHERE status = 'inactive'
""")
```

### MERGE（UPSERT）

最も強力な機能の1つ。新規データを挿入し、既存データを更新：

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# Delta テーブルを取得
delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")

# 更新データ
updates_df = spark.read.parquet("/path/to/updates.parquet")

# MERGE操作
delta_table.alias("target") \
    .merge(
        updates_df.alias("source"),
        "target.id = source.id"  # マッチング条件
    ) \
    .whenMatchedUpdate(set = {
        "name": "source.name",
        "age": "source.age",
        "updated_at": "source.updated_at"
    }) \
    .whenNotMatchedInsert(values = {
        "id": "source.id",
        "name": "source.name",
        "age": "source.age",
        "created_at": "source.created_at"
    }) \
    .execute()

# SQL構文
spark.sql("""
    MERGE INTO target_table AS t
    USING source_table AS s
    ON t.id = s.id
    WHEN MATCHED THEN
        UPDATE SET t.name = s.name, t.age = s.age
    WHEN NOT MATCHED THEN
        INSERT (id, name, age) VALUES (s.id, s.name, s.age)
""")
```

**条件付きMERGE:**

```python
# マッチ時に条件付き更新・削除
delta_table.alias("target") \
    .merge(
        updates_df.alias("source"),
        "target.id = source.id"
    ) \
    .whenMatchedUpdate(
        condition = "source.is_deleted = false",
        set = {"name": "source.name", "age": "source.age"}
    ) \
    .whenMatchedDelete(
        condition = "source.is_deleted = true"
    ) \
    .whenNotMatchedInsert(
        condition = "source.is_deleted = false",
        values = {"id": "source.id", "name": "source.name", "age": "source.age"}
    ) \
    .execute()
```

## スキーマエボリューション

### スキーマの自動進化

新しい列を自動的に追加：

```python
# スキーママージを有効化
df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/path/to/delta-table")

# または全体設定
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

**ユースケース:**
- 新しいフィールドを追加
- 既存のnullable列に新しいデータ型互換の値を追加

### スキーマの上書き

完全に新しいスキーマでテーブルを置き換え：

```python
# スキーマを上書き
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/path/to/delta-table")
```

### スキーマエンフォースメント

スキーマ不一致を検出して防止：

```python
# デフォルトで有効
# スキーマが一致しない場合はエラー
df.write.format("delta") \
    .mode("append") \
    .save("/path/to/delta-table")
# エラー: スキーマが一致しません
```

**保護内容:**
- 列の追加・削除の防止
- データ型の不一致検出
- nullability の変更検出

## トランザクション管理

### 分離レベル

Delta Lakeは2つの分離レベルを使用：

1. **書き込み（Write Serializable）** - デフォルト
   - すべての書き込み操作で使用
   - 楽観的同時実行制御
   - コンフリクトがある場合は再試行

2. **読み込み（Snapshot Isolation）**
   - すべての読み込み操作で使用
   - 開始時点のスナップショットを読み込み
   - 書き込みの影響を受けない

### 同時実行制御

```python
# 複数の書き込みが同時に実行される場合
# Delta Lakeが自動的に調整

# 例: 同時MERGE操作
from concurrent.futures import ThreadPoolExecutor

def merge_data(partition_id):
    updates_df = spark.read.parquet(f"/path/to/updates/partition={partition_id}")
    delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")
    delta_table.alias("target") \
        .merge(updates_df.alias("source"), "target.id = source.id") \
        .whenMatchedUpdateAll() \
        .whenNotMatchedInsertAll() \
        .execute()

# 並列実行（Delta Lakeが自動的にコンフリクトを解決）
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(merge_data, range(10))
```

### トランザクションコンフリクトへの対処

```python
# リトライロジックを実装
from delta.exceptions import ConcurrentWriteException
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        delta_table.merge(...).execute()
        break
    except ConcurrentWriteException:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

## ストリーミングとの統合

### ストリーミング読み込み

```python
# Delta テーブルをストリーミングソースとして読み込み
df_stream = spark.readStream.format("delta").load("/path/to/delta-table")

# 処理
df_processed = df_stream.filter(col("status") == "active")

# 別のDelta テーブルに書き込み
df_processed.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start("/path/to/output-delta-table")
```

### 変更データキャプチャ（CDC）

テーブルの変更をストリーミング：

```python
# 変更データフィード（Change Data Feed）を有効化
spark.sql("""
    ALTER TABLE my_table
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# 変更をストリーミング
df_changes = spark.readStream \
    .format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 10) \
    .load("/path/to/delta-table")

# 変更タイプを確認
df_changes.select("_change_type", "id", "name").show()
# _change_type: insert, update_preimage, update_postimage, delete
```

### ストリーミング書き込み

```python
# ストリーミングデータをDelta テーブルに書き込み
df_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start("/path/to/delta-table")

# MERGE モードでストリーミング
def merge_micro_batch(micro_batch_df, batch_id):
    delta_table = DeltaTable.forPath(spark, "/path/to/delta-table")
    delta_table.alias("target") \
        .merge(micro_batch_df.alias("source"), "target.id = source.id") \
        .whenMatchedUpdateAll() \
        .whenNotMatchedInsertAll() \
        .execute()

df_stream.writeStream \
    .foreachBatch(merge_micro_batch) \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start()
```

## データガバナンス

### テーブルプロパティ

```python
# テーブルプロパティを設定
spark.sql("""
    ALTER TABLE my_table
    SET TBLPROPERTIES (
        'delta.logRetentionDuration' = '30 days',
        'delta.deletedFileRetentionDuration' = '7 days',
        'delta.enableChangeDataFeed' = 'true'
    )
""")

# プロパティを確認
spark.sql("SHOW TBLPROPERTIES my_table").show()
```

### 制約（Constraints）

データ品質を保証：

```python
# CHECK制約を追加
spark.sql("""
    ALTER TABLE my_table
    ADD CONSTRAINT age_check CHECK (age >= 0 AND age <= 150)
""")

# NOT NULL制約
spark.sql("""
    ALTER TABLE my_table
    CHANGE COLUMN email email STRING NOT NULL
""")

# 制約を確認
spark.sql("SHOW TBLPROPERTIES my_table").filter("key LIKE '%constraint%'").show()

# 制約を削除
spark.sql("ALTER TABLE my_table DROP CONSTRAINT age_check")
```

### Unity Catalog との統合

```python
# Unity Catalogでテーブルを作成
spark.sql("""
    CREATE TABLE main.my_schema.my_table (
        id BIGINT,
        name STRING,
        age INT,
        created_at TIMESTAMP
    )
    USING delta
    LOCATION '/path/to/delta-table'
""")

# アクセス制御
spark.sql("GRANT SELECT ON TABLE main.my_schema.my_table TO `user@example.com`")

# 監査ログは自動的に記録される
```

## 他形式からの移行

### ParquetからDelta Lakeへ

```python
# 既存のParquetをDelta Lake に変換
from delta.tables import DeltaTable

# 方法1: インプレース変換
DeltaTable.convertToDelta(
    spark,
    "parquet.`/path/to/parquet`",
    "date DATE"  # パーティションスキーマ
)

# 方法2: 読み込んで書き込み
df = spark.read.parquet("/path/to/parquet")
df.write.format("delta").save("/path/to/delta-table")
```

### JSONからDelta Lakeへ

```python
# JSONを読み込んでDelta Lake に保存
df = spark.read.json("/path/to/input.json")
df.write.format("delta").save("/path/to/delta-table")

# ストリーミング
df_stream = spark.readStream.json("/path/to/streaming-json/")
df_stream.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start("/path/to/delta-table")
```

## ベストプラクティス

### テーブル設計

1. **パーティション戦略**
   - パーティション数は数千以下
   - 1パーティションあたり1GB以上のデータ
   - 時系列データは日付でパーティション分割

2. **スキーマ設計**
   - 可能な限りスキーマを事前定義
   - nullableフィールドを適切に設定
   - データ型を明示的に指定

### スキーマエボリューションの対処

```python
# スキーママージを有効化（新しい列の追加を許可）
df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/path/to/delta-table")

# 完全な置き換えが必要な場合
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/path/to/delta-table")
```

## 検証ポイント

### 機能検証

- [ ] ACIDトランザクションが機能しているか確認した
- [ ] UPDATE/DELETE/MERGE操作をテストした
- [ ] タイムトラベルが機能するか確認した
- [ ] スキーマエボリューションをテストした

### データ品質検証

- [ ] 制約が正しく適用されているか確認した
- [ ] トランザクション履歴を確認した
- [ ] データ整合性を検証した

## 次のステップ

基本操作を習得したら、運用・最適化スキルに進んでください：

**→ `databricks/data-engineering/delta-lake-operations/SKILL.md`**

以下のトピックをカバー：
- OPTIMIZE（ファイル圧縮）
- VACUUM（古いファイル削除）
- Z-ORDER（データクラスタリング）
- パフォーマンス監視
- 定期メンテナンス

## まとめ

Delta Lakeは、Databricks Lakehouseアーキテクチャの中核技術であり、以下の理由から強く推奨される：

1. **信頼性**: ACIDトランザクションによるデータ整合性
2. **柔軟性**: UPDATE/DELETE/MERGEによる柔軟なデータ操作
3. **パフォーマンス**: Parquetの性能 + データスキッピング最適化
4. **監査**: タイムトラベルとトランザクション履歴
5. **統合**: ストリーミングとバッチの統一インターフェース
6. **ガバナンス**: スキーマエンフォースメントと制約

**推奨される移行パス:**
JSON → Parquet → **Delta Lake**

Delta Lakeは、データレイクとデータウェアハウスの利点を統合し、真のLakehouseを実現する。
