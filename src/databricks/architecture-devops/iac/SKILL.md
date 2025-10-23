---
name: "Databricks Infrastructure as Code"
description: "Terraformによるインフラ自動化。ワークスペース、クラスター、ジョブ、権限設定の自動プロビジョニング"
---

# Databricks Infrastructure as Code

## Terraform Databricks Provider

### プロバイダー設定

```hcl
# terraform/main.tf
terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}
```

## クラスター定義

```hcl
# terraform/cluster.tf
resource "databricks_cluster" "shared_cluster" {
  cluster_name            = "Shared Analytics Cluster"
  spark_version           = "14.3.x-scala2.12"
  node_type_id            = "i3.xlarge"
  autotermination_minutes = 60
  
  autoscale {
    min_workers = 2
    max_workers = 8
  }
  
  spark_conf = {
    "spark.databricks.delta.preview.enabled" = "true"
    "spark.sql.adaptive.enabled"             = "true"
  }
}
```

## ジョブ定義

```hcl
# terraform/jobs.tf
resource "databricks_job" "etl_pipeline" {
  name = "ETL Pipeline"
  
  task {
    task_key = "extract"
    
    notebook_task {
      notebook_path = "/Repos/Production/etl/extract"
      base_parameters = {
        env = "prod"
      }
    }
    
    existing_cluster_id = databricks_cluster.shared_cluster.id
  }
  
  task {
    task_key = "transform"
    depends_on {
      task_key = "extract"
    }
    
    notebook_task {
      notebook_path = "/Repos/Production/etl/transform"
    }
    
    existing_cluster_id = databricks_cluster.shared_cluster.id
  }
  
  schedule {
    quartz_cron_expression = "0 0 2 * * ?"
    timezone_id            = "Asia/Tokyo"
  }
  
  email_notifications {
    on_failure = ["team@example.com"]
  }
}
```

## Unity Catalog設定

```hcl
# terraform/unity-catalog.tf
resource "databricks_catalog" "sales" {
  name    = "sales"
  comment = "Sales data catalog"
  owner   = "sales_admins"
}

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.sales.name
  name         = "bronze"
  comment      = "Raw data layer"
}

resource "databricks_grants" "schema_grants" {
  schema = "${databricks_catalog.sales.name}.${databricks_schema.bronze.name}"
  
  grant {
    principal  = "sales_engineers"
    privileges = ["ALL_PRIVILEGES"]
  }
  
  grant {
    principal  = "sales_analysts"
    privileges = ["SELECT"]
  }
}
```

## シークレット管理

```hcl
# terraform/secrets.tf
resource "databricks_secret_scope" "app_secrets" {
  name = "app-secrets"
}

resource "databricks_secret" "db_password" {
  scope        = databricks_secret_scope.app_secrets.name
  key          = "db-password"
  string_value = var.db_password
}
```

## ワークスペース管理

```hcl
# terraform/workspace.tf
resource "databricks_directory" "repos" {
  path = "/Repos/Production"
}

resource "databricks_repo" "etl_repo" {
  url    = "https://github.com/org/etl-pipeline"
  branch = "main"
  path   = "/Repos/Production/etl-pipeline"
}
```

## モジュール化

```hcl
# modules/etl-job/main.tf
module "etl_job" {
  source = "./modules/etl-job"
  
  job_name       = "Daily ETL"
  notebook_path  = "/Repos/Production/etl/main"
  cluster_id     = var.cluster_id
  cron_schedule  = "0 0 2 * * ?"
}
```

## 実行

```bash
# 初期化
terraform init

# プラン確認
terraform plan

# 適用
terraform apply

# 削除
terraform destroy
```

## ベストプラクティス

1. **状態管理** - リモートバックエンド (S3, Azure Blob)
2. **モジュール化** - 再利用可能なコンポーネント
3. **変数管理** - 環境別変数ファイル
4. **シークレット** - 外部管理 (Vault, Key Management)
5. **バージョン管理** - Terraform コードを Git 管理

## まとめ

TerraformでDatabricksインフラを宣言的に定義・管理。クラスター、ジョブ、Unity Catalog、権限を自動プロビジョニングし、再現可能で一貫性のある環境を構築。
