# マイグレーション支援: 実装例とパターン

このドキュメントでは、マイグレーション支援スキルで説明されている移行パターンの具体例を示します。

## React 17 → 18 への移行

```javascript
// 旧（React 17）
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// 新（React 18）
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);

// Concurrent Features の活用
import { startTransition } from 'react';

function TabContainer() {
  const [tab, setTab] = useState('about');

  function selectTab(nextTab) {
    startTransition(() => {
      setTab(nextTab);
    });
  }
}
```

## データベース移行スクリプト

```sql
-- 20250121_add_user_status.sql
-- UP
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
CREATE INDEX idx_status ON users(status);

-- DOWN
DROP INDEX idx_status ON users;
ALTER TABLE users DROP COLUMN status;
```

## ゼロダウンタイムマイグレーション

```sql
-- 1. 新カラム追加（NULL許可）
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- 2. データ移行
UPDATE users SET new_email = email WHERE new_email IS NULL;

-- 3. NOT NULL制約追加
ALTER TABLE users MODIFY new_email VARCHAR(255) NOT NULL;

-- 4. 古いカラム削除
ALTER TABLE users DROP COLUMN email;

-- 5. カラム名変更
ALTER TABLE users RENAME COLUMN new_email TO email;
```

## カナリアデプロイ

```python
class CanaryDeployment:
    def __init__(self, canary_percentage=10):
        self.canary_percentage = canary_percentage

    def route_request(self, request):
        if random.random() < self.canary_percentage / 100:
            return self.new_system.handle(request)
        return self.old_system.handle(request)

    def monitor_metrics(self):
        old_error_rate = self.get_error_rate(self.old_system)
        new_error_rate = self.get_error_rate(self.new_system)

        if new_error_rate > old_error_rate * 1.5:
            self.rollback()
            raise Exception("Canary deployment failed")

        if new_error_rate <= old_error_rate:
            self.increase_canary_percentage()
```

## ロールバックスクリプト

```bash
#!/bin/bash
# rollback.sh

echo "Starting rollback..."

# トラフィックを旧システムへ
kubectl patch service myapp -p '{"spec":{"selector":{"version":"old"}}}'

# 新システムのスケールダウン
kubectl scale deployment myapp-new --replicas=0

# 検証
curl -f https://myapp.example.com/health || exit 1

echo "Rollback successful"
```

詳細なマイグレーションプロセスについては、[SKILL.md](SKILL.md) を参照してください。
