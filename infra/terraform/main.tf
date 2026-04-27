provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  common_env = {
    GCP_PROJECT_ID       = var.project_id
    GCP_REGION           = var.region
    BQ_DATASET_RAW       = var.raw_dataset_id
    BQ_DATASET_ANALYTICS = var.analytics_dataset_id
    GCS_RAW_BUCKET       = var.raw_bucket_name
  }
}

resource "google_project_service" "required_apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "composer.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com"
  ])

  project = var.project_id
  service = each.key
}

resource "google_storage_bucket" "raw_iot_energy" {
  name                        = var.raw_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }

    condition {
      age = 90
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_bigquery_dataset" "raw" {
  dataset_id  = var.raw_dataset_id
  location    = var.region
  description = "Raw dataset for IoT energy events"

  depends_on = [google_project_service.required_apis]
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id  = var.analytics_dataset_id
  location    = var.region
  description = "Analytics dataset for dbt models"

  depends_on = [google_project_service.required_apis]
}

resource "google_artifact_registry_repository" "ingestion" {
  location      = var.region
  repository_id = var.artifact_registry_repository_id
  description   = "Repository for ingestion images"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

resource "google_service_account" "cloud_run_ingestion" {
  account_id   = "sa-iot-ingestion-job"
  display_name = "Service account for IoT ingestion Cloud Run Job"
}

resource "google_service_account" "composer" {
  account_id   = "sa-iot-composer"
  display_name = "Service account for Cloud Composer"
}

resource "google_project_iam_member" "ingestion_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_ingestion.email}"
}

resource "google_project_iam_member" "ingestion_bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_run_ingestion.email}"
}

resource "google_project_iam_member" "ingestion_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cloud_run_ingestion.email}"
}

resource "google_project_iam_member" "ingestion_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloud_run_ingestion.email}"
}

resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

resource "google_project_iam_member" "composer_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

resource "google_project_iam_member" "composer_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

resource "google_project_iam_member" "composer_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.composer.email}"
}

resource "google_cloud_run_v2_job" "iot_ingestion" {
  name     = var.ingestion_job_name
  location = var.region

  template {
    template {
      service_account = google_service_account.cloud_run_ingestion.email
      timeout         = "1200s"

      containers {
        image = var.ingestion_image

        env {
          name  = "GCP_PROJECT_ID"
          value = local.common_env.GCP_PROJECT_ID
        }
        env {
          name  = "GCP_REGION"
          value = local.common_env.GCP_REGION
        }
        env {
          name  = "BQ_DATASET_RAW"
          value = local.common_env.BQ_DATASET_RAW
        }
        env {
          name  = "BQ_DATASET_ANALYTICS"
          value = local.common_env.BQ_DATASET_ANALYTICS
        }
        env {
          name  = "GCS_RAW_BUCKET"
          value = local.common_env.GCS_RAW_BUCKET
        }
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.ingestion_storage_admin,
    google_project_iam_member.ingestion_bigquery_editor,
    google_project_iam_member.ingestion_bigquery_job_user,
    google_project_iam_member.ingestion_logging_writer
  ]
}

resource "google_composer_environment" "iot_platform" {
  name   = var.composer_environment_name
  region = var.region

  config {
    environment_size = var.composer_environment_size

    node_config {
      service_account = google_service_account.composer.email
    }

    software_config {
      image_version = var.composer_image_version

      env_variables = {
        GCP_PROJECT_ID          = var.project_id
        GCP_REGION              = var.region
        DBT_TARGET              = var.dbt_target_name
        INGESTION_CLOUD_RUN_JOB = var.ingestion_job_name
      }

      pypi_packages = {
        "apache-airflow-providers-google" = ">=10.21.0"
        "dbt-bigquery"                    = ">=1.8.0"
        "dbt-core"                        = ">=1.8.0"
      }
    }

    workloads_config {
      scheduler {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }

      web_server {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
      }

      worker {
        cpu        = 1
        memory_gb  = 4
        storage_gb = 10
        min_count  = 1
        max_count  = 2
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.composer_worker,
    google_project_iam_member.composer_run_developer,
    google_project_iam_member.composer_bigquery_job_user,
    google_project_iam_member.composer_bigquery_data_editor
  ]
}
