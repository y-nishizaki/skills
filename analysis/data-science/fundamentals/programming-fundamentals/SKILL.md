---
name: "プログラミング基礎"
description: "Python/Rでのデータ操作。pandas、NumPy、matplotlib、seabornなどの必須ライブラリ"
---

# プログラミング基礎: データサイエンスのための実装スキル

## このスキルを使う場面

- データ分析を実装したい
- データの加工・変換が必要
- 統計的分析を実行したい
- データを可視化したい
- 分析結果を再現可能にしたい
- 大規模データを効率的に処理したい

## 思考プロセス

### フェーズ1: Python基礎とNumPy

**ステップ1: Python基本文法**

**1. データ構造**

- [ ] リスト（list）: 順序付きコレクション
- [ ] タプル（tuple）: 不変のシーケンス
- [ ] 辞書（dict）: キーと値のペア
- [ ] セット（set）: 重複のない集合

**2. 制御構造**

- [ ] if文: 条件分岐
- [ ] forループ: 反復処理
- [ ] whileループ: 条件付き反復
- [ ] リスト内包表記: 効率的なリスト生成

**3. 関数とモジュール**

- [ ] 関数定義: def
- [ ] ラムダ関数: 匿名関数
- [ ] モジュールimport: ライブラリの使用
- [ ] パッケージ管理: pip

**ステップ2: NumPyによる数値計算**

**1. ndarray（N次元配列）**

```python
import numpy as np

# 配列の作成
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# 特殊な配列
zeros = np.zeros((3, 3))  # ゼロ行列
ones = np.ones((2, 4))     # 1の行列
arange = np.arange(0, 10, 2)  # 0から10まで2刻み
linspace = np.linspace(0, 1, 5)  # 0から1まで5等分
```

**2. 配列操作**

- [ ] shape: 配列の形状
- [ ] reshape: 形状変更
- [ ] flatten: 1次元化
- [ ] transpose: 転置
- [ ] concatenate: 結合

**3. 数値演算**

- [ ] 要素ごとの演算（ブロードキャスト）
- [ ] 統計関数: mean, std, min, max
- [ ] 線形代数: dot, matmul, linalg
- [ ] 乱数生成: random

**4. インデックスとスライス**

```python
# インデックス
arr[0]  # 最初の要素
arr[-1]  # 最後の要素

# スライス
arr[1:4]  # 1番目から3番目まで
arr[::2]  # 2個おき

# ブールインデックス
arr[arr > 3]  # 3より大きい要素
```

**移行条件:**

- [ ] NumPy配列を作成・操作できる
- [ ] ブロードキャストを理解した
- [ ] 基本的な数値計算を実行できる

### フェーズ2: pandasによるデータ操作

**ステップ1: DataFrameの基礎**

**1. DataFrameの作成**

```python
import pandas as pd

# 辞書から作成
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['Tokyo', 'Osaka', 'Kyoto']
})

# CSVから読み込み
df = pd.read_csv('data.csv')

# Excelから読み込み
df = pd.read_excel('data.xlsx')
```

**2. データの確認**

- [ ] head(): 先頭数行
- [ ] tail(): 末尾数行
- [ ] info(): データ型と欠損値
- [ ] describe(): 基本統計量
- [ ] shape: 行数と列数
- [ ] columns: 列名一覧

**3. 列の選択と追加**

```python
# 列の選択
df['age']  # 単一列
df[['name', 'age']]  # 複数列

# 列の追加
df['adult'] = df['age'] >= 20

# 列の削除
df.drop('city', axis=1, inplace=True)
```

**ステップ2: データフィルタリングと集計**

**1. 行のフィルタリング**

```python
# 条件でフィルタ
df[df['age'] > 25]

# 複数条件
df[(df['age'] > 25) & (df['city'] == 'Tokyo')]

# isinによるフィルタ
df[df['city'].isin(['Tokyo', 'Osaka'])]

# 文字列フィルタ
df[df['name'].str.contains('A')]
```

**2. グループ化と集計**

```python
# groupby
df.groupby('city')['age'].mean()

# 複数の集計
df.groupby('city').agg({
    'age': ['mean', 'min', 'max'],
    'name': 'count'
})

# pivot_table
pd.pivot_table(df,
               values='age',
               index='city',
               aggfunc='mean')
```

**3. ソートとランキング**

```python
# ソート
df.sort_values('age', ascending=False)

# 複数列でソート
df.sort_values(['city', 'age'])

# ランキング
df['rank'] = df['age'].rank()
```

**ステップ3: データ結合と変換**

**1. データ結合**

```python
# merge（SQLのJOINに相当）
pd.merge(df1, df2, on='key')
pd.merge(df1, df2, on='key', how='left')

# concat（縦・横に連結）
pd.concat([df1, df2], axis=0)  # 縦方向
pd.concat([df1, df2], axis=1)  # 横方向
```

**2. データ変換**

```python
# apply関数
df['age_group'] = df['age'].apply(
    lambda x: 'young' if x < 30 else 'senior'
)

# map（辞書マッピング）
df['city_code'] = df['city'].map({
    'Tokyo': 1,
    'Osaka': 2
})

# 型変換
df['age'] = df['age'].astype(int)
df['date'] = pd.to_datetime(df['date'])
```

**3. 欠損値処理**

```python
# 欠損値確認
df.isnull().sum()

# 欠損値削除
df.dropna()

# 欠損値補完
df.fillna(0)
df['age'].fillna(df['age'].mean())

# 前方補完・後方補完
df.fillna(method='ffill')
```

**移行条件:**

- [ ] DataFrameを自在に操作できる
- [ ] グループ化と集計ができる
- [ ] データ結合を実行できる
- [ ] 欠損値処理ができる

### フェーズ3: matplotlibによる可視化

**ステップ1: 基本的なプロット**

```python
import matplotlib.pyplot as plt

# 折れ線グラフ
plt.plot(x, y)
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Line Plot')
plt.show()

# 散布図
plt.scatter(x, y)
plt.show()

# 棒グラフ
plt.bar(categories, values)
plt.show()

# ヒストグラム
plt.hist(data, bins=20)
plt.show()
```

**ステップ2: 複数プロットとカスタマイズ**

```python
# サブプロット
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].plot(x, y)
axes[0, 1].scatter(x, y)
axes[1, 0].bar(categories, values)
axes[1, 1].hist(data)
plt.tight_layout()
plt.show()

# スタイルのカスタマイズ
plt.plot(x, y,
         color='red',
         linestyle='--',
         linewidth=2,
         marker='o',
         label='Data')
plt.legend()
plt.grid(True)
```

**移行条件:**

- [ ] 基本的なグラフを作成できる
- [ ] 複数プロットを配置できる
- [ ] 見やすくカスタマイズできる

### フェーズ4: seabornによる統計的可視化

**ステップ1: seabornの基本**

```python
import seaborn as sns

# スタイル設定
sns.set_style('whitegrid')
sns.set_palette('husl')

# 散布図（回帰線付き）
sns.regplot(x='age', y='income', data=df)

# 箱ひげ図
sns.boxplot(x='category', y='value', data=df)

# バイオリンプロット
sns.violinplot(x='category', y='value', data=df)

# ヒートマップ（相関行列）
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
```

**ステップ2: 高度な可視化**

```python
# ペアプロット
sns.pairplot(df, hue='category')

# カテゴリカルプロット
sns.catplot(x='category',
            y='value',
            hue='group',
            kind='box',  # 'violin', 'bar'等も可能
            data=df)

# 分布プロット
sns.displot(df, x='value', hue='category', kind='kde')
```

**移行条件:**

- [ ] seabornで統計的グラフを作成できる
- [ ] データの分布を視覚的に理解できる
- [ ] matplotlibとseabornを使い分けられる

### フェーズ5: 効率的なコーディング

**ステップ1: ベクトル化**

```python
# 避けるべき: ループ
result = []
for x in data:
    result.append(x * 2)

# 推奨: ベクトル化
result = data * 2  # NumPy/pandasで高速

# pandas apply vs ベクトル化
# 遅い
df['result'] = df['value'].apply(lambda x: x * 2)

# 速い
df['result'] = df['value'] * 2
```

**ステップ2: メモリ効率**

```python
# チャンク読み込み
chunks = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in chunks:
    process(chunk)

# データ型の最適化
df['int_col'] = df['int_col'].astype('int32')
df['cat_col'] = df['cat_col'].astype('category')
```

**ステップ3: コードの可読性**

```python
# メソッドチェーン
result = (df
    .query('age > 20')
    .groupby('city')
    .agg({'income': 'mean'})
    .sort_values('income', ascending=False)
)

# パイプライン
def filter_age(df):
    return df[df['age'] > 20]

def calculate_stats(df):
    return df.groupby('city').mean()

result = df.pipe(filter_age).pipe(calculate_stats)
```

**移行条件:**

- [ ] ベクトル化でコードを高速化できる
- [ ] メモリ効率を意識できる
- [ ] 可読性の高いコードを書ける

## 判断のポイント

### ライブラリの選択

**NumPy:**
- 数値計算
- 行列演算
- 配列操作

**pandas:**
- 表形式データ
- データの集計・変換
- 時系列データ

**matplotlib:**
- 細かいカスタマイズ
- 複雑なレイアウト
- 低レベル制御

**seaborn:**
- 統計的可視化
- 美しいデフォルト
- 高レベルインターフェース

### 処理速度の最適化

**ボトルネックの特定:**
- ループを避ける
- ベクトル化を使う
- 適切なデータ型を選ぶ

**大規模データ:**
- チャンク処理
- Dask, Polarsの検討
- データベースでの前処理

## よくある落とし穴

1. **ループの多用**
   - ❌ forループでデータ処理
   - ✅ ベクトル化演算

2. **コピーとビュー**
   - ❌ df[df['age'] > 20]['name'] = 'New'
   - ✅ df.loc[df['age'] > 20, 'name'] = 'New'

3. **inplace引数**
   - ❌ 不必要なinplace=True
   - ✅ メソッドチェーン

4. **非効率な結合**
   - ❌ ループでappend
   - ✅ concat/mergeを一度に

5. **メモリリーク**
   - ❌ 不要な中間変数
   - ✅ 適切なメモリ管理

## 検証ポイント

### コーディングスキル

- [ ] Python基本文法を理解している
- [ ] NumPy配列を扱える
- [ ] pandasでデータ操作できる
- [ ] 可視化ライブラリを使える

### 効率性

- [ ] ベクトル化を使っている
- [ ] 不要なループを避けている
- [ ] メモリ使用量を意識している
- [ ] 処理時間を測定している

### 可読性

- [ ] わかりやすい変数名
- [ ] 適切なコメント
- [ ] モジュール化
- [ ] コーディング規約

## 他スキルとの連携

### programming-fundamentals → all data science skills

すべてのスキルの実装基盤：

1. このスキルでプログラミング基礎
2. 他のスキルで理論を学ぶ
3. プログラミングで実装
4. 結果を評価・改善

## ベストプラクティス

### Jupyter Notebookの活用

- 対話的な分析
- 可視化の即座確認
- ドキュメントと一体化
- 再現性の確保

### バージョン管理

- Gitでコード管理
- .gitignoreの設定
- ブランチ戦略
- コミットメッセージ

### 環境管理

- 仮想環境（venv, conda）
- requirements.txt
- Dockerの活用
- 依存関係の明示

### テスト

- pytest, unittestの使用
- データの検証
- 関数の単体テスト
- CI/CDパイプライン
