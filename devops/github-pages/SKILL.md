---
name: "GitHub Pages"
description: "GitHub Pagesを使用した静的サイトホスティングの設定と管理。静的サイト、ドキュメントサイト、ポートフォリオ、プロジェクトページ、Jekyll、カスタムドメイン、GitHub Actions連携に関する依頼に対応"
---

# GitHub Pages: 静的サイトホスティングの思考プロセス

## このスキルを使う場面

- プロジェクトドキュメントサイトの公開
- ポートフォリオサイトの作成
- 静的Webサイトのホスティング
- Jekyllベースのブログの構築
- カスタムドメインの設定
- GitHub Actionsを使った自動デプロイ

## GitHub Pagesとは

GitHub Pagesは、GitHubリポジトリから直接HTML、CSS、JavaScriptファイルをホストする静的サイトホスティングサービス。オプションでビルドプロセスを経由してWebサイトを公開する。

### 主要機能

**サイトタイプ:**

- **ユーザー/組織サイト**: `<owner>.github.io` リポジトリ（アカウントごと1つ）
- **プロジェクトサイト**: 任意のリポジトリ（リポジトリごと1つ）

**公開URL:**

- ユーザーサイト: `https://<owner>.github.io`
- プロジェクトサイト: `https://<owner>.github.io/<repository-name>`
- カスタムドメイン: `https://example.com`

**利用可能範囲:**

- GitHub Free: パブリックリポジトリのみ
- GitHub Pro/Team/Enterprise: パブリック・プライベート両方

**組み込み機能:**

- HTTPS/SSL自動対応
- CDN配信
- Jekyll統合
- GitHub Actions連携

## 思考プロセス

### フェーズ1: サイトタイプの決定

**ステップ1: 要件の理解**

公開するサイトのタイプを明確にする:

**ユーザー/組織サイトの選択:**

- [ ] 個人ポートフォリオ
- [ ] 組織のメインサイト
- [ ] ブログ
- [ ] URL: `<owner>.github.io`

**プロジェクトサイトの選択:**

- [ ] プロジェクトドキュメント
- [ ] デモサイト
- [ ] プロダクトページ
- [ ] URL: `<owner>.github.io/<repo-name>`

**ステップ2: リポジトリの準備**

**ユーザーサイトの場合:**

```bash
# リポジトリ名: username.github.io
git init
git remote add origin https://github.com/username/username.github.io.git
```

**プロジェクトサイトの場合:**

```bash
# 既存プロジェクトリポジトリを使用
cd existing-project
```

**移行条件:**

- [ ] サイトタイプを決定した
- [ ] リポジトリを準備した
- [ ] 公開URLを確認した

### フェーズ2: 基本的なサイト設定

**ステップ1: 静的HTMLサイトの公開**

最小限の構成でサイトを公開:

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My GitHub Pages Site</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Welcome to My Site</h1>
    </header>
    <main>
        <p>This is hosted on GitHub Pages!</p>
    </main>
    <footer>
        <p>&copy; 2025 My Project</p>
    </footer>
</body>
</html>
```

```css
/* styles.css */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    border-bottom: 2px solid #333;
    margin-bottom: 20px;
}

footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #ccc;
    text-align: center;
    color: #666;
}
```

**ステップ2: GitHub Pagesの有効化**

リポジトリ設定でGitHub Pagesを有効化:

1. リポジトリの **Settings** → **Pages**
2. **Source** でブランチを選択（mainまたはgh-pages）
3. オプションでフォルダを選択（/ (root) または /docs）
4. **Save**をクリック

**ステップ3: 確認**

```bash
# ファイルをコミット・プッシュ
git add .
git commit -m "Initial GitHub Pages setup"
git push origin main

# 数分後にサイトにアクセス
# https://username.github.io または
# https://username.github.io/repository-name
```

**移行条件:**

- [ ] HTMLファイルを作成した
- [ ] GitHub Pagesを有効化した
- [ ] サイトが公開されたことを確認した

### フェーズ3: Jekyllの活用

**ステップ1: Jekyllの基本設定**

GitHub Pagesは自動的にJekyllをサポート:

```yaml
# _config.yml
title: My Awesome Site
description: A site built with Jekyll and GitHub Pages
author: Your Name
email: your-email@example.com

# テーマの選択
theme: minima

# URL設定
baseurl: "" # ユーザーサイトの場合
# baseurl: "/repository-name" # プロジェクトサイトの場合

# マークダウン設定
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge

# プラグイン
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-sitemap

# 除外するファイル
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
  - .gitignore
  - README.md
```

**ステップ2: ページの作成**

```markdown
<!-- index.md -->
---
layout: home
title: Home
---

# Welcome to My Site

This is the homepage of my Jekyll-powered GitHub Pages site.

## Features

- Easy content management with Markdown
- Built-in themes
- Blog support
- SEO optimized
```

```markdown
<!-- about.md -->
---
layout: page
title: About
permalink: /about/
---

## About This Project

This site demonstrates the power of GitHub Pages and Jekyll.

### Technologies Used

- GitHub Pages
- Jekyll
- Markdown
```

**ステップ3: ブログ機能の追加**

```markdown
<!-- _posts/2025-01-15-first-post.md -->
---
layout: post
title: "My First Blog Post"
date: 2025-01-15 10:00:00 +0900
categories: blog
tags: [github-pages, jekyll]
---

# Welcome to My Blog

This is my first post using Jekyll on GitHub Pages!

## Getting Started

Jekyll makes it easy to create blog posts with just Markdown files.

```ruby
puts "Hello, GitHub Pages!"
```
```

**ステップ4: ローカル開発環境**

```bash
# Bundlerのセットアップ（オプション）
# Gemfile
source 'https://rubygems.org'
gem 'github-pages', group: :jekyll_plugins
```

```bash
# ローカルでJekyllを実行
bundle install
bundle exec jekyll serve

# http://localhost:4000 でプレビュー
```

**移行条件:**

- [ ] _config.ymlを作成した
- [ ] ページを追加した
- [ ] ローカルで確認した（オプション）
- [ ] サイトが正しく表示されることを確認した

### フェーズ4: カスタムドメインの設定

**ステップ1: CNAMEファイルの作成**

```bash
# CNAMEファイルをリポジトリのルートに作成
echo "www.example.com" > CNAME
git add CNAME
git commit -m "Add custom domain"
git push
```

**ステップ2: DNSレコードの設定**

**Apexドメイン（example.com）の場合:**

DNSプロバイダーでAレコードを設定:

```
Type: A
Name: @
Value: 185.199.108.153
       185.199.109.153
       185.199.110.153
       185.199.111.153
```

**サブドメイン（www.example.com）の場合:**

CNAMEレコードを設定:

```
Type: CNAME
Name: www
Value: username.github.io
```

**ステップ3: GitHub設定の確認**

1. リポジトリの **Settings** → **Pages**
2. **Custom domain** にドメインを入力
3. **Enforce HTTPS** をチェック（DNSが反映された後）
4. DNS設定が反映されるまで待機（最大24時間）

**ステップ4: HTTPSの有効化**

```bash
# DNS設定後、GitHubが自動的にSSL証明書を発行
# Settings → Pages → Enforce HTTPS をチェック
```

**移行条件:**

- [ ] CNAMEファイルを作成した
- [ ] DNSレコードを設定した
- [ ] カスタムドメインが機能することを確認した
- [ ] HTTPSを有効化した

### フェーズ5: GitHub Actionsによる自動デプロイ

**ステップ1: カスタムビルドワークフロー**

静的サイトジェネレーター（Hugo、Next.js等）との統合:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

# GitHub Pagesへのデプロイ権限を設定
permissions:
  contents: read
  pages: write
  id-token: write

# 同時実行を制御
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**ステップ2: Jekyllカスタムビルド**

プラグインやカスタムテーマを使用する場合:

```yaml
# .github/workflows/jekyll.yml
name: Deploy Jekyll site to Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**ステップ3: 静的サイトジェネレーター別の例**

**Hugo:**

```yaml
# .github/workflows/hugo.yml
name: Deploy Hugo site to Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**VitePress/VuePress:**

```yaml
# .github/workflows/vitepress.yml
name: Deploy VitePress site to Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build with VitePress
        run: npm run docs:build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**移行条件:**

- [ ] ワークフローファイルを作成した
- [ ] ビルドが成功することを確認した
- [ ] デプロイが自動化されたことを確認した

### フェーズ6: 高度な設定

**ステップ1: リダイレクトの設定**

```html
<!-- 404.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        h1 { font-size: 6rem; margin: 0; }
        p { font-size: 1.5rem; }
        a {
            color: white;
            text-decoration: none;
            border: 2px solid white;
            padding: 0.5rem 2rem;
            border-radius: 5px;
            display: inline-block;
            margin-top: 1rem;
            transition: all 0.3s;
        }
        a:hover {
            background: white;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <p>Page Not Found</p>
        <p>お探しのページは見つかりませんでした。</p>
        <a href="/">ホームに戻る</a>
    </div>
</body>
</html>
```

**ステップ2: SEO最適化**

```html
<!-- headタグ内に追加 -->
<head>
    <!-- メタタグ -->
    <meta name="description" content="Site description here">
    <meta name="keywords" content="keyword1, keyword2, keyword3">
    <meta name="author" content="Your Name">

    <!-- Open Graph -->
    <meta property="og:title" content="Site Title">
    <meta property="og:description" content="Site description">
    <meta property="og:image" content="https://example.com/image.jpg">
    <meta property="og:url" content="https://example.com">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Site Title">
    <meta name="twitter:description" content="Site description">
    <meta name="twitter:image" content="https://example.com/image.jpg">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/favicon.png">
</head>
```

**Jekyllの場合:**

```yaml
# _config.ymlに追加
plugins:
  - jekyll-seo-tag
  - jekyll-sitemap
  - jekyll-feed

# ページのフロントマターに追加
---
layout: page
title: Page Title
description: Page description for SEO
image: /assets/images/og-image.jpg
---
```

**ステップ3: Google Analytics/Search Console**

```html
<!-- Google Analytics 4 -->
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>
</head>
```

**Jekyllの場合:**

```yaml
# _config.yml
google_analytics: G-XXXXXXXXXX
```

**Search Console検証:**

```html
<!-- Google Search Console verification -->
<meta name="google-site-verification" content="verification-code">
```

**ステップ4: robots.txtとsitemap.xml**

```txt
# robots.txt
User-agent: *
Allow: /
Sitemap: https://example.com/sitemap.xml
```

```xml
<!-- sitemap.xml (Jekyllは自動生成) -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2025-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

**移行条件:**

- [ ] 404ページを作成した
- [ ] SEOメタタグを追加した
- [ ] Analytics/Search Consoleを設定した
- [ ] sitemap.xmlを追加した

## 判断のポイント

### サイトタイプの選択

**ユーザー/組織サイト:**

- メインのポートフォリオ
- 個人ブログ
- 組織のメインサイト
- URL: `username.github.io`

**プロジェクトサイト:**

- プロジェクトドキュメント
- デモサイト
- 複数のプロジェクト
- URL: `username.github.io/project`

### 静的サイトジェネレーターの選択

**Jekyll:**

- GitHub Pagesネイティブサポート
- ブログに最適
- シンプルな設定
- Rubyベース

**Hugo:**

- 高速ビルド
- 豊富なテーマ
- Goベース
- GitHub Actionsが必要

**VitePress/VuePress:**

- ドキュメントサイトに最適
- Vueベース
- モダンなUI
- GitHub Actionsが必要

**Next.js/Gatsby:**

- Reactベース
- 高度な機能
- SPAサポート
- GitHub Actionsが必要

### デプロイ方法

**GitHub自動ビルド:**

- Jekyllのみ
- 設定不要
- プラグイン制限あり

**GitHub Actions:**

- 任意のツール使用可能
- カスタマイズ自由
- ビルドステップ制御可能

## よくある落とし穴

1. **baseurlの設定ミス**
   - ❌ プロジェクトサイトでbaseurlを設定しない
   - ✅ `baseurl: "/repository-name"` を設定

2. **CNAMEファイルの削除**
   - ❌ ビルド時にCNAMEが削除される
   - ✅ ビルド出力にCNAMEを含める

3. **HTTPSの強制なし**
   - ❌ HTTPで公開
   - ✅ Enforce HTTPSを有効化

4. **大きなファイルサイズ**
   - ❌ 最適化なしの画像
   - ✅ 画像圧縮・最適化

5. **ビルド時間の超過**
   - ❌ 10分以上のビルド
   - ✅ ビルド最適化・キャッシング

6. **404エラーページがない**
   - ❌ デフォルトの404ページ
   - ✅ カスタム404.htmlを作成

## 制限事項

### GitHub Pagesの制限

**サイズ制限:**

- リポジトリサイズ: 1GB推奨
- 公開サイトサイズ: 1GB
- ファイルサイズ: 100MB

**ビルド制限:**

- ビルド時間: 10分
- ビルド頻度: 1時間に10回

**トラフィック:**

- 帯域幅: 月100GB推奨
- リクエスト: 月100,000回推奨

**機能制限:**

- 静的サイトのみ（サーバーサイド処理なし）
- データベース使用不可
- サーバーサイドスクリプト不可

## トラブルシューティング

### サイトが表示されない

**確認項目:**

1. GitHub Pagesが有効になっているか確認
2. 正しいブランチ・フォルダを指定しているか確認
3. index.htmlまたはindex.mdが存在するか確認
4. ビルドエラーがないか確認（Settings → Pages）

```bash
# ローカルで確認
bundle exec jekyll serve

# ビルドエラーのチェック
bundle exec jekyll build --verbose
```

### 404エラーが発生

**原因と対処:**

1. **baseurlの設定ミス**（プロジェクトサイト）

```yaml
# _config.yml
baseurl: "/repository-name"
```

2. **リンクの絶対パス**

```html
<!-- ❌ 間違い -->
<link href="/styles.css">

<!-- ✅ 正しい -->
<link href="{{ '/styles.css' | relative_url }}">
```

### CSSやJSが読み込まれない

**対処法:**

```html
<!-- Jekyllの場合 -->
<link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
<script src="{{ '/assets/js/script.js' | relative_url }}"></script>

<!-- 静的HTMLの場合（プロジェクトサイト） -->
<link rel="stylesheet" href="/repository-name/assets/css/style.css">
```

### ビルドが失敗する

**確認項目:**

1. ワークフローログを確認
2. 依存関係のバージョンを確認
3. ビルドコマンドを確認

```yaml
# デバッグモードでビルド
- name: Build with verbose logging
  run: npm run build -- --debug
```

### カスタムドメインが機能しない

**確認手順:**

1. CNAMEファイルが存在するか確認
2. DNSレコードを確認（dig/nslookupコマンド）

```bash
# DNS確認
dig www.example.com
nslookup www.example.com

# GitHub IPアドレス確認
dig username.github.io
```

3. DNS伝播を待つ（最大24時間）
4. GitHub設定を再確認

## 検証ポイント

### 初期設定

- [ ] リポジトリを作成した
- [ ] GitHub Pagesを有効化した
- [ ] index.htmlまたはindex.mdを作成した
- [ ] サイトが公開されることを確認した

### Jekyll設定（使用する場合）

- [ ] _config.ymlを作成した
- [ ] テーマを選択した
- [ ] ページを作成した
- [ ] ローカルで確認した

### カスタムドメイン（使用する場合）

- [ ] CNAMEファイルを作成した
- [ ] DNSレコードを設定した
- [ ] HTTPSを有効化した
- [ ] ドメインが機能することを確認した

### GitHub Actions（使用する場合）

- [ ] ワークフローを作成した
- [ ] ビルドが成功することを確認した
- [ ] デプロイが自動化されたことを確認した

### 最適化

- [ ] 404ページを作成した
- [ ] SEOメタタグを追加した
- [ ] sitemap.xmlを追加した
- [ ] robots.txtを追加した

## 他スキルとの連携

### github-pages + ci-cd-setup

GitHub Actionsとの統合:

1. github-pagesでサイト作成
2. ci-cd-setupで自動デプロイ設定
3. プッシュごとに自動公開

### github-pages + documentation

ドキュメントサイトの構築:

1. documentationでドキュメント作成
2. github-pagesで公開
3. 常に最新のドキュメントを提供

### github-pages + api-design

APIドキュメントの公開:

1. api-designでAPI仕様作成
2. github-pagesでドキュメント公開
3. 開発者向けポータル構築

## GitHub Pagesのベストプラクティス

### パフォーマンス

- 画像の最適化（WebP、圧縮）
- CSSとJSの最小化
- キャッシング戦略
- CDN活用（自動）

### セキュリティ

- HTTPSの強制
- 依存関係の更新
- セキュアなリンク
- CSP設定（可能な場合）

### メンテナンス

- 定期的な依存関係更新
- リンク切れチェック
- Analytics監視
- コンテンツ更新

### アクセシビリティ

- セマンティックHTML
- alt属性の設定
- キーボードナビゲーション
- カラーコントラスト

## リソース

### 公式ドキュメント

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)

### テーマとテンプレート

- [Jekyll Themes](https://jekyllthemes.io/)
- [GitHub Pages Themes](https://pages.github.com/themes/)
- [Hugo Themes](https://themes.gohugo.io/)

### ツール

- [Jekyll](https://jekyllrb.com/)
- [Hugo](https://gohugo.io/)
- [VitePress](https://vitepress.dev/)
- [Docusaurus](https://docusaurus.io/)
