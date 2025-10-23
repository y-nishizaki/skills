---
name: "devsecops"
description: >
  DevSecOpsの実践を支援します。セキュリティをCI/CDパイプラインに統合、SAST、DAST、SCA、
  IaCスキャン、コンテナセキュリティ、シフトレフト、セキュリティゲート設計など、
  開発ライフサイクル全体のセキュリティ統合に使用します。
  キーワード - DevSecOps、SAST、DAST、SCA、CI/CD、シフトレフト、セキュリティゲート。
version: 1.0.0
---

# DevSecOpsスキル

## 目的

このスキルは、開発ライフサイクルにセキュリティを統合するDevSecOpsの実践を支援します。
CI/CDパイプラインへのセキュリティツール組み込み、自動化されたセキュリティテスト、
継続的なコンプライアンス監視など、セキュアな開発プロセスの確立に必要な知識を含みます。

## DevSecOps原則

1. **シフトレフト（Shift Left）**
   - 開発初期段階からセキュリティを考慮
   - 早期発見・早期修正

2. **自動化（Automation）**
   - セキュリティテストの自動化
   - 継続的なスキャン

3. **継続的モニタリング**
   - 本番環境の監視
   - リアルタイム脅威検出

4. **協働（Collaboration）**
   - Dev、Sec、Ops の緊密な連携
   - 共有責任モデル

## CI/CDセキュリティパイプライン

### パイプライン設計

```yaml
# GitLab CI/CD セキュリティパイプライン例

stages:
  - build
  - test
  - security
  - deploy

# SAST (Static Application Security Testing)
sast:
  stage: security
  script:
    - semgrep --config=auto .
    - bandit -r app/
  artifacts:
    reports:
      sast: gl-sast-report.json

# SCA (Software Composition Analysis)
dependency_scanning:
  stage: security
  script:
    - safety check -r requirements.txt
    - npm audit
  artifacts:
    reports:
      dependency_scanning: gl-dependency-scanning-report.json

# Secret Scanning
secret_detection:
  stage: security
  script:
    - trufflehog filesystem .
    - gitleaks detect --source=.

# IaC Scanning
iac_scanning:
  stage: security
  script:
    - checkov -d terraform/
    - tfsec terraform/

# Container Scanning
container_scanning:
  stage: security
  script:
    - trivy image $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# DAST (Dynamic Application Security Testing)
dast:
  stage: security
  script:
    - zap-baseline.py -t http://app-staging
  artifacts:
    reports:
      dast: gl-dast-report.json

# Security Gate
security_gate:
  stage: security
  script:
    - python check_vulnerabilities.py --threshold high
  allow_failure: false
```

### GitHub Actions例

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      # SAST
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1

      # Secret Scanning
      - name: Gitleaks
        uses: zricethezav/gitleaks-action@master

      # Dependency Check
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'myapp'
          path: '.'
          format: 'ALL'

      # Container Scan
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:latest'
          severity: 'CRITICAL,HIGH'
```

## SAST（静的アプリケーションセキュリティテスト）

### ツール

**SonarQube:**
```bash
# スキャン実行
sonar-scanner \
  -Dsonar.projectKey=myproject \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=token

# Quality Gate確認
curl -u token: \
  "http://localhost:9000/api/qualitygates/project_status?projectKey=myproject"
```

**Semgrep:**
```bash
# ルール指定スキャン
semgrep --config=p/owasp-top-ten .

# カスタムルール
semgrep --config=custom-rules.yaml src/
```

**Bandit（Python）:**
```bash
# プロジェクトスキャン
bandit -r myproject/

# 設定ファイル使用
bandit -r myproject/ -c .bandit.yaml

# JSON出力
bandit -r myproject/ -f json -o bandit-report.json
```

## DAST（動的アプリケーションセキュリティテスト）

### OWASP ZAP

```bash
# Baseline Scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://www.example.com \
  -r zap-report.html

# Full Scan
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://www.example.com \
  -r zap-full-report.html

# API Scan
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t https://api.example.com/openapi.json \
  -f openapi \
  -r zap-api-report.html
```

### Burp Suite Enterprise

```python
# Burp Suite Enterprise API
import requests

# スキャン開始
response = requests.post(
    'https://burp-enterprise/api/v0.1/scan',
    headers={'Authorization': f'Bearer {api_key}'},
    json={
        'site_id': 'site-123',
        'scan_configuration_ids': ['config-456']
    }
)

scan_id = response.json()['id']

# スキャン状態確認
status = requests.get(
    f'https://burp-enterprise/api/v0.1/scan/{scan_id}',
    headers={'Authorization': f'Bearer {api_key}'}
)
```

## SCA（ソフトウェア構成分析）

### 依存関係スキャン

**Snyk:**
```bash
# プロジェクトテスト
snyk test

# 修正可能な脆弱性を自動修正
snyk wizard

# コンテナイメージテスト
snyk container test nginx:latest

# IaC スキャン
snyk iac test terraform/
```

**OWASP Dependency-Check:**
```bash
# Mavenプロジェクト
mvn org.owasp:dependency-check-maven:check

# Gradleプロジェクト
gradle dependencyCheckAnalyze

# スタンドアロン
dependency-check --project myapp --scan ./lib
```

**npm audit / yarn audit:**
```bash
# 脆弱性チェック
npm audit

# 自動修正
npm audit fix

# 詳細レポート
npm audit --json > audit-report.json
```

## シークレット管理

### シークレット検出

**TruffleHog:**
```bash
# リポジトリスキャン
trufflehog git https://github.com/org/repo

# ファイルシステムスキャン
trufflehog filesystem /path/to/code

# Docker イメージスキャン
trufflehog docker --image myimage:latest
```

**Gitleaks:**
```bash
# ローカルリポジトリスキャン
gitleaks detect --source .

# 設定ファイル使用
gitleaks detect --config .gitleaks.toml

# プリコミットフック
gitleaks protect --staged
```

### シークレット管理ソリューション

**HashiCorp Vault:**
```bash
# シークレット保存
vault kv put secret/myapp/config \
  db_password="SecureP@ss"

# シークレット取得
vault kv get secret/myapp/config

# 動的シークレット（DBクレデンシャル）
vault read database/creds/my-role
```

**AWS Secrets Manager:**
```bash
# シークレット作成
aws secretsmanager create-secret \
  --name myapp/db-password \
  --secret-string "SecureP@ss"

# シークレット取得
aws secretsmanager get-secret-value \
  --secret-id myapp/db-password
```

## コンテナセキュリティ

### イメージスキャン

**Trivy:**
```bash
# 脆弱性スキャン
trivy image nginx:latest

# 設定ミススキャン
trivy config Dockerfile

# K8s マニフェストスキャン
trivy config deployment.yaml
```

**Clair:**
```bash
# イメージ分析
clairctl analyze myimage:latest

# レポート取得
clairctl report myimage:latest
```

### ランタイムセキュリティ

**Falco:**
```yaml
# カスタムルール
- rule: Unauthorized Process
  desc: Detect unauthorized process in container
  condition: >
    spawned_process and container and
    not proc.name in (authorized_procs)
  output: >
    Unauthorized process started in container
    (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING
```

## IaCセキュリティ

### Terraform スキャン

**Checkov:**
```bash
# ディレクトリスキャン
checkov -d terraform/

# 特定ファイル
checkov -f main.tf

# JSONレポート
checkov -d terraform/ -o json
```

**tfsec:**
```bash
# プロジェクトスキャン
tfsec .

# 特定の深刻度
tfsec --minimum-severity HIGH .

# 除外ルール
tfsec --exclude-downloaded-modules .
```

### CloudFormation スキャン

**cfn-nag:**
```bash
# テンプレートスキャン
cfn_nag_scan --input-path template.yaml

# ディレクトリスキャン
cfn_nag_scan --input-path cloudformation/
```

## セキュリティゲート

### 品質ゲート設計

```python
# security_gate.py

import json
import sys

def check_vulnerabilities(report_file, threshold='medium'):
    with open(report_file) as f:
        report = json.load(f)

    severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    threshold_level = severity_map[threshold.lower()]

    high_severity_count = 0

    for vuln in report.get('vulnerabilities', []):
        severity = vuln.get('severity', 'unknown').lower()
        if severity_map.get(severity, 0) >= threshold_level:
            high_severity_count += 1
            print(f"[{severity.upper()}] {vuln['title']}")

    if high_severity_count > 0:
        print(f"\n❌ Found {high_severity_count} vulnerabilities at or above {threshold} severity")
        sys.exit(1)
    else:
        print(f"\n✅ No vulnerabilities found at or above {threshold} severity")
        sys.exit(0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', required=True)
    parser.add_argument('--threshold', default='medium')
    args = parser.parse_args()

    check_vulnerabilities(args.report, args.threshold)
```

## 継続的コンプライアンス

### Compliance as Code

**Open Policy Agent (OPA):**
```rego
# Kubernetes ポリシー
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    image := input.request.object.spec.containers[_].image
    not startswith(image, "trusted-registry.com/")
    msg := sprintf("Image %v is not from trusted registry", [image])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := "Privileged containers are not allowed"
}
```

**InSpec:**
```ruby
# セキュリティ設定チェック
describe file('/etc/ssh/sshd_config') do
  its('content') { should match /^PermitRootLogin no/ }
  its('content') { should match /^PasswordAuthentication no/ }
end

describe port(22) do
  it { should be_listening }
end
```

## メトリクスとKPI

### DevSecOps メトリクス

**セキュリティメトリクス:**
- 脆弱性検出数（深刻度別）
- 平均修正時間（MTTR）
- デプロイ前検出率
- セキュリティテストカバレッジ

**プロセスメトリクス:**
- CI/CD実行時間
- セキュリティゲート通過率
- False Positive率

**ダッシュボード例（Grafana）:**
```json
{
  "panels": [
    {
      "title": "Vulnerabilities by Severity",
      "type": "pie",
      "targets": [{
        "expr": "sum by (severity) (vulnerabilities_total)"
      }]
    },
    {
      "title": "MTTR (Mean Time To Remediate)",
      "type": "stat",
      "targets": [{
        "expr": "avg(vulnerability_remediation_time_hours)"
      }]
    }
  ]
}
```

## ベストプラクティス

1. **早期統合**
   - IDE統合（SonarLint、Snyk等）
   - プリコミットフック
   - Pull Requestチェック

2. **自動化優先**
   - 手動プロセス最小化
   - 自動修復（可能な場合）

3. **開発者フレンドリー**
   - 誤検知の最小化
   - 明確なガイダンス
   - 簡単な修正方法

4. **継続的改善**
   - メトリクス監視
   - フィードバックループ
   - ツール最適化

5. **文化醸成**
   - セキュリティトレーニング
   - 責任共有
   - ベストプラクティス共有

## 参考リソース

- OWASP DevSecOps Guideline
- NIST SP 800-204 Security Strategies for Microservices
- The DevOps Handbook
- Accelerate (書籍)

## 注意事項

- パフォーマンスへの影響考慮
- False Positiveの管理
- ツールの定期更新
- 開発プロセスとのバランス
