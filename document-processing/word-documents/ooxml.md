# Office Open XML 技術リファレンス

**重要: 作業を開始する前に、このドキュメント全体を読んでください。** このドキュメントは以下をカバーします:

- [技術ガイドライン](#技術ガイドライン) - スキーマ準拠ルールと検証要件
- [ドキュメントコンテンツパターン](#ドキュメントコンテンツパターン) - 見出し、リスト、表、書式などのXMLパターン
- [ドキュメントライブラリ (Python)](#ドキュメントライブラリ-python) - 自動インフラストラクチャセットアップを備えたOOXML操作の推奨アプローチ
- [変更履歴 (赤線)](#変更履歴-赤線) - 変更履歴を実装するためのXMLパターン

## 技術ガイドライン

### スキーマ準拠

- **`<w:pPr>` 内の要素順序**: `<w:pStyle>`、`<w:numPr>`、`<w:spacing>`、`<w:ind>`、`<w:jc>`
- **空白文字**: 先頭または末尾にスペースがある `<w:t>` 要素には `xml:space='preserve'` を追加
- **Unicode**: ASCIIコンテンツで文字をエスケープ: `"` は `&#8220;` になります
  - **文字エンコーディングリファレンス**: カーリー引用符 `""` は `&#8220;&#8221;`、アポストロフィ `'` は `&#8217;`、emダッシュ `—` は `&#8212;`
- **変更履歴**: `<w:r>` 要素の外側で、`w:author="Claude"` を持つ `<w:del>` と `<w:ins>` タグを使用
  - **重要**: `<w:ins>` は `</w:ins>` で閉じ、`<w:del>` は `</w:del>` で閉じる - 混在させない
  - **RSIDは8桁の16進数である必要があります**: `00AB1234` のような値を使用 (0-9、A-Fの文字のみ)
  - **trackRevisionsの配置**: settings.xml の `<w:proofState>` の後に `<w:trackRevisions/>` を追加
- **画像**: `word/media/` に追加し、`document.xml` で参照し、オーバーフローを防ぐために寸法を設定

## ドキュメントコンテンツパターン

### 基本構造

```xml
<w:p>
  <w:r><w:t>テキストコンテンツ</w:t></w:r>
</w:p>
```

### 見出しとスタイル

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Title"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>ドキュメントタイトル</w:t></w:r>
</w:p>

<w:p>
  <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
  <w:r><w:t>セクション見出し</w:t></w:r>
</w:p>
```

### テキスト書式

```xml
<!-- 太字 -->
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>太字</w:t></w:r>
<!-- 斜体 -->
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>斜体</w:t></w:r>
<!-- 下線 -->
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>下線付き</w:t></w:r>
<!-- ハイライト -->
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>ハイライト</w:t></w:r>
```

### リスト

```xml
<!-- 番号付きリスト -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>最初のアイテム</w:t></w:r>
</w:p>

<!-- 番号付きリストを1から再開 - 異なるnumIdを使用 -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>新しいリストアイテム1</w:t></w:r>
</w:p>

<!-- 箇条書きリスト (レベル2) -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
    <w:ind w:left="900"/>
  </w:pPr>
  <w:r><w:t>箇条書きアイテム</w:t></w:r>
</w:p>
```

### 表

```xml
<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="0" w:type="auto"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="4675"/><w:gridCol w:w="4675"/>
  </w:tblGrid>
  <w:tr>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>セル1</w:t></w:r></w:p>
    </w:tc>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>セル2</w:t></w:r></w:p>
    </w:tc>
  </w:tr>
</w:tbl>
```

### レイアウト

```xml
<!-- 新しいセクション前の改ページ (一般的なパターン) -->
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
  </w:pPr>
  <w:r>
    <w:t>新しいセクションタイトル</w:t>
  </w:r>
</w:p>

<!-- 中央揃え段落 -->
<w:p>
  <w:pPr>
    <w:spacing w:before="240" w:after="0"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>中央揃えテキスト</w:t></w:r>
</w:p>

<!-- フォント変更 - 段落レベル (すべてのランに適用) -->
<w:p>
  <w:pPr>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
  </w:pPr>
  <w:r><w:t>等幅テキスト</w:t></w:r>
</w:p>

<!-- フォント変更 - ランレベル (このテキストに固有) -->
<w:p>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
    <w:t>このテキストはCourier New</w:t>
  </w:r>
  <w:r><w:t> そしてこのテキストはデフォルトフォント</w:t></w:r>
</w:p>
```

## ファイル更新

コンテンツを追加する際は、以下のファイルを更新します:

**`word/_rels/document.xml.rels`:**

```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
```

**`[Content_Types].xml`:**

```xml
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
```

### 画像

**重要**: ページオーバーフローを防ぎ、アスペクト比を維持するために寸法を計算します。

```xml
<!-- 最小限の必須構造 -->
<w:p>
  <w:r>
    <w:drawing>
      <wp:inline>
        <wp:extent cx="2743200" cy="1828800"/>
        <wp:docPr id="1" name="Picture 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="image1.png"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="rId5"/>
                <!-- アスペクト比を保持したストレッチフィルのために追加 -->
                <a:stretch>
                  <a:fillRect/>
                </a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm>
                  <a:ext cx="2743200" cy="1828800"/>
                </a:xfrm>
                <a:prstGeom prst="rect"/>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
```

### リンク (ハイパーリンク)

**重要**: すべてのハイパーリンク (内部および外部の両方) は、styles.xml で Hyperlink スタイルを定義する必要があります。このスタイルがないと、リンクは青い下線付きのクリック可能なリンクではなく、通常のテキストのように見えます。

**外部リンク:**

```xml
<!-- document.xml 内 -->
<w:hyperlink r:id="rId5">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>リンクテキスト</w:t>
  </w:r>
</w:hyperlink>

<!-- word/_rels/document.xml.rels 内 -->
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
              Target="https://www.example.com/" TargetMode="External"/>
```

**内部リンク:**

```xml
<!-- ブックマークへのリンク -->
<w:hyperlink w:anchor="myBookmark">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>リンクテキスト</w:t>
  </w:r>
</w:hyperlink>

<!-- ブックマークターゲット -->
<w:bookmarkStart w:id="0" w:name="myBookmark"/>
<w:r><w:t>ターゲットコンテンツ</w:t></w:r>
<w:bookmarkEnd w:id="0"/>
```

**ハイパーリンクスタイル (styles.xml で必須):**

```xml
<w:style w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/>
  <w:basedOn w:val="DefaultParagraphFont"/>
  <w:uiPriority w:val="99"/>
  <w:unhideWhenUsed/>
  <w:rPr>
    <w:color w:val="467886" w:themeColor="hyperlink"/>
    <w:u w:val="single"/>
  </w:rPr>
</w:style>
```

## ドキュメントライブラリ (Python)

すべての変更履歴とコメントには、`scripts/document.py` の Document クラスを使用します。これは、インフラストラクチャのセットアップ (people.xml、RSID、settings.xml、コメントファイル、リレーションシップ、コンテンツタイプ) を自動的に処理します。ライブラリでサポートされていない複雑なシナリオの場合にのみ、直接XML操作を使用してください。

**Unicode とエンティティの扱い:**

- **検索**: エンティティ表記とUnicode文字の両方が機能します - `contains="&#8220;Company"` と `contains="\u201cCompany"` は同じテキストを見つけます
- **置換**: エンティティ (`&#8220;`) またはUnicode (`\u201c`) のいずれかを使用 - どちらも機能し、ファイルのエンコーディングに基づいて適切に変換されます (ascii → エンティティ、utf-8 → Unicode)

### 初期化

**docx スキルルートを見つける** (`scripts/` と `ooxml/` を含むディレクトリ):

```bash
# document.py を検索してスキルルートを特定
# 注: /mnt/skills はここでは例として使用されています。実際の場所についてはコンテキストを確認してください
find /mnt/skills -name "document.py" -path "*/docx/scripts/*" 2>/dev/null | head -1
# 出力例: /mnt/skills/docx/scripts/document.py
# スキルルートは: /mnt/skills/docx
```

**PYTHONPATH を設定してスクリプトを実行** (docx スキルルートに設定):

```bash
PYTHONPATH=/mnt/skills/docx python your_script.py
```

**スクリプト内で**、スキルルートからインポート:

```python
from scripts.document import Document, DocxXMLEditor

# 基本的な初期化 (一時コピーを自動作成し、インフラストラクチャをセットアップ)
doc = Document('unpacked')

# 作成者とイニシャルをカスタマイズ
doc = Document('unpacked', author="John Doe", initials="JD")

# 変更履歴モードを有効化
doc = Document('unpacked', track_revisions=True)

# カスタムRSIDを指定 (提供されない場合は自動生成)
doc = Document('unpacked', rsid="07DC5ECB")
```

### 変更履歴の作成

**重要**: 実際に変更されるテキストのみをマークします。すべての変更されていないテキストは、`<w:del>`/`<w:ins>` タグの外に保持します。変更されていないテキストをマークすると、編集がプロフェッショナルでなくなり、レビューが困難になります。

**属性の処理**: Document クラスは、新しい要素に属性 (w:id、w:date、w:rsidR、w:rsidDel、w16du:dateUtc、xml:space) を自動的に挿入します。元のドキュメントから変更されていないテキストを保持する場合は、ドキュメントの整合性を維持するために、既存の属性を持つ元の `<w:r>` 要素をコピーします。

**メソッド選択ガイド**:

- **通常のテキストに自分の変更を追加**: `<w:del>`/`<w:ins>` タグを使用した `replace_node()`、または `<w:r>` または `<w:p>` 要素全体を削除するための `suggest_deletion()` を使用
- **他の作成者の変更履歴を部分的に変更**: `replace_node()` を使用して、彼らの `<w:ins>`/`<w:del>` 内に変更をネストします
- **他の作成者の挿入を完全に拒否**: `<w:ins>` 要素に対して `revert_insertion()` を使用 (`suggest_deletion()` ではありません)
- **他の作成者の削除を完全に拒否**: `<w:del>` 要素に対して `revert_deletion()` を使用し、変更履歴を使用して削除されたコンテンツを復元します

```python
# 最小限の編集 - 1つの単語を変更: "The report is monthly" → "The report is quarterly"
# 元: <w:r w:rsidR="00AB12CD"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>The report is monthly</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="The report is monthly")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00AB12CD">{rpr}<w:t>The report is </w:t></w:r><w:del><w:r>{rpr}<w:delText>monthly</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>quarterly</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 最小限の編集 - 数字を変更: "within 30 days" → "within 45 days"
# 元: <w:r w:rsidR="00XYZ789"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>within 30 days</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="within 30 days")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00XYZ789">{rpr}<w:t>within </w:t></w:r><w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>45</w:t></w:r></w:ins><w:r w:rsidR="00XYZ789">{rpr}<w:t> days</w:t></w:r>'
doc["word/document.xml"].replace_node(node, replacement)

# 完全な置換 - すべてのテキストを置き換える場合でも書式を保持
node = doc["word/document.xml"].get_node(tag="w:r", contains="apple")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:del><w:r>{rpr}<w:delText>apple</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>banana orange</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 新しいコンテンツを挿入 (属性は不要 - 自動挿入)
node = doc["word/document.xml"].get_node(tag="w:r", contains="existing text")
doc["word/document.xml"].insert_after(node, '<w:ins><w:r><w:t>new text</w:t></w:r></w:ins>')

# 他の作成者の挿入を部分的に削除
# 元: <w:ins w:author="Jane Smith" w:date="..."><w:r><w:t>quarterly financial report</w:t></w:r></w:ins>
# 目標: "financial" のみを削除して "quarterly report" にする
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
# 重要: 外側の <w:ins> の w:author="Jane Smith" を保持して著者情報を維持
replacement = '''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>quarterly </w:t></w:r>
  <w:del><w:r><w:delText>financial </w:delText></w:r></w:del>
  <w:r><w:t>report</w:t></w:r>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# 他の作成者の挿入の一部を変更
# 元: <w:ins w:author="Jane Smith"><w:r><w:t>in silence, safe and sound</w:t></w:r></w:ins>
# 目標: "safe and sound" を "soft and unbound" に変更
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "8"})
replacement = f'''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>in silence, </w:t></w:r>
</w:ins>
<w:ins>
  <w:r><w:t>soft and unbound</w:t></w:r>
</w:ins>
<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:del><w:r><w:delText>safe and sound</w:delText></w:r></w:del>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# ラン全体を削除 (すべてのコンテンツを削除する場合のみ使用; 部分削除には replace_node を使用)
node = doc["word/document.xml"].get_node(tag="w:r", contains="text to delete")
doc["word/document.xml"].suggest_deletion(node)

# 段落全体を削除 (インプレース、通常および番号付きリスト段落の両方を処理)
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph to delete")
doc["word/document.xml"].suggest_deletion(para)

# 新しい番号付きリストアイテムを追加
target_para = doc["word/document.xml"].get_node(tag="w:p", contains="existing list item")
pPr = tags[0].toxml() if (tags := target_para.getElementsByTagName("w:pPr")) else ""
new_item = f'<w:p>{pPr}<w:r><w:t>新しいアイテム</w:t></w:r></w:p>'
tracked_para = DocxXMLEditor.suggest_paragraph(new_item)
doc["word/document.xml"].insert_after(target_para, tracked_para)
# オプション: より良い視覚的な分離のために、コンテンツの前にスペーシング段落を追加
# spacing = DocxXMLEditor.suggest_paragraph('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr></w:p>')
# doc["word/document.xml"].insert_after(target_para, spacing + tracked_para)
```

### コメントの追加

```python
# 2つの既存の変更履歴にまたがるコメントを追加
# 注: w:id は自動生成されます。XML検査から知っている場合にのみ w:id で検索
start_node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
end_node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "2"})
doc.add_comment(start=start_node, end=end_node, text="この変更の説明")

# 段落にコメントを追加
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph text")
doc.add_comment(start=para, end=para, text="この段落へのコメント")

# 新しく作成された変更履歴にコメントを追加
# まず変更履歴を作成
node = doc["word/document.xml"].get_node(tag="w:r", contains="old")
new_nodes = doc["word/document.xml"].replace_node(
    node,
    '<w:del><w:r><w:delText>old</w:delText></w:r></w:del><w:ins><w:r><w:t>new</w:t></w:r></w:ins>'
)
# 次に新しく作成された要素にコメントを追加
# new_nodes[0] は <w:del>、new_nodes[1] は <w:ins>
doc.add_comment(start=new_nodes[0], end=new_nodes[1], text="要件に従って old を new に変更")

# 既存のコメントに返信
doc.reply_to_comment(parent_comment_id=0, text="この変更に同意します")
```

### 変更履歴の拒否

**重要**: 挿入を拒否するには `revert_insertion()` を使用し、削除を復元するには `revert_deletion()` を使用します。`suggest_deletion()` は通常のマークされていないコンテンツに対してのみ使用します。

```python
# 挿入を拒否 (削除でラップ)
# 他の作成者が挿入したテキストを削除したい場合に使用
ins = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
nodes = doc["word/document.xml"].revert_insertion(ins)  # [ins] を返す

# 削除を拒否 (削除されたコンテンツを復元するための挿入を作成)
# 他の作成者が削除したテキストを復元したい場合に使用
del_elem = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "3"})
nodes = doc["word/document.xml"].revert_deletion(del_elem)  # [del_elem, new_ins] を返す

# 段落内のすべての挿入を拒否
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph text")
nodes = doc["word/document.xml"].revert_insertion(para)  # [para] を返す

# 段落内のすべての削除を拒否
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph text")
nodes = doc["word/document.xml"].revert_deletion(para)  # [para] を返す
```

### 画像の挿入

**重要**: Document クラスは `doc.unpacked_path` の一時コピーで動作します。画像は常にこの一時ディレクトリにコピーし、元の展開フォルダにはコピーしません。

```python
from PIL import Image
import shutil, os

# まずドキュメントを初期化
doc = Document('unpacked')

# 画像をコピーし、アスペクト比を維持した全幅寸法を計算
media_dir = os.path.join(doc.unpacked_path, 'word/media')
os.makedirs(media_dir, exist_ok=True)
shutil.copy('image.png', os.path.join(media_dir, 'image1.png'))
img = Image.open(os.path.join(media_dir, 'image1.png'))
width_emus = int(6.5 * 914400)  # 6.5インチの使用可能幅、914400 EMU/インチ
height_emus = int(width_emus * img.size[1] / img.size[0])

# リレーションシップとコンテンツタイプを追加
rels_editor = doc['word/_rels/document.xml.rels']
next_rid = rels_editor.get_next_rid()
rels_editor.append_to(rels_editor.dom.documentElement,
    f'<Relationship Id="{next_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>')
doc['[Content_Types].xml'].append_to(doc['[Content_Types].xml'].dom.documentElement,
    '<Default Extension="png" ContentType="image/png"/>')

# 画像を挿入
node = doc["word/document.xml"].get_node(tag="w:p", line_number=100)
doc["word/document.xml"].insert_after(node, f'''<w:p>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{width_emus}" cy="{height_emus}"/>
        <wp:docPr id="1" name="Picture 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr><pic:cNvPr id="1" name="image1.png"/><pic:cNvPicPr/></pic:nvPicPr>
              <pic:blipFill><a:blip r:embed="{next_rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
              <pic:spPr><a:xfrm><a:ext cx="{width_emus}" cy="{height_emus}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>''')
```

### ノードの取得

```python
# テキストコンテンツで検索
node = doc["word/document.xml"].get_node(tag="w:p", contains="specific text")

# 行範囲で検索
para = doc["word/document.xml"].get_node(tag="w:p", line_number=range(100, 150))

# 属性で検索
node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})

# 正確な行番号で検索 (タグが開く行番号である必要があります)
para = doc["word/document.xml"].get_node(tag="w:p", line_number=42)

# フィルタを組み合わせ
node = doc["word/document.xml"].get_node(tag="w:r", line_number=range(40, 60), contains="text")

# テキストが複数回出現する場合の曖昧さ解消 - line_number範囲を追加
node = doc["word/document.xml"].get_node(tag="w:r", contains="Section", line_number=range(2400, 2500))
```

### 保存

```python
# 自動検証付きで保存 (元のディレクトリにコピーバック)
doc.save()  # デフォルトで検証、検証失敗時にエラーを発生

# 別の場所に保存
doc.save('modified-unpacked')

# 検証をスキップ (デバッグのみ - 本番環境でこれが必要な場合はXMLの問題を示します)
doc.save(validate=False)
```

### 直接DOM操作

ライブラリでカバーされていない複雑なシナリオの場合:

```python
# 任意のXMLファイルにアクセス
editor = doc["word/document.xml"]
editor = doc["word/comments.xml"]

# 直接DOMアクセス (defusedxml.minidom.Document)
node = doc["word/document.xml"].get_node(tag="w:p", line_number=5)
parent = node.parentNode
parent.removeChild(node)
parent.appendChild(node)  # 末尾に移動

# 一般的なドキュメント操作 (変更履歴なし)
old_node = doc["word/document.xml"].get_node(tag="w:p", contains="original text")
doc["word/document.xml"].replace_node(old_node, "<w:p><w:r><w:t>replacement text</w:t></w:r></w:p>")

# 複数の挿入 - 順序を維持するために戻り値を使用
node = doc["word/document.xml"].get_node(tag="w:r", line_number=100)
nodes = doc["word/document.xml"].insert_after(node, "<w:r><w:t>A</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>B</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>C</w:t></w:r>")
# 結果: original_node, A, B, C
```

## 変更履歴 (赤線)

**すべての変更履歴には、上記の Document クラスを使用します。** 以下のパターンは、置換XML文字列を構築する際の参照用です。

### 検証ルール

バリデータは、Claude の変更を元に戻した後、ドキュメントのテキストが元のテキストと一致することを確認します。これは次のことを意味します:

- **他の作成者の `<w:ins>` または `<w:del>` タグ内のテキストを変更しないでください**
- **常にネストされた削除を使用してください** 他の作成者の挿入を削除する場合
- **すべての編集は適切に追跡される必要があります** `<w:ins>` または `<w:del>` タグを使用

### 変更履歴パターン

**重要なルール**:

1. 他の作成者の変更履歴内のコンテンツを変更しないでください。常にネストされた削除を使用します。
2. **XML構造**: `<w:del>` と `<w:ins>` は常に段落レベルに配置し、完全な `<w:r>` 要素を含めます。`<w:r>` 要素内にネストしないでください - これは、ドキュメント処理を壊す無効なXMLを作成します。

**テキスト挿入:**

```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidR="00792858">
    <w:t>挿入されたテキスト</w:t>
  </w:r>
</w:ins>
```

**テキスト削除:**

```xml
<w:del w:id="2" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidDel="00792858">
    <w:delText>削除されたテキスト</w:delText>
  </w:r>
</w:del>
```

**他の作成者の挿入を削除 (ネスト構造を使用する必要があります):**

```xml
<!-- 元の挿入内に削除をネスト -->
<w:ins w:author="Jane Smith" w:id="16">
  <w:del w:author="Claude" w:id="40">
    <w:r><w:delText>monthly</w:delText></w:r>
  </w:del>
</w:ins>
<w:ins w:author="Claude" w:id="41">
  <w:r><w:t>weekly</w:t></w:r>
</w:ins>
```

**他の作成者の削除を復元:**

```xml
<!-- 彼らの削除を変更せず、その後に新しい挿入を追加 -->
<w:del w:author="Jane Smith" w:id="50">
  <w:r><w:delText>within 30 days</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="51">
  <w:r><w:t>within 30 days</w:t></w:r>
</w:ins>
```
