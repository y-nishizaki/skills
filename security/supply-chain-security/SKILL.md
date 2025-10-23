---
name: "supply-chain-security"
description: >
  サプライチェーンセキュリティの実践を支援します。SBOM（Software Bill of Materials）、
  署名付きビルド、依存関係監査、サプライチェーン攻撃対策、ベンダーリスク管理、
  ゼロトラストサプライチェーンなど、ソフトウェアサプライチェーン全体のセキュリティ確保に使用します。
  キーワード - サプライチェーン、SBOM、依存関係、署名、Sigstore、SLSA、ベンダーリスク。
version: 1.0.0
---

# サプライチェーンセキュリティスキル

## 目的

このスキルは、ソフトウェアとハードウェアのサプライチェーンに対するセキュリティ脅威と
対策を提供します。SBOM、署名検証、依存関係管理、ベンダーリスク評価など、
サプライチェーン全体のセキュリティを確保するための実践的知識を含みます。

## サプライチェーン攻撃

### 主要な攻撃タイプ

**1. 依存関係汚染**
- マルウェア含有ライブラリ
- タイポスクワッティング
- 依存関係混乱攻撃

**事例: event-stream（2018）**
```
正規ライブラリ → 悪意ある開発者に譲渡 → マルウェア追加 →
200万ダウンロード → Bitcoin盗難試行
```

**2. ビルドシステム侵害**
- SolarWinds（2020）
- CodeCov（2021）

**3. 更新メカニズム侵害**
- NotPetya（2017）

## SBOM（Software Bill of Materials）

### SBOMとは

ソフトウェアコンポーネントの詳細な目録:
- コンポーネント名
- バージョン
- ライセンス
- 依存関係
- 既知の脆弱性

### SBOM標準

**SPDX（Software Package Data Exchange）:**
```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "MyApp",
  "packages": [
    {
      "name": "express",
      "SPDXID": "SPDXRef-Package-express",
      "versionInfo": "4.18.2",
      "licenseDeclared": "MIT",
      "externalRefs": [
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:npm/express@4.18.2"
        }
      ]
    }
  ]
}
```

**CycloneDX:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bom xmlns="http://cyclonedx.org/schema/bom/1.4">
  <metadata>
    <component type="application">
      <name>MyApp</name>
      <version>1.0.0</version>
    </component>
  </metadata>
  <components>
    <component type="library">
      <name>express</name>
      <version>4.18.2</version>
      <purl>pkg:npm/express@4.18.2</purl>
      <licenses>
        <license><id>MIT</id></license>
      </licenses>
    </component>
  </components>
</bom>
```

### SBOM生成ツール

**Syft:**
```bash
# コンテナイメージ
syft nginx:latest

# ディレクトリ
syft dir:./myapp

# SPDX形式で出力
syft nginx:latest -o spdx-json > sbom.spdx.json

# CycloneDX形式
syft nginx:latest -o cyclonedx-json > sbom.cdx.json
```

**CycloneDX CLI:**
```bash
# NPMプロジェクト
cyclonedx-npm --output-file sbom.xml

# Mavenプロジェクト
mvn org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom
```

## 依存関係管理

### 依存関係固定（Pinning）

**package-lock.json (NPM):**
```json
{
  "name": "myapp",
  "version": "1.0.0",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "node_modules/express": {
      "version": "4.18.2",
      "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
      "integrity": "sha512-5/PsL6iGPdfQ/lKM1UuielYgv3BUoJfz1aUwU9vHZ+J7gyvwdQXFEBIEIaxeGf0GIcreATNyBExtalisDbuMqQ=="
    }
  }
}
```

**requirements.txt (Python) with hashes:**
```
flask==2.3.2 \
    --hash=sha256:8a4cf32d904cf5621db9f0c9fbcd7efabf3003f22a04e4d0ce790c7137ec5264 \
    --hash=sha256:edee9b0a7ff26621bd5a8c10ff484ae28737a2410d99b0bb9a6850c7fb977aa0
```

### サブリソース完全性（SRI）

```html
<script src="https://cdn.example.com/library.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

### 依存関係スキャン

**Dependabot:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

**Renovate:**
```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
```

## 署名とアーティファクト検証

### Sigstore

**Cosign（コンテナイメージ署名）:**

```bash
# イメージ署名
cosign sign --key cosign.key myregistry.com/myimage:v1.0

# 署名検証
cosign verify --key cosign.pub myregistry.com/myimage:v1.0

# Keyless署名（OIDC）
cosign sign myregistry.com/myimage:v1.0

# 添付情報（SBOM）
cosign attach sbom --sbom sbom.spdx.json myregistry.com/myimage:v1.0
```

**Rekor（透明性ログ）:**
```bash
# ログへの記録検索
rekor-cli search --artifact myimage:v1.0

# エントリ取得
rekor-cli get --uuid <uuid>
```

### in-toto

サプライチェーンメタデータフレームワーク:

```python
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock

# レイアウト定義
layout = Layout.read({
    "steps": [{
        "name": "build",
        "expected_materials": [["MATCH", "src/*", "WITH", "PRODUCTS", "FROM", "fetch"]],
        "expected_products": [["CREATE", "app"]],
        "pubkeys": ["builder-key"],
        "expected_command": ["go", "build"]
    }],
    "inspect": [{
        "name": "verify-signature",
        "expected_materials": [["MATCH", "app", "WITH", "PRODUCTS", "FROM", "build"]]
    }]
})
```

## SLSA（Supply chain Levels for Software Artifacts）

### SLSAレベル

**Level 0:**
- 保証なし

**Level 1:**
- ビルドプロセスの文書化
- 出所の記録

**Level 2:**
- ホスト型ビルドサービス使用
- 出所の認証

**Level 3:**
- ハードニングされたビルドプラットフォーム
- 監査可能

**Level 4:**
- ツーパーティレビュー
- ヘルメット型ビルド

### SLSA達成

**GitHub Actions (SLSA Level 3):**

```yaml
name: SLSA Build

on: [push]

permissions:
  id-token: write  # SLSAプロベナンス用
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
      - run: go build -o app

      # SLSAプロベナンス生成
      - uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.7.0
        with:
          artifacts: "app"
```

## ベンダーリスク管理

### サードパーティリスク評価

**評価項目:**
```markdown
## セキュリティ評価質問票

### 1. 情報セキュリティプログラム
- [ ] ISO 27001 認証取得済み
- [ ] SOC 2 Type II レポート提供可能
- [ ] 定期的なペネトレーションテスト実施
- [ ] インシデント対応計画の文書化

### 2. データ保護
- [ ] データ暗号化（保存時・通信時）
- [ ] データ分類ポリシー
- [ ] データ保持・削除ポリシー
- [ ] GDPRコンプライアンス

### 3. アクセス制御
- [ ] MFA必須
- [ ] 最小権限原則
- [ ] 定期的なアクセスレビュー
- [ ] 離職時のアクセス削除プロセス

### 4. サプライチェーン
- [ ] SBOM提供
- [ ] 脆弱性管理プロセス
- [ ] セキュアSDLC
- [ ] サブプロセッサー管理

### 5. インシデント管理
- [ ] インシデント通知義務（24時間以内）
- [ ] インシデント対応手順書
- [ ] 過去のインシデント履歴
```

### 継続的監視

```python
def monitor_vendor_risk():
    """
    ベンダーリスク継続監視
    """
    checks = {
        'security_posture': check_security_rating(),
        'vulnerabilities': scan_vendor_products(),
        'compliance': verify_certifications(),
        'incidents': check_breach_databases(),
        'reputation': monitor_security_news()
    }

    risk_score = calculate_risk_score(checks)

    if risk_score > threshold:
        alert_security_team()

    return risk_score
```

## ゼロトラストサプライチェーン

### 原則

1. **すべてを検証**
   - 依存関係の署名検証
   - SBOMによる透明性
   - 継続的スキャン

2. **最小権限**
   - ビルドシステムの権限制限
   - シークレット最小化
   - 環境分離

3. **侵害を想定**
   - 多層防御
   - 監視とログ
   - インシデント対応計画

### 実装

**ビルドパイプライン強化:**

```yaml
# セキュアビルドパイプライン
steps:
  - name: Checkout
    uses: actions/checkout@v3
    with:
      persist-credentials: false

  - name: Dependency Review
    uses: actions/dependency-review-action@v3

  - name: Build
    run: |
      # 再現可能ビルド
      export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
      go build -trimpath -ldflags="-buildid=" -o app

  - name: Generate SBOM
    run: syft . -o spdx-json=sbom.spdx.json

  - name: Sign
    run: cosign sign-blob --key key.pem app > app.sig

  - name: Attest
    run: |
      cosign attest --key key.pem \
        --predicate sbom.spdx.json \
        --type spdx \
        myregistry.com/app:v1.0
```

## ベストプラクティス

1. **SBOM生成と管理**
   - すべての成果物にSBOM
   - SBOMのバージョン管理
   - 顧客への提供

2. **署名検証**
   - すべての依存関係を検証
   - ビルド成果物に署名
   - 検証プロセスの自動化

3. **最小依存関係**
   - 不要な依存関係削除
   - 定期的な棚卸し
   - 代替案の検討

4. **監視と対応**
   - 脆弱性の継続監視
   - 迅速なパッチ適用
   - インシデント対応計画

5. **ベンダー管理**
   - リスク評価
   - 契約にセキュリティ条項
   - 定期的なレビュー

## 参考リソース

- CISA Software Bill of Materials (SBOM)
- SLSA Framework
- Sigstore Project
- NIST SP 800-161 Cybersecurity Supply Chain Risk Management
- in-toto Framework

## 注意事項

- サプライチェーンセキュリティは継続的プロセス
- 完全なセキュリティは不可能
- リスクベースのアプローチ
- 業界協力が重要
