---
name: "cryptography"
description: >
  暗号技術の基礎と実践を支援します。対称・非対称暗号、ハッシュ関数、デジタル署名、SSL/TLS、
  公開鍵基盤（PKI）、証明書管理など、暗号化技術の実装と分析、セキュアな通信設計に使用します。
  キーワード - 暗号、暗号化、復号化、ハッシュ、デジタル署名、SSL、TLS、PKI、証明書、
  AES、RSA、ECC。
version: 1.0.0
---

# 暗号技術スキル

## 目的

このスキルは、暗号技術の理論と実践的な応用に関する包括的な知識を提供します。
対称暗号、非対称暗号、ハッシュ関数、デジタル署名、SSL/TLS、公開鍵基盤（PKI）など、
現代の暗号技術を理解し、適切に実装するためのガイダンスを含みます。

## このスキルを使用する場合

以下の場合にこのスキルを使用します:

- ユーザーが暗号化の実装や暗号アルゴリズムの選択を求めた場合
- ユーザーがSSL/TLS証明書の設定や管理を必要とする場合
- ユーザーがデジタル署名や鍵管理の実装を求めた場合
- ユーザーがハッシュ関数の適切な使用法を知りたい場合
- ユーザーがPKIや証明書管理について質問した場合
- ユーザーが「暗号化」、「暗号」、「証明書」、「SSL/TLS」と言及した場合

## 暗号技術の基礎

### 暗号の基本概念

**主要な目標:**
1. **機密性（Confidentiality）**: 認可されたユーザーのみがデータにアクセス可能
2. **完全性（Integrity）**: データが改ざんされていないことを保証
3. **認証（Authentication）**: 通信相手が本物であることを証明
4. **否認防止（Non-repudiation）**: 送信者が送信を否定できない

### 暗号の分類

1. **対称鍵暗号（Symmetric Encryption）**
   - 暗号化と復号化に同じ鍵を使用
   - 高速
   - 鍵配送問題がある

2. **非対称鍵暗号（Asymmetric Encryption）**
   - 公開鍵と秘密鍵のペアを使用
   - 低速
   - 鍵配送問題が解決される

3. **ハッシュ関数（Hash Functions）**
   - 一方向関数
   - 固定長の出力
   - 完全性検証に使用

## 対称鍵暗号

### 主要なアルゴリズム

#### AES (Advanced Encryption Standard)

**特徴:**
- ブロック暗号（128ビットブロック）
- 鍵長: 128, 192, 256ビット
- 現代の標準暗号
- 高速で安全

**OpenSSL使用例:**

```bash
# ファイル暗号化（AES-256-CBC）
openssl enc -aes-256-cbc -salt -in plaintext.txt -out encrypted.bin -k password

# ファイル復号化
openssl enc -d -aes-256-cbc -in encrypted.bin -out decrypted.txt -k password

# AES-256-GCM（推奨モード）
openssl enc -aes-256-gcm -in plaintext.txt -out encrypted.bin -K $(openssl rand -hex 32) -iv $(openssl rand -hex 12)
```

**Pythonでの実装:**

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# AES-256-GCMによる暗号化
def encrypt_aes_gcm(plaintext, key):
    iv = os.urandom(12)
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag

# AES-256-GCMによる復号化
def decrypt_aes_gcm(ciphertext, key, iv, tag):
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# 使用例
key = os.urandom(32)  # 256ビット鍵
plaintext = b"Secret message"
iv, ciphertext, tag = encrypt_aes_gcm(plaintext, key)
decrypted = decrypt_aes_gcm(ciphertext, key, iv, tag)
```

#### ChaCha20-Poly1305

**特徴:**
- ストリーム暗号
- AESより高速（特にハードウェア支援なし環境）
- 認証付き暗号（AEAD）
- Googleが推奨

**OpenSSL使用例:**

```bash
# ChaCha20-Poly1305での暗号化
openssl enc -chacha20-poly1305 -in plaintext.txt -out encrypted.bin -K $(openssl rand -hex 32) -iv $(openssl rand -hex 12)
```

### 暗号化モード

**ブロック暗号モード:**

1. **ECB (Electronic Codebook)** - 使用禁止
   - 同じ平文ブロックが同じ暗号文に
   - パターンが漏洩

2. **CBC (Cipher Block Chaining)**
   - 前のブロックとXOR
   - IV（初期化ベクトル）が必要
   - パディングオラクル攻撃に注意

3. **CTR (Counter)**
   - ブロック暗号をストリーム暗号として使用
   - 並列化可能
   - IVの再利用は禁物

4. **GCM (Galois/Counter Mode)** - 推奨
   - 認証付き暗号（AEAD）
   - 高速
   - 完全性と機密性を同時に提供

**AEAD (Authenticated Encryption with Associated Data):**
- GCM
- CCM
- ChaCha20-Poly1305
- これらの使用を推奨

### 鍵管理

**鍵生成:**

```bash
# ランダムな鍵生成
openssl rand -hex 32  # 256ビット（64文字の16進数）
openssl rand -base64 32  # Base64エンコード

# パスワードベース鍵導出（PBKDF2）
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -in file.txt -out file.enc
```

**Python PBKDF2:**

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os

password = b"user_password"
salt = os.urandom(16)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,  # OWASP推奨（2023）
)
key = kdf.derive(password)
```

## 非対称鍵暗号

### RSA (Rivest-Shamir-Adleman)

**特徴:**
- 最も広く使用される公開鍵暗号
- 鍵長: 2048ビット以上推奨（4096ビット推奨）
- 暗号化、署名、鍵交換に使用

**鍵生成:**

```bash
# RSA鍵ペア生成
openssl genrsa -out private_key.pem 4096
openssl rsa -in private_key.pem -pubout -out public_key.pem

# パスワード保護された秘密鍵
openssl genrsa -aes256 -out private_key_encrypted.pem 4096
```

**暗号化と復号化:**

```bash
# 公開鍵で暗号化
openssl rsautl -encrypt -pubin -inkey public_key.pem -in plaintext.txt -out encrypted.bin

# 秘密鍵で復号化
openssl rsautl -decrypt -inkey private_key.pem -in encrypted.bin -out decrypted.txt
```

**Python RSA:**

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# 鍵生成
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)
public_key = private_key.public_key()

# 暗号化
ciphertext = public_key.encrypt(
    b"Secret message",
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# 復号化
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

### ECC (Elliptic Curve Cryptography)

**特徴:**
- RSAより短い鍵長で同等のセキュリティ
- 高速
- モバイル/IoTデバイスに適している

**推奨曲線:**
- P-256 (secp256r1) - 最小推奨
- P-384 (secp384r1) - より安全
- Curve25519 - EdDSA署名用
- Curve448

**鍵生成:**

```bash
# ECCキーペア生成（P-256）
openssl ecparam -name prime256v1 -genkey -noout -out ec_private_key.pem
openssl ec -in ec_private_key.pem -pubout -out ec_public_key.pem

# Curve25519（Ed25519）
openssl genpkey -algorithm Ed25519 -out ed25519_private_key.pem
openssl pkey -in ed25519_private_key.pem -pubout -out ed25519_public_key.pem
```

**Python ECC:**

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

# 鍵生成
private_key = ec.generate_private_key(ec.SECP384R1())
public_key = private_key.public_key()

# ECDH（鍵交換）
shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
```

## ハッシュ関数

### 主要なハッシュアルゴリズム

**安全なハッシュ関数:**
- SHA-256
- SHA-384
- SHA-512
- SHA-3 (Keccak)
- BLAKE2

**使用禁止:**
- MD5（完全に破られている）
- SHA-1（衝突攻撃が実用的）

**OpenSSL使用例:**

```bash
# SHA-256ハッシュ
echo -n "message" | openssl dgst -sha256
openssl dgst -sha256 filename

# ファイルのSHA-512ハッシュ
openssl dgst -sha512 file.txt

# HMAC（鍵付きハッシュ）
echo -n "message" | openssl dgst -sha256 -hmac "secret_key"
```

**Python ハッシュ:**

```python
import hashlib

# SHA-256
hash_obj = hashlib.sha256()
hash_obj.update(b"message")
digest = hash_obj.hexdigest()

# ファイルのハッシュ
def hash_file(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# HMAC
import hmac
signature = hmac.new(b"secret_key", b"message", hashlib.sha256).hexdigest()
```

### パスワードハッシュ

**推奨アルゴリズム:**
1. **Argon2** - OWASP推奨、最新
2. **bcrypt** - 広く使用されている
3. **scrypt** - メモリハード関数
4. **PBKDF2** - 標準、最低限

**使用禁止:**
- 単純なハッシュ（SHA-256など）
- Salt なし
- 低い反復回数

**Python bcrypt:**

```python
import bcrypt

# パスワードのハッシュ化
password = b"user_password"
salt = bcrypt.gensalt(rounds=12)  # 作業係数
hashed = bcrypt.hashpw(password, salt)

# パスワードの検証
if bcrypt.checkpw(password, hashed):
    print("パスワード一致")
```

**Python Argon2:**

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# ハッシュ化
hash = ph.hash("user_password")

# 検証
try:
    ph.verify(hash, "user_password")
    print("パスワード一致")
except:
    print("パスワード不一致")
```

## デジタル署名

### 署名の仕組み

1. メッセージのハッシュを計算
2. 秘密鍵でハッシュを署名
3. 署名とメッセージを送信
4. 受信者が公開鍵で署名を検証

### RSA署名

**OpenSSL:**

```bash
# メッセージに署名
openssl dgst -sha256 -sign private_key.pem -out signature.bin message.txt

# 署名の検証
openssl dgst -sha256 -verify public_key.pem -signature signature.bin message.txt
```

**Python:**

```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# 署名
signature = private_key.sign(
    b"message",
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# 検証
try:
    public_key.verify(
        signature,
        b"message",
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("署名は有効")
except:
    print("署名は無効")
```

### ECDSA署名

```bash
# EC鍵で署名
openssl dgst -sha256 -sign ec_private_key.pem -out signature.bin message.txt

# 検証
openssl dgst -sha256 -verify ec_public_key.pem -signature signature.bin message.txt
```

### EdDSA (Ed25519)

**特徴:**
- 非常に高速
- 実装が簡単で安全
- 決定論的署名

```bash
# Ed25519署名
openssl pkeyutl -sign -inkey ed25519_private_key.pem -rawin -in message.txt -out signature.bin
openssl pkeyutl -verify -pubin -inkey ed25519_public_key.pem -rawin -in message.txt -sigfile signature.bin
```

## SSL/TLS

### TLSの基礎

**TLSバージョン:**
- TLS 1.3 - 最新、推奨
- TLS 1.2 - 最低限サポート
- TLS 1.1以下 - 使用禁止

**TLSハンドシェイク（TLS 1.3簡略版）:**
1. ClientHello
2. ServerHello + 証明書 + ServerKeyExchange
3. クライアント検証
4. 暗号化通信開始

### 証明書の作成と管理

#### 自己署名証明書

```bash
# 自己署名証明書生成（開発用）
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Company/CN=example.com"

# より詳細な設定
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout key.pem -out cert.pem \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Company/CN=example.com" \
  -addext "subjectAltName=DNS:example.com,DNS:www.example.com,IP:192.168.1.1"
```

#### CSR（証明書署名要求）

```bash
# 秘密鍵生成
openssl genrsa -out private.key 4096

# CSR作成
openssl req -new -key private.key -out request.csr \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Company/CN=example.com"

# CSR内容確認
openssl req -text -noout -in request.csr
```

#### CA（認証局）の作成

```bash
# CA秘密鍵生成
openssl genrsa -aes256 -out ca-key.pem 4096

# CA証明書作成
openssl req -new -x509 -days 3650 -key ca-key.pem -sha256 -out ca.pem \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Company CA/CN=Company Root CA"

# CSRに署名
openssl x509 -req -in request.csr -CA ca.pem -CAkey ca-key.pem \
  -CAcreateserial -out cert.pem -days 365 -sha256
```

### 証明書の検証と管理

```bash
# 証明書内容確認
openssl x509 -in cert.pem -text -noout

# 証明書の有効期限確認
openssl x509 -in cert.pem -noout -dates

# 証明書チェーンの検証
openssl verify -CAfile ca.pem cert.pem

# リモートサーバーの証明書確認
openssl s_client -connect example.com:443 -servername example.com < /dev/null

# 証明書のフィンガープリント
openssl x509 -in cert.pem -noout -fingerprint -sha256
```

**Python証明書確認:**

```python
import ssl
import socket

# サーバー証明書取得
hostname = 'example.com'
context = ssl.create_default_context()
with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
        print(cert)
```

### 暗号スイート

**推奨暗号スイート（TLS 1.3）:**
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

**推奨暗号スイート（TLS 1.2）:**
- ECDHE-RSA-AES256-GCM-SHA384
- ECDHE-RSA-AES128-GCM-SHA256
- ECDHE-RSA-CHACHA20-POLY1305

**非推奨:**
- RC4
- 3DES
- CBC モード（TLS 1.2）
- MD5/SHA1

**OpenSSL設定:**

```
# OpenSSL.conf または nginx/apache設定
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-CHACHA20-POLY1305';
ssl_prefer_server_ciphers on;
```

## 公開鍵基盤（PKI）

### PKIの構成要素

1. **CA（認証局）**
   - ルートCA
   - 中間CA
   - 発行CA

2. **RA（登録局）**
   - 証明書要求の検証
   - ユーザー認証

3. **証明書リポジトリ**
   - 証明書の保管と配布

4. **CRL（証明書失効リスト）**
   - 失効した証明書のリスト

5. **OCSP（Online Certificate Status Protocol）**
   - リアルタイム証明書状態確認

### 証明書の失効

**CRL生成:**

```bash
# CRL作成
openssl ca -gencrl -out crl.pem -config openssl.conf

# CRL内容確認
openssl crl -in crl.pem -noout -text

# 証明書の失効
openssl ca -revoke cert.pem -config openssl.conf
```

**OCSP:**

```bash
# OCSPレスポンダー起動
openssl ocsp -index index.txt -port 8080 -rsigner ocsp_cert.pem -rkey ocsp_key.pem -CA ca.pem

# OCSP問い合わせ
openssl ocsp -issuer ca.pem -cert cert.pem -url http://ocsp.example.com:8080
```

## 実装のベストプラクティス

### 一般的な原則

1. **標準アルゴリズムを使用**
   - 独自暗号の開発は禁止
   - NIST、OWASP推奨アルゴリズムを使用

2. **適切な鍵長**
   - RSA: 最低2048ビット、推奨4096ビット
   - ECC: 最低256ビット、推奨384ビット
   - AES: 256ビット

3. **AEAD使用**
   - GCM、ChaCha20-Poly1305を優先
   - 暗号化と認証を分離しない

4. **ランダム性**
   - 暗号学的に安全な乱数生成器（CSPRNG）を使用
   - `/dev/urandom` (Linux)
   - `secrets` モジュール (Python)

5. **鍵管理**
   - 鍵をコードに埋め込まない
   - 環境変数、KMS、HSMを使用
   - 定期的な鍵ローテーション

### 避けるべき実践

**❌ 悪い例:**

```python
# ECBモード（パターンが漏洩）
cipher = AES.new(key, AES.MODE_ECB)

# 固定IV
iv = b'1234567890123456'

# 弱いハッシュ
hashlib.md5(data)

# パスワードを直接鍵として使用
key = password.encode()[:32]
```

**✅ 良い例:**

```python
# GCMモード
cipher = AES.new(key, AES.MODE_GCM)

# ランダムIV
iv = os.urandom(12)

# 強いハッシュ
hashlib.sha256(data)

# PBKDF2で鍵導出
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
key = kdf.derive(password)
```

## セキュリティ評価

### 暗号実装のチェックリスト

- [ ] 最新の暗号アルゴリズムを使用
- [ ] 適切な鍵長
- [ ] AEAD（認証付き暗号）を使用
- [ ] ランダムIV/Nonce
- [ ] パスワードはハッシュ化（bcrypt/Argon2）
- [ ] PBKDF2/Argon2で鍵導出
- [ ] TLS 1.2以上を使用
- [ ] 強い暗号スイート
- [ ] 証明書の検証
- [ ] 鍵のセキュアな保管
- [ ] 定期的な鍵ローテーション

### よくある脆弱性

1. **ECBモード使用**: パターンが漏洩
2. **IV再利用**: CTR/GCMモードで壊滅的
3. **パディングオラクル**: CBC モードの実装ミス
4. **タイミング攻撃**: 比較処理の時間差
5. **ダウングレード攻撃**: 古いプロトコルへの強制
6. **証明書検証の欠如**: 中間者攻撃
7. **弱い乱数**: 予測可能な鍵/IV

## ツールとライブラリ

### 推奨ライブラリ

**Python:**
- `cryptography` - 推奨、高レベルAPI
- `PyNaCl` - libsodiumのラッパー、シンプル

**JavaScript/Node.js:**
- `crypto` (組み込み)
- `node-forge`
- `tweetnacl`

**Java:**
- `Bouncy Castle`
- `javax.crypto` (JCE)

**Go:**
- `crypto` 標準ライブラリ

**C/C++:**
- `OpenSSL`
- `libsodium`

### 暗号解析ツール

```bash
# SSL Labs API
curl https://api.ssllabs.com/api/v3/analyze?host=example.com

# testssl.sh
testssl.sh example.com

# OpenSSL暗号スイート確認
openssl ciphers -v 'HIGH:!aNULL:!MD5'

# nmap SSLスキャン
nmap --script ssl-enum-ciphers -p 443 example.com
```

## 参考リソース

- NIST SP 800-175B: Guideline for Using Cryptographic Standards
- OWASP Cryptographic Storage Cheat Sheet
- RFC 8446: TLS 1.3
- FIPS 140-2/140-3 Standards
- PKCS (Public-Key Cryptography Standards)

## 注意事項

- **テスト環境**: 本番環境への適用前に必ずテストすること
- **互換性**: 暗号設定変更がクライアントに与える影響を考慮すること
- **規制遵守**: 輸出規制や暗号法規制を確認すること
- **定期的な見直し**: 暗号技術は進化するため、定期的に設定を見直すこと
- **専門家のレビュー**: 本番環境の暗号実装は専門家のレビューを推奨
