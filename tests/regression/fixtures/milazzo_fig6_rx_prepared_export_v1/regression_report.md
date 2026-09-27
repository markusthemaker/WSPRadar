# Regression Report: milazzo_fig6_rx_prepared_export_v1

- App: WSPRadar.org
- Version: v0.99m
- Built UTC: 2026-09-27T09:54:34Z
- Scope: fixture package integrity and exported evidence-shape regression

## benchmark - RX Benchmark: KP4MD (Target) vs. WB6RQN (Reference)

- Result mode: benchmark
- Sequential: False
- Segment: Full Range / All Directions
- Include Unpaired Evidence: True
- Evidence bin: 3h
- Analysis cache: benchmark/analysis_cache.parquet

| Kind | Name | Rows | Columns | Size | Description |
| --- | --- | ---: | ---: | ---: | --- |
| table | table_station_insights_current_segment.csv | 2 | 8 |  | station insight table shape, columns, joint/spot sums and median columns |
|  | metrics |  |  |  | `mean_of_Median Δ SNR (dB)` = `10.0`<br>`median_of_Median Δ SNR (dB)` = `10.0`<br>`segment_station_metric_column` = `Median Δ SNR (dB)`<br>`segment_station_metric_max` = `12.0`<br>`segment_station_metric_mean` = `10.0`<br>`segment_station_metric_median` = `10.0`<br>`segment_station_metric_min` = `8.0`<br>`segment_station_metric_non_null` = `2`<br>`sum_Joint Spots` = `5`<br>`sum_Only KP4MD` = `26`<br>`sum_Only WB6RQN` = `3` |
| table | table_drilldown_selected_stations.csv | 13 | 10 |  | selected-station drill-down shape and columns |
|  | metrics |  |  |  | `mean_of_KP4MD SNR (dB)` = `-16.455`<br>`mean_of_WB6RQN SNR (dB)` = `-26.8`<br>`mean_of_Δ SNR (dB)` = `12.333`<br>`median_of_KP4MD SNR (dB)` = `-17.0`<br>`median_of_WB6RQN SNR (dB)` = `-30.0`<br>`median_of_Δ SNR (dB)` = `8.0` |
| table | table_drilldown_all_stations_current_segment.csv | 34 | 10 |  | all-station current-segment drill-down shape and columns, including non-joint evidence where applicable |
|  | metrics |  |  |  | `mean_of_KP4MD SNR (dB)` = `-20.226`<br>`mean_of_WB6RQN SNR (dB)` = `-26.75`<br>`mean_of_Δ SNR (dB)` = `12.2`<br>`median_of_KP4MD SNR (dB)` = `-20.0`<br>`median_of_WB6RQN SNR (dB)` = `-29.5`<br>`median_of_Δ SNR (dB)` = `8.0` |
| figure | figure_map_highres.png |  |  | 3498x3632 | PNG presence and readability |
| figure | figure_segment_insight.png |  |  | 3885x1654 | PNG presence and readability |
| figure | figure_segment_temporal_evidence.png |  |  | 3815x1639 | PNG presence and readability |
| figure | figure_selected_station_evidence.png |  |  | 3815x1639 | PNG presence and readability |
| analysis_cache | analysis_cache.parquet | 34 | 11 |  | parquet cache readability, row count, column count and schema |
