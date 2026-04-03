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
description: "Staging layer partitioned by processing date and clustered by filename."
owner: "ana@suara-id.com"
custom_checks:
  - name: "check_id_range"
    description: "Ensure ID is always positive."
    query: "SELECT count(*) FROM suara_id.stg_audio_metadata WHERE id <= 0"
    value: 0
columns:
  - name: id
    type: int64
    description: "Primary key inherited from raw source."
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    description: "The name of the audio file."
    checks:
      - name: not_null
  - name: processed_at
    type: timestamp
    description: "Timestamp of when the record was processed."
    checks:
      - name: not_null
@bruin */

SELECT 
  id, 
  audio_file_name, 
  CURRENT_TIMESTAMP() as processed_at 
FROM suara_id.raw_source;