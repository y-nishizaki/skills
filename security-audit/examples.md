# セキュリティ監査: 脆弱性の例と対策

このドキュメントでは、セキュリティ監査スキルで説明されている脆弱性の具体例と、それらへの対策方法を示します。

## 目次

- [インジェクション攻撃の例](#インジェクション攻撃の例)
- [認証・認可の脆弱性](#認証認可の脆弱性)
- [暗号化の問題](#暗号化の問題)
- [セキュリティ設定の例](#セキュリティ設定の例)
- [セキュアコーディングパターン](#セキュアコーディングパターン)

## インジェクション攻撃の例

### SQLインジェクション

**脆弱なコード:**

```python
# Python + SQLite
import sqlite3

def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 危険: 文字列連結
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    return cursor.fetchone()

# 攻撃例
# username = "admin' OR '1'='1' --"
# 実行されるSQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
# 結果: すべてのユーザーが取得される
```

**安全なコード:**

```python
def get_user_by_username(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 安全: パラメータ化クエリ
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))

    return cursor.fetchone()
```

**ORMを使用した安全な実装:**

```python
# SQLAlchemy
from sqlalchemy.orm import Session
from models import User

def get_user_by_username(session: Session, username: str):
    # ORMは自動的にパラメータ化する
    return session.query(User).filter(User.username == username).first()
```

### NoSQLインジェクション

**脆弱なコード（MongoDB）:**

```javascript
// Node.js + MongoDB
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  // 危険: オブジェクトをそのまま使用
  const user = await db.collection('users').findOne({
    username: username,
    password: password
  });

  if (user) {
    return res.json({ success: true });
  }
  return res.json({ success: false });
});

// 攻撃例
// POST /api/login
// { "username": "admin", "password": { "$ne": null } }
// 結果: パスワードチェックをバイパス
```

**安全なコード:**

```javascript
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  // 入力検証
  if (typeof username !== 'string' || typeof password !== 'string') {
    return res.status(400).json({ error: 'Invalid input' });
  }

  // 安全なクエリ
  const user = await db.collection('users').findOne({
    username: username,
    password: hashPassword(password)  // パスワードはハッシュ化して比較
  });

  if (user) {
    return res.json({ success: true });
  }
  return res.json({ success: false });
});
```

### コマンドインジェクション

**脆弱なコード:**

```python
import subprocess

def ping_host(host):
    # 危険: シェルコマンドに直接挿入
    result = subprocess.run(
        f"ping -c 4 {host}",
        shell=True,  # shell=True は危険
        capture_output=True,
        text=True
    )
    return result.stdout

# 攻撃例
# host = "example.com; cat /etc/passwd"
# 実行されるコマンド: ping -c 4 example.com; cat /etc/passwd
```

**安全なコード:**

```python
import subprocess
import re

def ping_host(host):
    # 入力検証: ホスト名のみ許可
    if not re.match(r'^[a-zA-Z0-9\.\-]+$', host):
        raise ValueError("Invalid host name")

    # 安全: シェルを使わず、引数をリストで渡す
    result = subprocess.run(
        ['ping', '-c', '4', host],  # リスト形式
        shell=False,  # shell=False で安全
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout
```

### XSS（クロスサイトスクリプティング）

**脆弱なコード:**

```html
<!-- 危険: エスケープなし -->
<!DOCTYPE html>
<html>
<body>
  <h1>Welcome, <span id="username"></span>!</h1>

  <script>
    // URLパラメータから名前を取得
    const params = new URLSearchParams(window.location.search);
    const username = params.get('name');

    // 危険: HTMLに直接挿入
    document.getElementById('username').innerHTML = username;
  </script>
</body>
</html>

<!-- 攻撃例 -->
<!-- URL: /?name=<script>alert('XSS')</script> -->
<!-- または: /?name=<img src=x onerror=alert('XSS')> -->
```

**安全なコード:**

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Welcome, <span id="username"></span>!</h1>

  <script>
    const params = new URLSearchParams(window.location.search);
    const username = params.get('name');

    // 安全: textContentを使用（HTMLとして解釈されない）
    document.getElementById('username').textContent = username;

    // または、エスケープ関数を使用
    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    document.getElementById('username').innerHTML = escapeHtml(username);
  </script>
</body>
</html>
```

**React での安全な実装:**

```jsx
// React は自動的にエスケープする
function Welcome({ username }) {
  // 安全: React が自動エスケープ
  return <h1>Welcome, {username}!</h1>;

  // 危険: dangerouslySetInnerHTML は避ける
  // return <h1 dangerouslySetInnerHTML={{ __html: username }} />;
}
```

**サーバーサイドでのエスケープ（Python + Jinja2）:**

```python
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/welcome')
def welcome():
    username = request.args.get('name', '')

    # Jinja2 は自動的にエスケープ
    template = "<h1>Welcome, {{ username }}!</h1>"
    return render_template_string(template, username=username)

    # 自動エスケープを無効化しないこと
    # {{ username|safe }} は危険
```

## 認証・認可の脆弱性

### 不適切なパスワード保存

**脆弱なコード:**

```python
# 危険: 平文保存
def create_user(username, password):
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)  # 平文で保存
    )

# 危険: MD5/SHA1 ハッシュのみ
import hashlib

def create_user(username, password):
    password_hash = hashlib.md5(password.encode()).hexdigest()
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)  # ソルトなし、高速すぎる
    )
```

**安全なコード:**

```python
import bcrypt

def create_user(username, password):
    # bcrypt: 自動的にソルト生成、計算コスト高い
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)  # コストファクター
    )

    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )

def verify_password(username, password):
    user = db.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        return False

    return bcrypt.checkpw(
        password.encode('utf-8'),
        user['password_hash']
    )
```

**Argon2 を使用（推奨）:**

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

def create_user(username, password):
    password_hash = ph.hash(password)

    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )

def verify_password(username, password):
    user = db.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user:
        return False

    try:
        ph.verify(user['password_hash'], password)
        return True
    except:
        return False
```

### IDOR（Insecure Direct Object Reference）

**脆弱なコード:**

```python
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    # 危険: 認可チェックなし
    order = db.query(Order).get(order_id)
    return jsonify(order.to_dict())

# 攻撃例: 他人の注文も見れてしまう
# GET /api/orders/1
# GET /api/orders/2  ← 他人の注文
```

**安全なコード:**

```python
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    current_user = get_current_user()

    # 安全: 認可チェック
    order = db.query(Order).filter_by(
        id=order_id,
        user_id=current_user.id  # 自分の注文のみ
    ).first()

    if not order:
        return jsonify({'error': 'Not found'}), 404

    return jsonify(order.to_dict())
```

### セッション固定攻撃

**脆弱なコード:**

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if verify_credentials(username, password):
        # 危険: 既存のセッションIDを再利用
        session['user_id'] = get_user_id(username)
        return redirect('/dashboard')

    return 'Invalid credentials', 401
```

**安全なコード:**

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if verify_credentials(username, password):
        # 安全: セッションIDを再生成
        session.clear()
        session.regenerate()  # 新しいセッションID

        session['user_id'] = get_user_id(username)
        return redirect('/dashboard')

    return 'Invalid credentials', 401
```

### JWT の不適切な使用

**脆弱なコード:**

```python
import jwt

SECRET_KEY = "secret"

# 危険: アルゴリズムを "none" に変更可能
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256', 'none'])
        return payload
    except:
        return None

# 攻撃例: algorithms=['none'] で署名なしトークンを受け入れてしまう
```

**安全なコード:**

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ['JWT_SECRET_KEY']  # 環境変数から取得

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # 有効期限
        'iat': datetime.utcnow(),  # 発行時刻
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        # 安全: アルゴリズムを明示的に指定
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256']  # 単一のアルゴリズムのみ
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

## 暗号化の問題

### 弱い暗号化

**脆弱なコード:**

```python
# 危険: ECB モード
from Crypto.Cipher import AES

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_ECB)  # ECB は危険
    return cipher.encrypt(data)
```

**安全なコード:**

```python
from cryptography.fernet import Fernet
import os

def encrypt_data(data: str) -> tuple[bytes, bytes]:
    # 鍵の生成（初回のみ、安全に保存）
    key = Fernet.generate_key()
    fernet = Fernet(key)

    # 暗号化
    encrypted = fernet.encrypt(data.encode())

    return encrypted, key

def decrypt_data(encrypted: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode()

# AES-GCM を使用する場合
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_with_aes_gcm(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)  # 96-bit nonce
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext, nonce
```

### 不適切な乱数生成

**脆弱なコード:**

```python
import random

# 危険: 予測可能な乱数
def generate_token():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

# 危険: 時刻ベースのシード
random.seed(int(time.time()))
session_id = random.randint(1000000, 9999999)
```

**安全なコード:**

```python
import secrets

# 安全: 暗号論的に安全な乱数
def generate_token():
    return secrets.token_hex(32)  # 64文字の16進数

def generate_session_id():
    return secrets.token_urlsafe(32)  # URL安全な文字列

# パスワードリセットトークン
def generate_reset_token():
    return secrets.token_urlsafe(32)
```

## セキュリティ設定の例

### HTTPセキュリティヘッダー

**Express.js での実装:**

```javascript
const helmet = require('helmet');
const express = require('express');

const app = express();

// Helmet で基本的なヘッダーを設定
app.use(helmet());

// カスタム設定
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    scriptSrc: ["'self'"],
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    frameSrc: ["'none'"],
  },
}));

app.use(helmet.hsts({
  maxAge: 31536000,  // 1年
  includeSubDomains: true,
  preload: true
}));
```

**Nginx での実装:**

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # セキュリティヘッダー
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # その他のセキュリティ設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # クリックジャッキング対策
    add_header X-Frame-Options "SAMEORIGIN" always;
}
```

### CORS の適切な設定

**脆弱なコード:**

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# 危険: すべてのオリジンを許可
CORS(app, resources={r"/*": {"origins": "*"}})
```

**安全なコード:**

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# 安全: 特定のオリジンのみ許可
ALLOWED_ORIGINS = [
    'https://example.com',
    'https://app.example.com'
]

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Total-Count"],
        "supports_credentials": True,
        "max_age": 3600
    }
})
```

### CSRF 対策

**Django での実装:**

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF ミドルウェア
    # ...
]

# テンプレート
# <form method="post">
#     {% csrf_token %}
#     <!-- フォームフィールド -->
# </form>
```

**Express.js での実装:**

```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

app.use(cookieParser());

// CSRF 保護
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/process', csrfProtection, (req, res) => {
  res.send('Form processed');
});
```

## セキュアコーディングパターン

### 入力検証のパターン

```python
from typing import Optional
import re

class InputValidator:
    """入力検証クラス"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """メールアドレスの検証"""
        if not email or len(email) > 254:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> bool:
        """ユーザー名の検証"""
        if not username or len(username) < 3 or len(username) > 30:
            return False

        # 英数字とアンダースコアのみ
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_url(url: str, allowed_schemes: list = ['http', 'https']) -> bool:
        """URL の検証"""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.scheme in allowed_schemes and bool(parsed.netloc)
        except:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """ファイル名のサニタイゼーション"""
        # 危険な文字を削除
        safe_filename = re.sub(r'[^\w\s\-\.]', '', filename)

        # パストラバーサル対策
        safe_filename = safe_filename.replace('..', '')

        # 長さ制限
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:255-len(ext)] + ext

        return safe_filename

# 使用例
def create_user(email: str, username: str):
    if not InputValidator.validate_email(email):
        raise ValueError("Invalid email")

    if not InputValidator.validate_username(username):
        raise ValueError("Invalid username")

    # ユーザー作成処理
```

### セキュアなファイルアップロード

```python
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/var/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file'}, 400

    file = request.files['file']

    if file.filename == '':
        return {'error': 'No filename'}, 400

    # ファイル名の検証
    if not allowed_file(file.filename):
        return {'error': 'File type not allowed'}, 400

    # ファイルサイズの検証
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return {'error': 'File too large'}, 400

    # 安全なファイル名に変換
    filename = secure_filename(file.filename)

    # ユーザーごとのディレクトリに保存
    user_dir = os.path.join(UPLOAD_FOLDER, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    # ファイル保存
    filepath = os.path.join(user_dir, filename)
    file.save(filepath)

    return {'filename': filename}, 200
```

### レート制限の実装

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ログインエンドポイント: 厳しい制限
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ログイン処理
    pass

# API エンドポイント: 通常の制限
@app.route('/api/data', methods=['GET'])
@limiter.limit("100 per hour")
def get_data():
    # データ取得処理
    pass

# パスワードリセット: 非常に厳しい制限
@app.route('/api/password-reset', methods=['POST'])
@limiter.limit("3 per hour")
def password_reset():
    # パスワードリセット処理
    pass
```

### セキュアなAPI設計

```python
from functools import wraps
from flask import request, jsonify
import jwt

def require_api_key(f):
    """API キー認証デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated_function

def require_jwt(f):
    """JWT 認証デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token required'}), 401

        try:
            # "Bearer <token>" 形式
            token = token.split(' ')[1]

            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )

            request.user_id = payload['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

# 使用例
@app.route('/api/public')
def public_endpoint():
    return jsonify({'message': 'Public endpoint'})

@app.route('/api/protected')
@require_jwt
def protected_endpoint():
    return jsonify({'message': 'Protected endpoint'})

@app.route('/api/admin')
@require_jwt
@require_admin
def admin_endpoint():
    return jsonify({'message': 'Admin endpoint'})
```

## まとめ

セキュリティ監査の重要原則:

1. **多層防御** - 単一の防御に頼らない
2. **最小権限** - 必要最小限の権限のみ付与
3. **Fail Secure** - 失敗時は安全側に倒す
4. **入力検証** - すべての入力を検証
5. **出力エンコーディング** - 文脈に応じたエスケープ
6. **暗号化** - 実績のあるアルゴリズムとライブラリ
7. **監視とログ** - セキュリティイベントの記録

詳細なセキュリティ監査プロセスについては、[SKILL.md](SKILL.md) を参照してください。
