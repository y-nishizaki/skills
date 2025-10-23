---
name: aws-terraform
description: Terraformを使用してマルチクラウド対応のInfrastructure as Codeを実装し、state管理、モジュール、workspaceでインフラをバージョン管理する方法
---

# Terraform (AWS) スキル

## 概要

TerraformはHashiCorpが開発したオープンソースのIaCツールで、マルチクラウド対応が特徴です。HCL（HashiCorp Configuration Language）で宣言的にインフラを定義し、plan/applyで安全に変更を適用します。

## 主な使用ケース

### 1. 基本的なVPC構成

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "production/vpc.tfstate"
    region = "ap-northeast-1"
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "production-vpc"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}
```

### 2. 変数とアウトプット

```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}
```

### 3. モジュール

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "this" {
  cidr_block = var.cidr_block
  # ...
}

# ルートモジュール
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  name       = "production-vpc"
}
```

### 4. Terraform実行

```bash
# 初期化
terraform init

# プラン（変更プレビュー）
terraform plan -out=tfplan

# 適用
terraform apply tfplan

# 状態確認
terraform show

# 特定リソースの出力
terraform output vpc_id

# 削除
terraform destroy
```

### 5. Workspace（環境分離）

```bash
# 新規workspace作成
terraform workspace new production
terraform workspace new staging

# workspace切り替え
terraform workspace select production

# 現在のworkspace確認
terraform workspace show

# workspace一覧
terraform workspace list
```

### 6. State管理（S3バックエンド）

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "production/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

```bash
# DynamoDBテーブル作成（ステートロック用）
aws dynamodb create-table \
    --table-name terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## ベストプラクティス（2025年版）

### 1. リモートステート参照

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "terraform-state-bucket"
    key    = "network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.network.outputs.private_subnet_ids[0]
  # ...
}
```

### 2. Data Sourcesの活用

```hcl
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"
}
```

### 3. Count vs For_Each

```hcl
# For_Eachが推奨（削除時に安全）
resource "aws_subnet" "private" {
  for_each = toset(var.private_subnet_cidrs)

  vpc_id     = aws_vpc.main.id
  cidr_block = each.value

  tags = {
    Name = "private-subnet-${each.key}"
  }
}
```

## リソース

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
