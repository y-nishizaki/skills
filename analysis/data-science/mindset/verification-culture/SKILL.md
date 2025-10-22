---
name: "検証文化"
description: "思い込みを捨ててデータで確かめる習慣。証拠に基づく意思決定"
---

# 検証文化: データ駆動の意思決定

## このスキルを使う場面

- 重要な意思決定をするとき
- 直感や経験則に頼りそうなとき
- ステークホルダーの意見が分かれるとき
- 施策の効果を測定するとき

## 検証文化の原則

### 1. データで語る

**悪い例**:
「このキャンペーンは成功したと思います」

**良い例**:
「このキャンペーンにより、コンバージョン率が15%向上しました（95%信頼区間: 12-18%）。ROIは250%でした」

### 2. 仮定を明示する

```python
# 分析の仮定を明確に記録

ASSUMPTIONS = {
    'analysis_period': '2024-01-01 to 2024-12-31',
    'excluded_data': 'テストユーザー、社内アクセス',
    'missing_data_treatment': '欠損値は平均値で補完',
    'outlier_threshold': '99パーセンタイル以上を除外',
    'statistical_significance': 'α = 0.05'
}

# ドキュメントに残す
```


### 3. 再現可能な分析

```python
# 分析のすべてのステップをコードで記録

# 設定
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# データ読み込み
df = pd.read_csv('data.csv')
print(f"Initial data shape: {df.shape}")

# 前処理
df = df.dropna(subset=['key_column'])
print(f"After dropping nulls: {df.shape}")

# 分析
result = analyze(df)

# 結果保存
result.to_csv(f'result_{datetime.now():%Y%m%d}.csv')
```


## 証拠に基づく意思決定

### 1. HiPPO（Highest Paid Person's Opinion）を避ける

**シナリオ**: 経営層「直感的にAプランが良いと思う」

**検証アプローチ**:

```python
# データで比較
comparison = pd.DataFrame({
    'Plan': ['A', 'B'],
    'Expected ROI': [calculate_roi('A'), calculate_roi('B')],
    'Risk': [assess_risk('A'), assess_risk('B')],
    'Implementation Cost': [cost('A'), cost('B')]
})

print(comparison)

# A/Bテストで実証
run_ab_test(plan_a, plan_b, duration=14)
```


### 2. 確証バイアスへの対処

```python
# 自分の仮説に反するデータも積極的に探す

# 仮説: 新機能は全てのユーザーに好まれる

# 検証1: 全体的な評価
overall_rating = df['rating'].mean()

# 検証2: セグメント別（反例を探す）
segment_ratings = df.groupby('user_segment')['rating'].mean()
print(segment_ratings.sort_values())

# 検証3: ネガティブフィードバックの分析
negative_feedback = df[df['rating'] < 3]
print(f"Negative feedback rate: {len(negative_feedback) / len(df):.1%}")
print("\nCommon complaints:")
print(negative_feedback['comment'].value_counts().head())
```


### 3. 小さく試して学ぶ

```python
# 大規模展開前に小規模テスト

# フェーズ1: パイロット（10%）
pilot_users = df.sample(frac=0.1, random_state=42)
pilot_result = test_feature(pilot_users)

# 評価
if pilot_result['success_rate'] > 0.7:
    # フェーズ2: 拡大（30%）
    expanded_users = df.sample(frac=0.3, random_state=42)
    expanded_result = test_feature(expanded_users)

    if expanded_result['success_rate'] > 0.7:
        # フェーズ3: 全体展開
        full_rollout()
else:
    print("Pilot failed. Analyzing reasons...")
    analyze_failure(pilot_result)
```


## 測定と評価

### 1. 適切な指標を選ぶ

```python
# 北極星指標（North Star Metric）とサポート指標

metrics = {
    'north_star': {
        'name': 'Monthly Active Users',
        'current': 50000,
        'target': 60000,
        'tracking': 'daily'
    },
    'supporting': [
        {'name': 'Daily Active Users', 'current': 15000},
        {'name': 'Session Duration', 'current': 8.5},  # minutes
        {'name': 'Feature Adoption Rate', 'current': 0.35}
    ],
    'health': [
        {'name': 'Churn Rate', 'current': 0.05},
        {'name': 'Bug Report Rate', 'current': 0.02}
    ]
}
```


### 2. ベースラインの確立

```python
# 改善を測定するには基準が必要

# ベースライン期間
baseline_start = '2024-01-01'
baseline_end = '2024-01-31'

baseline_metrics = df[
    (df['date'] >= baseline_start) &
    (df['date'] <= baseline_end)
].agg({
    'conversion_rate': 'mean',
    'average_order_value': 'mean',
    'customer_satisfaction': 'mean'
})

print("Baseline metrics:")
print(baseline_metrics)

# 施策後の比較
after_metrics = df[df['date'] >= '2024-02-01'].agg({
    'conversion_rate': 'mean',
    'average_order_value': 'mean',
    'customer_satisfaction': 'mean'
})

# 改善率
improvement = (after_metrics - baseline_metrics) / baseline_metrics * 100
print(f"\nImprovement:")
print(improvement)
```


### 3. 統計的有意性の確認

```python
# 単なる偶然か、真の効果か？

from scipy.stats import ttest_ind

baseline_data = df[df['period'] == 'baseline']['metric']
after_data = df[df['period'] == 'after']['metric']

t_stat, p_value = ttest_ind(baseline_data, after_data)

if p_value < 0.05:
    effect_size = (after_data.mean() - baseline_data.mean()) / baseline_data.std()
    print(f"Statistically significant improvement (p={p_value:.4f})")
    print(f"Effect size (Cohen's d): {effect_size:.3f}")
else:
    print(f"No significant difference (p={p_value:.4f})")
```


## 実験と学習

### 1. 失敗を歓迎する

```python
# 失敗からの学びを記録

experiment_log = {
    'experiment_id': 'EXP-2024-001',
    'hypothesis': '割引率を上げれば売上が増える',
    'expected_outcome': '売上20%増',
    'actual_outcome': '売上5%増、利益15%減',
    'conclusion': '棄却 - 過度な割引は利益を圧迫',
    'learnings': [
        '顧客は割引に過度に依存しない',
        '利益率を考慮した施策が重要',
        '次回は段階的な割引テストを実施'
    ],
    'next_actions': [
        'ロイヤルティプログラムを検討',
        '商品バンドルの効果を測定'
    ]
}

# データベースに保存
save_experiment_log(experiment_log)
```


### 2. ポストモーテム（事後分析）

```markdown
## ポストモーテム: キャンペーンX

### 目標
- 新規顧客獲得数: 1000人
- CAC（顧客獲得コスト）: $50以下

### 実績
- 新規顧客獲得数: 750人（達成率75%）
- CAC: $65（目標超過30%）

### うまくいったこと
- SNS広告のクリエイティブが好評
- ランディングページのCVRが予想以上

### うまくいかなかったこと
- ターゲティングが広すぎた
- 競合のキャンペーンと重複

### 学んだこと
1. より narrow なターゲティングが必要
2. 競合分析を事前に徹底する
3. 段階的な予算投下でリスク管理

### 次回への改善
- ターゲットオーディエンスを詳細に定義
- 競合モニタリングツールの導入
- A/Bテストを並行実施
```


## 組織への浸透

### 1. データリテラシーの向上

```python
# チーム向けダッシュボード

import plotly.graph_objects as go
from dash import Dash, dcc, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Weekly KPI Dashboard'),

    # 主要指標
    html.Div([
        html.H3('North Star Metric: MAU'),
        dcc.Graph(figure=create_mau_chart(df))
    ]),

    # サポート指標
    html.Div([
        html.H3('Supporting Metrics'),
        dcc.Graph(figure=create_supporting_metrics(df))
    ]),

    # アラート
    html.Div(id='alerts', children=generate_alerts(df))
])
```


### 2. 意思決定プロセスの標準化

```markdown
## 意思決定フレームワーク

### ステップ1: 問題定義
- 何を決定する必要があるか？
- なぜ重要か？
- 期限は？

### ステップ2: データ収集
- どのデータが必要か？
- データは信頼できるか？
- データに欠けている点は？

### ステップ3: 分析
- 複数の選択肢を分析
- 定量的・定性的評価
- リスクの評価

### ステップ4: 推奨事項
- データに基づく推奨
- トレードオフの明示
- 実装計画

### ステップ5: 意思決定
- 決定とその理由を記録
- 責任者を明確に
- 次のステップ

### ステップ6: 検証
- KPIで効果を測定
- 定期的なレビュー
- 必要に応じて修正
```


### 3. 透明性の確保

```python
# 分析結果の共有

def create_analysis_report(analysis_id):
    report = {
        'title': 'Customer Segmentation Analysis',
        'date': datetime.now(),
        'analyst': 'Data Science Team',
        'objective': '顧客セグメントを特定し、ターゲティング戦略を策定',
        'data_source': 'CRM database (2024-01-01 to 2024-12-31)',
        'methodology': 'K-means clustering with 5 features',
        'key_findings': [
            'High-value segment: 20% of customers, 60% of revenue',
            'At-risk segment: 15% showing churn signals',
            'Growth segment: 30% with increasing engagement'
        ],
        'recommendations': [
            'Loyalty program for high-value segment',
            'Re-engagement campaign for at-risk',
            'Upsell strategy for growth segment'
        ],
        'limitations': [
            'Based on historical data only',
            'External factors not considered',
            'Segments may evolve over time'
        ],
        'next_steps': [
            'A/B test recommendations',
            'Monthly segment review',
            'Refine segmentation model'
        ]
    }

    # Markdown レポート生成
    generate_markdown_report(report)

    # Slack/Email で共有
    share_report(report)
```


## ベストプラクティス

### データで意思決定

- 直感ではなくデータ
- 複数の視点で分析
- 反証を積極的に探す

### 継続的な改善

- 小さく試す
- 早く失敗する
- 学びを記録する

### 透明性

- 分析過程を共有
- 仮定を明示
- 制約を認める

### コラボレーション

- チーム内で議論
- 多様な視点を取り入れる
- 知見を共有する

## 検証ポイント

- [ ] データで意思決定している
- [ ] 仮定を明示している
- [ ] 再現可能な分析
- [ ] 統計的有意性を確認している
- [ ] 失敗から学んでいる
- [ ] 透明性を確保している
- [ ] チームで検証文化を醸成している
