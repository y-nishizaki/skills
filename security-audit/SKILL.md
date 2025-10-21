---
name: "セキュリティ監査"
description: "セキュリティ監査と脆弱性評価。セキュリティ、脆弱性、セキュアコーディング、セキュリティチェック、監査に関する依頼に対応"
---

# セキュリティ監査: セキュリティ評価と対策の思考プロセス

## このスキルを使う場面

- コードのセキュリティレビュー
- 脆弱性の発見と修正
- セキュアコーディングガイドラインの適用
- 依存関係の脆弱性チェック
- セキュリティ設定の確認
- コンプライアンス要件の確認
- インシデント対応

## 思考プロセス

### フェーズ1: スコープの定義とリスク評価

**ステップ1: 監査対象の特定**

何を監査するか明確にする:

**対象システムの理解:**

- [ ] アプリケーションの種類（Web、API、モバイル等）
- [ ] 扱うデータの種類（個人情報、決済情報等）
- [ ] ユーザー数・アクセス量
- [ ] 外部サービスとの連携

**監査の範囲:**

- [ ] コードレビュー
- [ ] インフラ設定
- [ ] 依存関係
- [ ] 認証・認可
- [ ] データ保護
- [ ] ログとモニタリング

**制約条件:**

- [ ] 監査期間
- [ ] アクセス権限
- [ ] 利用可能なツール
- [ ] コンプライアンス要件（GDPR、PCI-DSS等）

**ステップ2: リスク評価**

脅威モデルを作成:

**資産の特定:**

1. **データ資産**
   - ユーザーの個人情報
   - 認証情報（パスワード、トークン）
   - 決済情報
   - ビジネス機密情報

2. **システム資産**
   - Webサーバー
   - データベース
   - API
   - 管理画面

**脅威の特定（STRIDE モデル）:**

- **S**poofing（なりすまし）: 認証の弱点
- **T**ampering（改ざん）: データの不正変更
- **R**epudiation（否認）: ログ不足
- **I**nformation Disclosure（情報漏洩）: 機密情報の露出
- **D**enial of Service（サービス妨害）: DoS攻撃
- **E**levation of Privilege（権限昇格）: 認可の弱点

**リスクの優先順位付け:**

各脅威のリスクレベルを評価:

```
リスク = 影響度 × 発生確率

高リスク: 即座に対応が必要
中リスク: 計画的に対応
低リスク: 監視または受容
```

**移行条件:**

- [ ] 監査スコープを定義した
- [ ] 主要な資産を特定した
- [ ] 脅威モデルを作成した
- [ ] リスクの優先順位を決めた

### フェーズ2: OWASP Top 10 によるチェック

**ステップ1: A01 - アクセス制御の不備**

認証・認可の確認:

**1. 認証の強度**

```python
# 悪い例: 弱いパスワードポリシー
def is_valid_password(password):
    return len(password) >= 6  # 短すぎる

# 良い例: 強力なパスワードポリシー
def is_valid_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):  # 大文字
        return False
    if not re.search(r'[a-z]', password):  # 小文字
        return False
    if not re.search(r'\d', password):     # 数字
        return False
    if not re.search(r'[!@#$%^&*]', password):  # 特殊文字
        return False
    return True
```

**チェック項目:**

- [ ] パスワードポリシーが適切
- [ ] パスワードがハッシュ化されている（bcrypt、Argon2等）
- [ ] ソルトが使用されている
- [ ] 多要素認証（MFA）の実装
- [ ] セッション管理が適切
- [ ] セッションタイムアウトの設定

**2. 認可の確認**

```python
# 悪い例: 認可チェックなし
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    db.delete_user(user_id)  # 誰でも削除できてしまう
    return {'status': 'deleted'}

# 良い例: 適切な認可チェック
@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    current_user = get_current_user()

    # 管理者または本人のみ削除可能
    if not (current_user.is_admin or current_user.id == user_id):
        return {'error': 'Forbidden'}, 403

    db.delete_user(user_id)
    return {'status': 'deleted'}
```

**チェック項目:**

- [ ] すべてのエンドポイントに認証が必要
- [ ] 権限チェックが適切（最小権限の原則）
- [ ] IDOR（Insecure Direct Object Reference）の脆弱性がない
- [ ] 横方向のアクセス制御
- [ ] 縦方向のアクセス制御（権限昇格）

**ステップ2: A02 - 暗号化の失敗**

データ保護の確認:

**1. 保存データの暗号化**

```python
# 悪い例: 平文で保存
db.save_credit_card(card_number="1234-5678-9012-3456")

# 良い例: 暗号化して保存
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data):
    key = load_encryption_key()  # 安全に管理された鍵
    f = Fernet(key)
    return f.encrypt(data.encode())

encrypted_card = encrypt_sensitive_data("1234-5678-9012-3456")
db.save_credit_card(encrypted_card)
```

**チェック項目:**

- [ ] 機密データが暗号化されている
- [ ] 強力な暗号化アルゴリズムを使用（AES-256等）
- [ ] 暗号化キーが安全に管理されている
- [ ] パスワードが平文で保存されていない
- [ ] ハッシュ化に適切なアルゴリズム（bcrypt、Argon2）

**2. 通信の暗号化**

```nginx
# 悪い例: HTTPのみ
server {
    listen 80;
    server_name example.com;
}

# 良い例: HTTPSの強制
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

**チェック項目:**

- [ ] HTTPS/TLSの使用
- [ ] 古いプロトコルの無効化（SSLv3、TLS 1.0/1.1）
- [ ] 強力な暗号スイートの使用
- [ ] HSTS（HTTP Strict Transport Security）の設定
- [ ] 証明書の有効期限

**ステップ3: A03 - インジェクション**

インジェクション攻撃の防止:

**1. SQLインジェクション**

```python
# 悪い例: 文字列連結
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
    # username = "admin' OR '1'='1" で全ユーザー取得可能

# 良い例: パラメータ化クエリ
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
```

**チェック項目:**

- [ ] パラメータ化クエリの使用
- [ ] ORM の適切な使用
- [ ] 入力検証
- [ ] 最小権限のDBユーザー
- [ ] ストアドプロシージャの検討

**2. コマンドインジェクション**

```python
# 悪い例: シェルコマンドの直接実行
import os
def process_file(filename):
    os.system(f"cat {filename}")  # filename = "; rm -rf /" で危険

# 良い例: 安全なAPI使用
def process_file(filename):
    # ホワイトリストチェック
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        raise ValueError("Invalid filename")

    # 安全なパスの構築
    safe_path = os.path.join('/safe/directory', filename)

    # シェル経由せずにファイル操作
    with open(safe_path, 'r') as f:
        return f.read()
```

**3. XSS（クロスサイトスクリプティング）**

```javascript
// 悪い例: エスケープなし
element.innerHTML = userInput;  // <script>alert('XSS')</script>

// 良い例: エスケープ
element.textContent = userInput;  // HTMLとして解釈されない

// または
const escapedInput = escapeHtml(userInput);
element.innerHTML = escapedInput;
```

**チェック項目:**

- [ ] 出力のエスケープ
- [ ] Content Security Policy（CSP）の設定
- [ ] HTTPOnly、Secure フラグのクッキー
- [ ] DOM based XSS の防止

**4. LDAP/XML/NoSQL インジェクション**

各種インジェクションに対する防御:

- [ ] 入力検証とサニタイゼーション
- [ ] 適切なエスケープ処理
- [ ] ホワイトリスト方式の採用

**ステップ4: A04 - 安全でない設計**

設計レベルのセキュリティ:

**チェック項目:**

- [ ] セキュリティ要件の定義
- [ ] 脅威モデリングの実施
- [ ] セキュアなアーキテクチャパターン
- [ ] 防御的プログラミング
- [ ] 失敗時の安全な挙動（Fail Secure）

**ステップ5: A05 - セキュリティの設定ミス**

設定の確認:

**1. デフォルト設定の変更**

```yaml
# 悪い例: デフォルトの認証情報
database:
  username: admin
  password: admin

# 良い例: 強力な認証情報
database:
  username: ${DB_USER}
  password: ${DB_PASSWORD}  # 環境変数から取得
```

**チェック項目:**

- [ ] デフォルトの認証情報の変更
- [ ] 不要なサービス・機能の無効化
- [ ] エラーメッセージの適切な処理
- [ ] セキュリティヘッダーの設定
- [ ] ディレクトリリスティングの無効化

**2. セキュリティヘッダー**

```python
# セキュリティヘッダーの設定
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

**ステップ6: A06 - 脆弱で古いコンポーネント**

依存関係の確認:

```bash
# 依存関係の脆弱性チェック
npm audit
pip-audit
bundle audit

# 自動更新の設定（Dependabot等）
```

**チェック項目:**

- [ ] 最新バージョンへの更新
- [ ] 既知の脆弱性のチェック
- [ ] サポート終了（EOL）コンポーネントの確認
- [ ] 不要な依存関係の削除
- [ ] 定期的な監査

**ステップ7: A07 - 識別と認証の失敗**

認証メカニズムの確認:

**1. ブルートフォース対策**

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # レート制限
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # アカウントロックアウト
    if is_account_locked(username):
        return {'error': 'Account locked'}, 403

    if not verify_credentials(username, password):
        increment_failed_attempts(username)
        return {'error': 'Invalid credentials'}, 401

    reset_failed_attempts(username)
    return create_session(username)
```

**チェック項目:**

- [ ] レート制限
- [ ] アカウントロックアウト
- [ ] CAPTCHA の実装
- [ ] セッション固定攻撃の防止
- [ ] セッションIDの再生成

**ステップ8: A08 - ソフトウェアとデータの整合性の不具合**

整合性の確認:

**チェック項目:**

- [ ] コード署名
- [ ] CI/CDパイプラインのセキュリティ
- [ ] 依存関係の検証
- [ ] 自動更新の検証
- [ ] デジタル署名の使用

**ステップ9: A09 - セキュリティログとモニタリングの失敗**

ログとモニタリング:

```python
import logging

# セキュリティイベントのログ
logger = logging.getLogger('security')

def login(username, password):
    if not verify_credentials(username, password):
        logger.warning(
            f"Failed login attempt",
            extra={
                'username': username,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string
            }
        )
        return {'error': 'Invalid credentials'}, 401

    logger.info(
        f"Successful login",
        extra={'username': username, 'ip': request.remote_addr}
    )
    return create_session(username)
```

**チェック項目:**

- [ ] セキュリティイベントのログ記録
- [ ] ログの集中管理
- [ ] リアルタイムアラート
- [ ] ログの改ざん防止
- [ ] ログの保管期間

**ステップ10: A10 - サーバーサイドリクエストフォージェリ（SSRF）**

SSRF の防止:

```python
# 悪い例: URLの検証なし
def fetch_url(url):
    return requests.get(url)  # 内部サービスへのアクセス可能

# 良い例: ホワイトリスト方式
ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

def fetch_url(url):
    parsed = urlparse(url)

    # ホワイトリストチェック
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")

    # プライベートIPの拒否
    ip = socket.gethostbyname(parsed.hostname)
    if ipaddress.ip_address(ip).is_private:
        raise ValueError("Private IP not allowed")

    return requests.get(url, timeout=5)
```

**チェック項目:**

- [ ] URLの検証
- [ ] ホワイトリスト方式
- [ ] プライベートIPの拒否
- [ ] ネットワーク分離

**移行条件:**

- [ ] OWASP Top 10 をチェックした
- [ ] 脆弱性を特定した
- [ ] 優先順位を決めた

### フェーズ3: コードレビューによるセキュリティチェック

**ステップ1: 入力検証**

すべての入力を検証:

**チェック項目:**

- [ ] クライアント側とサーバー側の両方で検証
- [ ] ホワイトリスト方式の採用
- [ ] 型チェック
- [ ] 長さ制限
- [ ] 範囲チェック
- [ ] 正規表現による検証

**ステップ2: 出力エンコーディング**

文脈に応じたエンコーディング:

- [ ] HTML エンコーディング
- [ ] JavaScript エンコーディング
- [ ] URL エンコーディング
- [ ] SQL エンコーディング

**ステップ3: エラーハンドリング**

```python
# 悪い例: 詳細なエラーを露出
@app.errorhandler(500)
def handle_error(e):
    return {'error': str(e), 'traceback': traceback.format_exc()}, 500

# 良い例: 一般的なエラーメッセージ
@app.errorhandler(500)
def handle_error(e):
    logger.error(f"Internal error: {e}", exc_info=True)
    return {'error': 'Internal server error'}, 500
```

**チェック項目:**

- [ ] エラーメッセージに機密情報が含まれていない
- [ ] スタックトレースが公開されていない
- [ ] エラーが適切にログされている

**ステップ4: 機密情報の管理**

```python
# 悪い例: ハードコード
API_KEY = "sk_live_1234567890abcdef"
db_password = "MyPassword123"

# 良い例: 環境変数
import os
API_KEY = os.environ['API_KEY']
db_password = os.environ['DB_PASSWORD']
```

**チェック項目:**

- [ ] 認証情報がハードコードされていない
- [ ] 環境変数の使用
- [ ] シークレット管理ツールの使用（Vault等）
- [ ] .gitignore の適切な設定
- [ ] ログに機密情報が出力されていない

**移行条件:**

- [ ] コードレビューを完了した
- [ ] セキュリティ問題を文書化した

### フェーズ4: 自動化ツールによる監査

**ステップ1: 静的解析ツール（SAST）**

コードの静的解析:

```bash
# Python
bandit -r ./src

# JavaScript
npm run eslint -- --ext .js,.jsx

# 複数言語対応
semgrep --config=auto .
```

**推奨ツール:**

- Bandit（Python）
- ESLint + security plugins（JavaScript）
- Brakeman（Ruby）
- SonarQube（複数言語）
- Semgrep（複数言語）

**ステップ2: 依存関係スキャン（SCA）**

```bash
# Node.js
npm audit fix

# Python
pip-audit
safety check

# Ruby
bundle audit

# 統合ツール
snyk test
```

**ステップ3: 動的解析ツール（DAST）**

実行時の脆弱性検出:

- OWASP ZAP
- Burp Suite
- Nikto

**ステップ4: コンテナスキャン**

```bash
# Docker イメージのスキャン
trivy image myapp:latest
docker scan myapp:latest
```

**移行条件:**

- [ ] 自動化ツールを実行した
- [ ] 結果を分析した
- [ ] False Positive を除外した

### フェーズ5: 修正と検証

**ステップ1: 修正の優先順位付け**

リスクベースで優先順位を決定:

**Critical（即座に修正）:**

- SQLインジェクション
- 認証バイパス
- リモートコード実行
- 機密情報の漏洩

**High（早急に修正）:**

- XSS
- CSRF
- 不適切なアクセス制御
- 暗号化の問題

**Medium（計画的に修正）:**

- セキュリティヘッダーの不足
- 情報漏洩（軽微）
- 設定の問題

**Low（監視または受容）:**

- 古いが安全なライブラリ
- 軽微な設定の改善

**ステップ2: 修正の実装**

セキュアコーディング:

**原則:**

1. **最小権限の原則**: 必要最小限の権限のみ
2. **深層防御**: 複数のセキュリティ層
3. **Fail Secure**: 失敗時は安全側に
4. **デフォルトで拒否**: ホワイトリスト方式
5. **完全な媒介**: すべてのアクセスをチェック

**ステップ3: 修正の検証**

修正が有効か確認:

- [ ] 脆弱性が修正されたことを確認
- [ ] 新しい問題が発生していないか
- [ ] パフォーマンスへの影響
- [ ] ユーザビリティへの影響

**移行条件:**

- [ ] すべてのCritical/High問題を修正した
- [ ] 修正を検証した
- [ ] テストを実施した

## 判断のポイント

### 修正すべきか受容すべきか

**即座に修正:**

- ユーザーデータの漏洩リスク
- 認証・認可の問題
- インジェクション脆弱性
- リモートコード実行

**計画的に修正:**

- セキュリティヘッダーの追加
- 古いライブラリの更新
- ログの改善

**受容（軽減策を実施）:**

- 影響範囲が限定的
- 修正コストが極めて高い
- 代替の軽減策がある

### False Positive の判断

自動ツールの誤検知:

- コードの文脈を確認
- 実際に悪用可能か検証
- 複数のツールで確認
- セキュリティ専門家に相談

## よくある落とし穴

1. **セキュリティの後回し**
   - ❌ 実装後にセキュリティ対策
   - ✅ 設計段階からセキュリティ考慮

2. **クライアント側の検証のみ**
   - ❌ JavaScriptでのみ検証
   - ✅ サーバー側でも必ず検証

3. **難読化 ≠ セキュリティ**
   - ❌ コードを読みにくくするだけ
   - ✅ 適切な暗号化と認証

4. **セキュリティバイオブスキュリティ**
   - ❌ 隠すことでセキュリティ確保
   - ✅ 公開されても安全な設計

5. **すべてを自作**
   - ❌ 暗号化アルゴリズムの自作
   - ✅ 実績のあるライブラリ使用

6. **ログに機密情報**
   - ❌ パスワードやトークンをログ
   - ✅ 機密情報はマスク・除外

7. **エラーメッセージの詳細露出**
   - ❌ スタックトレースを公開
   - ✅ 一般的なエラーメッセージ

## 検証ポイント

### 監査前

- [ ] スコープを定義した
- [ ] リスク評価を実施した
- [ ] チェックリストを準備した

### 監査中

- [ ] OWASP Top 10 をチェックした
- [ ] コードレビューを実施した
- [ ] 自動ツールを実行した
- [ ] 脆弱性を文書化した

### 監査後

- [ ] すべての脆弱性に対処した
- [ ] 修正を検証した
- [ ] 監査レポートを作成した
- [ ] 再発防止策を立案した

## 他スキルとの連携

### security-audit → code-review

セキュアコードレビュー:

1. security-auditスキルで脆弱性を特定
2. code-reviewスキルでコード品質全体を評価
3. セキュアコーディングのベストプラクティス適用

### security-audit → dependency-management

依存関係のセキュリティ:

1. security-auditスキルで脆弱性を検出
2. dependency-managementスキルで更新
3. 継続的な監視

### security-audit + test-automation

セキュリティテスト:

1. security-auditスキルで脆弱性を特定
2. test-automationスキルでテストケース作成
3. リグレッション防止

## セキュリティ監査のベストプラクティス

### 継続的なセキュリティ

- 開発プロセスへの統合
- 自動化ツールの活用
- 定期的な監査
- セキュリティ教育

### DevSecOps の実践

```yaml
# CI/CDパイプラインでのセキュリティチェック
pipeline:
  - stage: build
  - stage: test
  - stage: security-scan
    steps:
      - dependency-check
      - sast-scan
      - container-scan
  - stage: deploy
```

### インシデント対応計画

1. **検知**: モニタリングとアラート
2. **分析**: 影響範囲の特定
3. **対応**: 修正と展開
4. **回復**: サービス復旧
5. **事後**: 原因分析と改善

### セキュリティ文化の醸成

- セキュリティ意識の向上
- 定期的なトレーニング
- インシデントの共有
- 報奨制度（バグバウンティ等）
