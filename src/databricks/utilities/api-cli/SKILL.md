---
name: "Databricks REST API & CLI"
description: "Databricks REST APIとCLIの活用。自動化、スクリプト、統合、ジョブ管理、クラスター操作"
---

# Databricks REST API & CLI

## Databricks CLI

### インストール・設定

```bash
# インストール
pip install databricks-cli

# 認証設定
databricks configure --token
# Host: https://your-workspace.cloud.databricks.com
# Token: dapi...
```

### ワークスペース操作

```bash
# リスト
databricks workspace ls /

# エクスポート
databricks workspace export /path/to/notebook notebook.py

# インポート
databricks workspace import notebook.py /path/to/notebook

# ディレクトリ作成
databricks workspace mkdirs /MyProject
```

### ジョブ操作

```bash
# ジョブ一覧
databricks jobs list

# ジョブ実行
databricks jobs run-now --job-id 12345

# 実行状態確認
databricks runs get --run-id 67890

# ジョブ作成
databricks jobs create --json-file job-config.json
```

### クラスター操作

```bash
# クラスター一覧
databricks clusters list

# クラスター起動
databricks clusters start --cluster-id abc-123

# クラスター停止
databricks clusters delete --cluster-id abc-123

# クラスター作成
databricks clusters create --json-file cluster-config.json
```

### Secrets管理

```bash
# スコープ作成
databricks secrets create-scope --scope my-scope

# シークレット追加
databricks secrets put --scope my-scope --key db-password

# シークレット一覧
databricks secrets list --scope my-scope
```

## REST API

### 認証

```python
import requests

workspace_url = "https://your-workspace.cloud.databricks.com"
token = "dapi..."

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

### ジョブAPI

```python
# ジョブ一覧
response = requests.get(
    f"{workspace_url}/api/2.1/jobs/list",
    headers=headers
)
jobs = response.json()["jobs"]

# ジョブ実行
payload = {"job_id": 12345}
response = requests.post(
    f"{workspace_url}/api/2.1/jobs/run-now",
    headers=headers,
    json=payload
)
run_id = response.json()["run_id"]

# 実行状態確認
response = requests.get(
    f"{workspace_url}/api/2.1/jobs/runs/get",
    headers=headers,
    params={"run_id": run_id}
)
state = response.json()["state"]
```

### クラスターAPI

```python
# クラスター作成
cluster_config = {
    "cluster_name": "API Created Cluster",
    "spark_version": "14.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "autotermination_minutes": 60
}

response = requests.post(
    f"{workspace_url}/api/2.0/clusters/create",
    headers=headers,
    json=cluster_config
)
cluster_id = response.json()["cluster_id"]
```

### SQL API (クエリ実行)

```python
# ウェアハウスでクエリ実行
from databricks import sql

connection = sql.connect(
    server_hostname=workspace_url,
    http_path="/sql/1.0/warehouses/abc123",
    access_token=token
)

cursor = connection.cursor()
cursor.execute("SELECT * FROM my_table LIMIT 10")
results = cursor.fetchall()

cursor.close()
connection.close()
```

### Unity Catalog API

```python
# カタログ一覧
response = requests.get(
    f"{workspace_url}/api/2.1/unity-catalog/catalogs",
    headers=headers
)
catalogs = response.json()["catalogs"]

# 権限付与
grant_payload = {
    "securable_type": "TABLE",
    "full_name": "catalog.schema.table",
    "principal": "user@example.com",
    "privilege": "SELECT"
}

response = requests.post(
    f"{workspace_url}/api/2.1/unity-catalog/permissions",
    headers=headers,
    json=grant_payload
)
```

## 自動化スクリプト例

```python
#!/usr/bin/env python3
# daily_job_runner.py

import requests
import time
import sys

def run_job_and_wait(job_id):
    # ジョブ実行
    response = requests.post(
        f"{workspace_url}/api/2.1/jobs/run-now",
        headers=headers,
        json={"job_id": job_id}
    )
    run_id = response.json()["run_id"]
    
    # 完了待機
    while True:
        response = requests.get(
            f"{workspace_url}/api/2.1/jobs/runs/get",
            headers=headers,
            params={"run_id": run_id}
        )
        state = response.json()["state"]["life_cycle_state"]
        
        if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            result = response.json()["state"]["result_state"]
            return result == "SUCCESS"
        
        time.sleep(30)

if __name__ == "__main__":
    success = run_job_and_wait(12345)
    sys.exit(0 if success else 1)
```

## SDK (Python)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# ジョブ一覧
jobs = w.jobs.list()
for job in jobs:
    print(f"{job.job_id}: {job.settings.name}")

# クラスター起動
w.clusters.start(cluster_id="abc-123")

# ウェアハウス作成
w.warehouses.create(
    name="Analytics Warehouse",
    cluster_size="Medium",
    max_num_clusters=3
)
```

## ベストプラクティス

1. **SDK優先** - Python SDKは型安全で使いやすい
2. **エラーハンドリング** - リトライロジック実装
3. **レート制限** - API呼び出し頻度に注意
4. **シークレット管理** - トークンをコードに埋め込まない
5. **ロギング** - API呼び出しをログに記録

## まとめ

Databricks CLI/APIで、ワークスペース操作、ジョブ管理、クラスター制御を自動化。Python SDKは型安全で推奨。CI/CDパイプラインや運用自動化に不可欠。
