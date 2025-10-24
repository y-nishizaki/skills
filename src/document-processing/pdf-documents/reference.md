# PDF処理高度なリファレンス

このドキュメントには、メインのスキル指示書に含まれていない高度なPDF処理機能、詳細な例、追加ライブラリが含まれています。

## pypdfium2ライブラリ（Apache/BSDライセンス）

### 概要

pypdfium2は、PDFium（ChromiumのPDFライブラリ）のPythonバインディングです。高速なPDFレンダリング、画像生成に優れており、PyMuPDFの代替として機能します。

### PDFを画像にレンダリング

```python
import pypdfium2 as pdfium
from PIL import Image

# PDFを読み込む
pdf = pdfium.PdfDocument("document.pdf")

# ページを画像にレンダリング
page = pdf[0]  # 最初のページ
bitmap = page.render(
    scale=2.0,  # 高解像度
    rotation=0  # 回転なし
)

# PIL Imageに変換
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# 複数ページを処理
for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

### pypdfium2でテキストを抽出

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"ページ {i+1} のテキスト長: {len(text)} 文字")
```

## JavaScriptライブラリ

### pdf-lib（MITライセンス）

pdf-libは、あらゆるJavaScript環境でPDFドキュメントを作成・編集できる強力なJavaScriptライブラリです。

#### 既存PDFの読み込みと編集

```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function manipulatePDF() {
    // 既存PDFを読み込む
    const existingPdfBytes = fs.readFileSync('input.pdf');
    const pdfDoc = await PDFDocument.load(existingPdfBytes);

    // ページ数を取得
    const pageCount = pdfDoc.getPageCount();
    console.log(`ドキュメントは${pageCount}ページです`);

    // 新しいページを追加
    const newPage = pdfDoc.addPage([600, 400]);
    newPage.drawText('pdf-libで追加', {
        x: 100,
        y: 300,
        size: 16
    });

    // 編集したPDFを保存
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('modified.pdf', pdfBytes);
}
```

#### ゼロから複雑なPDFを作成

```javascript
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import fs from 'fs';

async function createPDF() {
    const pdfDoc = await PDFDocument.create();

    // フォントを追加
    const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
    const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

    // ページを追加
    const page = pdfDoc.addPage([595, 842]); // A4サイズ
    const { width, height } = page.getSize();

    // スタイル付きテキストを追加
    page.drawText('請求書 #12345', {
        x: 50,
        y: height - 50,
        size: 18,
        font: helveticaBold,
        color: rgb(0.2, 0.2, 0.8)
    });

    // 矩形を追加（ヘッダー背景）
    page.drawRectangle({
        x: 40,
        y: height - 100,
        width: width - 80,
        height: 30,
        color: rgb(0.9, 0.9, 0.9)
    });

    // 表形式のコンテンツを追加
    const items = [
        ['項目', '数量', '価格', '合計'],
        ['ウィジェット', '2', '$50', '$100'],
        ['ガジェット', '1', '$75', '$75']
    ];

    let yPos = height - 150;
    items.forEach(row => {
        let xPos = 50;
        row.forEach(cell => {
            page.drawText(cell, {
                x: xPos,
                y: yPos,
                size: 12,
                font: helveticaFont
            });
            xPos += 120;
        });
        yPos -= 25;
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('created.pdf', pdfBytes);
}
```

#### 高度な結合と分割操作

```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function mergePDFs() {
    // 新しいドキュメントを作成
    const mergedPdf = await PDFDocument.create();

    // ソースPDFを読み込む
    const pdf1Bytes = fs.readFileSync('doc1.pdf');
    const pdf2Bytes = fs.readFileSync('doc2.pdf');

    const pdf1 = await PDFDocument.load(pdf1Bytes);
    const pdf2 = await PDFDocument.load(pdf2Bytes);

    // 最初のPDFからページをコピー
    const pdf1Pages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices());
    pdf1Pages.forEach(page => mergedPdf.addPage(page));

    // 2番目のPDFから特定のページをコピー（ページ0, 2, 4）
    const pdf2Pages = await mergedPdf.copyPages(pdf2, [0, 2, 4]);
    pdf2Pages.forEach(page => mergedPdf.addPage(page));

    const mergedPdfBytes = await mergedPdf.save();
    fs.writeFileSync('merged.pdf', mergedPdfBytes);
}
```

### pdfjs-dist（Apacheライセンス）

PDF.jsは、ブラウザでPDFをレンダリングするためのMozillaのJavaScriptライブラリです。

#### 基本的なPDF読み込みとレンダリング

```javascript
import * as pdfjsLib from 'pdfjs-dist';

// ワーカーを設定（パフォーマンスに重要）
pdfjsLib.GlobalWorkerOptions.workerSrc = './pdf.worker.js';

async function renderPDF() {
    // PDFを読み込む
    const loadingTask = pdfjsLib.getDocument('document.pdf');
    const pdf = await loadingTask.promise;

    console.log(`${pdf.numPages}ページのPDFを読み込みました`);

    // 最初のページを取得
    const page = await pdf.getPage(1);
    const viewport = page.getViewport({ scale: 1.5 });

    // キャンバスにレンダリング
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    const renderContext = {
        canvasContext: context,
        viewport: viewport
    };

    await page.render(renderContext).promise;
    document.body.appendChild(canvas);
}
```

#### 座標付きでテキストを抽出

```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function extractText() {
    const loadingTask = pdfjsLib.getDocument('document.pdf');
    const pdf = await loadingTask.promise;

    let fullText = '';

    // すべてのページからテキストを抽出
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();

        const pageText = textContent.items
            .map(item => item.str)
            .join(' ');

        fullText += `\n--- ページ ${i} ---\n${pageText}`;

        // 高度な処理のために座標付きでテキストを取得
        const textWithCoords = textContent.items.map(item => ({
            text: item.str,
            x: item.transform[4],
            y: item.transform[5],
            width: item.width,
            height: item.height
        }));
    }

    console.log(fullText);
    return fullText;
}
```

#### 注釈とフォームの抽出

```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function extractAnnotations() {
    const loadingTask = pdfjsLib.getDocument('annotated.pdf');
    const pdf = await loadingTask.promise;

    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const annotations = await page.getAnnotations();

        annotations.forEach(annotation => {
            console.log(`注釈タイプ: ${annotation.subtype}`);
            console.log(`内容: ${annotation.contents}`);
            console.log(`座標: ${JSON.stringify(annotation.rect)}`);
        });
    }
}
```

## 高度なコマンドライン操作

### poppler-utils高度な機能

#### バウンディングボックス座標付きでテキストを抽出

```bash
# バウンディングボックス座標付きでテキストを抽出（構造化データに不可欠）
pdftotext -bbox-layout document.pdf output.xml

# XML出力には各テキスト要素の正確な座標が含まれます

```

#### 高度な画像変換

```bash
# 特定の解像度でPNG画像に変換
pdftoppm -png -r 300 document.pdf output_prefix

# 高解像度で特定のページ範囲を変換
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res_pages

# 品質設定でJPEGに変換
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

#### 埋め込み画像の抽出

```bash
# メタデータ付きですべての埋め込み画像を抽出
pdfimages -j -p document.pdf page_images

# 抽出せずに画像情報を一覧表示
pdfimages -list document.pdf

# 元の形式で画像を抽出
pdfimages -all document.pdf images/img
```

### qpdf高度な機能

#### 複雑なページ操作

```bash
# PDFをページグループに分割
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# 複雑な範囲で特定のページを抽出
qpdf input.pdf --pages input.pdf 1,3-5,8,10-end -- extracted.pdf

# 複数のPDFから特定のページを結合
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 doc3.pdf 2,4 -- combined.pdf
```

#### PDFの最適化と修復

```bash
# Web用にPDFを最適化（ストリーミング用に線形化）
qpdf --linearize input.pdf optimized.pdf

# 未使用オブジェクトを削除して圧縮
qpdf --optimize-level=all input.pdf compressed.pdf

# 破損したPDF構造を修復
qpdf --check input.pdf
qpdf --fix-qdf damaged.pdf repaired.pdf

# デバッグ用に詳細なPDF構造を表示
qpdf --show-all-pages input.pdf > structure.txt
```

#### 高度な暗号化

```bash
# 特定の権限でパスワード保護を追加
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf

# 暗号化ステータスを確認
qpdf --show-encryption encrypted.pdf

# パスワード保護を削除（パスワードが必要）
qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf
```

## 高度なPythonテクニック

### pdfplumber高度な機能

#### 正確な座標付きでテキストを抽出

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # 座標付きですべてのテキストを抽出
    chars = page.chars
    for char in chars[:10]:  # 最初の10文字
        print(f"文字: '{char['text']}' 位置 x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # バウンディングボックスでテキストを抽出（左、上、右、下）
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

#### カスタム設定での高度な表抽出

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]

    # 複雑なレイアウト用のカスタム設定で表を抽出
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    # 表抽出の視覚的デバッグ
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### reportlab高度な機能

#### 表付きの専門的なレポートを作成

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# サンプルデータ
data = [
    ['製品', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['ウィジェット', '120', '135', '142', '158'],
    ['ガジェット', '85', '92', '98', '105']
]

# 表付きPDFを作成
doc = SimpleDocTemplate("report.pdf")
elements = []

# タイトルを追加
styles = getSampleStyleSheet()
title = Paragraph("四半期売上レポート", styles['Title'])
elements.append(title)

# 高度なスタイルの表を追加
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)

doc.build(elements)
```

## 複雑なワークフロー

### PDFから図/画像を抽出

#### 方法1: pdfimagesを使用（最速）

```bash
# 元の品質ですべての画像を抽出
pdfimages -all document.pdf images/img
```

#### 方法2: pypdfium2 + 画像処理を使用

```python
import pypdfium2 as pdfium
from PIL import Image
import numpy as np

def extract_figures(pdf_path, output_dir):
    pdf = pdfium.PdfDocument(pdf_path)

    for page_num, page in enumerate(pdf):
        # 高解像度ページをレンダリング
        bitmap = page.render(scale=3.0)
        img = bitmap.to_pil()

        # 処理のためにnumpyに変換
        img_array = np.array(img)

        # 簡単な図検出（非白色領域）
        mask = np.any(img_array != [255, 255, 255], axis=2)

        # 輪郭を見つけてバウンディングボックスを抽出
        # （これは簡略化 - 実際の実装にはより高度な検出が必要）

        # 検出した図を保存
        # ... 実装は特定のニーズに依存
```

### エラーハンドリング付きのバッチPDF処理

```python
import os
import glob
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_pdfs(input_dir, operation='merge'):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if operation == 'merge':
        writer = PdfWriter()
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"処理完了: {pdf_file}")
            except Exception as e:
                logger.error(f"{pdf_file}の処理に失敗: {e}")
                continue

        with open("batch_merged.pdf", "wb") as output:
            writer.write(output)

    elif operation == 'extract_text':
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                output_file = pdf_file.replace('.pdf', '.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"テキスト抽出完了: {pdf_file}")

            except Exception as e:
                logger.error(f"{pdf_file}からのテキスト抽出に失敗: {e}")
                continue
```

### 高度なPDFトリミング

```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("input.pdf")
writer = PdfWriter()

# ページをトリミング（左、下、右、上をポイント単位で指定）
page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

writer.add_page(page)
with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

## パフォーマンス最適化のヒント

### 1. 大きなPDFの場合
- PDF全体をメモリに読み込むのではなく、ストリーミングアプローチを使用
- 大きなファイルの分割には `qpdf --split-pages` を使用
- pypdfium2でページを個別に処理

### 2. テキスト抽出の場合
- プレーンテキスト抽出には `pdftotext -bbox-layout` が最速
- 構造化データと表にはpdfplumberを使用
- 非常に大きなドキュメントでは `pypdf.extract_text()` を避ける

### 3. 画像抽出の場合
- `pdfimages` はページをレンダリングするよりもはるかに高速
- プレビューには低解像度、最終出力には高解像度を使用

### 4. フォーム記入の場合
- pdf-libはほとんどの代替よりもフォーム構造を維持
- 処理前にフォームフィールドを事前検証

### 5. メモリ管理

```python
# PDFをチャンクで処理
def process_large_pdf(pdf_path, chunk_size=10):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for start_idx in range(0, total_pages, chunk_size):
        end_idx = min(start_idx + chunk_size, total_pages)
        writer = PdfWriter()

        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])

        # チャンクを処理
        with open(f"chunk_{start_idx//chunk_size}.pdf", "wb") as output:
            writer.write(output)
```

## 一般的な問題のトラブルシューティング

### 暗号化されたPDF

```python
# パスワード保護されたPDFを処理
from pypdf import PdfReader

try:
    reader = PdfReader("encrypted.pdf")
    if reader.is_encrypted:
        reader.decrypt("password")
except Exception as e:
    print(f"復号化に失敗: {e}")
```

### 破損したPDF

```bash
# qpdfで修復
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### テキスト抽出の問題

```python
# スキャンされたPDFのOCRへのフォールバック
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image)
    return text
```

## ライセンス情報

- **pypdf**: BSDライセンス
- **pdfplumber**: MITライセンス
- **pypdfium2**: Apache/BSDライセンス
- **reportlab**: BSDライセンス
- **poppler-utils**: GPL-2ライセンス
- **qpdf**: Apacheライセンス
- **pdf-lib**: MITライセンス
- **pdfjs-dist**: Apacheライセンス
