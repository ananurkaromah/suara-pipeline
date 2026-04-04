# **Suara-ID: Indonesian Speech Intelligence Pipeline**

Suara-ID is an end-to-end, cloud-native Data Engineering pipeline designed to ingest, process, and transcribe diverse Indonesian regional audio datasets. This project serves as the capstone for the **Data Engineering Zoomcamp 2026**.

## **Problem Description**

**The Challenge:**
Indonesia is an archipelago with over 700 living languages and highly diverse regional accents (e.g., Batak, Melayu, Sunda, Jawa, Papua). Training inclusive Machine Learning models requires massive amounts of clean, labeled, and transcribed audio data that captures these nuances. However, raw `.wav` files are heavy, unstructured, and fundamentally incompatible with traditional relational data warehouses, making downstream AI ingestion incredibly difficult.

**The Solution:**
Suara-ID solves this by decoupling storage and compute. It automates the batch ingestion of large, multi-ethnic audio datasets (10GB+) into a highly scalable Data Lake (GCS). It then orchestrates a metadata extraction layer into a Data Warehouse (BigQuery) and uses a Python-based intelligence layer (Hugging Face Faster-Whisper) to automatically transcribe the audio. The final output is a structured, queryable dataset ready for Analytics and ML Engineers.

Here is the complete directory structure for the `suara-pipeline` repository:

Plaintext

```jsx
suara-pipeline/
├── .bruin.yml              # Global Orchestrator Config
├── .gitignore              # Git rules
├── README.md               # Project documentation
├── main.py
├── pyproject.toml          # Python package definitions
├── uv.lock                 # Locked Python dependency versions
│
├── assets/                 # The Bruin DAG
│   ├── 0_extract/          # Web-to-Lake Extraction
│   │   └── kaggle_to_gcs.py
│   ├── 1_ingestion/        # Raw Data Landing
│   │   └── raw_source.py
│   ├── 2_staging/          # Cleaning & Modeling
│   │   └── stg_audio_metadata.sql
│   └── 3_intelligence/     # AI Transcription Layer
│       └── transcriber.py
│
├── docker/                 # Container Architecture
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── terraform/              # Infrastructure as Code
│   ├── main.tf
│   ├── gcp-key.json        # (Ignored by .gitignore) GCP Auth
│   └── terraform.tfstate   # (Tracks cloud state)
└── .env                    # (Ignored by .gitignore) API keys
```

## **Project Architecture**

The **Suara-ID** pipeline is an automated, end-to-end Data Engineering architecture orchestrated by Bruin. It extracts raw data from Kaggle, loads it into a Google Cloud Data Lake, processes metadata in BigQuery, and utilizes an AI model to generate transcripts, which are finally visualized in a BI Dashboard.

Code snippet

```jsx
flowchart LR
    subgraph External [External Source]
        Kaggle[Kaggle API]
    end

    subgraph Bruin [Bruin Orchestration]
        direction TB
        E[0. Extract]
        I[1. Ingest]
        S[2. Stage]
        T[3. Intelligence]
        E --> I --> S --> T
    end

    subgraph GCP [Google Cloud Platform]
        direction TB
        GCS[(Cloud Storage<br/>Data Lake)]
        BQ_Raw[(BigQuery<br/>Raw Tables)]
        BQ_Stg[(BigQuery<br/>Staging Layer)]
        BQ_Final[(BigQuery<br/>AI Transcripts)]
    end

    subgraph BI [Presentation]
        Looker[Looker Studio]
    end

    %% Data Flow
    Kaggle -->|Download| E
    E -->|Upload .wav files| GCS
    E -.->|Batch Metadata| BQ_Raw
    I -.->|List Blobs| GCS
    I -->|Record Metadata| BQ_Raw
    BQ_Raw -->|SQL Partition/Cluster| BQ_Stg
    BQ_Stg -.->|Fetch Batch IDs| T
    T -->|Faster-Whisper Text| BQ_Final

    %% Presentation Flow
    BQ_Stg ===> Looker
    BQ_Final ===> Looker
```

## **Technology Stack**

- **Data Source:** [Kaggle API](https://www.kaggle.com/datasets/hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups) (Indonesian Ethnic Speech Dataset)
- **Environment:** Docker & Docker Compose
- **Orchestration:** [Bruin](https://www.google.com/search?q=https://bruin.data) (Containerized DAG execution)
- **Data Lake:** Google Cloud Storage (GCS)
- **Data Warehouse:** Google BigQuery
- **Transformations:** Pandas (Python) & BigQuery Standard SQL
- **Machine Learning / AI:** `faster-whisper` (CPU-optimized audio transcription)
- **Business Intelligence:** Google Looker Studio

## **Cloud & Infrastructure as Code (IaC)**

This project is fully developed in the cloud utilizing **Google Cloud Platform (GCP)**.

- **IaC Tool:** Terraform is used to programmatically provision the necessary cloud infrastructure, ensuring a reproducible environment.
- **Storage (Data Lake):** Google Cloud Storage (GCS) houses the unstructured `.wav` files.
- **Compute (Data Warehouse):** Google BigQuery houses the structured metadata and final transcriptions.
- **Region:** All infrastructure is deployed in `asia-southeast1` (Jakarta/Singapore) for low-latency regional processing.

## **Data Ingestion (Batch)**

The pipeline implements a robust **Batch Ingestion** strategy:

1. **Source:** The [Indonesian Speech with Accents dataset](https://www.kaggle.com/datasets/hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups) is pulled via the Kaggle API.
2. **Data Lake Upload:** The raw audio files are batch-uploaded directly to the GCS bucket (`suara-lake-ananur`) using an automated extraction script.
3. **Warehouse Ingestion:** A Python Bruin asset dynamically reads the GCS bucket and materializes the file metadata (names, IDs) into the BigQuery `raw_source` table.

## **Data Warehouse**

The data is housed in **Google BigQuery** and optimized for cost and query speed.

- **Partitioning:** The `stg_audio_metadata` table is partitioned by `DATE(processed_at)`.
    - *Explanation:* Downstream ML models or analytics queries usually request data ingested within specific timeframes (e.g., "new audio from the last 7 days"). Partitioning limits the data scanned, drastically reducing BigQuery costs.
- **Clustering:** The table is clustered by `audio_file_name`.
    - *Explanation:* Analysts frequently query specific files to spot-check transcription accuracy across different ethnic accents. Clustering by filename ensures rapid, indexed lookups for individual records.

## **Transformations**

Data transformations and orchestration are handled natively by **Bruin**, which acts as a modern alternative to dbt, seamlessly mixing SQL and Python DAGs with built-in data quality checks.

- **Staging (SQL):** Enforces data quality checks (Not Null, Unique) and adds temporal metadata (`processed_at`) to the raw ingestion list.
- **Intelligence Layer (Python):** Transforms the data by passing the records through a Hugging Face `faster-whisper` (tiny, int8 quantization) model optimized for the Indonesian language (`id`), and appending the AI-generated `transcript` directly into the final BigQuery presentation table.

## **Dashboard & Visualization**

## **Dashboard & Visualization**

The final presentation layer is built using **Looker Studio**, connected directly to a custom query joining the BigQuery staging metadata and the final AI `transcriptions` table.

- **Categorical Graph:** A Donut Chart visualizing the **Audio Distribution by Ethnic Accent**. This utilizes a custom SQL transformation to dynamically categorize the raw audio files into five regional Indonesian accents (Jawa, Batak, Melayu, Papua, and Sunda) based on file naming conventions.
- **Temporal Graph:** A Column Chart tracking the **Daily Ingestion Volume** against the `processed_at` timestamp. This visualizes the batch ingestion loads and confirms the temporal distribution of the pipeline's execution.
- **Data Quality Table:** A detailed grid displaying the original `audio_file_name` alongside the generated AI `transcript`, providing transparent, row-level proof of the successful end-to-end extraction and transformation flow.
    
    ![dashboard.png](attachment:991cf696-e50a-4889-ab88-d53c618ffb5c:dashboard.png)
    

---

## **Setup Instructions**

Follow these instructions to replicate the entire pipeline on any local machine (Windows/WSL, Mac, or Linux).

### **Prerequisites**

1. **Docker and Docker Compose** installed and running.
2. A Google Cloud Platform (GCP) account.
3. A Kaggle account.

### Step 1: Clone the Repository & Configure Credentials

Clone the repo to your local machine:

Bash

```jsx
git clone https://github.com/ananurkaromah/suara-pipeline.git
cd suara-pipeline
```

Next, securely provide your credentials:

1. **GCP:** Place your GCP Service Account JSON key in the root directory and name it exactly `gcp-key.json`.
2. **Kaggle & GCP Environment:** Create a file named `.env` in the root directory and add the following:

Bash

```jsx
GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

*(Note: `.env` and `gcp-key.json` are included in the `.gitignore` to prevent accidental exposure).*

### **Step 2: Provision Cloud Infrastructure (Terraform)**

Open your terminal and run Terraform to create your GCS bucket (Data Lake) and BigQuery dataset (Data Warehouse).

*(Note: Ensure you update `terraform/main.tf` with your specific GCP Project ID and a globally unique GCS bucket name before running).*

Bash

```jsx
cd terraform
terraform init
terraform apply
cd ..
```

### **Step 3: Start the Docker Environment**

The project relies on Docker to ensure a perfectly reproducible environment without polluting your local machine.

- **Dockerfile:** Handles the OS-level installations, sets up the `uv` package manager, and installs heavy data/AI dependencies (`faster-whisper`, `pandas`, `google-cloud-storage`).
- **docker-compose.yml:** Mounts your local project directory into the container so you can edit code live, and manages the lifecycle of the `suara-worker` environment.

Spin up the container. Docker Compose will automatically inject your credentials securely.

Bash

```jsx
docker-compose up -d --build
docker exec -it suara-worker bash
```

*(All following commands must be executed inside this `root@...:/app#` Docker terminal).*

### **Step 4: Authenticate APIs inside the Container**

Before running the pipeline, ensure the Kaggle Python API can find your credentials:

Bash

```jsx
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### **Step 5: Execute the Pipeline (Bruin)**

Bruin acts as our orchestrator and data transformer. Before running, ensure your  [.bruin.yml](https://github.com/ananurkaromah/suara-pipeline/blob/main/.bruin.yml)  file is configured with your correct GCP project ID and region.

The pipeline is structured as a Directed Acyclic Graph (DAG) across four assets in the `/assets` folder:

1. **`0_extract/`**[kaggle_to_gcs.py](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/0_extract/kaggle_to_gcs.py) **:** A Python asset that handles the Kaggle API call, unzips the data locally in the container, and batch uploads it to the GCS bucket.
2. **`1_ingestion/`**[raw_source.py](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/1_ingestion/raw_source.py)**:** A Python asset that connects to GCS, dynamically lists the physical `.wav` files, and materializes that metadata into BigQuery.
3. **`2_staging/`**[stg_audio_metadata.sql](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/2_staging/stg_audio_metadata.sql)**:** A SQL asset that applies data quality constraints (Unique/Not Null), adds processing timestamps, and builds a Partitioned and Clustered BigQuery table.
4. **`3_intelligence/`**[transcriber.py](https://github.com/ananurkaromah/suara-pipeline/blob/main/assets/3_intelligence/transcriber.py)**:** A Python asset that downloads the audio, runs the Hugging Face AI model for transcription, and writes the final text and language probabilities back to BigQuery.

Trigger the entire DAG with a single command:

Bash

```jsx
bruin run .
```

If successful, Bruin will output green success checks for the pipeline assets and all data quality constraints. The final transcribed dataset will be available in your BigQuery `transcriptions` table, ready to be attached to Looker Studio for dashboard visualization.

*(Note: In `1_ingestion/raw_source.py`, you can utilize `max_results=200` during "Development Mode" to prevent unexpected cloud costs. For a "Production" run, remove this limit so the full dataset is processed).*

### **Pipeline Idempotency & Incremental Loading**

This pipeline is designed to be fully idempotent:

- **Storage Layer:** The `kaggle_to_gcs` asset checks GCS before uploading, ensuring duplicate `.wav` files are never uploaded.
- **Compute Layer:** The Whisper AI transcription step uses an **incremental materialization** strategy. It performs a `LEFT JOIN` against the final BigQuery table, ensuring only net-new audio files are passed to the Hugging Face model. This drastically reduces compute time and prevents duplicate records upon multiple runs.

## **Acknowledgements**

- DataTalksClub — Data Engineering Zoomcamp course and community
- Kaggle — Dataset hosting
- Course Instructors — Alexey Grigorev and the DataTalksClub team