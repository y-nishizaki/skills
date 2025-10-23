---
name: "ai-ml-security"
description: >
  AI/MLセキュリティの実践を支援します。モデル盗用、データ汚染攻撃（Data Poisoning）、
  敵対的サンプル（Adversarial Examples）、モデル反転攻撃、プライバシー保護機械学習、
  AIシステムのセキュアな設計など、AI/MLの脅威と対策に使用します。
  キーワード - AI セキュリティ、ML セキュリティ、敵対的機械学習、モデル盗用、
  データポイズニング、プライバシー保護。
version: 1.0.0
---

# AI/MLセキュリティスキル

## 目的

このスキルは、AI/MLシステムに対するセキュリティ脅威と防御策を提供します。
敵対的攻撃、データポイズニング、モデル盗用、プライバシー侵害などの脅威を理解し、
セキュアなAI/MLシステムを構築するための実践的知識を含みます。

## AI/MLセキュリティの脅威分類

### 1. 訓練時攻撃

**データポイズニング（Data Poisoning）:**
- 訓練データに悪意のあるサンプルを混入
- モデルの決定境界を操作
- バックドア攻撃

**例:**
```python
# クリーンデータ
X_clean = [[1, 2], [2, 3], [3, 4]]
y_clean = [0, 0, 0]

# ポイズニングデータ
X_poison = [[5, 5], [5.1, 5.1]]
y_poison = [1, 1]  # 誤ったラベル

# 混入
X_train = X_clean + X_poison
y_train = y_clean + y_poison
```

### 2. 推論時攻撃

**敵対的サンプル（Adversarial Examples）:**
- 微小な摂動でモデルを欺く
- 人間には識別不可能
- 誤分類を引き起こす

**FGSM攻撃例:**
```python
import torch
import torch.nn.functional as F

def fgsm_attack(model, image, label, epsilon=0.1):
    """
    Fast Gradient Sign Method (FGSM) 攻撃
    """
    image.requires_grad = True

    # 順伝播
    output = model(image)
    loss = F.cross_entropy(output, label)

    # 勾配計算
    model.zero_grad()
    loss.backward()

    # 摂動生成
    perturbation = epsilon * image.grad.sign()
    adversarial_image = image + perturbation

    return adversarial_image.detach()

# 使用例
model = ...  # 訓練済みモデル
image = ...  # 入力画像
label = ...  # 正しいラベル

adv_image = fgsm_attack(model, image, label, epsilon=0.03)
```

**PGD攻撃（より強力）:**
```python
def pgd_attack(model, image, label, epsilon=0.3, alpha=0.01, num_iter=40):
    """
    Projected Gradient Descent 攻撃
    """
    original_image = image.clone()
    adv_image = image.clone()

    for i in range(num_iter):
        adv_image.requires_grad = True

        output = model(adv_image)
        loss = F.cross_entropy(output, label)

        model.zero_grad()
        loss.backward()

        # 勾配方向にステップ
        adv_image = adv_image + alpha * adv_image.grad.sign()

        # epsilon球内に制限
        perturbation = torch.clamp(adv_image - original_image, -epsilon, epsilon)
        adv_image = torch.clamp(original_image + perturbation, 0, 1).detach()

    return adv_image
```

### 3. モデル抽出攻撃

**モデル盗用:**
- APIクエリを通じてモデルを複製
- 決定境界の推定

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def model_extraction(target_model, num_queries=10000, feature_dim=10):
    """
    モデル抽出攻撃のシミュレーション
    """
    # ランダムクエリ生成
    X_query = np.random.randn(num_queries, feature_dim)

    # ターゲットモデルに問い合わせ
    y_query = target_model.predict(X_query)

    # 代替モデル訓練（盗用モデル）
    stolen_model = RandomForestClassifier()
    stolen_model.fit(X_query, y_query)

    return stolen_model
```

### 4. プライバシー攻撃

**メンバーシップ推論攻撃:**
- 特定のデータがトレーニングに使用されたか推測

```python
def membership_inference_attack(target_model, data, label):
    """
    メンバーシップ推論攻撃
    訓練データに含まれていたか判定
    """
    # 予測確率取得
    prob = target_model.predict_proba([data])[0]
    confidence = prob[label]

    # 高い確信度 = 訓練データの可能性高
    threshold = 0.9
    if confidence > threshold:
        return "Likely in training set"
    else:
        return "Likely not in training set"
```

**モデル反転攻撃:**
- モデルから訓練データを復元

## 防御策

### 1. 敵対的訓練（Adversarial Training）

```python
def adversarial_training(model, train_loader, optimizer, epsilon=0.3):
    """
    敵対的サンプルを含めた訓練
    """
    model.train()

    for images, labels in train_loader:
        # クリーンサンプルでの訓練
        optimizer.zero_grad()
        clean_output = model(images)
        clean_loss = F.cross_entropy(clean_output, labels)

        # 敵対的サンプル生成
        adv_images = fgsm_attack(model, images, labels, epsilon)

        # 敵対的サンプルでの訓練
        adv_output = model(adv_images)
        adv_loss = F.cross_entropy(adv_output, labels)

        # 合計損失
        total_loss = clean_loss + adv_loss
        total_loss.backward()
        optimizer.step()
```

### 2. 入力検証と前処理

```python
def defend_against_adversarial(image, defense_type='jpeg'):
    """
    敵対的サンプルに対する防御
    """
    if defense_type == 'jpeg':
        # JPEG圧縮（高周波ノイズ除去）
        from PIL import Image
        import io

        img_pil = Image.fromarray((image * 255).astype('uint8'))
        buffer = io.BytesIO()
        img_pil.save(buffer, format='JPEG', quality=75)
        buffer.seek(0)
        defended_img = Image.open(buffer)
        return np.array(defended_img) / 255.0

    elif defense_type == 'median_filter':
        # メディアンフィルタ
        from scipy.ndimage import median_filter
        return median_filter(image, size=3)

    elif defense_type == 'feature_squeezing':
        # 特徴圧縮（ビット深度削減）
        bit_depth = 4
        return np.round(image * (2**bit_depth)) / (2**bit_depth)
```

### 3. モデルロバスト性評価

**CleverHans:**
```python
from cleverhans.tf2.attacks.fast_gradient_method import fast_gradient_method

def evaluate_robustness(model, test_images, test_labels):
    """
    モデルのロバスト性評価
    """
    # クリーン精度
    clean_acc = model.evaluate(test_images, test_labels)[1]

    # 敵対的サンプル生成
    adv_images = fast_gradient_method(model, test_images, eps=0.3, norm=np.inf)

    # 敵対的精度
    adv_acc = model.evaluate(adv_images, test_labels)[1]

    print(f"Clean Accuracy: {clean_acc:.2%}")
    print(f"Adversarial Accuracy: {adv_acc:.2%}")
    print(f"Robustness Gap: {(clean_acc - adv_acc):.2%}")
```

### 4. 差分プライバシー（Differential Privacy）

```python
from tensorflow_privacy.privacy.optimizers import dp_optimizer_keras

def train_with_differential_privacy(
    model,
    train_data,
    noise_multiplier=1.1,
    l2_norm_clip=1.0,
    num_microbatches=250
):
    """
    差分プライバシーを用いた訓練
    """
    optimizer = dp_optimizer_keras.DPKerasSGDOptimizer(
        l2_norm_clip=l2_norm_clip,
        noise_multiplier=noise_multiplier,
        num_microbatches=num_microbatches,
        learning_rate=0.15
    )

    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(train_data, epochs=10, validation_split=0.2)
```

### 5. フェデレーテッドラーニング

```python
# 概念的な実装
class FederatedLearning:
    def __init__(self, global_model):
        self.global_model = global_model

    def client_update(self, client_data):
        """
        クライアント側での更新
        """
        local_model = self.global_model.copy()
        local_model.fit(client_data)
        return local_model.get_weights()

    def aggregate(self, client_weights):
        """
        複数クライアントの重みを集約
        """
        avg_weights = []
        for weights_list in zip(*client_weights):
            avg_weights.append(
                np.mean(weights_list, axis=0)
            )
        self.global_model.set_weights(avg_weights)
```

## MLOpsセキュリティ

### モデルの完全性検証

```python
import hashlib
import json

def create_model_manifest(model, model_path):
    """
    モデルマニフェスト作成（完全性検証用）
    """
    # モデルハッシュ
    with open(model_path, 'rb') as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()

    # メタデータ
    manifest = {
        'model_hash': model_hash,
        'architecture': model.to_json(),
        'training_date': '2024-01-01',
        'dataset_version': '1.0',
        'accuracy': 0.95,
        'signature': None  # デジタル署名
    }

    # マニフェスト保存
    with open('model_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

def verify_model(model_path, manifest_path):
    """
    モデルの完全性検証
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    with open(model_path, 'rb') as f:
        current_hash = hashlib.sha256(f.read()).hexdigest()

    if current_hash == manifest['model_hash']:
        print("✅ Model integrity verified")
        return True
    else:
        print("❌ Model has been tampered with")
        return False
```

### モデルモニタリング

```python
def monitor_model_drift(model, new_data, reference_data):
    """
    モデルドリフト検出
    """
    # 予測分布比較
    ref_predictions = model.predict(reference_data)
    new_predictions = model.predict(new_data)

    from scipy.stats import ks_2samp

    # Kolmogorov-Smirnov 検定
    statistic, p_value = ks_2samp(
        ref_predictions.flatten(),
        new_predictions.flatten()
    )

    if p_value < 0.05:
        print(f"⚠️  Significant drift detected (p-value: {p_value:.4f})")
        return True
    else:
        print(f"✅ No significant drift (p-value: {p_value:.4f})")
        return False
```

## 責任あるAI

### バイアス検出

```python
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric

def detect_bias(dataset, protected_attribute):
    """
    データセットのバイアス検出
    """
    metric = BinaryLabelDatasetMetric(
        dataset,
        unprivileged_groups=[{protected_attribute: 0}],
        privileged_groups=[{protected_attribute: 1}]
    )

    print(f"Disparate Impact: {metric.disparate_impact():.2f}")
    print(f"Statistical Parity Difference: {metric.statistical_parity_difference():.2f}")
```

### 説明可能性（XAI）

```python
import shap

def explain_model_predictions(model, data):
    """
    SHAPを使用した予測説明
    """
    explainer = shap.Explainer(model, data)
    shap_values = explainer(data)

    # 特徴量重要度可視化
    shap.summary_plot(shap_values, data)

    return shap_values
```

## ベストプラクティス

1. **セキュアな開発ライフサイクル**
   - 脅威モデリング
   - セキュリティテスト
   - 継続的監視

2. **データガバナンス**
   - データ出所の検証
   - ラベル品質管理
   - プライバシー保護

3. **モデルガバナンス**
   - バージョン管理
   - アクセス制御
   - 監査ログ

4. **レッドチーム演習**
   - 定期的な攻撃シミュレーション
   - ロバスト性評価

5. **透明性と説明責任**
   - モデル文書化
   - 決定の説明可能性
   - バイアス監視

## 参考リソース

- OWASP Top 10 for Large Language Model Applications
- NIST AI Risk Management Framework
- Microsoft Responsible AI Standard
- Google's ML Fairness

## 注意事項

- AI/MLセキュリティは発展途上
- 攻撃と防御の進化
- 規制動向の注視
- 倫理的考慮事項
