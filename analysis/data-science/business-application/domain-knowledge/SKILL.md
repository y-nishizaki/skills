---
name: "ドメイン知識"
description: "業界特有のデータ構造・指標の理解。専門的な洞察の獲得"
---

# ドメイン知識: 業界の文脈を理解する

## このスキルを使う場面

- 新しい業界のデータ分析を始めるとき
- 業界特有の指標を理解したい
- ビジネス課題を深く理解したい
- 専門家と対等に議論したい

## ドメイン知識の習得

### 1. 業界の基礎理解

**ビジネスモデル**

- 収益構造
- 顧客セグメント
- 価値提供
- コスト構造

**業界特有の用語**

- 専門用語集の作成
- 略語の理解
- KPIの意味

**規制・法律**

- 業界規制
- データ利用制限
- コンプライアンス

### 2. 学習方法

**社内リソース**

- 営業・マーケチームとの対話
- 社内ドキュメント
- 過去のプロジェクト
- 社内トレーニング

**外部リソース**

- 業界レポート
- 専門書・論文
- セミナー・カンファレンス
- オンラインコース

**実践**

- プロダクトを使ってみる
- 顧客の視点で体験
- 競合分析
- 現場観察

## 業界別の主要指標

### EC・小売

```python
# 主要KPI
conversion_rate = orders / sessions
average_order_value = revenue / orders
cart_abandonment_rate = (carts - orders) / carts
customer_lifetime_value = avg_purchase_value * avg_frequency * avg_lifespan

# RFM分析
rfm = df.groupby('customer_id').agg({
    'order_date': lambda x: (datetime.now() - x.max()).days,  # Recency
    'order_id': 'count',  # Frequency
    'amount': 'sum'  # Monetary
})
```

### SaaS

```python
# 主要KPI
monthly_recurring_revenue = sum(subscriptions)
churn_rate = churned_customers / total_customers
customer_acquisition_cost = marketing_cost / new_customers
ltv_cac_ratio = lifetime_value / customer_acquisition_cost

# コホート分析
cohort = df.groupby(['cohort_month', 'month_number'])['retained'].mean()
```

### 金融

```python
# 主要KPI
default_rate = defaults / total_loans
portfolio_at_risk = overdue_loans_value / total_portfolio_value
net_interest_margin = (interest_income - interest_expense) / assets

# リスク指標
value_at_risk = np.percentile(returns, 5)  # 95% VaR
sharpe_ratio = (return - risk_free_rate) / std_dev
```

### 医療・ヘルスケア

```python
# 主要KPI
patient_readmission_rate = readmissions / total_admissions
average_length_of_stay = total_days / admissions
bed_occupancy_rate = occupied_beds / total_beds

# 診断精度
sensitivity = true_positives / (true_positives + false_negatives)
specificity = true_negatives / (true_negatives + false_positives)
```

## ドメイン知識の活用

### 1. 特徴量エンジニアリング

```python
# EC: 購買行動の特徴
df['days_since_last_purchase'] = (datetime.now() - df['last_purchase']).dt.days
df['purchase_frequency'] = df.groupby('customer_id')['order_id'].transform('count')
df['avg_basket_size'] = df.groupby('customer_id')['items'].transform('mean')

# 時系列: 季節性
df['is_holiday_season'] = df['month'].isin([11, 12])
df['day_of_week'] = df['date'].dt.dayofweek
df['is_payday'] = df['date'].dt.day.isin([15, 25])
```

### 2. 異常値の判断

```python
# ドメイン知識に基づく妥当性チェック

# EC: 異常な注文
abnormal_orders = df[
    (df['order_value'] > 1000000) |  # 100万円以上
    (df['items_count'] > 100) |  # 100個以上
    (df['shipping_cost'] > df['order_value'] * 0.5)  # 送料が異常
]

# 医療: 生理学的に不可能な値
invalid_vitals = df[
    (df['heart_rate'] > 300) |
    (df['heart_rate'] < 30) |
    (df['body_temp'] > 45) |
    (df['body_temp'] < 30)
]
```

### 3. ビジネスルールの実装

```python
# SaaS: チャーンリスクスコアリング
def calculate_churn_risk(df):
    risk_score = 0

    # ログイン頻度の低下
    if df['login_last_30days'] < df['login_prev_30days'] * 0.5:
        risk_score += 30

    # サポートチケットの増加
    if df['tickets_last_month'] > 5:
        risk_score += 20

    # 支払い遅延
    if df['payment_delayed']:
        risk_score += 40

    # 使用機能の減少
    if df['features_used'] < 3:
        risk_score += 10

    return risk_score

df['churn_risk_score'] = df.apply(calculate_churn_risk, axis=1)
```

## ドメインエキスパートとの協働

### 1. 効果的な質問

**理解のための質問**:

- 「この指標はなぜ重要ですか？」
- 「通常の範囲はどれくらいですか？」
- 「季節性はありますか？」

**検証のための質問**:

- 「この結果は妥当ですか？」
- 「想定外の点はありますか？」
- 「これは実装可能ですか？」

### 2. ワークショップの実施

- 現状の課題ヒアリング
- データ理解の共有
- 仮説の議論
- 制約条件の確認

### 3. 継続的な学習

- 定期的な情報交換
- 新しいトレンドのキャッチアップ
- 失敗事例からの学び

## 注意点

### データの特性理解

- 収集方法の理解
- バイアスの認識
- 欠損の意味
- 更新頻度

### ビジネスコンテキスト

- 意思決定プロセス
- 実装の制約
- 組織文化
- 過去の取り組み

### 倫理的配慮

- 業界特有の倫理規定
- プライバシー保護
- 公平性の考慮
- 透明性の確保

## ベストプラクティス

- 謙虚に学ぶ姿勢
- 専門家を尊重
- データと経験を融合
- 継続的な知識更新
- 業界トレンドの把握

## 検証ポイント

- [ ] 業界のビジネスモデルを理解した
- [ ] 主要KPIの意味を知っている
- [ ] 業界特有の制約を認識した
- [ ] ドメインエキスパートと対話できる
- [ ] ビジネス文脈で分析できる
