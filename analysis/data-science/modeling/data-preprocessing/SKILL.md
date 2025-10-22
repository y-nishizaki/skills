---
name: "データ前処理"
description: "欠損値補完、異常値処理、特徴量エンジニアリング。クリーンで分析可能なデータを作成"
---

# データ前処理: モデル構築の基盤

## このスキルを使う場面

- 生データをモデリング可能な形式に変換したい
- データ品質を向上させたい
- モデル性能を改善したい
- 特徴量を作成・選択したい

## 主な処理

### 1. 欠損値処理

```python
# 欠損値の確認
df.isnull().sum()

# 削除
df.dropna()
df.dropna(subset=['重要な列'])

# 補完
df.fillna(df.mean())  # 平均値
df.fillna(df.median())  # 中央値
df.fillna(method='ffill')  # 前方補完

# 高度な補完
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=5)
df_imputed = imputer.fit_transform(df)
```


### 2. 外れ値処理

```python
# IQR法
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

# フィルタリング
df = df[(df['column'] >= lower) & (df['column'] <= upper)]

# キャッピング
df['column'] = df['column'].clip(lower, upper)

# 変換
df['column'] = np.log1p(df['column'])  # 対数変換
```


### 3. スケーリング・正規化

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 標準化（平均0、標準偏差1）
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[numeric_cols])

# 正規化（0-1の範囲）
scaler = MinMaxScaler()
df_normalized = scaler.fit_transform(df[numeric_cols])

# ロバストスケーリング（外れ値に強い）
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
df_robust = scaler.fit_transform(df[numeric_cols])
```


### 4. カテゴリ変数のエンコーディング

```python
# ラベルエンコーディング
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category'])

# ワンホットエンコーディング
df_onehot = pd.get_dummies(df, columns=['category'])

# ターゲットエンコーディング
category_means = df.groupby('category')['target'].mean()
df['category_encoded'] = df['category'].map(category_means)

# 頻度エンコーディング
freq = df['category'].value_counts()
df['category_freq'] = df['category'].map(freq)
```


### 5. 特徴量エンジニアリング

```python
# 数値特徴量の変換
df['log_value'] = np.log1p(df['value'])
df['sqrt_value'] = np.sqrt(df['value'])
df['squared'] = df['value'] ** 2

# 交互作用特徴量
df['feature_product'] = df['feature1'] * df['feature2']
df['feature_ratio'] = df['feature1'] / (df['feature2'] + 1e-5)

# ビニング（離散化）
df['age_group'] = pd.cut(df['age'], bins=[0, 20, 40, 60, 100],
                         labels=['young', 'adult', 'middle', 'senior'])

# 時系列特徴量
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek
df['hour'] = df['date'].dt.hour

# 集計特徴量
df['user_avg_amount'] = df.groupby('user_id')['amount'].transform('mean')
df['user_total_count'] = df.groupby('user_id')['order_id'].transform('count')
```


### 6. 特徴量選択

```python
# 相関による選択
corr_matrix = df.corr()
high_corr = corr_matrix[abs(corr_matrix['target']) > 0.5].index

# 分散による選択
from sklearn.feature_selection import VarianceThreshold
selector = VarianceThreshold(threshold=0.1)
df_selected = selector.fit_transform(df)

# 再帰的特徴量削減（RFE）
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
estimator = RandomForestClassifier()
selector = RFE(estimator, n_features_to_select=10)
selector.fit(X, y)

# 特徴量重要度
model = RandomForestClassifier()
model.fit(X, y)
importances = pd.Series(model.feature_importances_, index=X.columns)
top_features = importances.sort_values(ascending=False).head(20)
```


### 7. データ分割

```python
from sklearn.model_selection import train_test_split

# 単純分割
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 層化抽出
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 時系列分割
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
```


## ベストプラクティス

### パイプライン構築

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# 数値とカテゴリの前処理を定義
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# 統合
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# モデルと統合
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier())
])
```


### データリーケージの防止

- 前処理はトレーニングデータのみで学習
- テストデータには同じ変換を適用
- target encodingは慎重に使用
- 時系列データは未来のデータを使わない

### 再現性の確保

```python
# ランダムシード固定
np.random.seed(42)
random.seed(42)

# 前処理パラメータの保存
import joblib
joblib.dump(scaler, 'scaler.pkl')
scaler = joblib.load('scaler.pkl')
```


## 検証ポイント

- [ ] 欠損値を適切に処理した
- [ ] 外れ値を確認・対処した
- [ ] スケーリングが必要な場合に実施した
- [ ] カテゴリ変数を適切にエンコードした
- [ ] 有用な特徴量を作成した
- [ ] データリーケージを防いだ
- [ ] パイプラインで処理を自動化した
