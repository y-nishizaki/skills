---
name: "security-monitoring"
description: >
  セキュリティ監視（SOC/Blue Team）の実装を支援します。SIEM（Splunk、ELK、QRadar）のログ分析、
  インシデント検知・対応、攻撃チェーン（Cyber Kill Chain、MITRE ATT&CK）の理解、
  脅威ハンティング、アラートチューニングなど、防御側のセキュリティ運用に使用します。
  キーワード - SOC、Blue Team、SIEM、ログ分析、インシデント検知、MITRE ATT&CK、脅威ハンティング。
version: 1.0.0
---

# セキュリティ監視スキル

## 目的

このスキルは、セキュリティオペレーションセンター（SOC）とBlue Teamの活動を支援するための
包括的な知識を提供します。SIEM、ログ分析、インシデント検知・対応、脅威ハンティングなど、
防御側のセキュリティ運用に必要な実践的スキルを含みます。

## このスキルを使用する場合

- SOC構築やセキュリティ監視体制の強化を求めた場合
- SIEMの導入や運用、ログ分析を必要とする場合
- インシデント検知・対応プロセスを構築したい場合
- MITRE ATT&CKフレームワークの活用を検討している場合
- 脅威ハンティングの実施を求めた場合

## SIEM（Security Information and Event Management）

### Splunk

基本的な検索クエリ（SPL）:

```spl
# 失敗したログイン試行
index=security EventCode=4625 | stats count by src_ip, user

# 高頻度の接続試行
index=firewall action=denied | stats count by src_ip | where count > 100

# タイムチャート
index=web status=500 | timechart span=1h count

# 統計とソート
index=* sourcetype=access_combined | top limit=20 clientip

# サブサーチ
index=security [search index=threats | fields malicious_ip | rename malicious_ip as src_ip]

# トランザクション分析
index=web | transaction session_id maxspan=30m | where duration > 1800
```

### Elastic Stack (ELK)

Elasticsearch クエリ（KQL/Lucene）:

```json
# KQL クエリ
event.code: 4625 AND event.outcome: failure

# 複雑な検索
source.ip: 192.168.1.0/24 AND event.action: (denied OR blocked)

# 時間範囲とフィルタ
@timestamp >= "now-24h" AND process.name: powershell.exe AND event.type: process_start

# 集計クエリ (Elasticsearch DSL)
{
  "query": {
    "bool": {
      "must": [
        { "match": { "event.category": "authentication" }},
        { "match": { "event.outcome": "failure" }}
      ],
      "filter": [
        { "range": { "@timestamp": { "gte": "now-1h" }}}
      ]
    }
  },
  "aggs": {
    "failed_logins_by_user": {
      "terms": { "field": "user.name", "size": 10 }
    }
  }
}
```

Logstash設定例:

```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => { "message" => "%{SYSLOGLINE}" }
    }
    date {
      match => [ "timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }
  }

  if [source_ip] {
    geoip {
      source => "source_ip"
      target => "geoip"
    }
  }

  # 脅威インテリジェンス統合
  translate {
    field => "[source][ip]"
    destination => "[threat][indicator]"
    dictionary_path => "/etc/logstash/threat_intel.yml"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

## MITRE ATT&CK

### 主要なタクティクス（戦術）

1. **Initial Access（初期アクセス）**
   - フィッシング
   - 公開アプリケーションの悪用
   - 外部リモートサービス

2. **Execution（実行）**
   - コマンド/スクリプトインタープリター
   - ユーザー実行
   - スケジュールタスク

3. **Persistence（永続化）**
   - ブート/ログオン自動起動
   - スケジュールタスク
   - アカウント操作

4. **Privilege Escalation（権限昇格）**
   - プロセスインジェクション
   - アクセストークン操作
   - 脆弱性悪用

5. **Defense Evasion（防御回避）**
   - プロセスインジェクション
   - 難読化
   - ログ削除

6. **Credential Access（認証情報アクセス）**
   - OS認証情報ダンピング
   - ブルートフォース
   - 入力キャプチャ

7. **Discovery（探索）**
   - アカウント探索
   - ファイル/ディレクトリ探索
   - ネットワークサービススキャン

8. **Lateral Movement（横展開）**
   - リモートサービス
   - 内部スピアフィッシング
   - 代替認証材料の使用

9. **Collection（収集）**
   - データステージング
   - 入力キャプチャ
   - クリップボードデータ

10. **Command and Control（C2）**
    - アプリケーション層プロトコル
    - 暗号化チャネル
    - プロトコルトンネリング

11. **Exfiltration（持ち出し）**
    - C2チャネル経由の持ち出し
    - 代替プロトコル経由の持ち出し
    - 物理メディア経由

12. **Impact（影響）**
    - データ暗号化（ランサムウェア）
    - サービス拒否
    - データ破壊

### MITRE ATT&CK検出ルール例

Windowsイベントログベースの検出:

```yaml
# Mimikatz検出
title: Credential Dumping via Mimikatz
id: a642964e-bead-4bed-8910-1bb4d63e3b4d
status: stable
description: Detects credential dumping activity using Mimikatz
references:
    - https://attack.mitre.org/techniques/T1003/
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4656
        ObjectType: 'Process'
        ProcessName|contains: 'lsass.exe'
    condition: selection
falsepositives:
    - Legitimate administrative activity
level: high
tags:
    - attack.credential_access
    - attack.t1003

# PowerShell Empire検出
title: PowerShell Empire Activity
id: b89d1fb4-2309-4e58-91e8-5fd5b72e2e45
logsource:
    product: windows
    service: powershell
detection:
    keywords:
        - 'System.Net.WebClient'
        - 'DownloadString'
        - 'IEX'
        - 'Invoke-Expression'
    condition: keywords
level: high
tags:
    - attack.execution
    - attack.t1059.001
```

## インシデント検知と対応

### インシデント対応フレームワーク (NIST)

1. **準備（Preparation）**
   - ツールとプロセスの整備
   - チーム編成とトレーニング
   - 連絡先リストの作成

2. **検知と分析（Detection & Analysis）**
   - アラート監視
   - ログ分析
   - 影響範囲の特定

3. **封じ込め、根絶、復旧（Containment, Eradication & Recovery）**
   - 短期封じ込め：ネットワーク隔離
   - 長期封じ込め：パッチ適用
   - 根絶：マルウェア削除、脆弱性修正
   - 復旧：システム復元、監視

4. **事後活動（Post-Incident Activity）**
   - 教訓の文書化
   - プロセス改善
   - 報告書作成

### アラート分類とトリアージ

```python
class AlertClassification:
    SEVERITY = {
        'Critical': {'score': 10, 'response_time': '15min'},
        'High': {'score': 7-9, 'response_time': '1hour'},
        'Medium': {'score': 4-6, 'response_time': '4hours'},
        'Low': {'score': 1-3, 'response_time': '24hours'},
        'Info': {'score': 0, 'response_time': 'best_effort'}
    }

    def classify_alert(self, alert):
        score = 0

        # MITRE タクティクス
        if alert.get('tactic') in ['Impact', 'Exfiltration']:
            score += 4
        elif alert.get('tactic') in ['Lateral Movement', 'Credential Access']:
            score += 3

        # 資産の重要度
        if alert.get('asset_criticality') == 'critical':
            score += 3
        elif alert.get('asset_criticality') == 'high':
            score += 2

        # 信頼性
        if alert.get('confidence') == 'high':
            score += 2
        elif alert.get('confidence') == 'medium':
            score += 1

        # 影響範囲
        if alert.get('affected_hosts', 0) > 10:
            score += 2

        return self._get_severity(score)

    def _get_severity(self, score):
        if score >= 10:
            return 'Critical'
        elif score >= 7:
            return 'High'
        elif score >= 4:
            return 'Medium'
        elif score >= 1:
            return 'Low'
        else:
            return 'Info'
```

## 脅威ハンティング

### 仮説駆動型ハンティング

プロセス:
1. 仮説の策定
2. データ収集と調査
3. パターン分析
4. 検証
5. 検出ルール化

仮説例:

```
仮説: 攻撃者がPowerShellを使用してC2通信を行っている

調査クエリ:
- PowerShell実行の異常なパターン
- 外部への通信を行うPowerShellプロセス
- Base64エンコードされたコマンド
- ダウンロードクレードルの使用

検証:
1. プロセスツリー分析
2. ネットワーク接続の確認
3. スクリプト内容の確認
4. 実行元の特定
```

### ハンティングクエリ例

Splunk SPL:

```spl
# 異常なPowerShell実行
index=windows EventCode=4688 NewProcessName=*powershell.exe
| rex field=CommandLine "-e(?:nc)?\s+(?<encoded>[A-Za-z0-9+/=]{50,})"
| where isnotnull(encoded)
| table _time, Computer, User, CommandLine

# Beaconing検出（定期的なC2通信）
index=proxy
| bin _time span=1m
| stats count by _time, src_ip, dest_ip
| eventstats avg(count) as avg_count, stdev(count) as stdev_count
| where count > (avg_count + (2*stdev_count))
```

Elasticsearch:

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "event.category": "process" }},
        { "match": { "process.name": "powershell.exe" }}
      ],
      "should": [
        { "wildcard": { "process.command_line": "*-enc*" }},
        { "wildcard": { "process.command_line": "*-e *" }},
        { "wildcard": { "process.command_line": "*IEX*" }},
        { "wildcard": { "process.command_line": "*Invoke-Expression*" }}
      ],
      "minimum_should_match": 1
    }
  }
}
```

## ログソースと収集

### 重要なログソース

**Windows:**
- Security (Event ID 4624, 4625, 4672, 4688, etc.)
- System
- Application
- PowerShell Operational
- Sysmon

**Linux:**
- /var/log/auth.log または /var/log/secure
- /var/log/syslog
- /var/log/messages
- Auditd logs

**ネットワーク:**
- Firewall logs
- IDS/IPS alerts
- Proxy logs
- DNS logs
- NetFlow/IPFIX

**アプリケーション:**
- Web server logs (Apache, Nginx, IIS)
- Database audit logs
- Cloud service logs (AWS CloudTrail, Azure Activity Log)

### Sysmon設定

```xml
<Sysmon schemaversion="4.82">
  <EventFiltering>
    <!-- プロセス作成 -->
    <RuleGroup name="ProcessCreate" groupRelation="or">
      <ProcessCreate onmatch="include">
        <Image condition="contains">powershell.exe</Image>
        <Image condition="contains">cmd.exe</Image>
        <Image condition="contains">wscript.exe</Image>
        <Image condition="contains">cscript.exe</Image>
      </ProcessCreate>
    </RuleGroup>

    <!-- ネットワーク接続 -->
    <RuleGroup name="NetworkConnect" groupRelation="or">
      <NetworkConnect onmatch="include">
        <Image condition="contains">powershell.exe</Image>
        <Image condition="contains">rundll32.exe</Image>
      </NetworkConnect>
    </RuleGroup>

    <!-- ファイル作成 -->
    <RuleGroup name="FileCreate" groupRelation="or">
      <FileCreate onmatch="include">
        <TargetFilename condition="contains">\Start Menu\</TargetFilename>
        <TargetFilename condition="contains">\Startup\</TargetFilename>
      </FileCreate>
    </RuleGroup>
  </EventFiltering>
</Sysmon>
```

## ベストプラクティス

### SOC運用

1. **段階的エスカレーション**
   - L1: 初期トリアージ、既知の脅威対応
   - L2: 詳細分析、複雑なインシデント
   - L3: 高度な脅威ハンティング、フォレンジック

2. **プレイブック**
   - 標準化された対応手順
   - ランブックの作成
   - 定期的な更新

3. **メトリクス**
   - MTTD（Mean Time To Detect）
   - MTTR（Mean Time To Respond）
   - アラート量
   - 誤検知率

4. **継続的改善**
   - アラートチューニング
   - プロセス改善
   - スキル向上

## 参考リソース

- MITRE ATT&CK Navigator
- NIST SP 800-61: Computer Security Incident Handling Guide
- SANS SOC Survey
- Sigma Rules Repository

## 注意事項

- ログの適切な保管期間設定
- プライバシーと法規制の遵守
- 誤検知の最小化
- 定期的なプレイブックの見直し
