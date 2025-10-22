# テスト自動化: 実装例とパターン

このドキュメントでは、テスト自動化スキルで説明されている各種テストパターン、フレームワーク、ベストプラクティスの具体例を示します。

## 目次

- [ユニットテストの例](#ユニットテストの例)
- [統合テストの例](#統合テストの例)
- [E2Eテストの例](#e2eテストの例)
- [テストパターン](#テストパターン)
- [フレームワーク別実装例](#フレームワーク別実装例)

## ユニットテストの例

### 例1: シンプルな関数のテスト（Python）

**テスト対象:**

```python
# calculator.py
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

**テスト:**

```python
# test_calculator.py
import pytest
from calculator import add, divide, calculate_discount

class TestAdd:
    def test_add_positive_numbers(self):
        """正の数の加算"""
        result = add(3, 5)
        assert result == 8

    def test_add_negative_numbers(self):
        """負の数の加算"""
        result = add(-3, -5)
        assert result == -8

    def test_add_mixed_numbers(self):
        """正と負の数の加算"""
        result = add(10, -3)
        assert result == 7

class TestDivide:
    def test_divide_normal_case(self):
        """通常の除算"""
        result = divide(10, 2)
        assert result == 5.0

    def test_divide_by_zero_raises_error(self):
        """ゼロ除算でエラー"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

    def test_divide_negative_numbers(self):
        """負の数の除算"""
        result = divide(-10, 2)
        assert result == -5.0

class TestCalculateDiscount:
    def test_discount_normal_case(self):
        """通常の割引計算"""
        result = calculate_discount(1000, 20)
        assert result == 800

    def test_discount_zero_percent(self):
        """0%割引"""
        result = calculate_discount(1000, 0)
        assert result == 1000

    def test_discount_100_percent(self):
        """100%割引"""
        result = calculate_discount(1000, 100)
        assert result == 0

    def test_discount_negative_raises_error(self):
        """負の割引率でエラー"""
        with pytest.raises(ValueError):
            calculate_discount(1000, -10)

    def test_discount_over_100_raises_error(self):
        """100を超える割引率でエラー"""
        with pytest.raises(ValueError):
            calculate_discount(1000, 150)
```

### 例2: クラスのテスト（JavaScript）

**テスト対象:**

```javascript
// ShoppingCart.js
class ShoppingCart {
  constructor() {
    this.items = [];
  }

  addItem(product, quantity = 1) {
    if (quantity <= 0) {
      throw new Error('Quantity must be positive');
    }

    const existingItem = this.items.find(item => item.product.id === product.id);
    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      this.items.push({ product, quantity });
    }
  }

  removeItem(productId) {
    this.items = this.items.filter(item => item.product.id !== productId);
  }

  getTotal() {
    return this.items.reduce((total, item) => {
      return total + (item.product.price * item.quantity);
    }, 0);
  }

  isEmpty() {
    return this.items.length === 0;
  }

  clear() {
    this.items = [];
  }
}

module.exports = ShoppingCart;
```

**テスト:**

```javascript
// ShoppingCart.test.js
const ShoppingCart = require('./ShoppingCart');

describe('ShoppingCart', () => {
  let cart;

  beforeEach(() => {
    cart = new ShoppingCart();
  });

  describe('addItem', () => {
    test('空のカートに商品を追加できる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };

      cart.addItem(product, 2);

      expect(cart.items).toHaveLength(1);
      expect(cart.items[0].product).toBe(product);
      expect(cart.items[0].quantity).toBe(2);
    });

    test('同じ商品を追加すると数量が増加する', () => {
      const product = { id: 1, name: 'Book', price: 1000 };

      cart.addItem(product, 2);
      cart.addItem(product, 3);

      expect(cart.items).toHaveLength(1);
      expect(cart.items[0].quantity).toBe(5);
    });

    test('負の数量でエラーを投げる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };

      expect(() => {
        cart.addItem(product, -1);
      }).toThrow('Quantity must be positive');
    });

    test('数量を指定しない場合は1になる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };

      cart.addItem(product);

      expect(cart.items[0].quantity).toBe(1);
    });
  });

  describe('removeItem', () => {
    test('商品を削除できる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };
      cart.addItem(product, 2);

      cart.removeItem(1);

      expect(cart.isEmpty()).toBe(true);
    });

    test('存在しない商品IDを指定してもエラーにならない', () => {
      expect(() => {
        cart.removeItem(999);
      }).not.toThrow();
    });
  });

  describe('getTotal', () => {
    test('空のカートの合計は0', () => {
      expect(cart.getTotal()).toBe(0);
    });

    test('単一商品の合計を計算できる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };
      cart.addItem(product, 2);

      expect(cart.getTotal()).toBe(2000);
    });

    test('複数商品の合計を計算できる', () => {
      const book = { id: 1, name: 'Book', price: 1000 };
      const pen = { id: 2, name: 'Pen', price: 100 };

      cart.addItem(book, 2);
      cart.addItem(pen, 5);

      expect(cart.getTotal()).toBe(2500);
    });
  });

  describe('isEmpty', () => {
    test('新しいカートは空', () => {
      expect(cart.isEmpty()).toBe(true);
    });

    test('商品を追加すると空でなくなる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };
      cart.addItem(product);

      expect(cart.isEmpty()).toBe(false);
    });
  });

  describe('clear', () => {
    test('カートをクリアできる', () => {
      const product = { id: 1, name: 'Book', price: 1000 };
      cart.addItem(product, 2);

      cart.clear();

      expect(cart.isEmpty()).toBe(true);
      expect(cart.getTotal()).toBe(0);
    });
  });
});
```

### 例3: モックを使ったテスト（Python）

**テスト対象:**

```python
# user_service.py
class UserService:
    def __init__(self, database, email_service):
        self.database = database
        self.email_service = email_service

    def create_user(self, email, name):
        # メールアドレスの重複チェック
        existing_user = self.database.find_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # ユーザーを作成
        user = {
            'email': email,
            'name': name,
            'created_at': datetime.now()
        }
        saved_user = self.database.save(user)

        # ウェルカムメールを送信
        self.email_service.send(
            to=email,
            subject="Welcome!",
            body=f"Hello {name}, welcome to our service!"
        )

        return saved_user

    def get_user_stats(self, user_id):
        user = self.database.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        posts = self.database.get_user_posts(user_id)

        return {
            'user': user,
            'post_count': len(posts),
            'total_likes': sum(post.get('likes', 0) for post in posts)
        }
```

**テスト:**

```python
# test_user_service.py
import pytest
from unittest.mock import Mock, call
from datetime import datetime
from user_service import UserService

class TestUserService:
    @pytest.fixture
    def mock_database(self):
        return Mock()

    @pytest.fixture
    def mock_email_service(self):
        return Mock()

    @pytest.fixture
    def user_service(self, mock_database, mock_email_service):
        return UserService(mock_database, mock_email_service)

    def test_create_user_success(self, user_service, mock_database, mock_email_service):
        """ユーザー作成が成功する"""
        # Arrange
        mock_database.find_by_email.return_value = None
        mock_database.save.return_value = {
            'id': 123,
            'email': 'new@example.com',
            'name': 'New User'
        }

        # Act
        result = user_service.create_user('new@example.com', 'New User')

        # Assert
        assert result['id'] == 123
        assert result['email'] == 'new@example.com'

        # DBメソッドが正しく呼ばれたか
        mock_database.find_by_email.assert_called_once_with('new@example.com')
        mock_database.save.assert_called_once()

        # メールが送信されたか
        mock_email_service.send.assert_called_once_with(
            to='new@example.com',
            subject='Welcome!',
            body='Hello New User, welcome to our service!'
        )

    def test_create_user_duplicate_email_raises_error(
        self, user_service, mock_database, mock_email_service
    ):
        """重複メールアドレスでエラー"""
        # Arrange
        mock_database.find_by_email.return_value = {
            'id': 1,
            'email': 'existing@example.com'
        }

        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            user_service.create_user('existing@example.com', 'New User')

        # メールは送信されない
        mock_email_service.send.assert_not_called()

    def test_get_user_stats_calculates_correctly(
        self, user_service, mock_database
    ):
        """ユーザー統計を正しく計算する"""
        # Arrange
        mock_database.find_by_id.return_value = {
            'id': 1,
            'name': 'Test User'
        }
        mock_database.get_user_posts.return_value = [
            {'id': 1, 'likes': 10},
            {'id': 2, 'likes': 25},
            {'id': 3, 'likes': 5},
        ]

        # Act
        stats = user_service.get_user_stats(1)

        # Assert
        assert stats['post_count'] == 3
        assert stats['total_likes'] == 40
        assert stats['user']['name'] == 'Test User'

    def test_get_user_stats_user_not_found(self, user_service, mock_database):
        """存在しないユーザーでエラー"""
        # Arrange
        mock_database.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            user_service.get_user_stats(999)
```

## 統合テストの例

### 例1: データベース統合テスト（Python + SQLAlchemy）

```python
# test_user_repository_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from repositories import UserRepository

@pytest.fixture(scope='function')
def test_engine():
    """テスト用のインメモリDBエンジン"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope='function')
def test_session(test_engine):
    """テスト用のDBセッション"""
    Session = sessionmaker(bind=test_engine)
    session = Session()

    yield session

    session.rollback()
    session.close()

@pytest.fixture
def user_repository(test_session):
    """テスト対象のリポジトリ"""
    return UserRepository(test_session)

class TestUserRepositoryIntegration:
    def test_save_and_find_user(self, user_repository):
        """ユーザーを保存して取得できる"""
        # ユーザーを保存
        user = User(email='test@example.com', name='Test User')
        saved_user = user_repository.save(user)

        # IDが割り当てられている
        assert saved_user.id is not None

        # 取得できる
        found_user = user_repository.find_by_id(saved_user.id)
        assert found_user is not None
        assert found_user.email == 'test@example.com'
        assert found_user.name == 'Test User'

    def test_find_by_email(self, user_repository):
        """メールアドレスでユーザーを検索できる"""
        # 複数のユーザーを保存
        user1 = User(email='user1@example.com', name='User One')
        user2 = User(email='user2@example.com', name='User Two')
        user_repository.save(user1)
        user_repository.save(user2)

        # メールで検索
        found = user_repository.find_by_email('user2@example.com')
        assert found is not None
        assert found.name == 'User Two'

    def test_update_user(self, user_repository):
        """ユーザー情報を更新できる"""
        # ユーザーを作成
        user = User(email='test@example.com', name='Original Name')
        saved_user = user_repository.save(user)

        # 名前を変更
        saved_user.name = 'Updated Name'
        user_repository.save(saved_user)

        # 変更が保存されている
        updated_user = user_repository.find_by_id(saved_user.id)
        assert updated_user.name == 'Updated Name'

    def test_delete_user(self, user_repository):
        """ユーザーを削除できる"""
        # ユーザーを作成
        user = User(email='test@example.com', name='Test User')
        saved_user = user_repository.save(user)
        user_id = saved_user.id

        # 削除
        user_repository.delete(saved_user)

        # 取得できない
        deleted_user = user_repository.find_by_id(user_id)
        assert deleted_user is None

    def test_find_all_users(self, user_repository):
        """すべてのユーザーを取得できる"""
        # 複数のユーザーを作成
        for i in range(5):
            user = User(email=f'user{i}@example.com', name=f'User {i}')
            user_repository.save(user)

        # すべて取得
        all_users = user_repository.find_all()
        assert len(all_users) == 5
```

### 例2: REST API統合テスト（Python + FastAPI）

```python
# test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app, get_database
from database import TestDatabase

@pytest.fixture
def test_db():
    """テスト用データベース"""
    db = TestDatabase()
    db.reset()
    return db

@pytest.fixture
def client(test_db):
    """テスト用HTTPクライアント"""
    app.dependency_overrides[get_database] = lambda: test_db
    return TestClient(app)

class TestUserAPI:
    def test_create_user(self, client):
        """POST /api/users でユーザーを作成"""
        response = client.post(
            '/api/users',
            json={
                'email': 'new@example.com',
                'name': 'New User',
                'password': 'SecurePass123'
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['email'] == 'new@example.com'
        assert data['name'] == 'New User'
        assert 'id' in data
        assert 'password' not in data  # パスワードは返さない

    def test_create_user_duplicate_email(self, client):
        """重複メールアドレスでエラー"""
        # 1人目を作成
        client.post(
            '/api/users',
            json={'email': 'test@example.com', 'name': 'User 1', 'password': 'pass'}
        )

        # 同じメールで2人目を作成
        response = client.post(
            '/api/users',
            json={'email': 'test@example.com', 'name': 'User 2', 'password': 'pass'}
        )

        assert response.status_code == 400
        assert 'already exists' in response.json()['detail']

    def test_get_user(self, client):
        """GET /api/users/{id} でユーザーを取得"""
        # ユーザーを作成
        create_response = client.post(
            '/api/users',
            json={'email': 'test@example.com', 'name': 'Test User', 'password': 'pass'}
        )
        user_id = create_response.json()['id']

        # 取得
        response = client.get(f'/api/users/{user_id}')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == user_id
        assert data['email'] == 'test@example.com'

    def test_get_user_not_found(self, client):
        """存在しないユーザーで404"""
        response = client.get('/api/users/99999')
        assert response.status_code == 404

    def test_update_user(self, client):
        """PUT /api/users/{id} でユーザーを更新"""
        # ユーザーを作成
        create_response = client.post(
            '/api/users',
            json={'email': 'test@example.com', 'name': 'Original', 'password': 'pass'}
        )
        user_id = create_response.json()['id']

        # 更新
        response = client.put(
            f'/api/users/{user_id}',
            json={'name': 'Updated Name'}
        )

        assert response.status_code == 200
        assert response.json()['name'] == 'Updated Name'

        # 確認
        get_response = client.get(f'/api/users/{user_id}')
        assert get_response.json()['name'] == 'Updated Name'

    def test_delete_user(self, client):
        """DELETE /api/users/{id} でユーザーを削除"""
        # ユーザーを作成
        create_response = client.post(
            '/api/users',
            json={'email': 'test@example.com', 'name': 'Test User', 'password': 'pass'}
        )
        user_id = create_response.json()['id']

        # 削除
        response = client.delete(f'/api/users/{user_id}')
        assert response.status_code == 204

        # 取得できない
        get_response = client.get(f'/api/users/{user_id}')
        assert get_response.status_code == 404

    def test_list_users_pagination(self, client):
        """GET /api/users でページネーション"""
        # 10人のユーザーを作成
        for i in range(10):
            client.post(
                '/api/users',
                json={
                    'email': f'user{i}@example.com',
                    'name': f'User {i}',
                    'password': 'pass'
                }
            )

        # 最初のページ
        response = client.get('/api/users?page=1&limit=5')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 5
        assert data['total'] == 10
        assert data['page'] == 1

        # 2ページ目
        response = client.get('/api/users?page=2&limit=5')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 5
        assert data['page'] == 2
```

## E2Eテストの例

### 例1: Webアプリケーションのテスト（Playwright）

```javascript
// tests/e2e/user-journey.spec.js
const { test, expect } = require('@playwright/test');

test.describe('ユーザー登録から購入まで', () => {
  test('新規ユーザーが商品を購入できる', async ({ page }) => {
    // 1. ホームページを開く
    await page.goto('https://example.com');
    await expect(page).toHaveTitle(/Example Shop/);

    // 2. 新規登録ページへ
    await page.click('text=Sign Up');
    await expect(page).toHaveURL(/\/signup/);

    // 3. 登録フォームを入力
    await page.fill('#email', 'newuser@example.com');
    await page.fill('#name', 'Test User');
    await page.fill('#password', 'SecurePass123');
    await page.fill('#password-confirm', 'SecurePass123');

    // 4. 登録を実行
    await page.click('button[type=submit]');

    // 5. ダッシュボードにリダイレクト
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('.welcome-message')).toContainText('Welcome, Test User');

    // 6. 商品検索
    await page.fill('#search-input', 'laptop');
    await page.click('#search-button');

    // 7. 検索結果を確認
    await expect(page.locator('.search-results')).toBeVisible();
    const productCount = await page.locator('.product-item').count();
    expect(productCount).toBeGreaterThan(0);

    // 8. 最初の商品をクリック
    await page.click('.product-item:first-child');

    // 9. 商品詳細ページを確認
    await expect(page.locator('.product-title')).toBeVisible();
    await expect(page.locator('.product-price')).toBeVisible();

    // 10. カートに追加
    await page.click('button:has-text("Add to Cart")');

    // 11. 成功メッセージを確認
    await expect(page.locator('.toast-success')).toContainText('Added to cart');

    // 12. カート数が更新されている
    await expect(page.locator('.cart-count')).toHaveText('1');

    // 13. カートページへ
    await page.click('.cart-icon');
    await expect(page).toHaveURL(/\/cart/);

    // 14. カート内容を確認
    await expect(page.locator('.cart-item')).toHaveCount(1);

    // 15. チェックアウトへ
    await page.click('button:has-text("Proceed to Checkout")');

    // 16. 配送先情報を入力
    await page.fill('#address', '123 Test Street');
    await page.fill('#city', 'Tokyo');
    await page.fill('#postal-code', '100-0001');

    // 17. 支払い方法を選択（テストモード）
    await page.click('#payment-test-mode');

    // 18. 注文確認
    await page.click('button:has-text("Place Order")');

    // 19. 注文完了ページ
    await expect(page).toHaveURL(/\/order\/confirmation/);
    await expect(page.locator('.success-message')).toContainText('Thank you for your order');

    // 20. 注文番号が表示される
    const orderNumber = await page.locator('.order-number').textContent();
    expect(orderNumber).toMatch(/ORD-\d{8}/);

    // 21. 注文履歴で確認
    await page.click('text=My Orders');
    await expect(page.locator('.order-history')).toContainText(orderNumber);
  });

  test('ログイン済みユーザーがウィッシュリストから購入', async ({ page, context }) => {
    // 事前にログイン
    await context.addCookies([
      {
        name: 'session',
        value: 'test-session-token',
        domain: 'example.com',
        path: '/'
      }
    ]);

    // ダッシュボードへ
    await page.goto('https://example.com/dashboard');

    // ウィッシュリストを開く
    await page.click('text=Wishlist');

    // ウィッシュリストに商品があることを確認
    await expect(page.locator('.wishlist-item')).toHaveCount(3);

    // 最初の商品をカートに追加
    await page.click('.wishlist-item:first-child button:has-text("Add to Cart")');

    // カートから直接購入
    await page.click('.cart-icon');
    await page.click('button:has-text("Quick Checkout")');

    // 既存の配送先を選択
    await page.click('.saved-address:first-child');
    await page.click('button:has-text("Use this address")');

    // 注文確定
    await page.click('button:has-text("Place Order")');

    // 完了確認
    await expect(page.locator('.success-message')).toBeVisible();
  });
});

test.describe('エラーケース', () => {
  test('無効な支払い情報でエラー表示', async ({ page }) => {
    // カートに商品を追加（省略: ヘルパー関数使用）
    await addProductToCart(page, 'laptop');

    // チェックアウト
    await page.click('button:has-text("Checkout")');

    // 無効なカード情報
    await page.fill('#card-number', '1111 1111 1111 1111');
    await page.fill('#card-expiry', '12/25');
    await page.fill('#card-cvc', '123');

    // 注文試行
    await page.click('button:has-text("Place Order")');

    // エラーメッセージ
    await expect(page.locator('.error-message')).toContainText('Invalid card');
    await expect(page).toHaveURL(/\/checkout/); // ページは移動しない
  });

  test('在庫切れ商品をカートに追加できない', async ({ page }) => {
    await page.goto('https://example.com/product/out-of-stock-item');

    // カートに追加ボタンが無効
    const addButton = page.locator('button:has-text("Add to Cart")');
    await expect(addButton).toBeDisabled();

    // 在庫切れメッセージ
    await expect(page.locator('.stock-status')).toContainText('Out of Stock');
  });
});

// ヘルパー関数
async function addProductToCart(page, productName) {
  await page.goto('https://example.com');
  await page.fill('#search-input', productName);
  await page.click('#search-button');
  await page.click('.product-item:first-child');
  await page.click('button:has-text("Add to Cart")');
}
```

### 例2: ページオブジェクトパターン

```javascript
// page-objects/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.submitButton = page.locator('button[type=submit]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('https://example.com/login');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}

// page-objects/DashboardPage.js
class DashboardPage {
  constructor(page) {
    this.page = page;
    this.welcomeMessage = page.locator('.welcome-message');
    this.searchInput = page.locator('#search-input');
    this.cartIcon = page.locator('.cart-icon');
  }

  async isLoaded() {
    await this.welcomeMessage.waitFor({ state: 'visible' });
  }

  async searchProduct(query) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async goToCart() {
    await this.cartIcon.click();
  }
}

// tests/e2e/login.spec.js
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/LoginPage');
const { DashboardPage } = require('../page-objects/DashboardPage');

test.describe('ログイン機能', () => {
  test('有効な認証情報でログインできる', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');

    await dashboardPage.isLoaded();
    await expect(dashboardPage.welcomeMessage).toContainText('Welcome');
  });

  test('無効なパスワードでエラー', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('user@example.com', 'wrong-password');

    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toContain('Invalid credentials');
  });
});
```

## テストパターン

### パターン1: テストファクトリ

```python
# factories.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    name: str = ""
    created_at: datetime = None

class UserFactory:
    """ユーザーのテストデータを生成"""

    _counter = 0

    @classmethod
    def create(cls, **kwargs):
        """カスタマイズ可能なユーザーを生成"""
        cls._counter += 1

        defaults = {
            'id': cls._counter,
            'email': f'user{cls._counter}@example.com',
            'name': f'Test User {cls._counter}',
            'created_at': datetime.now()
        }

        # デフォルト値を上書き
        defaults.update(kwargs)

        return User(**defaults)

    @classmethod
    def create_batch(cls, count, **kwargs):
        """複数のユーザーを生成"""
        return [cls.create(**kwargs) for _ in range(count)]

# 使用例
def test_user_list():
    # デフォルト値で3人生成
    users = UserFactory.create_batch(3)
    assert len(users) == 3

    # カスタマイズして生成
    admin = UserFactory.create(email='admin@example.com', name='Admin User')
    assert admin.email == 'admin@example.com'
```

### パターン2: パラメタライズドテスト

```python
# test_validation.py
import pytest

@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("user+tag@example.co.jp", True),
    ("invalid@", False),
    ("@example.com", False),
    ("no-at-sign.com", False),
    ("", False),
])
def test_email_validation(email, expected):
    """メールアドレスのバリデーション"""
    result = is_valid_email(email)
    assert result == expected

@pytest.mark.parametrize("price,discount,expected", [
    (1000, 0, 1000),
    (1000, 10, 900),
    (1000, 50, 500),
    (1000, 100, 0),
])
def test_discount_calculation(price, discount, expected):
    """割引計算"""
    result = calculate_discount(price, discount)
    assert result == expected
```

### パターン3: フィクスチャの階層化

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope='session')
def engine():
    """セッション全体で1つのエンジン"""
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='session')
def tables(engine):
    """テーブルを作成"""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    """テストごとに新しいセッション"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user(session):
    """テスト用ユーザー"""
    user = User(email='test@example.com', name='Test User')
    session.add(user)
    session.commit()
    return user
```

## フレームワーク別実装例

### Go言語（testing + testify）

```go
// calculator_test.go
package calculator

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

type CalculatorTestSuite struct {
    suite.Suite
    calc *Calculator
}

func (suite *CalculatorTestSuite) SetupTest() {
    suite.calc = NewCalculator()
}

func (suite *CalculatorTestSuite) TestAdd() {
    result := suite.calc.Add(3, 5)
    assert.Equal(suite.T(), 8, result)
}

func (suite *CalculatorTestSuite) TestDivide() {
    result, err := suite.calc.Divide(10, 2)
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), 5.0, result)
}

func (suite *CalculatorTestSuite) TestDivideByZero() {
    _, err := suite.calc.Divide(10, 0)
    assert.Error(suite.T(), err)
    assert.Contains(suite.T(), err.Error(), "cannot divide by zero")
}

func TestCalculatorTestSuite(t *testing.T) {
    suite.Run(t, new(CalculatorTestSuite))
}

// モックの例
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) FindUser(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func TestUserService(t *testing.T) {
    mockDB := new(MockDatabase)
    mockDB.On("FindUser", 1).Return(&User{ID: 1, Name: "Test"}, nil)

    service := NewUserService(mockDB)
    user, err := service.GetUser(1)

    assert.NoError(t, err)
    assert.Equal(t, "Test", user.Name)
    mockDB.AssertExpectations(t)
}
```

### Rust（cargo test）

```rust
// calculator.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        let result = add(3, 5);
        assert_eq!(result, 8);
    }

    #[test]
    fn test_divide() {
        let result = divide(10.0, 2.0);
        assert_eq!(result, Ok(5.0));
    }

    #[test]
    fn test_divide_by_zero() {
        let result = divide(10.0, 0.0);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Cannot divide by zero");
    }

    #[test]
    #[should_panic(expected = "index out of bounds")]
    fn test_panic() {
        let v = vec![1, 2, 3];
        v[10]; // パニックを期待
    }
}
```

## まとめ

テスト自動化の重要原則:

1. **テストピラミッド** - ユニット多、統合中、E2E少
2. **FIRST原則** - Fast, Independent, Repeatable, Self-validating, Timely
3. **AAA パターン** - Arrange, Act, Assert
4. **適切なモック** - 外部依存を分離、テストの独立性
5. **継続的改善** - テストもコードの一部として保守

詳細なテストプロセスについては、[SKILL.md](SKILL.md) を参照してください。
