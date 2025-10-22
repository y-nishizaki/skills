---
name: "特化型機械学習（NLP/CV）"
description: "自然言語処理と画像認識。専門分野での応用"
---

# 特化型機械学習: NLP/画像認識

## このスキルを使う場面

- テキストデータを分析したい
- 画像データから情報を抽出したい
- チャットボットを構築したい
- 画像分類・物体検出が必要

## 自然言語処理（NLP）

### 1. テキスト前処理

```python
import re
from janome.tokenizer import Tokenizer

# 日本語の形態素解析
tokenizer = Tokenizer()
tokens = tokenizer.tokenize("これは自然言語処理の例です", wakati=True)

# 英語の前処理
import nltk
from nltk.corpus import stopwords

def preprocess_text(text):
    # 小文字化
    text = text.lower()
    # 記号削除
    text = re.sub(r'[^\w\s]', '', text)
    # ストップワード除去
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in text.split() if w not in stop_words]
    return ' '.join(tokens)
```


### 2. ベクトル化

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(documents)

# Word2Vec
from gensim.models import Word2Vec
model = Word2Vec(sentences, vector_size=100, window=5, min_count=2)

# 事前学習モデル（Transformers）
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

inputs = tokenizer(text, return_tensors='pt')
outputs = model(**inputs)
```


### 3. NLPタスク

```python
# 感情分析
from transformers import pipeline
classifier = pipeline('sentiment-analysis')
result = classifier("This is amazing!")

# 名前付き実体認識（NER）
ner = pipeline('ner')
entities = ner("Apple was founded by Steve Jobs in California")

# 要約
summarizer = pipeline('summarization')
summary = summarizer(long_text, max_length=130, min_length=30)

# 質問応答
qa = pipeline('question-answering')
answer = qa(question="Who founded Apple?", context=text)
```


## 画像認識（Computer Vision）

### 1. 画像前処理

```python
from PIL import Image
import numpy as np

# 画像読み込み
img = Image.open('image.jpg')

# リサイズ
img_resized = img.resize((224, 224))

# 正規化
img_array = np.array(img_resized) / 255.0

# データ拡張
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2
)
```


### 2. 画像分類

```python
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions

# 事前学習モデル
model = ResNet50(weights='imagenet')

# 推論
img = image.load_img('image.jpg', target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

preds = model.predict(x)
predictions = decode_predictions(preds, top=3)[0]
```


### 3. 物体検出

```python
# YOLOv5
import torch

# モデルロード
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# 推論
results = model('image.jpg')
results.show()

# バウンディングボックス取得
boxes = results.xyxy[0]  # x1, y1, x2, y2, confidence, class
```


### 4. セグメンテーション

```python
# Mask R-CNN
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")

predictor = DefaultPredictor(cfg)
outputs = predictor(image)
```


## 転移学習

### 1. ファインチューニング

```python
from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, models

# 事前学習モデル（特徴抽出部を固定）
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

# 新しい分類層を追加
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_data, epochs=10)
```


### 2. 事前学習モデルの活用

**NLP**: BERT, GPT, T5, RoBERTa
**CV**: ResNet, VGG, EfficientNet, Vision Transformer

## 最新トレンド

### 1. Transformer アーキテクチャ

- Attention機構
- BERT（双方向）
- GPT（一方向）
- Vision Transformer（画像）

### 2. Few-shot Learning

- 少量のデータで学習
- Meta-learning
- Prompt Engineering

### 3. マルチモーダル

- テキスト + 画像
- CLIP, DALL-E
- 統合的な理解

## ベストプラクティス

- 事前学習モデルの活用
- データ拡張で汎化性能向上
- 適切な評価指標
- 計算リソースの最適化
- 最新の研究動向のキャッチアップ

## 検証ポイント

- [ ] 適切な前処理を実施した
- [ ] 事前学習モデルを活用した
- [ ] ドメイン特化のファインチューニング
- [ ] 適切な評価指標で測定した
- [ ] 計算コストを考慮した
