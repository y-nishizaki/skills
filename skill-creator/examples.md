# スキル作成ツール - 拡張例

このドキュメントは、さまざまなシナリオでスキル作成ツールを使用する詳細な実世界の例を提供します。

## 例1: シンプルなスキルの作成

### ユーザーリクエスト

「MarkdownファイルにMarkdownlintを実行するスキルを作成して」

### スキル作成プロセス

**ステップ0: リサーチを実施**

*WebSearch: 「markdownlint ベストプラクティス 2025」*

- markdownlint-cli2が現在のツール
- `.markdownlint.json` で設定可能
- VS Code拡張機能との統合

*WebFetch: markdownlint公式ドキュメント*

- ルール一覧とオプション
- 一般的な設定パターン
- CLIの使用方法

*Grep: リポジトリ内の既存スキル*

- 類似のリンティングスキルが存在しないか確認
- 既存の命名規則を確認

**リサーチ結果:**
- markdownlint-cli2が最新のツール
- 一般的な設定ファイル: `.markdownlint.json`
- トリガーワード: "markdown lint", "markdownlint", "mdリント"

**ステップ1: 要件を収集**

- **スキル名**: markdown-linter
- **説明**: MarkdownファイルにMarkdownlintを実行してフォーマットと品質をチェックします。「markdown lint」、「markdownlint」、「Markdownチェック」時に使用します。
- **目的**: Markdownファイルの品質を確保し、一貫したフォーマットを維持する
- **指示**: markdownlint-cli2を実行し、エラーを報告し、修正方法を提案する

**ステップ2: ディレクトリ構造を作成**

```bash
mkdir -p markdown-linter
```

**ステップ3: SKILL.mdを生成**

```yaml
---
name: markdown-linter
description: >
  MarkdownファイルにMarkdownlintを実行してフォーマットと品質をチェックします。
  markdown lint、markdownlint、Markdownチェック時に使用します。
version: 1.0.0
dependencies:
  - markdownlint-cli2
---

# Markdownリンター

## 目的

このスキルは、markdownlint-cli2を使用してMarkdownファイルのリンティングを実行し、
フォーマットと品質の問題を特定して修正します。

## 指示

### ステップ1: ファイルを特定

ユーザーが指定したMarkdownファイル、または `.` を使用してすべての `.md` ファイルを
リンティングします。

### ステップ2: Markdownlintを実行

以下のコマンドを実行します：

```bash
npx markdownlint-cli2 "**/*.md"
```

または特定のファイル：

```bash
npx markdownlint-cli2 path/to/file.md
```

### ステップ3: 結果を報告

- エラーがない場合: ユーザーに成功を報告
- エラーがある場合: 各エラーをファイル名と行番号付きでリスト
- 修正方法を提案: 一般的な問題の修正方法を説明

### ステップ4: 修正を提供

可能な場合、`--fix` フラグを使用して自動修正を提供：

```bash
npx markdownlint-cli2 --fix "**/*.md"
```

## 例

### 例1: 単一ファイルのリント

**ユーザーリクエスト**: "README.mdをlintして"

**期待される動作**:
1. `npx markdownlint-cli2 README.md` を実行
2. エラーがあれば報告
3. 修正方法を提案

### 例2: すべてのMarkdownファイルのリント

**ユーザーリクエスト**: "すべてのMarkdownファイルをチェックして"

**期待される動作**:
1. `npx markdownlint-cli2 "**/*.md"` を実行
2. 見つかったすべてのエラーを報告
3. 自動修正を提案

## ベストプラクティス

- 常に結果を明確に報告する
- 可能な場合は自動修正を提供する
- `.markdownlint.json` 設定ファイルを尊重する
- ユーザーにエラーの修正方法を教育する

## エラー処理

- markdownlintがインストールされていない場合: インストール手順を提供
- 設定ファイルエラー: 設定の問題を特定して修正を提案
```

**ステップ4: サポートファイルを作成**

*reference.md* - Markdownlintルールの詳細なリファレンス

*examples.md* - より多くの使用例とシナリオ

**ステップ5: スキルを検証**

- ✓ YAMLフロントマターが有効
- ✓ トリガーキーワードを含む説明
- ✓ 明確なステップバイステップの指示
- ✓ 実用的な例

**ステップ6: 出力**

```
リサーチサマリー:
- 既存の類似スキル: なし
- 推奨ツール: markdownlint-cli2（最新版）
- 主要な発見: --fixフラグで自動修正が可能

作成されたスキル: markdown-linter
場所: ./markdown-linter/

作成されたファイル:
- SKILL.md（メイン定義）
- reference.md（Markdownlintルールリファレンス）
- examples.md（使用例）

次のステップ:
1. 生成されたファイルを確認
2. スキルをテスト: cp -r markdown-linter ~/.claude/skills/
3. 試してみる: "README.mdをlintして"
```

---

## 例2: 複雑なスキルの作成（テンプレート付き）

### ユーザーリクエスト

「Reactコンポーネントテンプレートを生成するスキルを作成して」

### スキル作成プロセス

**ステップ0: リサーチを実施**

*WebSearch: 「React component best practices 2025」*

- React 18+の機能（Hooks、Server Components）
- TypeScript型定義のベストプラクティス
- ファイル構造の規約

*既存のコードベースを確認*

```bash
Glob "**/*.tsx"
Read src/components/Button.tsx  # 例として
```

- 既存の命名規則を特定
- 現在のコンポーネント構造を理解
- TypeScriptパターンを確認

**リサーチ結果:**
- TypeScript + React 18が標準
- 関数コンポーネント + Hooksが推奨
- Propsインターフェースは別に定義
- テストファイルは `.test.tsx` の命名規則

**ステップ1: 要件を収集**

- **スキル名**: react-component-generator
- **説明**: TypeScriptとベストプラクティスを使用してReactコンポーネントテンプレートを生成します。「Reactコンポーネント作成」、「新しいコンポーネント」、「コンポーネント生成」時に使用します。
- **目的**: 一貫したReactコンポーネントボイラープレートを生成
- **テンプレート**: 基本コンポーネント、テストファイル、Storybookストーリー

**ステップ2: ディレクトリ構造を作成**

```bash
mkdir -p react-component-generator/templates
```

**ステップ3: SKILL.mdを生成**

```yaml
---
name: react-component-generator
description: >
  TypeScriptとベストプラクティスを使用してReactコンポーネントテンプレートを生成します。
  Reactコンポーネント作成、新しいコンポーネント、コンポーネント生成時に使用します。
version: 1.0.0
dependencies:
  - react@^18.0.0
  - typescript@^5.0.0
---

# Reactコンポーネントジェネレーター

## 目的

このスキルは、TypeScript、React 18のベストプラクティス、およびテストボイラープレートを
使用して新しいReactコンポーネントファイルを生成します。

## 指示

### ステップ1: コンポーネント情報を収集

ユーザーに以下を尋ねます（提供されていない場合）:
- コンポーネント名（PascalCase）
- コンポーネントタイプ（基本、フォーム、レイアウト）
- 必要なProps
- 場所（デフォルト: `src/components/`）

### ステップ2: テンプレートを選択

コンポーネントタイプに基づいてテンプレートを使用：
- 基本: `templates/basic-component.tsx`
- フォーム: `templates/form-component.tsx`
- レイアウト: `templates/layout-component.tsx`

### ステップ3: ファイルを生成

以下のファイルを作成：
1. `ComponentName.tsx` - メインコンポーネント
2. `ComponentName.test.tsx` - テストファイル
3. `ComponentName.stories.tsx` - Storybookストーリー（オプション）
4. `index.ts` - エクスポート

### ステップ4: テンプレートをカスタマイズ

- プレースホルダーをコンポーネント名に置き換え
- ユーザーが指定したPropsを追加
- インポートを調整
- 型定義を更新

### ステップ5: 確認

生成されたファイルをユーザーに表示し、次のステップを提供。

## 例

### 例1: 基本コンポーネント

**ユーザーリクエスト**: "Buttonという新しいコンポーネントを作成して"

**期待される動作**:
1. コンポーネント名を確認: "Button"
2. タイプを確認: "基本"
3. 必要なPropsを尋ねる: onClick、children、disabled
4. ファイルを生成:
   - `src/components/Button/Button.tsx`
   - `src/components/Button/Button.test.tsx`
   - `src/components/Button/index.ts`
5. 型安全なPropsインターフェースを含める

### 例2: フォームコンポーネント

**ユーザーリクエスト**: "LoginFormコンポーネントを作成して、onSubmitとloadingのpropsが必要です"

**期待される動作**:
1. コンポーネント名: "LoginForm"
2. タイプ: "フォーム"
3. Props: onSubmit、loading
4. フォームテンプレートを使用して生成
5. フォーム処理のベストプラクティスを含める

## ベストプラクティス

- 常にTypeScriptを使用
- Propsインターフェースを定義
- 適切なエクスポートを含める
- テストファイルを生成
- アクセシビリティを考慮
- 一貫した命名規則に従う

## エラー処理

- コンポーネント名が既に存在する場合: 警告し、上書きするか尋ねる
- 無効なコンポーネント名: PascalCaseを提案
- 場所が存在しない場合: ディレクトリを作成するか確認
```

**ステップ4: テンプレートファイルを作成**

*templates/basic-component.tsx*:

```typescript
import React from 'react';

export interface {{COMPONENT_NAME}}Props {
  {{PROPS}}
}

export const {{COMPONENT_NAME}}: React.FC<{{COMPONENT_NAME}}Props> = ({
  {{PROP_DESTRUCTURE}}
}) => {
  return (
    <div className="{{COMPONENT_NAME_LOWER}}">
      {/* コンポーネントの実装 */}
    </div>
  );
};
```

*templates/basic-component.test.tsx*:

```typescript
import { render, screen } from '@testing-library/react';
import { {{COMPONENT_NAME}} } from './{{COMPONENT_NAME}}';

describe('{{COMPONENT_NAME}}', () => {
  it('should render correctly', () => {
    render(<{{COMPONENT_NAME}} />);
    // テストの実装
  });
});
```

**ステップ5: サポートファイルを作成**

*reference.md* - React 18のベストプラクティス、TypeScript型パターン

*examples.md* - 様々なコンポーネントタイプの詳細な例

**ステップ6: スキルを検証**

- ✓ 複数のテンプレート
- ✓ プレースホルダー置換ロジック
- ✓ ファイル生成手順
- ✓ エラー処理

**ステップ7: 出力**

```
リサーチサマリー:
- React 18のベストプラクティスを調査
- TypeScript型パターンを確認
- 既存のコンポーネント構造を分析

作成されたスキル: react-component-generator
場所: ./react-component-generator/

作成されたファイル:
- SKILL.md（メイン定義）
- reference.md（React/TypeScriptリファレンス）
- examples.md（コンポーネント例）
- templates/basic-component.tsx
- templates/basic-component.test.tsx
- templates/form-component.tsx
- templates/layout-component.tsx

次のステップ:
1. テンプレートをプロジェクトの規約に合わせてカスタマイズ
2. スキルをテスト: cp -r react-component-generator ~/.claude/skills/
3. 試してみる: "Buttonコンポーネントを作成して"
```

---

## 例3: 既存スキルの改善

### ユーザーリクエスト

「既存のmarkdown-linterスキルにauto-fix機能を追加して」

### スキル改善プロセス

**ステップ0: リサーチを実施**

*既存のスキルを読む*

```bash
Read markdown-linter/SKILL.md
```

*改善領域を特定*
- 現在の機能を理解
- 追加すべき機能を特定
- 既存のユーザーワークフローを維持

*WebSearch: 「markdownlint auto-fix」*
- `--fix` フラグの使い方
- 自動修正の制限事項
- ベストプラクティス

**リサーチ結果:**
- `--fix` フラグで多くのエラーを自動修正可能
- 一部のエラーは手動修正が必要
- ユーザーに確認を求めるべき

**ステップ1: 既存のSKILL.mdを読む**

```bash
Read markdown-linter/SKILL.md
```

**ステップ2: 改善点を特定**

- ✓ auto-fixステップを追加
- ✓ 修正前の確認を追加
- ✓ バックアップの提案を追加
- ✓ 修正できないエラーの処理

**ステップ3: SKILL.mdを更新**

新しいステップを追加：

```markdown
### ステップ3.5: 自動修正の提案

エラーが見つかった場合、ユーザーに自動修正を提案：

**重要**: 修正を適用する前にユーザーの確認を取得します。

1. ユーザーに尋ねる: "これらのエラーを自動的に修正しますか？"
2. 確認された場合:
   ```bash
   npx markdownlint-cli2 --fix "**/*.md"
   ```
3. 修正されたファイルを報告
4. 残っているエラーがあれば手動修正を提案

### ステップ4: バックアップの推奨

大規模な修正の場合、変更をコミットまたはバックアップすることを推奨：

```bash
git add .
git commit -m "Backup before markdownlint auto-fix"
```
```

**ステップ4: examples.mdを更新**

新しい例を追加：

```markdown
### 例3: Auto-fix付きリント

**ユーザーリクエスト**: "Markdownファイルをlintして自動修正して"

**期待される動作**:
1. `npx markdownlint-cli2 "**/*.md"` を実行
2. エラーを報告
3. ユーザーに自動修正の確認を求める
4. 確認後、`--fix` フラグで再実行
5. 修正結果を報告
6. 残っているエラーがあれば手動修正を提案
```

**ステップ5: reference.mdを更新**

auto-fixの制限事項を追加：

```markdown
## Auto-fixの制限事項

以下のエラーは自動修正できません：
- MD013 (行の長さ) - 手動でリフォーマットが必要
- MD002 (最初の見出しレベル) - 構造的な変更が必要
- 一部のリストフォーマットの問題

手動修正が必要なエラーには、明確な修正ガイダンスを提供してください。
```

**ステップ6: 検証とテスト**

```bash
# 改善されたスキルをテスト
cp -r markdown-linter ~/.claude/skills/

# Claude Codeでテスト
# "MarkdownファイルをlintしてAuto-fixして"
```

**ステップ7: 出力**

```
リサーチサマリー:
- markdownlintの--fix機能を調査
- 自動修正の制限事項を特定
- ユーザー確認フローのベストプラクティスを確認

改善されたスキル: markdown-linter
場所: ./markdown-linter/

更新されたファイル:
- SKILL.md（auto-fixステップを追加）
- reference.md（auto-fixの制限事項を追加）
- examples.md（auto-fix例を追加）

追加された機能:
- ✓ 自動修正の提案
- ✓ ユーザー確認フロー
- ✓ バックアップの推奨
- ✓ 修正不可能なエラーの処理

次のステップ:
1. 改善されたスキルをテスト
2. auto-fix機能を試す
3. 必要に応じてさらに調整
```

---

## 例4: スキル作成時のトラブルシューティング

### シナリオ: YAMLフロントマターエラー

**問題**: スキル作成後、YAMLの解析エラーが発生

**ステップ1: エラーを特定**

```
Error: YAML parsing failed in SKILL.md
Line 3: unexpected token
```

**ステップ2: SKILL.mdを確認**

```yaml
---
name: my-skill
description: スキルの説明です  # タブ文字が含まれている！
---
```

**ステップ3: 問題を修正**

- タブ文字をスペースに置換
- 日本語テキストを引用符で囲む
- インデントを確認

**修正後:**

```yaml
---
name: my-skill
description: "スキルの説明です"
---
```

**ステップ4: 検証**

```bash
# YAMLリンターで検証
yamllint SKILL.md
```

---

## 例5: ドメイン固有のスキル作成

### ユーザーリクエスト

「Dockerコンテナのデバッグを支援するスキルを作成して」

### スキル作成プロセス

**ステップ0: 徹底的なリサーチ**

*WebSearch: 「Docker debugging best practices 2025」*

- 一般的なDockerの問題
- デバッグコマンドとツール
- ログ分析のベストプラクティス

*WebFetch: Docker公式ドキュメント*

- `docker logs`、`docker exec`、`docker inspect`
- デバッグモードとフラグ
- トラブルシューティングガイド

*コミュニティリソース*

- Stack Overflowの一般的な問題
- Dockerトラブルシューティングチェックリスト

**リサーチ結果:**
- 一般的な問題: コンテナが起動しない、ネットワーク問題、ボリュームマウント
- 主要コマンド: logs、inspect、exec、stats
- デバッグワークフロー: ログ確認 → コンテナ状態 → 内部調査

**ステップ1: 要件を収集**

- **スキル名**: docker-debugger
- **説明**: Dockerコンテナの問題をデバッグし、一般的な問題を診断します。「Dockerデバッグ」、「コンテナトラブルシューティング」、「Docker問題」時に使用します。
- **目的**: コンテナの問題を体系的に診断し、解決策を提供
- **ワークフロー**: ログ → 状態 → ネットワーク → ボリューム → 内部調査

**ステップ2-3: スキル構造とSKILL.mdを作成**

```yaml
---
name: docker-debugger
description: >
  Dockerコンテナの問題をデバッグし、一般的な問題を診断します。
  Dockerデバッグ、コンテナトラブルシューティング、Docker問題時に使用します。
version: 1.0.0
dependencies:
  - docker
---

# Dockerデバッガー

## 目的

Dockerコンテナの問題を体系的に診断し、一般的な問題の解決策を提供します。

## 指示

### ステップ1: 問題の特定

ユーザーに問題を尋ねます（または自動検出）:
- コンテナが起動しない
- コンテナがクラッシュする
- ネットワーク接続の問題
- ボリューム/ファイルシステムの問題
- パフォーマンスの問題

### ステップ2: 基本診断

すべてのケースで以下を確認：

```bash
# コンテナステータス
docker ps -a | grep <container-name>

# 最近のログ（最後の100行）
docker logs --tail 100 <container-name>

# コンテナの詳細情報
docker inspect <container-name>
```

### ステップ3: 問題固有の診断

**コンテナが起動しない:**
```bash
# 完全なログを確認
docker logs <container-name>

# イメージの確認
docker images | grep <image-name>

# リソース制限を確認
docker inspect <container-name> | grep -A 10 "Memory"
```

**ネットワーク問題:**
```bash
# ネットワーク設定
docker inspect <container-name> | grep -A 20 "Networks"

# コンテナ内から接続テスト
docker exec <container-name> ping <target>
docker exec <container-name> curl <url>
```

**ボリューム問題:**
```bash
# マウント確認
docker inspect <container-name> | grep -A 10 "Mounts"

# コンテナ内のファイル確認
docker exec <container-name> ls -la /mount/path
```

### ステップ4: 解決策の提案

診断結果に基づいて解決策を提供：
- 設定の修正
- 再起動コマンド
- docker-composeの調整
- リソース制限の変更

### ステップ5: 予防策の推奨

将来の問題を防ぐためのベストプラクティスを提案。

## 例

### 例1: クラッシュするコンテナ

**ユーザーリクエスト**: "myappコンテナが起動後すぐにクラッシュします"

**期待される動作**:
1. ステータス確認: `docker ps -a`
2. ログ確認: `docker logs myapp`
3. エラーメッセージを分析
4. 一般的な原因を特定（設定ミス、ポート競合など）
5. 具体的な解決策を提供

## ベストプラクティス

- 常に非破壊的なコマンドから開始
- ユーザーにコマンドの説明を提供
- セキュリティリスクを警告
- バックアップを推奨

## エラー処理

- Dockerがインストールされていない: インストール手順
- 権限エラー: sudoまたはDocker groupへの追加を提案
- コンテナが見つからない: 名前/IDを確認
```

**ステップ4: 包括的なreference.mdを作成**

Dockerコマンドリファレンス、一般的なエラーコード、トラブルシューティングチェックリストを含む詳細なリファレンスドキュメント。

**ステップ5: 実世界のexamples.mdを作成**

様々なDockerデバッグシナリオ（ネットワーク問題、ボリューム問題、パフォーマンス問題など）の詳細な例。

**ステップ6: 検証**

```bash
# 実際のDockerコンテナでテスト
docker run -d --name test-container nginx
# スキルを使用してテストコンテナをデバッグ
```

---

## 一般的なスキル作成パターンの概要

### パターン1: シンプルなツールラッパー

**特徴:**
- 単一のCLIツールをラップ
- SKILL.mdのみで十分
- 明確なステップバイステップの指示

**例:** markdown-linter、eslint-runner、prettier-formatter

### パターン2: テンプレートジェネレーター

**特徴:**
- `templates/` ディレクトリを使用
- プレースホルダー置換ロジック
- 複数のテンプレートオプション

**例:** react-component-generator、api-route-generator

### パターン3: ワークフローオーケストレーター

**特徴:**
- 複数のツール/ステップを組み合わせる
- 条件分岐
- 詳細なreference.mdとexamples.md

**例:** docker-debugger、deploy-assistant

### パターン4: リサーチアシスタント

**特徴:**
- WebSearchとWebFetchを使用
- 情報の検証と統合
- 構造化された出力形式

**例:** research、tech-comparison

---

## スキル作成のヒント

1. **リサーチから始める** - 類似スキルと既存のベストプラクティスを常に確認
2. **シンプルに保つ** - 1つのスキル = 1つの明確な目的
3. **明確なトリガーを使用** - ユーザーが言及する可能性のあるキーワードを含める
4. **実例を含める** - 実世界のシナリオがスキルを明確にする
5. **段階的に文書化** - SKILL.mdは簡潔に、詳細はreference.mdへ
6. **テストする** - 実際の使用例でスキルを検証
7. **反復する** - ユーザーフィードバックに基づいて改善
8. **エラー処理を含める** - 一般的な問題と解決策を予測
9. **依存関係を文書化** - 必要なツールとバージョンを明確に
10. **規約に従う** - リポジトリのスタイルとフォーマット基準を維持

---

## スキル品質チェックリスト

作成前：
- [ ] 類似スキルがないか確認
- [ ] 必要な技術を調査
- [ ] ベストプラクティスを確認
- [ ] トリガーキーワードを特定

作成中：
- [ ] 有効なYAMLフロントマター
- [ ] 明確な説明とトリガー
- [ ] ステップバイステップの指示
- [ ] 実用的な例
- [ ] エラー処理

作成後：
- [ ] YAMLとMarkdownのリント
- [ ] 実際のシナリオでテスト
- [ ] ドキュメントの完全性を確認
- [ ] ファイル構造を検証

---

このexamples.mdは、スキル作成ツールを効果的に使用して、シンプルなものから複雑なものまで、様々なタイプのスキルを作成する方法を示しています。
