---
name: "テスト自動化"
description: "テスト自動化の戦略と実装。テスト、ユニットテスト、統合テスト、E2Eテスト、テストカバレッジに関する依頼に対応"
---

# テスト自動化: テスト戦略と実装の思考プロセス

## このスキルを使う場面

- 新機能にテストを追加する
- 既存コードのテストカバレッジを向上させる
- テスト戦略を立案する
- CI/CDパイプラインにテストを統合する
- テストが失敗している原因を調査する
- テストフレームワークのセットアップ
- テストのリファクタリング

## 思考プロセス

### フェーズ1: テスト戦略の立案

**ステップ1: 要件とスコープの理解**

テスト対象を明確にする:

**何をテストするか:**

- [ ] テスト対象の機能・コンポーネント
- [ ] ビジネスロジックの重要度
- [ ] リスクの高い部分
- [ ] ユーザー影響の大きい部分

**テストの目的:**

- [ ] 正しく動作することの保証
- [ ] リグレッション防止
- [ ] リファクタリングの安全性確保
- [ ] ドキュメントとしての機能

**制約条件:**

- [ ] 実装期限
- [ ] 既存のテストフレームワーク
- [ ] チームのスキルレベル
- [ ] CI/CDの環境

**ステップ2: テストピラミッドの適用**

適切なテストレベルを選択:

```
        /\
       /E2E\      ← 少数（遅い、高コスト、壊れやすい）
      /------\
     /統合テスト\   ← 中程度
    /----------\
   /ユニットテスト \  ← 多数（速い、低コスト、安定）
  /--------------\
```

**1. ユニットテスト（最も多い）**

対象:
- 個別の関数・メソッド
- クラスの振る舞い
- ビジネスロジック
- エッジケース・境界値

特徴:
- 高速（ミリ秒単位）
- 外部依存なし（モック・スタブ使用）
- 変更に強い
- 開発者がすぐに実行できる

**2. 統合テスト（中程度）**

対象:
- コンポーネント間の連携
- データベース操作
- 外部API呼び出し
- ファイルシステム操作

特徴:
- 中程度の速度（秒単位）
- 実際の依存関係を使用
- より現実的なテスト
- セットアップが必要

**3. E2Eテスト（最も少ない）**

対象:
- ユーザーシナリオ全体
- クリティカルパス
- 主要なビジネスフロー

特徴:
- 低速（分単位）
- システム全体を使用
- 壊れやすい（UI変更等）
- メンテナンスコストが高い

**移行条件:**

- [ ] テスト対象を特定した
- [ ] 適切なテストレベルを決定した
- [ ] テスト優先度を決めた

### フェーズ2: テスト設計

**ステップ1: テストケースの洗い出し**

包括的なテストケースを設計:

**1. 正常系（Happy Path）**

基本的な動作:
- [ ] 典型的な入力での動作
- [ ] 期待される正常な出力
- [ ] 主要なユースケース

**2. 異常系（Error Cases）**

エラー処理:
- [ ] 不正な入力
- [ ] Null/undefined
- [ ] 空データ（空配列、空文字列）
- [ ] 型の不一致

**3. 境界値（Boundary Cases）**

境界条件:
- [ ] 最小値・最大値
- [ ] ゼロ
- [ ] 負の数
- [ ] 配列の最初・最後
- [ ] 文字列の長さ制限

**4. エッジケース**

特殊な状況:
- [ ] 同時実行・競合状態
- [ ] タイムアウト
- [ ] ネットワークエラー
- [ ] リソース不足
- [ ] 権限エラー

**ステップ2: テストデータの準備**

適切なテストデータを用意:

**1. 代表的なデータ**

```python
# 良い例: 現実的なデータ
test_user = {
    "id": 12345,
    "email": "user@example.com",
    "name": "山田太郎",
    "age": 30
}

# 悪い例: 意味のないデータ
test_user = {
    "id": 1,
    "email": "a@a.com",
    "name": "test",
    "age": 1
}
```

**2. フィクスチャの活用**

再利用可能なテストデータ:
- 共通のセットアップ処理
- テストごとの初期化
- クリーンアップ処理

**3. ファクトリパターン**

柔軟なテストデータ生成:
- デフォルト値の提供
- カスタマイズ可能
- 一貫性のあるデータ

**移行条件:**

- [ ] テストケースを網羅的に洗い出した
- [ ] テストデータを準備した
- [ ] テストの実装方針を決めた

### フェーズ3: ユニットテストの実装

**ステップ1: テスト構造の基本**

AAA（Arrange-Act-Assert）パターン:

```python
def test_calculate_total_price():
    # Arrange: テストの準備
    cart = ShoppingCart()
    cart.add_item(Product("Book", 1000), quantity=2)
    cart.add_item(Product("Pen", 100), quantity=5)

    # Act: テスト対象の実行
    total = cart.calculate_total()

    # Assert: 結果の検証
    assert total == 2500
```

**ステップ2: モック・スタブの活用**

外部依存を分離:

**1. モックの使用**

```python
from unittest.mock import Mock, patch

def test_send_email_notification():
    # メール送信をモック
    mock_email_service = Mock()

    # テスト対象を実行
    notifier = Notifier(email_service=mock_email_service)
    notifier.send_welcome_email(user_id=123)

    # モックが正しく呼ばれたか検証
    mock_email_service.send.assert_called_once_with(
        to="user@example.com",
        subject="Welcome!",
        body=ANY
    )
```

**2. スタブの使用**

```python
def test_get_user_profile():
    # データベース呼び出しをスタブ
    class StubDatabase:
        def query(self, user_id):
            return {"id": user_id, "name": "Test User"}

    db = StubDatabase()
    service = UserService(db)

    profile = service.get_user_profile(123)
    assert profile["name"] == "Test User"
```

**3. 依存性注入**

テストしやすい設計:

```python
# 悪い例: ハードコーディング
class UserService:
    def __init__(self):
        self.db = Database()  # テスト困難

    def get_user(self, user_id):
        return self.db.query(user_id)

# 良い例: 依存性注入
class UserService:
    def __init__(self, db):
        self.db = db  # テスト容易

    def get_user(self, user_id):
        return self.db.query(user_id)
```

**ステップ3: 良いテストの原則**

**FIRST原則:**

**Fast（高速）:**
- ユニットテストはミリ秒で完了
- 外部依存を排除
- 頻繁に実行できる

**Independent（独立）:**
- テスト間で依存しない
- 順序に依存しない
- 並列実行可能

**Repeatable（再現可能）:**
- 常に同じ結果
- ランダム性を排除
- 環境に依存しない

**Self-validating（自己検証）:**
- pass/failが明確
- 手動確認不要
- 自動化可能

**Timely（適時）:**
- コード実装と同時
- できればTDD
- 後回しにしない

**移行条件:**

- [ ] ユニットテストを実装した
- [ ] モック・スタブを適切に使用した
- [ ] FIRST原則に従った

### フェーズ4: 統合テストの実装

**ステップ1: 統合テストのセットアップ**

実際の依存関係を使用:

**1. テストデータベースの準備**

```python
import pytest
from sqlalchemy import create_engine

@pytest.fixture(scope="function")
def test_db():
    # テスト用DBを作成
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    yield engine

    # テスト後にクリーンアップ
    Base.metadata.drop_all(engine)

def test_user_repository(test_db):
    repo = UserRepository(test_db)

    # ユーザーを保存
    user = User(name="Test User", email="test@example.com")
    saved_user = repo.save(user)

    # DBから取得して検証
    retrieved = repo.find_by_id(saved_user.id)
    assert retrieved.name == "Test User"
```

**2. テストコンテナの活用**

Docker等で実環境を再現:

```python
import testcontainers.postgres

def test_with_real_postgres():
    with testcontainers.postgres.PostgresContainer("postgres:14") as postgres:
        connection_url = postgres.get_connection_url()

        # 実際のPostgreSQLでテスト
        db = Database(connection_url)
        # ... テスト実行
```

**ステップ2: API統合テストの実装**

エンドポイントのテスト:

```python
def test_create_user_endpoint():
    # テストクライアントを使用
    client = TestClient(app)

    # POSTリクエスト
    response = client.post(
        "/api/users",
        json={"name": "Test User", "email": "test@example.com"}
    )

    # レスポンスを検証
    assert response.status_code == 201
    assert response.json()["name"] == "Test User"

    # DBに保存されたか確認
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user is not None
```

**ステップ3: トランザクション管理**

テストの独立性を保つ:

```python
@pytest.fixture(autouse=True)
def reset_database():
    # テスト前にトランザクション開始
    db.begin()

    yield

    # テスト後にロールバック
    db.rollback()
```

**移行条件:**

- [ ] 統合テストを実装した
- [ ] テストデータの管理を整備した
- [ ] テストの独立性を確保した

### フェーズ5: E2Eテストの実装

**ステップ1: E2Eテストフレームワークの選択**

適切なツールを選択:

**ブラウザ自動化:**
- Playwright: モダン、高速、信頼性高
- Selenium: 広く使われている、ブラウザサポート豊富
- Cypress: 開発者フレンドリー、デバッグしやすい

**API E2E:**
- REST Assured
- Postman/Newman
- Supertest

**ステップ2: ユーザーシナリオのテスト**

重要なフローをテスト:

```javascript
// Playwright例
test('ユーザー登録から購入まで', async ({ page }) => {
  // 1. ホームページを開く
  await page.goto('https://example.com');

  // 2. 新規登録
  await page.click('text=Sign Up');
  await page.fill('#email', 'newuser@example.com');
  await page.fill('#password', 'SecurePass123');
  await page.click('button[type=submit]');

  // 3. 商品を検索
  await page.fill('#search', 'laptop');
  await page.click('button[type=search]');

  // 4. 商品をカートに追加
  await page.click('.product-item:first-child .add-to-cart');

  // 5. チェックアウト
  await page.click('#cart-icon');
  await page.click('text=Checkout');

  // 6. 購入完了を確認
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.order-number')).toContainText(/ORD-\d+/);
});
```

**ステップ3: E2Eテストのベストプラクティス**

**1. ページオブジェクトパターン**

UIの変更に強い:

```javascript
class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.submitButton = page.locator('button[type=submit]');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// テストで使用
test('ログインできる', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('user@example.com', 'password');

  await expect(page.locator('.welcome-message')).toBeVisible();
});
```

**2. 待機処理の適切な使用**

```javascript
// 悪い例: 固定wait
await page.waitForTimeout(3000);  // 遅い、不安定

// 良い例: 条件を待つ
await page.waitForSelector('.loading-spinner', { state: 'hidden' });
await page.waitForLoadState('networkidle');
```

**3. クリティカルパスに集中**

E2Eテストは少数精鋭:
- ユーザー登録・ログイン
- 主要な購入フロー
- 課金処理
- データ損失のリスクがある操作

**移行条件:**

- [ ] E2Eテストを実装した
- [ ] 主要なユーザーシナリオをカバーした
- [ ] メンテナンス性を考慮した

### フェーズ6: テストカバレッジと品質の確認

**ステップ1: カバレッジの測定**

どこがテストされていないか把握:

```bash
# Python例
pytest --cov=myapp --cov-report=html

# JavaScript例
jest --coverage

# Go例
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

**カバレッジの目標:**

- クリティカルなコード: 90%以上
- ビジネスロジック: 80%以上
- UI層・設定コード: 60%以上

**注意:** カバレッジは手段であって目的ではない。100%を目指す必要はない。

**ステップ2: テストの品質評価**

良いテストの条件:

**1. 読みやすい**

```python
# 悪い例
def test_u():
    u = User("a", "b")
    r = u.validate()
    assert r == True

# 良い例
def test_user_validation_succeeds_with_valid_data():
    user = User(email="valid@example.com", password="SecurePass123")

    is_valid = user.validate()

    assert is_valid == True
```

**2. 失敗理由が明確**

```python
# 悪い例
assert result == expected

# 良い例
assert result == expected, \
    f"Expected total price to be {expected}, but got {result}. " \
    f"Cart items: {cart.items}"
```

**3. 一つのテストで一つの概念**

```python
# 悪い例: 複数のことをテスト
def test_user():
    user = User("test@example.com", "pass")
    assert user.email == "test@example.com"
    assert user.validate() == True
    assert user.save() == True
    assert user.delete() == True

# 良い例: 分割
def test_user_has_correct_email():
    user = User("test@example.com", "pass")
    assert user.email == "test@example.com"

def test_user_validates_successfully():
    user = User("test@example.com", "SecurePass123")
    assert user.validate() == True
```

**ステップ3: テストの実行速度**

パフォーマンスの最適化:

**1. 並列実行**

```bash
# pytest
pytest -n auto

# jest
jest --maxWorkers=4
```

**2. 選択的実行**

```bash
# 変更されたファイルのみ
jest --onlyChanged

# 特定のマーク
pytest -m "not slow"
```

**3. テストの分類**

```python
import pytest

@pytest.mark.fast
def test_calculation():
    # 高速なテスト
    pass

@pytest.mark.slow
def test_api_integration():
    # 低速なテスト
    pass
```

**移行条件:**

- [ ] カバレッジを測定した
- [ ] テストの品質を確認した
- [ ] テストが十分に高速

## 判断のポイント

### どのレベルのテストを書くべきか

**ユニットテストを選ぶ場合:**

- ビジネスロジック
- 複雑なアルゴリズム
- エッジケースが多い
- 外部依存がない

**統合テストを選ぶ場合:**

- データベース操作
- 複数コンポーネントの連携
- API統合
- ファイルシステム操作

**E2Eテストを選ぶ場合:**

- クリティカルなユーザーフロー
- 複雑な画面遷移
- 課金・決済処理
- データ損失のリスク

### モックを使うべきか実物を使うべきか

**モックを使う:**

- ユニットテスト
- 外部サービス（課金API等）
- 低速な処理
- 不安定な依存関係

**実物を使う:**

- 統合テスト
- データベース（テスト環境）
- ファイルシステム（一時ディレクトリ）
- 内部サービス

## よくある落とし穴

1. **テストが遅すぎる**
   - ❌ すべてE2Eテスト
   - ✅ ピラミッド型のバランス

2. **テストが壊れやすい**
   - ❌ 実装詳細をテスト
   - ✅ 公開インターフェースをテスト

3. **テストが読みにくい**
   - ❌ 複雑なセットアップ
   - ✅ AAAパターン、明確な命名

4. **カバレッジのための無意味なテスト**
   - ❌ 100%カバレッジが目的
   - ✅ 意味のあるテストケース

5. **テストの独立性がない**
   - ❌ テスト間でデータ共有
   - ✅ 各テストで初期化・クリーンアップ

6. **外部依存のテスト**
   - ❌ 本番APIを叩く
   - ✅ モック・スタブを使用

7. **保守されないテスト**
   - ❌ 失敗したテストを無視
   - ✅ テストもコードの一部として保守

## 検証ポイント

### テスト戦略

- [ ] 適切なテストレベルを選択した
- [ ] テストの優先順位を決めた
- [ ] カバレッジ目標を設定した

### テスト設計

- [ ] 正常系・異常系・境界値をカバー
- [ ] テストデータを準備した
- [ ] テストケースが網羅的

### テスト実装

- [ ] テストが高速
- [ ] テストが独立している
- [ ] テストが読みやすい
- [ ] 失敗理由が明確

### テスト品質

- [ ] カバレッジが十分
- [ ] テストが安定している
- [ ] CI/CDに統合されている
- [ ] 保守しやすい

## 他スキルとの連携

### test-automation → code-review

テスト付きのコードレビュー:
1. テストスキルでテストを書く
2. code-reviewスキルでコードとテストをレビュー
3. テストの品質も評価

### test-automation → refactoring

安全なリファクタリング:
1. テストスキルでテストを書く
2. refactoringスキルでコード改善
3. テストでリグレッションを検出

### test-automation → debugging

テスト駆動デバッグ:
1. debuggingスキルでバグを再現
2. テストスキルで再現テストを作成
3. バグ修正後もテストで保護

### test-automation + ci-cd-setup

継続的テスト:
1. テストスキルでテストを実装
2. ci-cd-setupスキルでパイプライン統合
3. 自動テスト実行

## テスト自動化のベストプラクティス

### TDD（テスト駆動開発）

Red-Green-Refactorサイクル:

1. **Red**: 失敗するテストを書く
2. **Green**: テストを通す最小限のコード
3. **Refactor**: コードを改善

### テストの命名規則

分かりやすい名前:

```python
# パターン: test_<対象>_<条件>_<期待結果>
def test_login_with_valid_credentials_returns_success()
def test_login_with_invalid_password_returns_error()
def test_login_with_empty_email_raises_validation_error()
```

### テストの整理

```
tests/
├── unit/              # ユニットテスト
│   ├── models/
│   ├── services/
│   └── utils/
├── integration/       # 統合テスト
│   ├── api/
│   └── database/
├── e2e/              # E2Eテスト
│   └── scenarios/
└── fixtures/         # 共通テストデータ
    └── factories.py
```

### 継続的改善

- テストの実行時間を監視
- 不安定なテストを修正
- カバレッジの低い部分を補強
- テストコードもリファクタリング
