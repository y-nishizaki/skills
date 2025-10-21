---
name: "API設計"
description: "RESTful API設計とGraphQL設計。API、エンドポイント、REST、GraphQL、API設計に関する依頼に対応"
---

# API設計: APIアーキテクチャと設計の思考プロセス

## このスキルを使う場面

- 新規API の設計
- 既存APIのリファクタリング
- API仕様書の作成
- RESTful API の設計
- GraphQL スキーマ設計
- APIバージョニング戦略
- レート制限・認証の設計

## 思考プロセス

### フェーズ1: API要件の定義

**ステップ1: 目的とスコープの明確化**

APIの役割を理解する:

**API の目的:**

- [ ] 誰が使うか（クライアントアプリ、サードパーティ等）
- [ ] 何を提供するか（データ、機能）
- [ ] どのように使われるか（使用パターン）

**機能要件:**

- [ ] 必要なリソース・エンドポイント
- [ ] CRUD操作の必要性
- [ ] 検索・フィルタリング・ソート
- [ ] ページネーション
- [ ] 一括操作

**非機能要件:**

- [ ] パフォーマンス要件
- [ ] スケーラビリティ
- [ ] セキュリティ要件
- [ ] 可用性
- [ ] 後方互換性

**ステップ2: REST vs GraphQL の選択**

**REST API を選ぶ場合:**

- シンプルなCRUD操作
- キャッシュしやすい
- 標準的なHTTPメソッド
- 段階的な学習曲線

**GraphQL を選ぶ場合:**

- 複雑なデータ取得
- クライアントごとに異なるデータ要求
- Over-fetching/Under-fetching の回避
- リアルタイム更新（Subscription）

**移行条件:**

- [ ] API の目的を明確にした
- [ ] APIスタイルを選択した
- [ ] 主要なリソースを特定した

### フェーズ2: RESTful API 設計

**ステップ1: リソース設計**

リソース指向のURL設計:

**基本原則:**

```
# 良い例: 名詞の複数形
GET    /api/users
GET    /api/users/123
POST   /api/users
PUT    /api/users/123
DELETE /api/users/123

# 悪い例: 動詞を使用
GET    /api/getUser?id=123
POST   /api/createUser
POST   /api/deleteUser
```

**ネストされたリソース:**

```
# ユーザーの注文
GET    /api/users/123/orders
GET    /api/users/123/orders/456

# 浅いネスト（推奨: 2階層まで）
GET    /api/orders?user_id=123

# 深すぎるネスト（避ける）
GET    /api/users/123/orders/456/items/789
```

**ステップ2: HTTPメソッドとステータスコード**

適切な使用:

```
# HTTPメソッド
GET    /api/users       # 一覧取得（冪等）
POST   /api/users       # 新規作成（非冪等）
GET    /api/users/123   # 詳細取得（冪等）
PUT    /api/users/123   # 全体更新（冪等）
PATCH  /api/users/123   # 部分更新（非冪等）
DELETE /api/users/123   # 削除（冪等）

# ステータスコード
200 OK                  # 成功
201 Created             # 作成成功
204 No Content          # 成功（レスポンスボディなし）
400 Bad Request         # クライアントエラー
401 Unauthorized        # 認証エラー
403 Forbidden           # 認可エラー
404 Not Found           # リソースなし
409 Conflict            # 競合
422 Unprocessable Entity # バリデーションエラー
429 Too Many Requests   # レート制限
500 Internal Server Error # サーバーエラー
```

**ステップ3: リクエスト・レスポンス設計**

一貫性のあるフォーマット:

```json
// GET /api/users/123
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T15:45:00Z"
}

// POST /api/users
// Request
{
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "password": "SecurePass123"
}

// Response (201 Created)
{
  "id": 124,
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "created_at": "2025-01-21T09:00:00Z"
}

// エラーレスポンス
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ]
  }
}
```

**ステップ4: クエリパラメータ**

検索・フィルタリング・ソート・ページネーション:

```
# フィルタリング
GET /api/users?status=active&role=admin

# ソート
GET /api/users?sort=created_at&order=desc
GET /api/users?sort=-created_at  # マイナスで降順

# ページネーション（オフセットベース）
GET /api/users?page=2&limit=20

# ページネーション（カーソルベース）
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=20

# フィールド選択
GET /api/users?fields=id,name,email

# 検索
GET /api/users?q=john&search_fields=name,email
```

**移行条件:**

- [ ] リソースを設計した
- [ ] エンドポイントを定義した
- [ ] リクエスト・レスポンス形式を決定した

### フェーズ3: 認証と認可

**ステップ1: 認証方式の選択**

**API Key:**

```
GET /api/users
X-API-Key: your-api-key-here
```

**Bearer Token (JWT):**

```
GET /api/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**OAuth 2.0:**

```
# アクセストークン取得
POST /oauth/token
{
  "grant_type": "client_credentials",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}

# API呼び出し
GET /api/users
Authorization: Bearer <access_token>
```

**ステップ2: 認可の実装**

```json
// ロールベースアクセス制御（RBAC）
{
  "roles": ["admin", "user"],
  "permissions": ["users:read", "users:write", "orders:read"]
}

// エンドポイントの権限
GET    /api/users       # 認証不要（public）
POST   /api/users       # 認証不要（登録）
GET    /api/users/123   # 認証必要（本人 or 管理者）
PUT    /api/users/123   # 認証必要（本人 or 管理者）
DELETE /api/users/123   # 管理者のみ
```

**移行条件:**

- [ ] 認証方式を選択した
- [ ] 認可ロジックを設計した
- [ ] セキュリティを確保した

### フェーズ4: バージョニングとドキュメント

**ステップ1: バージョニング戦略**

**URL バージョニング（推奨）:**

```
GET /api/v1/users
GET /api/v2/users
```

**ヘッダーバージョニング:**

```
GET /api/users
Accept: application/vnd.myapi.v1+json
```

**クエリパラメータバージョニング:**

```
GET /api/users?version=1
```

**ステップ2: API ドキュメント**

OpenAPI (Swagger) 仕様:

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
  description: API for user management

servers:
  - url: https://api.example.com/v1

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        email:
          type: string
          format: email
        name:
          type: string
        created_at:
          type: string
          format: date-time

    UserCreate:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          format: password

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
```

**移行条件:**

- [ ] バージョニング戦略を決定した
- [ ] API ドキュメントを作成した
- [ ] 変更管理プロセスを確立した

### フェーズ5: パフォーマンスと最適化

**ステップ1: レート制限**

```
# レスポンスヘッダー
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642780800

# レート制限超過
HTTP/1.1 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 1 hour."
  }
}
```

**ステップ2: キャッシング**

```
# Cache-Control ヘッダー
GET /api/users/123
Cache-Control: public, max-age=3600

# ETag
GET /api/users/123
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# 条件付きリクエスト
GET /api/users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# レスポンス
HTTP/1.1 304 Not Modified
```

**ステップ3: ページネーション**

```json
// オフセットベース
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "first": "/api/users?page=1&limit=20",
    "prev": "/api/users?page=1&limit=20",
    "next": "/api/users?page=3&limit=20",
    "last": "/api/users?page=8&limit=20"
  }
}

// カーソルベース（大規模データに適している）
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzfQ",
    "has_more": true
  }
}
```

**移行条件:**

- [ ] レート制限を実装した
- [ ] キャッシング戦略を決定した
- [ ] ページネーションを実装した

### フェーズ6: GraphQL 設計（該当する場合）

**ステップ1: スキーマ設計**

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  post(id: ID!): Post
  posts(authorId: ID, limit: Int): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
}

input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

input UpdateUserInput {
  email: String
  name: String
}

input CreatePostInput {
  title: String!
  content: String!
  authorId: ID!
}
```

**ステップ2: クエリ例**

```graphql
# 単一ユーザー取得
query {
  user(id: "123") {
    id
    name
    email
  }
}

# ネストされたデータ取得
query {
  user(id: "123") {
    id
    name
    posts {
      id
      title
      comments {
        id
        text
        author {
          name
        }
      }
    }
  }
}

# ミューテーション
mutation {
  createUser(input: {
    email: "user@example.com"
    name: "John Doe"
    password: "SecurePass123"
  }) {
    id
    email
    name
  }
}
```

**移行条件:**

- [ ] GraphQL スキーマを設計した
- [ ] リゾルバを実装した
- [ ] N+1問題に対処した

## 判断のポイント

### REST vs GraphQL

**REST を選ぶ:**

- シンプルなCRUD
- キャッシュ重視
- HTTP標準に準拠
- 学習コスト低

**GraphQL を選ぶ:**

- 柔軟なデータ取得
- クライアント主導
- リアルタイム更新
- モバイルアプリ

### 同期 vs 非同期

**同期API（REST）:**

- 即座にレスポンス
- シンプルな処理
- リアルタイム性

**非同期API（ジョブキュー）:**

- 時間のかかる処理
- バックグラウンド実行
- スケーラビリティ

```json
// 非同期パターン
POST /api/reports
{
  "type": "user_activity",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}

// Response (202 Accepted)
{
  "job_id": "abc123",
  "status": "processing",
  "status_url": "/api/jobs/abc123"
}

// ステータス確認
GET /api/jobs/abc123
{
  "job_id": "abc123",
  "status": "completed",
  "result_url": "/api/reports/abc123/download"
}
```

## よくある落とし穴

1. **動詞の使用**
   - ❌ /api/getUsers
   - ✅ GET /api/users

2. **深いネスト**
   - ❌ /api/users/1/posts/2/comments/3
   - ✅ /api/comments/3

3. **不適切なHTTPメソッド**
   - ❌ POST /api/users/delete
   - ✅ DELETE /api/users/123

4. **エラーハンドリング不足**
   - ❌ 常に200を返す
   - ✅ 適切なステータスコード

5. **バージョニングなし**
   - ❌ 破壊的変更
   - ✅ /api/v1, /api/v2

6. **ドキュメント不足**
   - ❌ コードのみ
   - ✅ OpenAPI仕様

## 検証ポイント

### 設計段階

- [ ] リソースを特定した
- [ ] エンドポイントを設計した
- [ ] 認証・認可を定義した
- [ ] バージョニング戦略を決定した

### 実装段階

- [ ] OpenAPI仕様を作成した
- [ ] エラーハンドリングを実装した
- [ ] レート制限を実装した
- [ ] テストを作成した

### 公開前

- [ ] ドキュメントを整備した
- [ ] セキュリティレビューを実施した
- [ ] パフォーマンステストを実施した
- [ ] 後方互換性を確認した

## 他スキルとの連携

### api-design → database-design

APIとDB の整合:

1. api-designでエンドポイント設計
2. database-designでスキーマ設計
3. 効率的なデータアクセス

### api-design + security-audit

APIセキュリティ:

1. api-designでエンドポイント設計
2. security-auditで脆弱性チェック
3. 認証・認可の強化

### api-design → documentation

API ドキュメント:

1. api-designで仕様決定
2. documentationでドキュメント作成
3. OpenAPI仕様書

## API設計のベストプラクティス

### 一貫性

- 命名規則の統一
- エラー形式の統一
- レスポンス構造の統一

### セキュリティ

- HTTPS 必須
- 認証・認可
- レート制限
- 入力検証

### パフォーマンス

- ページネーション
- フィールド選択
- キャッシング
- 圧縮（gzip）

### 開発者体験

- 明確なドキュメント
- サンプルコード
- エラーメッセージ
- SDKの提供
