output "raw_bucket_name" {
  value = google_storage_bucket.raw_iot_energy.name
}

output "raw_dataset" {
  value = google_bigquery_dataset.raw.dataset_id
}

output "analytics_dataset" {
  value = google_bigquery_dataset.analytics.dataset_id
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.ingestion.repository_id
}

output "cloud_run_job_name" {
  value = google_cloud_run_v2_job.iot_ingestion.name
}

output "composer_environment_name" {
  value = google_composer_environment.iot_platform.name
}

output "composer_service_account" {
  value = google_service_account.composer.email
}
