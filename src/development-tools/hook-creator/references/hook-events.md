# Claude Code フックイベント詳細

このドキュメントでは、Claude Codeで利用可能な9つのフックイベントについて詳しく説明します。

## イベント一覧

| イベント | マッチャー対応 | タイミング | 主なユースケース |
|---------|--------------|-----------|----------------|
| **PreToolUse** | ✓ | ツール実行前 | 権限チェック、パラメータ検証 |
| **PostToolUse** | ✓ | ツール実行後 | 自動フォーマット、ログ記録 |
| **UserPromptSubmit** | ✗ | プロンプト送信時 | コンテキスト追加、入力検証 |
| **Notification** | ✗ | 通知時 | デスクトップ通知、Slack通知 |
| **SessionStart** | ✓ | セッション開始時 | 環境初期化、ログ開始 |
| **SessionEnd** | ✗ | セッション終了時 | クリーンアップ、ログ終了 |
| **Stop** | ✗ | エージェント停止時 | 状態保存 |
| **SubagentStop** | ✗ | サブエージェント停止時 | サブタスク完了処理 |
| **PreCompact** | ✓ | 圧縮前 | 重要情報の保存 |

## 1. PreToolUse

### 概要

Claude Codeがツールを実行する**直前**に発火します。ツールの実行を許可、拒否、またはユーザーに確認できます。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.ts",
    "old_string": "const x = 1;",
    "new_string": "const x = 2;"
  }
}
```

### マッチャー

ツール名でフィルタリング可能：
- `"Edit"` - Editツールのみ
- `"Write"` - Writeツールのみ
- `"Edit|Write"` - EditまたはWrite
- `"*"` - すべてのツール

### 出力オプション

#### 終了コード
- `0`: 許可
- `2`: 拒否（stderrのメッセージをClaudeに渡す）

#### JSON出力
```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
```

`permissionDecision`:
- `"allow"` - 実行を許可
- `"deny"` - 実行を拒否
- `"ask"` - ユーザーに確認

### ユースケース

#### 1. ファイル保護

本番ファイルや機密ファイルへの変更をブロック：

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "hookEventName": "PreToolUse",
      "command": "jq -r '.tool_input.file_path | select(test(\"production/|.env\"))' | grep -q . && echo 'Error: Cannot modify protected files' >&2 && exit 2 || exit 0"
    }
  ]
}
```

#### 2. パス検証

特定ディレクトリ外への書き込みを防止：

```bash
jq -r '.tool_input.file_path | select(test("^/safe/directory/") | not)' | grep -q . && exit 2 || exit 0
```

#### 3. 権限チェック

ユーザーに確認を求める：

```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask"
  }
}
```

## 2. PostToolUse

### 概要

Claude Codeがツールを実行した**直後**に発火します。実行結果に基づいて追加処理を行えます。

### 入力データ

PreToolUseと同じ構造ですが、ツール実行**後**のタイミング：

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "PostToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.ts",
    "old_string": "const x = 1;",
    "new_string": "const x = 2;"
  }
}
```

### マッチャー

PreToolUseと同様にツール名でフィルタリング可能。

### ユースケース

#### 1. 自動フォーマット

ファイル編集後に自動的にコードフォーマッタを実行：

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "hookEventName": "PostToolUse",
      "command": "jq -r '.tool_input.file_path | select(test(\"\\.tsx?$\"))' | xargs -r npx prettier --write"
    }
  ]
}
```

#### 2. コマンドログ記録

すべてのツール実行をログに記録：

```bash
jq -c '{timestamp: now, tool: .tool_name, input: .tool_input}' >> ~/.claude/audit.log
```

#### 3. ファイル拡張子別の処理

```bash
jq -r '.tool_input.file_path' | xargs -I {} sh -c '
  case {} in
    *.py) black {} ;;
    *.ts|*.tsx) npx prettier --write {} ;;
    *.go) gofmt -w {} ;;
    *.rs) rustfmt {} ;;
  esac
'
```

#### 4. Git自動コミット

編集後に自動的にコミット（慎重に使用）：

```bash
jq -r '.tool_input.file_path' | xargs git add && git commit -m "Auto-commit by Claude Code"
```

## 3. UserPromptSubmit

### 概要

ユーザーがプロンプトを送信した時に発火します。追加のコンテキストをClaudeに提供できます。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "TypeScriptのコードを書いて"
}
```

### マッチャー

このイベントはマッチャーをサポートしていません。

### 出力

終了コード0の場合、標準出力がClaudeの**追加コンテキスト**として扱われます。

または、JSON出力：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "プロジェクトのコーディング規約: ...\n現在のブランチ: main"
  }
}
```

### ユースケース

#### 1. プロジェクトコンテキストの自動追加

```bash
echo "Current branch: $(git branch --show-current)"
echo "Recent commits:"
git log -3 --oneline
```

#### 2. 環境情報の提供

```bash
echo "Node version: $(node --version)"
echo "Python version: $(python --version)"
echo "Available packages: $(pip list | wc -l)"
```

#### 3. コーディング規約の挿入

```bash
cat .claude/coding-standards.md
```

#### 4. TODOリストの表示

```bash
grep -r "TODO" src/ | head -10
```

## 4. Notification

### 概要

Claude Codeが入力待機状態になった時に発火します。デスクトップ通知などに使用します。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "Notification"
}
```

### マッチャー

このイベントはマッチャーをサポートしていません。

### ユースケース

#### 1. macOSデスクトップ通知

```bash
osascript -e 'display notification "Claude Code is waiting for input" with title "Claude Code"'
```

#### 2. Linuxデスクトップ通知

```bash
notify-send "Claude Code" "Waiting for input"
```

#### 3. サウンド再生

```bash
afplay /System/Library/Sounds/Glass.aiff  # macOS
```

#### 4. Slack通知

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Claude Code is ready"}' \
  YOUR_SLACK_WEBHOOK_URL
```

## 5. SessionStart

### 概要

Claudeセッションが開始された時に発火します。環境の初期化に使用します。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "SessionStart",
  "session_start_type": "startup"
}
```

`session_start_type`:
- `"startup"` - 新規セッション開始
- `"resume"` - セッション再開
- `"clear"` - コンテキストクリア後の再開始

### マッチャー

このイベントはマッチャーをサポートしています（`session_start_type`でフィルタリング可能）。

### ユースケース

#### 1. セッションログ開始

```bash
echo "[$(date)] Session started: $(jq -r '.session_id')" >> ~/.claude/sessions.log
```

#### 2. 環境変数の設定

```bash
export PROJECT_ENV="development"
export DEBUG_MODE="true"
```

#### 3. 初期化スクリプトの実行

```bash
# 依存関係の確認
npm list --depth=0

# データベース接続確認
psql -c "SELECT 1;" mydb
```

#### 4. Gitステータスの確認

```bash
git status
git branch --show-current
```

## 6. SessionEnd

### 概要

Claudeセッションが終了する時に発火します。クリーンアップ処理に使用します。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "SessionEnd"
}
```

### マッチャー

このイベントはマッチャーをサポートしていません。

### ユースケース

#### 1. セッションログ終了

```bash
echo "[$(date)] Session ended: $(jq -r '.session_id')" >> ~/.claude/sessions.log
```

#### 2. 一時ファイルのクリーンアップ

```bash
rm -f /tmp/claude-temp-*
```

#### 3. 統計情報の記録

```bash
echo "Total commands: $(jq 'length' "$transcript_path")" >> ~/.claude/stats.log
```

## 7. Stop

### 概要

エージェント（メインClaude）が停止する時に発火します。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "Stop"
}
```

### マッチャー

このイベントはマッチャーをサポートしていません。

### ユースケース

#### 1. 状態の保存

```bash
git stash push -m "Claude Code auto-save $(date)"
```

#### 2. 通知

```bash
osascript -e 'display notification "Agent stopped" with title "Claude Code"'
```

## 8. SubagentStop

### 概要

サブエージェントが停止する時に発火します。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "SubagentStop"
}
```

### マッチャー

このイベントはマッチャーをサポートしていません。

### ユースケース

#### 1. サブタスク完了ログ

```bash
echo "[$(date)] Subagent completed" >> ~/.claude/subagent.log
```

#### 2. リソースのクリーンアップ

```bash
# サブエージェント専用の一時ファイルを削除
rm -f /tmp/subagent-*
```

## 9. PreCompact

### 概要

コンテキストが圧縮される**前**に発火します。重要な情報を保存する最後の機会です。

### 入力データ

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "PreCompact",
  "compact_type": "manual"
}
```

`compact_type`:
- `"manual"` - ユーザーが手動で実行
- `"auto"` - 自動圧縮

### マッチャー

このイベントはマッチャーをサポートしています（`compact_type`でフィルタリング可能）。

### ユースケース

#### 1. 重要情報の保存

```bash
# 現在のコンテキストをファイルに保存
jq . "$transcript_path" > ~/.claude/backups/pre-compact-$(date +%s).json
```

#### 2. スナップショットの作成

```bash
git add -A
git commit -m "Pre-compact snapshot"
```

#### 3. 圧縮前の通知

```bash
if [ "$(jq -r '.compact_type')" = "auto" ]; then
  echo "Warning: Automatic context compression triggered" >&2
fi
```

## イベント選択ガイド

### ツール実行を制御したい
→ **PreToolUse** (実行前) または **PostToolUse** (実行後)

### ユーザー入力に応じて情報を追加したい
→ **UserPromptSubmit**

### 作業完了を通知したい
→ **Notification**

### セッション開始/終了時に処理したい
→ **SessionStart** / **SessionEnd**

### エージェント停止時に処理したい
→ **Stop** / **SubagentStop**

### コンテキスト圧縮前に保存したい
→ **PreCompact**

## マッチャー対応イベント

以下のイベントのみマッチャーパターンをサポート：
- PreToolUse
- PostToolUse
- SessionStart（session_start_typeでフィルタ）
- PreCompact（compact_typeでフィルタ）

その他のイベントは、すべての発生に対してフックが実行されます。
