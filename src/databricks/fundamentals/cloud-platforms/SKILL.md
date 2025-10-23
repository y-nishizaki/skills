---
name: "Databricksクラウドプラットフォーム連携"
description: "AWS、Azure、GCP上でのDatabricks統合。ストレージ、IAM、ネットワーク、サービス連携の理解と実践的な設定方法"
---

# Databricksクラウドプラットフォーム連携

## このスキルを使う場面

- Databricksとクラウドストレージの連携が必要
- IAM/認証設定を理解したい
- ネットワーク設定を構成したい
- クラウド固有のサービスと統合したい
- マルチクラウド戦略を検討している

## マルチクラウド対応

Databricksは3大クラウドプロバイダーで利用可能：
- **AWS**: 広範な互換性とサービス
- **Azure**: Microsoft製品との統合
- **GCP**: オープンソースとML重視

## AWS統合

### ストレージ (S3)

```python
# S3読み込み（IAMロール使用）
df = spark.read.parquet("s3://bucket-name/path/to/data/")

# S3書き込み
df.write.mode("overwrite").parquet("s3://bucket-name/output/")

# S3マウント
dbutils.fs.mount(
    source="s3://bucket-name/path",
    mount_point="/mnt/data",
    extra_configs={
        "fs.s3a.aws.credentials.provider":
        "com.amazonaws.auth.InstanceProfileCredentialsProvider"
    }
)

# マウント後のアクセス
df = spark.read.parquet("/mnt/data/file.parquet")
```

### IAM認証

```python
# インスタンスプロファイル（推奨）
# クラスター設定でIAMロールを指定

# アクセスキー（非推奨：開発のみ）
spark.conf.set("fs.s3a.access.key", "ACCESS_KEY")
spark.conf.set("fs.s3a.secret.key", "SECRET_KEY")

# AssumeRole
spark.conf.set("fs.s3a.assumed.role.arn", "arn:aws:iam::123456789:role/MyRole")
```

### AWS サービス連携

**AWS Glue Data Catalog:**
```python
# Glueカタログ使用
spark.sql("USE glue_catalog.database_name")
df = spark.table("table_name")
```

**Amazon Kinesis:**
```python
# Kinesisストリーム読み込み
df_stream = spark.readStream \
    .format("kinesis") \
    .option("streamName", "my-stream") \
    .option("region", "us-east-1") \
    .option("initialPosition", "latest") \
    .load()
```

**Amazon Redshift:**
```python
# Redshift読み込み
df = spark.read \
    .format("com.databricks.spark.redshift") \
    .option("url", "jdbc:redshift://endpoint:5439/database") \
    .option("dbtable", "schema.table") \
    .option("tempdir", "s3://bucket/temp/") \
    .option("aws_iam_role", "arn:aws:iam::123:role/RedshiftRole") \
    .load()
```

## Azure統合

### ストレージ (ADLS Gen2/Blob)

```python
# ADLS Gen2 読み込み（OAuth使用）
df = spark.read.parquet("abfss://container@storageaccount.dfs.core.windows.net/path/")

# Blob Storage
df = spark.read.parquet("wasbs://container@storageaccount.blob.core.windows.net/path/")

# ADLSマウント
configs = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type":
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id": "<application-id>",
    "fs.azure.account.oauth2.client.secret": "<secret>",
    "fs.azure.account.oauth2.client.endpoint":
    "https://login.microsoftonline.com/<directory-id>/oauth2/token"
}

dbutils.fs.mount(
    source="abfss://container@storageaccount.dfs.core.windows.net/",
    mount_point="/mnt/data",
    extra_configs=configs
)
```

### Azure AD認証

```python
# サービスプリンシパル
spark.conf.set("fs.azure.account.auth.type.<storage-account>.dfs.core.windows.net", "OAuth")
spark.conf.set("fs.azure.account.oauth.provider.type.<storage-account>.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set("fs.azure.account.oauth2.client.id.<storage-account>.dfs.core.windows.net", "<app-id>")
spark.conf.set("fs.azure.account.oauth2.client.secret.<storage-account>.dfs.core.windows.net", "<secret>")
spark.conf.set("fs.azure.account.oauth2.client.endpoint.<storage-account>.dfs.core.windows.net",
    "https://login.microsoftonline.com/<tenant-id>/oauth2/token")

# SASトークン（一時アクセス）
spark.conf.set("fs.azure.sas.<container>.<storage-account>.blob.core.windows.net", "<sas-token>")
```

### Azure サービス連携

**Azure Synapse Analytics:**
```python
# Synapse SQL Pool
df = spark.read \
    .format("com.databricks.spark.sqldw") \
    .option("url", "jdbc:sqlserver://server.database.windows.net:1433") \
    .option("tempDir", "abfss://container@storage.dfs.core.windows.net/temp") \
    .option("forwardSparkAzureStorageCredentials", "true") \
    .option("dbTable", "schema.table") \
    .load()
```

**Azure Event Hubs:**
```python
# Event Hubsストリーム
connectionString = "Endpoint=sb://..."
ehConf = {
    'eventhubs.connectionString': spark.sparkContext._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connectionString)
}

df_stream = spark.readStream \
    .format("eventhubs") \
    .options(**ehConf) \
    .load()
```

**Azure Key Vault (Secrets):**
```python
# Databricks Secretsと統合
secret_value = dbutils.secrets.get(scope="<scope-name>", key="<key-name>")
```

## GCP統合

### ストレージ (GCS)

```python
# GCS読み込み
df = spark.read.parquet("gs://bucket-name/path/to/data/")

# GCS書き込み
df.write.mode("overwrite").parquet("gs://bucket-name/output/")

# GCSマウント
dbutils.fs.mount(
    source="gs://bucket-name/path",
    mount_point="/mnt/data"
)
```

### GCP IAM

```python
# サービスアカウント認証
spark.conf.set("google.cloud.auth.service.account.enable", "true")
spark.conf.set("google.cloud.auth.service.account.json.keyfile", "/path/to/keyfile.json")
```

### GCP サービス連携

**BigQuery:**
```python
# BigQuery読み込み
df = spark.read \
    .format("bigquery") \
    .option("table", "project.dataset.table") \
    .load()

# BigQuery書き込み
df.write \
    .format("bigquery") \
    .option("table", "project.dataset.output_table") \
    .option("temporaryGcsBucket", "temp-bucket") \
    .mode("overwrite") \
    .save()
```

**Pub/Sub:**
```python
# Pub/Subストリーム
df_stream = spark.readStream \
    .format("pubsub") \
    .option("subscription", "projects/project-id/subscriptions/sub-id") \
    .load()
```

## ネットワーク設定

### AWS

**VPC・PrivateLink:**
- VPCピアリングでプライベート接続
- PrivateLinkでS3/Glueへの安全なアクセス

**セキュリティグループ:**
- インバウンド: クラスター間通信
- アウトバウンド: S3、Glue、その他AWSサービス

### Azure

**VNet Injection:**
- DatabricksクラスターをVNetに配置
- プライベートエンドポイントでストレージアクセス

**Private Link:**
- Databricksワークスペースへのプライベートアクセス

### GCP

**VPC Service Controls:**
- プロジェクト境界の設定
- GCSへのプライベートアクセス

## ベストプラクティス

### ストレージアクセス

**セキュリティ:**
```python
# ✅ IAM/サービスプリンシパル使用（推奨）
# クラスター設定で認証情報を管理

# ❌ ハードコードされたキー（絶対避ける）
spark.conf.set("fs.s3a.access.key", "AKIAIOSFODNN7EXAMPLE")
```

**Secrets管理:**
```python
# ✅ Databricks Secrets使用
db_password = dbutils.secrets.get(scope="my-scope", key="db-password")

# ❌ ノートブックに直接記載
db_password = "my-secret-password"
```

### コスト最適化

**ストレージクラス選択:**
- **頻繁アクセス**: S3 Standard、ADLS Hot、GCS Standard
- **低頻度アクセス**: S3 IA、ADLS Cool、GCS Nearline
- **アーカイブ**: S3 Glacier、ADLS Archive、GCS Coldline

**データ転送コスト:**
- 同一リージョン内でDatabricksとストレージを配置
- VPCエンドポイント/Private Linkでインターネット経由を避ける

### パフォーマンス

**並列アクセス:**
```python
# パーティション数を調整
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128MB
```

**キャッシング:**
```python
# よく使うデータをローカルストレージにキャッシュ
df.cache()
```

## プラットフォーム選択ガイド

### AWS - 推奨ケース

- 既存AWS環境がある
- Redshift、Glue、Kinesisとの統合
- Gravitonインスタンスでコスト削減
- 幅広いリージョン展開

### Azure - 推奨ケース

- Microsoft製品エコシステム（Office 365、Power BI）
- Azure Synapse、Azure ML との統合
- Azure ADでの認証統合
- Entra IDガバナンス

### GCP - 推奨ケース

- BigQueryとの統合
- Vertex AIでのML
- Kubernetesベースの環境
- オープンソース重視

## まとめ

**クラウド統合の鍵:**

1. **セキュリティ** - IAM/サービスプリンシパルを使用
2. **ネットワーク** - プライベート接続でセキュアに
3. **コスト** - 同一リージョン、適切なストレージクラス
4. **パフォーマンス** - 並列化とキャッシング
5. **ガバナンス** - Secrets管理と監査ログ

各クラウドプロバイダーの強みを理解し、要件に応じて選択することが重要。
