---
name: "Databricks JSON形式"
description: "Databricks環境でのJSON形式データの読み込み、処理、最適化に関する実践的なガイド。PySpark、スキーマ定義、ネストされたJSONの処理、パフォーマンス最適化に対応"
---

# Databricks JSON形式: JSON形式データの読み込みと最適化

## このスキルを使う場面

- DatabricksでJSONファイルを読み込む必要がある
- ネストされたJSON構造を処理したい
- JSONデータのスキーマを定義したい
- JSONデータのパフォーマンスを最適化したい
- JSONからParquetへの変換が必要
- 複数行JSONやストリーミングJSONを扱う

## JSON形式の概要

### Databricksで扱うJSON形式の種類

**1. ラインデリミテッドJSON（標準）**

1行に1つの完全なJSONオブジェクト：

```json
{"id": 1, "name": "Alice", "age": 30}
{"id": 2, "name": "Bob", "age": 25}
{"id": 3, "name": "Charlie", "age": 35}
```

- Databricksの標準フォーマット
- 並列処理に最適
- ファイルサイズが大きくても効率的に読み込み可能

**2. マルチラインJSON**

複数行にまたがる整形されたJSON：

```json
{
  "id": 1,
  "name": "Alice",
  "age": 30
}
```

- 可読性が高い
- `multiline: true`オプションが必要
- 大きなファイルでは非効率的

**3. ネストされたJSON**

階層構造を持つJSON：

```json
{
  "id": 1,
  "user": {
    "name": "Alice",
    "email": "alice@example.com"
  },
  "orders": [
    {"order_id": 101, "amount": 50.00},
    {"order_id": 102, "amount": 75.00}
  ]
}
```

## JSONの読み込み

### 基本的な読み込み

**PySpark での読み込み:**

```python
# 基本的な読み込み
df = spark.read.format("json").load("/path/to/file.json")

# または簡潔な記法
df = spark.read.json("/path/to/file.json")

# データの確認
df.show()
df.printSchema()
```

**SQL での読み込み:**

```sql
-- JSONファイルから直接クエリ
SELECT * FROM json.`/path/to/file.json`;

-- テーブルとして登録
CREATE TABLE my_table
USING json
OPTIONS (path "/path/to/file.json");
```

### マルチラインJSONの読み込み

複数行にまたがるJSONファイルを読み込む場合：

```python
# multilineオプションを使用
df = spark.read \
    .option("multiline", "true") \
    .format("json") \
    .load("/path/to/multiline.json")
```

**注意点:**
- マルチラインモードでは並列処理が制限される
- 大きなファイルではパフォーマンスが低下する可能性
- 可能な限りラインデリミテッド形式を推奨

### スキーマ定義による最適化

**スキーマ推論（デフォルト）:**

```python
# Sparkが自動的にスキーマを推論（全データをスキャン）
df = spark.read.json("/path/to/file.json")
```

**明示的なスキーマ定義（推奨）:**

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# スキーマを定義
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("email", StringType(), True)
])

# スキーマを指定して読み込み
df = spark.read.schema(schema).json("/path/to/file.json")
```

**スキーマ定義のメリット:**
- データを2回スキャンする必要がない（大幅な高速化）
- データ型が明確になり、エラーを早期に検出
- メモリ使用量の削減
- 予期しないスキーマ変更からの保護

### ネストされたJSONの処理

**構造体（Struct）のアクセス:**

```python
# ネストされたフィールドへのアクセス
df.select("user.name", "user.email").show()

# または列記法
from pyspark.sql.functions import col
df.select(col("user.name"), col("user.email")).show()
```

**配列（Array）の処理:**

```python
from pyspark.sql.functions import explode, col

# 配列を行に展開
df_exploded = df.select(
    col("id"),
    explode(col("orders")).alias("order")
)

# 展開後のフィールドへのアクセス
df_exploded.select(
    "id",
    "order.order_id",
    "order.amount"
).show()
```

**JSON文字列からの値抽出:**

```python
from pyspark.sql.functions import get_json_object, from_json

# JSON文字列から特定の値を抽出
df.select(
    get_json_object(col("json_string"), "$.user.name").alias("name")
).show()

# JSON文字列を構造体に変換
schema = StructType([
    StructField("name", StringType()),
    StructField("age", IntegerType())
])

df.select(
    from_json(col("json_string"), schema).alias("data")
).select("data.*").show()
```

### JSONのフラット化

ネストされたJSONを1階層のテーブルに変換：

```python
from pyspark.sql.functions import col

# 手動でのフラット化
df_flat = df.select(
    col("id"),
    col("user.name").alias("user_name"),
    col("user.email").alias("user_email")
)

# 複数レベルのネストを処理
df_orders = df.select(
    col("id"),
    col("user.name").alias("user_name"),
    explode(col("orders")).alias("order")
).select(
    col("id"),
    col("user_name"),
    col("order.order_id").alias("order_id"),
    col("order.amount").alias("amount")
)
```

## エラーハンドリング

### パースモードの設定

JSONパース時のエラー処理を制御：

```python
# PERMISSIVEモード（デフォルト）: エラー行をnullとして保持
df = spark.read \
    .option("mode", "PERMISSIVE") \
    .json("/path/to/file.json")

# DROPMALFORMEDモード: エラー行を削除
df = spark.read \
    .option("mode", "DROPMALFORMED") \
    .json("/path/to/file.json")

# FAILFASTモード: エラー発生時に処理を停止
df = spark.read \
    .option("mode", "FAILFAST") \
    .json("/path/to/file.json")
```

### 救済データカラム（Rescued Data Column）

パースできなかったデータをキャプチャ：

```python
# 救済データカラムを有効化
df = spark.read \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .json("/path/to/file.json")

# エラー行を確認
df.filter(col("_corrupt_record").isNotNull()).show()
```

## パフォーマンス最適化

### JSONからParquetへの変換

JSONは人間が読みやすい形式だが、パフォーマンスに課題がある。Parquet形式への変換を推奨：

```python
# JSONを読み込み
df = spark.read.json("/path/to/input.json")

# Parquet形式で保存
df.write.mode("overwrite").parquet("/path/to/output.parquet")

# 以降はParquetから読み込み
df_parquet = spark.read.parquet("/path/to/output.parquet")
```

**Parquet変換のメリット:**
- 10x-100x高速な読み込み
- カラムナ形式による効率的な圧縮
- スキーマが埋め込まれている（推論不要）
- 述語プッシュダウンによるクエリ最適化

### パーティション分割

大規模なJSONデータの処理効率化：

```python
# パーティション分割して保存
df.write \
    .mode("overwrite") \
    .partitionBy("date", "country") \
    .parquet("/path/to/partitioned")

# パーティションを活用したクエリ
df_filtered = spark.read.parquet("/path/to/partitioned") \
    .filter(col("date") == "2025-01-01")
```

### ファイルサイズの最適化

出力ファイル数を制御：

```python
# 出力パーティション数を削減
df.coalesce(10).write.parquet("/path/to/output")

# または再パーティション（データをシャッフル）
df.repartition(10).write.parquet("/path/to/output")
```

**coalesce vs repartition:**
- `coalesce`: シャッフルなしでパーティション削減（軽量）
- `repartition`: データをシャッフルして再分散（均等分散）

### 圧縮設定

```python
# 圧縮コーデックの指定
df.write \
    .option("compression", "snappy") \
    .parquet("/path/to/output")
```

**主な圧縮形式:**
- `snappy`: 高速、中程度の圧縮率（デフォルト推奨）
- `gzip`: 低速、高い圧縮率
- `lz4`: 最高速、低い圧縮率
- `zstd`: バランス型

## JSONの書き込み

### DataFrameからJSONへの出力

```python
# 基本的な書き込み
df.write.format("json").save("/path/to/output.json")

# または簡潔な記法
df.write.json("/path/to/output.json")

# 上書きモード
df.write.mode("overwrite").json("/path/to/output.json")

# 追記モード
df.write.mode("append").json("/path/to/output.json")
```

### 整形されたJSON出力

```python
# Pretty-printされたJSON（可読性向上）
df.write \
    .option("compression", "none") \
    .json("/path/to/output.json")

# Pythonでの整形出力（小規模データのみ）
import json
data = df.toPandas().to_dict('records')
with open('/dbfs/path/to/output.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## ベストプラクティス

### スキーマ管理

1. **常にスキーマを定義する**
   - 大規模データではスキーマ推論を避ける
   - データ型を明示的に指定
   - スキーマ定義を別ファイルで管理

2. **スキーマエボリューションへの対応**
   - 新しいフィールドを追加する場合は`nullable=True`
   - 互換性のあるスキーマ変更を計画
   - バージョン管理を実施

### データ品質

1. **データ検証**
   - 読み込み後にデータ型を確認
   - 欠損値の処理戦略を定義
   - 期待値に合わないデータをログに記録

2. **エラーハンドリング**
   - 本番環境では`PERMISSIVE`モードを使用
   - `_corrupt_record`カラムでエラーを監視
   - 定期的にエラーログを確認

### パフォーマンス

1. **ETLパイプラインでの位置づけ**
   - JSONは入力形式として使用
   - 処理中間結果はParquetまたはDelta形式
   - 最終出力は用途に応じて選択

2. **キャッシング戦略**
   - 同じJSONを複数回読む場合はキャッシュ
   - 変換後のデータをキャッシュまたは永続化

```python
# データをキャッシュ
df_cached = df.cache()

# または永続化レベルを指定
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)
```

## よくある課題と解決策

### 課題1: スキーマ推論が遅い

**問題:**
大規模なJSONファイルでスキーマ推論に時間がかかる

**解決策:**
```python
# サンプルからスキーマを取得
sample_df = spark.read.json("/path/to/file.json", samplingRatio=0.1)
schema = sample_df.schema

# 全データに適用
df = spark.read.schema(schema).json("/path/to/file.json")
```

### 課題2: ネストされたJSONのフラット化が複雑

**問題:**
深くネストされたJSONの処理が困難

**解決策:**
```python
# 段階的にフラット化
def flatten_struct(df, prefix=""):
    from pyspark.sql.functions import col
    flat_cols = []
    nested_cols = []

    for field in df.schema.fields:
        name = field.name
        dtype = field.dataType

        if isinstance(dtype, StructType):
            nested_cols.append(name)
        else:
            flat_cols.append(col(f"{prefix}{name}"))

    # ネストされたフィールドを再帰的に処理
    if nested_cols:
        for nc in nested_cols:
            df = df.select("*", f"{nc}.*").drop(nc)
        return flatten_struct(df, prefix)
    else:
        return df.select(*flat_cols)

df_flat = flatten_struct(df)
```

### 課題3: メモリ不足エラー

**問題:**
大きなJSONファイルの読み込みでメモリ不足

**解決策:**
```python
# ストリーミング読み込み
df_stream = spark.readStream.json("/path/to/json/")

# バッチ処理でチャンク分割
file_list = dbutils.fs.ls("/path/to/json/")
for file_info in file_list:
    df_chunk = spark.read.json(file_info.path)
    # 処理とパーシャル保存
    df_chunk.write.mode("append").parquet("/path/to/output")
```

### 課題4: JSON配列の処理

**問題:**
配列を含むJSONの処理が複雑

**解決策:**
```python
from pyspark.sql.functions import explode_outer, posexplode

# 配列を展開（nullを保持）
df_exploded = df.select("*", explode_outer("array_field").alias("item"))

# インデックス付きで展開
df_indexed = df.select("*", posexplode("array_field").alias("pos", "item"))
```

## 検証ポイント

### 読み込み検証

- [ ] スキーマが期待通りか確認した
- [ ] データ型が正しいか確認した
- [ ] レコード数が期待値と一致するか確認した
- [ ] ネストされたフィールドにアクセスできるか確認した

### データ品質検証

- [ ] 欠損値の割合を確認した
- [ ] `_corrupt_record`にエラーがないか確認した
- [ ] ユニークキーの重複がないか確認した
- [ ] データの範囲が妥当か確認した

### パフォーマンス検証

- [ ] 読み込み時間を測定した
- [ ] Parquet変換のメリットを評価した
- [ ] パーティション戦略を検討した
- [ ] キャッシングの必要性を判断した

## 他フォーマットとの連携

### JSON → Parquet

最も一般的な変換パターン：

```python
# JSONを読み込んでParquetに変換
spark.read.json("/path/to/input.json") \
    .write.mode("overwrite") \
    .parquet("/path/to/output.parquet")
```

### JSON → Delta

トランザクショナルなデータレイクを構築：

```python
# JSONを読み込んでDelta Lakeに保存
spark.read.json("/path/to/input.json") \
    .write.format("delta") \
    .mode("overwrite") \
    .save("/path/to/delta-table")
```

### JSON + Streaming

リアルタイムJSONデータの処理：

```python
# ストリーミング読み込み
df_stream = spark.readStream \
    .schema(schema) \
    .json("/path/to/streaming-json/")

# ストリーミング書き込み
df_stream.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start("/path/to/delta-table")
```

## まとめ

JSONフォーマットは柔軟性が高いが、パフォーマンスに課題がある。Databricks環境では以下のアプローチを推奨：

1. **入力**: JSON形式でデータを受け取る
2. **処理**: スキーマを定義し、エラーハンドリングを実装
3. **保存**: Parquet または Delta 形式に変換して保存
4. **分析**: 変換後のデータを高速にクエリ

この戦略により、JSONの柔軟性とカラムナ形式の高速性を両立できる。
