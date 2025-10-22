# Claude Code スキルカタログ

このディレクトリには GitHub Pages 用のスキルカタログページが含まれています。

## ファイル構成

- `index.html` - メインのカタログページ
- `skills.json` - スキルメタデータ（自動生成）
- `generate_catalog.py` - スキルメタデータ抽出スクリプト
- `.nojekyll` - Jekyll処理を無効化

## スキルカタログの更新方法

新しいスキルを追加したり、既存のスキルを更新した場合は、以下のコマンドでカタログを再生成してください：

```bash
python3 docs/generate_catalog.py
```

これにより `docs/skills.json` が更新され、GitHub Pages に反映されます。

## GitHub Pages の設定

1. GitHubリポジトリの **Settings** → **Pages** に移動
2. **Source** を `Deploy from a branch` に設定
3. **Branch** を `main` (または `master`) に設定し、フォルダを `/docs` に設定
4. **Save** をクリック

数分後、以下のURLでカタログページが公開されます：

```
https://y-nishizaki.github.io/skills/
```

## ローカルでのプレビュー

ローカルでプレビューする場合は、簡易的なHTTPサーバーを起動してください：

```bash
cd docs
python3 -m http.server 8000
```

その後、ブラウザで `http://localhost:8000` を開きます。
