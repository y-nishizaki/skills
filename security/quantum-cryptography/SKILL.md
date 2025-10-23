---
name: "quantum-cryptography"
description: >
  量子暗号とポスト量子暗号の理解を支援します。量子計算機がもたらす暗号崩壊のリスク、
  耐量子暗号アルゴリズム（NIST標準化）、量子鍵配送（QKD）、量子耐性への移行戦略など、
  量子時代の暗号技術に使用します。
  キーワード - 量子暗号、ポスト量子暗号、量子コンピュータ、耐量子性、QKD、
  NIST PQC、暗号移行。
version: 1.0.0
---

# 量子暗号・ポスト量子暗号スキル

## 目的

このスキルは、量子計算時代の暗号技術を理解し、準備するための知識を提供します。
量子コンピュータによる現行暗号の脅威、ポスト量子暗号（PQC）アルゴリズム、
量子鍵配送（QKD）、移行戦略など、実践的な対応策を含みます。

## 量子脅威

### 現行暗号への影響

**脆弱な暗号:**
- **RSA**: Shorのアルゴリズムで破られる
- **ECC（楕円曲線暗号）**: Shorのアルゴリズムで破られる
- **Diffie-Hellman**: 鍵交換が危殆化
- **DSA/ECDSA**: デジタル署名が偽造可能

**比較的安全な暗号:**
- **AES**: Groverのアルゴリズムで効率低下（鍵長倍増で対応）
- **SHA-2/SHA-3**: 同様に一部効率低下

### 量子計算の脅威タイムライン

**現在の見積もり:**
- 2030年代初期: 実用的な量子コンピュータ
- 暗号学的に有意な量子コンピュータ（CRQC）: 10-20年

**Harvest Now, Decrypt Later攻撃:**
- 現在暗号化データを収集
- 将来の量子コンピュータで復号
- 長期機密データは今すぐ保護必要

## ポスト量子暗号（PQC）

### NIST標準化プロセス

**選定アルゴリズム（2022年7月）:**

**公開鍵暗号/KEM:**
1. **CRYSTALS-Kyber**（鍵カプセル化）
   - 格子ベース
   - 高速、小サイズ
   - 推奨用途: 一般的な暗号化

**デジタル署名:**
1. **CRYSTALS-Dilithium**
   - 格子ベース
   - 高速署名・検証
   - 推奨用途: 一般的な署名

2. **Falcon**
   - 格子ベース（NTRU）
   - 小さい署名サイズ
   - 推奨用途: 制約環境

3. **SPHINCS+**
   - ハッシュベース
   - 保守的選択
   - 推奨用途: 長期署名

**追加選定中:**
- BIKE
- HQC
- Classic McEliece
- SIKE（後に脆弱性発見で除外）

### アルゴリズム実装

**Kyberサンプル（概念的）:**

```python
# liboqs-python を使用
from oqs import KeyEncapsulation

# 鍵生成
kem = KeyEncapsulation("Kyber512")
public_key = kem.generate_keypair()

# カプセル化（送信側）
ciphertext, shared_secret_sender = kem.encap_secret(public_key)

# デカプセル化（受信側）
shared_secret_receiver = kem.decap_secret(ciphertext)

# 共有秘密が一致
assert shared_secret_sender == shared_secret_receiver
```

**Dilithiumサンプル:**

```python
from oqs import Signature

# 鍵生成
sig = Signature("Dilithium2")
public_key = sig.generate_keypair()

# 署名
message = b"Important message"
signature = sig.sign(message)

# 検証
is_valid = sig.verify(message, signature, public_key)
```

### ハイブリッドアプローチ

現行暗号とPQCを組み合わせ:

```python
def hybrid_kex():
    """
    ハイブリッド鍵交換
    ECDH + Kyber
    """
    from cryptography.hazmat.primitives.asymmetric import ec
    from oqs import KeyEncapsulation

    # ECDH
    ecdh_private = ec.generate_private_key(ec.SECP256R1())
    ecdh_public = ecdh_private.public_key()
    ecdh_shared = ecdh_private.exchange(ec.ECDH(), peer_ecdh_public)

    # Kyber
    kem = KeyEncapsulation("Kyber768")
    kyber_public = kem.generate_keypair()
    ciphertext, kyber_shared = kem.encap_secret(kyber_public)

    # 結合
    import hashlib
    combined_secret = hashlib.sha256(
        ecdh_shared + kyber_shared
    ).digest()

    return combined_secret
```

## 量子鍵配送（QKD）

### BB84プロトコル

**原理:**
1. Aliceが量子状態でビット送信
2. Bobがランダムな基底で測定
3. 公開チャネルで基底照合
4. 一致した測定のみ使用
5. 盗聴検出（エラー率確認）

**セキュリティ保証:**
- 量子力学の不確定性原理
- 盗聴は必ず検出可能

**商用QKDシステム:**
- ID Quantique
- Toshiba
- QuantumCTek

**制限:**
- 距離制限（〜100km、ファイバー）
- 高コスト
- 専用インフラ必要

## 移行戦略

### 暗号インベントリ

```markdown
# 暗号資産棚卸し

## システムA
- プロトコル: TLS 1.3
- 鍵交換: ECDHE (P-256)
- 署名: ECDSA
- 暗号化: AES-256-GCM
- 証明書: RSA 2048ビット
- リスク: 高（RSA、ECC使用）
- 優先度: P1

## システムB
- プロトコル: SSH
- 鍵交換: Curve25519
- 暗号化: ChaCha20-Poly1305
- リスク: 中（ECC使用）
- 優先度: P2
```

### 移行ロードマップ

```
フェーズ1（2024-2025）: 準備
- 暗号インベントリ作成
- リスク評価
- PQCアルゴリズム選定
- パイロットプロジェクト

フェーズ2（2025-2027）: ハイブリッド移行
- ハイブリッド暗号実装
- 重要システム優先
- 互換性確保

フェーズ3（2027-2030）: 完全移行
- PQCへ完全移行
- 旧暗号の廃止
- 継続的監視

フェーズ4（2030+）: 維持・更新
- 新標準への対応
- 量子脅威の監視
```

### TLS 1.3 ハイブリッド設定

OpenSSL 3.0+ with OQS プロバイダ:

```bash
# OQS プロバイダビルド
git clone https://github.com/open-quantum-safe/oqs-provider.git
cd oqs-provider
mkdir build && cd build
cmake -DOPENSSL_ROOT_DIR=/usr/local/openssl ..
make && make install

# サーバー設定
openssl s_server \
  -cert server_cert.pem \
  -key server_key.pem \
  -groups kyber512:x25519 \  # ハイブリッド
  -www
```

### 証明書管理

**PQC証明書:**
```bash
# Dilithium秘密鍵生成
openssl genpkey -algorithm dilithium2 -out dilithium_key.pem

# CSR作成
openssl req -new -key dilithium_key.pem -out dilithium.csr

# ハイブリッド証明書（将来）
openssl req -new \
  -key rsa_key.pem \
  -key dilithium_key.pem \
  -out hybrid.csr
```

## 実装ガイダンス

### ライブラリ

**liboqs:**
- Open Quantum Safe project
- C言語実装
- 多数のPQCアルゴリズム

```c
#include <oqs/oqs.h>

int main() {
    OQS_KEM *kem = OQS_KEM_new(OQS_KEM_alg_kyber_512);

    uint8_t *public_key = malloc(kem->length_public_key);
    uint8_t *secret_key = malloc(kem->length_secret_key);

    OQS_KEM_keypair(kem, public_key, secret_key);

    uint8_t *ciphertext = malloc(kem->length_ciphertext);
    uint8_t *shared_secret_e = malloc(kem->length_shared_secret);

    OQS_KEM_encaps(kem, ciphertext, shared_secret_e, public_key);

    uint8_t *shared_secret_d = malloc(kem->length_shared_secret);
    OQS_KEM_decaps(kem, shared_secret_d, ciphertext, secret_key);

    // shared_secret_e == shared_secret_d

    OQS_KEM_free(kem);
    return 0;
}
```

**pqcrypto (Rust):**
```rust
use pqcrypto_kyber::kyber512;

fn main() {
    let (pk, sk) = kyber512::keypair();
    let (ss1, ct) = kyber512::encapsulate(&pk);
    let ss2 = kyber512::decapsulate(&ct, &sk);
    assert_eq!(ss1, ss2);
}
```

## パフォーマンス考慮事項

### アルゴリズム比較

| アルゴリズム | 公開鍵 | 秘密鍵 | 暗号文 | 署名 |
|------------|-------|-------|--------|-----|
| RSA-2048 | 256 B | 256 B | 256 B | 256 B |
| Kyber512 | 800 B | 1632 B | 768 B | - |
| Dilithium2 | 1312 B | 2528 B | - | 2420 B |

**影響:**
- ネットワーク帯域幅増加
- ストレージ要件増加
- 計算オーバーヘッド（一部は高速）

### 最適化

```python
def optimize_pqc_deployment():
    """
    PQC最適化戦略
    """
    strategies = {
        '証明書チェーン圧縮': '中間CA証明書の最小化',
        'セッション再利用': 'TLSセッションキャッシュ',
        'キャッシング': '公開鍵のキャッシュ',
        '選択的使用': '重要通信のみPQC'
    }
    return strategies
```

## セキュリティ考慮事項

### サイドチャネル攻撃

**対策:**
- 定数時間実装
- マスキング
- ブラインディング

### 実装脆弱性

**検証:**
- 暗号学的テストベクター
- ファジング
- コードレビュー

### 鍵管理

**PQC特有の課題:**
- 鍵サイズ増大
- 鍵の安全な保管
- 鍵のライフサイクル管理

## 標準化動向

**主要標準:**
- NIST FIPS 203/204/205（策定中）
- IETF Hybrid Key Exchange
- ETSI Quantum-Safe Cryptography

**業界動向:**
- CNSA 2.0 (NSA)
- BSI TR-02102 (ドイツ)
- ANSSI (フランス)

## ベストプラクティス

1. **今すぐ開始**
   - 暗号インベントリ作成
   - リスク評価
   - パイロットプロジェクト

2. **暗号俊敏性（Crypto Agility）**
   - 容易に暗号切り替え可能な設計
   - ハードコード回避
   - 設定ベース

3. **ハイブリッドアプローチ**
   - 移行期間の安全性確保
   - 互換性維持

4. **継続的監視**
   - 標準化動向
   - 脆弱性情報
   - 量子計算進歩

## 参考リソース

- NIST Post-Quantum Cryptography Standardization
- Open Quantum Safe Project
- Cloud Security Alliance - Quantum-Safe Security
- ETSI Quantum Safe Cryptography

## 注意事項

- PQCは進化中の分野
- 標準は暫定的
- 早期採用にはリスクあり
- 専門家の助言推奨
