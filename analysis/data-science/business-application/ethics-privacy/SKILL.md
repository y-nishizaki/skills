---
name: "倫理・プライバシー意識"
description: "データ利用の法的・倫理的ルール。責任あるAIの実践"
---

# 倫理・プライバシー意識: 責任あるデータ活用

## このスキルを使う場面

- データ収集・利用を開始するとき
- モデルを本番環境にデプロイするとき
- プライバシーに配慮が必要なとき
- 公平性を確保したいとき

## プライバシー保護

### 1. 個人情報の取り扱い

**日本の法律**: 個人情報保護法
- 個人を識別できる情報
- 取得時の利用目的明示
- 本人同意の原則
- 安全管理措置

**GDPR（EU）**:
- データの最小化
- 忘れられる権利
- データポータビリティ
- 処理の合法性

### 2. 匿名化・仮名化

```python
# PII（個人識別情報）の削除
pii_columns = ['name', 'email', 'phone', 'address']
df_anonymized = df.drop(columns=pii_columns)

# ハッシュ化
import hashlib
def hash_id(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

df['user_id_hashed'] = df['user_id'].apply(hash_id)

# k-匿名性の確保
# 同じ属性の組み合わせを持つレコードがk個以上
quasi_identifiers = ['age_group', 'gender', 'zip_code']
counts = df.groupby(quasi_identifiers).size()
print(f"Minimum k: {counts.min()}")
```

### 3. 差分プライバシー

```python
# ノイズの追加で個人の寄与を隠す
import numpy as np

def add_laplace_noise(value, sensitivity, epsilon):
    """
    epsilon: プライバシー予算（小さいほど強い保護）
    """
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise

# 集計値へのノイズ追加
true_count = 1000
private_count = add_laplace_noise(true_count, sensitivity=1, epsilon=0.1)
```

## 公平性とバイアス

### 1. バイアスの種類

**データバイアス**:
- 選択バイアス
- 測定バイアス
- 歴史的バイアス

**アルゴリズムバイアス**:
- 特定グループへの不公平な扱い
- フィードバックループ

### 2. 公平性の指標

```python
from sklearn.metrics import confusion_matrix

def demographic_parity(y_true, y_pred, sensitive_attr):
    """異なるグループで予測率が同じか"""
    groups = np.unique(sensitive_attr)
    selection_rates = []

    for group in groups:
        mask = (sensitive_attr == group)
        selection_rate = y_pred[mask].mean()
        selection_rates.append(selection_rate)

    return max(selection_rates) / min(selection_rates)

def equal_opportunity(y_true, y_pred, sensitive_attr):
    """異なるグループで真陽性率が同じか"""
    groups = np.unique(sensitive_attr)
    tpr_list = []

    for group in groups:
        mask = (sensitive_attr == group)
        cm = confusion_matrix(y_true[mask], y_pred[mask])
        tpr = cm[1, 1] / (cm[1, 1] + cm[1, 0])
        tpr_list.append(tpr)

    return max(tpr_list) / min(tpr_list)

# バイアス検出
ratio = demographic_parity(y_test, y_pred, gender)
print(f"Demographic parity ratio: {ratio:.2f}")
# 1.0に近いほど公平
```

### 3. バイアスの軽減

```python
# リサンプリング
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# 重み付け
from sklearn.utils.class_weight import compute_sample_weight
sample_weights = compute_sample_weight('balanced', y)
model.fit(X, y, sample_weight=sample_weights)

# 閾値調整（グループごと）
thresholds = {}
for group in ['A', 'B']:
    mask = (sensitive_attr == group)
    # グループごとに最適な閾値を決定
    thresholds[group] = find_optimal_threshold(y_test[mask], y_pred_proba[mask])
```

## データガバナンス

### 1. データカタログ

```yaml
# メタデータの管理
dataset:
  name: "customer_transactions"
  description: "顧客の取引履歴"
  owner: "data-team"
  sensitivity: "high"
  pii_fields:
    - customer_id
    - email
    - phone
  retention_period: "3 years"
  access_control:
    - role: "analyst"
      permission: "read"
    - role: "ml-engineer"
      permission: "read-write"
```

### 2. データアクセス管理

- ロールベースアクセス制御（RBAC）
- 最小権限の原則
- アクセスログの記録
- 定期的な権限見直し

### 3. データライフサイクル

```python
# データ保持ポリシー
retention_policy = {
    'transaction_data': '7 years',  # 法的要件
    'user_behavior_logs': '2 years',
    'temporary_analysis': '90 days'
}

# 自動削除
def delete_expired_data(table_name, date_column):
    cutoff_date = datetime.now() - retention_policy[table_name]
    query = f"""
        DELETE FROM {table_name}
        WHERE {date_column} < '{cutoff_date}'
    """
    execute_query(query)
```

## 透明性と説明可能性

### 1. モデルの説明

```python
# SHAP値で特徴量の寄与を説明
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# 個別予測の説明
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# 全体的な特徴量重要度
shap.summary_plot(shap_values, X_test)
```

### 2. モデルカード

```markdown
# Model Card

## Model Details
- モデルタイプ: XGBoost Classifier
- バージョン: 1.2
- 作成日: 2025-01-15
- 作成者: Data Science Team

## Intended Use
- 用途: 顧客離脱予測
- 対象ユーザー: マーケティングチーム
- 対象外用途: 個人の評価・採用判断

## Training Data
- データソース: 社内CRM
- 期間: 2023-2025
- サイズ: 100万レコード
- 前処理: 欠損値補完、外れ値除去

## Performance
- AUC: 0.85
- Precision: 0.78
- Recall: 0.82
- 評価データ: 2024年12月-2025年1月

## Limitations
- 新規顧客には精度が低い
- 季節変動を完全には捉えられない
- 外部要因（経済状況など）は考慮外

## Ethical Considerations
- 年齢・性別によるバイアス: 確認済み（公平性指標 0.95）
- プライバシー: 個人識別情報は使用せず
```

## 責任あるAIの実践

### 1. チェックリスト

- [ ] データ収集に同意を得たか
- [ ] プライバシーリスクを評価したか
- [ ] バイアスをチェックしたか
- [ ] 公平性指標を測定したか
- [ ] 透明性を確保したか
- [ ] 説明可能性を考慮したか
- [ ] セキュリティ対策をしたか
- [ ] 法的要件を満たしたか

### 2. 倫理委員会・レビュー

- プロジェクト開始時のレビュー
- 定期的な監査
- インシデント報告制度
- 改善プロセス

### 3. 継続的モニタリング

```python
# モデルの公平性を定期的にチェック
def fairness_monitoring(model, X, y, sensitive_attr):
    y_pred = model.predict(X)

    metrics = {
        'demographic_parity': demographic_parity(y, y_pred, sensitive_attr),
        'equal_opportunity': equal_opportunity(y, y_pred, sensitive_attr),
        'overall_accuracy': accuracy_score(y, y_pred)
    }

    # アラート
    if metrics['demographic_parity'] > 1.2:
        send_alert("Fairness issue detected")

    return metrics

# 週次で実行
schedule.every().week.do(lambda: fairness_monitoring(model, X_prod, y_prod, sensitive))
```

## ベストプラクティス

- Privacy by Design
- セキュリティバイデザイン
- 継続的な倫理評価
- 透明性の確保
- ステークホルダーとの対話
- 最新の法規制の把握

## 検証ポイント

- [ ] 法的要件を満たしている
- [ ] プライバシーを保護している
- [ ] バイアスをチェックした
- [ ] 公平性を確保している
- [ ] 透明性がある
- [ ] 説明可能である
- [ ] 継続的にモニタリングしている
