---
name: aws-dynamodb
description: AWS DynamoDBを使用してスケーラブルなNoSQLデータベースを構築し、Single-Tableデザイン、パーティションキー設計、DAXキャッシングを活用する方法
---

# AWS DynamoDB スキル

## 概要

Amazon DynamoDBは、あらゆる規模で高速かつ予測可能なパフォーマンスを提供する、フルマネージドのNoSQLデータベースサービスです。シングルテーブルデザイン、効率的なパーティションキー設計、DAXキャッシングを駆使して、低レイテンシでスケーラブルなアプリケーションを構築します。

### 2025年の重要なアップデート

- **オンデマンド容量モード**: デフォルト推奨（予測不要、使った分だけ課金）
- **PartiQL**: SQL互換のクエリ言語でDynamoDBにアクセス
- **標準-IA (Infrequent Access)**: 低頻度アクセスデータで60%コスト削減
- **DynamoDB Streams + Lambda**: リアルタイムイベント駆動アーキテクチャ

## 主な使用ケース

### 1. シングルテーブルデザイン（2025年推奨）

複数のエンティティを1つのテーブルに格納して、結合なしで効率的にクエリします。

```bash
# シングルテーブルの作成
aws dynamodb create-table \
    --table-name AppData \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=GSI1PK,AttributeType=S \
        AttributeName=GSI1SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes file://gsi-config.json \
    --billing-mode PAY_PER_REQUEST \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --table-class STANDARD \
    --tags Key=Environment,Value=production

# gsi-config.json
cat > gsi-config.json << 'EOF'
[
  {
    "IndexName": "GSI1",
    "KeySchema": [
      {"AttributeName": "GSI1PK", "KeyType": "HASH"},
      {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
    ],
    "Projection": {"ProjectionType": "ALL"}
  }
]
EOF
```

**シングルテーブルデザインパターン**:

```python
"""
シングルテーブルデザインの実装例
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AppData')

# エンティティ1: ユーザー
# PK: USER#<user_id>
# SK: #METADATA
user_item = {
    'PK': 'USER#12345',
    'SK': '#METADATA',
    'EntityType': 'User',
    'Username': 'johndoe',
    'Email': 'john@example.com',
    'CreatedAt': datetime.now().isoformat(),
    'GSI1PK': 'USER',
    'GSI1SK': 'john@example.com'  # Emailで検索可能
}

# エンティティ2: 注文
# PK: USER#<user_id>
# SK: ORDER#<order_id>
order_item = {
    'PK': 'USER#12345',
    'SK': 'ORDER#67890',
    'EntityType': 'Order',
    'OrderId': '67890',
    'TotalAmount': 9999,
    'Status': 'pending',
    'CreatedAt': datetime.now().isoformat(),
    'GSI1PK': 'ORDER#PENDING',  # ステータス別に検索可能
    'GSI1SK': datetime.now().isoformat()
}

# エンティティ3: 商品
# PK: PRODUCT#<product_id>
# SK: #METADATA
product_item = {
    'PK': 'PRODUCT#111',
    'SK': '#METADATA',
    'EntityType': 'Product',
    'ProductName': 'Widget',
    'Price': 1999,
    'Category': 'Electronics',
    'GSI1PK': 'PRODUCT#CATEGORY#Electronics',
    'GSI1SK': 'Widget'
}

# データの挿入
table.put_item(Item=user_item)
table.put_item(Item=order_item)
table.put_item(Item=product_item)

# クエリ1: ユーザー情報と注文を1回のクエリで取得
response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={':pk': 'USER#12345'}
)
print(f"ユーザーと注文: {response['Items']}")

# クエリ2: Emailでユーザーを検索（GSI使用）
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :gsi1pk AND GSI1SK = :gsi1sk',
    ExpressionAttributeValues={
        ':gsi1pk': 'USER',
        ':gsi1sk': 'john@example.com'
    }
)
print(f"Emailで検索: {response['Items']}")

# クエリ3: ペンディング中の注文を取得（GSI使用）
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :gsi1pk',
    ExpressionAttributeValues={':gsi1pk': 'ORDER#PENDING'}
)
print(f"ペンディング注文: {response['Items']}")
```

### 2. トランザクション

複数の操作をACID準拠で実行します。

```python
"""
DynamoDBトランザクション
"""
import boto3

dynamodb = boto3.client('dynamodb')

# トランザクション書き込み
try:
    response = dynamodb.transact_write_items(
        TransactItems=[
            {
                # 在庫を減らす
                'Update': {
                    'TableName': 'AppData',
                    'Key': {
                        'PK': {'S': 'PRODUCT#111'},
                        'SK': {'S': '#METADATA'}
                    },
                    'UpdateExpression': 'SET Stock = Stock - :qty',
                    'ConditionExpression': 'Stock >= :qty',
                    'ExpressionAttributeValues': {
                        ':qty': {'N': '1'}
                    }
                }
            },
            {
                # 注文を作成
                'Put': {
                    'TableName': 'AppData',
                    'Item': {
                        'PK': {'S': 'USER#12345'},
                        'SK': {'S': 'ORDER#67890'},
                        'EntityType': {'S': 'Order'},
                        'ProductId': {'S': '111'},
                        'Quantity': {'N': '1'}
                    },
                    'ConditionExpression': 'attribute_not_exists(PK)'
                }
            }
        ]
    )
    print("トランザクション成功")
except dynamodb.exceptions.TransactionCanceledException as e:
    print(f"トランザクション失敗: {e}")
```

### 3. PartiQL（SQL互換クエリ）

SQLライクな構文でDynamoDBにアクセスします。

```python
"""
PartiQLでDynamoDBをクエリ
"""
import boto3

dynamodb = boto3.client('dynamodb')

# SELECT文
response = dynamodb.execute_statement(
    Statement="SELECT * FROM AppData WHERE PK = ? AND SK = ?",
    Parameters=[
        {'S': 'USER#12345'},
        {'S': '#METADATA'}
    ]
)
print(response['Items'])

# INSERT文
response = dynamodb.execute_statement(
    Statement="INSERT INTO AppData VALUE {'PK': ?, 'SK': ?, 'Username': ?}",
    Parameters=[
        {'S': 'USER#67890'},
        {'S': '#METADATA'},
        {'S': 'janedoe'}
    ]
)

# UPDATE文
response = dynamodb.execute_statement(
    Statement="UPDATE AppData SET Status = ? WHERE PK = ? AND SK = ?",
    Parameters=[
        {'S': 'completed'},
        {'S': 'USER#12345'},
        {'S': 'ORDER#67890'}
    ]
)

# トランザクション（PartiQL）
response = dynamodb.execute_transaction(
    TransactStatements=[
        {
            'Statement': "UPDATE AppData SET Stock = Stock - 1 WHERE PK = ? AND SK = ?",
            'Parameters': [{'S': 'PRODUCT#111'}, {'S': '#METADATA'}]
        },
        {
            'Statement': "INSERT INTO AppData VALUE {'PK': ?, 'SK': ?, 'ProductId': ?}",
            'Parameters': [{'S': 'USER#12345'}, {'S': 'ORDER#67890'}, {'S': '111'}]
        }
    ]
)
```

**重要**: PartiQLはインデックスされたフィールドのWHERE句を使用しないとフルテーブルスキャンになる

### 4. DynamoDB Streams + Lambda

データ変更をリアルタイムで処理します。

```python
"""
DynamoDB Streams + Lambda
"""
import json

def lambda_handler(event, context):
    """
    DynamoDB Streams イベントを処理
    """
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            print(f"新規アイテム: {new_image}")

            # 例: 新規ユーザー登録時にWelcomeメールを送信
            if new_image['EntityType']['S'] == 'User':
                send_welcome_email(new_image['Email']['S'])

        elif record['eventName'] == 'MODIFY':
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']

            # 例: 注文ステータスが変更されたら通知
            if old_image.get('Status', {}).get('S') != new_image.get('Status', {}).get('S'):
                notify_status_change(
                    order_id=new_image['OrderId']['S'],
                    old_status=old_image['Status']['S'],
                    new_status=new_image['Status']['S']
                )

        elif record['eventName'] == 'REMOVE':
            old_image = record['dynamodb']['OldImage']
            print(f"削除されたアイテム: {old_image}")

    return {'statusCode': 200}

def send_welcome_email(email):
    # SES経由でメール送信
    print(f"Welcomeメールを送信: {email}")

def notify_status_change(order_id, old_status, new_status):
    # SNS経由で通知
    print(f"注文{order_id}のステータス変更: {old_status} → {new_status}")
```

### 5. DAX（DynamoDB Accelerator）

マイクロ秒レイテンシのキャッシュを提供します。

```bash
# DAXクラスターの作成
aws dax create-cluster \
    --cluster-name production-dax \
    --node-type dax.r5.large \
    --replication-factor 3 \
    --iam-role-arn arn:aws:iam::123456789012:role/DAXServiceRole \
    --subnet-group dax-subnet-group \
    --security-group-ids sg-0123456789abcdef0 \
    --parameter-group default.dax1.0
```

```python
"""
DAXクライアントの使用
"""
from amazondax import AmazonDaxClient

# DAXクライアントの初期化
dax = AmazonDaxClient(
    endpoint_url='production-dax.abcdef.dax-clusters.ap-northeast-1.amazonaws.com:8111'
)

# DAX経由でアイテム取得（キャッシュヒット時はマイクロ秒レイテンシ）
response = dax.get_item(
    TableName='AppData',
    Key={
        'PK': {'S': 'USER#12345'},
        'SK': {'S': '#METADATA'}
    }
)
print(response['Item'])
```

**重要**: DAXはPartiQL APIをサポートしていない。従来のDynamoDB APIのみ使用可能。

### 6. グローバルテーブル

複数リージョンでマルチマスターレプリケーションを実現します。

```bash
# グローバルテーブルの作成
aws dynamodb create-global-table \
    --global-table-name GlobalAppData \
    --replication-group \
        RegionName=ap-northeast-1 \
        RegionName=us-east-1 \
        RegionName=eu-west-1

# 各リージョンでテーブルが自動作成・レプリケーション
# レプリケーションラグ: 通常1秒未満
```

### 7. Time to Live (TTL)

古いデータを自動削除してコストを削減します。

```bash
# TTLの有効化
aws dynamodb update-time-to-live \
    --table-name AppData \
    --time-to-live-specification "Enabled=true,AttributeName=TTL"
```

```python
"""
TTLの使用例
"""
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AppData')

# 7日後に自動削除されるアイテム
ttl = int((datetime.now() + timedelta(days=7)).timestamp())

table.put_item(
    Item={
        'PK': 'SESSION#abc123',
        'SK': '#METADATA',
        'UserId': '12345',
        'SessionData': {'key': 'value'},
        'TTL': ttl  # UNIX タイムスタンプ
    }
)
```

### 8. バックアップとリストア

ポイントインタイムリカバリで誤削除から保護します。

```bash
# Point-in-Time Recovery（PITR）の有効化
aws dynamodb update-continuous-backups \
    --table-name AppData \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# オンデマンドバックアップの作成
aws dynamodb create-backup \
    --table-name AppData \
    --backup-name AppData-backup-$(date +%Y%m%d)

# PITRでリストア
aws dynamodb restore-table-to-point-in-time \
    --source-table-name AppData \
    --target-table-name AppData-restored \
    --restore-date-time 2025-01-22T10:00:00Z

# バックアップからリストア
aws dynamodb restore-table-from-backup \
    --target-table-name AppData-restored \
    --backup-arn arn:aws:dynamodb:ap-northeast-1:123456789012:table/AppData/backup/01234567890123-abcdefgh
```

## 思考プロセス

DynamoDBの設計を行う際の段階的な思考プロセスです。

### フェーズ1: アクセスパターンの定義

```markdown
## アクセスパターンの洗い出し

### 必須アクセスパターン
1. ユーザーIDで情報を取得
2. Emailでユーザーを検索
3. ユーザーの全注文を取得
4. 注文IDで注文詳細を取得
5. ステータス別の注文一覧を取得
6. カテゴリ別の商品一覧を取得
7. 商品IDで商品詳細を取得

### 頻度分析
- 高頻度（1000 req/s以上）: 1, 4, 7 → DAX推奨
- 中頻度（100-1000 req/s）: 3, 5, 6
- 低頻度（<100 req/s）: 2

### 一貫性要件
- 強い一貫性: 注文作成、在庫更新
- 結果整合性で可: 商品一覧表示、検索
```

### フェーズ2: パーティションキー設計

```python
"""
パーティションキー設計ロジック
"""

def design_partition_key(access_patterns):
    """
    アクセスパターンに基づいてパーティションキー設計
    """
    designs = []

    # 原則1: 高カーディナリティのキーを選択
    # 悪い例: Status（値が数個しかない）
    # 良い例: UserId（ユニーク値が多い）

    # 原則2: アクセスパターンの80%をカバー
    # メインテーブル: UserId をベースに
    # GSI: 他のアクセスパターンをカバー

    # シングルテーブル設計
    main_table = {
        'PK': 'USER#<user_id> または PRODUCT#<product_id>',
        'SK': '#METADATA または ORDER#<order_id>',
        'reasoning': 'エンティティタイプ別にPKプレフィックスを使用'
    }

    # GSI1: Email検索、ステータス検索
    gsi1 = {
        'GSI1PK': 'USER または ORDER#<STATUS>',
        'GSI1SK': '<email> または <timestamp>',
        'access_patterns': ['Emailでユーザー検索', 'ステータス別注文一覧']
    }

    # GSI2: カテゴリ検索
    gsi2 = {
        'GSI2PK': 'PRODUCT#CATEGORY#<category>',
        'GSI2SK': '<product_name>',
        'access_patterns': ['カテゴリ別商品一覧']
    }

    return {
        'main_table': main_table,
        'gsi1': gsi1,
        'gsi2': gsi2
    }

# 使用例
access_patterns = [
    'ユーザーIDで取得',
    'Emailで検索',
    'ステータス別注文一覧'
]
design = design_partition_key(access_patterns)
print(f"推奨設計: {design}")
```

### フェーズ3: 容量モードの選択

```python
"""
オンデマンド vs プロビジョニング 選択ロジック
"""

def choose_capacity_mode(workload_characteristics):
    """
    ワークロード特性に基づいて容量モードを選択
    """
    # オンデマンド推奨ケース（2025年デフォルト）
    if workload_characteristics.traffic_pattern == 'unpredictable':
        return {
            'mode': 'ON_DEMAND',
            'reason': 'トラフィックが予測不可能',
            'cost': '使用した分だけ課金'
        }

    if workload_characteristics.is_new_application:
        return {
            'mode': 'ON_DEMAND',
            'reason': '新規アプリケーションで使用量が不明',
            'recommendation': '6ヶ月後にコスト分析してプロビジョニングを検討'
        }

    # プロビジョニング推奨ケース
    if workload_characteristics.avg_utilization > 35:
        # 35%以上の利用率ならプロビジョニングが安い
        return {
            'mode': 'PROVISIONED',
            'reason': '高い利用率で予測可能',
            'recommendation': 'Auto Scalingを有効化',
            'cost_savings': '30-50%'
        }

    # デフォルト
    return {
        'mode': 'ON_DEMAND',
        'reason': '2025年のデフォルト推奨'
    }

# 使用例
class WorkloadCharacteristics:
    traffic_pattern = 'unpredictable'
    is_new_application = True
    avg_utilization = 25

workload = WorkloadCharacteristics()
capacity_mode = choose_capacity_mode(workload)
print(f"推奨容量モード: {capacity_mode}")
```

### フェーズ4: パフォーマンス最適化

```python
"""
DynamoDBパフォーマンス最適化
"""

# ベストプラクティス1: バッチ操作を使用
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AppData')

# 悪い例: 個別にPutItem（25回のAPI呼び出し）
for i in range(25):
    table.put_item(Item={'PK': f'USER#{i}', 'SK': '#METADATA'})

# 良い例: BatchWriteItem（1回のAPI呼び出し）
with table.batch_writer() as batch:
    for i in range(25):
        batch.put_item(Item={'PK': f'USER#{i}', 'SK': '#METADATA'})

# ベストプラクティス2: プロジェクション式で必要な属性のみ取得
response = table.get_item(
    Key={'PK': 'USER#12345', 'SK': '#METADATA'},
    ProjectionExpression='Username, Email'  # 必要な属性のみ
)

# ベストプラクティス3: 並列スキャン
import concurrent.futures

def scan_segment(segment, total_segments):
    """セグメントをスキャン"""
    return table.scan(
        Segment=segment,
        TotalSegments=total_segments
    )

# 4つのセグメントで並列スキャン
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(scan_segment, i, 4) for i in range(4)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]
```

## ベストプラクティス（2025年版）

### 1. オンデマンド容量モードをデフォルトに

**推奨**: 新規テーブルはすべてオンデマンドで開始

```bash
# オンデマンドモードで作成
aws dynamodb create-table \
    --table-name AppData \
    --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
    --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
```

### 2. シングルテーブルデザインを採用

**理由**: 結合不要、レイテンシ削減、コスト削減

```python
# 複数のエンティティを1つのテーブルに
# PK/SKの命名規則を統一
# GSIで追加のアクセスパターンをカバー
```

### 3. TTLで古いデータを自動削除

```bash
# TTL有効化でストレージコスト削減
aws dynamodb update-time-to-live \
    --table-name AppData \
    --time-to-live-specification Enabled=true,AttributeName=TTL
```

### 4. Point-in-Time Recovery有効化

```bash
# 本番環境では必須
aws dynamodb update-continuous-backups \
    --table-name AppData \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### 5. DAXで頻繁な読み取りを最適化

```bash
# 読み取り頻度が高い場合はDAX推奨
# レイテンシ: ミリ秒 → マイクロ秒
```

### 6. DynamoDB Streamsでイベント駆動

```bash
# データ変更をリアルタイムで処理
# Lambda, Kinesis, OpenSearch Serviceと連携
```

## よくある落とし穴と対策

### 1. ホットパーティション

**症状**: スロットリングエラー（ProvisionedThroughputExceededException）

**原因**: 特定のパーティションキーへのアクセスが集中

**対策**:

```python
# 悪い例: StatusをパーティションキーにRUSTすると
# 'pending'に全注文が集中
# PK: 'pending'

# 良い例: UserIdをパーティションキーに
# PK: 'USER#12345'
# GSI1PK: 'ORDER#pending' (GSIで分散)
```

### 2. フルテーブルスキャン

**症状**: 高額な請求、遅いクエリ

**原因**: Query/GetItemの代わりにScanを使用

**対策**:

```python
# 悪い例: Scan
response = table.scan(
    FilterExpression='Username = :username',
    ExpressionAttributeValues={':username': 'johndoe'}
)

# 良い例: Query（GSI使用）
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :pk AND GSI1SK = :sk',
    ExpressionAttributeValues={
        ':pk': 'USER',
        ':sk': 'johndoe'
    }
)
```

### 3. GSIの過剰使用

**症状**: 高額なコスト

**原因**: 不要なGSIを複数作成

**対策**:

```bash
# GSIは必要最小限に（推奨: 2-3個まで）
# 各GSIは追加コストがかかる
```

### 4. アイテムサイズ制限超過

**症状**: アイテムサイズが400KBを超える

**対策**:

```python
# 大きいデータはS3に保存し、DynamoDBにはURLのみ格納
item = {
    'PK': 'USER#12345',
    'SK': 'PROFILE#IMAGE',
    'ImageUrl': 's3://bucket/images/profile.jpg',  # S3 URL
    'ImageSize': 2048000  # メタデータのみ
}
```

## 判断ポイント

### 容量モード選択マトリクス

| トラフィックパターン | 利用率 | 推奨モード | 理由 |
|-------------------|-------|----------|------|
| 予測不可能 | - | **オンデマンド** | 使用量に応じて自動スケーリング |
| 新規アプリケーション | - | **オンデマンド** | 使用量が不明 |
| スパイキー | <35% | **オンデマンド** | コスト効率が良い |
| 安定的 | >35% | **プロビジョニング** | オンデマンドより安い |
| 安定的 + 予測可能 | >50% | **プロビジョニング + Reserved Capacity** | 最大75%削減 |

### DAX使用判断

```python
"""
DAX使用判断ロジック
"""

def should_use_dax(workload):
    """
    DAXが必要かどうか判断
    """
    # DAX推奨ケース
    if workload.read_latency_requirement < 10:  # 10ms未満
        return True, 'マイクロ秒レイテンシが必要'

    if workload.read_qps > 10000:  # 10000 QPS以上
        return True, '高スループット要件'

    if workload.read_to_write_ratio > 10:  # 読み取り:書き込み = 10:1以上
        return True, '読み取り頻度が高い'

    # DAX不要ケース
    if workload.strongly_consistent_reads_required:
        return False, 'DAXは結果整合性のみサポート'

    if workload.uses_partiql:
        return False, 'DAXはPartiQLをサポートしていない'

    return False, 'DynamoDB直接アクセスで十分'

# 使用例
class Workload:
    read_latency_requirement = 5  # ms
    read_qps = 15000
    read_to_write_ratio = 20
    strongly_consistent_reads_required = False
    uses_partiql = False

workload = Workload()
use_dax, reason = should_use_dax(workload)
print(f"DAX使用: {use_dax}, 理由: {reason}")
```

## 検証ポイント

### 1. パフォーマンステスト

```python
"""
DynamoDBパフォーマンスベンチマーク
"""
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AppData')

# 書き込みベンチマーク
start = time.time()
with table.batch_writer() as batch:
    for i in range(1000):
        batch.put_item(Item={'PK': f'TEST#{i}', 'SK': '#METADATA', 'Data': 'x' * 1024})
write_time = time.time() - start

print(f"書き込み: 1000アイテム in {write_time:.2f}秒")
print(f"スループット: {1000 / write_time:.2f} items/秒")

# 読み取りベンチマーク
start = time.time()
for i in range(1000):
    table.get_item(Key={'PK': f'TEST#{i}', 'SK': '#METADATA'})
read_time = time.time() - start

print(f"読み取り: 1000アイテム in {read_time:.2f}秒")
print(f"スループット: {1000 / read_time:.2f} items/秒")
```

### 2. コスト分析

```bash
# CloudWatchメトリクスでRCU/WCUを確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name ConsumedReadCapacityUnits \
    --dimensions Name=TableName,Value=AppData \
    --start-time 2025-01-21T00:00:00Z \
    --end-time 2025-01-22T00:00:00Z \
    --period 3600 \
    --statistics Sum

# コスト最適化の判断
# オンデマンド: $1.25/百万WRU、$0.25/百万RRU
# プロビジョニング: $0.00065/WCU/時、$0.00013/RCU/時
```

## 他のスキルとの統合

### Lambdaスキルとの統合

```python
"""
Lambda + DynamoDB Streams
"""
def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            process_new_item(record['dynamodb']['NewImage'])
```

### API Gatewayスキルとの統合

```bash
# API Gateway → Lambda → DynamoDB
# RESTful API の構築
```

## リソース

### 公式ドキュメント

- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Single-Table Design](https://aws.amazon.com/blogs/compute/creating-a-single-table-design-with-amazon-dynamodb/)
- [PartiQL for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ql-reference.html)

### ツールとライブラリ

- [AWS CLI DynamoDB Commands](https://docs.aws.amazon.com/cli/latest/reference/dynamodb/)
- [Boto3 DynamoDB Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
- [DynamoDB Toolbox](https://github.com/jeremydaly/dynamodb-toolbox)
