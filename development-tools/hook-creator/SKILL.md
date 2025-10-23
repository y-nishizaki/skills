---
name: hook-creator
description: Claude Codeのフック（hooks）を作成・設定するためのガイド。ユーザーがClaude Codeのライフサイクルイベント（ツール実行前後、プロンプト送信時、セッション開始/終了時など）に応じて自動実行されるシェルコマンドを設定したい場合に使用される。自動フォーマット、通知、ログ記録、ファイル保護などのユースケースに対応。
license: 完全な条項はLICENSE.txtを参照
---

# フック作成ツール（Hook Creator）

このスキルは、Claude Codeのフック機能を活用して、自動化されたワークフローを実装するためのガイダンスを提供します。

## フックについて

フックは、Claude Codeのライフサイクルの特定のポイントで自動実行されるユーザー定義のシェルコマンドです。LLMの判断に依存せず、確実に特定のアクションを実行できるため、以下のような用途に最適です：

- **自動フォーマット**: ファイル編集後に自動的にprettier、gofmt、black等を実行
- **デスクトップ通知**: Claude Codeが入力待機時に通知を送信
- **ログ記録**: コンプライアンスやデバッグのためにコマンドを追跡
- **コード品質チェック**: コード規約に合わないコードに対して自動的にフィードバック
- **権限制御**: 本番ファイルや機密ディレクトリの変更をブロック

### フックが提供する価値

1. **確実性**: LLMの判断に依存せず、指定したイベントで必ず実行される
2. **自動化**: 手動での確認や実行が不要
3. **柔軟性**: 任意のシェルコマンドを実行可能
4. **イベント駆動**: 9つの異なるライフサイクルイベントに対応

## フックの設定方法

フックは設定ファイル（`~/.claude/settings.json` または `.claude/settings.json`）で定義します。

### 基本構造

```json
{
  "hooks": [
    {
      "matcher": "ツールパターン",
      "hooks": [
        {
          "hookEventName": "イベント名",
          "command": "実行するシェルコマンド",
          "timeout": 60
        }
      ]
    }
  ]
}
```

### 設定例：TypeScript自動フォーマット

```json
{
  "hooks": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.tsx?$\"))' | xargs -r npx prettier --write",
          "timeout": 30
        }
      ]
    }
  ]
}
```

## フック作成プロセス

### ステップ1: ユースケースを明確にする

まず、実現したい自動化の目的を明確にします。以下の質問に答えてください：

1. **何を自動化したいか？**
   - 例：「TypeScriptファイルを保存したら自動的にフォーマットしたい」

2. **どのタイミングで実行すべきか？**
   - 例：「ファイル編集後」→ PostToolUse イベント

3. **どのツール/ファイルが対象か？**
   - 例：「Editツール」「.ts/.tsxファイル」

4. **実行すべきコマンドは何か？**
   - 例：「prettier --write」

### ステップ2: 適切なフックイベントを選択する

ユースケースに応じて、以下のイベントから選択します：

| イベント | タイミング | 主なユースケース |
|---------|-----------|----------------|
| **PreToolUse** | ツール実行前 | 権限チェック、パラメータ検証 |
| **PostToolUse** | ツール実行後 | 自動フォーマット、ログ記録 |
| **UserPromptSubmit** | プロンプト送信時 | コンテキスト追加、入力検証 |
| **Notification** | 通知時 | デスクトップ通知、Slack通知 |
| **SessionStart** | セッション開始時 | 環境初期化、ログ開始 |
| **SessionEnd** | セッション終了時 | クリーンアップ、ログ終了 |
| **Stop** | エージェント停止時 | 状態保存 |
| **SubagentStop** | サブエージェント停止時 | サブタスク完了処理 |
| **PreCompact** | 圧縮前 | 重要情報の保存 |

詳細は `references/hook-events.md` を参照してください。

### ステップ3: マッチャーパターンを定義する

マッチャーは、フックを適用するツールやファイルを指定します。

**ツールマッチャーの例：**
- `"Edit"` - Editツールのみ
- `"Read"` - Readツールのみ
- `"Write"` - Writeツールのみ
- `"*"` - すべてのツール
- `"Edit|Write"` - 正規表現でEditまたはWrite

**ファイルフィルタリング：**
コマンド内でjqやgrepを使用して、特定のファイルタイプのみを対象にします：

```bash
# TypeScriptファイルのみ
jq -r '.tool_input.file_path | select(test("\\.tsx?$"))'

# Pythonファイルのみ
jq -r '.tool_input.file_path | select(test("\\.py$"))'

# 特定ディレクトリを除外
jq -r '.tool_input.file_path | select(test("^(?!node_modules/)"))'
```

### ステップ4: コマンドを実装する

フックコマンドは標準入力からJSON形式のイベントデータを受け取ります。

**入力データの構造：**
```json
{
  "session_id": "セッションID",
  "transcript_path": "会話ログパス",
  "cwd": "作業ディレクトリ",
  "hook_event_name": "イベント名",
  "tool_name": "ツール名",
  "tool_input": {
    "file_path": "/path/to/file",
    ...
  }
}
```

**コマンド実装のベストプラクティス：**

1. **jqを使用してデータを抽出**
   ```bash
   jq -r '.tool_input.file_path'
   ```

2. **エラーハンドリング**
   - 終了コード0：成功
   - 終了コード2：ブロック（Claudeの処理を停止）
   - その他：非ブロックエラー

3. **タイムアウト設定**
   - デフォルト60秒
   - 長時間実行される場合は適切に設定

4. **セキュリティ**
   - 入力サニタイズを必ず実施
   - パスの検証を行う
   - 秘密情報を出力しない

### ステップ5: 設定をテストする

フックを本番使用する前に、必ずテストを実施します。

**テスト手順：**

1. **構文検証**
   ```bash
   # settings.jsonの構文チェック
   jq . ~/.claude/settings.json
   ```

2. **小規模テスト**
   - まず安全なファイルで試す
   - echoコマンドでデバッグ出力を確認

   ```json
   {
     "hookEventName": "PostToolUse",
     "command": "jq . >&2"
   }
   ```

3. **段階的なロールアウト**
   - 特定のツールのみから開始
   - 徐々に対象を拡大

4. **ログ確認**
   - フックの実行ログを確認
   - エラーメッセージをチェック

### ステップ6: リファレンスとテンプレートを活用する

一般的なユースケース向けのテンプレートが `assets/templates/` に用意されています：

- `auto-format.json` - 自動フォーマット設定
- `notification.json` - デスクトップ通知設定
- `logging.json` - ログ記録設定
- `file-protection.json` - ファイル保護設定
- `code-quality-check.json` - コード品質チェック設定

テンプレートをコピーして、プロジェクトに合わせてカスタマイズしてください。

## よくあるパターン

### パターン1: 自動フォーマット

ファイル保存時に自動的にコードフォーマッタを実行：

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "hookEventName": "PostToolUse",
      "command": "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'case {} in *.py) black {} ;; *.ts|*.tsx) npx prettier --write {} ;; *.go) gofmt -w {} ;; esac'"
    }
  ]
}
```

### パターン2: ファイル保護

本番ファイルへの変更をブロック：

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "hookEventName": "PreToolUse",
      "command": "jq -r '.tool_input.file_path | select(test(\"production/|.env\"))' | grep -q . && echo 'Error: Cannot modify production files' >&2 && exit 2 || exit 0"
    }
  ]
}
```

### パターン3: デスクトップ通知

Claude Codeが入力待機時に通知：

```json
{
  "matcher": "*",
  "hooks": [
    {
      "hookEventName": "Notification",
      "command": "osascript -e 'display notification \"Claude Code is waiting for input\" with title \"Claude Code\"'"
    }
  ]
}
```

### パターン4: コマンドログ記録

すべてのツール実行をログファイルに記録：

```json
{
  "matcher": "*",
  "hooks": [
    {
      "hookEventName": "PostToolUse",
      "command": "jq -c '{timestamp: now, tool: .tool_name, input: .tool_input}' >> ~/.claude/audit.log"
    }
  ]
}
```

## トラブルシューティング

### フックが実行されない

1. **settings.jsonの場所を確認**
   - プロジェクト: `.claude/settings.json`
   - グローバル: `~/.claude/settings.json`

2. **JSON構文をチェック**
   ```bash
   jq . ~/.claude/settings.json
   ```

3. **マッチャーパターンを確認**
   - ツール名が正確か
   - 正規表現が正しいか

### コマンドがエラーになる

1. **手動でコマンドをテスト**
   ```bash
   echo '{"tool_input":{"file_path":"test.ts"}}' | your-command
   ```

2. **タイムアウトを延長**
   ```json
   "timeout": 120
   ```

3. **デバッグ出力を追加**
   ```bash
   command | tee -a /tmp/hook-debug.log
   ```

### 意図しないファイルが対象になる

1. **より具体的なフィルタを使用**
   ```bash
   jq -r '.tool_input.file_path | select(test("^src/.*\\.ts$"))'
   ```

2. **除外パターンを追加**
   ```bash
   jq -r '.tool_input.file_path | select(test("node_modules|dist") | not)'
   ```

## セキュリティ上の注意

フックは任意のシェルコマンドを自動実行するため、以下に注意してください：

1. **入力の検証とサニタイズ**
   - ファイルパスを必ず検証
   - インジェクション攻撃を防ぐ

2. **権限の最小化**
   - 必要最小限の権限で実行
   - sudoの使用を避ける

3. **秘密情報の保護**
   - 環境変数やログに秘密情報を出力しない
   - .envファイル等の取り扱いに注意

4. **コードレビュー**
   - フック設定をチームで共有する前にレビュー
   - 外部から取得したフックは慎重に検証

## 参照ドキュメント

- `references/hook-specification.md` - 詳細な技術仕様
- `references/hook-events.md` - 全イベントの詳細説明
- `references/examples.md` - 実践的な実装例集
- [Claude Code公式ドキュメント](https://docs.claude.com/en/docs/claude-code/hooks.md)

## ツール

- `scripts/validate_hook.py` - フック設定の検証スクリプト
- `scripts/test_hook.sh` - フックのテストスクリプト
