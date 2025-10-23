---
name: aws-cloudtrail
description: AWS CloudTrailを使用してAPI呼び出しを監査し、ガバナンス、コンプライアンス、リスク監査を実現する方法
---

# AWS CloudTrail スキル

## 概要

AWS CloudTrailは、AWSアカウント内のAPI呼び出しを記録し、ガバナンス、コンプライアンス、運用監査、リスク監査を可能にするサービスです。90日間の無料イベント履歴と、長期保存用のCloudTrail Lakeを提供します。

### 2025年の重要なアップデート

- **CloudTrail Lake**: 最大10年間のイベント保存とSQLクエリ
- **ネットワークアクティビティイベント**: VPCエンドポイント経由のAPI記録
- **データイベント**: S3、Lambda、DynamoDBのデータアクセス記録
- **料金**: 管理イベント無料（最初の証跡）、データイベント$0.10/10万イベント

## 主な使用ケース

### 1. 基本的な証跡作成

```bash
# S3バケット作成（ログ保存用）
aws s3 mb s3://cloudtrail-logs-123456789012 --region ap-northeast-1

# バケットポリシー設定
cat > bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AWSCloudTrailAclCheck",
    "Effect": "Allow",
    "Principal": {"Service": "cloudtrail.amazonaws.com"},
    "Action": "s3:GetBucketAcl",
    "Resource": "arn:aws:s3:::cloudtrail-logs-123456789012"
  },{
    "Sid": "AWSCloudTrailWrite",
    "Effect": "Allow",
    "Principal": {"Service": "cloudtrail.amazonaws.com"},
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::cloudtrail-logs-123456789012/AWSLogs/123456789012/*",
    "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
  }]
}
EOF

aws s3api put-bucket-policy --bucket cloudtrail-logs-123456789012 --policy file://bucket-policy.json

# CloudTrail証跡作成
aws cloudtrail create-trail \
    --name organization-trail \
    --s3-bucket-name cloudtrail-logs-123456789012 \
    --is-multi-region-trail \
    --enable-log-file-validation \
    --include-global-service-events

# ロギング開始
aws cloudtrail start-logging --name organization-trail
```

### 2. CloudTrail Lake（長期保存とクエリ）

```bash
# イベントデータストアの作成
aws cloudtrail create-event-data-store \
    --name security-audit-store \
    --retention-period 2557 \
    --multi-region-enabled \
    --organization-enabled

# SQLクエリ実行
aws cloudtrail start-query \
    --query-statement "SELECT eventTime, eventName, userIdentity.principalId, sourceIPAddress FROM cloudtrail_events WHERE eventName = 'DeleteBucket' AND eventTime > '2025-01-01 00:00:00'"

# クエリ結果取得
QUERY_ID=$(aws cloudtrail start-query --query-statement "..." --query 'QueryId' --output text)
aws cloudtrail get-query-results --query-id $QUERY_ID
```

### 3. データイベントの記録（S3、Lambda）

```bash
# S3データイベントを記録
aws cloudtrail put-event-selectors \
    --trail-name organization-trail \
    --event-selectors file://event-selectors.json

# event-selectors.json
cat > event-selectors.json << 'EOF'
[{
  "ReadWriteType": "All",
  "IncludeManagementEvents": true,
  "DataResources": [{
    "Type": "AWS::S3::Object",
    "Values": ["arn:aws:s3:::sensitive-data-bucket/*"]
  },{
    "Type": "AWS::Lambda::Function",
    "Values": ["arn:aws:lambda:ap-northeast-1:123456789012:function/*"]
  }]
}]
EOF
```

### 4. CloudWatch Logs統合

```bash
# CloudWatch Logsにストリーミング
aws cloudtrail update-trail \
    --name organization-trail \
    --cloud-watch-logs-log-group-arn arn:aws:logs:ap-northeast-1:123456789012:log-group:/aws/cloudtrail:* \
    --cloud-watch-logs-role-arn arn:aws:iam::123456789012:role/CloudTrailCloudWatchLogsRole

# メトリクスフィルター（ルートユーザー使用検知）
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail \
    --filter-name RootAccountUsage \
    --filter-pattern '{ $.userIdentity.type = "Root" }' \
    --metric-transformations \
        metricName=RootAccountLoginCount,metricNamespace=CloudTrailMetrics,metricValue=1

# アラーム設定
aws cloudwatch put-metric-alarm \
    --alarm-name root-account-usage \
    --metric-name RootAccountLoginCount \
    --namespace CloudTrailMetrics \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:security-alerts
```

### 5. セキュリティ分析

```python
"""
CloudTrailログ分析
"""
import boto3
import json

cloudtrail = boto3.client('cloudtrail')

# 過去24時間のイベント検索
response = cloudtrail.lookup_events(
    LookupAttributes=[{
        'AttributeKey': 'EventName',
        'AttributeValue': 'ConsoleLogin'
    }],
    MaxResults=50
)

# ログイン失敗の検出
for event in response['Events']:
    event_data = json.loads(event['CloudTrailEvent'])
    if event_data.get('errorCode') == 'Failed authentication':
        print(f"Failed login: {event_data['userIdentity']['principalId']} at {event['EventTime']}")
```

## ベストプラクティス（2025年版）

### 1. 組織全体で有効化

```bash
# AWS Organizations全体で証跡を有効化
aws cloudtrail create-trail \
    --name org-wide-trail \
    --s3-bucket-name cloudtrail-logs-org \
    --is-organization-trail \
    --is-multi-region-trail
```

### 2. ログファイル検証

```bash
# 改ざん検知のためログファイル検証を有効化
aws cloudtrail update-trail \
    --name organization-trail \
    --enable-log-file-validation

# 検証
aws cloudtrail validate-logs \
    --trail-arn arn:aws:cloudtrail:ap-northeast-1:123456789012:trail/organization-trail \
    --start-time 2025-01-20T00:00:00Z
```

### 3. 重要イベントのアラート

```bash
# SecurityGroupの変更検知
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail \
    --filter-name SecurityGroupChanges \
    --filter-pattern '{ ($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupIngress) }' \
    --metric-transformations metricName=SecurityGroupChanges,metricNamespace=CloudTrailMetrics,metricValue=1
```

## リソース

- [CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [CloudTrail Lake](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html)
