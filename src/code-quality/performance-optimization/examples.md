# パフォーマンス最適化: 実装例集

このドキュメントでは、パフォーマンス最適化スキルで説明されている各種最適化手法の具体的な実装例を示します。

## 目次

- [アーキテクチャレベルの最適化](#アーキテクチャレベルの最適化)
- [アルゴリズムレベルの最適化](#アルゴリズムレベルの最適化)
- [コードレベルの最適化](#コードレベルの最適化)

## アーキテクチャレベルの最適化

### 例1: キャッシュの導入

**最適化前（キャッシュなし）:**

```python
def get_user_posts(user_id):
    return database.query("SELECT * FROM posts WHERE user_id = ?", user_id)
```

**最適化後（キャッシュあり）:**

```python
def get_user_posts(user_id):
    cache_key = f"user_posts:{user_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    posts = database.query("SELECT * FROM posts WHERE user_id = ?", user_id)
    cache.set(cache_key, posts, ttl=300)  # 5分間キャッシュ
    return posts
```

**計測すべき指標:**

- キャッシュヒット率
- レスポンスタイムの改善（例: 500ms → 50ms）
- データベース負荷の削減（例: クエリ数 90% 削減）

**注意点:**

- キャッシュの無効化戦略を実装する
- TTL（生存時間）を適切に設定する
- メモリ使用量とのトレードオフを考慮する

### 例2: 非同期処理

**最適化前（同期処理）:**

```python
def create_order(order_data):
    order = save_order(order_data)
    send_confirmation_email(order)  # 遅い（数秒）
    update_inventory(order)  # 遅い（数秒）
    return order
```

**問題点:**

- メール送信とインベントリ更新を待つ必要がある
- レスポンスタイムが長い（5秒以上）
- スループットが低い

**最適化後（非同期処理）:**

```python
def create_order(order_data):
    order = save_order(order_data)
    # 非同期タスクとして実行
    async_task.send_confirmation_email.delay(order.id)
    async_task.update_inventory.delay(order.id)
    return order
```

**計測結果の例:**

- レスポンスタイム: 5秒 → 0.5秒（10倍改善）
- スループット: 10 req/s → 100 req/s（10倍改善）

## アルゴリズムレベルの最適化

### 例3: 重複検出のアルゴリズム改善

**最適化前（O(n²) - 二重ループ）:**

```python
def find_duplicates(items):
    duplicates = []
    for i, item1 in enumerate(items):
        for j, item2 in enumerate(items):
            if i != j and item1 == item2:
                duplicates.append(item1)
    return duplicates
```

**問題点:**

- 時間計算量: O(n²)
- 10,000件のデータで約1億回の比較
- 実行時間: 数秒〜数分

**最適化後（O(n) - セットを使用）:**

```python
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**計測結果の例:**

- 時間計算量: O(n²) → O(n)
- 10,000件のデータ: 5秒 → 0.01秒（500倍改善）
- 100,000件のデータ: 500秒 → 0.1秒（5000倍改善）

### 例4: データ構造の変更

**最適化前（リスト - 線形探索 O(n)）:**

```python
user_ids = [1, 2, 3, 4, 5, ...]  # 10,000個

if user_id in user_ids:  # O(n) - 遅い
    allow_access()
```

**問題点:**

- リストの検索は線形時間 O(n)
- 10,000件のリストで最悪10,000回の比較
- 実行時間: ミリ秒単位

**最適化後（セット - ハッシュ探索 O(1)）:**

```python
user_ids = {1, 2, 3, 4, 5, ...}  # 10,000個

if user_id in user_ids:  # O(1) - 速い
    allow_access()
```

**計測結果の例:**

- 時間計算量: O(n) → O(1)
- 10,000件の検索: 1ms → 0.001ms（1000倍改善）

## コードレベルの最適化

### 例5: ループ内の不要な計算を排除

**最適化前（毎回計算）:**

```python
def process_users(users):
    results = []
    for user in users:
        # ループ内で毎回計算（不要）
        threshold = calculate_threshold()  # 1ms × 10,000回 = 10秒
        if user.score > threshold:
            results.append(user)
    return results
```

**問題点:**

- `calculate_threshold()` をループ内で毎回実行
- 10,000ユーザーで10,000回の計算
- 実行時間: 約10秒

**最適化後（一度だけ計算）:**

```python
def process_users(users):
    results = []
    threshold = calculate_threshold()  # 一度だけ計算: 1ms
    for user in users:
        if user.score > threshold:
            results.append(user)
    return results
```

**計測結果:**

- 実行時間: 10秒 → 0.01秒（1000倍改善）

### 例6: リスト内包表記の活用（Python）

**最適化前（通常のループ）:**

```python
result = []
for item in items:
    result.append(item.value * 2)
```

**最適化後（リスト内包表記）:**

```python
result = [item.value * 2 for item in items]
```

**理由:**

- Pythonではリスト内包表記がC言語レベルで最適化されている
- `.append()` の関数呼び出しオーバーヘッドを削減
- 通常、10-30% の速度向上

**計測結果の例:**

- 100,000件の処理: 150ms → 100ms（1.5倍改善）

### 例7: 早期リターンによる無駄な処理の削減

**最適化前（全ユーザーを取得）:**

```python
def find_user(user_id):
    users = get_all_users()  # すべてのユーザーを取得（遅い）
    for user in users:
        if user.id == user_id:
            return user
    return None
```

**問題点:**

- 全ユーザーをデータベースから取得（10,000件）
- メモリを大量に使用
- 実行時間: 数秒

**最適化後（直接検索）:**

```python
def find_user(user_id):
    # 直接データベースで検索（インデックス使用）
    return database.query("SELECT * FROM users WHERE id = ?", user_id)
```

**計測結果:**

- データベースクエリ: 1回（インデックス使用）
- 実行時間: 3秒 → 0.001秒（3000倍改善）
- メモリ使用量: 100MB → 1KB

### 例8: データベースクエリの最適化（N+1問題の解決）

**最適化前（N+1クエリ問題）:**

```python
# 1回目: ユーザー一覧を取得
users = User.query.all()  # 1クエリ

# 2回目以降: 各ユーザーの投稿を取得
for user in users:
    posts = get_posts(user.id)  # N回クエリ（ユーザー数分）
    # 合計: 1 + N クエリ
```

**問題点:**

- 100ユーザーで101回のクエリ
- 各クエリに10msかかる場合、合計1秒以上
- データベース負荷が高い

**最適化後（JOINまたはバッチクエリ）:**

```python
# 方法1: JOIN を使用
posts_by_user = database.query("""
    SELECT users.*, posts.*
    FROM users
    JOIN posts ON posts.user_id = users.id
""")

# 方法2: IN句でバッチ取得
user_ids = [user.id for user in users]
posts_by_user = get_all_posts(user_ids)  # 1クエリ
```

**計測結果:**

- クエリ数: 101回 → 1-2回
- 実行時間: 1秒 → 0.02秒（50倍改善）

## パフォーマンス計測の例

### ベンチマーク実装例（Python）

```python
import time

def benchmark(func, *args, iterations=100):
    """関数のパフォーマンスを計測"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return {
        'average': avg_time,
        'min': min_time,
        'max': max_time,
        'total': sum(times)
    }

# 使用例
result = benchmark(find_duplicates, large_list, iterations=100)
print(f"平均: {result['average']*1000:.2f}ms")
print(f"最小: {result['min']*1000:.2f}ms")
print(f"最大: {result['max']*1000:.2f}ms")
```

### プロファイリング例（Python cProfile）

```python
import cProfile
import pstats

def profile_function(func, *args):
    """関数をプロファイリング"""
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 上位10個を表示

    return result
```

## まとめ

各最適化手法の選択ガイド:

| 最適化レベル | 効果 | 実装難易度 | 適用タイミング |
|------------|------|----------|--------------|
| アーキテクチャ | 大（10-100倍） | 高 | 設計時 |
| アルゴリズム | 大（10-1000倍） | 中 | ボトルネック特定後 |
| コード | 小-中（1.5-10倍） | 低 | 実装時・リファクタリング時 |

**重要な原則:**

1. **計測が先、最適化は後** - 推測で最適化しない
2. **80/20の法則** - 20%のコードが80%の時間を消費
3. **段階的改善** - 一度に一つの最適化を実施・計測
4. **バランス** - 速度 vs 可読性・保守性

詳細な最適化プロセスについては、[SKILL.md](SKILL.md) を参照してください。
