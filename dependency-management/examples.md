# 依存関係管理: 実装例とパターン

このドキュメントでは、依存関係管理スキルで説明されているパッケージ管理の具体例を示します。

## package.json の例

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0",
    "react": "18.2.0",
    "lodash": "~4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  },
  "overrides": {
    "vulnerable-package": "^2.0.0"
  }
}
```

## Dependabot 設定

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    ignore:
      - dependency-name: "react"
        versions: [">=18.0.0"]
```

## 脆弱性チェックスクリプト

```bash
#!/bin/bash
# check-vulnerabilities.sh

echo "Checking for vulnerabilities..."

# npm audit
npm audit --audit-level=moderate

if [ $? -ne 0 ]; then
  echo "Vulnerabilities found!"
  npm audit fix

  echo "Please review the changes and test."
  exit 1
fi

echo "No vulnerabilities found."
```

## 依存関係更新ワークフロー

```yaml
# .github/workflows/dependency-update.yml
name: Dependency Update

on:
  schedule:
    - cron: '0 0 * * 0'  # 毎週日曜日

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Update dependencies
        run: |
          npm outdated
          npm update

      - name: Run tests
        run: npm test

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: update dependencies'
          title: 'Dependency Updates'
          body: 'Automated dependency updates'
```

詳細な依存関係管理プロセスについては、[SKILL.md](SKILL.md) を参照してください。
