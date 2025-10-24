# DOCXライブラリチュートリアル

JavaScript/TypeScriptで.docxファイルを生成します。

**重要: 作業を開始する前に、このドキュメント全体をお読みください。**重要なフォーマットルールや一般的な落とし穴について全体を通して説明しています - セクションをスキップすると、ファイルの破損やレンダリングの問題が発生する可能性があります。

## セットアップ

docxがグローバルにインストールされていることを前提としています
インストールされていない場合: `npm install -g docx`

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Media,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        InternalHyperlink, TableOfContents, HeadingLevel, BorderStyle, WidthType, TabStopType,
        TabStopPosition, UnderlineType, ShadingType, VerticalAlign, SymbolRun, PageNumber,
        FootnoteReferenceRun, Footnote, PageBreak } = require('docx');

// 作成と保存
const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer)); // Node.js
Packer.toBlob(doc).then(blob => { /* download logic */ }); // Browser
```

## テキストとフォーマット

```javascript
// 重要: 改行に\nを使用しないでください - 常に別々のParagraph要素を使用してください
// ❌ 間違い: new TextRun("Line 1\nLine 2")
// ✅ 正しい: new Paragraph({ children: [new TextRun("Line 1")] }), new Paragraph({ children: [new TextRun("Line 2")] })

// すべてのフォーマットオプションを含む基本的なテキスト
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200, after: 200 },
  indent: { left: 720, right: 720 },
  children: [
    new TextRun({ text: "太字", bold: true }),
    new TextRun({ text: "斜体", italics: true }),
    new TextRun({ text: "下線", underline: { type: UnderlineType.DOUBLE, color: "FF0000" } }),
    new TextRun({ text: "色付き", color: "FF0000", size: 28, font: "Arial" }), // Arialがデフォルト
    new TextRun({ text: "ハイライト", highlight: "yellow" }),
    new TextRun({ text: "取り消し線", strike: true }),
    new TextRun({ text: "x2", superScript: true }),
    new TextRun({ text: "H2O", subScript: true }),
    new TextRun({ text: "SMALL CAPS", smallCaps: true }),
    new SymbolRun({ char: "2022", font: "Symbol" }), // 箇条書き記号 •
    new SymbolRun({ char: "00A9", font: "Arial" })   // 著作権記号 © - 記号にはArialを使用
  ]
})
```

## スタイルとプロフェッショナルなフォーマット

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12ptがデフォルト
    paragraphStyles: [
      // ドキュメントタイトルスタイル - ビルトインのTitleスタイルをオーバーライド
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      // 重要: ビルトイン見出しスタイルをオーバーライドするには、正確なIDを使用してください
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" }, // 16pt
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // TOCに必要
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" }, // 14pt
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
      // カスタムスタイルは独自のIDを使用
      { id: "myStyle", name: "My Style", basedOn: "Normal",
        run: { size: 28, bold: true, color: "000000" },
        paragraph: { spacing: { after: 120 }, alignment: AlignmentType.CENTER } }
    ],
    characterStyles: [{ id: "myCharStyle", name: "My Char Style",
      run: { color: "FF0000", bold: true, underline: { type: UnderlineType.SINGLE } } }]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("ドキュメントタイトル")] }), // オーバーライドされたTitleスタイルを使用
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("見出し1")] }), // オーバーライドされたHeading1スタイルを使用
      new Paragraph({ style: "myStyle", children: [new TextRun("カスタム段落スタイル")] }),
      new Paragraph({ children: [
        new TextRun("通常テキストと "),
        new TextRun({ text: "カスタム文字スタイル", style: "myCharStyle" })
      ]})
    ]
  }]
});
```

**プロフェッショナルなフォントの組み合わせ:**

- **Arial (見出し) + Arial (本文)** - 最も広くサポートされており、清潔でプロフェッショナル
- **Times New Roman (見出し) + Arial (本文)** - クラシックなセリフ見出しとモダンなサンセリフ本文
- **Georgia (見出し) + Verdana (本文)** - 画面表示に最適化、エレガントなコントラスト

**スタイリングの主要原則:**

- **ビルトインスタイルをオーバーライド**: "Heading1"、"Heading2"、"Heading3"などの正確なIDを使用して、Wordのビルトイン見出しスタイルをオーバーライド
- **HeadingLevel定数**: `HeadingLevel.HEADING_1`は"Heading1"スタイルを使用、`HeadingLevel.HEADING_2`は"Heading2"スタイルを使用など
- **outlineLevelを含める**: TOCが正しく機能するように、H1には`outlineLevel: 0`、H2には`outlineLevel: 1`などを設定
- 一貫性のために**カスタムスタイルを使用**（インラインフォーマットの代わりに）
- `styles.default.document.run.font`を使用して**デフォルトフォントを設定** - Arialは広くサポートされています
- 異なるフォントサイズ（タイトル > 見出し > 本文）で**視覚的階層を確立**
- `before`と`after`段落間隔で**適切な間隔を追加**
- **色は控えめに使用**: タイトルと見出し（見出し1、見出し2など）には黒（000000）とグレーのシェードをデフォルトに
- **一貫したマージンを設定**（1440 = 1インチが標準）

## リスト（常に適切なリストを使用 - Unicode箇条書き記号を使用しない）

```javascript
// 箇条書き - 常にnumbering設定を使用し、Unicode記号は使用しない
// 重要: LevelFormat.BULLET定数を使用し、文字列"bullet"は使用しない
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "first-numbered-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "second-numbered-list", // 異なるreference = 1から再開
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    children: [
      // 箇条書きリストアイテム
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("最初の箇条書きポイント")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("2番目の箇条書きポイント")] }),
      // 番号付きリストアイテム
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("最初の番号付きアイテム")] }),
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("2番目の番号付きアイテム")] }),
      // ⚠️ 重要: 異なるreference = 独立したリストで1から再開
      // 同じreference = 前の番号付けを継続
      new Paragraph({ numbering: { reference: "second-numbered-list", level: 0 },
        children: [new TextRun("再び1から開始（異なるreferenceのため）")] })
    ]
  }]
});

// ⚠️ 重要な番号付けルール: 各referenceは独立した番号付きリストを作成
// - 同じreference = 番号付けを継続（1, 2, 3... その後 4, 5, 6...）
// - 異なるreference = 1から再開（1, 2, 3... その後 1, 2, 3...）
// 各独立した番号付きセクションには一意のreference名を使用してください！

// ⚠️ 重要: Unicode箇条書き記号を使用しないでください - 正しく機能しない偽のリストを作成します
// new TextRun("• Item")           // 間違い
// new SymbolRun({ char: "2022" }) // 間違い
// ✅ 常にLevelFormat.BULLETでnumbering設定を使用して、本物のWordリストを作成
```

## テーブル

```javascript
// マージン、枠線、ヘッダー、箇条書きポイントを含む完全なテーブル
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

new Table({
  columnWidths: [4680, 4680], // ⚠️ 重要: テーブルレベルで列幅を設定 - 値はDXA（ポイントの20分の1）
  margins: { top: 100, bottom: 100, left: 180, right: 180 }, // すべてのセルに対して一度設定
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 各セルにも幅を設定
          // ⚠️ 重要: Wordで黒い背景を防ぐために、常にShadingType.CLEARを使用してください。
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "ヘッダー", bold: true, size: 22 })]
          })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 各セルにも幅を設定
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "箇条書きポイント", bold: true, size: 22 })]
          })]
        })
      ]
    }),
    new TableRow({
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 各セルにも幅を設定
          children: [new Paragraph({ children: [new TextRun("通常のデータ")] })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 各セルにも幅を設定
          children: [
            new Paragraph({
              numbering: { reference: "bullet-list", level: 0 },
              children: [new TextRun("最初の箇条書きポイント")]
            }),
            new Paragraph({
              numbering: { reference: "bullet-list", level: 0 },
              children: [new TextRun("2番目の箇条書きポイント")]
            })
          ]
        })
      ]
    })
  ]
})
```

**重要: テーブルの幅と枠線**

- `columnWidths: [width1, width2, ...]`配列と各セルの`width: { size: X, type: WidthType.DXA }`の両方を使用
- 値はDXA（ポイントの20分の1）: 1440 = 1インチ、レターの使用可能幅 = 9360 DXA（1インチのマージン付き）
- 枠線は個々の`TableCell`要素に適用し、`Table`自体には適用しない

**事前計算された列幅（レターサイズで1インチマージン = 合計9360 DXA）:**

- **2列:** `columnWidths: [4680, 4680]`（等幅）
- **3列:** `columnWidths: [3120, 3120, 3120]`（等幅）

## リンクとナビゲーション

```javascript
// 目次（見出しが必要） - 重要: HeadingLevelのみを使用し、カスタムスタイルは使用しない
// ❌ 間違い: new Paragraph({ heading: HeadingLevel.HEADING_1, style: "customHeader", children: [new TextRun("タイトル")] })
// ✅ 正しい: new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("タイトル")] })
new TableOfContents("目次", { hyperlink: true, headingStyleRange: "1-3" }),

// 外部リンク
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "Google", style: "Hyperlink" })],
    link: "https://www.google.com"
  })]
}),

// 内部リンクとブックマーク
new Paragraph({
  children: [new InternalHyperlink({
    children: [new TextRun({ text: "セクションに移動", style: "Hyperlink" })],
    anchor: "section1"
  })]
}),
new Paragraph({
  children: [new TextRun("セクションコンテンツ")],
  bookmark: { id: "section1", name: "section1" }
}),
```

## 画像とメディア

```javascript
// サイズ変更と配置を含む基本的な画像
// 重要: 常に'type'パラメータを指定してください - ImageRunには必須です
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png", // 新要件: 画像タイプを指定する必要があります（png, jpg, jpeg, gif, bmp, svg）
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150, rotation: 0 }, // 回転は度単位
    altText: { title: "ロゴ", description: "会社のロゴ", name: "名前" } // 重要: 3つのフィールドすべてが必須
  })]
})
```

## 改ページ

```javascript
// 手動改ページ
new Paragraph({ children: [new PageBreak()] }),

// 段落の前に改ページ
new Paragraph({
  pageBreakBefore: true,
  children: [new TextRun("これは新しいページから始まります")]
})

// ⚠️ 重要: PageBreakを単独で使用しないでください - Wordが開けない無効なXMLを作成します
// ❌ 間違い: new PageBreak()
// ✅ 正しい: new Paragraph({ children: [new PageBreak()] })
```

## ヘッダー/フッターとページ設定

```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1440 = 1インチ
        size: { orientation: PageOrientation.LANDSCAPE },
        pageNumbers: { start: 1, formatType: "decimal" } // "upperRoman", "lowerRoman", "upperLetter", "lowerLetter"
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun("ヘッダーテキスト")]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun("ページ "), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun(" / "), new TextRun({ children: [PageNumber.TOTAL_PAGES] })]
      })] })
    },
    children: [/* content */]
  }]
});
```

## タブ

```javascript
new Paragraph({
  tabStops: [
    { type: TabStopType.LEFT, position: TabStopPosition.MAX / 4 },
    { type: TabStopType.CENTER, position: TabStopPosition.MAX / 2 },
    { type: TabStopType.RIGHT, position: TabStopPosition.MAX * 3 / 4 }
  ],
  children: [new TextRun("左\t中央\t右")]
})
```

## 定数とクイックリファレンス

- **下線:** `SINGLE`, `DOUBLE`, `WAVY`, `DASH`
- **枠線:** `SINGLE`, `DOUBLE`, `DASHED`, `DOTTED`
- **番号付け:** `DECIMAL` (1,2,3), `UPPER_ROMAN` (I,II,III), `LOWER_LETTER` (a,b,c)
- **タブ:** `LEFT`, `CENTER`, `RIGHT`, `DECIMAL`
- **記号:** `"2022"` (•), `"00A9"` (©), `"00AE"` (®), `"2122"` (™), `"00B0"` (°), `"F070"` (✓), `"F0FC"` (✗)

## 重大な問題と一般的なミス

- **重要: PageBreakは常にParagraph内に配置する必要があります** - 単独のPageBreakはWordが開けない無効なXMLを作成します
- **テーブルセルのシェーディングには常にShadingType.CLEARを使用** - ShadingType.SOLIDは使用しないでください（黒い背景を引き起こします）。
- 測定値はDXA（1440 = 1インチ）| 各テーブルセルには最低1つのParagraphが必要 | TOCにはHeadingLevelスタイルのみが必要
- **常にカスタムスタイルを使用**し、プロフェッショナルな外観と適切な視覚的階層のためにArialフォントを使用
- `styles.default.document.run.font`を使用して**常にデフォルトフォントを設定** - Arialを推奨
- 互換性のために**テーブルにはcolumnWidths配列を常に使用** + 個々のセル幅
- **箇条書きにUnicode記号を使用しない** - 常に`LevelFormat.BULLET`定数を使用した適切なnumbering設定を使用（文字列"bullet"ではなく）
- **改行に\nをどこでも使用しない** - 各行には常に別々のParagraph要素を使用
- **Paragraph children内では常にTextRunオブジェクトを使用** - Paragraphのtextプロパティを直接使用しない
- **画像の重要事項**: ImageRunには`type`パラメータが必須 - 常に"png"、"jpg"、"jpeg"、"gif"、"bmp"、または"svg"を指定
- **箇条書きの重要事項**: `LevelFormat.BULLET`定数を使用する必要があり、文字列"bullet"ではなく、箇条書き文字のために`text: "•"`を含める
- **番号付けの重要事項**: 各numbering referenceは独立したリストを作成します。同じreference = 番号付けを継続（1,2,3 その後 4,5,6）。異なるreference = 1から再開（1,2,3 その後 1,2,3）。各独立した番号付きセクションには一意のreference名を使用してください！
- **TOCの重要事項**: TableOfContentsを使用する場合、見出しはHeadingLevelのみを使用する必要があります - 見出し段落にカスタムスタイルを追加しないでください。さもないとTOCが壊れます
- **テーブル**: `columnWidths`配列 + 個々のセル幅を設定、枠線はテーブルではなくセルに適用
- 一貫したセルパディングのために**テーブルマージンはTABLEレベルで設定**（セルごとの繰り返しを避ける）
