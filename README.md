# Claude Code スキルリポジトリ

[![CI](https://github.com/y-nishizaki/skills/workflows/CI/badge.svg)](https://github.com/y-nishizaki/skills/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Claude Code](https://claude.com/claude-code) の能力を拡張する、再利用可能なスキルのキュレーションされたコレクションです。専門的な知識とワークフローを提供します。

**[スキルカタログを見る](https://y-nishizaki.github.io/skills/)** - すべてのスキルを一覧で確認

## Claude Code スキルとは？

スキルは Claude Code の機能を拡張するモジュール式の機能です。各スキルは、ドメインの専門知識を発見可能な機能にパッケージ化し、Claude がリクエストに関連する場合に自律的に呼び出すことができます。

**主な特徴:**

- **モデルによる呼び出し**: Claude がコンテキストに基づいてスキルを使用するタイミングを自動的に判断
- **モジュール式**: 各スキルは特定の機能またはワークフローに焦点を当てる
- **共有可能**: git やプラグインを通じてチーム全体で簡単に配布
- **設定可能**: ツール制限により、機密性の高いコンテキストでの安全な実行を保証

## リポジトリの構造

```
skills/
├── README.md
├── LICENSE
├── src/                   # スキルのソースコード
│   ├── development-tools/     # 開発ツール・メタ
│   │   ├── skill-creator/
│   │   ├── subagent-creator/
│   │   └── generic-subagent/
│   ├── code-quality/          # コード品質
│   │   ├── code-review/
│   │   ├── refactoring/
│   │   ├── debugging/
│   │   ├── error-handling/
│   │   ├── security-audit/
│   │   └── performance-optimization/
│   ├── design/                # 設計
│   │   ├── system-design/
│   │   ├── api-design/
│   │   └── database-design/
│   ├── devops/                # 開発運用
│   │   ├── ci-cd-setup/
│   │   ├── dependency-management/
│   │   └── migration-assistant/
│   ├── testing/               # テスト
│   │   └── test-automation/
│   ├── code-generation/       # コード生成
│   │   └── code-creation/
│   ├── analysis/              # 分析・調査
│   │   ├── data-analysis/
│   │   ├── research/
│   │   └── documentation/
│   └── shared/                # 共通
│       └── shared-practices/
├── docs/                  # ドキュメント
└── tests/                 # テスト

各スキルの構造:
[スキル名]/
├── SKILL.md          # 必須: スキルの定義と手順
├── reference.md      # オプション: リファレンスドキュメント
├── examples.md       # オプション: 使用例
├── scripts/          # オプション: ヘルパースクリプト
└── templates/        # オプション: ファイルテンプレート
```

## クイックスタート

### 前提条件

- [Claude Code](https://claude.com/claude-code) がインストールされていること
- YAML と Markdown の基本的な理解

### スキルのインストール

#### 個人用

個人のスキルディレクトリにスキルをクローンします:

```bash
# リポジトリをクローン
git clone https://github.com/y-nishizaki/skills.git
cd skills

# 個別のスキルをコピー
cp -r src/[カテゴリ]/[スキル名] ~/.claude/skills/

# 例: スキル作成ツールをインストール
cp -r src/development-tools/skill-creator ~/.claude/skills/
```

#### チーム/プロジェクト用

プロジェクトに直接スキルを追加します:

```bash
# プロジェクトディレクトリで
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/y-nishizaki/skills.git
# 必要なスキルを .claude/skills/ にコピー
cp -r skills/src/[カテゴリ]/[スキル名] .
```

`.claude/skills/` ディレクトリをリポジトリにコミットします。チームメンバーは変更をプルした後、自動的にアクセスできるようになります。

## 開発者向けセットアップ

### pre-commit フックのセットアップ

このリポジトリでは、コードの品質を保つために pre-commit フックを使用しています。
コミット前に自動的に以下のチェックが実行されます：

- 末尾の空白の削除
- ファイル末尾の改行の修正
- YAML 構文チェック
- Markdown Lint
- YAML Lint
- スキル構造の検証

#### インストール方法

```bash
# pre-commit をインストール
pip install pre-commit

# pre-commit フックを有効化
pre-commit install

# (オプション) 既存のすべてのファイルでチェックを実行
pre-commit run --all-files
```

#### 使い方

pre-commit フックをインストール後は、`git commit` を実行するたびに自動的にチェックが実行されます。

```bash
# 通常通りコミット - 自動的にチェックが実行される
git add .
git commit -m "commit message"
```

チェックに失敗した場合、一部のファイルは自動的に修正されます。修正されたファイルを再度 add してコミットしてください：

```bash
git add .
git commit -m "commit message"
```

#### トラブルシューティング

**特定のチェックをスキップする場合：**

```bash
# すべてのフックをスキップ（推奨しません）
git commit --no-verify

# 特定のフックのみ実行
SKIP=markdownlint-cli2 git commit -m "message"
```

**pre-commit を更新する場合：**

```bash
pre-commit autoupdate
```

## 独自のスキルを作成する

### 基本的なスキル構造

すべてのスキルには、YAML フロントマターを含む `SKILL.md` ファイルが必要です:

```yaml
---
name: スキル名
description: Claude がこのスキルをいつ使用すべきかを知るのに役立つトリガー用語を含む簡潔な説明
---

# スキル名

## 目的
このスキルが何をするか、いつ使用すべきかを説明します。

## 手順
Claude が従うべきステップバイステップの手順。

## 例
具体的な使用シナリオ。
```

### ベストプラクティス

**1. 具体的な説明を書く**

- ユーザーが言及する可能性のあるトリガー用語を含める
- スキルがいつアクティブになるべきかを明示的に示す
- 曖昧または過度に広範な説明を避ける

**2. スキルを焦点を絞ったものにする**

- 1つのスキル = 1つの機能
- 複雑なワークフローを複数の補完的なスキルに分割

**3. 適切な場合はツール制限を使用する**

```yaml
---
name: コードレビュアー
description: ベストプラクティスと潜在的な問題についてコードをレビューする
allowed-tools: Read, Grep, Glob
---
```

**4. 明確な例を提供する**

- 現実的な使用シナリオを示す
- 入力と期待される動作の両方を含める
- エッジケースを文書化する

**5. パスにはフォワードスラッシュを使用する**

- クロスプラットフォームの互換性を保証
- Windows でも常に `/` を使用

**6. 段階的なドキュメント**

- SKILL.md に必須情報から始める
- 詳細なリファレンスは別ファイルに移動
- Claude は必要に応じて追加のコンテキストを読み込む

### スキルのテスト

1. **ローカルテスト**: スキルを `~/.claude/skills/` に配置し、Claude Code でテスト
2. **説明の検証**: Claude が自然なリクエストでスキルをアクティブにすることを確認
3. **チームの検証**: プロジェクトにコミットする前に同僚にテストしてもらう
4. **YAML の検証**: YAML リンターで構文をチェック

## コントリビューション

コントリビューションを歓迎します！以下のガイドラインに従ってください:

1. **リポジトリをフォーク**
2. **フィーチャーブランチを作成**: `git checkout -b feature/amazing-skill`
3. **上記のスキル構造に従う**
4. **Claude Code で徹底的にテスト**
5. **SKILL.md で明確に文書化**
6. **プルリクエストを送信**（以下を含む）:
   - スキルの目的の明確な説明
   - 使用例
   - 依存関係または要件

### コントリビューションチェックリスト

- [ ] SKILL.md に完全なフロントマター（name、description）が含まれている
- [ ] 説明に具体的なトリガー用語が含まれている
- [ ] 手順が明確で実行可能である
- [ ] 例が現実的な使用法を示している
- [ ] すべてのファイルパスでフォワードスラッシュを使用している
- [ ] Claude Code でローカルテストを実施した
- [ ] ファイルに機密情報が含まれていない
- [ ] ライセンスに互換性がある（MIT）

## 利用可能なスキル

スキルはカテゴリごとに整理されています。各カテゴリのREADME.mdで詳細を確認できます。

### 開発ツール (development-tools/)

Claude Code自体を拡張するためのメタツール。

- **skill-creator** - 新しいスキルを作成するためのガイドとツール
- **subagent-creator** - サブエージェント作成ツール
- **generic-subagent** - 汎用サブエージェント実装

### コード品質 (code-quality/)

コードの品質を多角的に向上。

- **code-review** - コードレビューの思考プロセス
- **refactoring** - リファクタリングの計画と実行
- **debugging** - デバッグの体系的アプローチ
- **error-handling** - エラーハンドリング設計
- **security-audit** - セキュリティ監査
- **performance-optimization** - パフォーマンス最適化

### 設計 (design/)

システム、API、データベースの設計。

- **system-design** - システムアーキテクチャ設計
- **api-design** - REST API、GraphQL設計
- **database-design** - データベーススキーマ設計

### DevOps (devops/)

開発運用の自動化とベストプラクティス。

- **ci-cd-setup** - CI/CDパイプライン構築
- **dependency-management** - 依存関係管理
- **migration-assistant** - システム・データ移行支援

### テスト (testing/)

自動テストの戦略と実装。

- **test-automation** - テスト自動化

### コード生成 (code-generation/)

高品質なコードの生成。

- **code-creation** - 新規コード作成

### ドキュメント処理 (document-processing/)

ビジネスドキュメントの作成、編集、分析。

- **word-documents** - Word文書の作成・編集・分析
- **pdf-documents** - PDFの作成・編集・抽出
- **presentations** - PowerPointプレゼンテーションの作成・編集
- **spreadsheets** - Excelスプレッドシートの作成・編集・分析

### 分析・調査 (analysis/)

データ分析、リサーチ、ドキュメント作成。

- **data-analysis** - データ分析とEDA
- **research** - 技術調査とリサーチ
- **documentation** - ドキュメント作成

### 共通 (shared/)

プロジェクト全体で共有されるベストプラクティス。

- **shared-practices** - 共通パターンと標準手順

---

### 使用例: Skill Creator

**場所**: `src/development-tools/skill-creator/`

最も基本的なスキルとして、新しいスキルの作成を支援します。

**インストール**:

```bash
cp -r src/development-tools/skill-creator ~/.claude/skills/
```

**使用方法**:

Claudeに「新しいスキルを作成」または「[目的]のためのスキルを作って」と依頼してください

## よくある問題のデバッグ

### Claude がスキルを使用しない

- **説明の具体性を確認**: より明確なトリガー用語を追加
- **ファイルの場所を確認**: スキルが `~/.claude/skills/` または `.claude/skills/` にあることを確認
- **アクティベーションをテスト**: トリガー用語に一致する明示的なリクエストを試す

### YAML 解析エラー

- 開始と終了の `---` マーカーを確認
- タブがないか確認（スペースのみを使用）
- インデントを検証
- YAML リンターを使用

### 他のスキルとの競合

- 説明で異なるトリガー用語を使用
- スキルがアクティブになるタイミングのスコープを絞る
- 重複するスキルの統合を検討

## リソース

- [Claude Code スキル公式ドキュメント](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Claude Code ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [GitHub Issues](https://github.com/y-nishizaki/skills/issues) - バグ報告や機能リクエスト

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 謝辞

- Anthropic の [Claude Code](https://claude.com/claude-code) 向けに構築
- Claude Code コミュニティとベストプラクティスに触発されて作成

---

**注意**: これは非公式のコミュニティリポジトリです。公式の Claude Code ドキュメントとサポートについては、[docs.claude.com](https://docs.claude.com) を参照してください。
