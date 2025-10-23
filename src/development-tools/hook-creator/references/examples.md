# Claude Code フック実装例集

このドキュメントでは、実践的なフック実装例を紹介します。

## 基本パターン

### 1. TypeScript/JavaScript自動フォーマット

ファイル保存時に自動的にPrettierを実行：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.([tj]sx?|json|css|md)$\"))' | xargs -r npx prettier --write",
          "timeout": 30
        }
      ]
    }
  ]
}
```

**特徴**:
- TypeScript (.ts, .tsx)、JavaScript (.js, .jsx)、JSON、CSS、Markdownに対応
- `xargs -r`で対象ファイルがない場合はスキップ
- タイムアウト30秒

### 2. Python自動フォーマット

Pythonファイル保存時にblackとisortを実行：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.py$\"))' | xargs -r sh -c 'black \"$1\" && isort \"$1\"' sh",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### 3. Go自動フォーマット

Goファイル保存時にgofmtとgoimportsを実行：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.go$\"))' | xargs -r sh -c 'gofmt -w \"$1\" && goimports -w \"$1\"' sh",
          "timeout": 20
        }
      ]
    }
  ]
}
```

## ファイル保護パターン

### 4. 本番ファイルの保護

本番環境のファイルへの変更をブロック：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PreToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"^(production/|prod/|dist/)\"))' | grep -q . && echo '🚫 Error: Cannot modify production files. Please modify source files instead.' >&2 && exit 2 || exit 0"
        }
      ]
    }
  ]
}
```

### 5. 環境ファイルの保護

.env、credentials.jsonなどの機密ファイルを保護：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PreToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.env$|credentials|secrets|private-key\"))' | grep -q . && echo '🔒 Error: Cannot modify sensitive files. Please update manually.' >&2 && exit 2 || exit 0"
        }
      ]
    }
  ]
}
```

### 6. node_modules保護

node_modulesディレクトリへの直接編集を防止：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PreToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"node_modules/\"))' | grep -q . && echo '⚠️  Error: Cannot modify node_modules. Please update package.json instead.' >&2 && exit 2 || exit 0"
        }
      ]
    }
  ]
}
```

## 通知パターン

### 7. macOSデスクトップ通知

Claude Codeが入力待機時にデスクトップ通知を表示：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "Notification",
          "command": "osascript -e 'display notification \"I have completed your task and am waiting for input\" with title \"Claude Code\"'",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 8. Linuxデスクトップ通知

Linuxデスクトップ環境での通知：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "Notification",
          "command": "notify-send -i dialog-information 'Claude Code' 'Waiting for your input'",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 9. サウンド付き通知（macOS）

通知時に音も鳴らす：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "Notification",
          "command": "osascript -e 'display notification \"Task complete\" with title \"Claude Code\" sound name \"Glass\"'",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## ログ記録パターン

### 10. コマンド監査ログ

すべてのツール実行を詳細にログ記録：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -c '{timestamp: now | strftime(\"%Y-%m-%d %H:%M:%S\"), session: .session_id, tool: .tool_name, input: .tool_input}' >> ~/.claude/audit.log",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 11. ファイル変更ログ

ファイル編集のみを記録：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -c '{time: now | strftime(\"%Y-%m-%d %H:%M:%S\"), file: .tool_input.file_path, tool: .tool_name}' >> ~/.claude/file-changes.log",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 12. セッションログ

セッション開始・終了を記録：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "SessionStart",
          "command": "echo \"[$(date '+%Y-%m-%d %H:%M:%S')] Session started: $(jq -r '.session_id') in $(jq -r '.cwd')\" >> ~/.claude/sessions.log",
          "timeout": 5
        },
        {
          "hookEventName": "SessionEnd",
          "command": "echo \"[$(date '+%Y-%m-%d %H:%M:%S')] Session ended: $(jq -r '.session_id')\" >> ~/.claude/sessions.log",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## コンテキスト追加パターン

### 13. Git情報の自動追加

プロンプト送信時にGit情報を追加：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "UserPromptSubmit",
          "command": "echo \"Current Git Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')\" && echo \"Recent Commits:\" && git log -3 --oneline 2>/dev/null || echo 'No git repository'",
          "timeout": 10
        }
      ]
    }
  ]
}
```

### 14. プロジェクト情報の自動追加

package.jsonやpyproject.tomlの情報を追加：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "UserPromptSubmit",
          "command": "if [ -f package.json ]; then echo \"Project: $(jq -r '.name' package.json)\" && echo \"Version: $(jq -r '.version' package.json)\"; elif [ -f pyproject.toml ]; then echo \"Python Project\"; fi",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 15. TODOリストの表示

プロジェクト内のTODOを自動表示：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "UserPromptSubmit",
          "command": "echo \"Outstanding TODOs:\" && grep -r \"TODO\\|FIXME\" src/ 2>/dev/null | head -5 || echo \"No TODOs found\"",
          "timeout": 10
        }
      ]
    }
  ]
}
```

## 複合パターン

### 16. 多言語自動フォーマット

複数の言語に対応した統合フォーマッター：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'case \"{}\" in *.py) black \"{}\" ;; *.ts|*.tsx|*.js|*.jsx) npx prettier --write \"{}\" ;; *.go) gofmt -w \"{}\" ;; *.rs) rustfmt \"{}\" ;; *.java) google-java-format -i \"{}\" ;; esac'",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### 17. Linter + Formatter

フォーマット前にLinterを実行：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.tsx?$\"))' | xargs -r sh -c 'npx eslint --fix \"$1\" && npx prettier --write \"$1\"' sh",
          "timeout": 45
        }
      ]
    }
  ]
}
```

### 18. Git自動ステージング

ファイル変更後にGitにステージング（自動コミットはしない）：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path' | xargs -r git add",
          "timeout": 10
        }
      ]
    }
  ]
}
```

## 検証パターン

### 19. TypeScript型チェック

TypeScriptファイル編集後に型チェック：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.tsx?$\"))' | xargs -r sh -c 'npx tsc --noEmit \"$1\" 2>&1 | head -20' sh",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### 20. Python型チェック

Pythonファイル編集後にmypyで型チェック：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.py$\"))' | xargs -r mypy",
          "timeout": 20
        }
      ]
    }
  ]
}
```

## デバッグパターン

### 21. デバッグ出力

すべてのフックイベントをファイルに出力（デバッグ用）：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq . >> ~/.claude/debug.log",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### 22. 詳細ログ

イベントデータを読みやすい形式でログ：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "echo \"===\" >> ~/.claude/verbose.log && jq -r '\"Event: \\(.hook_event_name)\\nTool: \\(.tool_name // \"N/A\")\\nTime: \\(now | strftime(\"%Y-%m-%d %H:%M:%S\"))\\n\"' >> ~/.claude/verbose.log",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## 高度なパターン

### 23. Markdownリンク検証

Markdownファイル編集後にリンク切れチェック：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.md$\"))' | xargs -r markdown-link-check",
          "timeout": 60
        }
      ]
    }
  ]
}
```

### 24. 画像最適化

画像ファイル保存時に自動的に最適化：

```json
{
  "hooks": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.png$\"))' | xargs -r optipng -o2",
          "timeout": 120
        }
      ]
    }
  ]
}
```

### 25. コンテキスト圧縮前のバックアップ

コンテキスト圧縮前に会話ログをバックアップ：

```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "PreCompact",
          "command": "jq . \"$(jq -r '.transcript_path')\" > ~/.claude/backups/transcript-$(date +%Y%m%d-%H%M%S).json",
          "timeout": 10
        }
      ]
    }
  ]
}
```

## プロジェクト固有パターン

### 26. フロントエンド開発向け

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'case \"{}\" in *.tsx|*.ts|*.jsx|*.js) npx eslint --fix \"{}\" && npx prettier --write \"{}\" ;; *.css|*.scss) npx stylelint --fix \"{}\" ;; esac'",
          "timeout": 45
        }
      ]
    }
  ]
}
```

### 27. バックエンド開発向け（Python）

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.py$\"))' | xargs -r sh -c 'black \"$1\" && isort \"$1\" && flake8 \"$1\"' sh",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### 28. DevOps向け

YAMLファイルのLint：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"\\\\.ya?ml$\"))' | xargs -r yamllint",
          "timeout": 20
        }
      ]
    }
  ]
}
```

## 組み合わせ例

### 29. フル機能設定

複数のフックを組み合わせた完全な設定例：

```json
{
  "hooks": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "hookEventName": "PreToolUse",
          "command": "jq -r '.tool_input.file_path | select(test(\"production/|.env\"))' | grep -q . && echo 'Cannot modify protected files' >&2 && exit 2 || exit 0"
        },
        {
          "hookEventName": "PostToolUse",
          "command": "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'case \"{}\" in *.py) black \"{}\" && isort \"{}\" ;; *.ts|*.tsx) npx prettier --write \"{}\" ;; *.go) gofmt -w \"{}\" ;; esac'",
          "timeout": 30
        },
        {
          "hookEventName": "PostToolUse",
          "command": "jq -c '{time: now | strftime(\"%Y-%m-%d %H:%M:%S\"), file: .tool_input.file_path}' >> ~/.claude/changes.log",
          "timeout": 5
        }
      ]
    },
    {
      "matcher": "*",
      "hooks": [
        {
          "hookEventName": "Notification",
          "command": "osascript -e 'display notification \"Task complete\" with title \"Claude Code\"'",
          "timeout": 5
        },
        {
          "hookEventName": "UserPromptSubmit",
          "command": "echo \"Branch: $(git branch --show-current 2>/dev/null || echo N/A)\"",
          "timeout": 5
        }
      ]
    }
  ]
}
```

## トラブルシューティング例

### 30. エラーハンドリング

フォーマッターが失敗してもエラーを無視：

```bash
jq -r '.tool_input.file_path' | xargs -r npx prettier --write 2>/dev/null || true
```

### 31. 条件付き実行

特定条件下でのみ実行：

```bash
if [ -f .prettierrc ]; then
  jq -r '.tool_input.file_path' | xargs -r npx prettier --write
fi
```

### 32. タイムアウト対策

バックグラウンド実行で長時間処理を回避：

```bash
jq -r '.tool_input.file_path' | xargs -r sh -c 'nohup eslint "$1" > /dev/null 2>&1 &' sh
```

## まとめ

これらの例は、様々なユースケースに対応したフック実装を示しています。プロジェクトの要件に応じて、これらの例をカスタマイズして使用してください。

**重要な注意事項**:
- フックは自動実行されるため、十分にテストしてから本番使用してください
- タイムアウトを適切に設定し、長時間実行を避けてください
- セキュリティに注意し、入力を適切に検証してください
- エラーハンドリングを実装し、予期しない失敗に対処してください
