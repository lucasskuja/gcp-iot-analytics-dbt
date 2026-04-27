{{
  config(
    materialized='incremental',
    unique_key='event_sk',
    incremental_strategy='merge',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['building_id', 'device_id', 'status_normalized'],
    on_schema_change='sync_all_columns'
  )
}}

with source_data as (
    select
        ingestion_batch_id,
        event_id,
        device_id,
        building_id,
        timestamp as event_timestamp,
        date(timestamp) as event_date,
        energy_consumption,
        temperature,
        {{ normalize_status('status') }} as status_normalized,
        ingested_at,
        source_file
    from {{ source('raw_iot_energy', 'iot_energy_events_raw') }}
    where true
    {{ incremental_reprocess_window('timestamp', 2) }}
),

ranked as (
    select
        {{ generate_business_key(['event_id', 'device_id', 'cast(event_timestamp as string)']) }} as event_sk,
        ingestion_batch_id,
        event_id,
        device_id,
        building_id,
        event_timestamp,
        event_date,
        energy_consumption,
        temperature,
        status_normalized,
        ingested_at,
        source_file,
        row_number() over (
            partition by event_id, device_id, event_timestamp
            order by ingested_at desc
        ) as dedup_rank
    from source_data
),

cleaned as (
    select
        event_sk,
        ingestion_batch_id,
        event_id,
        device_id,
        building_id,
        event_timestamp,
        event_date,
        case
            when energy_consumption is null then null
            when energy_consumption < 0 then null
            else energy_consumption
        end as energy_consumption_kwh,
        temperature as temperature_celsius,
        status_normalized,
        ingested_at,
        source_file,
        case when energy_consumption < 0 then true else false end as had_negative_energy,
        case when energy_consumption is null or temperature is null then true else false end as had_null_metric
    from ranked
    where dedup_rank = 1
)

select * from cleaned
