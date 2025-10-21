# スキル作成リファレンスドキュメント

このリファレンスは、[anthropics/skills](https://github.com/anthropics/skills)公式リポジトリの仕様と、このリポジトリのパターンを統合したものです。

## 目次

1. [公式スキル仕様](#公式スキル仕様)
2. [Progressive Disclosure（段階的開示）](#progressive-disclosure段階的開示)
3. [YAMLフロントマター仕様](#yamlフロントマター仕様)
4. [ファイル構造パターン](#ファイル構造パターン)
5. [記述スタイルガイド](#記述スタイルガイド)
6. [説明の書き方ガイド](#説明の書き方ガイド)
7. [指示の書き方ベストプラクティス](#指示の書き方ベストプラクティス)
8. [バンドルリソースの使用](#バンドルリソースの使用)
9. [ツール使用ガイドライン](#ツール使用ガイドライン)
10. [テストと検証](#テストと検証)
11. [よくある落とし穴](#よくある落とし穴)
12. [高度なパターン](#高度なパターン)

---

## 公式スキル仕様

公式仕様（[Agent Skills Spec v1.0](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)）に基づく要件：

### 必須要素

- **SKILL.md**: スキルのエントリーポイント（唯一の必須ファイル）
- **YAMLフロントマター**: name と description フィールドが必須
- **ディレクトリ名**: nameフィールドと一致する必要あり

### 任意要素

- **scripts/**: 実行可能なスクリプト
- **references/**: リファレンスドキュメント
- **assets/**: 出力用ファイル

### 公式リソース

- [anthropics/skills](https://github.com/anthropics/skills) - 公式スキルコレクション
- [agent_skills_spec.md](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md) - 正式な仕様
- [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) - 公式のスキル作成ガイド

---

## Progressive Disclosure（段階的開示）

公式の設計原則に基づく3段階のコンテキスト読み込みシステム：

### レベル1: メタデータ（常時読み込み、~100語）

```yaml
---
name: skill-name
description: >
  Complete description of functionality and when to use it.
---
```

- **目的**: Claudeがスキルを起動するタイミングを決定
- **内容**: name + description のみ
- **サイズ**: ~100語を目標
- **読み込み**: 常時

### レベル2: SKILL.md本文（トリガー時、<5k語）

```markdown
# Skill Name

## Purpose
[Brief description]

## Instructions
[Step-by-step procedures]

## Examples
[Usage scenarios]
```

- **目的**: 手順とワークフローのガイダンスを提供
- **内容**: 重要な指示、例、ベストプラクティス
- **サイズ**: <5k語を目標
- **読み込み**: スキルがトリガーされた時

### レベル3: バンドルリソース（必要時のみ）

```
skill-name/
├── SKILL.md
├── scripts/         # 決定論的な実行用
├── references/      # 詳細なドキュメント用
└── assets/          # 出力ファイル用
```

- **目的**: 必要に応じて追加情報を提供
- **内容**: スクリプト、リファレンス、テンプレート
- **サイズ**: 制限なし（スクリプトは実行のみ、コンテキストに読み込まれない）
- **読み込み**: 明示的に参照された時のみ

### Progressive Disclosureの利点

1. **効率的なコンテキスト管理**: 必要な情報のみを読み込む
2. **トークン節約**: 大規模なドキュメントをスキル本文から分離
3. **決定論的な実行**: スクリプトはコンテキストに読み込まれず、直接実行
4. **スケーラビリティ**: 詳細な仕様を無制限に追加可能

### 適用ガイドライン

**SKILL.mdに含めるべき内容:**
- スキルの目的（数文）
- ワークフローと手順
- 簡潔な例
- 重要なガイドライン

**references/に移動すべき内容:**
- 詳細なAPI仕様
- スキーマ定義
- 企業ポリシー
- 拡張例とチュートリアル

**scripts/に配置すべき内容:**
- 繰り返し再作成されるコード
- 決定論的な実行が必要な処理
- データ変換スクリプト
- バリデーター

**assets/に配置すべき内容:**
- ファイルテンプレート
- ボイラープレートコード
- ロゴや画像
- 設定ファイルのサンプル

---

## YAMLフロントマター仕様

公式仕様（Agent Skills Spec v1.0）と拡張フィールド：

### 必須フィールド

#### name

- **型**: 文字列
- **最大長**: 64文字
- **形式**: ハイフン区切りの小文字（ケバブケース）
- **例**: `skill-creator`、`code-reviewer`、`api-tester`
- **検証**: ユニークで、英数字とハイフンのみ
- **公式要件**: ディレクトリ名と一致する必要あり

#### description

- **型**: 文字列
- **最大長**: 200文字（推奨: ~100語）
- **目的**: Claudeがスキルを起動するタイミングを決定するのを支援
- **記述スタイル**: third-person（三人称）を使用
  - ❌ "Use this skill when..."
  - ✅ "This skill should be used when..."
- **必須内容**:
  - スキルが何をするか
  - いつ使用するか
  - トリガーキーワード
- **例**: "This skill creates new Claude Code skills with proper structure and best practices. Should be used for skill building, feature generation, and custom tool creation."

### 公式の任意フィールド

#### allowed-tools

- **型**: 配列
- **適用**: Claude Codeのみ
- **目的**: 事前承認されたツールのリストを指定
- **例**: `allowed-tools: [Read, Write, Edit, Bash]`
- **使用タイミング**: スキルが使用できるツールを制限したい場合

#### license

- **型**: 文字列
- **形式**: 簡潔なライセンス識別子
- **例**: `MIT`、`Apache-2.0`、`Proprietary`
- **推奨**: 簡潔に保つ

#### metadata

- **型**: オブジェクト（キー・バリューペア）
- **目的**: 実装固有のカスタムデータ
- **例**:
  ```yaml
  metadata:
    author: "Your Name"
    category: "development"
    tags: ["python", "testing"]
  ```

### 拡張任意フィールド（このリポジトリ）

#### version

- **型**: 文字列（セマンティックバージョニング）
- **形式**: `MAJOR.MINOR.PATCH`
- **例**: `1.0.0`、`2.1.3`
- **目的**: スキルの反復と変更を追跡

#### dependencies

- **型**: 文字列または配列
- **形式**: パッケージ仕様
- **例**:
  - 単一: `python>=3.8`
  - 複数: `python>=3.8, node>=18, docker`
- **目的**: 必要なソフトウェア/ツールを文書化

### YAML構文ルール

1. **区切り文字**: 別の行に`---`で開始と終了が必要
2. **スペーシング**: スペースのみ使用、タブは不可
3. **インデント**: レベルごとに2スペース
4. **引用符**: 特殊文字を含む値には引用符を使用
5. **リスト**: 配列項目にはスペース付き`-`プレフィックスを使用

### 有効なYAML例

```yaml
---
name: example-skill
description: これは適切なYAMLフォーマットと必須フィールドを示すサンプルスキルです。
version: 1.0.0
dependencies: python>=3.8
---
```

### 無効なYAML例

```yaml
# 終了区切り文字がない
---
name: example-skill
description: 終了区切り文字がありません

# タブの使用（ここでは見えませんがエラーの原因になります）
---
name:→example-skill
description:→不適切なフォーマット

# 名前が長すぎる
---
name: this-is-an-extremely-long-skill-name-that-exceeds-sixty-four-characters-limit
description: これは検証に失敗します
```

---

## ファイル構造パターン

### 公式推奨構造

#### 最小スキル（SKILL.mdのみ）

```
skill-name/
└── SKILL.md
```

**使用タイミング**:

- シンプルで直接的な機能
- 外部依存関係なし
- 最小限のドキュメントが必要
- 例がメインファイルに収まる

#### スクリプトベースのスキル

```
skill-name/
├── SKILL.md
└── scripts/
    ├── rotate_pdf.py
    ├── validate_schema.sh
    └── format_output.js
```

**使用タイミング**:

- 決定論的な実行が必要
- 同じコードが繰り返し再作成される
- トークン効率が重要
- コンテキストへの読み込みを避けたい

#### リファレンス重視のスキル

```
skill-name/
├── SKILL.md
└── references/
    ├── finance.md
    ├── api_docs.md
    └── policies.md
```

**使用タイミング**:

- 詳細な仕様が必要
- APIドキュメントを参照
- 企業ポリシーやスキーマを含む
- SKILL.mdが長くなりすぎる場合

#### アセット重視のスキル

```
skill-name/
├── SKILL.md
└── assets/
    ├── logo.png
    ├── template.pptx
    └── boilerplate/
        ├── index.html
        └── styles.css
```

**使用タイミング**:

- テンプレートファイルを生成
- ボイラープレートコードを提供
- ブランドリソース（ロゴなど）を使用
- プロジェクト初期化

#### 複合スキル（フルスタック）

```
skill-name/
├── SKILL.md
├── scripts/
│   ├── helper.py
│   └── validator.sh
├── references/
│   ├── api_docs.md
│   └── schema.md
└── assets/
    ├── template1.md
    └── config.yaml
```

**使用タイミング**:

- 複雑な複数ステップのプロセス
- 実行可能なスクリプトと詳細なドキュメントの両方が必要
- テンプレートとリファレンスを組み合わせる
- エンタープライズレベルのワークフロー

### このリポジトリの代替構造

#### 標準スキル（最も一般的）

```
skill-name/
├── SKILL.md
├── reference.md
└── examples.md
```

**使用タイミング**:

- 中程度の複雑さ
- 拡張例が必要
- 技術仕様が有益
- APIまたはフォーマットリファレンスが必要

#### 複雑なスキル（高度なワークフロー）

```
skill-name/
├── SKILL.md
├── reference.md
├── examples.md
├── templates/
│   ├── template1.md
│   └── template2.json
└── scripts/
    ├── helper.py
    └── validator.sh
```

**使用タイミング**:

- 複雑な複数ステップのプロセス
- テンプレートからファイルを生成
- ヘルパースクリプトが必要
- 複数の設定オプション
- ドメイン固有の知識

### 構造選択のガイドライン

**公式構造 vs このリポジトリ:**

| 要素 | 公式 | このリポジトリ | 推奨 |
|------|------|----------------|------|
| リファレンス | `references/` ディレクトリ | `reference.md` 単一ファイル | 大規模: `references/`、小規模: `reference.md` |
| テンプレート | `assets/` | `templates/` | どちらでも可（一貫性を保つ） |
| 例 | `references/` に含める | `examples.md` | どちらでも可 |
| スクリプト | `scripts/` | `scripts/` | `scripts/`（両方同じ） |

**選択基準:**

- **公式構造を使用**: 他の公式スキルとの互換性が重要な場合
- **このリポジトリの構造を使用**: シンプルさと単一ファイルの利便性を優先する場合
- **混合アプローチ**: プロジェクトのニーズに応じて柔軟に選択

---

## 記述スタイルガイド

公式のスキル作成ガイドに基づく記述スタイル：

### YAMLフロントマターの記述スタイル

#### description フィールド

**ルール**: third-person（三人称）で記述

**良い例:**

```yaml
description: >
  This skill creates new Claude Code skills with proper structure.
  Should be used for skill building and feature generation.
```

```yaml
description: >
  Analyzes code for bugs, performance issues, and best practices.
  Use for code review, quality checks, and pattern analysis.
```

**悪い例:**

```yaml
description: >
  Use this skill when you want to create a new skill.  # 二人称（"you"）を使用
```

```yaml
description: >
  I will help you build skills with best practices.  # 一人称（"I"）を使用
```

**修正方法:**

- "Use this skill when..." → "This skill should be used when..."
- "I will help..." → "This skill helps..."
- "You should use..." → "Should be used for..."

### SKILL.md本文の記述スタイル

#### 指示の記述

**ルール**: imperative/infinitive form（命令形/不定詞形）を使用

**良い例:**

```markdown
## Instructions

### Step 1: Analyze the request
To accomplish X, do Y.
Check the file permissions.
Verify the syntax is correct.

### Step 2: Generate output
Create the file structure.
Add the necessary files.
Validate the results.
```

**悪い例:**

```markdown
## Instructions

### Step 1: Analyze the request
You should analyze the request.  # 二人称を使用
You need to check the file permissions.
Claude will verify the syntax.

### Step 2: Generate output
You should create the file structure.
Then you add the necessary files.
```

**修正方法:**

- "You should check..." → "Check..."
- "Claude will verify..." → "Verify..."
- "You need to..." → "To accomplish X, do Y" または "Do X"

### 比較表

| コンテキスト | 悪い（避ける） | 良い（使用） |
|--------------|----------------|--------------|
| description | "Use this skill when..." | "This skill should be used when..." |
| description | "I will help you..." | "This skill helps..." |
| 指示 | "You should check..." | "Check..." |
| 指示 | "You need to verify..." | "Verify..." / "To verify X, do Y" |
| 指示 | "Claude will analyze..." | "Analyze..." |
| 目的 | "This skill will help you..." | "This skill helps..." |

### 記述のベストプラクティス

1. **簡潔さを保つ**
   - 冗長な表現を避ける
   - 直接的な指示を使用
   - 不要な修飾語を削除

2. **明確な動作動詞を使用**
   - ✅ Check, Verify, Create, Analyze, Generate
   - ❌ Should check, Need to verify, Will create

3. **手順を論理的に構造化**
   - 番号付きステップを使用
   - 階層的な構造を維持
   - 各ステップを明確に区別

4. **例を含める**
   - 実際の使用シナリオを示す
   - 期待される入力と出力を明示
   - エッジケースをカバー

---

## 説明の書き方ガイド

### 説明の目的

説明フィールドは2つの重要な機能を果たします：

1. Claudeがスキルを起動するタイミングを決定するのを支援
2. スキルの機能に関するコンテキストを提供

### 説明の公式

```
[何をするか] + [いつ使用するか] + [トリガーキーワード]
```

### 良い説明の例

```yaml
description: "バグ、パフォーマンス問題、ベストプラクティスについてコードをレビューします。コードレビュー、品質チェック、パターン分析時に使用します。キーワード: コードレビュー、コード確認、PRレビュー。"
```

**良い理由**:

- 明確な機能
- 具体的なユースケース
- 明示的なトリガーキーワード
- 200文字以下

```yaml
description: "コードコメントと型定義からAPIドキュメントを生成します。API文書化、リファレンス作成、ドキュメント更新時に使用します。キーワード: APIドキュメント、ドキュメント化、ドキュメント生成。"
```

**良い理由**:

- 正確なアクション
- アクティベーションのコンテキスト
- ユーザー言語のキーワード

### 悪い説明の例

```yaml
description: "コード用の便利なスキル"
```

**問題点**:

- 曖昧すぎる
- トリガーキーワードなし
- 使用タイミングが不明確
- 最小限のコンテキスト

```yaml
description: "この非常に包括的なスキルは、構文チェック、セマンティック分析、パフォーマンス最適化提案、セキュリティ脆弱性検出、ベストプラクティス適用を含むコードレビューのすべての側面を処理します。"
```

**問題点**:

- 長すぎる
- 過度に複雑
- 多くのことをやろうとしすぎ
- 複数のスキルに分割すべき

### トリガーキーワード戦略

**以下のタイプを含める**:

1. **動作動詞**: 作成、構築、生成、レビュー、分析、テスト
2. **ドメイン用語**: API、データベース、フロントエンド、バックエンド、DevOps
3. **ユーザーフレーズ**: "〜を手伝って"、"〜を作成"、"〜をレビュー"
4. **略語**: PR、CI/CD、API、DB

**キーワードリストの例**:

```yaml
# コードレビュースキル
キーワード: レビュー、チェック、分析、PR、プルリクエスト、コード品質

# データベースマイグレーションスキル
キーワード: マイグレート、マイグレーション、データベース、スキーマ、DB

# コンポーネント生成スキル
キーワード: コンポーネント、生成、作成、スキャフォールド、ボイラープレート
```

---

## 指示の書き方ベストプラクティス

### 指示を構造化する

階層構造を使用します：

```markdown
## 指示

### フェーズ1: 準備
#### ステップ1.1: リクエストを分析
- サブステップの詳細
- 確認すべきこと
- 検証方法

#### ステップ1.2: リソースを収集
- どのようなリソース
- どこで見つけるか
- 検証方法

### フェーズ2: 実行
[パターンを続ける...]
```

### 具体的で実行可能にする

**悪い**:

```markdown
## 指示
コードをレビューしてフィードバックを提供します。
```

**良い**:

```markdown
## 指示

### ステップ1: コード分析
1. Readツールを使用してファイル全体を読む
2. 主要言語とフレームワークを特定
3. 以下を確認:
   - 構文エラー
   - 未使用の変数
   - 潜在的なヌルポインタ例外
   - パフォーマンスのアンチパターン

### ステップ2: フィードバックを生成
1. 以下を含む構造化されたレポートを作成:
   - 重大な問題（修正必須）
   - 警告（修正すべき）
   - 提案（あると良い）
2. 各問題について以下を提供:
   - 行番号
   - 問題の説明
   - 修正の提案
   - コード例
```

### 条件ロジックを使用

```markdown
### ステップ3: 言語固有のチェック

**Pythonの場合**:
- PEP 8準拠を確認
- 型ヒントを検証
- 一般的な落とし穴を確認（可変デフォルトなど）

**JavaScript/TypeScriptの場合**:
- ESLintルールを確認
- async/await使用を検証
- プロミス処理を確認

**Goの場合**:
- gofmt準拠を確認
- エラー処理を検証
- ゴルーチンリークを確認
```

### エッジケースを含める

```markdown
### エラー処理

**ファイルが空の場合**:
- ユーザーに警告
- テンプレートコンテンツを作成するか尋ねる
- オプションを提供

**ファイルが大きすぎる場合**（10,000行以上）:
- レビューするセクションを指定するよう依頼
- チャンクでレビューすることを提案
- 自動化ツールを提案

**言語が認識できない場合**:
- 言語を指定するよう依頼
- 一般的なレビューを試みる
- 構造パターンに焦点を当てる
```

---

## バンドルリソースの使用

公式のスキル構造に基づくバンドルリソースの詳細ガイド：

### scripts/ ディレクトリ

#### 目的と利点

**主な目的:**
- 決定論的な実行を保証
- トークン効率を向上
- 同じコードの繰り返し再作成を避ける

**利点:**
1. **コンテキストに読み込まれない**: スクリプトは実行されるだけで、Claudeのコンテキストウィンドウを消費しない
2. **決定論的な信頼性**: コードが毎回同じように実行される
3. **トークン節約**: 大きなコードブロックをコンテキストから除外

#### 使用タイミング

以下の場合にscripts/を使用：

- **繰り返しパターン**: 同じコードが複数回再作成される
- **複雑なロジック**: 手動で記述するには複雑すぎる処理
- **データ変換**: PDFの回転、画像処理、データフォーマット変換
- **バリデーション**: スキーマ検証、構文チェック

#### 例

```python
# scripts/rotate_pdf.py
import PyPDF2
import sys

def rotate_pdf(input_path, output_path, degrees):
    """Rotate PDF pages by specified degrees"""
    with open(input_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        for page in pdf_reader.pages:
            page.rotate(degrees)
            pdf_writer.add_page(page)

        with open(output_path, 'wb') as output:
            pdf_writer.write(output)

if __name__ == "__main__":
    rotate_pdf(sys.argv[1], sys.argv[2], int(sys.argv[3]))
```

**SKILL.mdでの参照:**

```markdown
### Step 2: Rotate PDF

Execute the rotation script:

\`\`\`bash
python scripts/rotate_pdf.py input.pdf output.pdf 90
\`\`\`
```

### references/ ディレクトリ

#### 目的と利点

**主な目的:**
- 詳細なドキュメントを必要時のみ読み込む
- SKILL.mdを簡潔に保つ
- 専門知識を文書化

**利点:**
1. **Progressive Disclosure**: 必要な時にのみ読み込まれる
2. **無制限の詳細**: サイズ制限なし
3. **モジュール化**: トピックごとに分割可能

#### 使用タイミング

以下の場合にreferences/を使用：

- **API仕様**: 詳細なAPIドキュメント
- **スキーマ定義**: データベーススキーマ、JSONスキーマ
- **企業ポリシー**: コンプライアンスルール、ブランドガイドライン
- **技術リファレンス**: 詳細な技術仕様

#### 例

```markdown
<!-- references/api_docs.md -->
# BigQuery API Documentation

## Authentication

Use service account credentials...

## Common Queries

### Query 1: Get user data
\`\`\`sql
SELECT * FROM users WHERE created_at > TIMESTAMP('2025-01-01')
\`\`\`

### Query 2: Aggregate metrics
\`\`\`sql
SELECT
  DATE(timestamp) as date,
  COUNT(*) as events
FROM events
GROUP BY date
ORDER BY date DESC
\`\`\`

## Error Handling

- Error 403: Check IAM permissions...
- Error 404: Verify dataset exists...
```

**SKILL.mdでの参照:**

```markdown
### Step 3: Execute Query

Refer to `references/api_docs.md` for query examples and best practices.

Use Read tool to access specific query patterns from the reference.
```

### assets/ ディレクトリ

#### 目的と利点

**主な目的:**
- そのまま使用できる出力ファイルを提供
- ブランドリソースを含める
- ボイラープレートコードを格納

**利点:**
1. **即座に使用可能**: 変更なしで使用できるファイル
2. **コンテキスト節約**: コンテキストに読み込まれない
3. **一貫性**: テンプレートやブランドの一貫性を保証

#### 使用タイミング

以下の場合にassets/を使用：

- **テンプレートファイル**: PPTX、DOCX、PDFテンプレート
- **ボイラープレート**: プロジェクト初期化コード
- **ブランドリソース**: ロゴ、フォント、カラーパレット
- **設定ファイル**: サンプル設定、.envテンプレート

#### 例

```
assets/
├── logo.png                    # 企業ロゴ
├── presentation-template.pptx  # プレゼンテーションテンプレート
├── boilerplate/
│   ├── index.html             # HTMLボイラープレート
│   ├── styles.css             # CSSテンプレート
│   └── app.js                 # JavaScriptスターター
└── config/
    ├── .env.example           # 環境変数テンプレート
    └── eslint.config.js       # ESLint設定サンプル
```

**SKILL.mdでの参照:**

```markdown
### Step 4: Initialize Project

Copy boilerplate files from assets:

\`\`\`bash
cp -r assets/boilerplate/* ./project/
cp assets/config/.env.example ./project/.env
\`\`\`

Customize the files according to project requirements.
```

### バンドルリソースのベストプラクティス

1. **重複を避ける**
   - 情報はSKILL.mdまたはreferencesのいずれかに配置
   - 同じ内容を複数の場所に記載しない

2. **明確な命名規則**
   - ファイル名は目的を明確に示す
   - 階層的なディレクトリ構造を使用

3. **適切な分割**
   - references/: トピックごとに分割（api_docs.md、schema.md、policies.md）
   - assets/: タイプごとに分割（templates/、logos/、configs/）

4. **ドキュメント化**
   - SKILL.mdでバンドルリソースの使用方法を説明
   - 各リソースの目的を明確に記述

5. **Progressive Disclosureを意識**
   - SKILL.mdは簡潔に（<5k語）
   - 詳細はreferences/へ
   - 実行可能コードはscripts/へ
   - 出力ファイルはassets/へ

---

## ツール使用ガイドライン

### タスク別の推奨ツール

| タスク | 推奨ツール | 避けるべき |
|------|---------------|-------|
| ファイル読み取り | `Read` | `cat`、`head`、`tail` |
| コンテンツ検索 | `Grep` | `grep`、`rg` |
| ファイル検索 | `Glob` | `find`、`ls` |
| ファイル編集 | `Edit` | `sed`、`awk` |
| ファイル作成 | `Write` | `echo >`、`cat > EOF` |
| コマンド実行 | `Bash` | （適切な使用） |
| Webリクエスト | `WebFetch` | `curl`、`wget` |

### スキルでのツール使用

**ツールを明示的に指定**:

```markdown
## 指示

### ステップ1: 設定ファイルを見つける
**Glob**ツールを使用して設定ファイルを検索:
- パターン: `**/*.config.js`
- プロジェクトルートで検索
- 一般的な場所を確認

### ステップ2: 設定を読む
**Read**ツールを使用して各設定を調べる:
- ファイル全体を読む
- JSON/YAML構造を解析
- 関連する設定を抽出
```

**特定のツールを使用する理由を説明**:

```markdown
### ツール選択

以下の場合に**Grep**を使用:
- 多くのファイルを検索する
- パターンマッチングが必要
- 出現箇所を見つけるだけで良い

以下の場合に**Read**を使用:
- 完全なコンテキストが必要
- 構造を分析する
- 関係を理解する
```

---

## テストと検証

### 作成前の検証チェックリスト

スキルを作成する前に、以下を確認：

- [ ] スキル名がユニークで説明的
- [ ] 名前がケバブケース規則に従っている
- [ ] 名前が64文字以下
- [ ] 説明が明確で具体的
- [ ] 説明にトリガーキーワードが含まれている
- [ ] 説明が200文字以下
- [ ] スキルが単一の焦点を絞った目的を持つ
- [ ] 指示が実行可能
- [ ] 例が現実的
- [ ] すべてのパスでフォワードスラッシュを使用
- [ ] YAML構文が有効
- [ ] YAMLにタブがない（スペースのみ）

### 作成後のテスト

**1. YAML検証**

```bash
# YAMLリンターを使用
yamllint SKILL.md

# またはPython
python -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
```

**2. インストールテスト**

```bash
# 個人用スキルディレクトリにコピー
cp -r skill-name ~/.claude/skills/

# ファイル構造を確認
ls -la ~/.claude/skills/skill-name/
```

**3. アクティベーションテスト**

スキルをトリガーすべきリクエストを試す：

- 正確なトリガーキーワードを使用
- 自然言語のバリエーションを使用
- エッジケースをテスト

**4. 機能テスト**

スキルが以下を行うことを確認：

- 期待される出力を生成
- エラーを適切に処理
- 様々な入力で動作
- 正常に完了

### 検証スクリプトテンプレート

```bash
#!/bin/bash
# validate-skill.sh

SKILL_DIR=$1

echo "スキルを検証中: $SKILL_DIR"

# 必須ファイルを確認
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "エラー: SKILL.mdが見つかりません"
    exit 1
fi

# YAML構文を確認
python3 -c "
import yaml
import sys

with open('$SKILL_DIR/SKILL.md') as f:
    content = f.read()
    parts = content.split('---')
    if len(parts) < 3:
        print('エラー: 無効なYAMLフロントマター形式')
        sys.exit(1)
    try:
        yaml.safe_load(parts[1])
        print('✓ YAML構文が有効')
    except Exception as e:
        print(f'エラー: YAMLパースに失敗: {e}')
        sys.exit(1)
"

# 必須フィールドを確認
python3 -c "
import yaml

with open('$SKILL_DIR/SKILL.md') as f:
    content = f.read()
    frontmatter = yaml.safe_load(content.split('---')[1])

    if 'name' not in frontmatter:
        print('エラー: 必須フィールドが不足: name')
        exit(1)

    if 'description' not in frontmatter:
        print('エラー: 必須フィールドが不足: description')
        exit(1)

    if len(frontmatter['name']) > 64:
        print('エラー: 名前が64文字を超えています')
        exit(1)

    if len(frontmatter['description']) > 200:
        print('エラー: 説明が200文字を超えています')
        exit(1)

    print('✓ 必須フィールドが存在し、有効です')
"

echo "✓ 検証完了"
```

---

## よくある落とし穴

### 1. 過度に広範なスキル

**問題**: スキルが多くのことをやろうとしすぎ

**例**:

```yaml
name: web-development
description: フロントエンド、バックエンド、データベース、DevOps、テスト、デプロイを含むすべてのWeb開発タスクを処理
```

**解決策**: 焦点を絞ったスキルに分割

```yaml
# より良いアプローチ
name: frontend-component-generator
description: テスト付きReact/Vueコンポーネントを生成します。UIコンポーネント作成時に使用します。

name: api-endpoint-creator
description: 検証付きREST APIエンドポイントを作成します。API構築時に使用します。
```

### 2. 曖昧な説明

**問題**: 説明がCl audeが起動タイミングを知るのに役立たない

**例**:

```yaml
description: 開発者のための便利なスキル
```

**解決策**: 具体的にする

```yaml
description: コード品質、ベストプラクティス、潜在的なバグについてプルリクエストをレビューします。PRレビュー、コードレビュー、品質チェックに使用します。キーワード: PRレビュー、コード確認。
```

### 3. 不適切なYAMLフォーマット

**問題**: スペースの代わりにタブ、区切り文字の欠落

**例**:

```yaml
# タブを使用している（見えませんがエラーの原因になります）
---
name: skill-name
  description: 不適切なフォーマット
```

**解決策**: スペースを使用し、適切な構造にする

```yaml
---
name: skill-name
description: スペースを使った適切なフォーマット
---
```

### 4. プラットフォーム固有のパス

**問題**: バックスラッシュやプラットフォーム固有のパスを使用

**例**:

```markdown
以下のファイルを確認: C:\Users\Project\src\
```

**解決策**: フォワードスラッシュを使用

```markdown
以下のファイルを確認: /project/src/
相対パスを使用: ./src/
```

### 5. 不明確な指示

**問題**: 指示が高レベルすぎる

**例**:

```markdown
## 指示
コードを分析してより良くします。
```

**解決策**: 具体的なステップを提供

```markdown
## 指示

### ステップ1: コード構造を分析
1. Readツールを使用してファイルを読む
2. 言語とフレームワークを特定
3. 関数/クラス構造をマッピング
4. 依存関係に注目

### ステップ2: 問題を確認
1. 構文エラー
2. 未使用の変数
3. 潜在的なバグ
4. パフォーマンス問題

### ステップ3: レポートを生成
1. 重要度別に問題をリスト
2. 行番号を提供
3. 具体的な修正を提案
4. コード例を含める
```

### 6. 例の欠落

**問題**: 具体的な使用例がない

**解決策**: 常に現実的な例を含める

```markdown
## 例

### 例1: 基本的なコードレビュー

**ユーザーリクエスト**: "このPythonファイルをレビューしてください"

**期待されるプロセス**:
1. ファイルを読む
2. PEP 8準拠を確認
3. 一般的なPythonの落とし穴を探す
4. 構造化されたフィードバックを生成

**期待される出力**:
```

file.pyのコードレビュー:

重大:

- 行23: ゼロ除算の可能性
- 行45: SQLインジェクション脆弱性

警告:

- 行12: 未使用のインポート 'sys'
- 行34: 変数名がPEP 8に従っていない

提案:

- 型ヒントの使用を検討
- 関数にdocstringを追加

```
```

---

## 高度なパターン

### 複数ステージスキル

明確なフェーズを持つ複雑なワークフロー用：

```markdown
## 指示

### ステージ1: 発見
[発見ステップ]

**チェックポイント**: 続行前に以下を確認:
- [ ] すべてのファイルが見つかった
- [ ] 依存関係が特定された
- [ ] 設定が有効

### ステージ2: 分析
[分析ステップ]

**チェックポイント**: 分析を検証:
- [ ] データが正しく構造化されている
- [ ] エッジケースが特定された
- [ ] 要件が明確

### ステージ3: 実行
[実行ステップ]

**最終検証**:
- [ ] 出力が要件を満たす
- [ ] エラーが発生していない
- [ ] ユーザー確認を受けた
```

### 条件付きスキル

コンテキストに基づいて分岐するスキル：

```markdown
## 指示

### ステップ1: コンテキストを検出

**Gitリポジトリ内の場合**:
- git statusを確認
- 現在のブランチを特定
- Git対応ワークフローに従う

**Gitリポジトリでない場合**:
- ファイルシステム操作を使用
- スタンドアロンワークフローに従う

### ステップ2: 言語に基づいて処理

Grepを使用して言語を検出し、その後:

**コンパイル言語**（Java、C++、Rust）の場合:
1. ビルドファイルを確認
2. コンパイルチェックを実行
3. 型チェックを実行

**インタープリタ言語**（Python、JavaScript）の場合:
1. 構文の有効性を確認
2. リンターを実行
3. テストを実行

**マークアップ言語**（HTML、Markdown）の場合:
1. 構造を検証
2. リンクを確認
3. フォーマットを検証
```

### 反復スキル

ループで動作するスキル：

```markdown
## 指示

### 反復処理

対象ディレクトリの各ファイルについて:

1. **読み取る** ファイルを
2. **分析する** 基準に従って
3. **収集する** 結果を
4. **続ける** 次のファイルへ

すべてのファイルが処理された後:

1. **集約する** 結果を
2. **ソートする** 優先度で
3. **生成する** サマリーレポート
4. **提示する** ユーザーに

### ループ制御

- 最大反復: 100ファイル
- スキップ条件: ファイルサイズ > 1MB
- 中断条件: 重大なエラーが見つかった
- 継続条件: ファイルタイプがサポートされていない
```

### メタスキル

他のスキルと連携するスキル：

```markdown
## 指示

### スキル調整

このメタスキルは複数の専門スキルを調整します:

1. **特定する** どのスキルが必要か
2. **順序付ける** スキル実行順序
3. **渡す** スキル間でコンテキストを
4. **集約する** 結果を
5. **提示する** 統一された出力を

### ワークフロー例

"コードベースを分析して改善"の場合:

1. `code-analyzer`スキルをアクティベート
2. 分析結果を収集
3. 分析を使って`code-improver`スキルをアクティベート
4. `code-tester`スキルで改善を検証
5. 最終レポートを生成

### スキル間通信

- 一貫したデータ形式を使用
- 期待される入力/出力を文書化
- スキルの失敗を適切に処理
- 必要に応じてロールバックを提供
```

---

## スキル命名規則

### 推奨パターン

| パターン | 例 | ユースケース |
|---------|---------|----------|
| `[action]-[target]` | `review-code`、`test-api` | アクション重視のスキル |
| `[domain]-[role]` | `frontend-developer`、`devops-engineer` | ロールベースのスキル |
| `[tool]-[integration]` | `docker-compose`、`git-workflow` | ツール固有のスキル |
| `[format]-[converter]` | `json-to-yaml`、`markdown-to-pdf` | 変換スキル |

### 避けるべき名前

- 一般的すぎる: `helper`、`utils`、`tools`
- 長すぎる: `comprehensive-full-stack-development-assistant`
- 数字付き: `skill-v2`、`helper-2024`
- 特殊文字付き: `skill_name`、`skill.helper`

---

## バージョン管理

### セマンティックバージョニングガイドライン

**メジャーバージョン**（1.0.0 → 2.0.0）:

- 指示フローへの破壊的変更
- 期待される入力/出力への互換性のない変更
- 機能の削除

**マイナーバージョン**（1.0.0 → 1.1.0）:

- 新機能の追加
- 新しい任意ステップ
- 機能の拡張

**パッチバージョン**（1.0.0 → 1.0.1）:

- バグ修正
- ドキュメント更新
- 小さな改善

### 変更履歴形式

```markdown
## バージョン管理

### バージョン1.2.1（2025-10-21）
- 修正: 複数行説明のYAMLパースエラー
- 更新: 最新のAPIパターンを使った例
- 改善: 不足している依存関係のエラーメッセージ

### バージョン1.2.0（2025-10-15）
- 追加: TypeScriptプロジェクトサポート
- 追加: ESLint統合
- 拡張: 大規模コードベースのパフォーマンス

### バージョン1.1.0（2025-10-01）
- 追加: Python型ヒントチェック
- 改善: エラーレポート形式

### バージョン1.0.0（2025-09-15）
- 初回リリース
- コアコードレビュー機能
```

---

このリファレンスドキュメントは、堅牢で適切に構造化されたClaude Codeスキルを作成するための包括的な技術詳細を提供します。ステップバイステップの作成プロセスについてはSKILL.mdを、すぐに使えるスタートポイントについてはtemplatesを参照してください。
