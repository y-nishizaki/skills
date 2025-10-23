---
name: ec-data-automation
description: ECサイトのデータ分析基盤構築と業務自動化を支援するスキル。RPA、Python/スクリプト自動化、ETL/データパイプライン、BigQuery等のデータ基盤、レコメンドアルゴリズム、機械学習、AIエージェント（2025年）に使用される。
license: 完全な条項はLICENSE.txtを参照
---

# ECデータ・自動化スキル

このスキルは、ECサイトにおけるデータ基盤の構築、業務プロセスの自動化、AI/機械学習の活用を支援します。

## スキルの目的

ECサイトの運営効率を大幅に向上させるため、反復的な業務の自動化、データ分析基盤の構築、AIを活用したレコメンデーションや予測分析の実装を支援します。

## 使用タイミング

以下の場合にこのスキルを使用する：

- 反復作業を自動化したい
- データ分析基盤を構築する
- レコメンデーションエンジンを実装する
- 需要予測や価格最適化を行う
- ビッグデータ分析を導入する
- AI/機械学習を活用する
- データドリブンな意思決定体制を構築する

## RPA・スクリプト自動化

### EC運営における自動化対象業務

#### 在庫管理の自動化

**対象業務:**
- 在庫データの自動更新（1日複数回）
- 在庫監視とアラート
- 発注点到達時の自動通知
- マルチチャネル在庫同期

**実装例（Python）:**
```python
import requests
import smtplib

def check_inventory():
    # API から在庫データ取得
    response = requests.get('https://api.example.com/inventory')
    inventory = response.json()

    for item in inventory:
        if item['stock'] < item['reorder_point']:
            send_reorder_alert(item)

def send_reorder_alert(item):
    subject = f"発注推奨: {item['name']}"
    message = f"在庫が{item['stock']}個です。{item['reorder_quantity']}個の発注を推奨します。"
    # メール送信処理
    send_email(subject, message)
```

**効果:**
- 人的ミス削減
- 欠品防止
- 過剰在庫削減

#### 注文処理の自動化

**対象業務:**
- 注文受付から処理までの一連の流れ
- 注文データの入力
- 発送ラベル生成
- トラッキング番号登録
- 顧客への通知メール送信

**ツール:**
- Zapier / Make（ノーコード）
- Python + Selenium（複雑な処理）

**Zapier例:**
```
トリガー: Shopifyで新規注文
  ↓
アクション1: Google Sheets に注文データ追加
  ↓
アクション2: 配送業者APIで発送ラベル作成
  ↓
アクション3: 顧客にメール送信
```

**効果:**
- 処理時間50-70%削減
- 24時間自動処理
- スケーラビリティ

#### 価格モニタリング

**対象業務:**
- 競合サイトの価格収集
- 自社価格との比較
- 価格変動アラート

**実装（Python + Beautiful Soup）:**
```python
from bs4 import BeautifulSoup
import requests

def scrape_competitor_price(url, selector):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_element = soup.select_one(selector)
    price = parse_price(price_element.text)
    return price

# 定期実行（cron）
# 0 */6 * * * python price_monitor.py
```

**注意:**
- robots.txtの確認
- 利用規約遵守
- レート制限

#### データ入力・転記

**対象業務:**
- 商品情報の複数サイトへの登録
- レポート作成
- データ集計

### 2025年のトレンド: AIエージェントによるRPA

#### 従来のRPAの課題

- シナリオ作成が複雑
- UI変更に脆弱
- メンテナンスコスト高

#### AIエージェントの特徴

**Anthropic Computer Use（2024年10月発表）:**
- AIがPC上でGUI操作
- ブラウザからデータ読み取り→Excelに記載
- 自然言語での指示

**利点:**
- IT技術に不慣れでも構築可能
- 自然言語でメンテナンス
- 柔軟な対応

**実装例:**
```python
# AIエージェントへの指示
instruction = """
ECサイトの注文一覧ページから、
今日の注文データをすべて取得して、
Excelファイル「daily_orders.xlsx」に保存してください。
"""

# AIエージェントが自律的に実行
agent.execute(instruction)
```

### Python と RPA の使い分け

**Python:**
- 柔軟なデータ処理
- AI連携
- API統合
- 複雑なロジック

**RPA:**
- 直感的な画面操作
- システム間の橋渡し
- レガシーシステム連携

**推奨:**
適材適所で使い分け、組み合わせることが自動化成功の鍵。

## ETL・データ基盤設計

### データパイプラインの必要性

**課題:**
- データが各システムに分散
  - ECプラットフォーム（Shopify、Magento）
  - Google Analytics
  - 広告プラットフォーム（Google Ads、Meta Ads）
  - CRM
  - メールマーケティングツール

**解決:**
データ統合プラットフォーム構築。

### ETL（Extract, Transform, Load）

#### Extract（抽出）

**データソース:**
- ECプラットフォームAPI
- Google Analytics Data API
- 広告プラットフォームAPI
- データベース（MySQL、PostgreSQL）
- CSV/Excelファイル

**実装例（Python）:**
```python
import requests

# Shopify API から注文データ取得
def extract_shopify_orders():
    url = 'https://your-store.myshopify.com/admin/api/2024-01/orders.json'
    headers = {'X-Shopify-Access-Token': 'your-token'}
    response = requests.get(url, headers=headers)
    return response.json()['orders']
```

#### Transform（変換）

**処理:**
- データクレンジング（重複削除、欠損値処理）
- データ正規化
- 集計
- 計算フィールド追加

**実装例（Pandas）:**
```python
import pandas as pd

def transform_orders(orders):
    df = pd.DataFrame(orders)

    # 日付変換
    df['created_at'] = pd.to_datetime(df['created_at'])

    # 売上計算
    df['revenue'] = df['line_items'].apply(lambda x: sum([item['price'] * item['quantity'] for item in x]))

    # 不要カラム削除
    df = df[['id', 'created_at', 'customer_id', 'revenue']]

    return df
```

#### Load（ロード）

**格納先:**
- データウェアハウス（BigQuery、Snowflake、Redshift）
- データベース（PostgreSQL）
- データレイク（S3）

**実装例（BigQuery）:**
```python
from google.cloud import bigquery

def load_to_bigquery(df, table_id):
    client = bigquery.Client()
    job = client.load_table_from_dataframe(df, table_id)
    job.result()  # 完了待ち
    print(f"Loaded {len(df)} rows to {table_id}")
```

### データパイプライン自動化

**オーケストレーションツール:**
- **Apache Airflow**: 複雑なワークフロー
- **Prefect**: モダンな代替
- **Cloud Composer**: Google Cloud版Airflow

**例（Airflow DAG）:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG(
    'ec_data_pipeline',
    schedule_interval='0 1 * * *',  # 毎日1時実行
    start_date=datetime(2025, 1, 1)
)

extract_task = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_shopify_orders,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_orders',
    python_callable=transform_orders,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_to_bigquery',
    python_callable=load_to_bigquery,
    dag=dag
)

extract_task >> transform_task >> load_task
```

### クラウドプラットフォーム

#### BigQuery（2025年AI統合プラットフォーム）

**特徴:**
- 自律型データ基盤
- AIエージェント運用可能
- SQL、Python、Spark統合IDE（BigQuery Studio）
- Gemini in BigQuery（自然言語→SQL生成）

**例（自然言語クエリ）:**
```
ユーザー: 「先月の商品カテゴリー別売上トップ10を教えて」

Gemini: 以下のSQLを生成
SELECT
  category,
  SUM(revenue) as total_revenue
FROM `project.dataset.orders`
WHERE DATE(created_at) BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10
```

**ETL自動化:**
- Dataform（dbt互換）
- Scheduled queries
- データ転送サービス（Google Ads、GA4等）

#### Snowflake

**特徴:**
- マルチクラウド対応
- データシェアリング
- 時間遡行（Time Travel）

#### AWS（Redshift + Glue）

**構成:**
- Redshift: データウェアハウス
- Glue: ETLサービス
- S3: データレイク

### データモデリング

**スタースキーマ例（EC）:**

```
ファクトテーブル: orders_fact
- order_id (PK)
- customer_key (FK)
- product_key (FK)
- date_key (FK)
- quantity
- revenue
- cost

ディメンションテーブル:
- dim_customer (customer_key, name, email, segment)
- dim_product (product_key, name, category, brand)
- dim_date (date_key, date, month, quarter, year)
```

**利点:**
- クエリパフォーマンス向上
- 分析しやすい構造
- スケーラビリティ

## レコメンドアルゴリズム

### レコメンデーションの重要性

**効果:**
- CVR向上: 10-30%
- AOV（平均注文単価）向上: 5-15%
- ユーザーエンゲージメント向上

### 主要アルゴリズム

#### 1. 協調フィルタリング

**ユーザーベース:**
「あなたと似たユーザーが購入した商品」

**アイテムベース:**
「この商品を購入した人はこちらも購入」

**実装例（Surprise ライブラリ）:**
```python
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate

# データ読み込み
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'product_id', 'rating']], reader)

# モデル訓練
algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5)

# 予測
algo.fit(data.build_full_trainset())
prediction = algo.predict(user_id='123', item_id='456')
```

#### 2. コンテンツベースフィルタリング

商品属性（カテゴリー、ブランド、価格帯等）に基づく推奨。

**実装例（TF-IDF）:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 商品説明文からベクトル化
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(products_df['description'])

# 類似度計算
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 類似商品取得
def get_similar_products(product_id, top_n=5):
    idx = products_df[products_df['id'] == product_id].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]  # 自分自身を除く
    product_indices = [i[0] for i in sim_scores]
    return products_df.iloc[product_indices]
```

#### 3. ハイブリッド

協調フィルタリングとコンテンツベースの組み合わせ。

**利点:**
- コールドスタート問題の軽減
- 精度向上

#### 4. ディープラーニング

**手法:**
- Neural Collaborative Filtering
- Transformer ベース
- グラフニューラルネットワーク

**事例:**
ZOZOでディープラーニングを活用したレコメンドエンジンの精度向上。

### プラットフォーム活用

#### Amazon Personalize

**特徴:**
- AWS提供のマネージドサービス
- 自動MLパイプライン
- リアルタイムレコメンド

**実装:**
```python
import boto3

personalize = boto3.client('personalize-runtime')

response = personalize.get_recommendations(
    campaignArn='arn:aws:personalize:region:account-id:campaign/campaign-name',
    userId='123'
)

recommended_items = response['itemList']
```

**自動化:**
AWS Glueでデータ更新を自動化。

#### カスタム実装

**スタック:**
- Python（Scikit-learn、TensorFlow、PyTorch）
- Spark MLlib（大規模データ）
- Redis（リアルタイム配信）

## AI/機械学習活用

### 需要予測

**目的:**
- 在庫最適化
- 仕入れ計画
- 人員配置

**手法:**
- ARIMA（時系列分析）
- Prophet（Facebook製）
- LSTM（ディープラーニング）

**実装例（Prophet）:**
```python
from fbprophet import Prophet

# データ準備
df = pd.DataFrame({
    'ds': dates,  # 日付
    'y': sales    # 売上
})

# モデル訓練
model = Prophet()
model.fit(df)

# 予測（30日先）
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
```

### 動的価格設定

**目的:**
- 利益最大化
- 需給バランス調整

**要因:**
- 需要予測
- 競合価格
- 在庫状況
- 顧客セグメント

**手法:**
- 強化学習
- 多腕バンディット

**倫理的配慮:**
- 透明性
- 公正性（差別的価格設定の回避）

### 顧客生涯価値（LTV）予測

**目的:**
- 高価値顧客の早期発見
- マーケティング投資最適化

**特徴量:**
- 初回購入金額
- 購入頻度（初期）
- 平均注文単価
- カテゴリー嗜好
- エンゲージメント（メール開封率等）

**モデル:**
- 線形回帰
- ランダムフォレスト
- XGBoost

### チャーン予測

**目的:**
- 離脱リスク顧客の特定
- プロアクティブな施策

**特徴量:**
- 最終購入日からの経過日数
- 購入頻度の変化
- サイト訪問頻度
- メール開封率

**モデル:**
- ロジスティック回帰
- ランダムフォレスト
- ニューラルネットワーク

### 不正検出

**目的:**
- 不正注文の検出
- チャージバック削減

**異常パターン:**
- 短時間の大量注文
- 異常な配送先
- 高額商品の初回購入
- IPアドレス・デバイスの不一致

**手法:**
- 異常検知（Isolation Forest）
- ルールベースエンジン
- 機械学習モデル

**プラットフォーム:**
- Signifyd
- Riskified
- PayPal（不正検知機能）

## パーソナライゼーション

### 実装レベル

#### レベル1: セグメントベース

```python
if customer.segment == 'VIP':
    show_exclusive_products()
elif customer.segment == 'New':
    show_popular_products()
```

#### レベル2: 行動ベース

```python
# 閲覧履歴に基づく
viewed_categories = get_viewed_categories(customer_id)
recommended_products = get_products_by_categories(viewed_categories)
```

#### レベル3: AIパーソナライズ

```python
# リアルタイムMLモデル
features = {
    'customer_id': customer_id,
    'time_of_day': current_hour,
    'device': device_type,
    'recent_views': recent_product_ids,
    'cart_value': current_cart_value
}

recommended_products = ml_model.predict(features)
```

### A/Bテスト

パーソナライゼーションの効果を測定：

```python
# A: コントロール（パーソナライズなし）
# B: パーソナライズあり

if customer_id % 2 == 0:
    show_personalized_content()  # B群
else:
    show_default_content()  # A群
```

## リアルタイムデータ処理

### ストリーミング処理

**ユースケース:**
- リアルタイムレコメンド
- リアルタイム在庫更新
- リアルタイムダッシュボード

**ツール:**
- Apache Kafka
- Google Cloud Pub/Sub
- AWS Kinesis

**アーキテクチャ例:**
```
ECサイト
  ↓ (イベント送信)
Kafka
  ↓ (リアルタイム処理)
Stream Processing (Spark Streaming / Flink)
  ↓ (保存)
BigQuery / Redshift
  ↓ (可視化)
ダッシュボード（Tableau / Looker）
```

## データガバナンス

### プライバシー保護

**GDPR対応:**
- データ削除権（Right to be Forgotten）
- データポータビリティ
- 同意管理

**実装:**
```python
def anonymize_customer_data(customer_id):
    # PII（個人識別情報）の匿名化
    db.execute("""
        UPDATE customers
        SET email = CONCAT('deleted_', id, '@example.com'),
            name = 'Deleted User',
            phone = NULL
        WHERE id = %s
    """, (customer_id,))
```

### データ品質管理

**検証:**
- スキーマ検証
- 範囲チェック
- 重複チェック

**Great Expectations（ライブラリ）:**
```python
import great_expectations as ge

df = ge.read_csv('orders.csv')
df.expect_column_values_to_be_between('price', min_value=0, max_value=1000000)
df.expect_column_values_to_be_unique('order_id')
```

## まとめ

ECデータ・自動化では以下が重要：

1. **業務自動化**: RPA、Python、AIエージェント（2025年）
2. **データ基盤**: ETL、データウェアハウス（BigQuery等）
3. **AI/ML活用**: レコメンド、需要予測、パーソナライゼーション
4. **リアルタイム処理**: ストリーミングデータ処理
5. **データガバナンス**: プライバシー保護、品質管理
6. **継続的改善**: A/Bテスト、効果測定

これらを統合し、データドリブンで効率的なEC運営を実現する。自動化により人的リソースを戦略的業務にシフトし、AIにより顧客体験を向上させる。
