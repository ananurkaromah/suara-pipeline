# Suara-SEA: Southeast Asian Speech Intelligence Pipeline 

Suara-SEA is an end-to-end, cloud-native Data Engineering pipeline designed to ingest, process, and transcribe diverse Southeast Asian audio datasets. This project serves as the capstone for the **Data Engineering Zoomcamp 2026**.

## 1. Problem Description
**The Challenge:** Southeast Asia features highly diverse linguistic accents (e.g., Batak, Melayu, Sunda, Jawa, Papua in Indonesia). Training Machine Learning models requires massive amounts of clean, labeled, and transcribed audio data. However, raw `.wav` files are heavy, unstructured, and incompatible with traditional data warehouses, making downstream AI ingestion incredibly difficult.

**The Solution:** Suara-SEA solves this by decoupling storage and compute. It automates the batch ingestion of large audio datasets (over 20,000 files / 10GB) into a highly scalable Data Lake (GCS). It then orchestrates a metadata extraction layer into a Data Warehouse (BigQuery) and uses a Python-based intelligence layer (Hugging Face Faster-Whisper) to automatically transcribe the audio. The final output is a structured, queryable dataset ready for Analytics and ML Engineers.

## 2. Cloud & Infrastructure as Code (IaC)
This project is fully developed in the cloud utilizing **Google Cloud Platform (GCP)**.
* **IaC Tool:** Terraform is used to programmatically provision the necessary cloud infrastructure, ensuring reproducible and trackable environments.
* **Storage:** Google Cloud Storage (GCS) acts as the Data Lake for unstructured `.wav` files.
* **Compute/Warehouse:** Google BigQuery acts as the structured Data Warehouse.
* **Region:** All infrastructure is deployed in `asia-southeast1` (Singapore/Jakarta) for low-latency regional processing.

## 3. Data Ingestion (Batch)
The pipeline implements a robust **Batch Ingestion** strategy:
1. **Source:** The [Indonesian Speech with Accents dataset](https://www.kaggle.com/datasets/hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups) is pulled via the Kaggle API.
2. **Data Lake Upload:** The raw audio files are batch-uploaded directly to the GCS bucket (`suara-lake-ananur`).
3. **Warehouse Ingestion:** A Python asset dynamically reads the GCS bucket and materializes the file metadata (names, IDs) into the BigQuery `raw_source` table.

## 4. Data Warehouse (Partitioning & Clustering)
The data is housed in **Google BigQuery** (`suara_sea` dataset) and optimized for cost and query speed.
* **Partitioning:** The `stg_audio_metadata` table is partitioned by `DATE(processed_at)`.
  * *Explanation:* Downstream ML models or analytics queries usually request data ingested within specific timeframes (e.g., "new audio from the last 7 days"). Partitioning limits the data scanned, drastically reducing BigQuery costs.
* **Clustering:** The table is clustered by `audio_file_name`.
  * *Explanation:* Analysts frequently query specific files to spot-check transcription accuracy. Clustering by filename ensures rapid, indexed lookups for individual records.

## 5. Transformations
Data transformations and orchestration are handled natively by **Bruin**, which acts as a modern alternative to dbt, seamlessly mixing SQL and Python DAGs.
* **Staging (SQL):** Enforces data quality checks (Not Null, Unique) and adds temporal metadata (`processed_at`) to the raw ingestion list.
* **Intelligence Layer (Python):** Transforms the data by passing the GCS cloud URIs into a Hugging Face `faster-whisper` (tiny, int8 quantization) model, appending the AI-generated `transcript`, `language_detected`, and `language_probability` directly into the final BigQuery presentation table.

## 6. Dashboard & Visualization
The final presentation layer is built using **Looker Studio**, connected directly to the BigQuery `transcriptions` table.
* **Categorical Graph:** A Pie Chart visualizing the distribution of the `language_detected` (e.g., verifying the AI's confidence in classifying the audio as Indonesian (`id`)).
* **Temporal Graph:** A Time Series Line Chart mapping the `Total Files Transcribed` against the `processed_at` timestamp, showing the ingestion volume over time.

## 7. Reproducibility
The project is containerized using Docker, utilizing `uv` for lightning-fast Python dependency management. It can be reproduced on any machine (Windows/WSL, Mac, Linux).

### Setup Instructions

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/suara-pipeline.git](https://github.com/yourusername/suara-pipeline.git)
cd suara-pipeline