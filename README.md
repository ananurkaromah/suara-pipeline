# Suara-ID: Indonesian Speech Intelligence Pipeline

Suara-ID is an end-to-end, cloud-native Data Engineering pipeline designed to ingest, process, and transcribe diverse Indonesian regional audio datasets. This project serves as the capstone for the **Data Engineering Zoomcamp 2026**.

## 1. Problem Description

**The Challenge:** Indonesia is an archipelago with over 700 living languages and highly diverse regional accents (e.g., Batak, Melayu, Sunda, Jawa, Papua). Training inclusive Machine Learning models requires massive amounts of clean, labeled, and transcribed audio data that captures these nuances. However, raw `.wav` files are heavy, unstructured, and fundamentally incompatible with traditional relational data warehouses, making downstream AI ingestion incredibly difficult.

**The Solution:** Suara-ID solves this by decoupling storage and compute. It automates the batch ingestion of large, multi-ethnic audio datasets (10GB+) into a highly scalable Data Lake (GCS). It then orchestrates a metadata extraction layer into a Data Warehouse (BigQuery) and uses a Python-based intelligence layer (Hugging Face Faster-Whisper) to automatically transcribe the audio. The final output is a structured, queryable dataset ready for Analytics and ML Engineers.

Here is the complete map of the `suara-pipeline` repository.

```jsx
suara-pipeline/
├── .bruin.yml                          #Global Orchestrator Config
├── .gitignore                          #Git rules
├── [README.md](http://readme.md/)                     #project documentation
├── [main.py](http://main.py/)
├── pyproject.toml                      #Python package definitions
├── uv.lock                             #Locked Python dependency versions
│
├── assets/                             #The Bruin DAG
│   ├── 1_ingestion/                    # Raw Data Landing
│   │   └── raw_source.py
│   ├── 2_staging/                      # Cleaning & Modeling
│   │   └── stg_audio_metadata.sql
│   └── 3_intelligence/
│       └── [transcriber.py](http://transcriber.py/)
│
├── docker/                            #Container Architecture
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── terraform/                        #Infrastructure as Code
│   ├── [main.tf](http://main.tf/)
│   ├── gcp-key.json                  #(Ignored by *.json) SUPER IMPORTANT!
│   └── terraform.tfstate             #(Usually ignored, tracks cloud state)*
└── kaggle.json                       #(Ignored by *.json) Kaggle API Key
```

## 2. Cloud & Infrastructure as Code (IaC)

This project is fully developed in the cloud utilizing **Google Cloud Platform (GCP)**.

- **IaC Tool:** Terraform is used to programmatically provision the necessary cloud infrastructure, ensuring a reproducible environment.
- **Storage (Data Lake):** Google Cloud Storage (GCS) houses the unstructured `.wav` files.
- **Compute (Data Warehouse):** Google BigQuery houses the structured metadata and final transcriptions.
- **Region:** All infrastructure is deployed in `asia-southeast1` (Jakarta/Singapore) for low-latency regional processing.

## 3. Data Ingestion (Batch)

The pipeline implements a robust **Batch Ingestion** strategy:

1. **Source:** The [Indonesian Speech with Accents dataset](https://www.kaggle.com/datasets/hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups) is pulled via the Kaggle API.
2. **Data Lake Upload:** The raw audio files are batch-uploaded directly to the GCS bucket (`suara-lake-ananur`).
3. **Warehouse Ingestion:** A Python Bruin asset dynamically reads the GCS bucket and materializes the file metadata (names, IDs) into the BigQuery `raw_source` table.

## 4. Data Warehouse (Partitioning & Clustering)

The data is housed in **Google BigQuery** and optimized for cost and query speed.

- **Partitioning:** The `stg_audio_metadata` table is partitioned by `DATE(processed_at)`.
    - *Explanation:* Downstream ML models or analytics queries usually request data ingested within specific timeframes (e.g., "new audio from the last 7 days"). Partitioning limits the data scanned, drastically reducing BigQuery costs.
- **Clustering:** The table is clustered by `audio_file_name`.
    - *Explanation:* Analysts frequently query specific files to spot-check transcription accuracy across different ethnic accents. Clustering by filename ensures rapid, indexed lookups for individual records.

## 5. Transformations

Data transformations and orchestration are handled natively by **Bruin**, which acts as a modern alternative to dbt, seamlessly mixing SQL and Python DAGs with built-in data quality checks.

- **Staging (SQL):** Enforces data quality checks (Not Null, Unique) and adds temporal metadata (`processed_at`) to the raw ingestion list.
- **Intelligence Layer (Python):** Transforms the data by downloading the physical files from GCS to a temporary local volume, passing them through a Hugging Face `faster-whisper` (tiny, int8 quantization) model optimized for the Indonesian language (`id`), and appending the AI-generated `transcript`, `language_detected`, and `language_probability` directly into the final BigQuery presentation table.

## 6. Dashboard & Visualization

The final presentation layer is built using **Looker Studio**, connected directly to the BigQuery `transcriptions` table.

- **Categorical Graph:** A Pie Chart visualizing the distribution of the `language_detected` verifying the AI's confidence in classifying the diverse regional accents as Indonesian (`id`).
- **Temporal Graph:** A Time Series Line Chart mapping the `Total Files Transcribed` against the `processed_at` timestamp, showing the batch ingestion volume over time.

---

## 7. Setup Instructions

Follow these instructions to replicate the entire pipeline on any local machine (Windows/WSL, Mac, or Linux).

### Prerequisites

1. **Docker and Docker Compose** installed and running.
2. A Google Cloud Platform (GCP) account.
3. A Kaggle account.

### Step 1: Clone the Repository & Add Credentials

```bash
git clone [<https://github.com/ananurkaromah/suara-pipeline.git>](<https://github.com/ananurkaromah/suara-pipeline.git>)
cd suara-pipeline
```

- **Kaggle API:** Download your `kaggle.json` from your Kaggle account settings and place it in the root `suara-pipeline/` directory.
- **GCP Service Account:** Create a Service Account in GCP with `Storage Admin` and `BigQuery Admin` roles. Download the JSON key, rename it exactly to `gcp-key.json`, and place it inside the `suara-pipeline/terraform/` directory.

### Step 2: Provision Cloud Infrastructure (Terraform)

Open your terminal and run Terraform to create your GCS bucket (Data Lake) and BigQuery dataset (Data Warehouse).
*(Note: Ensure you update* [main.tf](https://github.com/ananurkaromah/suara-pipeline/blob/main/terraform/main.tf) *with your specific GCP Project ID and a globally unique GCS bucket name before running).*

Bash

```jsx
cd terraform
terraform init
terraform apply
cd ..
```

### Step 3: Start the Docker Environment

The project relies on Docker to ensure a perfectly reproducible environment without polluting your local machine.

- [Dockerfile](https://github.com/ananurkaromah/suara-pipeline/blob/main/docker/Dockerfile)**:** Handles the OS-level installations, sets up the `uv` package manager, and installs heavy data/AI dependencies (`faster-whisper`, `pandas`, `google-cloud-storage`).
- [docker-compose.yml](https://github.com/ananurkaromah/suara-pipeline/blob/main/docker/docker-compose.yml)**:** Mounts your local project directory into the container so you can edit code live, and manages the lifecycle of the `suara-worker` environment.

Spin up the containerized environment and jump inside:

Bash

```jsx
docker-compose up -d --build
docker exec -it suara-worker bash
```

*(All following commands must be executed inside this `root@...:/app#` Docker terminal).*

### Step 4: Data Lake Batch Ingestion (Kaggle to GCS)

Execute the batch download and upload to your Google Cloud Storage bucket:

Bash

```jsx
# 1. Configure Kaggle Credentials inside the container
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 2. Download and Extract the Dataset
uvx kaggle datasets download -d hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups
apt-get update && apt-get install -y unzip
unzip indonesian-speech-with-accents-5-ethnic-groups.zip -d raw_audio/

# 3. Authenticate the container with Google Cloud
gcloud auth activate-service-account --key-file=./terraform/gcp-key.json

# 4. Upload Audio to Data Lake (Replace YOUR_BUCKET_NAME with your exact bucket)
gcloud storage cp -r raw_audio/* gs://YOUR_BUCKET_NAME/
```

### Step 5: Execute the Pipeline (Bruin)

Bruin acts as our orchestrator and data transformer. Before running, ensure your [.bruin.yml](https://github.com/ananurkaromah/suara-pipeline/blob/main/.bruin.yml) file is configured with your correct GCP project ID and region (e.g., `asia-southeast1`).

The pipeline is structured as a Directed Acyclic Graph (DAG) across three assets in the `/assets` folder:

1. **`1_ingestion/`**[raw_source.py](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/1_ingestion/raw_source.py) **:** A Python asset that connects to GCS, dynamically lists the physical `.wav` files, and materializes that metadata into BigQuery.
2. **`2_staging/`**[stg_audio_metadata.sql](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/2_staging/stg_audio_metadata.sql)**:** A SQL asset that applies data quality constraints (Unique/Not Null), adds processing timestamps, and builds a **Partitioned and Clustered** BigQuery table.
3. **`3_intelligence/`**[transcriber.py](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/3_intelligence/transcriber.py)**:** A Python asset that downloads the audio, runs the Hugging Face AI model for transcription, and writes the final text and language probabilities back to BigQuery.

Trigger the entire DAG with a single command:

Bash

```jsx
bruin run .
```

If successful, Bruin will output green success checks for the pipeline assets and all data quality constraints. The final transcribed dataset will be available in your BigQuery `transcriptions` table, ready to be attached to Looker Studio for dashboard visualization.
