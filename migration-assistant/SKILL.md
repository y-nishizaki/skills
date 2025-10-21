---
name: "マイグレーション支援"
description: "技術スタックの移行支援。migration、移行、アップグレード、マイグレーション、技術スタック変更に関する依頼に対応"
---

# マイグレーション支援: システム移行の計画と実行プロセス

## このスキルを使う場面

- フレームワークのメジャーバージョンアップ
- プログラミング言語の移行
- ライブラリの置き換え
- データベースの移行
- クラウドプロバイダーの変更
- モノリスからマイクロサービスへ

## 思考プロセス

### フェーズ1: 移行計画の策定

**ステップ1: 現状分析**

移行元の理解:

**技術スタックの棚卸:**

- [ ] 使用中のフレームワーク・ライブラリ
- [ ] バージョン情報
- [ ] 依存関係マップ
- [ ] カスタマイズ箇所
- [ ] 既知の問題点

**影響範囲の特定:**

- [ ] 影響を受けるコード量
- [ ] 変更が必要なファイル数
- [ ] テストカバレッジ
- [ ] ユーザー数・トラフィック
- [ ] ダウンタイム許容度

**リスク評価:**

```
リスクマトリックス:
        影響度
        小  中  大
発 高  中  高  最高
生 中  低  中  高
確 低  低  低  中
率
```

**ステップ2: 移行先の評価**

なぜ移行するのか明確にする:

**移行の目的:**

- パフォーマンス改善
- セキュリティ強化
- 保守性向上
- コスト削減
- サポート終了への対応
- 新機能の活用

**移行先の調査:**

- [ ] ドキュメントの充実度
- [ ] コミュニティの活発さ
- [ ] マイグレーションガイドの有無
- [ ] 破壊的変更のリスト
- [ ] 互換性レイヤーの有無

**ステップ3: 移行戦略の選択**

**Big Bang（一括移行）:**

```
[旧システム] → [停止] → [新システム]
```

**メリット:**
- シンプル
- 期間が短い
- 並行運用不要

**デメリット:**
- リスクが高い
- ダウンタイム発生
- ロールバック困難

**適用場面:**
- 小規模システム
- ダウンタイム許容
- 大きな変更が必要

**Strangler Fig（段階的移行）:**

```
[旧システム] ← → [プロキシ] ← → [新システム]
     ↓                              ↑
  徐々に縮小                    徐々に拡大
```

**メリット:**
- リスク分散
- 段階的検証
- ロールバック容易

**デメリット:**
- 期間が長い
- 複雑性増加
- 並行運用コスト

**適用場面:**
- 大規模システム
- ダウンタイム不可
- 継続的な検証が必要

**Parallel Run（並行運用）:**

```
[旧システム] ← → [ルーター] ← → [新システム]
     ↓                              ↓
  検証用に保持                   徐々に移行
```

**メリット:**
- 比較検証可能
- 安全性が高い
- 段階的移行

**デメリット:**
- リソース2倍
- 同期の複雑さ
- コスト増

**移行条件:**

- [ ] 現状を分析した
- [ ] 移行目的を明確にした
- [ ] 移行戦略を選択した
- [ ] リスクを評価した

### フェーズ2: マイグレーション計画書の作成

**ステップ1: タイムラインの策定**

```
Week 1-2: 準備フェーズ
  - 環境構築
  - 依存関係の整理
  - ツール準備

Week 3-6: 実装フェーズ
  - コア機能の移行
  - テスト実装
  - 段階的デプロイ

Week 7-8: 検証フェーズ
  - 性能テスト
  - セキュリティテスト
  - ユーザー受け入れテスト

Week 9-10: 本番移行
  - Blue-Green デプロイ
  - モニタリング
  - 問題対応

Week 11-12: 安定化
  - バグ修正
  - 最適化
  - 旧システム廃止
```

**ステップ2: チェックリストの作成**

```markdown
## 移行前チェックリスト

### 準備
- [ ] 移行計画書の承認
- [ ] バックアップ取得
- [ ] ロールバック手順の確認
- [ ] 関係者への通知
- [ ] メンテナンスウィンドウの確保

### 環境
- [ ] 開発環境での検証完了
- [ ] ステージング環境での検証完了
- [ ] 本番環境の準備完了
- [ ] モニタリング設定
- [ ] ログ設定

### コード
- [ ] すべてのテストが通過
- [ ] コードレビュー完了
- [ ] ドキュメント更新
- [ ] 設定ファイルの確認

## 移行中チェックリスト

- [ ] サービス停止通知
- [ ] トラフィックの切り替え
- [ ] ヘルスチェック確認
- [ ] エラーログ監視
- [ ] パフォーマンスメトリクス確認

## 移行後チェックリスト

- [ ] 主要機能の動作確認
- [ ] ユーザーからの報告確認
- [ ] エラーレート確認
- [ ] パフォーマンス確認
- [ ] データ整合性確認
- [ ] 旧システムの保持（一定期間）
```

**移行条件:**

- [ ] 計画書を作成した
- [ ] タイムラインを策定した
- [ ] チェックリストを準備した

### フェーズ3: 具体的な移行パターン

**パターン1: React 17 → 18 への移行**

```javascript
// 1. 依存関係の更新
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}

// 2. ルートレンダリングの変更
// 旧（React 17）
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// 新（React 18）
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);

// 3. Concurrent Features の採用
import { startTransition } from 'react';

function TabContainer() {
  const [tab, setTab] = useState('about');

  function selectTab(nextTab) {
    startTransition(() => {
      setTab(nextTab);  // 低優先度の更新
    });
  }

  return (
    <>
      <TabButton onClick={() => selectTab('about')}>About</TabButton>
      <TabButton onClick={() => selectTab('posts')}>Posts</TabButton>
      {tab === 'about' && <AboutTab />}
      {tab === 'posts' && <PostsTab />}
    </>
  );
}

// 4. 自動バッチングの恩恵
// React 18 では自動的にバッチング
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React 18: 1回のレンダリング
  // React 17: 2回のレンダリング
}
```

**パターン2: Python 3.8 → 3.11 への移行**

```python
# 1. 新機能の活用

# 3.9: dict の merge
old = {'a': 1}
new = {'b': 2}
merged = old | new  # {  'a': 1, 'b': 2}

# 3.10: パターンマッチング
def process_command(command):
    match command.split():
        case ["quit"]:
            quit_program()
        case ["load", filename]:
            load_file(filename)
        case ["save", filename]:
            save_file(filename)
        case _:
            print("Unknown command")

# 3.10: 型ヒントの改善
def process(data: list[str] | None) -> dict[str, int]:
    # Union を | で表現
    pass

# 3.11: Exception Groups
try:
    # 複数の非同期タスク
    async with asyncio.TaskGroup() as group:
        task1 = group.create_task(fetch_data1())
        task2 = group.create_task(fetch_data2())
except* HTTPError as e:
    # HTTPError のみキャッチ
    handle_http_errors(e.exceptions)
except* TimeoutError as e:
    # TimeoutError のみキャッチ
    handle_timeout_errors(e.exceptions)

# 2. 非推奨機能の置き換え

# 旧: collections.abc から直接import
from collections import Mapping  # Deprecated

# 新: collections.abc から明示的に
from collections.abc import Mapping
```

**パターン3: MySQL → PostgreSQL への移行**

```sql
-- 1. スキーマの変換

-- MySQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PostgreSQL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. データ型の違い

-- MySQL: TINYINT, MEDIUMINT等
-- PostgreSQL: SMALLINT, INTEGER, BIGINT

-- MySQL: DATETIME
-- PostgreSQL: TIMESTAMP

-- 3. 構文の違い

-- MySQL
SELECT * FROM users LIMIT 10 OFFSET 20;

-- PostgreSQL（同じだが、追加機能あり）
SELECT * FROM users LIMIT 10 OFFSET 20;
SELECT * FROM users OFFSET 20 FETCH FIRST 10 ROWS ONLY;

-- 4. JSON機能

-- PostgreSQL の方が高機能
SELECT data->>'name' FROM users WHERE data @> '{"active": true}';

-- 5. データ移行ツール
-- pgloader を使用
```

```bash
# pgloader での移行
pgloader mysql://user:pass@localhost/mydb \
          postgresql://user:pass@localhost/mydb
```

**パターン4: モノリス → マイクロサービス**

```python
# 1. 境界の特定（ドメイン駆動設計）

# モノリス
class OrderService:
    def create_order(self, user_id, items):
        # ユーザー確認
        user = UserRepository.find(user_id)

        # 在庫確認
        for item in items:
            Inventory.check_stock(item)

        # 注文作成
        order = Order.create(user_id, items)

        # 支払い処理
        Payment.process(order)

        # メール送信
        Email.send_confirmation(user, order)

        return order

# マイクロサービス化

# Order Service
class OrderService:
    def create_order(self, user_id, items):
        # ユーザーサービスAPI呼び出し
        user = self.user_client.get_user(user_id)

        # 在庫サービスAPI呼び出し
        self.inventory_client.reserve_items(items)

        # 注文作成
        order = self.repository.create(user_id, items)

        # イベント発行
        self.event_bus.publish(OrderCreatedEvent(order))

        return order

# Payment Service（別サービス）
class PaymentEventHandler:
    def on_order_created(self, event):
        order = event.order
        # 支払い処理
        result = self.process_payment(order)

        if result.success:
            self.event_bus.publish(PaymentCompletedEvent(order))
        else:
            self.event_bus.publish(PaymentFailedEvent(order))

# Notification Service（別サービス）
class NotificationEventHandler:
    def on_payment_completed(self, event):
        order = event.order
        user = self.user_client.get_user(order.user_id)
        # メール送信
        self.email_service.send_confirmation(user, order)
```

**移行条件:**

- [ ] 移行パターンを適用した
- [ ] テストを実装した
- [ ] 段階的に移行した

### フェーズ4: データ移行

**ステップ1: データ移行戦略**

**双方向同期:**

```python
class DataSynchronizer:
    def sync_old_to_new(self):
        """旧 → 新へのデータ同期"""
        # 旧システムから読み取り
        old_records = old_db.query("SELECT * FROM users WHERE updated_at > ?", last_sync)

        for record in old_records:
            # 新システムへ書き込み
            new_db.upsert("users", transform_record(record))

        self.update_last_sync_time()

    def sync_new_to_old(self):
        """新 → 旧への同期（移行期間中）"""
        # 新システムから読み取り
        new_records = new_db.query("SELECT * FROM users WHERE updated_at > ?", last_sync)

        for record in new_records:
            # 旧システムへ書き込み
            old_db.upsert("users", reverse_transform(record))
```

**差分移行:**

```python
def incremental_migration():
    """差分移行（大量データ向け）"""

    # 1. 初回: 大部分を移行
    migrate_historical_data(cutoff_date="2024-01-01")

    # 2. 差分: 最近のデータを移行
    while not complete:
        migrate_recent_data(since=last_migration_time)
        time.sleep(60)  # 1分ごとに差分移行

    # 3. 最終同期: 停止後に完全同期
    stop_old_system()
    final_sync()
    start_new_system()
```

**ステップ2: データ整合性の検証**

```python
def verify_data_integrity():
    """データ整合性の検証"""

    # レコード数の比較
    old_count = old_db.count("users")
    new_count = new_db.count("users")
    assert old_count == new_count, f"Count mismatch: {old_count} vs {new_count}"

    # サンプルデータの比較
    sample_ids = random.sample(range(1, old_count), 1000)

    mismatches = []
    for user_id in sample_ids:
        old_user = old_db.get("users", user_id)
        new_user = new_db.get("users", user_id)

        if not compare_records(old_user, new_user):
            mismatches.append(user_id)

    if mismatches:
        raise DataMismatchError(f"Found {len(mismatches)} mismatches")

    # チェックサムの比較
    old_checksum = calculate_checksum(old_db, "users")
    new_checksum = calculate_checksum(new_db, "users")
    assert old_checksum == new_checksum
```

**移行条件:**

- [ ] データ移行を実行した
- [ ] 整合性を検証した
- [ ] バックアップを取得した

### フェーズ5: テストと検証

**ステップ1: 互換性テスト**

```python
import pytest

class TestBackwardCompatibility:
    """後方互換性テスト"""

    def test_api_response_format(self):
        """APIレスポンス形式が変わっていないか"""
        response = new_api.get_user(123)
        assert 'id' in response
        assert 'email' in response
        assert 'name' in response

    def test_api_behavior(self):
        """API動作が同じか"""
        old_result = old_api.search_users(query="john")
        new_result = new_api.search_users(query="john")

        assert len(old_result) == len(new_result)
        assert old_result[0]['id'] == new_result[0]['id']
```

**ステップ2: パフォーマンステスト**

```python
import time

def performance_comparison():
    """移行前後のパフォーマンス比較"""

    # 旧システム
    start = time.time()
    for _ in range(1000):
        old_system.process_request()
    old_time = time.time() - start

    # 新システム
    start = time.time()
    for _ in range(1000):
        new_system.process_request()
    new_time = time.time() - start

    improvement = (old_time - new_time) / old_time * 100
    print(f"Performance improvement: {improvement:.2f}%")

    # 期待値チェック
    assert new_time <= old_time * 1.1, "Performance regression detected"
```

**ステップ3: カナリアリリース**

```python
class CanaryDeployment:
    def __init__(self, canary_percentage=10):
        self.canary_percentage = canary_percentage

    def route_request(self, request):
        """リクエストを振り分け"""
        # カナリアグループのユーザー
        if self.is_canary_user(request.user_id):
            return self.new_system.handle(request)

        # ランダムで一部を新システムへ
        if random.random() < self.canary_percentage / 100:
            return self.new_system.handle(request)

        # 残りは旧システム
        return self.old_system.handle(request)

    def monitor_metrics(self):
        """メトリクスを監視"""
        old_error_rate = self.get_error_rate(self.old_system)
        new_error_rate = self.get_error_rate(self.new_system)

        # エラーレートが悪化していないかチェック
        if new_error_rate > old_error_rate * 1.5:
            self.rollback()
            raise Exception("Canary deployment failed: high error rate")

        # 段階的に比率を上げる
        if new_error_rate <= old_error_rate:
            self.increase_canary_percentage()
```

**移行条件:**

- [ ] テストを実施した
- [ ] パフォーマンスを確認した
- [ ] 段階的にリリースした

### フェーズ6: ロールバック計画

**ステップ1: ロールバック手順**

```bash
#!/bin/bash
# rollback.sh

echo "Starting rollback..."

# 1. トラフィックを旧システムへ
kubectl patch service myapp -p '{"spec":{"selector":{"version":"old"}}}'

# 2. 新システムのスケールダウン
kubectl scale deployment myapp-new --replicas=0

# 3. 検証
curl -f https://myapp.example.com/health || exit 1

# 4. データの巻き戻し（必要な場合）
./restore_database.sh

# 5. 通知
send_notification "Rollback completed"

echo "Rollback successful"
```

**ステップ2: ロールバック判断基準**

```python
class RollbackDecision:
    def should_rollback(self):
        """ロールバックすべきか判定"""

        # エラーレートのチェック
        if self.get_error_rate() > 5.0:  # 5%以上
            return True, "High error rate"

        # レスポンスタイムのチェック
        if self.get_avg_response_time() > 1000:  # 1秒以上
            return True, "Slow response time"

        # ビジネスメトリクスのチェック
        if self.get_conversion_rate() < self.baseline * 0.9:  # 10%以上低下
            return True, "Low conversion rate"

        return False, None
```

**移行条件:**

- [ ] ロールバック手順を準備した
- [ ] 判断基準を定義した
- [ ] 実際にテストした

## 判断のポイント

### いつ移行すべきか

**移行すべき:**
- セキュリティリスク
- サポート終了
- パフォーマンス問題
- 保守困難

**様子見:**
- 安定稼働中
- 移行コスト高
- 代替手段あり

### 移行戦略の選択

**Big Bang:**
- 小規模
- 変更大
- 期限厳守

**Strangler Fig:**
- 大規模
- 段階的
- リスク回避

## よくある落とし穴

1. **不十分なテスト**
   - ❌ 本番で初めて発見
   - ✅ 徹底的な事前テスト

2. **ロールバック計画なし**
   - ❌ 失敗時に慌てる
   - ✅ 事前に手順確立

3. **データ移行の軽視**
   - ❌ データ不整合
   - ✅ 検証プロセス

4. **コミュニケーション不足**
   - ❌ 関係者が知らない
   - ✅ 定期的な報告

5. **段階的移行の怠慢**
   - ❌ 一気に全切り替え
   - ✅ カナリアリリース

## 検証ポイント

### 計画段階

- [ ] 移行計画書を作成した
- [ ] リスクを評価した
- [ ] タイムラインを策定した
- [ ] ロールバック計画を準備した

### 実装段階

- [ ] 段階的に移行した
- [ ] テストを実施した
- [ ] データ整合性を確認した
- [ ] パフォーマンスを検証した

### 本番移行

- [ ] 監視を強化した
- [ ] ロールバック準備完了
- [ ] 関係者に通知した
- [ ] 段階的にリリースした

## 他スキルとの連携

### migration-assistant + database-design

DB移行:
1. database-designで新スキーマ設計
2. migration-assistantで移行計画
3. データ移行実施

### migration-assistant + test-automation

テスト戦略:
1. test-automationでテスト実装
2. migration-assistantで移行実施
3. 継続的な検証

### migration-assistant + dependency-management

依存関係更新:
1. dependency-managementで更新検出
2. migration-assistantで影響分析
3. 段階的な更新

## マイグレーションのベストプラクティス

### 段階的アプローチ

- 小さく始める
- 継続的な検証
- 早期フィードバック

### コミュニケーション

- 定期的な報告
- リスクの共有
- 成功の祝福

### 自動化

- テスト自動化
- デプロイ自動化
- ロールバック自動化

### ドキュメント

- 移行計画書
- 手順書
- トラブルシューティング
