variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "raw_bucket_name" {
  description = "Raw bucket for IoT events"
  type        = string
}

variable "raw_dataset_id" {
  description = "BigQuery raw dataset"
  type        = string
  default     = "raw_iot_energy"
}

variable "analytics_dataset_id" {
  description = "BigQuery analytics dataset"
  type        = string
  default     = "analytics_iot_energy"
}

variable "artifact_registry_repository_id" {
  description = "Artifact Registry repository id for ingestion images"
  type        = string
  default     = "iot-platform"
}

variable "ingestion_job_name" {
  description = "Cloud Run Job name for ingestion"
  type        = string
  default     = "iot-energy-ingestion-job"
}

variable "ingestion_image" {
  description = "Container image URI for the Cloud Run Job"
  type        = string
}

variable "composer_environment_name" {
  description = "Cloud Composer environment name"
  type        = string
  default     = "iot-energy-composer"
}

variable "composer_environment_size" {
  description = "Cloud Composer environment size"
  type        = string
  default     = "ENVIRONMENT_SIZE_SMALL"
}

variable "composer_image_version" {
  description = "Cloud Composer image version"
  type        = string
  default     = "composer-2-airflow-2.10.5"
}

variable "dbt_target_name" {
  description = "dbt target configured in profiles.yml"
  type        = string
  default     = "dev"
}
