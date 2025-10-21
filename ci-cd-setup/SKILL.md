---
name: "CI/CD設定"
description: "CI/CDパイプラインの設定と自動化。CI/CD、パイプライン、GitHub Actions、GitLab CI、自動デプロイに関する依頼に対応"
---

# CI/CD設定: 継続的インテグレーション/デリバリーの思考プロセス

## このスキルを使う場面

- CI/CDパイプラインの新規構築
- 既存パイプラインの改善
- 自動テストの統合
- 自動デプロイの設定
- ビルドの最適化
- セキュリティチェックの統合

## 思考プロセス

### フェーズ1: CI/CD戦略の立案

**ステップ1: 要件の理解**

何を自動化するか明確にする:

**自動化の範囲:**

- [ ] ビルド
- [ ] テスト（ユニット、統合、E2E）
- [ ] Lint/静的解析
- [ ] セキュリティスキャン
- [ ] デプロイ
- [ ] ロールバック

**環境の定義:**

- [ ] 開発環境（Development）
- [ ] ステージング環境（Staging）
- [ ] 本番環境（Production）
- [ ] デプロイ戦略（Blue-Green、Canary等）

**トリガーの定義:**

- [ ] プッシュ時
- [ ] プルリクエスト作成時
- [ ] タグ作成時
- [ ] スケジュール実行
- [ ] 手動トリガー

**ステップ2: CI/CDツールの選択**

**GitHub Actions:**

- GitHubネイティブ
- YAMLベース
- マーケットプレイス豊富
- 無料枠あり

**GitLab CI/CD:**

- GitLabネイティブ
- .gitlab-ci.yml
- Auto DevOps
- セルフホスト可能

**Jenkins:**

- オープンソース
- プラグイン豊富
- セルフホスト
- 柔軟性高い

**CircleCI, Travis CI:**

- クラウドベース
- 設定シンプル
- 並列実行

**移行条件:**

- [ ] 自動化スコープを定義した
- [ ] CI/CDツールを選択した
- [ ] デプロイ戦略を決定した

### フェーズ2: GitHub Actions の設定

**ステップ1: 基本ワークフロー**

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: dist/
```

**ステップ2: マトリックスビルド**

複数環境でテスト:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node-version: [16, 18, 20]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

      - run: npm ci
      - run: npm test
```

**ステップ3: キャッシングの活用**

ビルド時間短縮:

```yaml
steps:
  - uses: actions/checkout@v3

  - name: Cache dependencies
    uses: actions/cache@v3
    with:
      path: ~/.npm
      key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-node-

  - run: npm ci
  - run: npm test
```

**ステップ4: シークレットの管理**

```yaml
steps:
  - name: Deploy to production
    env:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    run: |
      aws s3 sync ./dist s3://my-bucket
```

**移行条件:**

- [ ] ワークフローを作成した
- [ ] テストを統合した
- [ ] キャッシングを設定した

### フェーズ3: GitLab CI/CD の設定

**ステップ1: 基本パイプライン**

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  NODE_VERSION: "18"

# キャッシュ設定
cache:
  paths:
    - node_modules/

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

test:unit:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run test:unit
  coverage: '/Coverage: \d+\.\d+%/'

test:integration:
  stage: test
  image: node:${NODE_VERSION}
  services:
    - postgres:14
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: testpass
  script:
    - npm ci
    - npm run test:integration

lint:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run lint

deploy:staging:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - curl -X POST $STAGING_DEPLOY_WEBHOOK
  only:
    - develop

deploy:production:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - curl -X POST $PRODUCTION_DEPLOY_WEBHOOK
  only:
    - main
  when: manual  # 手動承認
```

**ステップ2: Docker イメージのビルド**

```yaml
build:docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
```

**移行条件:**

- [ ] パイプラインを作成した
- [ ] ステージを定義した
- [ ] デプロイを自動化した

### フェーズ4: テストの統合

**ステップ1: ユニットテスト**

```yaml
# GitHub Actions
- name: Run unit tests
  run: |
    npm test -- --coverage
    npm run test:report

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage/coverage-final.json
```

**ステップ2: 統合テスト**

```yaml
# Docker Compose でサービス起動
services:
  postgres:
    image: postgres:14
    env:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - uses: actions/checkout@v3

  - name: Run integration tests
    env:
      DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
    run: npm run test:integration
```

**ステップ3: E2Eテスト**

```yaml
e2e-test:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright
      run: npx playwright install --with-deps

    - name: Run E2E tests
      run: npm run test:e2e

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-report
        path: playwright-report/
```

**移行条件:**

- [ ] テストを統合した
- [ ] カバレッジを測定した
- [ ] レポートを生成した

### フェーズ5: セキュリティとコード品質

**ステップ1: 静的解析**

```yaml
security:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    # 依存関係の脆弱性チェック
    - name: Run npm audit
      run: npm audit --audit-level=moderate

    # Snyk でセキュリティスキャン
    - name: Run Snyk
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

    # Semgrep で静的解析
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
```

**ステップ2: コード品質チェック**

```yaml
code-quality:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # SonarQube用

    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**ステップ3: コンテナスキャン**

```yaml
container-scan:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t myapp:${{ github.sha }} .

    - name: Run Trivy scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: myapp:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

**移行条件:**

- [ ] セキュリティチェックを統合した
- [ ] コード品質を監視した
- [ ] 脆弱性スキャンを実装した

### フェーズ6: デプロイの自動化

**ステップ1: AWS へのデプロイ**

```yaml
deploy-aws:
  runs-on: ubuntu-latest
  needs: [build-and-test]

  steps:
    - uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Deploy to S3
      run: |
        aws s3 sync ./dist s3://my-bucket --delete

    - name: Invalidate CloudFront cache
      run: |
        aws cloudfront create-invalidation \
          --distribution-id ${{ secrets.CF_DISTRIBUTION_ID }} \
          --paths "/*"
```

**ステップ2: Kubernetes へのデプロイ**

```yaml
deploy-k8s:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    - name: Set up kubectl
      uses: azure/setup-kubectl@v3

    - name: Configure kubeconfig
      run: |
        echo "${{ secrets.KUBECONFIG }}" > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/myapp \
          myapp=myregistry/myapp:${{ github.sha }}
        kubectl rollout status deployment/myapp
```

**ステップ3: Blue-Green デプロイ**

```yaml
deploy-blue-green:
  runs-on: ubuntu-latest

  steps:
    - name: Deploy to Green environment
      run: |
        # 新バージョンをGreen環境にデプロイ
        kubectl apply -f k8s/deployment-green.yaml

    - name: Wait for Green to be ready
      run: |
        kubectl wait --for=condition=available \
          deployment/myapp-green --timeout=300s

    - name: Run smoke tests
      run: |
        curl -f https://green.example.com/health || exit 1

    - name: Switch traffic to Green
      run: |
        kubectl patch service myapp \
          -p '{"spec":{"selector":{"version":"green"}}}'

    - name: Wait and verify
      run: sleep 60

    - name: Delete Blue deployment
      run: kubectl delete deployment myapp-blue
```

**移行条件:**

- [ ] デプロイを自動化した
- [ ] ロールバック手順を準備した
- [ ] 本番環境でテストした

## 判断のポイント

### デプロイ戦略の選択

**Rolling Update:**

- 段階的な置き換え
- ダウンタイムなし
- ロールバック可能

**Blue-Green:**

- 即座の切り替え
- 簡単なロールバック
- リソース2倍必要

**Canary:**

- 段階的なトラフィック移行
- リスク最小化
- 複雑な設定

### 自動 vs 手動デプロイ

**自動デプロイ:**

- 開発環境
- ステージング環境
- 高頻度リリース

**手動承認:**

- 本番環境
- 重要な変更
- コンプライアンス要件

## よくある落とし穴

1. **テストなしのデプロイ**
   - ❌ テストスキップ
   - ✅ 必ずテスト実行

2. **シークレットの平文保存**
   - ❌ コードに直接記述
   - ✅ シークレット管理

3. **ロールバック計画なし**
   - ❌ デプロイのみ
   - ✅ ロールバック手順

4. **環境の違い**
   - ❌ 本番のみ異なる設定
   - ✅ 環境の一貫性

5. **並列実行の考慮不足**
   - ❌ 競合状態
   - ✅ 適切な依存関係

6. **ログ・監視の欠如**
   - ❌ デプロイ後の状態不明
   - ✅ メトリクス・ログ収集

## 検証ポイント

### パイプライン設定

- [ ] ワークフローを作成した
- [ ] ステージを定義した
- [ ] トリガーを設定した
- [ ] キャッシングを実装した

### テストとセキュリティ

- [ ] テストを統合した
- [ ] セキュリティチェックを追加した
- [ ] カバレッジを測定した
- [ ] 脆弱性スキャンを実装した

### デプロイ

- [ ] デプロイを自動化した
- [ ] ロールバック手順を準備した
- [ ] 環境変数を設定した
- [ ] 監視を実装した

## 他スキルとの連携

### ci-cd-setup + test-automation

自動テストの統合:

1. test-automationでテスト作成
2. ci-cd-setupでパイプライン統合
3. 継続的なテスト実行

### ci-cd-setup + security-audit

セキュリティチェックの自動化:

1. security-auditで要件定義
2. ci-cd-setupでスキャン統合
3. 脆弱性の早期発見

### ci-cd-setup → dependency-management

依存関係の自動更新:

1. dependency-managementで更新検出
2. ci-cd-setupで自動テスト
3. 安全な依存関係更新

## CI/CDのベストプラクティス

### 高速なフィードバック

- 頻繁なコミット
- 早期のテスト実行
- 並列実行の活用
- キャッシングの最適化

### 信頼性

- 冪等なスクリプト
- エラーハンドリング
- リトライロジック
- ロールバック計画

### セキュリティ

- シークレット管理
- 最小権限
- 監査ログ
- 脆弱性スキャン

### 可視性

- ステータスバッジ
- 通知設定
- メトリクス収集
- ログ保存
