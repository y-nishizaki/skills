---
name: "統計的推論"
description: "仮説検定、信頼区間、因果推論。データに基づく結論の導出"
---

# 統計的推論: データから結論を導く

## このスキルを使う場面

- 施策の効果を統計的に検証したい
- サンプルから母集団について推論したい
- 偶然か真の効果かを判断したい
- A/Bテストの結果を評価したい

## 主な手法

### 1. 仮説検定の基本

```python
from scipy import stats

# t検定（2グループの平均比較）
group_a = df[df['group'] == 'A']['value']
group_b = df[df['group'] == 'B']['value']
t_stat, p_value = stats.ttest_ind(group_a, group_b)

print(f"t統計量: {t_stat:.4f}")
print(f"p値: {p_value:.4f}")
if p_value < 0.05:
    print("統計的に有意な差がある")
```

### 2. 主要な検定手法

```python
# 対応のあるt検定
t_stat, p_value = stats.ttest_rel(before, after)

# 分散分析（ANOVA）
f_stat, p_value = stats.f_oneway(group1, group2, group3)

# カイ二乗検定（独立性の検定）
contingency_table = pd.crosstab(df['var1'], df['var2'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# マン・ホイットニーのU検定（ノンパラメトリック）
u_stat, p_value = stats.mannwhitneyu(group_a, group_b)

# ウィルコクソン符号順位検定
w_stat, p_value = stats.wilcoxon(before, after)
```

### 3. 信頼区間

```python
from scipy.stats import t

# 平均の信頼区間
mean = df['value'].mean()
std_error = stats.sem(df['value'])
confidence_level = 0.95
degrees_freedom = len(df['value']) - 1

confidence_interval = t.interval(
    confidence_level,
    degrees_freedom,
    loc=mean,
    scale=std_error
)

print(f"95%信頼区間: {confidence_interval}")

# 割合の信頼区間
from statsmodels.stats.proportion import proportion_confint
count = 50  # 成功回数
n = 100  # 試行回数
ci = proportion_confint(count, n, method='wilson')
```

### 4. 効果量

```python
# Cohen's d（標準化された平均差）
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (group1.mean() - group2.mean()) / pooled_std

d = cohens_d(group_a, group_b)
print(f"Cohen's d: {d:.3f}")

# 解釈
if abs(d) < 0.2:
    print("小さい効果")
elif abs(d) < 0.5:
    print("中程度の効果")
else:
    print("大きい効果")
```

### 5. A/Bテスト

```python
# コンバージョン率の検定
from statsmodels.stats.proportion import proportions_ztest

# データ
conversions = [250, 280]  # A群、B群の転換数
visitors = [10000, 10000]  # 訪問者数

# 検定
z_stat, p_value = proportions_ztest(conversions, visitors)

# 効果量（リフト率）
cr_a = conversions[0] / visitors[0]
cr_b = conversions[1] / visitors[1]
lift = (cr_b - cr_a) / cr_a * 100

print(f"A群のCR: {cr_a:.2%}")
print(f"B群のCR: {cr_b:.2%}")
print(f"リフト: {lift:.2f}%")
print(f"p値: {p_value:.4f}")
```

### 6. サンプルサイズ設計

```python
from statsmodels.stats.power import tt_ind_solve_power

# 必要サンプルサイズの計算
required_n = tt_ind_solve_power(
    effect_size=0.5,  # Cohen's d
    alpha=0.05,  # 有意水準
    power=0.8,  # 検出力
    ratio=1.0,  # サンプルサイズ比
    alternative='two-sided'
)

print(f"必要サンプルサイズ: {int(required_n)} (各群)")
```

### 7. 多重検定の補正

```python
from statsmodels.stats.multitest import multipletests

# 複数のp値
p_values = [0.01, 0.04, 0.03, 0.08, 0.001]

# Bonferroni補正
rejected, p_adjusted, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method='bonferroni'
)

# FDR制御（Benjamini-Hochberg法）
rejected, p_adjusted, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method='fdr_bh'
)

print(f"調整後p値: {p_adjusted}")
print(f"棄却された帰無仮説: {rejected}")
```

## 因果推論の基礎

### 1. 傾向スコアマッチング

```python
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

# 傾向スコアの推定
X = df[['age', 'gender', 'income']]
treatment = df['treatment']

model = LogisticRegression()
model.fit(X, treatment)
propensity_scores = model.predict_proba(X)[:, 1]

# マッチング
def match_by_propensity(df, propensity_scores, caliper=0.1):
    treated = df[df['treatment'] == 1].copy()
    control = df[df['treatment'] == 0].copy()

    treated['propensity'] = propensity_scores[df['treatment'] == 1]
    control['propensity'] = propensity_scores[df['treatment'] == 0]

    # 最近傍マッチング
    # ... (実装の詳細)

    return matched_df
```

### 2. 差分の差分法（DID）

```python
# Before-After, Treatment-Control
import statsmodels.formula.api as smf

# データ構造: time (before/after), treated (0/1), outcome
model = smf.ols('outcome ~ treated * time', data=df).fit()
print(model.summary())

# DID推定値
did_effect = model.params['treated:time']
print(f"DID効果: {did_effect:.3f}")
```

### 3. 回帰不連続デザイン（RDD）

```python
# カットオフ点の前後で効果を推定
cutoff = 50
df['above_cutoff'] = (df['score'] >= cutoff).astype(int)
df['score_centered'] = df['score'] - cutoff

model = smf.ols(
    'outcome ~ above_cutoff + score_centered + above_cutoff:score_centered',
    data=df
).fit()

rdd_effect = model.params['above_cutoff']
print(f"RDD効果: {rdd_effect:.3f}")
```

## ベストプラクティス

### 仮説検定の注意点

- 事前に仮説と手法を決定
- サンプルサイズを事前計算
- 多重検定を補正
- 効果量も報告
- p値だけで判断しない

### A/Bテストの設計

- 十分なサンプルサイズ
- ランダム化の確認
- 同時期に実施
- セグメント分析
- ノベルティ効果に注意

### 因果推論の要件

- 交絡因子の特定
- ランダム化または適切な準実験デザイン
- 並行トレンドの仮定（DIDの場合）
- 選択バイアスへの対処

## 検証ポイント

- [ ] 適切な検定手法を選択した
- [ ] 前提条件を確認した
- [ ] サンプルサイズは十分か
- [ ] 効果量を計算した
- [ ] 多重検定を考慮した
- [ ] 実務的な意味を解釈した
- [ ] 因果関係と相関を区別した
