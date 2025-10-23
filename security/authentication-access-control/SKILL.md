---
name: "authentication-access-control"
description: >
  認証とアクセス制御の実装を支援します。多要素認証（MFA）、OAuth2.0、SAML、Zero Trust、
  RBAC、ABAC、セッション管理、認証プロトコルなど、ID管理とアクセス制御の設計・実装に使用します。
  キーワード - 認証、アクセス制御、MFA、OAuth、SAML、Zero Trust、RBAC、ABAC、セッション、
  パスワードレス。
version: 1.0.0
---

# 認証・アクセス制御スキル

## 目的

このスキルは、認証とアクセス制御の設計、実装、管理に関する包括的な知識を提供します。
多要素認証、最新の認証プロトコル、アクセス制御モデル、セッション管理など、
セキュアな認証システムを構築するための実践的なガイダンスを含みます。

## このスキルを使用する場合

以下の場合にこのスキルを使用します:

- ユーザーが認証システムの実装や強化を求めた場合
- ユーザーがOAuth、SAML、OpenID Connectの実装を必要とする場合
- ユーザーが多要素認証（MFA）の導入を検討している場合
- ユーザーがRBAC、ABAC などのアクセス制御モデルを実装したい場合
- ユーザーがZero Trustアーキテクチャを設計したい場合
- ユーザーが「認証」、「アクセス制御」、「MFA」と言及した場合

## 認証の基礎

### 認証の三要素

1. **知識要素（Something you know）**
   - パスワード
   - PIN
   - セキュリティ質問

2. **所有要素（Something you have）**
   - スマートフォン
   - セキュリティトークン
   - スマートカード

3. **生体要素（Something you are）**
   - 指紋
   - 顔認証
   - 虹彩認証
   - 声紋

### 認証方式

#### パスワード認証

**ベストプラクティス:**
- 最低12文字
- 複雑性要件（大文字、小文字、数字、記号）
- パスワード履歴（過去のパスワード再利用防止）
- 定期的な変更（90日推奨）
- アカウントロックアウト（5回失敗で30分）

**実装例（Python Flask）:**

```python
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# パスワードのハッシュ化
hashed_password = generate_password_hash('user_password', method='pbkdf2:sha256')

# パスワードの検証
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # DBからハッシュ化されたパスワードを取得
    stored_hash = get_password_hash_from_db(username)

    if check_password_hash(stored_hash, password):
        session['user'] = username
        return "ログイン成功"
    else:
        return "認証失敗", 401
```

#### 多要素認証（MFA）

**TOTP（Time-based One-Time Password）:**

```python
import pyotp
import qrcode

# シークレットキー生成
secret = pyotp.random_base32()

# TOTP URI生成
totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name='user@example.com',
    issuer_name='YourApp'
)

# QRコード生成
qrcode.make(totp_uri).save('qrcode.png')

# 検証
totp = pyotp.TOTP(secret)
is_valid = totp.verify('123456')  # ユーザー入力のコード
```

**SMS/Email OTP:**

```python
import random
import string

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# OTP生成と保存（有効期限5分）
otp = generate_otp()
store_otp_with_expiry(user_id, otp, expires_in=300)

# SMS送信
send_sms(user_phone, f"Your verification code: {otp}")

# 検証
def verify_otp(user_id, input_otp):
    stored_otp, expiry = get_otp_from_db(user_id)
    if time.time() > expiry:
        return False, "OTP expired"
    if stored_otp == input_otp:
        delete_otp(user_id)
        return True, "Verified"
    return False, "Invalid OTP"
```

**Hardware Tokens（WebAuthn）:**

```javascript
// サーバー側で登録チャレンジ生成
const challenge = crypto.randomBytes(32);

// クライアント側で認証器登録
const credential = await navigator.credentials.create({
    publicKey: {
        challenge: challenge,
        rp: { name: "Example Corp" },
        user: {
            id: new Uint8Array(16),
            name: "user@example.com",
            displayName: "User Name"
        },
        pubKeyCredParams: [
            { type: "public-key", alg: -7 }  // ES256
        ],
        authenticatorSelection: {
            authenticatorAttachment: "platform",
            userVerification: "required"
        }
    }
});

// サーバーで検証
```

#### パスワードレス認証

**Magic Links:**

```python
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(app.secret_key)

# Magic Link生成
def generate_magic_link(email):
    token = serializer.dumps(email, salt='email-login')
    link = f"https://example.com/login/{token}"
    send_email(email, f"Login link: {link}")
    return token

# トークン検証
def verify_magic_link(token, max_age=600):  # 10分有効
    try:
        email = serializer.loads(token, salt='email-login', max_age=max_age)
        return email
    except:
        return None
```

**生体認証:**
- Face ID / Touch ID
- Windows Hello
- Android Biometric API

## OAuth 2.0

### OAuth 2.0 フロー

#### Authorization Code Flow（推奨）

```
1. Client → Authorization Server: 認可リクエスト
2. User → Authorization Server: ログイン・同意
3. Authorization Server → Client: 認可コード
4. Client → Authorization Server: 認可コード + Client Secret
5. Authorization Server → Client: Access Token
6. Client → Resource Server: Access Token でリソース取得
```

**実装例（Flask-OAuthlib）:**

```python
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'random-secret'

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['user'] = user
    return redirect('/')
```

#### Client Credentials Flow（M2M）

```python
import requests

# トークン取得
response = requests.post('https://auth.example.com/token', data={
    'grant_type': 'client_credentials',
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET',
    'scope': 'api.read api.write'
})

access_token = response.json()['access_token']

# API呼び出し
api_response = requests.get(
    'https://api.example.com/resource',
    headers={'Authorization': f'Bearer {access_token}'}
)
```

### PKCE (Proof Key for Code Exchange)

モバイルアプリ・SPAでの推奨方式

```python
import hashlib
import base64
import secrets

# Code Verifier生成
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

# Code Challenge生成
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).decode('utf-8').rstrip('=')

# 認可リクエスト
auth_url = f"https://auth.example.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&code_challenge={code_challenge}&code_challenge_method=S256"

# トークン取得
token_response = requests.post('https://auth.example.com/token', data={
    'grant_type': 'authorization_code',
    'code': authorization_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'code_verifier': code_verifier
})
```

## OpenID Connect (OIDC)

OAuth 2.0の上に構築された認証レイヤー

**ID Token（JWT）:**

```python
import jwt

# ID Token検証
def verify_id_token(token, client_id, issuer):
    try:
        # 公開鍵取得（JWKSエンドポイントから）
        jwks_client = jwt.PyJWKClient(f"{issuer}/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # トークン検証
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=issuer
        )
        return decoded
    except jwt.InvalidTokenError:
        return None

# ID Token デコード
id_token = "eyJhbGciOiJSUzI1NiIs..."
user_info = verify_id_token(id_token, client_id, "https://accounts.google.com")
```

## SAML 2.0

エンタープライズ環境でのSSO

**SAMLフロー（SP-Initiated）:**

```
1. User → SP: リソースアクセス
2. SP → User: SAMLリクエスト（IdPへリダイレクト）
3. User → IdP: ログイン
4. IdP → User: SAMLアサーション（SPへリダイレクト）
5. User → SP: SAMLアサーション提示
6. SP: アサーション検証 → アクセス許可
```

**Python SAML実装:**

```python
from onelogin.saml2.auth import OneLogin_Saml2_Auth

def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
    return auth

def saml_login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return redirect(auth.login())

def saml_acs():  # Assertion Consumer Service
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        if auth.is_authenticated():
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            return redirect(url_for('index'))

    return "認証失敗", 401
```

## セッション管理

### セッションのベストプラクティス

1. **Secure Cookie属性**

```python
app.config.update(
    SESSION_COOKIE_SECURE=True,       # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,     # JavaScript からアクセス不可
    SESSION_COOKIE_SAMESITE='Lax',    # CSRF対策
    PERMANENT_SESSION_LIFETIME=1800   # 30分でタイムアウト
)
```

2. **セッション固定攻撃対策**

```python
# ログイン成功時にセッションIDを再生成
@app.route('/login', methods=['POST'])
def login():
    if authenticate(username, password):
        session.regenerate()  # Flask: session.clear() + new session
        session['user_id'] = user.id
        return redirect('/')
```

3. **セッションタイムアウト**

```python
from datetime import datetime, timedelta

@app.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last > timedelta(minutes=30):
            session.clear()
            return redirect('/login')
    session['last_activity'] = datetime.now().isoformat()
```

### JWT (JSON Web Tokens)

**JWT生成と検証:**

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'

# JWT生成
def create_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'sub': str(user_id)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# JWT検証
def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # トークン期限切れ
    except jwt.InvalidTokenError:
        return None  # 無効なトークン

# デコレータ
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'message': 'Token missing'}), 401

        payload = verify_jwt(token)
        if not payload:
            return jsonify({'message': 'Invalid token'}), 401

        return f(payload, *args, **kwargs)
    return decorated

@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({'user_id': current_user['user_id']})
```

## アクセス制御モデル

### RBAC (Role-Based Access Control)

**実装例:**

```python
class Permission:
    READ = 1
    WRITE = 2
    DELETE = 4
    ADMIN = 8

roles = {
    'viewer': Permission.READ,
    'editor': Permission.READ | Permission.WRITE,
    'admin': Permission.READ | Permission.WRITE | Permission.DELETE | Permission.ADMIN
}

def check_permission(user_role, required_permission):
    return (roles.get(user_role, 0) & required_permission) == required_permission

# デコレータ
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not check_permission(user.role, permission):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/users')
@require_permission(Permission.ADMIN)
def admin_users():
    return "Admin panel"
```

### ABAC (Attribute-Based Access Control)

ポリシーベースのアクセス制御

```python
class Policy:
    def __init__(self):
        self.rules = []

    def add_rule(self, subject_attrs, resource_attrs, action, effect):
        self.rules.append({
            'subject': subject_attrs,
            'resource': resource_attrs,
            'action': action,
            'effect': effect
        })

    def evaluate(self, subject, resource, action):
        for rule in self.rules:
            if self._match_attributes(subject, rule['subject']) and \
               self._match_attributes(resource, rule['resource']) and \
               action == rule['action']:
                return rule['effect']
        return 'deny'  # デフォルト拒否

    def _match_attributes(self, obj, attrs):
        return all(getattr(obj, k, None) == v for k, v in attrs.items())

# ポリシー定義
policy = Policy()
policy.add_rule(
    subject_attrs={'department': 'HR'},
    resource_attrs={'type': 'employee_record'},
    action='read',
    effect='allow'
)
policy.add_rule(
    subject_attrs={'role': 'manager', 'department': 'HR'},
    resource_attrs={'type': 'employee_record'},
    action='write',
    effect='allow'
)

# アクセス制御チェック
result = policy.evaluate(current_user, resource, 'write')
```

## Zero Trust アーキテクチャ

### 主要原則

1. **常に検証する（Verify Explicitly）**
   - すべてのリクエストを認証・認可
   - ネットワーク位置を信頼しない

2. **最小権限アクセス（Least Privilege）**
   - Just-In-Time (JIT) アクセス
   - Just-Enough-Access (JEA)

3. **侵害を想定（Assume Breach）**
   - マイクロセグメンテーション
   - エンドツーエンド暗号化
   - 継続的な監視

### 実装要素

**デバイス認証:**

```python
# デバイスフィンガープリント
import hashlib

def generate_device_fingerprint(request):
    components = [
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        request.headers.get('Accept-Encoding', ''),
        request.remote_addr
    ]
    fingerprint = hashlib.sha256('|'.join(components).encode()).hexdigest()
    return fingerprint

# デバイス検証
def verify_device(user_id, fingerprint):
    trusted_devices = get_trusted_devices(user_id)
    return fingerprint in trusted_devices
```

**コンテキストベース認証:**

```python
def assess_risk(user, request):
    risk_score = 0

    # 未知のデバイス
    if not verify_device(user.id, get_device_fingerprint(request)):
        risk_score += 30

    # 異常な位置
    if is_unusual_location(user.id, request.remote_addr):
        risk_score += 40

    # 異常な時間
    if is_unusual_time(user.id):
        risk_score += 20

    # 高リスク操作
    if is_sensitive_operation(request.path):
        risk_score += 20

    return risk_score

def adaptive_authentication(user, request):
    risk = assess_risk(user, request)

    if risk < 30:
        return 'allow'
    elif risk < 60:
        return 'require_mfa'
    else:
        return 'block'
```

## シングルサインオン（SSO）

### エンタープライズSSO実装

**CAS (Central Authentication Service):**
**Kerberos:**
**LDAP統合:**

```python
import ldap

def ldap_authenticate(username, password):
    try:
        ldap_server = "ldap://ldap.example.com"
        conn = ldap.initialize(ldap_server)
        conn.set_option(ldap.OPT_REFERRALS, 0)

        user_dn = f"uid={username},ou=users,dc=example,dc=com"
        conn.simple_bind_s(user_dn, password)

        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    finally:
        conn.unbind()
```

## セキュリティベストプラクティス

### 認証

- [ ] パスワードは強固にハッシュ化（bcrypt/Argon2）
- [ ] MFAを実装
- [ ] アカウントロックアウトポリシー
- [ ] パスワードレス認証の検討
- [ ] セッション管理の適切な実装
- [ ] HTTPS必須
- [ ] CSRF対策
- [ ] ブルートフォース攻撃対策

### アクセス制御

- [ ] 最小権限の原則
- [ ] デフォルト拒否
- [ ] 定期的な権限レビュー
- [ ] 特権アクセス管理（PAM）
- [ ] ログとモニタリング

## 参考リソース

- OWASP Authentication Cheat Sheet
- NIST SP 800-63B: Digital Identity Guidelines
- OAuth 2.0 RFC 6749
- OpenID Connect Core 1.0
- SAML 2.0 Specifications

## 注意事項

- **セキュリティレビュー**: 本番実装前に必ずセキュリティ専門家のレビューを受けること
- **コンプライアンス**: GDPR、個人情報保護法などの法規制遵守を確認すること
- **テスト**: 認証フローの徹底的なテストを実施すること
- **監視**: 認証失敗や異常なアクセスパターンを監視すること
