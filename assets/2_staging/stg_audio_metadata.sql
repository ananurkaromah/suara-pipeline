/* @bruin
name: suara_sea.stg_audio_metadata
type: bq.sql
connection: gcp-default
materialization:
  type: table
depends:
  - suara_sea.raw_source
description: "Staging layer that adds processing metadata to raw audio records."
owner: "data.engineer@suara-sea.com"
custom_checks:
  - name: "business_rule_no_future_processing"
    query: "SELECT count(*) FROM suara_sea.stg_audio_metadata WHERE processed_at > CURRENT_TIMESTAMP()"
    value: 0
columns:
  - name: id
    type: int64
    description: "Primary key inherited from raw source"
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    description: "The filename of the audio sample"
    checks:
      - name: not_null
  - name: processed_at
    type: timestamp
    description: "The exact time this record was staged"
    checks:
      - name: not_null
@bruin */

SELECT 
  id, 
  audio_file_name, 
  CURRENT_TIMESTAMP() as processed_at 
FROM suara_sea.raw_source;
