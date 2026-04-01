terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  credentials = file("gcp-key.json")
  project     = "suara-pipeline" # <--- REPLACE THIS
  region      = "asia-southeast1"
}

# 1. Cloud Storage Bucket (Data Lake)
resource "google_storage_bucket" "audio_lake" {
  name          = "suara-lake-ananur" # <--- MUST BE GLOBALLY UNIQUE
  location      = "ASIA-SOUTHEAST1"
  force_destroy = true
  
  public_access_prevention = "enforced"
}

# 2. BigQuery Dataset (Data Warehouse)
resource "google_bigquery_dataset" "speech_dataset" {
  dataset_id = "suara_sea"
  location   = "asia-southeast1"
}

# 3. Output for Bruin configuration
output "project_id" {
  value = "suara-pipeline"
}