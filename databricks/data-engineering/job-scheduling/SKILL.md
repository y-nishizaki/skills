---
name: "Databricks Workflows ジョブスケジューリング"
description: "Databricks Workflowsによるジョブスケジューリング。タスク依存関係、条件分岐、トリガー設定、エラーハンドリング、運用監視"
---

# Databricks Workflows ジョブスケジューリング

## このスキルを使う場面

- データパイプラインを定期実行したい
- タスク間の依存関係を管理したい
- 条件分岐やループ処理が必要
- イベントベースのトリガーを設定したい
- ジョブの監視・アラートを設定したい

## Lakeflow Jobs 基礎

**3つの主要概念**:
1. **Jobs** - 操作の調整・スケジューリング・実行
2. **Tasks** - ジョブ内の個別の実行単位
3. **Triggers** - 時間ベースまたはイベントベースの起動

## タスクタイプ

```python
# Notebookタスク
# UIまたはJSONで設定
{
  "task_key": "etl_task",
  "notebook_task": {
    "notebook_path": "/Workspace/ETL/process_data",
    "base_parameters": {"date": "{{job.start_time.date}}"}
  }
}

# Python Script タスク
{
  "task_key": "python_task",
  "python_script_task": {
    "script_path": "/Workspace/scripts/process.py"
  }
}

# SQLタスク
{
  "task_key": "sql_task",
  "sql_task": {
    "query": "SELECT * FROM my_table WHERE date = '{{job.start_time.date}}'"
  }
}

# DLTタスク
{
  "task_key": "dlt_pipeline",
  "pipeline_task": {
    "pipeline_id": "abc123"
  }
}
```

## タスク依存関係 (DAG)

### 基本的な依存関係

```json
{
  "tasks": [
    {
      "task_key": "extract",
      "notebook_task": {...}
    },
    {
      "task_key": "transform",
      "depends_on": [{"task_key": "extract"}],
      "notebook_task": {...}
    },
    {
      "task_key": "load",
      "depends_on": [{"task_key": "transform"}],
      "notebook_task": {...}
    }
  ]
}
```

### 並列実行

```json
{
  "tasks": [
    {"task_key": "extract", ...},
    {
      "task_key": "transform_a",
      "depends_on": [{"task_key": "extract"}],
      ...
    },
    {
      "task_key": "transform_b",
      "depends_on": [{"task_key": "extract"}],
      ...
    },
    {
      "task_key": "merge",
      "depends_on": [
        {"task_key": "transform_a"},
        {"task_key": "transform_b"}
      ],
      ...
    }
  ]
}
```

## 条件分岐

### Run If 条件

```json
{
  "task_key": "cleanup",
  "depends_on": [{"task_key": "process"}],
  "run_if": "AT_LEAST_ONE_SUCCEEDED",
  "notebook_task": {...}
}
```

**Run If オプション**:
- `ALL_SUCCEEDED` - すべての依存タスクが成功 (デフォルト)
- `AT_LEAST_ONE_SUCCEEDED` - 少なくとも1つが成功
- `NONE_FAILED` - 失敗したタスクがない
- `ALL_DONE` - すべてのタスクが完了 (成功/失敗問わず)

### If/Elseタスク

```json
{
  "task_key": "check_data",
  "condition_task": {
    "left": "{{tasks.extract.values.row_count}}",
    "op": "GREATER_THAN",
    "right": "0"
  }
},
{
  "task_key": "process_data",
  "depends_on": [{"task_key": "check_data", "outcome": "true"}],
  ...
},
{
  "task_key": "send_alert",
  "depends_on": [{"task_key": "check_data", "outcome": "false"}],
  ...
}
```

### For Eachループ

```json
{
  "task_key": "process_partitions",
  "for_each_task": {
    "inputs": "[\"2025-01-01\", \"2025-01-02\", \"2025-01-03\"]",
    "task": {
      "task_key": "process_date",
      "notebook_task": {
        "notebook_path": "/ETL/process",
        "base_parameters": {"date": "{{input}}"}
      }
    }
  }
}
```

## トリガー設定

### スケジュールトリガー

```json
{
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "Asia/Tokyo",
    "pause_status": "UNPAUSED"
  }
}
```

**Cron式の例**:
- `0 0 2 * * ?` - 毎日 2:00
- `0 0 */6 * * ?` - 6時間ごと
- `0 0 9 ? * MON-FRI` - 平日 9:00

### ファイル到着トリガー

```json
{
  "file_arrival": {
    "url": "s3://bucket/incoming-data/",
    "min_time_between_triggers_seconds": 3600
  }
}
```

## パラメーター渡し

```python
# ノートブック内でパラメーター受け取り
dbutils.widgets.text("date", "2025-01-01")
date = dbutils.widgets.get("date")

# 次のタスクにパラメーター渡し
dbutils.jobs.taskValues.set("row_count", row_count)

# 別タスクで値を取得
row_count = dbutils.jobs.taskValues.get("extract", "row_count")
```

## エラーハンドリング

```json
{
  "max_retries": 3,
  "retry_on_timeout": true,
  "timeout_seconds": 3600,
  "email_notifications": {
    "on_failure": ["team@example.com"],
    "no_alert_for_skipped_runs": true
  }
}
```

## 運用監視

### ジョブ実行履歴の確認

```python
# Jobs API でジョブ履歴取得
import requests

workspace_url = "https://your-workspace.cloud.databricks.com"
token = dbutils.secrets.get("scope", "token")

response = requests.get(
    f"{workspace_url}/api/2.1/jobs/runs/list",
    headers={"Authorization": f"Bearer {token}"},
    params={"job_id": 123, "limit": 20}
)
```

## ベストプラクティス

1. **タスク粒度** - 1タスク1責務で再利用性向上
2. **エラーハンドリング** - リトライと通知を適切に設定
3. **パラメーター化** - ハードコードを避け、柔軟性を確保
4. **監視** - アラートとログを定期確認
5. **依存関係の最小化** - 並列実行を最大化

## まとめ

Databricks Workflowsは、DAGベースのタスク依存関係管理、条件分岐、ループ、柔軟なトリガーを提供し、複雑なデータパイプラインを効率的に運用できる。
