{{
  config(
    materialized='table',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['building_id', 'device_id']
  )
}}

with base as (
    select *
    from {{ ref('stg_iot_energy_events') }}
    where energy_consumption_kwh is not null
),

hourly as (
    select
        building_id,
        device_id,
        timestamp_trunc(event_timestamp, hour) as event_hour,
        date(event_timestamp) as event_date,
        avg(energy_consumption_kwh) as avg_energy_kwh,
        max(energy_consumption_kwh) as peak_energy_kwh,
        avg(temperature_celsius) as avg_temperature_celsius,
        count(*) as events_in_hour
    from base
    group by 1, 2, 3, 4
)

select * from hourly
