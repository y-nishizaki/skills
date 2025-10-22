---
name: "データ可視化・ストーリーテリング"
description: "効果的な可視化とストーリー構築。インサイトを伝える技術"
---

# データ可視化・ストーリーテリング: データを語らせる

## このスキルを使う場面

- 分析結果を効果的に伝えたい
- ダッシュボードを作成したい
- データで説得したい
- 非技術者に説明したい

## 効果的な可視化

### 1. グラフの選択

**比較**: 棒グラフ、折れ線グラフ
**分布**: ヒストグラム、箱ひげ図
**関係**: 散布図、バブルチャート
**構成**: 積み上げ棒グラフ、ツリーマップ
**時系列**: 折れ線グラフ、エリアチャート

### 2. 可視化の原則

**明確性**

- タイトルで結論を伝える
- 軸ラベルを明記
- 単位を明示
- 凡例を分かりやすく

**正確性**

- 軸の原点（0始まり）
- 適切なスケール
- 誤解を招く表現を避ける

**美的要素**

- 色の使い方（3-5色まで）
- 余白の確保
- フォントサイズ
- アクセシビリティ（色覚多様性）

### 3. ダッシュボード設計

```python
# Plotly Dashを使用した例
import dash
from dash import dcc, html
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Sales Dashboard'),

    dcc.Graph(
        id='sales-trend',
        figure=px.line(df, x='date', y='sales', title='Sales Trend')
    ),

    dcc.Graph(
        id='sales-by-category',
        figure=px.bar(df, x='category', y='sales', title='Sales by Category')
    )
])
```


### 4. インタラクティブ可視化

```python
# Plotlyを使用
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['sales'],
    mode='lines+markers',
    name='Sales',
    hovertemplate='<b>Date</b>: %{x}<br>' +
                  '<b>Sales</b>: %{y:,.0f}<br>'
))

fig.update_layout(
    title='Interactive Sales Chart',
    xaxis_title='Date',
    yaxis_title='Sales',
    hovermode='x unified'
)

fig.show()
```


## ストーリーテリング

### 1. ストーリー構造

**導入**: 問題提起・背景
**展開**: データと分析
**結論**: 発見と洞察
**提案**: 推奨アクション

### 2. ナラティブの作成

```
例：離脱率改善の分析

1. 問題: 「過去3ヶ月で離脱率が15%増加」
2. 分析: 「データを分析した結果、特定セグメントで顕著」
3. 発見: 「新規ユーザーの初回体験に問題」
4. 提案: 「オンボーディングを改善することで10%改善可能」
```


### 3. Three Numbers Rule

- 重要な数値は3つまでに絞る
- シンプルなメッセージ
- 記憶に残りやすい

### 4. Before/After比較

```python
# ビフォー・アフター可視化
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Before
ax1.bar(categories, before_values)
ax1.set_title('Before: 離脱率 25%')
ax1.set_ylabel('Users')

# After
ax2.bar(categories, after_values)
ax2.set_title('After: 離脱率 18% (-28%)')
ax2.set_ylabel('Users')

plt.suptitle('オンボーディング改善の効果', fontsize=16)
```


## ツールの活用

### 1. BIツール

**Tableau**

- ドラッグ&ドロップでダッシュボード
- 豊富な可視化オプション
- パブリッシュ・共有機能

**Power BI**

- Microsoftエコシステムとの統合
- DAX for計算
- レポート配信

**Looker**

- LookMLでデータモデリング
- SQLベース
- 埋め込み可能

### 2. Pythonライブラリ

```python
# Seaborn: 統計的可視化
import seaborn as sns
sns.set_style("whitegrid")
sns.catplot(data=df, x='category', y='value', kind='box')

# Plotly: インタラクティブ
import plotly.express as px
px.scatter(df, x='x', y='y', size='size', color='category')

# Altair: 宣言的可視化
import altair as alt
alt.Chart(df).mark_bar().encode(x='category', y='value')
```


## プレゼンテーション

### 1. スライド構成

1. エグゼクティブサマリー（1スライド）
2. 問題と背景（2-3スライド）
3. 分析アプローチ（1-2スライド）
4. 主要な発見（3-5スライド）
5. 推奨アクション（2-3スライド）
6. 次のステップ（1スライド）

### 2. 1スライド1メッセージ

- タイトルで結論
- グラフは1つ
- 補足は最小限
- アニメーションは控えめに

### 3. オーディエンスに合わせる

**経営層**:

- エグゼクティブサマリー重視
- ビジネスインパクト
- 簡潔に

**技術者**:

- 手法の詳細
- 再現性
- 技術的妥当性

**現場担当者**:

- 具体的なアクション
- 実装方法
- 日常業務への影響

## ベストプラクティス

- シンプルに保つ
- ストーリーを明確に
- データで裏付ける
- 視覚的階層を作る
- 繰り返しテストする

## 検証ポイント

- [ ] 適切なグラフを選択した
- [ ] 明確で正確な可視化
- [ ] ストーリーが論理的
- [ ] オーディエンスに合わせた
- [ ] アクションが明確
