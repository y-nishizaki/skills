---
name: "digital-forensics"
description: >
  デジタルフォレンジックの実施を支援します。メモリダンプ解析、タイムライン分析、証拠保全手順、
  ディスクイメージング、ファイルカービング、アーティファクト分析など、インシデント調査と
  法的証拠収集に使用します。
  キーワード - フォレンジック、証拠保全、メモリ解析、ディスクイメージ、タイムライン、
  アーティファクト。
version: 1.0.0
---

# デジタルフォレンジックスキル

## 目的

このスキルは、デジタルフォレンジック調査の方法論とツールを提供します。
証拠保全、データ収集、分析、報告までの一連のプロセスをカバーし、
法的に有効な証拠を確保するための実践的知識を含みます。

## このスキルを使用する場合

- インシデント調査やフォレンジック分析を求めた場合
- 証拠保全やディスクイメージング手順が必要な場合
- メモリダンプ解析やタイムライン分析を実施する場合
- デジタル証拠の法的妥当性を確保したい場合
- アーティファクト分析が必要な場合

## フォレンジックプロセス

### 1. 準備（Preparation）
- ツールとハードウェアの準備
- 法的要件の確認
- 調査計画の策定

### 2. 識別（Identification）
- 証拠源の特定
- データタイプの分類
- 範囲の決定

### 3. 保全（Preservation）
- Chain of Custody確立
- 書き込み防止
- ビット完全コピー作成

### 4. 収集（Collection）
- データ取得
- ハッシュ値記録
- ドキュメント作成

### 5. 分析（Analysis）
- データ復元
- タイムライン作成
- パターン識別

### 6. 報告（Reporting）
- 調査結果文書化
- 証拠チェーン維持
- 法的報告書作成

## 証拠保全

### ライブシステム収集

**揮発性データ（優先順位順）:**
1. レジスタ、キャッシュ
2. ルーティングテーブル、ARPキャッシュ、プロセステーブル
3. メモリ
4. 一時ファイル
5. ディスク
6. リモートログ
7. 物理的設定、ネットワークトポロジー

Linux揮発性データ収集:

```bash
#!/bin/bash
# フォレンジック収集スクリプト

OUTPUT_DIR="/forensics/$(hostname)-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# システム情報
date > "$OUTPUT_DIR/date.txt"
uname -a > "$OUTPUT_DIR/uname.txt"
uptime > "$OUTPUT_DIR/uptime.txt"

# ネットワーク情報
ifconfig -a > "$OUTPUT_DIR/ifconfig.txt"
netstat -an > "$OUTPUT_DIR/netstat.txt"
netstat -rn > "$OUTPUT_DIR/routes.txt"
arp -a > "$OUTPUT_DIR/arp.txt"

# プロセス情報
ps aux > "$OUTPUT_DIR/ps.txt"
ps -ef > "$OUTPUT_DIR/ps-ef.txt"
lsof > "$OUTPUT_DIR/lsof.txt"

# ログインユーザー
w > "$OUTPUT_DIR/w.txt"
last > "$OUTPUT_DIR/last.txt"

# メモリダンプ
dd if=/proc/kcore of="$OUTPUT_DIR/memory.dump" bs=1M
# または LiME
insmod lime.ko "path=$OUTPUT_DIR/memory.lime format=lime"

# ハッシュ計算
find "$OUTPUT_DIR" -type f -exec md5sum {} \; > "$OUTPUT_DIR/hashes.txt"
```

Windows揮発性データ収集:

```powershell
# フォレンジック収集（PowerShell）

$OutputDir = "C:\Forensics\$env:COMPUTERNAME-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $OutputDir

# システム情報
Get-ComputerInfo | Out-File "$OutputDir\systeminfo.txt"
Get-Date | Out-File "$OutputDir\date.txt"

# ネットワーク情報
Get-NetIPConfiguration | Out-File "$OutputDir\ipconfig.txt"
Get-NetTCPConnection | Export-Csv "$OutputDir\netstat.csv"
Get-NetRoute | Out-File "$OutputDir\routes.txt"
Get-NetNeighbor | Out-File "$OutputDir\arp.txt"

# プロセス情報
Get-Process | Export-Csv "$OutputDir\processes.csv"
Get-WmiObject Win32_Process | Select-Object * | Export-Csv "$OutputDir\processes-wmi.csv"

# サービス
Get-Service | Export-Csv "$OutputDir\services.csv"

# ログインユーザー
query user | Out-File "$OutputDir\users.txt"

# メモリダンプ（DumpIt, WinPmem, Magnet RAMなど）
.\DumpIt.exe /O "$OutputDir\memory.dmp"

# レジストリキーハイブ
reg save HKLM\SAM "$OutputDir\SAM.hive"
reg save HKLM\SYSTEM "$OutputDir\SYSTEM.hive"
reg save HKLM\SECURITY "$OutputDir\SECURITY.hive"
```

### ディスクイメージング

**dd (Linux/Unix):**

```bash
# 物理ディスク全体
dd if=/dev/sda of=/mnt/evidence/disk.img bs=4M conv=noerror,sync status=progress

# ハッシュ計算と同時実行
dd if=/dev/sda | tee /mnt/evidence/disk.img | sha256sum > /mnt/evidence/disk.img.sha256

# dcfldd（強化版dd）
dcfldd if=/dev/sda of=/mnt/evidence/disk.img hash=sha256 hashlog=/mnt/evidence/hash.txt
```

**FTK Imager:**
- Windows向けGUIツール
- E01（EnCase）形式対応
- ベリファイ機能内蔵

**ewfacquire（libewf）:**

```bash
# Expert Witness Format（E01）作成
ewfacquire -t /mnt/evidence/disk /dev/sda
```

### Chain of Custody

証拠チェーン文書テンプレート:

```
証拠番号: CASE-2024-001-E001
証拠タイプ: ハードディスク
製造元/モデル: Seagate ST1000DM003
シリアル番号: Z1D4V2KL

収集情報:
- 収集日時: 2024-01-15 14:30:00 JST
- 収集者: 山田太郎
- 収集場所: 東京オフィス サーバールーム
- 収集方法: 物理的取り外し

ハッシュ値:
- MD5: 5d41402abc4b2a76b9719d911017c592
- SHA256: 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae

移管記録:
[日時] [引継者] → [受領者] [目的] [署名]
2024-01-15 15:00 山田太郎 → 佐藤花子 分析のため 両者署名
```

## メモリフォレンジック

### Volatility 3

```bash
# イメージ情報
vol -f memory.dmp windows.info

# プロセス一覧
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.pstree

# ネットワーク接続
vol -f memory.dmp windows.netscan

# レジストリハイブ
vol -f memory.dmp windows.registry.hivelist
vol -f memory.dmp windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"

# マルウェア検出
vol -f memory.dmp windows.malfind

# DLLリスト
vol -f memory.dmp windows.dlllist --pid 1234

# ハンドル
vol -f memory.dmp windows.handles --pid 1234

# コマンドライン
vol -f memory.dmp windows.cmdline

# ファイルスキャン
vol -f memory.dmp windows.filescan

# ファイル抽出
vol -f memory.dmp windows.dumpfiles --pid 1234
```

## ディスク解析

### The Sleuth Kit (TSK)

```bash
# パーティション情報
mmls disk.img

# ファイルシステム情報
fsstat -o 2048 disk.img

# ディレクトリ一覧
fls -r -o 2048 disk.img

# ファイル抽出
icat -o 2048 disk.img 128 > extracted_file

# タイムライン作成
fls -r -m / -o 2048 disk.img > bodyfile
mactime -b bodyfile -d > timeline.csv
```

### Autopsy

GUIベースのフォレンジックツール:
- TSKのフロントエンド
- 自動アーティファクト抽出
- キーワード検索
- タイムライン視覚化

## ファイルカービング

### Scalpel

設定ファイル（scalpel.conf）:

```
# JPEG
jpg     y       5000000         \xff\xd8\xff\xe0\x00\x10        \xff\xd9

# PNG
png     y       5000000         \x50\x4e\x47?   \xff\xfc\xfd\xfe

# PDF
pdf     y       5000000         %PDF            %EOF\x0d

# ZIP
zip     y       10000000        PK\x03\x04      \x3c\xac

# Microsoft Office
doc     y       10000000        \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1        \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1
```

実行:

```bash
scalpel -c scalpel.conf -o output/ disk.img
```

### PhotoRec

```bash
# インタラクティブモード
photorec disk.img

# コマンドラインモード
photorec /d recovered_files /cmd disk.img search
```

## Windows アーティファクト

### レジストリ分析

**SAM (Security Account Manager):**
- ローカルユーザーアカウント
- パスワードハッシュ

**SYSTEM:**
- コンピュータ名
- ネットワーク設定
- マウントデバイス

**SOFTWARE:**
- インストールされたアプリケーション
- Run キー（自動起動）

**NTUSER.DAT:**
- ユーザープロファイル
- 最近使用したファイル
- UserAssist

レジストリ解析ツール:

```bash
# RegRipper
rip.pl -r NTUSER.DAT -p userassist

# Registry Explorer (Eric Zimmerman)
# GUIツール
```

### イベントログ

重要なイベントID:
- 4624: ログオン成功
- 4625: ログオン失敗
- 4672: 特権ログオン
- 4688: プロセス作成
- 4698: スケジュールタスク作成
- 4720: ユーザーアカウント作成

Evtxファイル解析:

```python
from evtx import PyEvtxParser

parser = PyEvtxParser('Security.evtx')

for record in parser.records():
    if record['event_id'] == 4624:  # Successful logon
        print(f"Time: {record['timestamp']}")
        print(f"User: {record['data']['TargetUserName']}")
        print(f"IP: {record['data']['IpAddress']}")
```

### Prefetch

Windowsアプリケーション実行履歴:

```bash
# PECmd (Eric Zimmerman)
PECmd.exe -f "C:\Windows\Prefetch\NOTEPAD.EXE-XXXXXXXX.pf"
```

### USBデバイス履歴

レジストリパス:
```
HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR
HKLM\SYSTEM\CurrentControlSet\Enum\USB
```

### ブラウザアーティファクト

**Chrome/Edge:**
- History: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`
- Cache: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache`
- Downloads: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`

SQLiteデータベース解析:

```bash
sqlite3 History "SELECT url, title, datetime(last_visit_time/1000000-11644473600,'unixepoch') FROM urls ORDER BY last_visit_time DESC LIMIT 100;"
```

## Linux アーティファクト

### ログファイル

```
/var/log/auth.log       - 認証ログ
/var/log/syslog         - システムログ
/var/log/kern.log       - カーネルログ
/var/log/apache2/       - Webサーバーログ
/var/log/mysql/         - データベースログ
~/.bash_history         - コマンド履歴
```

### 永続化メカニズム

```bash
# Cron jobs
cat /etc/crontab
ls -la /etc/cron.*
crontab -l

# Systemd services
systemctl list-unit-files --type=service

# 起動スクリプト
ls -la /etc/init.d/
ls -la /etc/rc*.d/

# .bashrc, .profile
cat ~/.bashrc
cat ~/.profile
```

## タイムライン分析

### Plaso (log2timeline)

```bash
# タイムライン作成
log2timeline.py timeline.plaso disk.img

# フィルタリング
psort.py -o l2tcsv -w timeline.csv timeline.plaso "date > '2024-01-01 00:00:00'"

# 出力形式
psort.py -o dynamic -w timeline.csv timeline.plaso
```

### タイムライン視覚化

```python
import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv('timeline.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 時系列プロット
df.set_index('timestamp').resample('1H').size().plot()
plt.title('Event Frequency Over Time')
plt.xlabel('Time')
plt.ylabel('Number of Events')
plt.show()
```

## ネットワークフォレンジック

### PCAP解析

```bash
# Wireshark/tshark
tshark -r capture.pcap -Y "http.request" -T fields -e ip.src -e http.host -e http.request.uri

# TCP ストリーム抽出
tshark -r capture.pcap -z "follow,tcp,ascii,0" -q

# HTTP オブジェクト抽出
tshark -r capture.pcap --export-objects http,exported_files/

# 統計
tshark -r capture.pcap -q -z io,phs
tshark -r capture.pcap -q -z conv,ip
```

### NetworkMiner

- 自動ファイル抽出
- ホスト情報抽出
- 認証情報検出
- セッション再構築

## モバイルフォレンジック

### Android

重要なパス:
```
/data/data/                          - アプリデータ
/data/data/com.android.providers.contacts/databases/contacts2.db - 連絡先
/data/data/com.android.providers.telephony/databases/mmssms.db - SMS/MMS
/data/system/packages.xml            - インストール済みアプリ
```

ADB経由でのデータ収集:

```bash
# デバイス情報
adb shell getprop

# ファイルシステム一覧
adb shell ls -lR / > filesystem.txt

# データベース抽出
adb pull /data/data/com.android.providers.contacts/databases/contacts2.db

# ログ収集
adb logcat -d > logcat.txt
```

### iOS

- iTunes バックアップ解析
- 物理的取得（JailbreakまたはCellebrite等）
- SQLiteデータベース（SMS、通話履歴、Safari履歴）

## 報告書作成

### フォレンジックレポート構成

1. **エグゼクティブサマリー**
   - 調査目的
   - 主要な発見
   - 結論と推奨事項

2. **調査範囲**
   - 対象システム
   - 調査期間
   - 制限事項

3. **証拠リスト**
   - 証拠番号
   - 説明
   - ハッシュ値
   - Chain of Custody

4. **方法論**
   - 使用ツール
   - 手順
   - 技術的詳細

5. **発見事項**
   - タイムライン
   - アーティファクト
   - 分析結果

6. **結論**
   - 要約
   - 推奨事項

7. **付録**
   - 技術的詳細
   - ログ
   - スクリーンショット

## ベストプラクティス

1. **法的妥当性**
   - Chain of Custody維持
   - 書き込み防止の徹底
   - ハッシュ値記録

2. **文書化**
   - すべての手順を記録
   - タイムスタンプ
   - スクリーンショット

3. **再現性**
   - 同じ手順で同じ結果
   - ツールバージョン記録
   - 自動化スクリプト保存

4. **倫理と法律**
   - プライバシー尊重
   - 法的権限確認
   - データ保護法遵守

## 参考リソース

- SANS DFIR (Digital Forensics and Incident Response)
- NIST SP 800-86: Guide to Integrating Forensic Techniques
- Eric Zimmerman's Tools
- DFIR Training

## 注意事項

- 適切な法的権限の確保
- プライバシー法規制の遵守
- 証拠の完全性維持
- 専門家証言の準備
