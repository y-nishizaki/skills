---
name: "Databricks Parquet形式"
description: "Databricks環境でのParquet形式データの読み込み、書き込み、パフォーマンス最適化に関する実践的なガイド。カラムナストレージ、圧縮、パーティショニング、述語プッシュダウンに対応"
---

# Databricks Parquet形式: 高性能カラムナストレージの活用

## このスキルを使う場面

- 大規模データの高速読み込みが必要
- カラムナ形式でのデータ保存を検討している
- クエリパフォーマンスを最適化したい
- ストレージコストを削減したい
- OLAP系ワークロードに最適化したい
- JSONやCSVからの移行を検討している

## Parquet形式の概要

### Parquetとは

Apache Parquetは、Hadoop エコシステム向けに設計されたオープンソースのカラムナストレージ形式。

**主な特徴:**

1. **カラムナストレージ** - データを列単位で保存
2. **高圧縮率** - エンコーディングと圧縮による効率的なストレージ
3. **スキーマ埋め込み** - メタデータとしてスキーマを保持
4. **述語プッシュダウン** - クエリ時の最適化
5. **言語非依存** - 多くのデータ処理フレームワークで利用可能

### カラムナストレージ vs 行指向ストレージ

**行指向（CSV、JSONなど）:**
```
Row1: [id=1, name=Alice, age=30, city=Tokyo]
Row2: [id=2, name=Bob, age=25, city=Osaka]
Row3: [id=3, name=Charlie, age=35, city=Kyoto]
```

**カラムナ（Parquet）:**
```
Column id:    [1, 2, 3]
Column name:  [Alice, Bob, Charlie]
Column age:   [30, 25, 35]
Column city:  [Tokyo, Osaka, Kyoto]
```

**カラムナのメリット:**
- 特定の列のみを読み込む場合に高速（I/O削減）
- 同じ型のデータがまとまり、圧縮効率が向上
- 集計クエリ（SUM、AVG、COUNTなど）で高速
- OLAP（分析）ワークロードに最適

**カラムナのデメリット:**
- 行全体を取得する場合はオーバーヘッド
- 小さなレコードの頻繁な書き込みには不向き（OLTP向きではない）
- 更新・削除操作が非効率（イミュータブル設計）

## Parquetの読み込み

### 基本的な読み込み

**PySpark での読み込み:**

```python
# 基本的な読み込み
df = spark.read.format("parquet").load("/path/to/file.parquet")

# または簡潔な記法
df = spark.read.parquet("/path/to/file.parquet")

# 複数ファイルの読み込み
df = spark.read.parquet("/path/to/directory/")

# ワイルドカード使用
df = spark.read.parquet("/path/to/data/*.parquet")

# データの確認
df.show()
df.printSchema()
```

**SQL での読み込み:**

```sql
-- Parquetファイルから直接クエリ
SELECT * FROM parquet.`/path/to/file.parquet`;

-- テーブルとして登録
CREATE TABLE my_table
USING parquet
OPTIONS (path "/path/to/file.parquet");

-- または
CREATE TABLE my_table
LOCATION '/path/to/file.parquet';
```

### スキーマの確認

Parquetはスキーマを埋め込んでいるため、推論不要：

```python
# スキーマを表示
df.printSchema()

# スキーマを取得
schema = df.schema
print(schema)

# スキーマをJSON形式で出力
print(schema.json())
```

### 列の選択（プロジェクション・プッシュダウン）

Parquetは必要な列のみを読み込むため、列を絞ることで大幅に高速化：

```python
# 必要な列のみを選択（I/O削減）
df = spark.read.parquet("/path/to/file.parquet") \
    .select("id", "name", "age")

# または読み込み時に指定は不可（全列読み込み後にselect）
# Sparkが自動的に最適化（カタリストオプティマイザ）
```

### 述語プッシュダウン

フィルタ条件をファイルレベルで適用し、不要なデータをスキップ：

```python
from pyspark.sql.functions import col

# フィルタ条件（Sparkが自動的に最適化）
df = spark.read.parquet("/path/to/file.parquet") \
    .filter(col("age") > 30)

# 複数条件
df = spark.read.parquet("/path/to/file.parquet") \
    .filter((col("age") > 30) & (col("city") == "Tokyo"))
```

**述語プッシュダウンのメリット:**
- ファイル全体を読まずに、統計情報で不要なデータをスキップ
- I/O量の削減
- メモリ使用量の削減
- クエリ時間の大幅短縮

## Parquetの書き込み

### 基本的な書き込み

```python
# 基本的な書き込み
df.write.format("parquet").save("/path/to/output.parquet")

# または簡潔な記法
df.write.parquet("/path/to/output.parquet")

# 保存モード指定
df.write.mode("overwrite").parquet("/path/to/output.parquet")
df.write.mode("append").parquet("/path/to/output.parquet")
df.write.mode("errorIfExists").parquet("/path/to/output.parquet")
df.write.mode("ignore").parquet("/path/to/output.parquet")
```

### 圧縮の設定

Parquetは複数の圧縮アルゴリズムをサポート：

```python
# Snappy圧縮（デフォルト、推奨）
df.write \
    .option("compression", "snappy") \
    .parquet("/path/to/output.parquet")

# Gzip圧縮（高圧縮率）
df.write \
    .option("compression", "gzip") \
    .parquet("/path/to/output.parquet")

# LZ4圧縮（最高速）
df.write \
    .option("compression", "lz4") \
    .parquet("/path/to/output.parquet")

# Zstd圧縮（バランス型）
df.write \
    .option("compression", "zstd") \
    .parquet("/path/to/output.parquet")

# 非圧縮
df.write \
    .option("compression", "none") \
    .parquet("/path/to/output.parquet")
```

**圧縮アルゴリズムの選択:**

| 圧縮形式 | 圧縮速度 | 圧縮率 | 解凍速度 | 推奨用途 |
|---------|---------|-------|---------|---------|
| snappy  | 速い    | 中    | 速い    | デフォルト、汎用 |
| gzip    | 遅い    | 高    | 中      | ストレージ重視 |
| lz4     | 最速    | 低    | 最速    | 速度重視 |
| zstd    | 中      | 高    | 速い    | バランス重視 |
| none    | -       | -     | -       | テスト用 |

**推奨:**
- **デフォルト**: snappy（速度と圧縮率のバランス）
- **ストレージ削減**: gzip または zstd
- **リアルタイム処理**: lz4

## パーティショニング

### パーティション分割の基本

大規模データを論理的なサブセットに分割してパフォーマンス向上：

```python
# 単一列でパーティション分割
df.write \
    .partitionBy("date") \
    .parquet("/path/to/output")

# 複数列でパーティション分割
df.write \
    .partitionBy("year", "month", "day") \
    .parquet("/path/to/output")

# 出力例:
# /path/to/output/year=2025/month=01/day=01/part-00000.parquet
# /path/to/output/year=2025/month=01/day=02/part-00000.parquet
```

### パーティション戦略

**良いパーティションキーの条件:**

1. **カーディナリティが適度** - 数十〜数千程度
   - ❌ 悪い例: user_id（カーディナリティが高すぎる、小さなファイルが大量生成）
   - ✅ 良い例: date, country, category

2. **クエリでよく使われる** - フィルタ条件に頻出
   - ✅ `WHERE date = '2025-01-01'`
   - ✅ `WHERE country = 'Japan'`

3. **データが均等に分散** - 特定のパーティションに偏らない
   - ❌ 悪い例: is_premium（ほとんどがfalse）
   - ✅ 良い例: region（ある程度均等に分散）

**パーティション数の目安:**
- 1パーティションあたり 100MB - 1GB のデータが理想
- パーティション総数は数千以下を推奨
- 小さすぎるファイルは small file problem を引き起こす

### パーティションプルーニング

パーティション分割されたデータを効率的にクエリ：

```python
# パーティションを指定してクエリ（不要なパーティションをスキップ）
df = spark.read.parquet("/path/to/output") \
    .filter(col("date") == "2025-01-01")

# 複数パーティション
df = spark.read.parquet("/path/to/output") \
    .filter((col("year") == "2025") & (col("month") == "01"))

# 範囲指定
df = spark.read.parquet("/path/to/output") \
    .filter(col("date").between("2025-01-01", "2025-01-31"))
```

**パーティションプルーニングの効果:**
- 不要なパーティション全体をスキップ
- I/O量の大幅削減
- クエリ時間の短縮

## ファイルサイズの最適化

### Small File Problem

**問題:**
多数の小さなファイルがパフォーマンスを低下させる

**原因:**
- パーティション分割のしすぎ
- 頻繁な小さなバッチ書き込み
- 並列度の設定ミス

**解決策:**

```python
# coalesceで出力ファイル数を削減（シャッフルなし）
df.coalesce(10).write.parquet("/path/to/output")

# repartitionでデータを再分散（シャッフルあり）
df.repartition(10).write.parquet("/path/to/output")

# パーティション列と組み合わせ
df.repartition("date") \
    .write.partitionBy("date").parquet("/path/to/output")
```

**coalesce vs repartition:**

| 操作 | シャッフル | 用途 | パフォーマンス |
|------|----------|------|--------------|
| coalesce | なし | パーティション削減 | 高速 |
| repartition | あり | パーティション増減・再分散 | 低速 |

### ファイル結合（Compaction）

既存の小さなファイルを結合：

```python
# 既存データを読み込んで再書き込み
df = spark.read.parquet("/path/to/small-files")
df.coalesce(10).write.mode("overwrite").parquet("/path/to/optimized")

# またはDelta Lakeの最適化機能を使用（推奨）
spark.sql("OPTIMIZE delta.`/path/to/delta-table`")
```

### 適切なファイルサイズ

**推奨:**
- 1ファイルあたり 128MB - 1GB
- ファイル数は1000個以下を目安
- HDFS/S3のブロックサイズを考慮

## パフォーマンス最適化

### 統計情報の活用

Parquetファイルには統計情報（min、max、null count）が埋め込まれている：

```python
# Sparkが自動的に統計情報を活用
# フィルタクエリで不要なRow Groupをスキップ
df = spark.read.parquet("/path/to/file.parquet") \
    .filter(col("age") > 50)
```

### キャッシング

頻繁にアクセスするデータをメモリにキャッシュ：

```python
# データをキャッシュ
df_cached = spark.read.parquet("/path/to/file.parquet").cache()
df_cached.count()  # キャッシュを実行

# 永続化レベルを指定
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)

# キャッシュ解放
df_cached.unpersist()
```

### ブロードキャスト結合

小さなテーブルをブロードキャストして結合を高速化：

```python
from pyspark.sql.functions import broadcast

# 小さいテーブルをブロードキャスト
df_result = df_large.join(
    broadcast(df_small),
    on="key",
    how="inner"
)
```

### データスキッピング（Data Skipping）

Delta Lakeと組み合わせて、より高度なデータスキッピングを実現：

```python
# Parquet単体では限定的
# Delta Lakeへの移行を推奨（自動的に統計収集）
df.write.format("delta").save("/path/to/delta-table")
```

Delta Lakeは最初の32列について自動的に統計を収集し、データスキッピングを最適化。

## Parquetの詳細設定

### Row Group サイズ

Row Groupは、Parquetファイル内の行のまとまり：

```python
# Row Groupサイズを設定（デフォルト: 128MB）
df.write \
    .option("parquet.block.size", 134217728) \  # 128MB in bytes
    .parquet("/path/to/output")
```

**推奨:**
- デフォルト（128MB）で問題なし
- 大きなクラスタでは 256MB - 512MB も可

### Page サイズ

Pageは、カラム内のさらに小さな単位：

```python
# Pageサイズを設定（デフォルト: 1MB）
df.write \
    .option("parquet.page.size", 1048576) \  # 1MB in bytes
    .parquet("/path/to/output")
```

### 辞書エンコーディング

カーディナリティの低い列を効率的に圧縮：

```python
# 辞書エンコーディングを有効化（デフォルトで有効）
df.write \
    .option("parquet.enable.dictionary", "true") \
    .parquet("/path/to/output")
```

**辞書エンコーディングが効果的なケース:**
- カテゴリ列（country、status、category など）
- 繰り返しの多い文字列
- 低カーディナリティの列

## 他形式からの移行

### JSONからParquetへ

```python
# JSONを読み込んでParquetに変換
df = spark.read.json("/path/to/input.json")

# スキーマ最適化（必要に応じて）
from pyspark.sql.types import IntegerType
df = df.withColumn("age", col("age").cast(IntegerType()))

# Parquet形式で保存
df.write.mode("overwrite").parquet("/path/to/output.parquet")
```

**パフォーマンス比較:**
- 読み込み速度: 10x - 100x 高速
- ストレージサイズ: 50% - 90% 削減

### CSVからParquetへ

```python
# CSVを読み込んでParquetに変換
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("/path/to/input.csv")

# Parquet形式で保存
df.write.mode("overwrite").parquet("/path/to/output.parquet")
```

### ParquetからDeltaへ

Parquetの利点を保ちながら、ACIDトランザクションを追加：

```python
# Parquetを読み込んでDelta形式に変換
df = spark.read.parquet("/path/to/input.parquet")
df.write.format("delta").mode("overwrite").save("/path/to/delta-table")

# または既存のParquetをDelta変換
from delta.tables import DeltaTable

DeltaTable.convertToDelta(
    spark,
    "parquet.`/path/to/parquet`",
    partitionSchema="date DATE"
)
```

## ベストプラクティス

### データモデリング

1. **適切なパーティション戦略**
   - クエリパターンを分析
   - パーティションキーはフィルタ条件に頻出する列を選択
   - カーディナリティは数十〜数千程度

2. **スキーマ設計**
   - ネストされた構造体を活用（関連データをまとめる）
   - データ型を適切に選択（Int vs Long、String vs Categoricalなど）
   - Nullableフィールドを正しく設定

3. **列の順序**
   - よく使う列を前に配置
   - カーディナリティの低い列を前に配置（圧縮効率向上）

### 運用

1. **定期的な最適化**
   - Small fileを定期的に結合
   - 統計情報を更新
   - 不要なパーティションを削除

2. **モニタリング**
   - ファイル数を監視
   - ファイルサイズ分布を確認
   - クエリパフォーマンスを追跡

3. **バージョン管理**
   - スキーマ変更を慎重に管理
   - 後方互換性を維持
   - 必要に応じてスキーマエボリューション

### コスト最適化

1. **ストレージコスト削減**
   - 適切な圧縮アルゴリズムを選択
   - 不要なデータを定期的に削除
   - パーティションプルーニングでスキャン量削減

2. **コンピュートコスト削減**
   - キャッシングで繰り返し読み込みを削減
   - 列選択でI/O削減
   - 適切なクラスタサイズ

## よくある課題と解決策

### 課題1: Small File Problem

**問題:**
数千〜数万の小さなファイルが生成され、パフォーマンスが低下

**診断:**
```python
# ファイル数を確認
files = dbutils.fs.ls("/path/to/parquet/")
print(f"File count: {len(files)}")

# ファイルサイズ分布を確認
sizes = [f.size for f in files]
print(f"Average size: {sum(sizes) / len(sizes) / 1024 / 1024:.2f} MB")
```

**解決策:**
```python
# ファイルを結合
df = spark.read.parquet("/path/to/small-files")
df.repartition(100).write.mode("overwrite").parquet("/path/to/optimized")
```

### 課題2: データスキュー

**問題:**
特定のパーティションが非常に大きく、処理が遅い

**解決策:**
```python
# パーティションキーを見直す
# 高カーディナリティのキーを追加
df.write \
    .partitionBy("date", "region") \
    .parquet("/path/to/output")

# または repartition で均等化
df.repartition(100, "date").write.parquet("/path/to/output")
```

### 課題3: スキーマ不一致

**問題:**
異なるスキーマのParquetファイルを読み込むとエラー

**解決策:**
```python
# スキーママージを有効化
df = spark.read \
    .option("mergeSchema", "true") \
    .parquet("/path/to/files")

# またはスキーマを統一
df.write.mode("overwrite").parquet("/path/to/normalized")
```

### 課題4: メモリ不足

**問題:**
大きなParquetファイルの読み込みでメモリ不足

**解決策:**
```python
# バッチ処理
partitions = dbutils.fs.ls("/path/to/partitioned/")
for partition in partitions:
    df_batch = spark.read.parquet(partition.path)
    # 処理
    df_batch.write.mode("append").parquet("/path/to/output")

# またはストリーミング
df_stream = spark.readStream.parquet("/path/to/files")
```

## 検証ポイント

### データ品質検証

- [ ] スキーマが期待通りか確認した
- [ ] レコード数が一致するか確認した
- [ ] パーティション数が適切か確認した
- [ ] ファイルサイズが適切か（100MB-1GB）確認した

### パフォーマンス検証

- [ ] 読み込み時間を測定した
- [ ] クエリパフォーマンスをテストした
- [ ] パーティションプルーニングが効いているか確認した
- [ ] Small file problemが発生していないか確認した

### ストレージ検証

- [ ] 圧縮率を確認した
- [ ] ストレージコストを試算した
- [ ] 不要なファイルを削除した

## 次のステップ: Delta Lake への移行

Parquetは強力だが、以下の制約がある：
- ACIDトランザクション非対応
- 更新・削除が非効率
- タイムトラベル非対応
- スキーマエボリューションが限定的

**Delta Lake へ移行するメリット:**
- Parquetの全メリットを保持
- ACIDトランザクション
- タイムトラベル
- MERGE/UPDATE/DELETE サポート
- 自動的な統計収集とデータスキッピング
- より効率的な Small file 管理

移行は簡単：

```python
# ParquetからDeltaへ
df = spark.read.parquet("/path/to/parquet")
df.write.format("delta").save("/path/to/delta-table")
```

## まとめ

Parquet形式はDatabricks環境での標準的なストレージ形式であり、以下の理由から推奨される：

1. **高速性**: JSONやCSVと比較して10x-100x高速
2. **圧縮効率**: ストレージコストを大幅に削減
3. **クエリ最適化**: カラムナ形式と述語プッシュダウン
4. **エコシステム**: Sparkとのシームレスな統合

さらなる機能が必要な場合は、Delta Lake への移行を検討すること。
