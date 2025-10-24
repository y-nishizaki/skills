# ドキュメント処理スキル (Document Processing)

ビジネスドキュメントの作成、編集、分析を自動化するスキル群です。

## 概要

このカテゴリには、主要なオフィスドキュメント形式（Word、Excel、PowerPoint、PDF）を処理するための包括的なスキルが含まれています。これらのスキルはAnthropic公式の[document-skills](https://github.com/anthropics/skills/tree/main/document-skills)を日本語化したものです。

## 利用可能なスキル

### word-documents

Word文書（.docx）の作成、編集、分析を行うスキルです。

**主な機能:**

- ドキュメントの作成と編集
- 変更履歴（トラック変更/赤線）の管理
- コメントとメタデータの操作
- テキスト抽出とMarkdown変換
- OOXML形式の直接操作

**ファイル構成:**

- `SKILL.md` - メインスキル定義
- `docx-js.md` - docx-jsライブラリのリファレンス
- `ooxml.md` - OOXML形式の詳細ガイド
- `scripts/` - Python/JavaScriptスクリプト
- `ooxml/scripts/` - OOXML処理ユーティリティ

**依存関係:** pandoc、docx (npm)、LibreOffice、defusedxml

### pdf-documents

PDF文書の作成、編集、分析を行うスキルです。

**主な機能:**

- PDFの結合と分割
- テキストと表の抽出
- PDFの作成とレンダリング
- OCR（スキャン文書の文字認識）
- パスワード保護と透かし
- フォーム処理

**ファイル構成:**

- `SKILL.md` - メインスキル定義
- `reference.md` - ツールとライブラリのリファレンス
- `forms.md` - PDFフォーム処理ガイド
- `scripts/` - Pythonスクリプト

**依存関係:** pypdf、pdfplumber、reportlab、qpdf、poppler-utils

### presentations

PowerPointプレゼンテーション（.pptx）の作成、編集、分析を行うスキルです。

**主な機能:**

- HTMLからPowerPointへの変換
- テンプレートを使用したプレゼンテーション作成
- スライドの操作（複製、並べ替え、削除）
- テキスト抽出とMarkdown変換
- OOXML形式の直接操作
- サムネイルグリッド生成

**ファイル構成:**

- `SKILL.md` - メインスキル定義
- `html2pptx.md` - HTML→PowerPoint変換ガイド
- `ooxml.md` - OOXML技術リファレンス
- `scripts/` - Python/JavaScriptスクリプト
- `ooxml/scripts/` - OOXML処理ユーティリティ

**依存関係:** markitdown、pptxgenjs、playwright、sharp、LibreOffice、poppler-utils

### spreadsheets

Excelスプレッドシート（.xlsx）の作成、編集、分析を行うスキルです。

**主な機能:**

- スプレッドシートの作成と編集
- 数式とデータ検証
- 財務モデリングのベストプラクティス
- データ分析とビジュアライゼーション
- 数式エラーの自動検出
- Excel数式の再計算

**ファイル構成:**

- `SKILL.md` - メインスキル定義
- `recalc.py` - Excel数式再計算スクリプト

**依存関係:** pandas、openpyxl、xlrd、LibreOffice

## インストール方法

### 個人用

```bash
# 全カテゴリをインストール
cp -r document-processing ~/.claude/skills/

# 特定のスキルのみインストール
cp -r document-processing/word-documents ~/.claude/skills/
cp -r document-processing/pdf-documents ~/.claude/skills/
cp -r document-processing/presentations ~/.claude/skills/
cp -r document-processing/spreadsheets ~/.claude/skills/
```

### チーム/プロジェクト用

```bash
# プロジェクトディレクトリで
mkdir -p .claude/skills
cp -r document-processing .claude/skills/
```

## 使用例

### Word文書の編集

```bash
# Claude Codeで
"この契約書の変更履歴を確認して"
"Word文書に新しいセクションを追加して"
```

### PDFの処理

```bash
# Claude Codeで
"これらのPDFファイルを結合して"
"このPDFから表を抽出してCSVに変換して"
```

### PowerPointプレゼンテーションの作成

```bash
# Claude Codeで
"このMarkdownファイルからプレゼンテーションを作成して"
"スライド3を複製してテキストを置換して"
```

### Excelスプレッドシートの分析

```bash
# Claude Codeで
"このExcelファイルの数式エラーをチェックして"
"売上データを分析してグラフを作成して"
```

## 注意事項

### ライセンス

これらのスキルはAnthropic Inc.のオリジナルスキルを日本語化したものです。ライセンスについては各スキルディレクトリの`LICENSE.txt`を参照してください。

### 依存関係

各スキルには外部ツールやライブラリが必要です。使用前に必要な依存関係をインストールしてください：

```bash
# Word文書処理
brew install pandoc libreoffice
pip install defusedxml

# PDF処理
brew install qpdf poppler
pip install pypdf pdfplumber reportlab

# PowerPointプレゼンテーション
brew install libreoffice poppler
npm install pptxgenjs
pip install markitdown playwright sharp

# Excelスプレッドシート
brew install libreoffice
pip install pandas openpyxl xlrd
```

### 技術的な制約

- **OOXML操作**: 複雑なドキュメントの直接編集にはOOXML仕様の理解が必要です
- **数式エラー**: Excelスキルは数式エラーゼロを要求します（財務モデリング基準）
- **フォント**: PowerPointスキルはWeb安全フォントのみを使用します
- **OCR精度**: PDFのOCRは元の画像品質に依存します

## トラブルシューティング

### スキルが起動しない

1. YAML frontmatterの構文を確認
2. 依存関係がインストールされているか確認
3. ファイルパスが正しいか確認

### ドキュメント処理エラー

1. 入力ファイルが破損していないか確認
2. 必要な外部ツール（pandoc、LibreOfficeなど）がインストールされているか確認
3. ファイル権限を確認

### 詳細なエラー情報

各スキルの`SKILL.md`に詳細なトラブルシューティング情報が記載されています。

## 貢献

改善提案やバグレポートは[GitHubリポジトリ](https://github.com/y-nishizaki/skills)にお願いします。

## 関連リソース

- [Anthropic公式document-skills](https://github.com/anthropics/skills/tree/main/document-skills)
- [Claude Codeスキル公式ドキュメント](https://docs.claude.com/en/docs/claude-code/skills.md)
- [OOXML仕様](https://www.ecma-international.org/publications-and-standards/standards/ecma-376/)
