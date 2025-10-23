---
name: "AWS ECS / EKS (コンテナオーケストレーション)"
description: "AWSのコンテナ管理サービス。ECS（Elastic Container Service）、EKS（Elastic Kubernetes Service）、Fargate、コンテナデプロイ、サービス管理、ベストプラクティスに関する思考プロセスを提供"
---

# AWS ECS / EKS (コンテナオーケストレーション)

## このスキルを使う場面

- コンテナ化されたアプリケーションのデプロイ
- マイクロサービスアーキテクチャの構築
- Kubernetesベースのアプリケーション運用
- スケーラブルなコンテナワークロードの管理
- CI/CDパイプラインでのコンテナデプロイ
- サーバーレスコンテナの実行

## サービスの概要

### Amazon ECS（Elastic Container Service）

AWSネイティブのコンテナオーケストレーションサービス。シンプルで管理が容易、AWSサービスとの統合が深い。

**特徴:**
- AWSネイティブ
- シンプルな学習曲線
- 予測可能なパフォーマンス
- 低コスト（EC2起動タイプ）
- Fargateサポート

**使用場面:**
- AWS中心の環境
- シンプルなコンテナデプロイ
- AWSサービスとの緊密な統合
- 迅速な導入

### Amazon EKS（Elastic Kubernetes Service）

マネージドKubernetesサービス。Kubernetes標準に準拠し、マルチクラウド・ハイブリッド環境に対応。

**特徴:**
- Kubernetes標準
- マルチクラウド対応
- 豊富なエコシステム
- 複雑なデプロイメント対応
- Fargateサポート

**使用場面:**
- Kubernetes経験者
- 複雑なデプロイメント
- マルチクラウド戦略
- Kubernetesエコシステムの活用

### AWS Fargate

EC2インスタンスの管理不要なサーバーレスコンテナ実行環境。ECSとEKS両方で使用可能。

**特徴:**
- サーバーレス
- インフラ管理不要
- 自動スケーリング
- セキュリティ分離

**使用場面:**
- インフラ管理を最小化
- 迅速なデプロイ
- 断続的なワークロード
- セキュリティ要件が高い

## 思考プロセス

### フェーズ1: サービスの選択

**ステップ1: ECS vs EKS vs Fargateの判断**

| 要因 | ECS | EKS | Fargate |
|-----|-----|-----|---------|
| 学習曲線 | 低 | 高 | 低 |
| AWSネイティブ | 高 | 中 | 高 |
| コスト | 低 | 中 | 中〜高 |
| 柔軟性 | 中 | 高 | 中 |
| 管理負担 | 中 | 高 | 最小 |

**ECSを選択する場合:**
- [ ] AWSエコシステムに完全依存できる
- [ ] シンプルな管理を優先
- [ ] コスト最適化が重要
- [ ] Kubernetesの複雑さを避けたい

**EKSを選択する場合:**
- [ ] Kubernetes標準が必要
- [ ] 既存のKubernetes資産がある
- [ ] マルチクラウド・ハイブリッド戦略
- [ ] 複雑なデプロイメント要件

**Fargateを選択する場合:**
- [ ] サーバー管理を避けたい
- [ ] 迅速な展開が必要
- [ ] スパイク性のあるワークロード
- [ ] セキュリティ分離が重要

**ステップ2: 起動タイプの選択（ECS/EKS）**

**EC2起動タイプ:**
- より低コスト
- 完全な制御
- カスタマイズ可能
- インスタンス管理が必要

**Fargate起動タイプ:**
- サーバーレス
- 管理不要
- タスクレベルの分離
- やや高コスト

**2025年のハイブリッドアプローチ:**
- EKS：Kubernetes標準アプリ
- ECS：安定したAWSネイティブワークロード
- Fargate：オンデマンド・スパイクタスク

**移行条件:**
- [ ] ECS/EKS/Fargateを選択した
- [ ] 起動タイプを決定した
- [ ] ユースケースに適合することを確認した

### フェーズ2: ECSの構築

**ステップ1: タスク定義の作成**

```json
{
  "family": "web-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [{
    "name": "web",
    "image": "123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/web-app:latest",
    "portMappings": [{
      "containerPort": 80,
      "protocol": "tcp"
    }],
    "environment": [{
      "name": "ENVIRONMENT",
      "value": "production"
    }],
    "secrets": [{
      "name": "DB_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-password"
    }],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/web-app",
        "awslogs-region": "ap-northeast-1",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost/ || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3,
      "startPeriod": 60
    }
  }],
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole"
}
```

```bash
# タスク定義の登録
aws ecs register-task-definition \
    --cli-input-json file://task-definition.json
```

**ステップ2: ECSクラスターの作成**

```bash
# Fargateクラスターの作成
aws ecs create-cluster \
    --cluster-name production-cluster \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy \
        capacityProvider=FARGATE,weight=1,base=1 \
        capacityProvider=FARGATE_SPOT,weight=4
```

**ステップ3: サービスの作成**

```bash
# ECSサービスの作成
aws ecs create-service \
    --cluster production-cluster \
    --service-name web-service \
    --task-definition web-app:1 \
    --desired-count 3 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={
      subnets=[subnet-12345,subnet-67890],
      securityGroups=[sg-12345678],
      assignPublicIp=DISABLED
    }" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/web-tg/abc123,containerName=web,containerPort=80" \
    --health-check-grace-period-seconds 60 \
    --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" \
    --enable-execute-command
```

**ステップ4: Auto Scalingの設定**

```bash
# Application Auto Scalingの登録
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/production-cluster/web-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 3 \
    --max-capacity 10

# Target Trackingポリシーの作成
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/production-cluster/web-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
      },
      "ScaleInCooldown": 300,
      "ScaleOutCooldown": 60
    }'
```

**移行条件:**
- [ ] タスク定義を作成した
- [ ] ECSクラスターを作成した
- [ ] サービスをデプロイした
- [ ] Auto Scalingを設定した

### フェーズ3: EKSの構築

**ステップ1: EKSクラスターの作成**

```bash
# eksctlを使用（推奨）
eksctl create cluster \
    --name production-cluster \
    --region ap-northeast-1 \
    --version 1.28 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3 \
    --nodes-min 3 \
    --nodes-max 10 \
    --managed \
    --asg-access \
    --external-dns-access \
    --full-ecr-access \
    --alb-ingress-access

# またはAWS CLIを使用
aws eks create-cluster \
    --name production-cluster \
    --role-arn arn:aws:iam::123456789012:role/eks-cluster-role \
    --resources-vpc-config subnetIds=subnet-12345,subnet-67890,securityGroupIds=sg-12345678 \
    --kubernetes-version 1.28
```

**ステップ2: kubeconfigの更新**

```bash
# kubeconfigの更新
aws eks update-kubeconfig \
    --name production-cluster \
    --region ap-northeast-1

# 接続確認
kubectl get nodes
```

**ステップ3: アプリケーションのデプロイ**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/web-app:latest
        ports:
        - containerPort: 80
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

```bash
# デプロイ
kubectl apply -f deployment.yaml

# 状態確認
kubectl get pods -n production
kubectl get svc -n production
```

**ステップ4: Horizontal Pod Autoscaler**

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

```bash
kubectl apply -f hpa.yaml
```

**移行条件:**
- [ ] EKSクラスターを作成した
- [ ] ワーカーノードを追加した
- [ ] アプリケーションをデプロイした
- [ ] HPAを設定した

### フェーズ4: Fargateの活用

**ECS Fargate:**

```bash
# Fargateタスク定義（上記参照）
# requiresCompatibilities: ["FARGATE"]を指定

# Fargateサービスの作成
aws ecs create-service \
    --cluster production-cluster \
    --service-name fargate-service \
    --task-definition web-app:1 \
    --desired-count 3 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={
      subnets=[subnet-private1,subnet-private2],
      securityGroups=[sg-12345678],
      assignPublicIp=DISABLED
    }"
```

**EKS Fargate:**

```yaml
# fargate-profile.yaml
apiVersion: v1
kind: FargateProfile
metadata:
  name: app-profile
spec:
  selectors:
  - namespace: production
    labels:
      compute-type: fargate
  podExecutionRoleArn: arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role
  subnets:
  - subnet-private1
  - subnet-private2
```

```bash
# Fargateプロファイルの作成
aws eks create-fargate-profile \
    --cluster-name production-cluster \
    --fargate-profile-name app-profile \
    --pod-execution-role-arn arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role \
    --selectors namespace=production,labels={compute-type=fargate} \
    --subnets subnet-private1 subnet-private2
```

**移行条件:**
- [ ] Fargate設定を完了した
- [ ] タスク/Podが正常に起動することを確認した
- [ ] コストを評価した

### フェーズ5: CI/CD統合

**ステップ1: ECRリポジトリの作成**

```bash
# ECRリポジトリの作成
aws ecr create-repository \
    --repository-name web-app \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

# イメージのプッシュ
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com

docker build -t web-app .
docker tag web-app:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/web-app:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/web-app:latest
```

**ステップ2: CodePipelineの設定**

```yaml
# buildspec.yml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}
  build:
    commands:
      - echo Build started on `date`
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
      - echo Writing image definitions file...
      - printf '[{"name":"web","imageUri":"%s"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json
artifacts:
  files: imagedefinitions.json
```

**移行条件:**
- [ ] ECRリポジトリを作成した
- [ ] CI/CDパイプラインを構築した
- [ ] 自動デプロイを設定した

## ベストプラクティス

### セキュリティ

**1. タスク/Podロールの使用:**

```bash
# ECS：タスクロール
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}

# EKS：IRSAを使用
eksctl create iamserviceaccount \
    --name my-service-account \
    --namespace production \
    --cluster production-cluster \
    --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
    --approve
```

**2. 最小権限の原則:**

```json
# 必要最小限の権限のみ付与
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::my-bucket/app-data/*"
  }]
}
```

**3. イメージスキャン:**

```bash
# ECRでイメージスキャンを有効化
aws ecr put-image-scanning-configuration \
    --repository-name web-app \
    --image-scanning-configuration scanOnPush=true
```

### パフォーマンス

**1. リソース制限の設定:**

```yaml
# Kubernetes
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**2. ヘルスチェックの実装:**

```json
// ECS
"healthCheck": {
  "command": ["CMD-SHELL", "curl -f http://localhost/health || exit 1"],
  "interval": 30,
  "timeout": 5,
  "retries": 3,
  "startPeriod": 60
}
```

**3. 効率的なイメージの使用:**

```dockerfile
# マルチステージビルド
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

## コスト最適化

**1. Fargate Spotの活用:**

```bash
# Fargate Spotで最大70%削減
--capacity-providers FARGATE FARGATE_SPOT \
--default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=4
```

**2. 適切なサイズ設定:**

```bash
# 過剰なCPU/メモリ割り当てを避ける
# CloudWatchで実際の使用量を監視
```

**3. EC2起動タイプの活用:**

```bash
# 安定したワークロード：EC2起動タイプ（低コスト）
# スパイクワークロード：Fargate（柔軟性）
```

## よくある落とし穴

1. **リソース制限の未設定**
   - ❌ リソース制限なし → ノード全体のリソースを消費
   - ✅ 適切なrequests/limitsを設定

2. **ヘルスチェックの不備**
   - ❌ ヘルスチェックなし → 障害検出遅延
   - ✅ liveness/readiness probeを実装

3. **ログ管理の欠如**
   - ❌ ログを収集しない
   - ✅ CloudWatch Logsまたは集中ログシステム

4. **セキュリティグループの過剰な開放**
   - ❌ 0.0.0.0/0から全ポート開放
   - ✅ 必要最小限のアクセスのみ許可

5. **IAMロールの共有**
   - ❌ 全タスク/Podで同じロール
   - ✅ タスク/Pod単位で適切なロール

## 判断のポイント

### ECS vs EKS

| 要因 | ECS | EKS |
|-----|-----|-----|
| 学習コスト | 低 | 高 |
| AWS統合 | 深い | 標準的 |
| マルチクラウド | 不可 | 可能 |
| エコシステム | 小 | 大 |
| コスト | 低 | 中（コントロールプレーン課金） |

### EC2 vs Fargate

| 要因 | EC2起動タイプ | Fargate |
|-----|-------------|---------|
| コスト | 低（連続稼働） | 中（従量課金） |
| 管理 | 必要 | 不要 |
| 柔軟性 | 高 | 中 |
| 起動速度 | 遅い | 速い |

## 検証ポイント

### 設計

- [ ] 適切なオーケストレーションサービスを選択
- [ ] 起動タイプを決定
- [ ] リソース要件を定義

### デプロイ

- [ ] タスク定義/マニフェストを作成
- [ ] クラスターを構築
- [ ] サービスをデプロイ
- [ ] ヘルスチェックを設定

### スケーリング

- [ ] Auto Scalingを設定
- [ ] スケーリングポリシーをテスト
- [ ] リソース使用率を監視

### セキュリティ

- [ ] IAMロールを適切に設定
- [ ] ネットワーク分離を実装
- [ ] イメージスキャンを有効化

## 他スキルとの連携

### ecs-eks + ecr

コンテナオーケストレーションとレジストリの組み合わせ:

1. ecrでコンテナイメージを管理
2. ecs-eksでデプロイ・実行
3. CI/CDパイプラインを構築

### ecs-eks + alb

コンテナとロードバランサーの組み合わせ:

1. albでトラフィック分散
2. ecs-eksでコンテナ実行
3. 高可用性なサービスを構築

### ecs-eks + cloudwatch

コンテナと監視の組み合わせ:

1. ecs-eksでコンテナ実行
2. cloudwatchでメトリクス・ログ収集
3. 可観測性を確保

## リソース

### 公式ドキュメント

- [Amazon ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AWS Fargate](https://aws.amazon.com/fargate/)

### ツール

- [eksctl](https://eksctl.io/)
- [AWS Copilot CLI](https://aws.github.io/copilot-cli/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### 学習リソース

- [ECS Best Practices Guide](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
