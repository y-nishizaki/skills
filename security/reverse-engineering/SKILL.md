---
name: "reverse-engineering"
description: >
  リバースエンジニアリングの技術を支援します。Assemblyの基礎、バイナリ解析、
  デバッガ（Ghidra、IDA、OllyDbg）の使用、難読化解除、コードフロー分析、
  プロトコルリバースエンジニアリングなど、バイナリ解析に使用します。
  キーワード - リバースエンジニアリング、バイナリ解析、逆アセンブル、デバッガ、
  Ghidra、IDA、Assembly。
version: 1.0.0
---

# リバースエンジニアリングスキル

## 目的

このスキルは、バイナリファイルのリバースエンジニアリング技術を提供します。
アセンブリ言語、逆アセンブラ、デバッガの使用、難読化の解除、プロトコル解析など、
実行可能ファイルの内部動作を理解するための実践的知識を含みます。

**注意:** このスキルは防御的セキュリティ分析と教育目的にのみ使用してください。

## Assembly言語基礎

### x86/x64 レジスタ

**汎用レジスタ（64ビット）:**
- RAX, RBX, RCX, RDX - 汎用演算
- RSI, RDI - ソース/デスティネーションインデックス
- RBP - ベースポインタ
- RSP - スタックポインタ
- R8-R15 - 追加汎用レジスタ

**特殊レジスタ:**
- RIP - 命令ポインタ
- RFLAGS - フラグレジスタ

### 基本命令

```assembly
; データ移動
MOV rax, rbx        ; rbxをraxにコピー
LEA rax, [rbx+8]    ; アドレス計算

; 算術演算
ADD rax, rbx        ; rax = rax + rbx
SUB rax, rbx        ; rax = rax - rbx
IMUL rax, rbx       ; rax = rax * rbx
IDIV rbx            ; rax = rax / rbx

; ビット演算
AND rax, rbx
OR rax, rbx
XOR rax, rbx
NOT rax
SHL rax, 2          ; 左シフト
SHR rax, 2          ; 右シフト

; 比較と分岐
CMP rax, rbx        ; フラグ設定
JE label            ; 等しければジャンプ
JNE label           ; 等しくなければジャンプ
JG label            ; 大きければジャンプ
JL label            ; 小さければジャンプ
JMP label           ; 無条件ジャンプ

; 関数呼び出し
CALL function       ; 関数呼び出し
RET                 ; 関数から戻る

; スタック操作
PUSH rax            ; スタックにプッシュ
POP rax             ; スタックからポップ
```

### 呼び出し規約

**x64 Windows (Microsoft):**
- 引数: RCX, RDX, R8, R9, Stack
- 戻り値: RAX
- 保存レジスタ: RBX, RBP, RDI, RSI, R12-R15

**x64 Linux (System V):**
- 引数: RDI, RSI, RDX, RCX, R8, R9, Stack
- 戻り値: RAX
- 保存レジスタ: RBX, RBP, R12-R15

## 逆アセンブルツール

### Ghidra

**基本操作:**
1. File → Import File
2. CodeBrowser起動
3. Analysis実行
4. Decompile ウィンドウでC言語表示

**スクリプト（Python）:**

```python
# GetGhidraScript.py
from ghidra.program.model.block import BasicBlockModel
from ghidra.program.model.symbol import SymbolType

# 現在の関数取得
function = getFunctionContaining(currentAddress)

if function:
    # 関数名
    print("Function: {}".format(function.getName()))

    # 基本ブロック
    bbm = BasicBlockModel(currentProgram)
    blocks = bbm.getCodeBlocksContaining(function.getBody(), monitor)

    while blocks.hasNext():
        block = blocks.next()
        print("Basic Block: {}".format(block.getMinAddress()))
```

### IDA Pro

**ショートカット:**
- `Space`: グラフビュー ↔ テキストビュー
- `X`: クロスリファレンス
- `N`: 名前変更
- `Y`: 型変更
- `;`: コメント
- `/`: 検索

**IDAPython:**

```python
import idaapi
import idc
import idautils

# すべての関数を列挙
for func_ea in idautils.Functions():
    func_name = idc.get_func_name(func_ea)
    print(f"{hex(func_ea)}: {func_name}")

# 文字列検索
for s in idautils.Strings():
    if "password" in str(s):
        print(f"{hex(s.ea)}: {s}")

# XREFsを辿る
for xref in idautils.XrefsTo(target_ea):
    print(f"From: {hex(xref.frm)}")
```

### Radare2

```bash
# ファイルオープン
r2 binary

# 分析
aa          # 基本分析
aaa         # 詳細分析
aaaa        # 最大分析

# 関数
afl         # 関数一覧
pdf @main   # main関数を逆アセンブル
VV @main    # グラフビュー

# シンボル
is          # シンボル一覧
ii          # インポート
iz          # 文字列

# 探索
/ password  # 文字列検索
/x 4883ec20 # バイト列検索

# デバッグ
db 0x400500 # ブレークポイント
dc          # 実行継続
dr          # レジスタ表示
ds          # ステップ実行
```

## デバッグ

### x64dbg

**基本操作:**
- `F2`: ブレークポイント設定/解除
- `F7`: ステップイン
- `F8`: ステップオーバー
- `F9`: 実行
- `Ctrl+G`: アドレスへジャンプ
- `Ctrl+B`: バイナリ検索
- `Ctrl+F`: 検索

**スクリプト:**

```cpp
// 自動解析スクリプト
var mainbase = Module.BaseFromName("target.exe");
var entry = Module.GetMainModuleEntry();

// ブレークポイント設定
SetBPX(entry);

// 実行
Run();

// レジスタ読み取り
var rax = GetRAX();
Log("RAX = " + rax.toString(16));
```

### GDB

```bash
# ブレークポイント
break main
break *0x400500

# 実行
run
run arg1 arg2
continue

# ステップ
step       # 関数内に入る
next       # 関数をスキップ
finish     # 関数から戻るまで実行

# 情報
info registers
info breakpoints
info functions
info variables

# メモリ
x/20x $rsp          # スタックをhex表示
x/s 0x400000        # 文字列として表示
x/i $rip            # 命令として表示

# 逆アセンブル
disassemble main
disas /r main       # バイトコード付き

# Set
set $rax = 0x1234
set {int}0x400000 = 0x90

# ウォッチポイント
watch *0x600000
rwatch *0x600000    # 読み取り
awatch *0x600000    # 読み書き
```

### WinDbg

```
# シンボル読み込み
.sympath srv*c:\symbols*https://msdl.microsoft.com/download/symbols
.reload

# ブレークポイント
bp kernel32!CreateFileW
bp 0x401000

# スタックトレース
k

# レジスタ
r

# メモリダンプ
db 0x401000         # Byte
dw 0x401000         # Word
dd 0x401000         # Dword
dq 0x401000         # Qword
da 0x401000         # ASCII
du 0x401000         # Unicode

# 逆アセンブル
u 0x401000

# 構造体
dt _PEB
dt nt!_EPROCESS

# 実行
g                   # Go
t                   # Trace (step into)
p                   # Step over
```

## アンパッキング

### 一般的なパッカー検出

```bash
# DIE (Detect It Easy)
die binary.exe

# PEiD (Windows)
peid binary.exe

# Exeinfo PE
exeinfope binary.exe
```

### UPX

```bash
# 検出
upx -t binary.exe

# アンパック
upx -d binary.exe
```

### 手動アンパッキング

1. OEP（Original Entry Point）を見つける
2. OEPでダンプ
3. Import再構築

```
x64dbg:
1. エントリポイントから実行
2. POPAD命令またはJMP命令を探す
3. JMP先がOEP
4. OEPでダンプ: Scylla プラグイン
```

## パッチング

### バイナリパッチ

```python
# Python
with open('binary.exe', 'r+b') as f:
    f.seek(0x1000)
    f.write(b'\x90\x90\x90')  # NOP

# HxD (Hex Editor)
# GUI操作
```

### Keygenme解析

```assembly
; CMP命令を探す
cmp eax, ebx
je valid_key

; パッチ例：JEをJMPに変更
je valid_key  → jmp valid_key
74 xx         → EB xx
```

## 難読化の解除

### 一般的な難読化手法

1. **ジャンク挿入**
```assembly
mov eax, eax    ; 無意味な命令
nop
```

2. **コントロールフロー難読化**
```assembly
jmp label1
label2:
  実際のコード
  ret
label1:
  jmp label2
```

3. **文字列暗号化**
```c
char key[] = {0x48, 0x65, 0x6c, 0x6c, 0x6f};  # XOR暗号化
```

4. **VMベース難読化**
- カスタムバイトコード
- インタープリタ実行

### 難読化解除

**IDAPython スクリプト:**

```python
# NOPスレッド削除
def remove_nop_sled():
    start = idc.get_screen_ea()
    end = idc.get_func_attr(start, FUNCATTR_END)

    for ea in range(start, end):
        if idc.print_insn_mnem(ea) == "nop":
            idc.patch_byte(ea, 0x90)  # 既にNOPだが...

# ジャンク除去
def remove_junk():
    # mov reg, reg パターン検索
    for func_ea in idautils.Functions():
        for ea in idautils.FuncItems(func_ea):
            if idc.print_insn_mnem(ea) == "mov":
                op1 = idc.print_operand(ea, 0)
                op2 = idc.print_operand(ea, 1)
                if op1 == op2:
                    idc.patch_byte(ea, 0x90)
                    print(f"Removed junk at {hex(ea)}")
```

## プロトコルリバースエンジニアリング

### ネットワークプロトコル解析

```python
from scapy.all import *

# パケットキャプチャ
packets = rdpcap('capture.pcap')

# カスタムプロトコル解析
for pkt in packets:
    if TCP in pkt and pkt[TCP].dport == 9999:
        payload = bytes(pkt[TCP].payload)
        # プロトコル解析
        command = payload[0]
        length = int.from_bytes(payload[1:3], 'big')
        data = payload[3:3+length]
        print(f"Command: {command}, Data: {data}")
```

### ファイルフォーマット解析

```python
import struct

def parse_custom_format(filename):
    with open(filename, 'rb') as f:
        # ヘッダー
        magic = f.read(4)
        if magic != b'CUST':
            raise ValueError("Invalid magic")

        version = struct.unpack('<I', f.read(4))[0]
        num_entries = struct.unpack('<I', f.read(4))[0]

        entries = []
        for i in range(num_entries):
            entry_type = struct.unpack('<H', f.read(2))[0]
            entry_size = struct.unpack('<I', f.read(4))[0]
            entry_data = f.read(entry_size)
            entries.append({
                'type': entry_type,
                'size': entry_size,
                'data': entry_data
            })

        return {
            'version': version,
            'entries': entries
        }
```

## Android APKリバースエンジニアリング

```bash
# APK解凍
unzip app.apk -d app/

# dex2jar (DEX → JAR)
d2j-dex2jar app/classes.dex

# JD-GUI (JAR → Java Source)
jd-gui classes-dex2jar.jar

# APKTool (APK → Smali)
apktool d app.apk

# Smali編集後、再パッケージ
apktool b app/ -o modified.apk

# 署名
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore modified.apk alias_name
```

## .NETリバースエンジニアリング

**dnSpy:**
- デバッグ機能付き.NET逆アセンブラ
- IL → C#変換
- 実行時デバッグ

```csharp
// dnSpyで変数ウォッチ
// ブレークポイント設定
// ステップ実行
```

**ILSpy:**
- オープンソース.NET逆アセンブラ
- IL → C#

## ベストプラクティス

1. **仮想環境使用**
   - VM内で解析
   - スナップショット活用

2. **文書化**
   - 発見事項をコメント
   - 関数名の適切な命名
   - グラフ・図の作成

3. **ツールの組み合わせ**
   - 静的解析 + 動的解析
   - 複数のツールで検証

4. **自動化**
   - スクリプト活用
   - 反復タスクの自動化

## 参考リソース

- Practical Binary Analysis (書籍)
- Reverse Engineering for Beginners (RE4B)
- Malware Unicorn's RE101
- Crackmes.one

## 注意事項

- 合法的な目的でのみ使用
- ライセンス条項の遵守
- リバースエンジニアリング禁止条項の確認
- 倫理的な行動
