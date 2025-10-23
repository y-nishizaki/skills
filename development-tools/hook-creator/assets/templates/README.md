# フックテンプレート集

このディレクトリには、よくあるユースケース向けのフック設定テンプレートが含まれています。

## 使い方

1. テンプレートファイルを開く
2. 内容を `~/.claude/settings.json` または `.claude/settings.json` にコピー
3. 必要に応じてカスタマイズ
4. Claude Codeを再起動（設定を反映）

## テンプレート一覧

### 1. auto-format.json

**用途**: ファイル保存時に自動的にコードフォーマッタを実行

**対応言語**:
- Python: black + isort
- TypeScript/JavaScript: prettier
- Go: gofmt
- Rust: rustfmt
- Java: google-java-format
- CSS/SCSS: prettier
- JSON/Markdown/YAML: prettier

**必要なツール**:
```bash
# Python
pip install black isort

# JavaScript/TypeScript
npm install -g prettier

# Go (標準搭載)

# Rust (標準搭載)

# Java
# google-java-formatをインストール
```

**カスタマイズ例**:
- 特定の言語のみに限定
- フォーマッタのオプションを追加
- タイムアウトを調整

### 2. notification.json (macOS)

**用途**: Claude Codeが入力待機時にデスクトップ通知を表示

**対応OS**: macOS

**追加設定**: 不要（osascriptは標準搭載）

**カスタマイズ例**:
- 通知メッセージの変更
- サウンドの追加
- 通知スタイルの変更

### 3. notification-linux.json (Linux)

**用途**: Claude Codeが入力待機時にデスクトップ通知を表示

**対応OS**: Linux (GNOME, KDE, etc.)

**必要なツール**:
```bash
sudo apt-get install libnotify-bin  # Debian/Ubuntu
sudo dnf install libnotify           # Fedora
```

### 4. logging.json

**用途**: Claude Codeの操作を詳細にログ記録

**ログファイル**:
- `~/.claude/audit.log` - すべてのツール実行
- `~/.claude/sessions.log` - セッション開始/終了

**機能**:
- タイムスタンプ付きログ
- ツール名とパラメータの記録
- セッション追跡

**カスタマイズ例**:
- ログファイルの場所を変更
- ログフォーマットを変更
- 特定のツールのみログ

### 5. file-protection.json

**用途**: 重要なファイルやディレクトリへの変更を防止

**保護対象**:
- 本番ファイル: `production/`, `prod/`, `dist/`, `build/`
- 機密ファイル: `.env`, `credentials`, `secrets`, `private-key`
- 依存関係: `node_modules/`, `vendor/`, `venv/`, `__pycache__/`

**動作**:
- 変更をブロック（終了コード2）
- エラーメッセージを表示
- Claudeがユーザーに説明

**カスタマイズ例**:
- 保護するディレクトリを追加
- 正規表現パターンを調整
- エラーメッセージを変更

### 6. code-quality-check.json

**用途**: ファイル保存後に自動的にLinterとフォーマッタを実行

**対応言語**:
- TypeScript/JavaScript: eslint + prettier
- Python: black + isort + flake8
- Go: gofmt + go vet

**必要なツール**:
```bash
# TypeScript/JavaScript
npm install -g eslint prettier

# Python
pip install black isort flake8

# Go (標準搭載)
```

**特徴**:
- Lintエラーを自動修正
- フォーマットを統一
- 静的解析を実行

**カスタマイズ例**:
- Linterルールを調整
- 特定のチェックをスキップ
- エラーを無視（`|| true`）

### 7. git-context.json

**用途**: プロンプト送信時にGit情報を自動的に追加

**追加情報**:
- 現在のブランチ名
- 最近のコミット（直近3件）

**利点**:
- Claudeがプロジェクトの状態を把握
- ブランチ固有の作業に対応
- コミット履歴を参照可能

**カスタマイズ例**:
- コミット表示数を変更
- 追加のGit情報（diff、status等）
- プロジェクト情報の追加

## 複数テンプレートの組み合わせ

複数のテンプレートを同時に使用できます：

```json
{
  "hooks": [
    // auto-format.jsonの内容
    {
      "matcher": "Edit|Write",
      "hooks": [...]
    },
    // notification.jsonの内容
    {
      "matcher": "*",
      "hooks": [...]
    },
    // logging.jsonの内容
    {
      "matcher": "*",
      "hooks": [...]
    }
  ]
}
```

## トラブルシューティング

### フックが動作しない

1. **設定ファイルの場所を確認**
   - グローバル: `~/.claude/settings.json`
   - プロジェクト: `.claude/settings.json`

2. **JSON構文をチェック**
   ```bash
   jq . ~/.claude/settings.json
   ```

3. **Claude Codeを再起動**

### コマンドがエラーになる

1. **必要なツールがインストールされているか確認**
   ```bash
   which prettier  # または該当ツール
   ```

2. **手動でコマンドをテスト**
   ```bash
   echo '{"tool_input":{"file_path":"test.ts"}}' | jq -r '.tool_input.file_path'
   ```

3. **タイムアウトを延長**
   ```json
   "timeout": 60
   ```

### パフォーマンスが悪い

1. **対象ファイルを限定**
   ```bash
   jq -r '.tool_input.file_path | select(test("^src/"))'
   ```

2. **タイムアウトを短縮**
   ```json
   "timeout": 10
   ```

3. **不要なフックを無効化**

## 参考資料

- [SKILL.md](../../SKILL.md) - フック作成ガイド
- [references/hook-specification.md](../../references/hook-specification.md) - 技術仕様
- [references/hook-events.md](../../references/hook-events.md) - イベント詳細
- [references/examples.md](../../references/examples.md) - 実装例集
