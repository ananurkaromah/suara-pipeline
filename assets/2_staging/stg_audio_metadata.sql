/* @bruin
name: suara_id.stg_audio_metadata
type: bq.sql
connection: gcp-default

materialization:
  type: table
  partition_by: "DATE(processed_at)"
  cluster_by: ["audio_file_name"]

depends:
  - suara_id.raw_source

description: "Cleaned staging metadata table for WAV audio files."

owner: "ana@suara-id.com"

custom_checks:
  - name: "check_id_positive"
    description: "Ensure all IDs are positive."
    query: "
      SELECT COUNT(*)
      FROM suara_id.stg_audio_metadata
      WHERE id <= 0
    "
    value: 0

  - name: "check_no_duplicate_audio"
    description: "Ensure audio file names are unique."
    query: "
      SELECT COUNT(*)
      FROM (
        SELECT audio_file_name
        FROM suara_id.stg_audio_metadata
        GROUP BY audio_file_name
        HAVING COUNT(*) > 1
      )
    "
    value: 0

columns:
  - name: id
    type: int64
    description: "Unique identifier from raw source."
    primary_key: true
    checks:
      - name: not_null
      - name: unique

  - name: audio_file_name
    type: string
    description: "WAV audio file name."
    checks:
      - name: not_null

  - name: processed_at
    type: timestamp
    description: "Timestamp when staging process occurred."
    checks:
      - name: not_null

@bruin */

WITH deduplicated AS (
    SELECT
        id,
        audio_file_name,
        CURRENT_TIMESTAMP() AS processed_at,
        ROW_NUMBER() OVER (
            PARTITION BY audio_file_name
            ORDER BY id
        ) AS rn
    FROM suara_id.raw_source
    WHERE LOWER(audio_file_name) LIKE '%.wav'
)

SELECT
    id,
    audio_file_name,
    processed_at
FROM deduplicated
WHERE rn = 1;