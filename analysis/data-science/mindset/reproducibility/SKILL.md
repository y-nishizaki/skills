---
name: "再現性・透明性の意識"
description: "誰が見ても理解できるコードとレポート。科学的なデータ分析の実践"
---

# 再現性・透明性の意識: 信頼できる分析

## このスキルを使う場面

- 分析結果を他者に共有するとき
- 過去の分析を再実行する必要があるとき
- チームで分析を引き継ぐとき
- 結果の妥当性を検証したいとき

## 再現可能な分析

### 1. 環境の記録

```bash
# requirements.txt
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.2.0
matplotlib==3.7.0
seaborn==0.12.0

# 環境の固定
pip freeze > requirements.txt

# 環境の再現
pip install -r requirements.txt
```

```python
# Pythonバージョンの記録
import sys
print(f"Python version: {sys.version}")

# パッケージバージョン
import pandas as pd
import numpy as np
print(f"pandas: {pd.__version__}")
print(f"numpy: {np.__version__}")
```

### 2. ランダムシードの固定

```python
# すべての乱数を再現可能に
import random
import numpy as np
import tensorflow as tf

RANDOM_SEED = 42

# Python標準
random.seed(RANDOM_SEED)

# NumPy
np.random.seed(RANDOM_SEED)

# TensorFlow
tf.random.set_seed(RANDOM_SEED)

# scikit-learn
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=RANDOM_SEED  # ここでも指定
)
```

### 3. データのバージョン管理

```python
# データスナップショットの作成
import hashlib
from datetime import datetime

def create_data_snapshot(df, description):
    """データのスナップショットを保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # データハッシュ（変更検出用）
    data_hash = hashlib.md5(
        pd.util.hash_pandas_object(df).values
    ).hexdigest()

    # メタデータ
    metadata = {
        'timestamp': timestamp,
        'hash': data_hash,
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'description': description
    }

    # 保存
    filename = f'data_snapshot_{timestamp}.parquet'
    df.to_parquet(filename)

    with open(f'metadata_{timestamp}.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    return filename, metadata

# 使用例
snapshot_file, meta = create_data_snapshot(
    df,
    "Initial dataset before preprocessing"
)
```

## コードの可読性

### 1. クリーンなコード

```python
# 悪い例
df2=df[df['x']>10].groupby('y')['z'].mean()

# 良い例
# 閾値以上のデータをフィルタ
filtered_df = df[df['sales'] > 10]

# カテゴリ別の平均を計算
category_means = filtered_df.groupby('category')['revenue'].mean()
```

### 2. 関数化

```python
# 悪い例: 長いスクリプト
df = pd.read_csv('data.csv')
df = df.dropna()
df['new_col'] = df['col1'] * df['col2']
# ... 100行以上続く

# 良い例: 関数に分割
def load_data(filepath):
    """データを読み込む"""
    return pd.read_csv(filepath)

def clean_data(df):
    """欠損値を処理する"""
    return df.dropna()

def create_features(df):
    """特徴量を作成する"""
    df = df.copy()
    df['new_col'] = df['col1'] * df['col2']
    return df

def run_analysis():
    """分析パイプライン全体を実行"""
    df = load_data('data.csv')
    df = clean_data(df)
    df = create_features(df)
    return analyze(df)

# 実行
result = run_analysis()
```

### 3. ドキュメンテーション

```python
def calculate_customer_lifetime_value(
    avg_purchase_value: float,
    purchase_frequency: float,
    customer_lifespan: float,
    discount_rate: float = 0.1
) -> float:
    """
    顧客生涯価値（CLV）を計算する

    Parameters
    ----------
    avg_purchase_value : float
        平均購買額（円）
    purchase_frequency : float
        年間購買頻度（回/年）
    customer_lifespan : float
        顧客の平均寿命（年）
    discount_rate : float, optional
        割引率（デフォルト: 0.1）

    Returns
    -------
    float
        顧客生涯価値（円）

    Examples
    --------
    >>> calculate_customer_lifetime_value(
    ...     avg_purchase_value=10000,
    ...     purchase_frequency=4,
    ...     customer_lifespan=3
    ... )
    108108.11

    Notes
    -----
    CLV = (平均購買額 × 購買頻度) / (1 + 割引率 - 購買頻度)
    """
    clv = (avg_purchase_value * purchase_frequency) / \
          (1 + discount_rate - purchase_frequency)

    return clv
```

## Jupyter Notebookのベストプラクティス

### 1. 構造化されたNotebook

```markdown
# データ分析: 顧客セグメンテーション

## 1. 目的と背景
- 顧客を行動パターンでセグメント化
- ターゲティング戦略の策定に活用

## 2. データの読み込みと確認
```

```python
# データ読み込み
df = pd.read_csv('customer_data.csv')

# 基本情報
print(f"Shape: {df.shape}")
df.info()
df.head()
```

```markdown
## 3. データクリーニング

欠損値は以下の方針で処理：
- age: 中央値で補完
- income: 削除（欠損率が高いため）
```

### 2. セルの適切な分割

```python
# 悪い例: 1つのセルに全て
df = pd.read_csv('data.csv')
df = df.dropna()
df['new_col'] = df['col1'] * 2
result = df.groupby('category').mean()
plt.plot(result)

# 良い例: 論理的な単位で分割

# セル1: データ読み込み
df = pd.read_csv('data.csv')

# セル2: 前処理
df = df.dropna()
df['new_col'] = df['col1'] * 2

# セル3: 集計
result = df.groupby('category').mean()

# セル4: 可視化
plt.figure(figsize=(10, 6))
plt.plot(result.index, result.values)
plt.title('Category Means')
plt.show()
```

### 3. 出力の管理

```python
# 悪い例: 大量の出力
for i in range(1000):
    print(df.iloc[i])  # 1000行の出力！

# 良い例: 必要な情報のみ
print(f"Total rows: {len(df)}")
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())
```

## 分析の記録

### 1. 分析ログ

```python
import logging
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'analysis_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 分析の記録
logger.info("Analysis started")
logger.info(f"Data shape: {df.shape}")

# 重要な決定を記録
logger.info("Dropping outliers > 99th percentile")
df = df[df['value'] < df['value'].quantile(0.99)]
logger.info(f"Data shape after outlier removal: {df.shape}")

# エラーも記録
try:
    result = risky_operation(df)
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    raise

logger.info("Analysis completed successfully")
```

### 2. 決定の記録

```python
# 分析の重要な決定を文書化
ANALYSIS_DECISIONS = {
    'date': '2024-01-15',
    'analyst': 'Data Science Team',
    'decisions': [
        {
            'decision': '欠損値の補完方法',
            'choice': '平均値で補完',
            'alternatives': ['削除', '中央値', '予測モデル'],
            'rationale': '欠損率が低い（< 5%）ため、平均値補完が適切',
            'impact': '分析対象データが95%保持される'
        },
        {
            'decision': '外れ値の処理',
            'choice': '99パーセンタイル以上を削除',
            'alternatives': ['winsorization', 'log変換', 'そのまま'],
            'rationale': '明らかなデータエラーが含まれている',
            'impact': '約1%のデータが除外される'
        }
    ]
}

# JSON で保存
with open('analysis_decisions.json', 'w') as f:
    json.dump(ANALYSIS_DECISIONS, f, indent=2, ensure_ascii=False)
```

## 結果の共有

### 1. README の作成

```markdown
# 顧客セグメンテーション分析

## 概要
顧客の購買行動に基づいてセグメントを作成し、
マーケティング戦略の最適化を図る。

## データ
- ソース: CRM database
- 期間: 2024-01-01 ~ 2024-12-31
- レコード数: 100,000
- 特徴量: 15

## 実行方法

### 環境構築
```bash
pip install -r requirements.txt
```

### 分析実行
```bash
python main.py --config config.yaml
```

### Jupyter Notebookで確認
```bash
jupyter notebook analysis.ipynb
```

## 結果
- 5つの顧客セグメントを特定
- 高価値セグメント: 全体の20%、売上の60%
- 詳細は `results/segmentation_report.pdf` を参照

## ファイル構成
```
.
├── README.md
├── requirements.txt
├── config.yaml
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── analysis.ipynb
├── src/
│   ├── data_processing.py
│   ├── modeling.py
│   └── visualization.py
├── results/
│   ├── segmentation_report.pdf
│   └── figures/
└── tests/
    └── test_processing.py
```

## 連絡先
Data Science Team <ds-team@example.com>
```

### 2. コードのテスト

```python
# tests/test_processing.py
import unittest
import pandas as pd
from src.data_processing import clean_data, create_features

class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        """テスト用データの準備"""
        self.sample_df = pd.DataFrame({
            'age': [25, 35, None, 45],
            'income': [30000, 50000, 60000, 40000],
            'city': ['Tokyo', 'Osaka', 'Tokyo', 'Kyoto']
        })

    def test_clean_data(self):
        """データクリーニングのテスト"""
        cleaned = clean_data(self.sample_df)

        # 欠損値が処理されていることを確認
        self.assertEqual(cleaned['age'].isnull().sum(), 0)

        # データ型が正しいことを確認
        self.assertEqual(cleaned['age'].dtype, float)

    def test_create_features(self):
        """特徴量作成のテスト"""
        result = create_features(self.sample_df)

        # 新しい特徴量が作成されていることを確認
        self.assertIn('age_group', result.columns)

        # 値が期待通りであることを確認
        self.assertEqual(result.loc[0, 'age_group'], 'young')

if __name__ == '__main__':
    unittest.main()
```

## バージョン管理

### 1. Git の活用

```bash
# .gitignore
*.pyc
__pycache__/
.ipynb_checkpoints/
data/raw/  # 生データは除外
*.csv  # 大きいファイルは除外
.env  # 認証情報は除外

# コミットメッセージの書き方
git commit -m "Add feature: customer segmentation analysis

- Implement K-means clustering
- Add visualization functions
- Update README with usage instructions"
```

### 2. プルリクエストテンプレート

```markdown
## 変更内容
- 顧客セグメンテーション機能を追加

## 変更理由
- マーケティングチームからの要望

## テスト
- [ ] ユニットテストを追加
- [ ] 実データで動作確認
- [ ] コードレビュー実施

## チェックリスト
- [ ] READMEを更新
- [ ] ドキュメント文字列を追加
- [ ] Linterを実行
- [ ] テストが通ることを確認
```

## ベストプラクティス

### 再現性

- ランダムシードを固定
- 環境を記録
- データをバージョン管理

### 可読性

- 明確な変数名
- 適切なコメント
- 関数の文書化

### 保守性

- モジュール化
- テストの作成
- エラーハンドリング

### 透明性

- 分析過程を記録
- 決定の理由を説明
- 制約を明示

## 検証ポイント

- [ ] 環境を記録した
- [ ] ランダムシードを固定した
- [ ] コードが可読である
- [ ] ドキュメントを作成した
- [ ] 分析過程を記録した
- [ ] テストを書いた
- [ ] バージョン管理している
- [ ] 他者が再現できる
