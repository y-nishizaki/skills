---
name: "os-security"
description: >
  オペレーティングシステムのセキュリティ管理を支援します。Linux/Windowsの権限管理、ログ監査、
  セキュリティ設定、Active Directoryのセキュリティ、カーネルセキュリティ、プロセス管理など、
  OSレベルでのセキュリティ対策の実装と分析に使用します。
  キーワード - OS、Linux、Windows、権限管理、ログ、Active Directory、セキュリティ設定、
  カーネル、プロセス。
version: 1.0.0
---

# OSセキュリティスキル

## 目的

このスキルは、オペレーティングシステム（Linux/Windows）のセキュリティに関する包括的な知識とベストプラクティスを提供します。
システム管理者、セキュリティエンジニア、監査担当者がOSレベルでのセキュリティ対策を実装、
評価、維持するための実践的なガイダンスを含みます。

## このスキルを使用する場合

以下の場合にこのスキルを使用します:

- ユーザーがOS（Linux/Windows）のセキュリティ設定を強化したい場合
- ユーザーが権限管理やアクセス制御の実装を求めた場合
- ユーザーがシステムログの監査や分析を必要とする場合
- ユーザーがActive Directoryのセキュリティ設計を求めた場合
- ユーザーがカーネルセキュリティやプロセス保護を実装したい場合
- ユーザーが「OS セキュリティ」、「権限管理」、「ログ監査」と言及した場合

## Linuxセキュリティ

### ユーザーとグループ管理

#### 基本的な権限管理

**ファイルパーミッション:**

```bash
# パーミッションの確認
ls -l filename

# パーミッションの変更
chmod 644 filename     # rw-r--r--
chmod 755 directory    # rwxr-xr-x
chmod 600 private_key  # rw-------

# 所有者とグループの変更
chown user:group filename
chgrp group filename

# 再帰的な変更
chmod -R 755 directory
chown -R user:group directory
```

**特殊パーミッション:**

1. **SUID (Set User ID) - 4000**
   - 実行時にファイル所有者の権限で実行
   - セキュリティリスクあり、慎重に使用

```bash
# SUID設定
chmod u+s /usr/bin/program
chmod 4755 /usr/bin/program

# SUID検索
find / -perm -4000 -type f 2>/dev/null
```

2. **SGID (Set Group ID) - 2000**
   - 実行時にファイルグループの権限で実行
   - ディレクトリに設定すると、作成ファイルがディレクトリのグループを継承

```bash
# SGID設定
chmod g+s /shared/directory
chmod 2755 /shared/directory

# SGID検索
find / -perm -2000 -type f 2>/dev/null
```

3. **Sticky Bit - 1000**
   - ディレクトリ内のファイルを所有者のみが削除可能

```bash
# Sticky Bit設定
chmod +t /tmp
chmod 1777 /shared/directory
```

#### 高度なアクセス制御

**ACL (Access Control Lists):**

```bash
# ACL確認
getfacl filename

# ACL設定
setfacl -m u:username:rwx filename
setfacl -m g:groupname:rx filename

# デフォルトACL（ディレクトリ用）
setfacl -d -m u:username:rwx directory

# ACL削除
setfacl -x u:username filename
setfacl -b filename  # すべてのACL削除
```

**SELinux (Security-Enhanced Linux):**

```bash
# SELinuxステータス確認
sestatus
getenforce

# モード変更
setenforce 0  # Permissive
setenforce 1  # Enforcing

# コンテキスト確認
ls -Z filename
ps -eZ

# コンテキスト変更
chcon -t httpd_sys_content_t /var/www/html/file
restorecon -Rv /var/www/html

# ポリシー管理
semanage port -l
semanage port -a -t http_port_t -p tcp 8080

# ブール値の確認と変更
getsebool -a
setsebool -P httpd_can_network_connect on

# 監査ログ確認
ausearch -m AVC -ts recent
```

**AppArmor:**

```bash
# ステータス確認
aa-status

# プロファイル管理
aa-enforce /etc/apparmor.d/usr.bin.program
aa-complain /etc/apparmor.d/usr.bin.program
aa-disable /etc/apparmor.d/usr.bin.program

# ログ確認
aa-logprof
```

### ユーザーアカウント管理

**セキュアなユーザー管理:**

```bash
# ユーザー作成（最小権限）
useradd -m -s /bin/bash -G wheel username
passwd username

# パスワードポリシー設定 (/etc/login.defs)
PASS_MAX_DAYS   90
PASS_MIN_DAYS   1
PASS_MIN_LEN    12
PASS_WARN_AGE   7

# パスワード複雑性 (/etc/pam.d/system-auth or /etc/security/pwquality.conf)
# minlen = 12
# minclass = 3
# maxrepeat = 2

# アカウントロック
faillock --user username --reset
pam_tally2 --user=username --reset

# sudo設定 (/etc/sudoers)
# visudo コマンドで編集
username ALL=(ALL) NOPASSWD: /usr/bin/specific-command

# ログインシェルの無効化（サービスアカウント）
usermod -s /sbin/nologin username

# アカウントの有効期限
chage -E 2025-12-31 username
chage -l username  # 確認
```

### システムログとモニタリング

#### Syslog/Journald

**Journald（systemd）:**

```bash
# ログ確認
journalctl -xe                    # すべてのログ（末尾）
journalctl -u sshd.service        # 特定のサービス
journalctl -p err                 # エラーレベル以上
journalctl --since "1 hour ago"   # 時間指定
journalctl -f                     # リアルタイム監視

# 特定ユーザーのログ
journalctl _UID=1000

# カーネルメッセージ
journalctl -k

# ログの永続化設定 (/etc/systemd/journald.conf)
Storage=persistent
```

**Rsyslog:**

```bash
# 設定ファイル: /etc/rsyslog.conf, /etc/rsyslog.d/

# リモートログ送信
*.* @@remote-host:514  # TCP
*.* @remote-host:514   # UDP

# ファシリティとプライオリティ
auth,authpriv.*         /var/log/auth.log
*.*                     /var/log/syslog
*.emerg                 :omusrmsg:*
```

#### 監査システム (auditd)

```bash
# auditd起動
systemctl start auditd
systemctl enable auditd

# ルール確認
auditctl -l

# ファイルアクセス監査
auditctl -w /etc/passwd -p wa -k passwd_changes
auditctl -w /etc/shadow -p wa -k shadow_changes
auditctl -w /etc/sudoers -p wa -k sudoers_changes

# システムコール監査
auditctl -a always,exit -F arch=b64 -S execve -k process_execution

# ログ検索
ausearch -k passwd_changes
ausearch -m USER_LOGIN --start today
ausearch -ua 1000  # 特定ユーザー

# レポート生成
aureport
aureport -au  # 認証レポート
aureport -x   # 実行レポート
```

#### 重要なログファイル

```
/var/log/auth.log (Debian) または /var/log/secure (Red Hat)  - 認証ログ
/var/log/syslog または /var/log/messages                      - システムログ
/var/log/kern.log                                             - カーネルログ
/var/log/cron                                                 - Cronジョブ
/var/log/mail.log                                             - メールログ
/var/log/apache2/ または /var/log/httpd/                      - Webサーバー
~/.bash_history                                               - コマンド履歴
/var/log/wtmp, /var/log/btmp, /var/log/lastlog              - ログイン記録
```

**ログ分析コマンド:**

```bash
# ログイン履歴
last
last -f /var/log/wtmp
lastb  # 失敗したログイン試行

# 現在のログインユーザー
who
w

# 最後のログイン
lastlog

# 認証ログの分析
grep "Failed password" /var/log/auth.log
grep "Accepted publickey" /var/log/auth.log
```

### カーネルセキュリティ

#### Sysctl設定

```bash
# /etc/sysctl.conf または /etc/sysctl.d/*.conf

# IP forwarding無効化（ルーターでない場合）
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# SYNクッキー有効化（SYN flood対策）
net.ipv4.tcp_syncookies = 1

# ICMP redirects無効化
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Source routing無効化
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Reverse path filtering
net.ipv4.conf.all.rp_filter = 1

# ICMP echo request無視（ping応答しない）
net.ipv4.icmp_echo_ignore_all = 1

# ログマーシャンパケット
net.ipv4.conf.all.log_martians = 1

# 設定反映
sysctl -p
```

#### カーネルモジュール管理

```bash
# ロード済みモジュール確認
lsmod

# モジュール情報
modinfo module_name

# モジュールロード
modprobe module_name

# モジュールアンロード
modprobe -r module_name

# 不要なモジュールの無効化 (/etc/modprobe.d/blacklist.conf)
blacklist usb-storage
blacklist firewire-core
```

### ネットワークセキュリティ

#### Firewall (iptables/nftables/firewalld)

**iptables:**

```bash
# 現在のルール確認
iptables -L -n -v

# デフォルトポリシー
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# SSH許可
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Established接続許可
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Loopback許可
iptables -A INPUT -i lo -j ACCEPT

# ルール保存
iptables-save > /etc/iptables/rules.v4
```

**firewalld:**

```bash
# ステータス確認
firewall-cmd --state

# ゾーン管理
firewall-cmd --get-active-zones
firewall-cmd --zone=public --add-service=http --permanent
firewall-cmd --zone=public --add-port=8080/tcp --permanent
firewall-cmd --reload

# Rich rules
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'
```

### プロセスセキュリティ

#### プロセス管理と監視

```bash
# プロセス一覧
ps aux
ps -ef
pstree

# リアルタイム監視
top
htop

# 特定プロセスの詳細
ps -p <PID> -o pid,user,cmd,%cpu,%mem,start_time

# プロセスのオープンファイル
lsof -p <PID>

# ネットワーク接続
netstat -tulpn
ss -tulpn

# 不審なプロセスの検出
ps aux | grep -v "\[" | awk '{if($3>50.0) print $0}'  # 高CPU使用率
```

#### Namespace とCgroups

```bash
# プロセス隔離（Namespace）
unshare --fork --pid --mount-proc /bin/bash

# Cgroups（リソース制限）
cgcreate -g cpu,memory:limited_group
cgset -r cpu.shares=512 limited_group
cgset -r memory.limit_in_bytes=1G limited_group
cgexec -g cpu,memory:limited_group command
```

### システム強化（Hardening）

#### 基本的な強化

```bash
# 不要なサービス無効化
systemctl list-unit-files --type=service
systemctl disable service_name
systemctl stop service_name

# 不要なパッケージ削除
apt autoremove  # Debian/Ubuntu
yum autoremove  # Red Hat/CentOS

# 自動セキュリティアップデート
# Debian/Ubuntu
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Red Hat/CentOS
yum install yum-cron
systemctl enable yum-cron
```

#### SSH強化

```bash
# /etc/ssh/sshd_config

# ルートログイン無効化
PermitRootLogin no

# パスワード認証無効化（公開鍵認証のみ）
PasswordAuthentication no
PubkeyAuthentication yes

# 空パスワード禁止
PermitEmptyPasswords no

# プロトコルバージョン
Protocol 2

# ポート変更（デフォルト22から変更）
Port 2222

# ログインユーザー制限
AllowUsers user1 user2
DenyUsers baduser

# ログインタイムアウト
LoginGraceTime 60

# 最大認証試行回数
MaxAuthTries 3

# X11転送無効化
X11Forwarding no

# 設定反映
systemctl restart sshd
```

## Windowsセキュリティ

### ユーザーとグループ管理

#### ローカルユーザー管理

**PowerShellコマンド:**

```powershell
# ユーザー作成
New-LocalUser -Name "username" -Password (ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force) -PasswordNeverExpires:$false

# ユーザー情報確認
Get-LocalUser
Get-LocalUser -Name "username" | Select-Object *

# グループ管理
Get-LocalGroup
Add-LocalGroupMember -Group "Administrators" -Member "username"
Remove-LocalGroupMember -Group "Administrators" -Member "username"

# パスワードポリシー
net accounts
net accounts /maxpwage:90 /minpwage:1 /minpwlen:12

# アカウントロックアウト
net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30
```

**グループポリシー (GPO):**

```
コンピューターの構成 > Windowsの設定 > セキュリティの設定 > アカウントポリシー

パスワードのポリシー:
- パスワードの長さの最小値: 12文字
- パスワードの有効期間: 90日
- パスワードの履歴を記録する: 24個
- パスワードは複雑さの要件を満たす必要がある: 有効

アカウントロックアウトのポリシー:
- アカウントのロックアウトのしきい値: 5回
- ロックアウト期間: 30分
- ロックアウトカウンターのリセット: 30分
```

### Active Directory セキュリティ

#### AD基本セキュリティ

**OU（組織単位）設計:**
- 管理目的に基づいた論理的な構造
- GPO適用の最小単位
- 権限委任の境界

**グループ戦略:**
- AGDLP原則（Account, Global, Domain Local, Permission）
- セキュリティグループと配布グループの適切な使用
- 特権グループ（Domain Admins、Enterprise Adminsなど）の最小化

**PowerShell AD管理:**

```powershell
# ADモジュールインポート
Import-Module ActiveDirectory

# ユーザー管理
Get-ADUser -Filter * -Properties *
New-ADUser -Name "John Doe" -SamAccountName "jdoe" -UserPrincipalName "jdoe@domain.com" -Path "OU=Users,DC=domain,DC=com" -AccountPassword (ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force) -Enabled $true

# グループ管理
Get-ADGroup -Filter {Name -like "*Admin*"}
Add-ADGroupMember -Identity "GroupName" -Members "username"

# 特権アカウント監視
Get-ADGroupMember -Identity "Domain Admins" -Recursive
Get-ADGroupMember -Identity "Enterprise Admins" -Recursive

# 無効なアカウント
Search-ADAccount -AccountDisabled
Search-ADAccount -AccountInactive -TimeSpan 90.00:00:00

# パスワード期限切れアカウント
Search-ADAccount -PasswordExpired
```

#### AD監査とログ

**監査ポリシー設定:**

```
グループポリシー > コンピューターの構成 > Windowsの設定 > セキュリティの設定 > 高度な監査ポリシーの構成

アカウント ログオン:
- 資格情報の検証の監査: 成功と失敗

アカウント管理:
- ユーザーアカウント管理の監査: 成功と失敗
- セキュリティグループ管理の監査: 成功と失敗

ログオン/ログオフ:
- ログオンの監査: 成功と失敗
- ログオフの監査: 成功

オブジェクト アクセス:
- ファイル システムの監査: 成功と失敗（必要に応じて）

特権の使用:
- 機密性の高い特権の使用の監査: 成功と失敗
```

**重要なイベントID:**

```
4624: アカウントログオン成功
4625: アカウントログオン失敗
4634, 4647: アカウントログオフ
4720: ユーザーアカウント作成
4722: ユーザーアカウント有効化
4723: パスワード変更試行
4724: パスワードリセット
4728: セキュリティグループにメンバー追加
4732: ローカルグループにメンバー追加
4740: ユーザーアカウントロックアウト
4768: Kerberosチケット（TGT）要求
4769: Kerberosサービスチケット要求
4776: NTLM認証試行
```

**PowerShellでのログ分析:**

```powershell
# セキュリティログから特定イベント取得
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} -MaxEvents 100

# 最近の失敗ログイン
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625; StartTime=(Get-Date).AddHours(-24)} | Select-Object TimeCreated, Message

# 特権グループ変更
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4728,4732,4756}

# カスタムフィルタ
$Filter = @{
    LogName = 'Security'
    ID = 4624
    StartTime = (Get-Date).AddDays(-7)
}
Get-WinEvent -FilterHashtable $Filter | Where-Object {$_.Properties[8].Value -eq 10}  # リモートログオン
```

### レジストリセキュリティ

**重要なセキュリティ設定:**

```powershell
# UAC有効化
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1

# リモートデスクトップ無効化
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1

# LLMNR無効化（中間者攻撃対策）
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Force
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Name "EnableMulticast" -Value 0

# NetBIOS無効化
# ネットワークアダプタ設定で個別に設定

# SMBv1無効化
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force
```

### Windows Defender と Windows Firewall

**Windows Defender:**

```powershell
# ステータス確認
Get-MpComputerStatus

# リアルタイム保護
Set-MpPreference -DisableRealtimeMonitoring $false

# スキャン
Start-MpScan -ScanType QuickScan
Start-MpScan -ScanType FullScan

# 定義更新
Update-MpSignature

# 除外設定
Add-MpPreference -ExclusionPath "C:\TrustedFolder"
Add-MpPreference -ExclusionExtension ".log"
```

**Windows Firewall:**

```powershell
# ファイアウォールステータス
Get-NetFirewallProfile | Select-Object Name, Enabled

# ファイアウォール有効化
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# ルール追加
New-NetFirewallRule -DisplayName "Allow SSH" -Direction Inbound -LocalPort 22 -Protocol TCP -Action Allow

# ルール確認
Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True'} | Select-Object DisplayName, Direction, Action

# ログ有効化
Set-NetFirewallProfile -All -LogAllowed True -LogBlocked True -LogFileName "%systemroot%\system32\LogFiles\Firewall\pfirewall.log"
```

### イベントログ管理

**PowerShell EventLog管理:**

```powershell
# ログ一覧
Get-WinEvent -ListLog * | Select-Object LogName, RecordCount, IsEnabled

# ログサイズとポリシー設定
wevtutil sl Security /ms:1073741824  # 1GB
wevtutil sl Security /rt:false       # 上書きしない

# ログのバックアップ
wevtutil epl Security C:\Backup\Security.evtx

# ログのクリア（慎重に！）
wevtutil cl Application
```

### システム強化（Hardening）

#### 基本的な強化

```powershell
# 不要なサービス無効化
Get-Service | Where-Object {$_.Status -eq 'Running' -and $_.StartType -eq 'Automatic'}
Stop-Service -Name "ServiceName" -Force
Set-Service -Name "ServiceName" -StartupType Disabled

# 不要な機能削除
Get-WindowsOptionalFeature -Online | Where-Object {$_.State -eq 'Enabled'}
Disable-WindowsOptionalFeature -Online -FeatureName "FeatureName"

# 自動更新設定
# グループポリシー: コンピューターの構成 > 管理用テンプレート > Windowsコンポーネント > Windows Update
```

#### RDP強化

```powershell
# RDP無効化（不要な場合）
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1
Disable-NetFirewallRule -DisplayGroup "リモート デスクトップ"

# RDP使用時の強化
# ネットワークレベル認証（NLA）有効化
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication" -Value 1

# 暗号化レベル
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 3  # High

# アイドルタイムアウト
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MaxIdleTime" -Value 900000  # 15分
```

## ベストプラクティス

### 一般的な原則

1. **最小権限の原則**
   - ユーザーとプロセスに必要最小限の権限のみ付与
   - 管理者権限の使用を最小化

2. **防御の多層化**
   - 複数のセキュリティ層を実装
   - 単一の防御機構に依存しない

3. **パッチ管理**
   - 定期的なシステム更新
   - セキュリティパッチの迅速な適用
   - テスト環境での検証

4. **ログと監視**
   - すべての重要イベントをログに記録
   - リアルタイム監視とアラート
   - ログの集中管理と長期保存

5. **バックアップ**
   - 定期的なバックアップ
   - バックアップの検証
   - オフサイトまたはオフライン保存

### セキュリティチェックリスト

#### Linux

- [ ] すべてのソフトウェアが最新
- [ ] 不要なサービスが無効化されている
- [ ] ファイアウォールが適切に設定されている
- [ ] SSH が強化されている（鍵認証、ルートログイン無効など）
- [ ] SELinux/AppArmor が有効
- [ ] 監査ログ（auditd）が設定されている
- [ ] sudo が適切に設定されている
- [ ] パスワードポリシーが強制されている
- [ ] SUID/SGIDファイルがレビューされている
- [ ] カーネルパラメータが強化されている

#### Windows

- [ ] すべてのソフトウェアが最新
- [ ] Windows Defender が有効で最新
- [ ] Windows Firewall が有効
- [ ] UAC が有効
- [ ] 監査ポリシーが設定されている
- [ ] 管理者アカウントの数が最小化されている
- [ ] パスワードポリシーが強制されている
- [ ] 不要なサービスが無効化されている
- [ ] SMBv1 が無効化されている
- [ ] LLMNR/NetBIOS が無効化されている（必要に応じて）

## トラブルシューティング

### パフォーマンス問題

**Linux:**
```bash
# CPU使用率
top
mpstat 1

# メモリ使用率
free -h
vmstat 1

# ディスクI/O
iostat -x 1
iotop

# ネットワーク
iftop
nethogs
```

**Windows:**
```powershell
# パフォーマンスモニター
perfmon

# タスクマネージャー（CLI）
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Process | Sort-Object WS -Descending | Select-Object -First 10

# ネットワーク接続
Get-NetTCPConnection | Where-Object {$_.State -eq 'Established'}
```

## 参考リソース

- CIS Benchmarks (Center for Internet Security)
- NIST Special Publications (SP 800シリーズ)
- SANS Security Checklists
- Linux Security Modules Documentation
- Microsoft Security Baselines
- Red Hat Enterprise Linux Security Guide
- Ubuntu Security Documentation

## 注意事項

- **テスト環境**: 本番環境に適用する前に必ずテスト環境で検証すること
- **バックアップ**: 設定変更前に必ずバックアップを取ること
- **ドキュメント**: すべての変更を文書化すること
- **互換性**: セキュリティ設定がアプリケーションの動作に影響を与えないか確認すること
- **コンプライアンス**: 組織のポリシーと規制要件を遵守すること
