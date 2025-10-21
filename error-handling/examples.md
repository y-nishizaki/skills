# エラーハンドリング改善: 実装例とパターン

このドキュメントでは、エラーハンドリングスキルで説明されているエラー処理パターンの具体例を示します。

## カスタムエラークラス

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
  }
}

class ValidationError extends ApplicationError {
  constructor(message: string, field?: string) {
    super(message, 'VALIDATION_ERROR', 400, { field });
  }
}

class NotFoundError extends ApplicationError {
  constructor(resource: string, id: string | number) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', 404);
  }
}
```

## グローバルエラーハンドラー

```javascript
// Express.js
app.use((err, req, res, next) => {
  logger.error({
    error: err.message,
    stack: err.stack,
    path: req.path
  });

  if (err instanceof ApplicationError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details
      }
    });
  }

  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  });
});
```

## リトライロジック

```python
import time
import random

def exponential_backoff_retry(func, max_retries=5, base_delay=1):
    """指数バックオフでリトライ"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = min(base_delay * (2 ** attempt), 60)
            delay = delay * (0.5 + random.random())

            print(f"Retry {attempt + 1}/{max_retries} in {delay:.2f}s")
            time.sleep(delay)
```

## 構造化ログ

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

詳細なエラーハンドリングプロセスについては、[SKILL.md](SKILL.md) を参照してください。
