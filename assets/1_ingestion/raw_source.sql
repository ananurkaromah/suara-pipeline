/* @bruin
name: suara_sea.raw_source
type: bq.sql
connection: gcp-default
materialization:
  type: table
description: "Ingestion table for raw Southeast Asian audio file records."
owner: "data.engineer@suara-sea.com"
custom_checks:
  - name: "business_rule_valid_audio_format"
    query: "SELECT count(*) FROM suara_sea.raw_source WHERE audio_file_name NOT LIKE '%.wav'"
    value: 0
columns:
  - name: id
    type: int64
    description: "Unique identifier for the audio record"
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    description: "The filename of the audio sample"
    checks:
      - name: not_null
@bruin */

-- Simulating incoming raw data
SELECT 
  1 as id, 
  'sample_indonesian_01.wav' as audio_file_name;
