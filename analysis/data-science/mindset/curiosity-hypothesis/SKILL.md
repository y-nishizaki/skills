---
name: "好奇心と仮説思考"
description: "「なぜ？」を問い続ける姿勢。データから洞察を引き出す探求心"
---

# 好奇心と仮説思考: 探索的思考の習慣

## このスキルを使う場面

- データ分析を開始するとき
- 異常値や予想外の結果に遭遇したとき
- 新しいパターンを発見したとき
- 問題の根本原因を探るとき

## 好奇心の育て方

### 1. 「なぜ？」を5回繰り返す

```
問題: 売上が前月比で15%減少

なぜ1: なぜ売上が減少したのか？
→ 新規顧客の獲得数が減少したから

なぜ2: なぜ新規顧客が減少したのか？
→ 広告のクリック率が低下したから

なぜ3: なぜクリック率が低下したのか？
→ 広告のターゲティングが適切でなかったから

なぜ4: なぜターゲティングが不適切だったのか？
→ 顧客セグメントの分析が古いデータに基づいていたから

なぜ5: なぜ古いデータを使っていたのか？
→ 定期的な更新プロセスがなかったから

根本原因: データ更新プロセスの欠如
```


### 2. データに「質問」する

**良い質問の例**:

- 「このセグメントは他と何が違うのか？」
- 「時系列でどう変化しているか？」
- 「外れ値は何を意味するのか？」
- 「この関係性の背後にある理由は？」

### 3. 異なる視点で見る

```python
# 同じデータを複数の角度から分析

# 時間軸
df.groupby(df['date'].dt.month)['sales'].mean()

# セグメント別
df.groupby('customer_segment')['sales'].mean()

# 地域別
df.groupby('region')['sales'].mean()

# 組み合わせ
df.groupby(['region', 'customer_segment'])['sales'].mean()
```


## 仮説思考の実践

### 1. 仮説の立て方

**良い仮説の条件**:

- 検証可能
- 具体的
- 測定可能
- ビジネス的意味がある

**仮説の例**:

```
悪い例: 「売上を増やせるはず」
良い例: 「20代女性向けの商品ラインを拡充すれば、
        このセグメントの売上が20%増加する」
```


### 2. 仮説駆動型分析

```python
# 仮説: 高頻度購入者は高単価商品も買う

# 検証1: 購入頻度と平均購入単価の関係
high_freq = df[df['purchase_count'] > 10]
low_freq = df[df['purchase_count'] <= 10]

print(f"High freq avg order: {high_freq['order_value'].mean()}")
print(f"Low freq avg order: {low_freq['order_value'].mean()}")

# 検証2: 統計的検定
from scipy.stats import ttest_ind
t_stat, p_value = ttest_ind(
    high_freq['order_value'],
    low_freq['order_value']
)

# 検証3: 可視化
plt.boxplot([high_freq['order_value'], low_freq['order_value']])
```


### 3. 仮説の反証可能性

**ポパーの反証主義**:

- 仮説は反証可能でなければならない
- 「〜〜ではない」ことを示せる条件を明確に

```python
# 仮説: 新機能の追加でユーザーエンゲージメントが向上する

# 反証条件を明確に
- 平均セッション時間が前月比で変化なし（± 5%以内）
- DAU（Daily Active Users）が増加しない
- 新機能の使用率が10%未満

# これらが観測されたら仮説を棄却
```


## 探索的思考の習慣

### 1. パターンの発見

```python
# 予想外のパターンを探す

# 外れ値
outliers = df[df['value'] > df['value'].quantile(0.99)]
print("Outliers characteristics:")
print(outliers.describe())

# 相関の強い変数ペア
corr = df.corr()
high_corr = corr[abs(corr) > 0.7]

# 時系列の変化点
from ruptures import Ptt
algo = Ptt(model="rbf").fit(signal)
result = algo.predict(pen=10)
```


### 2. 仮説のリスト化

```markdown
## 売上減少の仮説リスト

1. 競合の新商品による市場シェア低下
   - 検証方法: 市場調査データ、SNSメンション分析
   - 優先度: 高

2. 季節要因（例年この時期は低い）
   - 検証方法: 過去3年分の同月データ比較
   - 優先度: 中

3. 価格設定の問題
   - 検証方法: 価格弾力性分析
   - 優先度: 高

4. 顧客満足度の低下
   - 検証方法: NPSスコア、レビュー分析
   - 優先度: 中
```


### 3. 実験的アプローチ

```python
# 小さな実験で仮説を検証

# 仮説: メール送信タイミングを朝にすると開封率が上がる

# 実験設計
experiment_df = pd.DataFrame({
    'user_id': range(1000),
    'group': np.random.choice(['morning', 'evening'], 1000)
})

# 結果収集（仮想データ）
experiment_df['opened'] = np.random.binomial(
    1,
    p=np.where(experiment_df['group'] == 'morning', 0.25, 0.20)
)

# 分析
morning_rate = experiment_df[experiment_df['group'] == 'morning']['opened'].mean()
evening_rate = experiment_df[experiment_df['group'] == 'evening']['opened'].mean()

print(f"Morning open rate: {morning_rate:.2%}")
print(f"Evening open rate: {evening_rate:.2%}")
```


## データ探索のベストプラクティス

### 1. まず可視化

```python
# データの理解は可視化から始める
import seaborn as sns

# 全体的な分布
sns.pairplot(df[numeric_cols])

# 時系列
df.set_index('date')[['sales', 'visitors']].plot(figsize=(15, 5))

# カテゴリ別比較
sns.boxplot(data=df, x='category', y='value')
```


### 2. 複数の仮説を並行検証

```python
# 効率的に複数の仮説を検証

hypotheses = {
    'H1_age': 'age',
    'H2_gender': 'gender',
    'H3_region': 'region'
}

results = {}
for name, variable in hypotheses.items():
    group_means = df.groupby(variable)['target'].mean()
    f_stat, p_value = stats.f_oneway(
        *[group['target'].values for _, group in df.groupby(variable)]
    )
    results[name] = {'p_value': p_value, 'means': group_means}

# 最も有望な仮説を特定
best_hypothesis = min(results.items(), key=lambda x: x[1]['p_value'])
```


### 3. 失敗から学ぶ

**仮説が棄却されたとき**:

- なぜ間違っていたのか？
- 何を見落としていたのか？
- 次はどう改善できるか？

## マインドセットの育成

### 1. 日常の習慣

- データを見たら「なぜ？」と問う
- 予想を立ててから分析する
- 意外な結果を喜ぶ
- 仮説を文書化する

### 2. 知的誠実さ

- 都合の良いデータだけを見ない
- 自分の仮説に批判的
- 反証を積極的に探す
- 不確実性を認める

### 3. 継続的学習

- 新しい分析手法を学ぶ
- 他分野の知見を取り入れる
- 論文・事例を読む
- コミュニティに参加

## 実践例

### Case: ECサイトのカート放棄率改善

```python
# 1. 好奇心から始まる質問
"なぜカート放棄率が50%もあるのか？"

# 2. 複数の仮説
hypotheses = [
    "送料が高すぎる",
    "決済方法が限られている",
    "チェックアウトプロセスが複雑",
    "予想外の追加費用がある"
]

# 3. データで検証
abandonment_reasons = df.groupby('abandon_reason').size()
print(abandonment_reasons.sort_values(ascending=False))

# 結果: 送料が主要因と判明

# 4. さらに深掘り
"どの商品カテゴリで送料が問題になるのか？"
df.groupby('category')['abandoned_due_to_shipping'].mean()

# 5. 実験
# 特定カテゴリで送料無料キャンペーンを実施
```


## 検証ポイント

- [ ] 「なぜ？」を繰り返している
- [ ] 複数の仮説を立てている
- [ ] データで検証している
- [ ] 予想外の結果を探求している
- [ ] 失敗から学んでいる
- [ ] 継続的に好奇心を維持している
