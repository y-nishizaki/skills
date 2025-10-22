# Claude Code スキルカタログ

このディレクトリには GitHub Pages 用のスキルカタログページが含まれています。

## ファイル構成

- `index.html` - メインのカタログページ
- `skills.json` - スキルメタデータ（自動生成）
- `generate_catalog.py` - スキルメタデータ抽出スクリプト
- `.nojekyll` - Jekyll処理を無効化

## スキルカタログの更新方法

### 自動更新（推奨）

`main` ブランチにプッシュすると、GitHub Actions が自動的に：

1. `docs/generate_catalog.py` を実行してスキルカタログを生成
2. GitHub Pages にデプロイ

新しいスキルを追加したら、`main` ブランチにマージするだけで自動的にカタログが更新されます。

### 手動更新

ローカルでカタログを確認したい場合：

```bash
python3 docs/generate_catalog.py
```

これにより `docs/skills.json` が更新されます。

## GitHub Pages の設定

### GitHub Actions を使用する場合（推奨）

1. GitHubリポジトリの **Settings** → **Pages** に移動
2. **Source** を `GitHub Actions` に設定
3. `.github/workflows/deploy-pages.yml` が自動的にデプロイを実行

### 手動デプロイの場合

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
