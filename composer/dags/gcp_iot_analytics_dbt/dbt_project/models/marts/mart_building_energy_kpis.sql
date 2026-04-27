{{
  config(
    materialized='table',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['building_id']
  )
}}

with hourly as (
    select * from {{ ref('int_device_hourly_energy') }}
),

quality as (
    select * from {{ ref('int_device_daily_quality') }}
),

daily_building as (
    select
        h.building_id,
        date(h.event_hour) as event_date,
        avg(h.avg_energy_kwh) as building_avg_energy_kwh,
        max(h.peak_energy_kwh) as building_peak_energy_kwh,
        avg(h.avg_temperature_celsius) as building_avg_temperature_celsius,
        sum(h.events_in_hour) as total_events
    from hourly h
    group by 1, 2
),

quality_rollup as (
    select
        building_id,
        event_date,
        sum(invalid_negative_energy_events) as invalid_negative_energy_events,
        sum(null_metric_events) as null_metric_events,
        avg(null_ratio) as avg_null_ratio,
        sum(offline_events) as offline_events
    from quality
    group by 1, 2
)

select
    d.building_id,
    d.event_date,
    d.building_avg_energy_kwh,
    d.building_peak_energy_kwh,
    d.building_avg_temperature_celsius,
    d.total_events,
    q.invalid_negative_energy_events,
    q.null_metric_events,
    q.avg_null_ratio,
    q.offline_events
from daily_building d
left join quality_rollup q
  using (building_id, event_date)
