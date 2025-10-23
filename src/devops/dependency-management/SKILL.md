---
name: "依存関係管理"
description: "パッケージ依存関係の管理と更新。依存関係、パッケージ、npm、pip、更新、脆弱性に関する依頼に対応"
---

# 依存関係管理: パッケージとライブラリの管理プロセス

## このスキルを使う場面

- 依存関係の追加・更新
- 脆弱性への対応
- バージョン競合の解決
- パッケージマネージャーの選択
- ロックファイルの管理
- 定期的なメンテナンス

## 思考プロセス

### フェーズ1: 依存関係の理解と分析

**ステップ1: 現状把握**

既存の依存関係を確認:

**依存関係の種類:**

- **直接依存**: プロジェクトが直接使用
- **間接依存**: 直接依存が使用（推移的依存）
- **開発依存**: テスト・ビルドツール等
- **本番依存**: 実行時に必要

**確認コマンド:**

```bash
# Node.js
npm list
npm list --depth=0  # 直接依存のみ
npm outdated  # 更新可能なパッケージ

# Python
pip list
pip list --outdated
pip show <package>  # パッケージ詳細

# Ruby
bundle list
bundle outdated

# Go
go list -m all
go list -u -m all
```

**ステップ2: 脆弱性チェック**

セキュリティ監査:

```bash
# Node.js
npm audit
npm audit --json  # JSON出力
npm audit fix  # 自動修正

# Python
pip-audit
safety check  # safety パッケージ

# Ruby
bundle audit

# 統合ツール
snyk test
```

**移行条件:**

- [ ] 依存関係リストを作成した
- [ ] 脆弱性を特定した
- [ ] 更新が必要なパッケージを特定した

### フェーズ2: 依存関係の追加

**ステップ1: パッケージの選定**

適切なパッケージを選ぶ:

**評価基準:**

- [ ] メンテナンス状況（最終更新日）
- [ ] ダウンロード数・人気度
- [ ] GitHub スター数
- [ ] オープンイシュー数
- [ ] ライセンス
- [ ] ドキュメント品質
- [ ] コミュニティの活発さ
- [ ] セキュリティ履歴

**ツール:**

- npmjs.com - npm パッケージ検索
- pypi.org - Python パッケージ
- rubygems.org - Ruby gem
- libraries.io - 複数言語対応

**ステップ2: インストール**

```bash
# Node.js
npm install <package>  # 本番依存
npm install --save-dev <package>  # 開発依存
npm install <package>@<version>  # バージョン指定

# Yarn
yarn add <package>
yarn add --dev <package>

# pnpm
pnpm add <package>

# Python
pip install <package>
pip install <package>==1.2.3  # バージョン固定

# Poetry
poetry add <package>
poetry add --dev <package>

# Ruby
bundle add <package>
```

**ステップ3: バージョン指定**

セマンティックバージョニング:

```json
// package.json
{
  "dependencies": {
    "express": "^4.18.0",  // 4.x.x の最新（メジャーバージョン固定）
    "lodash": "~4.17.21",  // 4.17.x の最新（マイナーバージョン固定）
    "react": "18.2.0"      // 完全固定
  }
}
```

**記号の意味:**

- `^1.2.3` - 1.x.x（破壊的変更なし）
- `~1.2.3` - 1.2.x（機能追加なし）
- `1.2.3` - 完全固定
- `*` または `latest` - 常に最新（非推奨）

```python
# requirements.txt
requests==2.31.0  # 完全固定
flask>=2.0.0,<3.0.0  # 範囲指定
django~=4.2.0  # 4.2.x
```

**移行条件:**

- [ ] パッケージを評価した
- [ ] 適切なバージョンを選択した
- [ ] 依存関係ファイルを更新した

### フェーズ3: 依存関係の更新

**ステップ1: 更新戦略の決定**

**保守的アプローチ:**

- パッチバージョンのみ自動更新
- マイナー・メジャーは手動確認
- 安定性重視

**積極的アプローチ:**

- マイナーバージョンも自動更新
- メジャーバージョンは計画的更新
- 新機能の活用

**ステップ2: 更新の実行**

```bash
# Node.js
# 1. 利用可能な更新を確認
npm outdated

# 2. package.jsonを更新（バージョン範囲内）
npm update

# 3. メジャーバージョン更新（手動）
npm install <package>@latest

# 4. 全パッケージを最新に（注意）
npm-check-updates -u
npm install

# Python
# 1. 更新可能なパッケージ確認
pip list --outdated

# 2. パッケージ更新
pip install --upgrade <package>

# 3. requirements.txt再生成
pip freeze > requirements.txt

# Poetry
poetry update  # 範囲内で更新
poetry update <package>  # 特定パッケージ

# Ruby
bundle update  # 全パッケージ
bundle update <gem>  # 特定gem
```

**ステップ3: 更新後の検証**

```bash
# テスト実行
npm test

# ビルド確認
npm run build

# 型チェック（TypeScript）
npm run type-check

# Lint
npm run lint

# E2Eテスト
npm run test:e2e
```

**移行条件:**

- [ ] 更新を実行した
- [ ] テストが通過した
- [ ] 破壊的変更がないことを確認した

### フェーズ4: 脆弱性への対応

**ステップ1: 脆弱性の評価**

重大度を確認:

```bash
# npm audit の出力例
found 3 vulnerabilities (1 moderate, 2 high)
```

**重大度レベル:**

- **Critical**: 即座に対応
- **High**: 早急に対応（数日以内）
- **Moderate**: 計画的に対応（数週間以内）
- **Low**: 次回メンテナンス時

**ステップ2: 修正の適用**

```bash
# Node.js
# 自動修正（破壊的変更なし）
npm audit fix

# 強制修正（破壊的変更含む）
npm audit fix --force

# 手動修正
npm install <vulnerable-package>@<fixed-version>

# Python
# 特定パッケージの更新
pip install --upgrade <vulnerable-package>

# Ruby
bundle update <vulnerable-gem>
```

**ステップ3: 回避策の検討**

直接修正できない場合:

**overrides/resolutions の使用:**

```json
// package.json (npm 8.3+)
{
  "overrides": {
    "vulnerable-package": "^2.0.0"
  }
}

// package.json (Yarn)
{
  "resolutions": {
    "vulnerable-package": "^2.0.0"
  }
}
```

**代替パッケージの検討:**

- メンテナンスされていない → 代替を探す
- フォークが存在 → フォークへ移行
- 機能削減 → 自作検討

**移行条件:**

- [ ] 脆弱性を修正した
- [ ] テストで検証した
- [ ] 本番環境に適用した

### フェーズ5: バージョン競合の解決

**ステップ1: 競合の特定**

```bash
# Node.js
npm ls <package>  # パッケージの依存ツリー

# 例: react が複数バージョン存在
myapp@1.0.0
├── react@18.2.0
└─┬ some-lib@1.0.0
  └── react@17.0.2  # 競合！

# Python
pip check  # 依存関係の不整合チェック
```

**ステップ2: 解決方法**

**方法1: バージョン範囲の調整**

```json
// 競合前
{
  "dependencies": {
    "package-a": "^1.0.0",  // requires lodash ^4.17.0
    "package-b": "^2.0.0"   // requires lodash ^3.10.0
  }
}

// 解決: どちらか一方を更新
{
  "dependencies": {
    "package-a": "^2.0.0",  // 新バージョン（lodash ^4対応）
    "package-b": "^2.0.0"
  }
}
```

**方法2: peer dependencies の解決**

```bash
# npm 7+ は peer dependencies を自動インストール
npm install

# エラーが出る場合は --legacy-peer-deps
npm install --legacy-peer-deps
```

**移行条件:**

- [ ] 競合を解決した
- [ ] 依存関係が整合した
- [ ] テストが通過した

### フェーズ6: 自動化と継続的メンテナンス

**ステップ1: Dependabot の設定**

```yaml
# .github/dependabot.yml
version: 2
updates:
  # npm
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "team-name"
    labels:
      - "dependencies"
    # バージョン制約
    ignore:
      - dependency-name: "react"
        versions: [">=18.0.0"]  # メジャー更新を無視

  # Python
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"
```

**ステップ2: Renovate の設定**

```json
// renovate.json
{
  "extends": ["config:base"],
  "schedule": ["before 3am on Monday"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "labels": ["major-update"],
      "automerge": false
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "schedule": ["at any time"]
  }
}
```

**ステップ3: CI/CD との統合**

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check

on:
  schedule:
    - cron: '0 0 * * 0'  # 毎週日曜日
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Check for outdated dependencies
        run: |
          npm outdated || true

      - name: Security audit
        run: |
          npm audit --audit-level=moderate

      - name: Notify
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Dependency vulnerabilities found',
              body: 'Please review and update dependencies'
            })
```

**移行条件:**

- [ ] 自動更新を設定した
- [ ] CI/CD に統合した
- [ ] 定期的な監視体制を確立した

## 判断のポイント

### いつ更新すべきか

**即座に更新:**

- Critical/High 脆弱性
- セキュリティパッチ
- バグ修正

**計画的に更新:**

- マイナーバージョン
- 新機能追加
- パフォーマンス改善

**慎重に検討:**

- メジャーバージョン
- 破壊的変更あり
- 大規模なリファクタリング必要

### ロックファイルの扱い

**コミットする:**

- 一貫性確保
- 再現性
- CI/CD で同じバージョン

**例外:**

- ライブラリの場合（アプリケーションではない）
- 常に最新を使いたい場合

## よくある落とし穴

1. **ロックファイルの無視**
   - ❌ .gitignore に追加
   - ✅ コミットして共有

2. **`npm install --force`の乱用**
   - ❌ 問題を隠蔽
   - ✅ 根本原因を解決

3. **古すぎる依存関係**
   - ❌ 数年間更新なし
   - ✅ 定期的なメンテナンス

4. **不要な依存関係**
   - ❌ 使っていないパッケージ
   - ✅ 定期的なクリーンアップ

5. **直接依存と間接依存の混同**
   - ❌ 間接依存を直接インストール
   - ✅ 必要最小限の直接依存

6. **脆弱性の放置**
   - ❌ audit の警告を無視
   - ✅ 定期的な確認と対応

## 検証ポイント

### 追加時

- [ ] パッケージを評価した
- [ ] ライセンスを確認した
- [ ] バージョンを指定した
- [ ] 依存関係を記録した

### 更新時

- [ ] 変更履歴を確認した
- [ ] 破壊的変更を確認した
- [ ] テストを実行した
- [ ] ロックファイルを更新した

### セキュリティ

- [ ] 脆弱性をチェックした
- [ ] 修正を適用した
- [ ] 再度テストした
- [ ] デプロイした

## 他スキルとの連携

### dependency-management + security-audit

セキュリティチェック:

1. security-auditで脆弱性検出
2. dependency-managementで更新
3. 継続的な監視

### dependency-management + ci-cd-setup

自動化:

1. ci-cd-setupでパイプライン設定
2. dependency-managementで定期チェック
3. 自動PR作成

### dependency-management → migration-assistant

メジャーアップグレード:

1. dependency-managementで更新検出
2. migration-assistantで移行計画
3. 段階的な更新

## 依存関係管理のベストプラクティス

### 定期的なメンテナンス

```bash
# 週次タスク
npm outdated
npm audit

# 月次タスク
npm-check-updates -u  # package.json 更新
npm install
npm test

# 四半期タスク
# メジャーバージョン更新の検討
```

### バージョン固定の使い分け

```json
// ライブラリ: 柔軟なバージョン
{
  "peerDependencies": {
    "react": "^16.8.0 || ^17.0.0 || ^18.0.0"
  }
}

// アプリケーション: 厳格なバージョン
{
  "dependencies": {
    "react": "18.2.0"
  }
}
```

### 不要な依存関係の削除

```bash
# 使われていないパッケージを検出
npx depcheck

# 削除
npm uninstall <package>
```

### ライセンスチェック

```bash
# ライセンス一覧
npx license-checker --summary

# 特定ライセンスを除外
npx license-checker --exclude "MIT, Apache-2.0"
```
