---
name: "因果推論・実験設計"
description: "A/Bテスト、介入効果分析。因果関係の特定"
---

# 因果推論・実験設計: 原因と結果を見極める

## このスキルを使う場面

- 施策の効果を測定したい
- 因果関係を特定したい
- A/Bテストを設計・分析したい
- 観測データから因果を推論したい

## A/Bテスト

### 1. 実験設計

```python
# サンプルサイズ計算
from statsmodels.stats.power import tt_ind_solve_power

required_n = tt_ind_solve_power(
    effect_size=0.2,  # 検出したい効果
    alpha=0.05,  # 有意水準
    power=0.8  # 検出力
)
print(f"Required sample size per group: {int(required_n)}")
```


### 2. ランダム割り当て

```python
import numpy as np

np.random.seed(42)
df['group'] = np.random.choice(['A', 'B'], size=len(df), p=[0.5, 0.5])
```


### 3. 分析

```python
from scipy.stats import ttest_ind

group_a = df[df['group'] == 'A']['conversion']
group_b = df[df['group'] == 'B']['conversion']

t_stat, p_value = ttest_ind(group_a, group_b)

# 効果量
cohens_d = (group_b.mean() - group_a.mean()) / pooled_std

print(f"p-value: {p_value:.4f}")
print(f"Effect size: {cohens_d:.3f}")
```


## 準実験デザイン

### 1. 差分の差分法（DID）

```python
# DID分析
import statsmodels.formula.api as smf

model = smf.ols(
    'outcome ~ treated + post + treated:post',
    data=df
).fit()

did_effect = model.params['treated:post']
print(f"DID Effect: {did_effect:.3f}")
```


### 2. 傾向スコアマッチング

```python
from sklearn.neighbors import NearestNeighbors

# 傾向スコアの推定
propensity_model = LogisticRegression()
propensity_model.fit(X, treatment)
propensity_scores = propensity_model.predict_proba(X)[:, 1]

# マッチング
treated = df[df['treatment'] == 1]
control = df[df['treatment'] == 0]

knn = NearestNeighbors(n_neighbors=1)
knn.fit(control[['propensity_score']])
matches = knn.kneighbors(treated[['propensity_score']])
```


### 3. 回帰不連続デザイン（RDD）

```python
# RDD分析
cutoff = 50
df['above'] = (df['score'] >= cutoff).astype(int)
df['score_centered'] = df['score'] - cutoff

model = smf.ols(
    'outcome ~ above + score_centered + above:score_centered',
    data=df
).fit()

rdd_effect = model.params['above']
```


## 因果推論のフレームワーク

### 1. 因果グラフ（DAG）

```python
# DoWhy ライブラリ
import dowhy

# 因果モデルの定義
model = dowhy.CausalModel(
    data=df,
    treatment='treatment',
    outcome='outcome',
    common_causes=['confounder1', 'confounder2']
)

# 因果効果の推定
identified_estimand = model.identify_effect()
estimate = model.estimate_effect(identified_estimand)

print(estimate)
```


### 2. 媒介分析

```python
# 直接効果と間接効果
from statsmodels.regression.linear_model import OLS

# Total effect
total_model = OLS(outcome, treatment).fit()

# Direct effect (媒介変数を含む)
direct_model = OLS(outcome, [treatment, mediator]).fit()

# Indirect effect
indirect_effect = total_effect - direct_effect
```


## 実験デザインの原則

### 1. ランダム化

- 完全ランダム化
- 層化ランダム化
- クラスターランダム化

### 2. バランスチェック

```python
# 共変量のバランス確認
for var in covariates:
    t_stat, p_value = ttest_ind(
        df[df['group'] == 'A'][var],
        df[df['group'] == 'B'][var]
    )
    print(f"{var}: p={p_value:.3f}")
```


### 3. サンプルサイズ

- 十分な検出力（80%以上推奨）
- 期待される効果量
- 有意水準（通常0.05）

## 注意点

### 1. 多重検定

- 複数の指標を同時に検定しない
- 事前に主要指標を決定
- Bonferroni補正

### 2. 早期停止

- p-hackingを避ける
- 事前に停止ルールを決定
- Sequential testingの活用

### 3. 外的妥当性

- 実験環境と実際の環境の違い
- ノベルティ効果
- 長期的な効果

## ベストプラクティス

- 事前に分析計画を文書化
- ランダム化の確認
- バランスチェック
- 複数の感度分析
- 結果の再現性確認

## 検証ポイント

- [ ] 適切な実験デザインを選択した
- [ ] サンプルサイズは十分か
- [ ] ランダム化を実施した
- [ ] 交絡因子を考慮した
- [ ] 因果関係を慎重に解釈した
