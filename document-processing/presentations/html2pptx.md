# HTMLからPowerPointへのガイド

`html2pptx.js`ライブラリを使用して、HTMLスライドを正確な配置でPowerPointプレゼンテーションに変換します。

## 目次

1. [HTMLスライドの作成](#htmlスライドの作成)
2. [html2pptxライブラリの使用](#html2pptxライブラリの使用)
3. [PptxGenJSの使用](#pptxgenjsの使用)

---

## HTMLスライドの作成

すべてのHTMLスライドには適切なbody寸法を含める必要があります:

### レイアウト寸法

- **16:9**（デフォルト）: `width: 720pt; height: 405pt`
- **4:3**: `width: 720pt; height: 540pt`
- **16:10**: `width: 720pt; height: 450pt`

### サポートされる要素

- `<p>`、`<h1>`-`<h6>` - スタイル付きテキスト
- `<ul>`、`<ol>` - リスト（手動の箇条書き記号•、-、*は絶対に使用しない）
- `<b>`、`<strong>` - 太字テキスト（インライン書式）
- `<i>`、`<em>` - イタリックテキスト（インライン書式）
- `<u>` - 下線付きテキスト（インライン書式）
- `<span>` - CSSスタイルを持つインライン書式（太字、イタリック、下線、色）
- `<br>` - 改行
- `<div>`（背景/ボーダー付き） - 図形になる
- `<img>` - 画像
- `class="placeholder"` - チャート用の予約スペース（`{ id, x, y, w, h }`を返す）

### 重要なテキストルール

**すべてのテキストは`<p>`、`<h1>`-`<h6>`、`<ul>`、または`<ol>`タグ内にある必要があります：**
- ✅ 正しい: `<div><p>ここにテキスト</p></div>`
- ❌ 間違い: `<div>ここにテキスト</div>` - **テキストはPowerPointに表示されません**
- ❌ 間違い: `<span>テキスト</span>` - **テキストはPowerPointに表示されません**
- テキストタグのない`<div>`または`<span>`内のテキストは黙って無視されます

**手動の箇条書き記号（•、-、*など）は絶対に使用しない** - 代わりに`<ul>`または`<ol>`リストを使用してください

**普遍的に利用可能なWebセーフフォントのみを使用：**
- ✅ Webセーフフォント: `Arial`、`Helvetica`、`Times New Roman`、`Georgia`、`Courier New`、`Verdana`、`Tahoma`、`Trebuchet MS`、`Impact`、`Comic Sans MS`
- ❌ 間違い: `'Segoe UI'`、`'SF Pro'`、`'Roboto'`、カスタムフォント - **レンダリングの問題を引き起こす可能性があります**

### スタイリング

- オーバーフロー検証を壊すマージン崩壊を防ぐために、bodyで`display: flex`を使用
- 間隔には`margin`を使用（paddingはサイズに含まれる）
- インライン書式: `<b>`、`<i>`、`<u>`タグまたはCSSスタイルを持つ`<span>`を使用
  - `<span>`サポート: `font-weight: bold`、`font-style: italic`、`text-decoration: underline`、`color: #rrggbb`
  - `<span>`非サポート: `margin`、`padding`（PowerPointテキストランでサポートされていない）
  - 例: `<span style="font-weight: bold; color: #667eea;">太字の青いテキスト</span>`
- Flexboxが機能 - レンダリングされたレイアウトから計算された位置
- CSSでは`#`プレフィックス付きの16進数カラーを使用
- **テキスト配置**: テキスト長がわずかにずれている場合のテキスト書式のPptxGenJSへのヒントとして、必要に応じてCSS `text-align`（`center`、`right`など）を使用

### 図形スタイリング（DIV要素のみ）

**重要: 背景、ボーダー、シャドウは`<div>`要素でのみ機能し、テキスト要素（`<p>`、`<h1>`-`<h6>`、`<ul>`、`<ol>`）では機能しません**

- **背景**: `<div>`要素のみのCSS `background`または`background-color`
  - 例: `<div style="background: #f0f0f0;">` - 背景付きの図形を作成
- **ボーダー**: `<div>`要素のCSS `border`はPowerPoint図形ボーダーに変換
  - 均一なボーダーをサポート: `border: 2px solid #333333`
  - 部分的なボーダーをサポート: `border-left`、`border-right`、`border-top`、`border-bottom`（線図形としてレンダリング）
  - 例: `<div style="border-left: 8pt solid #E76F51;">`
- **ボーダー半径**: 角丸の`<div>`要素のCSS `border-radius`
  - `border-radius: 50%`以上で円形図形を作成
  - 50%未満のパーセンテージは図形の小さい方の寸法に対して相対的に計算
  - pxとpt単位をサポート（例：`border-radius: 8pt;`、`border-radius: 12px;`）
  - 例: `<div style="border-radius: 25%;">`（100x200pxボックス）= 100pxの25% = 25px半径
- **ボックスシャドウ**: `<div>`要素のCSS `box-shadow`はPowerPointシャドウに変換
  - 外側のシャドウのみをサポート（内側のシャドウは破損を防ぐために無視）
  - 例: `<div style="box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);">`
  - 注意: インセット/内側のシャドウはPowerPointでサポートされておらず、スキップされます

### アイコンとグラデーション

- **重要: CSSグラデーション（`linear-gradient`、`radial-gradient`）は絶対に使用しない** - PowerPointに変換されません
- **常にSharpを使用してグラデーション/アイコンPNGを最初に作成し、HTMLで参照**
- グラデーションの場合: SVGをPNG背景画像にラスタライズ
- アイコンの場合: react-icons SVGをPNG画像にラスタライズ
- すべての視覚効果は、HTMLレンダリング前にラスター画像として事前レンダリングする必要があります

**Sharpでアイコンをラスタライズ：**

```javascript
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const { FaHome } = require('react-icons/fa');

async function rasterizeIconPng(IconComponent, color, size = "256", filename) {
  const svgString = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color: `#${color}`, size: size })
  );

  // SharpでSVGをPNGに変換
  await sharp(Buffer.from(svgString))
    .png()
    .toFile(filename);

  return filename;
}

// 使用法: HTMLで使用する前にアイコンをラスタライズ
const iconPath = await rasterizeIconPng(FaHome, "4472c4", "256", "home-icon.png");
// その後HTMLで参照: <img src="home-icon.png" style="width: 40pt; height: 40pt;">
```

**Sharpでグラデーションをラスタライズ：**

```javascript
const sharp = require('sharp');

async function createGradientBackground(filename) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="562.5">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#COLOR1"/>
        <stop offset="100%" style="stop-color:#COLOR2"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;

  await sharp(Buffer.from(svg))
    .png()
    .toFile(filename);

  return filename;
}

// 使用法: HTML前にグラデーション背景を作成
const bgPath = await createGradientBackground("gradient-bg.png");
// その後HTMLで: <body style="background-image: url('gradient-bg.png');">
```

### 例

```html
<!DOCTYPE html>
<html>
<head>
<style>
html { background: #ffffff; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #f5f5f5; font-family: Arial, sans-serif;
  display: flex;
}
.content { margin: 30pt; padding: 40pt; background: #ffffff; border-radius: 8pt; }
h1 { color: #2d3748; font-size: 32pt; }
.box {
  background: #70ad47; padding: 20pt; border: 3px solid #5a8f37;
  border-radius: 12pt; box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.25);
}
</style>
</head>
<body>
<div class="content">
  <h1>レシピタイトル</h1>
  <ul>
    <li><b>項目:</b> 説明</li>
  </ul>
  <p><b>太字</b>、<i>イタリック</i>、<u>下線</u>付きのテキスト。</p>
  <div id="chart" class="placeholder" style="width: 350pt; height: 200pt;"></div>

  <!-- テキストは<p>タグ内にある必要があります -->
  <div class="box">
    <p>5</p>
  </div>
</div>
</body>
</html>
```

## html2pptxライブラリの使用

### 依存関係

これらのライブラリはグローバルにインストールされており、使用可能です:
- `pptxgenjs`
- `playwright`
- `sharp`

### 基本的な使用法

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';  // HTMLのbody寸法と一致する必要があります

const { slide, placeholders } = await html2pptx('slide1.html', pptx);

// プレースホルダーエリアにチャートを追加
if (placeholders.length > 0) {
    slide.addChart(pptx.charts.LINE, chartData, placeholders[0]);
}

await pptx.writeFile('output.pptx');
```

### APIリファレンス

#### 関数シグネチャ
```javascript
await html2pptx(htmlFile, pres, options)
```

#### パラメータ
- `htmlFile`（文字列）: HTMLファイルへのパス（絶対または相対）
- `pres`（pptxgen）: レイアウトがすでに設定されたPptxGenJSプレゼンテーションインスタンス
- `options`（オブジェクト、オプション）:
  - `tmpDir`（文字列）: 生成されたファイルの一時ディレクトリ（デフォルト: `process.env.TMPDIR || '/tmp'`）
  - `slide`（オブジェクト）: 再利用する既存のスライド（デフォルト: 新しいスライドを作成）

#### 戻り値
```javascript
{
    slide: pptxgenSlide,           // 作成/更新されたスライド
    placeholders: [                 // プレースホルダー位置の配列
        { id: string, x: number, y: number, w: number, h: number },
        ...
    ]
}
```

### 検証

ライブラリは、スローする前にすべてのエラーを自動的に検証して収集します:

1. **HTML寸法はプレゼンテーションレイアウトと一致する必要があります** - 寸法の不一致を報告
2. **コンテンツはbodyからオーバーフローしてはいけません** - 正確な測定値でオーバーフローを報告
3. **CSSグラデーション** - サポートされていないグラデーションの使用を報告
4. **テキスト要素のスタイリング** - テキスト要素の背景/ボーダー/シャドウを報告（divでのみ許可）

**すべての検証エラーは一度に収集して報告されます**。単一のエラーメッセージで、1つずつではなく、すべての問題を一度に修正できます。

### プレースホルダーの操作

```javascript
const { slide, placeholders } = await html2pptx('slide.html', pptx);

// 最初のプレースホルダーを使用
slide.addChart(pptx.charts.BAR, data, placeholders[0]);

// IDで検索
const chartArea = placeholders.find(p => p.id === 'chart-area');
slide.addChart(pptx.charts.LINE, data, chartArea);
```

### 完全な例

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'あなたの名前';
    pptx.title = 'マイプレゼンテーション';

    // スライド1: タイトル
    const { slide: slide1 } = await html2pptx('slides/title.html', pptx);

    // スライド2: チャート付きコンテンツ
    const { slide: slide2, placeholders } = await html2pptx('slides/data.html', pptx);

    const chartData = [{
        name: '売上',
        labels: ['第1四半期', '第2四半期', '第3四半期', '第4四半期'],
        values: [4500, 5500, 6200, 7100]
    }];

    slide2.addChart(pptx.charts.BAR, chartData, {
        ...placeholders[0],
        showTitle: true,
        title: '四半期売上',
        showCatAxisTitle: true,
        catAxisTitle: '四半期',
        showValAxisTitle: true,
        valAxisTitle: '売上（千ドル）'
    });

    // 保存
    await pptx.writeFile({ fileName: 'presentation.pptx' });
    console.log('プレゼンテーションが正常に作成されました！');
}

createPresentation().catch(console.error);
```

## PptxGenJSの使用

`html2pptx`でHTMLをスライドに変換した後、PptxGenJSを使用してチャート、画像、追加要素などの動的コンテンツを追加します。

### ⚠️ 重要なルール

#### 色
- **PptxGenJSで16進数カラーに`#`プレフィックスを絶対に使用しない** - ファイルの破損を引き起こします
- ✅ 正しい: `color: "FF0000"`、`fill: { color: "0066CC" }`
- ❌ 間違い: `color: "#FF0000"`（ドキュメントを壊す）

### 画像の追加

常に実際の画像寸法からアスペクト比を計算してください:

```javascript
// 画像寸法を取得: identify image.png | grep -o '[0-9]* x [0-9]*'
const imgWidth = 1860, imgHeight = 1519;  // 実際のファイルから
const aspectRatio = imgWidth / imgHeight;

const h = 3;  // 最大高さ
const w = h * aspectRatio;
const x = (10 - w) / 2;  // 16:9スライドで中央揃え

slide.addImage({ path: "chart.png", x, y: 1.5, w, h });
```

### テキストの追加

```javascript
// 書式付きリッチテキスト
slide.addText([
    { text: "太字 ", options: { bold: true } },
    { text: "イタリック ", options: { italic: true } },
    { text: "通常" }
], {
    x: 1, y: 2, w: 8, h: 1
});
```

### 図形の追加

```javascript
// 長方形
slide.addShape(pptx.shapes.RECTANGLE, {
    x: 1, y: 1, w: 3, h: 2,
    fill: { color: "4472C4" },
    line: { color: "000000", width: 2 }
});

// 円
slide.addShape(pptx.shapes.OVAL, {
    x: 5, y: 1, w: 2, h: 2,
    fill: { color: "ED7D31" }
});

// 角丸長方形
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 1, y: 4, w: 3, h: 1.5,
    fill: { color: "70AD47" },
    rectRadius: 0.2
});
```

### チャートの追加

**ほとんどのチャートに必須：** `catAxisTitle`（カテゴリ）と`valAxisTitle`（値）を使用した軸ラベル。

**チャートデータ形式：**
- シンプルな棒/折れ線グラフには**すべてのラベルを持つ単一系列**を使用
- 各系列は個別の凡例エントリを作成
- ラベル配列はX軸の値を定義

**時系列データ - 正しい粒度を選択：**
- **< 30日**: 日次グループ化を使用（例：「10-01」、「10-02」） - 単一ポイントチャートを作成する月次集計を避ける
- **30-365日**: 月次グループ化を使用（例：「2024-01」、「2024-02」）
- **> 365日**: 年次グループ化を使用（例：「2023」、「2024」）
- **検証**: 1つのデータポイントのみのチャートは、期間に対して誤った集計を示している可能性があります

```javascript
const { slide, placeholders } = await html2pptx('slide.html', pptx);

// 正しい: すべてのラベルを持つ単一系列
slide.addChart(pptx.charts.BAR, [{
    name: "2024年売上",
    labels: ["第1四半期", "第2四半期", "第3四半期", "第4四半期"],
    values: [4500, 5500, 6200, 7100]
}], {
    ...placeholders[0],  // プレースホルダー位置を使用
    barDir: 'col',       // 'col' = 垂直棒、'bar' = 水平
    showTitle: true,
    title: '四半期売上',
    showLegend: false,   // 単一系列には凡例は不要
    // 必須の軸ラベル
    showCatAxisTitle: true,
    catAxisTitle: '四半期',
    showValAxisTitle: true,
    valAxisTitle: '売上（千ドル）',
    // オプション: スケーリングを制御（より良い視覚化のためにデータ範囲に基づいて最小値を調整）
    valAxisMaxVal: 8000,
    valAxisMinVal: 0,  // カウント/金額には0を使用; クラスタ化されたデータ（例：4500-7100）の場合、最小値に近い開始を検討
    valAxisMajorUnit: 2000,  // 混雑を防ぐためにy軸ラベルの間隔を制御
    catAxisLabelRotate: 45,  // 混雑している場合はラベルを回転
    dataLabelPosition: 'outEnd',
    dataLabelColor: '000000',
    // 単一系列チャートには単一色を使用
    chartColors: ["4472C4"]  // すべての棒が同じ色
});
```

#### 散布図

**重要**: 散布図のデータ形式は異例です - 最初の系列にX軸の値が含まれ、後続の系列にY値が含まれます:

```javascript
// データを準備
const data1 = [{ x: 10, y: 20 }, { x: 15, y: 25 }, { x: 20, y: 30 }];
const data2 = [{ x: 12, y: 18 }, { x: 18, y: 22 }];

const allXValues = [...data1.map(d => d.x), ...data2.map(d => d.x)];

slide.addChart(pptx.charts.SCATTER, [
    { name: 'X軸', values: allXValues },  // 最初の系列 = X値
    { name: '系列1', values: data1.map(d => d.y) },  // Y値のみ
    { name: '系列2', values: data2.map(d => d.y) }   // Y値のみ
], {
    x: 1, y: 1, w: 8, h: 4,
    lineSize: 0,  // 0 = 接続線なし
    lineDataSymbol: 'circle',
    lineDataSymbolSize: 6,
    showCatAxisTitle: true,
    catAxisTitle: 'X軸',
    showValAxisTitle: true,
    valAxisTitle: 'Y軸',
    chartColors: ["4472C4", "ED7D31"]
});
```

#### 折れ線グラフ

```javascript
slide.addChart(pptx.charts.LINE, [{
    name: "温度",
    labels: ["1月", "2月", "3月", "4月"],
    values: [32, 35, 42, 55]
}], {
    x: 1, y: 1, w: 8, h: 4,
    lineSize: 4,
    lineSmooth: true,
    // 必須の軸ラベル
    showCatAxisTitle: true,
    catAxisTitle: '月',
    showValAxisTitle: true,
    valAxisTitle: '温度（°F）',
    // オプション: Y軸範囲（より良い視覚化のためにデータ範囲に基づいて最小値を設定）
    valAxisMinVal: 0,     // 0から始まる範囲（カウント、パーセンテージなど）
    valAxisMaxVal: 60,
    valAxisMajorUnit: 20,  // 混雑を防ぐためにy軸ラベルの間隔を制御（例：10、20、25）
    // valAxisMinVal: 30,  // 推奨: 範囲内にクラスタ化されたデータ（例：32-55または評価3-5）の場合、変動を示すために最小値に近い軸を開始
    // オプション: チャートカラー
    chartColors: ["4472C4", "ED7D31", "A5A5A5"]
});
```

#### 円グラフ（軸ラベル不要）

**重要**: 円グラフには、`labels`配列のすべてのカテゴリと`values`配列の対応する値を持つ**単一データ系列**が必要です。

```javascript
slide.addChart(pptx.charts.PIE, [{
    name: "市場シェア",
    labels: ["製品A", "製品B", "その他"],  // すべてのカテゴリを1つの配列に
    values: [35, 45, 20]  // すべての値を1つの配列に
}], {
    x: 2, y: 1, w: 6, h: 4,
    showPercent: true,
    showLegend: true,
    legendPos: 'r',  // 右
    chartColors: ["4472C4", "ED7D31", "A5A5A5"]
});
```

#### 複数データ系列

```javascript
slide.addChart(pptx.charts.LINE, [
    {
        name: "製品A",
        labels: ["第1四半期", "第2四半期", "第3四半期", "第4四半期"],
        values: [10, 20, 30, 40]
    },
    {
        name: "製品B",
        labels: ["第1四半期", "第2四半期", "第3四半期", "第4四半期"],
        values: [15, 25, 20, 35]
    }
], {
    x: 1, y: 1, w: 8, h: 4,
    showCatAxisTitle: true,
    catAxisTitle: '四半期',
    showValAxisTitle: true,
    valAxisTitle: '収益（百万ドル）'
});
```

### チャートカラー

**重要**: `#`プレフィックスなしの16進数カラーを使用 - `#`を含めるとファイルの破損を引き起こします。

**選択したデザインパレットとチャートカラーを揃え**、データ視覚化に十分なコントラストと識別性を確保します。次のために色を調整:
- 隣接する系列間の強いコントラスト
- スライド背景に対する読みやすさ
- アクセシビリティ（赤-緑のみの組み合わせを避ける）

```javascript
// 例: オーシャンパレットに触発されたチャートカラー（コントラスト用に調整）
const chartColors = ["16A085", "FF6B9D", "2C3E50", "F39C12", "9B59B6"];

// 単一系列チャート: すべての棒/ポイントに1色を使用
slide.addChart(pptx.charts.BAR, [{
    name: "売上",
    labels: ["第1四半期", "第2四半期", "第3四半期", "第4四半期"],
    values: [4500, 5500, 6200, 7100]
}], {
    ...placeholders[0],
    chartColors: ["16A085"],  // すべての棒が同じ色
    showLegend: false
});

// 複数系列チャート: 各系列が異なる色を取得
slide.addChart(pptx.charts.LINE, [
    { name: "製品A", labels: ["第1四半期", "第2四半期", "第3四半期"], values: [10, 20, 30] },
    { name: "製品B", labels: ["第1四半期", "第2四半期", "第3四半期"], values: [15, 25, 20] }
], {
    ...placeholders[0],
    chartColors: ["16A085", "FF6B9D"]  // 系列ごとに1色
});
```

### テーブルの追加

テーブルは基本的または高度な書式で追加できます:

#### 基本的なテーブル

```javascript
slide.addTable([
    ["ヘッダー1", "ヘッダー2", "ヘッダー3"],
    ["行1、列1", "行1、列2", "行1、列3"],
    ["行2、列1", "行2、列2", "行2、列3"]
], {
    x: 0.5,
    y: 1,
    w: 9,
    h: 3,
    border: { pt: 1, color: "999999" },
    fill: { color: "F1F1F1" }
});
```

#### カスタム書式付きテーブル

```javascript
const tableData = [
    // カスタムスタイリング付きヘッダー行
    [
        { text: "製品", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } },
        { text: "収益", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } },
        { text: "成長", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } }
    ],
    // データ行
    ["製品A", "$50M", "+15%"],
    ["製品B", "$35M", "+22%"],
    ["製品C", "$28M", "+8%"]
];

slide.addTable(tableData, {
    x: 1,
    y: 1.5,
    w: 8,
    h: 3,
    colW: [3, 2.5, 2.5],  // 列幅
    rowH: [0.5, 0.6, 0.6, 0.6],  // 行の高さ
    border: { pt: 1, color: "CCCCCC" },
    align: "center",
    valign: "middle",
    fontSize: 14
});
```

#### 結合セル付きテーブル

```javascript
const mergedTableData = [
    [
        { text: "第1四半期の結果", options: { colspan: 3, fill: { color: "4472C4" }, color: "FFFFFF", bold: true } }
    ],
    ["製品", "売上", "市場シェア"],
    ["製品A", "$25M", "35%"],
    ["製品B", "$18M", "25%"]
];

slide.addTable(mergedTableData, {
    x: 1,
    y: 1,
    w: 8,
    h: 2.5,
    colW: [3, 2.5, 2.5],
    border: { pt: 1, color: "DDDDDD" }
});
```

### テーブルオプション

一般的なテーブルオプション:
- `x, y, w, h` - 位置とサイズ
- `colW` - 列幅の配列（インチ単位）
- `rowH` - 行の高さの配列（インチ単位）
- `border` - ボーダースタイル: `{ pt: 1, color: "999999" }`
- `fill` - 背景色（#プレフィックスなし）
- `align` - テキスト配置: "left"、"center"、"right"
- `valign` - 垂直配置: "top"、"middle"、"bottom"
- `fontSize` - テキストサイズ
- `autoPage` - コンテンツがオーバーフローする場合に新しいスライドを自動作成
