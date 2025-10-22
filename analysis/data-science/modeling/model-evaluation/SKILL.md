---
name: "モデル評価"
description: "精度、再現率、AUC等の指標理解。モデル性能の適切な評価と改善"
---

# モデル評価: 予測モデルの性能測定

## このスキルを使う場面

- モデルの性能を測定したい
- 複数モデルを比較したい
- モデルを改善したい
- 本番運用の判断をしたい

## 分類モデルの評価

### 1. 混同行列

```python
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

# 混同行列
cm = confusion_matrix(y_test, y_pred)
print(cm)

# 可視化
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')

# 詳細レポート
print(classification_report(y_test, y_pred))
```


### 2. 主要な指標

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 正解率（Accuracy）
accuracy = accuracy_score(y_test, y_pred)

# 適合率（Precision）
precision = precision_score(y_test, y_pred)

# 再現率（Recall / Sensitivity）
recall = recall_score(y_test, y_pred)

# F1スコア
f1 = f1_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")
```


### 3. ROC曲線とAUC

```python
from sklearn.metrics import roc_curve, roc_auc_score

# ROC曲線
y_pred_proba = model.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

# AUC
auc = roc_auc_score(y_test, y_pred_proba)

# プロット
plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
```


### 4. Precision-Recall曲線

```python
from sklearn.metrics import precision_recall_curve, average_precision_score

precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
ap = average_precision_score(y_test, y_pred_proba)

plt.plot(recall, precision, label=f'AP = {ap:.3f}')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
```


### 5. 閾値の最適化

```python
# 最適な閾値を見つける
from sklearn.metrics import f1_score

thresholds = np.arange(0, 1, 0.01)
f1_scores = []

for threshold in thresholds:
    y_pred_adjusted = (y_pred_proba >= threshold).astype(int)
    f1 = f1_score(y_test, y_pred_adjusted)
    f1_scores.append(f1)

optimal_threshold = thresholds[np.argmax(f1_scores)]
print(f"Optimal threshold: {optimal_threshold:.2f}")

# プロット
plt.plot(thresholds, f1_scores)
plt.xlabel('Threshold')
plt.ylabel('F1 Score')
plt.axvline(optimal_threshold, color='r', linestyle='--')
```


### 6. 多クラス分類の評価

```python
# マクロ平均とマイクロ平均
from sklearn.metrics import precision_recall_fscore_support

precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, average='macro'
)

# クラスごとの評価
print(classification_report(y_test, y_pred))

# マルチクラスROC-AUC
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
```


## 回帰モデルの評価

### 1. 主要な指標

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 平均二乗誤差（MSE）
mse = mean_squared_error(y_test, y_pred)

# 二乗平均平方根誤差（RMSE）
rmse = np.sqrt(mse)

# 平均絶対誤差（MAE）
mae = mean_absolute_error(y_test, y_pred)

# 決定係数（R²）
r2 = r2_score(y_test, y_pred)

# 調整済みR²
n = len(y_test)
p = X_test.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

print(f"MSE: {mse:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")
print(f"R²: {r2:.3f}")
print(f"Adjusted R²: {adj_r2:.3f}")
```


### 2. 残差分析

```python
# 残差
residuals = y_test - y_pred

# 残差プロット
plt.scatter(y_pred, residuals)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residual Plot')

# 残差の分布
plt.hist(residuals, bins=30)
plt.xlabel('Residuals')
plt.title('Residual Distribution')

# Q-Qプロット
from scipy import stats
stats.probplot(residuals, dist="norm", plot=plt)
```


### 3. 予測値vs実測値

```python
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         'r--', lw=2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Predicted vs Actual')

# 相関係数
correlation = np.corrcoef(y_test, y_pred)[0, 1]
print(f"Correlation: {correlation:.3f}")
```


## クラスタリングの評価

### 1. シルエットスコア

```python
from sklearn.metrics import silhouette_score, silhouette_samples

# シルエットスコア
score = silhouette_score(X, clusters)
print(f"Silhouette Score: {score:.3f}")

# サンプルごとのシルエット値
sample_scores = silhouette_samples(X, clusters)

# 可視化
for i in range(n_clusters):
    cluster_scores = sample_scores[clusters == i]
    cluster_scores.sort()
    plt.fill_betweenx(
        np.arange(len(cluster_scores)),
        0, cluster_scores,
        alpha=0.7
    )
```


### 2. その他の指標

```python
from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score

# Davies-Bouldin指数（小さいほど良い）
db_score = davies_bouldin_score(X, clusters)

# Calinski-Harabasz指数（大きいほど良い）
ch_score = calinski_harabasz_score(X, clusters)

print(f"Davies-Bouldin: {db_score:.3f}")
print(f"Calinski-Harabasz: {ch_score:.3f}")
```


## モデル比較

### 1. 交差検証スコア

```python
from sklearn.model_selection import cross_validate

models = {
    'Logistic': LogisticRegression(),
    'Random Forest': RandomForestClassifier(),
    'XGBoost': XGBClassifier()
}

results = {}
for name, model in models.items():
    cv_results = cross_validate(
        model, X, y,
        cv=5,
        scoring=['accuracy', 'roc_auc'],
        return_train_score=True
    )
    results[name] = cv_results

# 結果の比較
for name, cv_results in results.items():
    print(f"\n{name}:")
    print(f"  Test Accuracy: {cv_results['test_accuracy'].mean():.3f}")
    print(f"  Test AUC: {cv_results['test_roc_auc'].mean():.3f}")
```


### 2. 学習曲線

```python
from sklearn.model_selection import learning_curve

train_sizes, train_scores, test_scores = learning_curve(
    model, X, y,
    cv=5,
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='accuracy'
)

# プロット
train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
test_mean = test_scores.mean(axis=1)
test_std = test_scores.std(axis=1)

plt.plot(train_sizes, train_mean, label='Training score')
plt.plot(train_sizes, test_mean, label='Cross-validation score')
plt.fill_between(train_sizes, train_mean - train_std,
                 train_mean + train_std, alpha=0.1)
plt.fill_between(train_sizes, test_mean - test_std,
                 test_mean + test_std, alpha=0.1)
plt.xlabel('Training Size')
plt.ylabel('Score')
plt.legend()
```


### 3. 検証曲線

```python
from sklearn.model_selection import validation_curve

param_range = [1, 3, 5, 7, 10, 15, 20]
train_scores, test_scores = validation_curve(
    RandomForestClassifier(),
    X, y,
    param_name='max_depth',
    param_range=param_range,
    cv=5,
    scoring='accuracy'
)

# プロット
train_mean = train_scores.mean(axis=1)
test_mean = test_scores.mean(axis=1)

plt.plot(param_range, train_mean, label='Training score')
plt.plot(param_range, test_mean, label='Cross-validation score')
plt.xlabel('max_depth')
plt.ylabel('Score')
plt.legend()
```


## ビジネス指標との連携

```python
# コストを考慮した評価
def business_value(y_true, y_pred):
    """
    True Positive: +100円（正しく予測して獲得）
    False Positive: -10円（誤って投資）
    False Negative: -50円（機会損失）
    True Negative: 0円（何もしない）
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    value = tp * 100 + fp * (-10) + fn * (-50) + tn * 0
    return value

# 閾値ごとのビジネス価値
for threshold in [0.3, 0.5, 0.7]:
    y_pred = (y_pred_proba >= threshold).astype(int)
    value = business_value(y_test, y_pred)
    print(f"Threshold {threshold}: ¥{value:,}")
```


## ベストプラクティス

- 複数の指標で総合評価
- ビジネス目標に合った指標を選択
- 不均衡データではAccuracyだけで判断しない
- 交差検証で安定性を確認
- 学習曲線で過学習を確認
- テストデータは最後まで使わない

## 検証ポイント

- [ ] 適切な評価指標を選択した
- [ ] 複数の視点で評価した
- [ ] 交差検証を実施した
- [ ] 過学習を確認した
- [ ] ビジネス指標と連携した
- [ ] モデルの弱点を特定した
