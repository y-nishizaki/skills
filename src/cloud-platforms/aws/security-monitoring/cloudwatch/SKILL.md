---
name: aws-cloudwatch
description: AWS CloudWatchを使用してメトリクス、ログ、アラーム、ダッシュボードでAWSリソースを監視し、CloudWatch InsightsとApplication Signalsで詳細分析を行う方法
---

# AWS CloudWatch スキル

## 概要

Amazon CloudWatchは、AWSリソースとアプリケーションをリアルタイムで監視するフルマネージドサービスです。メトリクス、ログ、アラーム、ダッシュボードを統合し、システムの可観測性を実現します。

### 2025年の重要なアップデート

- **Application Signals**: アプリケーションパフォーマンス自動監視
- **CloudWatch Logs Insights**: SQLライクなクエリで高速ログ分析
- **クロスアカウント監視**: 統合ダッシュボード
- **料金**: メトリクス$0.30/個/月、ログ$0.50/GB

## 主な使用ケース

### 1. メトリクスとアラーム

```bash
# EC2 CPU使用率アラーム
aws cloudwatch put-metric-alarm \
    --alarm-name high-cpu-utilization \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:ops-alerts

# カスタムメトリクスの送信
aws cloudwatch put-metric-data \
    --namespace "CustomApp/Metrics" \
    --metric-name OrdersProcessed \
    --value 150 \
    --timestamp $(date -u +"%Y-%m-%dT%H:%M:%S") \
    --dimensions AppName=OrderProcessor,Environment=Production
```

### 2. CloudWatch Logs

```bash
# ロググループの作成
aws logs create-log-group --log-group-name /aws/application/web-server

# ログストリームの作成
aws logs create-log-stream \
    --log-group-name /aws/application/web-server \
    --log-stream-name instance-001

# ログイベントの送信
aws logs put-log-events \
    --log-group-name /aws/application/web-server \
    --log-stream-name instance-001 \
    --log-events timestamp=$(date +%s000),message="Application started successfully"

# メトリクスフィルター（エラーカウント）
aws logs put-metric-filter \
    --log-group-name /aws/application/web-server \
    --filter-name ErrorCount \
    --filter-pattern "[time, request_id, level = ERROR*, ...]" \
    --metric-transformations \
        metricName=ApplicationErrors,metricNamespace=CustomApp,metricValue=1
```

### 3. CloudWatch Logs Insights

```sql
-- エラーログの分析
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
| sort @timestamp desc

-- レイテンシ分析
fields @timestamp, responseTime
| filter responseTime > 1000
| stats avg(responseTime), max(responseTime), count() by endpoint
| sort avg(responseTime) desc

-- トップN分析
fields @timestamp, userId, action
| stats count() as actionCount by userId
| sort actionCount desc
| limit 10
```

### 4. ダッシュボード

```python
"""
CloudWatchダッシュボード作成
"""
import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "ap-northeast-1",
                "title": "EC2 CPU Utilization"
            }
        },
        {
            "type": "log",
            "properties": {
                "query": "SOURCE '/aws/application/web-server' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
                "region": "ap-northeast-1",
                "title": "Recent Errors"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='ApplicationMonitoring',
    DashboardBody=json.dumps(dashboard_body)
)
```

### 5. CloudWatch Agent（詳細メトリクス）

```bash
# CloudWatch Agentのインストール
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# 設定ファイル
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << 'EOF'
{
  "metrics": {
    "namespace": "CustomApp",
    "metrics_collected": {
      "mem": {
        "measurement": [{"name": "mem_used_percent"}],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [{"name": "used_percent"}],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [{
          "file_path": "/var/log/application.log",
          "log_group_name": "/aws/application/web-server",
          "log_stream_name": "{instance_id}"
        }]
      }
    }
  }
}
EOF

# Agent起動
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

## ベストプラクティス（2025年版）

### 1. 複合アラーム

```bash
# CPU高 AND ディスク高
aws cloudwatch put-composite-alarm \
    --alarm-name critical-resource-usage \
    --alarm-rule "ALARM(high-cpu-alarm) AND ALARM(high-disk-alarm)" \
    --actions-enabled \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:critical-alerts
```

### 2. Anomaly Detection

```bash
# 異常検知アラーム
aws cloudwatch put-metric-alarm \
    --alarm-name api-requests-anomaly \
    --metric-name RequestCount \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold-metric-id e1 \
    --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
    --metrics '[
        {"Id":"m1","ReturnData":true,"MetricStat":{"Metric":{"Namespace":"AWS/ApplicationELB","MetricName":"RequestCount"},"Period":300,"Stat":"Sum"}},
        {"Id":"e1","Expression":"ANOMALY_DETECTION_BAND(m1,2)"}
    ]'
```

### 3. ログ保持期間の最適化

```bash
# 古いログを削除してコスト削減
aws logs put-retention-policy \
    --log-group-name /aws/application/web-server \
    --retention-in-days 30
```

## リソース

- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
