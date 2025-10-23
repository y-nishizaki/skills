# Claude Code フック技術仕様

このドキュメントでは、Claude Codeのフック機能の詳細な技術仕様を説明します。

## 概要

フックは、Claude Codeのライフサイクルイベントに応じて自動実行されるユーザー定義のシェルコマンドです。設定ファイル（`~/.claude/settings.json`または`.claude/settings.json`）で定義され、イベント駆動型の自動化を可能にします。

## 設定ファイルの場所

フック設定は以下の場所に配置できます（優先度順）：

1. **プロジェクトローカル**: `.claude/settings.json`
   - プロジェクト固有のフック
   - リポジトリにコミットして共有可能

2. **ユーザーグローバル**: `~/.claude/settings.json`
   - すべてのプロジェクトで有効
   - 個人的な設定に使用

## 設定構造

### 基本フォーマット

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

### フィールド説明

#### matcher（文字列、必須）

フックを適用するツールを指定するパターン。以下の形式をサポート：

- **完全一致**: `"Edit"`, `"Read"`, `"Write"`, `"Bash"` など
- **ワイルドカード**: `"*"` - すべてのツールに適用
- **正規表現**: `"Edit|Write"` - EditまたはWrite

**注意**: イベントタイプによってマッチャーの適用可否が異なります。詳細は「フックイベント」セクションを参照。

#### hookEventName（文字列、必須）

フックを実行するライフサイクルイベント。以下のいずれか：

- `PreToolUse`
- `PostToolUse`
- `UserPromptSubmit`
- `Notification`
- `SessionStart`
- `SessionEnd`
- `Stop`
- `SubagentStop`
- `PreCompact`

#### command（文字列、必須）

実行するシェルコマンド。標準入力からJSON形式のイベントデータを受け取ります。

**特徴**:
- `/bin/sh`で実行される
- パイプ、リダイレクト、コマンド連結が使用可能
- 環境変数にアクセス可能（`CLAUDE_PROJECT_DIR`, `CLAUDE_CODE_REMOTE`など）

#### timeout（数値、オプション）

コマンドの最大実行時間（秒単位）。

- **デフォルト**: 60秒
- **最大**: 制限なし（設定可能）
- タイムアウト時はコマンドが強制終了される

## 入力形式

すべてのフックコマンドは、標準入力（stdin）からJSON形式のイベントデータを受け取ります。

### 共通フィールド

すべてのイベントに含まれる基本フィールド：

```json
{
  "session_id": "セッション識別子",
  "transcript_path": "会話ログファイルのパス",
  "cwd": "現在の作業ディレクトリ",
  "hook_event_name": "イベント名"
}
```

### イベント固有フィールド

#### PreToolUse / PostToolUse

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

**フィールド**:
- `tool_name`: 実行されるツールの名前
- `tool_input`: ツールに渡されるパラメータ（ツールによって異なる）

#### UserPromptSubmit

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "ユーザーが入力したプロンプト"
}
```

**フィールド**:
- `prompt`: ユーザーが送信したプロンプトテキスト

#### SessionStart

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "SessionStart",
  "session_start_type": "startup"
}
```

**フィールド**:
- `session_start_type`: セッション開始の種類
  - `"startup"` - 新規セッション
  - `"resume"` - セッション再開
  - `"clear"` - コンテキストクリア後

#### Notification

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "Notification"
}
```

#### Stop / SubagentStop / SessionEnd / PreCompact

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/working/directory",
  "hook_event_name": "Stop"
}
```

PreCompactイベントには追加で以下のフィールドが含まれます：

```json
{
  "compact_type": "manual"
}
```

**フィールド**:
- `compact_type`: 圧縮の種類
  - `"manual"` - ユーザーが手動で実行
  - `"auto"` - 自動圧縮

## 出力形式

フックコマンドは、終了コードまたはJSON出力で結果を返します。

### 終了コードによる制御

最もシンプルな出力方法：

- **0**: 成功
  - 標準出力（stdout）がユーザーに表示される
  - ただし、`UserPromptSubmit`の場合は追加コンテキストとして扱われる

- **2**: ブロック（処理を停止）
  - 標準エラー出力（stderr）がClaudeに渡される
  - Claudeがエラーメッセージを処理してユーザーに説明

- **その他（1, 3-255）**: 非ブロックエラー
  - エラーメッセージが表示されるが、処理は継続

### JSON出力による高度な制御

より細かい制御が必要な場合は、JSON形式で出力：

```json
{
  "continue": true,
  "stopReason": "オプションのメッセージ",
  "suppressOutput": false,
  "hookSpecificOutput": {
    "hookEventName": "イベントタイプ",
    ...
  }
}
```

#### 共通フィールド

- **continue** (boolean): 処理を継続するか
  - `true`: 継続
  - `false`: 停止（終了コード2と同等）

- **stopReason** (string): 停止理由メッセージ

- **suppressOutput** (boolean): 標準出力を抑制するか
  - `true`: 出力を表示しない
  - `false`: 出力を表示（デフォルト）

#### イベント固有の出力

**PreToolUse**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
```

`permissionDecision`:
- `"allow"` - ツール実行を許可
- `"deny"` - ツール実行を拒否
- `"ask"` - ユーザーに確認

**UserPromptSubmit**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "追加コンテキストテキスト"
  }
}
```

`additionalContext`: Claudeのコンテキストに追加される情報

## 実行環境

### 環境変数

フックコマンドは以下の環境変数にアクセスできます：

- **CLAUDE_PROJECT_DIR**: プロジェクトルートディレクトリ
- **CLAUDE_CODE_REMOTE**: リモート実行モードかどうか
- その他システム環境変数

### シェル

- コマンドは `/bin/sh` で実行されます
- Bash固有の機能を使用する場合は明示的に `bash -c "command"` を指定

### 並列実行と重複排除

- 複数のフックが同じイベントに登録されている場合、並列実行されます
- 同一の`(matcher, hookEventName, command)`の組み合わせは自動的に重複排除されます

## データ抽出パターン

### jqを使用した基本的な抽出

```bash
# ファイルパスを取得
jq -r '.tool_input.file_path'

# ツール名を取得
jq -r '.tool_name'

# プロンプトを取得
jq -r '.prompt'
```

### フィルタリング

```bash
# TypeScriptファイルのみ
jq -r '.tool_input.file_path | select(test("\\.tsx?$"))'

# 特定ディレクトリを除外
jq -r '.tool_input.file_path | select(test("^(?!node_modules/)"))'

# 特定ディレクトリのみ
jq -r '.tool_input.file_path | select(test("^src/"))'
```

### 条件分岐

```bash
# ファイル拡張子に応じて異なる処理
jq -r '.tool_input.file_path' | xargs -I {} sh -c '
  case {} in
    *.py) black {} ;;
    *.ts|*.tsx) npx prettier --write {} ;;
    *.go) gofmt -w {} ;;
  esac
'
```

## ベストプラクティス

### セキュリティ

1. **入力のサニタイズ**
   ```bash
   # 悪い例：直接評価
   eval "$(jq -r '.some_field')"  # 危険！

   # 良い例：安全な処理
   jq -r '.some_field' | xargs -0 command
   ```

2. **パスの検証**
   ```bash
   # ファイルパスを検証
   jq -r '.tool_input.file_path' | grep -E '^[a-zA-Z0-9/_.-]+$'
   ```

3. **秘密情報の保護**
   ```bash
   # .envファイルを除外
   jq -r '.tool_input.file_path | select(test("\\.env") | not)'
   ```

### エラーハンドリング

```bash
# コマンドの成功/失敗を確認
jq -r '.tool_input.file_path' | xargs prettier --write || {
  echo "Formatting failed" >&2
  exit 1
}
```

### デバッグ

```bash
# デバッグ出力
jq . >&2  # 全入力をstderrに出力

# ログファイルに記録
jq -c '{time: now, event: .hook_event_name, tool: .tool_name}' >> ~/.claude/debug.log
```

### パフォーマンス

1. **タイムアウトを適切に設定**
   ```json
   {
     "timeout": 30
   }
   ```

2. **重い処理はバックグラウンドで**
   ```bash
   command & disown  # バックグラウンド実行
   ```

3. **不要な処理をスキップ**
   ```bash
   # 特定条件でのみ実行
   jq -r '.tool_input.file_path | select(test("\\.ts$"))' | xargs -r command
   ```

## 制限事項

1. **タイムアウト**: デフォルト60秒で実行が打ち切られる
2. **並列実行**: 複数フックの実行順序は保証されない
3. **環境依存**: シェルコマンドはOSやインストール済みツールに依存
4. **エラーログ**: フックのエラーは通常のログに混在する可能性がある

## トラブルシューティング

### フックが実行されない

1. JSON構文を確認: `jq . settings.json`
2. マッチャーパターンを確認
3. イベント名のスペルを確認

### コマンドがエラーになる

1. 手動でテスト: `echo '{"tool_input":{"file_path":"test.ts"}}' | command`
2. デバッグ出力を追加: `jq . >&2`
3. タイムアウトを延長

### パフォーマンスが悪い

1. 処理をフィルタリング
2. タイムアウトを短縮
3. 並列処理を避ける

## 参考資料

- [Claude Code公式ドキュメント - Hooks](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [Claude Code公式ドキュメント - Hooks Guide](https://docs.claude.com/en/docs/claude-code/hooks-guide.md)
