---
name: "機械学習"
description: "回帰、分類、クラスタリング。予測モデルの構築とチューニング"
---

# 機械学習: データから学習するモデル構築

## このスキルを使う場面

- 予測モデルを構築したい
- パターン認識を自動化したい
- データからルールを学習させたい
- 意思決定を支援したい

## 教師あり学習

### 1. 線形回帰

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# データ分割
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# モデル訓練
model = LinearRegression()
model.fit(X_train, y_train)

# 予測
y_pred = model.predict(X_test)

# 評価
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"MSE: {mse:.3f}, R²: {r2:.3f}")
```

### 2. ロジスティック回帰

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# 予測
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# 評価
from sklearn.metrics import accuracy_score, roc_auc_score
accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)
print(f"Accuracy: {accuracy:.3f}, AUC: {auc:.3f}")
```

### 3. 決定木

```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=20,
    random_state=42
)
model.fit(X_train, y_train)

# 特徴量重要度
importances = pd.Series(
    model.feature_importances_,
    index=X.columns
).sort_values(ascending=False)
```

### 4. ランダムフォレスト

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# OOB（Out-of-Bag）スコア
print(f"OOB Score: {model.oob_score_:.3f}")
```

### 5. 勾配ブースティング

```python
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],
          early_stopping_rounds=10,
          verbose=False)

# 予測
y_pred = model.predict(X_test)
```

### 6. サポートベクターマシン（SVM）

```python
from sklearn.svm import SVC

model = SVC(
    kernel='rbf',
    C=1.0,
    gamma='scale',
    probability=True,
    random_state=42
)
model.fit(X_train, y_train)
```

### 7. k近傍法（k-NN）

```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(
    n_neighbors=5,
    weights='distance'
)
model.fit(X_train, y_train)
```

## 教師なし学習

### 1. k-means クラスタリング

```python
from sklearn.cluster import KMeans

# エルボー法で最適なk を決定
inertias = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

plt.plot(range(1, 11), inertias)
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')

# クラスタリング
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(X)
```

### 2. 階層的クラスタリング

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

# デンドログラム
linkage_matrix = linkage(X, method='ward')
dendrogram(linkage_matrix)

# クラスタリング
model = AgglomerativeClustering(n_clusters=3)
clusters = model.fit_predict(X)
```

### 3. 主成分分析（PCA）

```python
from sklearn.decomposition import PCA

# 分散の累積寄与率
pca = PCA()
pca.fit(X)
cumsum = np.cumsum(pca.explained_variance_ratio_)

# 次元削減
pca = PCA(n_components=0.95)  # 95%の分散を保持
X_reduced = pca.fit_transform(X)
```

## ハイパーパラメータチューニング

### 1. グリッドサーチ

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15],
    'learning_rate': [0.01, 0.1, 0.3]
}

grid_search = GridSearchCV(
    XGBClassifier(),
    param_grid,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")
```

### 2. ランダムサーチ

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_dist = {
    'n_estimators': randint(50, 300),
    'max_depth': randint(3, 15),
    'learning_rate': uniform(0.01, 0.3)
}

random_search = RandomizedSearchCV(
    XGBClassifier(),
    param_dist,
    n_iter=50,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1,
    random_state=42
)
random_search.fit(X_train, y_train)
```

### 3. ベイズ最適化

```python
from skopt import BayesSearchCV

search_spaces = {
    'n_estimators': (50, 300),
    'max_depth': (3, 15),
    'learning_rate': (0.01, 0.3, 'log-uniform')
}

bayes_search = BayesSearchCV(
    XGBClassifier(),
    search_spaces,
    n_iter=50,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1,
    random_state=42
)
bayes_search.fit(X_train, y_train)
```

## 交差検証

```python
from sklearn.model_selection import cross_val_score

# k-fold交差検証
scores = cross_val_score(
    model, X, y,
    cv=5,
    scoring='accuracy'
)
print(f"CV scores: {scores}")
print(f"Mean: {scores.mean():.3f} (+/- {scores.std():.3f})")

# 層化k-fold
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf)

# 時系列交差検証
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv)
```

## アンサンブル学習

### 1. バギング

```python
from sklearn.ensemble import BaggingClassifier

model = BaggingClassifier(
    base_estimator=DecisionTreeClassifier(),
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)
```

### 2. スタッキング

```python
from sklearn.ensemble import StackingClassifier

estimators = [
    ('rf', RandomForestClassifier()),
    ('xgb', XGBClassifier()),
    ('lr', LogisticRegression())
]

stacking_model = StackingClassifier(
    estimators=estimators,
    final_estimator=LogisticRegression()
)
stacking_model.fit(X_train, y_train)
```

### 3. ブレンディング

```python
# メタモデルで複数モデルの予測を統合
model1_pred = model1.predict_proba(X_test)
model2_pred = model2.predict_proba(X_test)
model3_pred = model3.predict_proba(X_test)

# 重み付き平均
weights = [0.4, 0.35, 0.25]
final_pred = (
    weights[0] * model1_pred +
    weights[1] * model2_pred +
    weights[2] * model3_pred
)
```

## ベストプラクティス

- データ前処理を適切に実施
- 訓練・検証・テストに分割
- 交差検証で性能を評価
- ハイパーパラメータを調整
- 過学習を防ぐ（正則化、Early Stopping）
- 特徴量重要度を確認
- モデルの解釈性を考慮

## 検証ポイント

- [ ] 適切なアルゴリズムを選択した
- [ ] データ前処理を実施した
- [ ] 交差検証で評価した
- [ ] ハイパーパラメータを調整した
- [ ] 過学習を防いだ
- [ ] テストデータで最終評価した
