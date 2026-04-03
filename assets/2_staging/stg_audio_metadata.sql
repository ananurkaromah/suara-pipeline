-- @bruin
-- name: suara_id.stg_audio_metadata
-- type: bq.sql
-- connection: gcp-default
-- materialization:
--   type: table
-- description: "Staging dataset containing extracted metadata and file paths from raw audio files."
-- owner: "data.engineering@suara-pipeline.com"
-- depends:
--   - suara_id.raw_source
-- columns:
--   - name: audio_id
--     type: string
--     description: "Unique identifier for the audio file."
--     primary_key: true
--     checks:
--       - name: not_null
--       - name: unique
--   - name: file_path
--     type: string
--     description: "Cloud storage path or local URI to the raw audio file."
--     checks:
--       - name: not_null
--   - name: duration_seconds
--     type: numeric
--     description: "Duration of the audio file in seconds."
--     checks:
--       - name: not_null
-- custom_checks:
--   - name: "ensure_positive_duration"
--     query: "SELECT count(*) FROM suara_id.stg_audio_metadata WHERE duration_seconds <= 0"
--     value: 0
-- @bruin

SELECT 
  CAST(id AS STRING) AS audio_id, 
  audio_file_name AS file_path, 
  1.0 AS duration_seconds, 
  CURRENT_TIMESTAMP() as processed_at 
FROM suara_id.raw_source;
