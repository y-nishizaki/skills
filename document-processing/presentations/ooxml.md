# PowerPoint用Office Open XML技術リファレンス

**重要: 開始する前にこのドキュメント全体を読んでください。** 重要なXMLスキーマルールと書式要件は全体にわたってカバーされています。誤った実装は、PowerPointが開けない無効なPPTXファイルを作成する可能性があります。

## 技術ガイドライン

### スキーマ準拠
- **`<p:txBody>`内の要素順序**: `<a:bodyPr>`、`<a:lstStyle>`、`<a:p>`
- **空白**: 先頭/末尾にスペースがある`<a:t>`要素に`xml:space='preserve'`を追加
- **Unicode**: ASCIIコンテンツ内の文字をエスケープ: `"`は`&#8220;`になる
- **画像**: `ppt/media/`に追加し、スライドXMLで参照し、スライド境界に収まるように寸法を設定
- **リレーションシップ**: 各スライドのリソースに対して`ppt/slides/_rels/slideN.xml.rels`を更新
- **dirty属性**: クリーンな状態を示すために`<a:rPr>`と`<a:endParaRPr>`要素に`dirty="0"`を追加

## プレゼンテーション構造

### 基本的なスライド構造
```xml
<!-- ppt/slides/slide1.xml -->
<p:sld>
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>...</p:nvGrpSpPr>
      <p:grpSpPr>...</p:grpSpPr>
      <!-- 図形はここに配置 -->
    </p:spTree>
  </p:cSld>
</p:sld>
```

### テキスト付きテキストボックス/図形
```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="2" name="Title"/>
    <p:cNvSpPr>
      <a:spLocks noGrp="1"/>
    </p:cNvSpPr>
    <p:nvPr>
      <p:ph type="ctrTitle"/>
    </p:nvPr>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="838200" y="365125"/>
      <a:ext cx="7772400" cy="1470025"/>
    </a:xfrm>
  </p:spPr>
  <p:txBody>
    <a:bodyPr/>
    <a:lstStyle/>
    <a:p>
      <a:r>
        <a:t>スライドタイトル</a:t>
      </a:r>
    </a:p>
  </p:txBody>
</p:sp>
```

### テキスト書式
```xml
<!-- 太字 -->
<a:r>
  <a:rPr b="1"/>
  <a:t>太字テキスト</a:t>
</a:r>

<!-- イタリック -->
<a:r>
  <a:rPr i="1"/>
  <a:t>イタリックテキスト</a:t>
</a:r>

<!-- 下線 -->
<a:r>
  <a:rPr u="sng"/>
  <a:t>下線付き</a:t>
</a:r>

<!-- ハイライト -->
<a:r>
  <a:rPr>
    <a:highlight>
      <a:srgbClr val="FFFF00"/>
    </a:highlight>
  </a:rPr>
  <a:t>ハイライトされたテキスト</a:t>
</a:r>

<!-- フォントとサイズ -->
<a:r>
  <a:rPr sz="2400" typeface="Arial">
    <a:solidFill>
      <a:srgbClr val="FF0000"/>
    </a:solidFill>
  </a:rPr>
  <a:t>色付きArial 24pt</a:t>
</a:r>

<!-- 完全な書式の例 -->
<a:r>
  <a:rPr lang="en-US" sz="1400" b="1" dirty="0">
    <a:solidFill>
      <a:srgbClr val="FAFAFA"/>
    </a:solidFill>
  </a:rPr>
  <a:t>書式付きテキスト</a:t>
</a:r>
```

### リスト
```xml
<!-- 箇条書きリスト -->
<a:p>
  <a:pPr lvl="0">
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:t>最初の箇条書き</a:t>
  </a:r>
</a:p>

<!-- 番号付きリスト -->
<a:p>
  <a:pPr lvl="0">
    <a:buAutoNum type="arabicPeriod"/>
  </a:pPr>
  <a:r>
    <a:t>最初の番号付き項目</a:t>
  </a:r>
</a:p>

<!-- 第2レベルインデント -->
<a:p>
  <a:pPr lvl="1">
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:t>インデントされた箇条書き</a:t>
  </a:r>
</a:p>
```

### 図形
```xml
<!-- 長方形 -->
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="3" name="Rectangle"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="1000000" y="1000000"/>
      <a:ext cx="3000000" cy="2000000"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
      <a:avLst/>
    </a:prstGeom>
    <a:solidFill>
      <a:srgbClr val="FF0000"/>
    </a:solidFill>
    <a:ln w="25400">
      <a:solidFill>
        <a:srgbClr val="000000"/>
      </a:solidFill>
    </a:ln>
  </p:spPr>
</p:sp>

<!-- 角丸長方形 -->
<p:sp>
  <p:spPr>
    <a:prstGeom prst="roundRect">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:sp>

<!-- 円/楕円 -->
<p:sp>
  <p:spPr>
    <a:prstGeom prst="ellipse">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:sp>
```

### 画像
```xml
<p:pic>
  <p:nvPicPr>
    <p:cNvPr id="4" name="Picture">
      <a:hlinkClick r:id="" action="ppaction://media"/>
    </p:cNvPr>
    <p:cNvPicPr>
      <a:picLocks noChangeAspect="1"/>
    </p:cNvPicPr>
    <p:nvPr/>
  </p:nvPicPr>
  <p:blipFill>
    <a:blip r:embed="rId2"/>
    <a:stretch>
      <a:fillRect/>
    </a:stretch>
  </p:blipFill>
  <p:spPr>
    <a:xfrm>
      <a:off x="1000000" y="1000000"/>
      <a:ext cx="3000000" cy="2000000"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:pic>
```

### テーブル
```xml
<p:graphicFrame>
  <p:nvGraphicFramePr>
    <p:cNvPr id="5" name="Table"/>
    <p:cNvGraphicFramePr>
      <a:graphicFrameLocks noGrp="1"/>
    </p:cNvGraphicFramePr>
    <p:nvPr/>
  </p:nvGraphicFramePr>
  <p:xfrm>
    <a:off x="1000000" y="1000000"/>
    <a:ext cx="6000000" cy="2000000"/>
  </p:xfrm>
  <a:graphic>
    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">
      <a:tbl>
        <a:tblGrid>
          <a:gridCol w="3000000"/>
          <a:gridCol w="3000000"/>
        </a:tblGrid>
        <a:tr h="500000">
          <a:tc>
            <a:txBody>
              <a:bodyPr/>
              <a:lstStyle/>
              <a:p>
                <a:r>
                  <a:t>セル1</a:t>
                </a:r>
              </a:p>
            </a:txBody>
          </a:tc>
          <a:tc>
            <a:txBody>
              <a:bodyPr/>
              <a:lstStyle/>
              <a:p>
                <a:r>
                  <a:t>セル2</a:t>
                </a:r>
              </a:p>
            </a:txBody>
          </a:tc>
        </a:tr>
      </a:tbl>
    </a:graphicData>
  </a:graphic>
</p:graphicFrame>
```

### スライドレイアウト

```xml
<!-- タイトルスライドレイアウト -->
<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="ctrTitle"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- タイトルコンテンツ -->
</p:sp>

<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="subTitle" idx="1"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- サブタイトルコンテンツ -->
</p:sp>

<!-- コンテンツスライドレイアウト -->
<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="title"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- スライドタイトル -->
</p:sp>

<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="body" idx="1"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- コンテンツ本文 -->
</p:sp>
```

## ファイル更新

コンテンツを追加する際、これらのファイルを更新してください:

**`ppt/_rels/presentation.xml.rels`:**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
```

**`ppt/slides/_rels/slide1.xml.rels`:**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>
```

**`[Content_Types].xml`:**
```xml
<Default Extension="png" ContentType="image/png"/>
<Default Extension="jpg" ContentType="image/jpeg"/>
<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
```

**`ppt/presentation.xml`:**
```xml
<p:sldIdLst>
  <p:sldId id="256" r:id="rId1"/>
  <p:sldId id="257" r:id="rId2"/>
</p:sldIdLst>
```

**`docProps/app.xml`:** スライド数と統計を更新
```xml
<Slides>2</Slides>
<Paragraphs>10</Paragraphs>
<Words>50</Words>
```

## スライド操作

### 新しいスライドの追加
プレゼンテーションの最後にスライドを追加する場合:

1. **スライドファイルを作成**（`ppt/slides/slideN.xml`）
2. **`[Content_Types].xml`を更新**: 新しいスライドのOverrideを追加
3. **`ppt/_rels/presentation.xml.rels`を更新**: 新しいスライドのリレーションシップを追加
4. **`ppt/presentation.xml`を更新**: `<p:sldIdLst>`にスライドIDを追加
5. **スライドリレーションシップを作成**（必要に応じて`ppt/slides/_rels/slideN.xml.rels`）
6. **`docProps/app.xml`を更新**: スライド数を増やし、統計を更新（存在する場合）

### スライドの複製
1. ソーススライドXMLファイルを新しい名前でコピー
2. 新しいスライドのすべてのIDを一意になるように更新
3. 上記の「新しいスライドの追加」手順に従う
4. **重要**: `_rels`ファイルのノートスライド参照を削除または更新
5. 未使用のメディアファイルへの参照を削除

### スライドの並べ替え
1. **`ppt/presentation.xml`を更新**: `<p:sldIdLst>`内の`<p:sldId>`要素を並べ替え
2. `<p:sldId>`要素の順序がスライドの順序を決定
3. スライドIDとリレーションシップIDは変更しないでください

例:
```xml
<!-- 元の順序 -->
<p:sldIdLst>
  <p:sldId id="256" r:id="rId2"/>
  <p:sldId id="257" r:id="rId3"/>
  <p:sldId id="258" r:id="rId4"/>
</p:sldIdLst>

<!-- スライド3を位置2に移動した後 -->
<p:sldIdLst>
  <p:sldId id="256" r:id="rId2"/>
  <p:sldId id="258" r:id="rId4"/>
  <p:sldId id="257" r:id="rId3"/>
</p:sldIdLst>
```

### スライドの削除
1. **`ppt/presentation.xml`から削除**: `<p:sldId>`エントリを削除
2. **`ppt/_rels/presentation.xml.rels`から削除**: リレーションシップを削除
3. **`[Content_Types].xml`から削除**: Overrideエントリを削除
4. **ファイルを削除**: `ppt/slides/slideN.xml`と`ppt/slides/_rels/slideN.xml.rels`を削除
5. **`docProps/app.xml`を更新**: スライド数を減らし、統計を更新
6. **未使用のメディアをクリーンアップ**: `ppt/media/`から孤立した画像を削除

注意: 残りのスライドに番号を付け直さない - 元のIDとファイル名を保持してください。

## 避けるべき一般的なエラー

- **エンコーディング**: ASCIIコンテンツ内のUnicode文字をエスケープ: `"`は`&#8220;`になる
- **画像**: `ppt/media/`に追加し、リレーションシップファイルを更新
- **リスト**: リストヘッダーから箇条書きを省略
- **ID**: UUIDに有効な16進数値を使用
- **テーマ**: 色のために`theme`ディレクトリのすべてのテーマを確認

## テンプレートベースのプレゼンテーションの検証チェックリスト

### パッキング前に常に:
- **未使用のリソースをクリーン**: 参照されていないメディア、フォント、ノートディレクトリを削除
- **Content_Types.xmlを修正**: パッケージに存在するすべてのスライド、レイアウト、テーマを宣言
- **リレーションシップIDを修正**:
   - 埋め込みフォントを使用していない場合はフォント埋め込み参照を削除
- **壊れた参照を削除**: 削除されたリソースへの参照のために`_rels`ファイルをすべて確認

### 一般的なテンプレート複製の落とし穴:
- 複製後に複数のスライドが同じノートスライドを参照
- テンプレートスライドからの画像/メディア参照がもはや存在しない
- フォントが含まれていない場合のフォント埋め込み参照
- レイアウト12-25の欠落したslideLayout宣言
- docPropsディレクトリが解凍されない可能性がある - これはオプション
