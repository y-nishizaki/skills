---
name: "探索的データ分析（EDA）"
description: "データの傾向を可視化して洞察を得る。パターン発見とデータ理解"
---

# 探索的データ分析（EDA）: データから洞察を引き出す

## このスキルを使う場面

- データセットを初めて扱うとき
- パターンや傾向を発見したい
- 仮説を生成したい
- モデリング前にデータを理解したい

## EDAの流れ

### 1. データ概要の把握

```python
# 基本情報
df.shape  # 行数・列数
df.info()  # データ型・欠損値
df.describe()  # 基本統計量
df.head()  # 先頭データ

# 欠損値確認
df.isnull().sum()
df.isnull().sum() / len(df) * 100  # 欠損率

# ユニーク値
df.nunique()
df['column'].value_counts()
```


### 2. 単変量分析

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 数値変数：ヒストグラム
plt.figure(figsize=(10, 6))
df['age'].hist(bins=30)
plt.xlabel('Age')
plt.title('Age Distribution')

# 数値変数：箱ひげ図
sns.boxplot(y=df['income'])

# 数値変数：密度プロット
df['age'].plot(kind='density')

# カテゴリ変数：棒グラフ
df['category'].value_counts().plot(kind='bar')

# カテゴリ変数：円グラフ
df['category'].value_counts().plot(kind='pie')
```


### 3. 二変量分析

```python
# 数値 vs 数値：散布図
plt.scatter(df['age'], df['income'])
plt.xlabel('Age')
plt.ylabel('Income')

# 回帰線付き散布図
sns.regplot(x='age', y='income', data=df)

# カテゴリ vs 数値：箱ひげ図
sns.boxplot(x='category', y='value', data=df)

# カテゴリ vs 数値：バイオリンプロット
sns.violinplot(x='category', y='value', data=df)

# カテゴリ vs カテゴリ：クロス集計
pd.crosstab(df['category1'], df['category2'])

# ヒートマップ
sns.heatmap(pd.crosstab(df['cat1'], df['cat2']), annot=True)
```


### 4. 相関分析

```python
# 相関行列
corr = df.corr()

# ヒートマップで可視化
plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)

# 目的変数との相関
target_corr = df.corr()['target'].sort_values(ascending=False)
print(target_corr)

# ペアプロット
sns.pairplot(df[['var1', 'var2', 'var3', 'target']], hue='target')
```


### 5. 多変量分析

```python
# グループ化して集計
df.groupby('category')[['value1', 'value2']].agg(['mean', 'median', 'std'])

# ピボットテーブル
pd.pivot_table(df, values='sales',
               index='category',
               columns='region',
               aggfunc='sum')

# 複数条件での分析
df.groupby(['category', 'region'])['sales'].mean().unstack()
```


### 6. 時系列分析

```python
# 時系列プロット
df.set_index('date')['value'].plot(figsize=(15, 5))

# 移動平均
df['MA_7'] = df['value'].rolling(window=7).mean()
df['MA_30'] = df['value'].rolling(window=30).mean()
df[['value', 'MA_7', 'MA_30']].plot()

# 季節性分解
from statsmodels.tsa.seasonal import seasonal_decompose
decomposition = seasonal_decompose(df['value'], model='additive', period=12)
decomposition.plot()

# 曜日別集計
df.groupby(df['date'].dt.dayofweek)['value'].mean().plot(kind='bar')
```


### 7. 分布の確認

```python
# Q-Qプロット（正規性の確認）
from scipy import stats
stats.probplot(df['value'], dist="norm", plot=plt)

# 歪度・尖度
print(f"Skewness: {df['value'].skew()}")
print(f"Kurtosis: {df['value'].kurtosis()}")

# 複数変数の分布
df[numeric_cols].hist(figsize=(15, 10), bins=30)
```


## 効果的な可視化テクニック

### Seabornの活用

```python
# スタイル設定
sns.set_style("whitegrid")
sns.set_palette("husl")

# カテゴリカルプロット
sns.catplot(x='category', y='value', hue='group',
            kind='box', data=df, height=6, aspect=1.5)

# 分布プロット
sns.displot(df, x='value', hue='category', kind='kde')

# 関係性プロット
sns.relplot(x='var1', y='var2', hue='category',
            size='value', data=df)

# ファセットグリッド
g = sns.FacetGrid(df, col='category', row='region')
g.map(plt.scatter, 'x', 'y')
```


### 複数プロット

```python
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 左上
axes[0, 0].hist(df['age'], bins=30)
axes[0, 0].set_title('Age Distribution')

# 右上
axes[0, 1].scatter(df['age'], df['income'])
axes[0, 1].set_title('Age vs Income')

# 左下
df['category'].value_counts().plot(kind='bar', ax=axes[1, 0])
axes[1, 0].set_title('Category Counts')

# 右下
sns.boxplot(x='category', y='value', data=df, ax=axes[1, 1])
axes[1, 1].set_title('Value by Category')

plt.tight_layout()
```


## 洞察の抽出

### パターンの発見

- 外れ値や異常値の特定
- グループ間の差異
- 変数間の関係性
- 時系列トレンドと季節性
- セグメントの特徴

### 仮説の生成

```python
# 例：年齢層別の購買傾向
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 45, 65, 100])
df.groupby('age_group')['purchase_amount'].agg(['mean', 'median', 'count'])

# 例：曜日別の売上パターン
df['dayofweek'] = df['date'].dt.day_name()
df.groupby('dayofweek')['sales'].mean().plot(kind='bar')
```


## ベストプラクティス

- 段階的に深掘りする
- 可視化とと数値を組み合わせる
- 複数の視点で分析する
- 発見をドキュメント化する
- ビジネス的意味を考える

## 検証ポイント

- [ ] データの全体像を把握した
- [ ] 主要な変数の分布を確認した
- [ ] 変数間の関係を分析した
- [ ] 異常値や外れ値を特定した
- [ ] パターンや傾向を発見した
- [ ] ビジネス的な洞察を得た
