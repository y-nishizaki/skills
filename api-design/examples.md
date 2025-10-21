# API設計: 実装例とパターン

このドキュメントでは、API設計スキルで説明されている設計パターンの具体例を示します。

## RESTful API 実装例

### Express.js による実装

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// ユーザー一覧
app.get('/api/v1/users', async (req, res) => {
  try {
    const { page = 1, limit = 20, sort = 'created_at', order = 'desc' } = req.query;

    const users = await User.findAll({
      limit: parseInt(limit),
      offset: (parseInt(page) - 1) * parseInt(limit),
      order: [[sort, order]]
    });

    const total = await User.count();

    res.json({
      data: users,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        total_pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An error occurred'
      }
    });
  }
});

// ユーザー作成
app.post('/api/v1/users', async (req, res) => {
  try {
    const { email, name, password } = req.body;

    // バリデーション
    if (!email || !name || !password) {
      return res.status(400).json({
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Missing required fields',
          details: [
            { field: 'email', message: 'Email is required' },
            { field: 'name', message: 'Name is required' },
            { field: 'password', message: 'Password is required' }
          ]
        }
      });
    }

    const user = await User.create({ email, name, password });

    res.status(201).json(user);
  } catch (error) {
    if (error.code === 'ER_DUP_ENTRY') {
      return res.status(409).json({
        error: {
          code: 'CONFLICT',
          message: 'Email already exists'
        }
      });
    }

    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An error occurred'
      }
    });
  }
});
```

## GraphQL スキーマ例

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  posts(limit: Int, offset: Int): [Post!]!
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

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  post(id: ID!): Post
  posts(authorId: ID, limit: Int): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  createPost(input: CreatePostInput!): Post!
}

input CreateUserInput {
  email: String!
  name: String!
  password: String!
}
```

## OpenAPI仕様例

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /api/v1/users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

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
```

詳細なAPI設計プロセスについては、[SKILL.md](SKILL.md) を参照してください。
