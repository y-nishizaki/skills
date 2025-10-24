---
name: pdf
description: PythonライブラリとコマンドラインツールでPDF処理操作を実行する
---

# PDF処理ガイド

## 概要

このガイドでは、Pythonライブラリとコマンドラインツールを使用した基本的なPDF処理操作について説明します。高度な機能、JavaScriptライブラリ、詳細な例については、reference.md を参照してください。PDFフォームに記入する必要がある場合は、forms.md を読み、その指示に従ってください。

## クイックスタート

```python
from pypdf import PdfReader, PdfWriter

# PDFを読み込む
reader = PdfReader("document.pdf")
print(f"ページ数: {len(reader.pages)}")

# テキストを抽出
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Pythonライブラリ

### pypdf - 基本操作

#### PDFの結合

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### PDFの分割

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### メタデータの抽出

```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"タイトル: {meta.title}")
print(f"著者: {meta.author}")
print(f"サブジェクト: {meta.subject}")
print(f"作成者: {meta.creator}")
```

#### ページの回転

```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # 時計回りに90度回転
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - テキストと表の抽出

#### レイアウトを保持したテキスト抽出

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### 表の抽出

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"ページ {i+1} の表 {j+1}:")
            for row in table:
                print(row)
```

#### 高度な表抽出

```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # 表が空でないことを確認
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# すべての表を結合
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - PDFの作成

#### 基本的なPDF作成

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# テキストを追加
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "reportlabで作成したPDFです")

# 線を追加
c.line(100, height - 140, 400, height - 140)

# 保存
c.save()
```

#### 複数ページのPDF作成

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# コンテンツを追加
title = Paragraph("レポートタイトル", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("これはレポートの本文です。" * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# ページ2
story.append(Paragraph("ページ2", styles['Heading1']))
story.append(Paragraph("ページ2のコンテンツ", styles['Normal']))

# PDFを構築
doc.build(story)
```

## コマンドラインツール

### pdftotext (poppler-utils)

```bash
# テキストを抽出
pdftotext input.pdf output.txt

# レイアウトを保持してテキストを抽出
pdftotext -layout input.pdf output.txt

# 特定のページを抽出
pdftotext -f 1 -l 5 input.pdf output.txt  # ページ1-5
```

### qpdf

```bash
# PDFの結合
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# ページの分割
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# ページの回転
qpdf input.pdf output.pdf --rotate=+90:1  # ページ1を90度回転

# パスワードの除去
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (利用可能な場合)

```bash
# 結合
pdftk file1.pdf file2.pdf cat output merged.pdf

# 分割
pdftk input.pdf burst

# 回転
pdftk input.pdf rotate 1east output rotated.pdf
```

## 一般的なタスク

### スキャンされたPDFからテキストを抽出

```python
# 必要なパッケージ: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# PDFを画像に変換
images = convert_from_path('scanned.pdf')

# 各ページをOCR処理
text = ""
for i, image in enumerate(images):
    text += f"ページ {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### 透かし（ウォーターマーク）の追加

```python
from pypdf import PdfReader, PdfWriter

# 透かしを作成（または既存のものを読み込む）
watermark = PdfReader("watermark.pdf").pages[0]

# すべてのページに適用
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 画像の抽出

```bash
# pdfimagesを使用（poppler-utils）
pdfimages -j input.pdf output_prefix

# すべての画像が output_prefix-000.jpg, output_prefix-001.jpg などとして抽出されます

```

### パスワード保護

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# パスワードを追加
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## クイックリファレンス

| タスク | 最適なツール | コマンド/コード |
|------|-----------|--------------|
| PDFの結合 | pypdf | `writer.add_page(page)` |
| PDFの分割 | pypdf | ファイルごとに1ページ |
| テキスト抽出 | pdfplumber | `page.extract_text()` |
| 表の抽出 | pdfplumber | `page.extract_tables()` |
| PDF作成 | reportlab | CanvasまたはPlatypus |
| コマンドライン結合 | qpdf | `qpdf --empty --pages ...` |
| スキャンPDFのOCR | pytesseract | 最初に画像に変換 |
| PDFフォームの記入 | pdf-libまたはpypdf（forms.md参照） | forms.md参照 |

## 次のステップ

- 高度なpypdfium2の使用方法については、reference.md を参照してください
- JavaScriptライブラリ（pdf-lib）については、reference.md を参照してください
- PDFフォームに記入する必要がある場合は、forms.md の指示に従ってください
- トラブルシューティングガイドについては、reference.md を参照してください
