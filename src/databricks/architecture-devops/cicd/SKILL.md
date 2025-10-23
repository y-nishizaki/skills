---
name: "Databricks CI/CDパイプライン"
description: "Databricks向けCI/CD構築。Git統合、自動テスト、デプロイメント、環境管理、GitHub Actions/Azure DevOps"
---

# Databricks CI/CDパイプライン

## Git統合 (Databricks Repos)

### リポジトリ接続

```python
# Repos UI または CLI
databricks repos create \
  --url https://github.com/org/repo \
  --provider github \
  --path /Repos/Production/my-project
```

### ブランチ戦略

```
main     → 本番環境
staging  → ステージング環境
develop  → 開発環境
feature/* → 機能開発
```

## GitHub Actions CI/CD

```yaml
# .github/workflows/databricks-ci.yml
name: Databricks CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest
      
      - name: Run tests
        run: pytest tests/
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Databricks CLI
        run: pip install databricks-cli
      
      - name: Deploy to Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          # ノートブック更新
          databricks repos update \
            --path /Repos/Production/my-project \
            --branch main
          
          # ジョブ実行
          databricks jobs run-now --job-id 12345
```

## 環境管理

### 環境別設定

```python
# config/dev.yaml
workspace_url: "https://dev.cloud.databricks.com"
catalog: "dev"
cluster:
  node_type: "i3.xlarge"
  num_workers: 2

# config/prod.yaml
workspace_url: "https://prod.cloud.databricks.com"
catalog: "prod"
cluster:
  node_type: "i3.2xlarge"
  num_workers: 8
```

### パラメーター管理

```python
# Databricks Widgets で環境変数
dbutils.widgets.text("env", "dev")
env = dbutils.widgets.get("env")

# 環境別カタログ
catalog = f"{env}_catalog"
spark.sql(f"USE CATALOG {catalog}")
```

## 自動テスト

```python
# tests/test_etl.py
import pytest
from pyspark.sql import SparkSession

def test_data_transformation():
    spark = SparkSession.builder.getOrCreate()
    
    # テストデータ
    test_df = spark.createDataFrame([
        (1, "Alice", 30),
        (2, "Bob", 25)
    ], ["id", "name", "age"])
    
    # 変換実行
    result_df = transform_data(test_df)
    
    # アサーション
    assert result_df.count() == 2
    assert "age_group" in result_df.columns
```

## デプロイメント戦略

### Blue-Green デプロイ

```python
# 新バージョンを並行デプロイ
# Jobを新クラスターで実行
# 検証後、トラフィック切り替え
```

### カナリアデプロイ

```python
# 一部トラフィックを新バージョンに
# エラー率監視
# 段階的に全トラフィック移行
```

## ベストプラクティス

1. **Git連携** - Repos で全コードをバージョン管理
2. **自動テスト** - PR時に必ずテスト実行
3. **環境分離** - dev/staging/prod を明確に分離
4. **シークレット管理** - Databricks Secrets 使用
5. **ロールバック計画** - 問題発生時の復旧手順

## まとめ

Databricks ReposとCI/CDツール統合で、コードのバージョン管理、自動テスト、自動デプロイを実現。環境分離とシークレット管理で、安全な本番運用が可能。
