---
name: "エラーハンドリング改善"
description: "エラー処理とエラーハンドリングの改善。エラー処理、例外処理、エラーハンドリング、リトライ、ログに関する依頼に対応"
---

# エラーハンドリング改善: エラー処理の設計と実装プロセス

## このスキルを使う場面

- エラー処理の実装
- 例外処理の改善
- エラーメッセージの設計
- リトライロジックの実装
- ログ戦略の策定
- ユーザーへのエラー通知

## 思考プロセス

### フェーズ1: エラーの分類と戦略

**ステップ1: エラーの種類を理解する**

**予期可能なエラー:**

- バリデーションエラー
- 認証・認可エラー
- リソース not found
- レート制限
- ビジネスルール違反

**予期不可能なエラー:**

- ネットワークエラー
- データベース接続エラー
- メモリ不足
- 外部API障害
- プログラミングエラー

**ステップ2: エラーハンドリング戦略**

**回復可能 vs 回復不可能:**

```python
# 回復可能: リトライで解決
try:
    response = api_call()
except NetworkError as e:
    # リトライする
    retry_with_backoff()

# 回復不可能: エラー報告
try:
    result = critical_operation()
except FatalError as e:
    # ログして失敗を返す
    logger.error(f"Fatal error: {e}")
    notify_admin(e)
    raise
```

**Fail Fast vs Fail Safe:**

```python
# Fail Fast: 早期にエラー検出
def process_order(order):
    if not order.is_valid():
        raise ValueError("Invalid order")  # すぐに失敗
    # 処理続行

# Fail Safe: 安全側に倒す
def get_user_settings(user_id):
    try:
        return db.get_settings(user_id)
    except DatabaseError:
        return DEFAULT_SETTINGS  # デフォルト値を返す
```

**移行条件:**

- [ ] エラーの種類を特定した
- [ ] ハンドリング戦略を決定した
- [ ] 回復可能性を評価した

### フェーズ2: エラークラスの設計

**ステップ1: カスタムエラー階層**

```python
# Python
class ApplicationError(Exception):
    """アプリケーションのベースエラー"""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(ApplicationError):
    """バリデーションエラー"""
    def __init__(self, message, field=None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field}
        )

class AuthenticationError(ApplicationError):
    """認証エラー"""
    def __init__(self, message):
        super().__init__(message, code="AUTH_ERROR")

class ResourceNotFoundError(ApplicationError):
    """リソースが見つからない"""
    def __init__(self, resource_type, resource_id):
        super().__init__(
            f"{resource_type} not found: {resource_id}",
            code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class ExternalServiceError(ApplicationError):
    """外部サービスエラー"""
    def __init__(self, service_name, original_error):
        super().__init__(
            f"External service error: {service_name}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name, "error": str(original_error)}
        )
```

**JavaScript/TypeScript:**

```typescript
class ApplicationError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends ApplicationError {
  constructor(message: string, field?: string) {
    super(message, 'VALIDATION_ERROR', 400, { field });
  }
}

class NotFoundError extends ApplicationError {
  constructor(resource: string, id: string | number) {
    super(
      `${resource} not found: ${id}`,
      'NOT_FOUND',
      404,
      { resource, id }
    );
  }
}

class UnauthorizedError extends ApplicationError {
  constructor(message: string = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401);
  }
}
```

**ステップ2: エラーコードの体系化**

```typescript
// エラーコード定義
enum ErrorCode {
  // 4xx: クライアントエラー
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',

  // 5xx: サーバーエラー
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  TIMEOUT = 'TIMEOUT',
}
```

**移行条件:**

- [ ] エラー階層を設計した
- [ ] エラーコードを定義した
- [ ] 必要な情報を含めた

### フェーズ3: エラーハンドリングパターン

**ステップ1: Try-Catch パターン**

```python
def get_user(user_id):
    try:
        user = db.query(User).get(user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)
        return user

    except DatabaseError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise ExternalServiceError("database", e)

    except Exception as e:
        # 予期しないエラー
        logger.exception(f"Unexpected error: {e}")
        raise ApplicationError("Internal error")
```

**ステップ2: グローバルエラーハンドラー**

```python
# Flask
from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(ApplicationError)
def handle_application_error(error):
    response = {
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    }
    status_code = getattr(error, 'status_code', 500)
    return jsonify(response), status_code

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource not found"
        }
    }), 404

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.exception("Unexpected error")
    return jsonify({
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    }), 500
```

**Express.js:**

```javascript
// エラーハンドリングミドルウェア
app.use((err, req, res, next) => {
  // ログ記録
  logger.error({
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  // カスタムエラー
  if (err instanceof ApplicationError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
      },
    });
  }

  // 予期しないエラー
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
});
```

**ステップ3: Result/Option パターン**

```typescript
// Result型（エラーを値として扱う）
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function divide(a: number, b: number): Result<number> {
  if (b === 0) {
    return { ok: false, error: new Error('Division by zero') };
  }
  return { ok: true, value: a / b };
}

// 使用例
const result = divide(10, 2);
if (result.ok) {
  console.log(`Result: ${result.value}`);
} else {
  console.error(`Error: ${result.error.message}`);
}
```

**Rust風のResult（TypeScript）:**

```typescript
class Ok<T> {
  constructor(public value: T) {}
  isOk(): this is Ok<T> { return true; }
  isErr(): this is Err<any> { return false; }
}

class Err<E> {
  constructor(public error: E) {}
  isOk(): this is Ok<any> { return false; }
  isErr(): this is Err<E> { return true; }
}

type Result<T, E> = Ok<T> | Err<E>;

function parseJSON(str: string): Result<any, string> {
  try {
    return new Ok(JSON.parse(str));
  } catch (e) {
    return new Err('Invalid JSON');
  }
}
```

**移行条件:**

- [ ] エラーハンドリングパターンを適用した
- [ ] グローバルハンドラーを実装した
- [ ] 一貫性のあるエラーレスポンス

### フェーズ4: リトライロジック

**ステップ1: 指数バックオフ**

```python
import time
import random

def exponential_backoff_retry(
    func,
    max_retries=5,
    base_delay=1,
    max_delay=60,
    exponential_base=2,
    jitter=True
):
    """指数バックオフでリトライ"""
    for attempt in range(max_retries):
        try:
            return func()

        except Exception as e:
            if attempt == max_retries - 1:
                # 最後の試行
                raise

            # 遅延時間計算
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # ジッター追加（同時リトライの分散）
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)

# 使用例
def fetch_data():
    return exponential_backoff_retry(
        lambda: requests.get('https://api.example.com/data'),
        max_retries=3
    )
```

**デコレータ版:**

```python
from functools import wraps

def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """リトライデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise

                    logger.warning(f"Retry {attempt + 1}/{max_retries}: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator

# 使用例
@retry(max_retries=3, delay=1, backoff=2, exceptions=(NetworkError,))
def fetch_user_data(user_id):
    return api.get_user(user_id)
```

**ステップ2: 条件付きリトライ**

```python
def should_retry(error):
    """リトライすべきエラーか判定"""
    # リトライすべきエラー
    retryable_errors = (
        NetworkError,
        TimeoutError,
        ServiceUnavailableError,
    )

    if isinstance(error, retryable_errors):
        return True

    # HTTPステータスコード
    if hasattr(error, 'status_code'):
        # 429 Too Many Requests, 503 Service Unavailable
        if error.status_code in [429, 503]:
            return True

    return False

def conditional_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if not should_retry(e) or attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

**移行条件:**

- [ ] リトライロジックを実装した
- [ ] 適切なバックオフ戦略
- [ ] リトライ条件を定義した

### フェーズ5: ログとモニタリング

**ステップ1: 構造化ログ**

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # カスタムフィールド
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

# 設定
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 使用例
logger.info("User login", extra={"user_id": 123, "request_id": "abc"})
```

**ステップ2: エラー通知**

```python
def handle_critical_error(error, context=None):
    """重大なエラーの処理"""

    # ログ記録
    logger.critical(
        f"Critical error: {error}",
        extra={
            "context": context,
            "error_type": type(error).__name__,
            "stack_trace": traceback.format_exc()
        }
    )

    # メトリクス送信
    metrics.increment('errors.critical', tags=[
        f'error_type:{type(error).__name__}'
    ])

    # 通知（Slack、Email等）
    if should_notify(error):
        send_alert(
            title=f"Critical Error: {type(error).__name__}",
            message=str(error),
            severity="critical",
            context=context
        )

    # エラートラッキング（Sentry等）
    if sentry_sdk:
        sentry_sdk.capture_exception(error)
```

**ステップ3: エラーレート監視**

```python
from collections import deque
from datetime import datetime, timedelta

class ErrorRateMonitor:
    def __init__(self, window_seconds=60, threshold=10):
        self.window_seconds = window_seconds
        self.threshold = threshold
        self.errors = deque()

    def record_error(self, error):
        now = datetime.now()
        self.errors.append(now)

        # 古いエラーを削除
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self.errors and self.errors[0] < cutoff:
            self.errors.popleft()

        # 閾値チェック
        if len(self.errors) > self.threshold:
            self.alert_high_error_rate()

    def alert_high_error_rate(self):
        logger.critical(
            f"High error rate: {len(self.errors)} errors "
            f"in {self.window_seconds}s"
        )
        send_alert("High error rate detected")
```

**移行条件:**

- [ ] ログを実装した
- [ ] エラー通知を設定した
- [ ] モニタリングを構築した

### フェーズ6: ユーザー向けエラーメッセージ

**ステップ1: わかりやすいメッセージ**

```python
# 悪い例
raise Exception("ERR_001: Invalid input")

# 良い例
raise ValidationError(
    "メールアドレスの形式が正しくありません。example@example.com のように入力してください。",
    field="email"
)
```

**ステップ2: 多言語対応**

```python
ERROR_MESSAGES = {
    "ja": {
        "VALIDATION_ERROR": "入力内容に誤りがあります",
        "NOT_FOUND": "指定されたリソースが見つかりません",
        "UNAUTHORIZED": "認証が必要です",
    },
    "en": {
        "VALIDATION_ERROR": "Invalid input",
        "NOT_FOUND": "Resource not found",
        "UNAUTHORIZED": "Authentication required",
    }
}

def get_error_message(code, lang="ja"):
    return ERROR_MESSAGES.get(lang, {}).get(code, "An error occurred")
```

**ステップ3: エラーレスポンスの一貫性**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": [
      {
        "field": "email",
        "message": "メールアドレスは必須です"
      },
      {
        "field": "password",
        "message": "パスワードは8文字以上である必要があります"
      }
    ],
    "request_id": "abc123",
    "timestamp": "2025-01-21T10:30:00Z"
  }
}
```

**移行条件:**

- [ ] わかりやすいメッセージを作成した
- [ ] 一貫性のあるレスポンス
- [ ] ユーザーへの適切な情報提供

## 判断のポイント

### どこでエラーをキャッチするか

**早期（関数内）:**

- バリデーション
- ビジネスルール
- リソースクリーンアップ

**遅延（ハンドラー）:**

- 横断的関心事
- ログ・メトリクス
- HTTPレスポンス

### エラーログのレベル

- **DEBUG**: 開発時のみ
- **INFO**: 通常の動作
- **WARNING**: 注意が必要
- **ERROR**: エラー（回復可能）
- **CRITICAL**: 重大（即座対応必要）

## よくある落とし穴

1. **エラーの握りつぶし**
   - ❌ `except: pass`
   - ✅ 適切にログして処理

2. **スタックトレースの露出**
   - ❌ 本番でスタックトレース表示
   - ✅ ログのみに記録

3. **汎用的すぎる例外**
   - ❌ `except Exception`
   - ✅ 具体的な例外型

4. **エラーメッセージに機密情報**
   - ❌ パスワードやトークンを含む
   - ✅ 一般的なメッセージ

5. **リトライの無限ループ**
   - ❌ 制限なしリトライ
   - ✅ 最大回数を設定

6. **ユーザーへの技術的エラー**
   - ❌ "NullPointerException"
   - ✅ "データの取得に失敗しました"

## 検証ポイント

### 設計段階

- [ ] エラーの種類を分類した
- [ ] エラー階層を設計した
- [ ] ハンドリング戦略を決定した

### 実装段階

- [ ] カスタムエラークラス作成
- [ ] グローバルハンドラー実装
- [ ] リトライロジック実装
- [ ] ログを適切に記録

### テスト段階

- [ ] エラーケースをテスト
- [ ] リトライをテスト
- [ ] エラーレスポンスを確認
- [ ] ログ出力を確認

## 他スキルとの連携

### error-handling + debugging

エラー調査:

1. error-handlingで適切なログ
2. debuggingで原因特定
3. 修正と改善

### error-handling + test-automation

エラーのテスト:

1. error-handlingでエラー設計
2. test-automationでテストケース
3. エラーパスの検証

### error-handling + security-audit

セキュアなエラー処理:

1. security-auditで情報漏洩チェック
2. error-handlingで適切なメッセージ
3. セキュリティ強化

## エラーハンドリングのベストプラクティス

### エラーを値として扱う

- Result/Option パターン
- 明示的なエラー処理
- 型安全性

### 適切なログレベル

- 環境に応じた設定
- 構造化ログ
- コンテキスト情報

### ユーザー体験

- わかりやすいメッセージ
- 解決方法の提示
- 適切なフィードバック

### 監視と改善

- エラーレート監視
- トレンド分析
- 継続的改善
