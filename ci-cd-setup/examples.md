# CI/CD設定: 実装例とパターン

このドキュメントでは、CI/CD設定スキルで説明されているパイプライン設定の具体例を示します。

## GitHub Actions の実装例

### Node.js プロジェクト

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16, 18, 20]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/coverage-final.json

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          npm run build
          aws s3 sync ./dist s3://my-bucket
```

## Docker イメージビルド

```yaml
build:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: myapp/myimage:${{ github.sha }},myapp/myimage:latest
        cache-from: type=registry,ref=myapp/myimage:buildcache
        cache-to: type=registry,ref=myapp/myimage:buildcache,mode=max
```

## GitLab CI の例

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: node:18
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm test

deploy:
  stage: deploy
  image: alpine:latest
  only:
    - main
  script:
    - apk add --no-cache curl
    - curl -X POST $DEPLOY_WEBHOOK
```

詳細なCI/CD設定プロセスについては、[SKILL.md](SKILL.md) を参照してください。
