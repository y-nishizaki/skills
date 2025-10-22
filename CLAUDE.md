# Claude Code スキルリポジトリ - Claude 用ガイド

## リポジトリの目的

このリポジトリは、[Claude Code](https://claude.com/claude-code) の機能を拡張する再利用可能なスキルのコレクションです。

## スキルの作成

新しいスキルを作成する場合は、**skill-creator スキル**を使用してください。
詳細な手順とベストプラクティスは [skill-creator/SKILL.md](development-tools/skill-creator/SKILL.md) を参照してください。

## 技術要件

このリポジトリには以下の品質チェックがあります：

- **Markdown Lint**: `.markdownlint.json`
- **YAML Lint**: `.yamllint.yml`
- **ファイル構造の検証**: CI/CD パイプライン

すべての変更はこれらのチェックをパスする必要があります。

## 参照ドキュメント

- [README.md](README.md) - リポジトリの概要とクイックスタート
- [CONTRIBUTING.md](CONTRIBUTING.md) - コントリビューションガイドライン
- [skill-creator/SKILL.md](development-tools/skill-creator/SKILL.md) - スキル作成の詳細ガイド
