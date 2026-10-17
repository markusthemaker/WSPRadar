# Fixed security boundary for the public website workflow, not operator configuration.
# Application source and history must never be published through these helpers.
$script:WebsiteRepositoryPolicy = @{
    FullName = 'markusthemaker/WSPRadar'
    Id = 1416038123L
    RootCommit = 'ce3546f4ad40f7729a7397d813359630e29b2e79'
    AllowedUrls = @(
        'https://github.com/markusthemaker/WSPRadar.git',
        'https://github.com/markusthemaker/WSPRadar',
        'git@github.com:markusthemaker/WSPRadar.git',
        'git@github.com:markusthemaker/WSPRadar',
        'ssh://git@github.com/markusthemaker/WSPRadar.git',
        'ssh://git@github.com/markusthemaker/WSPRadar'
    )
}
$script:WebsiteRepositoryRoot = $null
$script:WebsiteAllowedFiles = @(
    '.github/ISSUE_TEMPLATE/bug_report.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/ISSUE_TEMPLATE/feature_request.yml',
    '.github/ISSUE_TEMPLATE/scientific_concern.yml',
    '.github/SUPPORT.md',
    'CNAME',
    'README.md',
    'img/WSPRadar-2x1.png',
    'index.html',
    'scripts/git-repository-guard.ps1',
    'scripts/git-push-temp.ps1',
    'scripts/git-release-main.ps1',
    'scripts/git-baseline-temp.ps1',
    'scripts/README.md',
    'scripts/tests/test_git_workflow_safety.py',
    # Reviewed static website sources, public-content bundle, assets, and tests.
    '.gitattributes',
    '.github/DISCUSSION_TEMPLATE/report-a-bug-or-concern.yml',
    '.gitignore',
    'AGENTS.md',
    'content/generated/assets/brand/Rajdhani-OFL.txt',
    'content/generated/assets/brand/SourceSans3-OFL.txt',
    'content/generated/assets/brand/SpaceMono-OFL.txt',
    'content/generated/assets/brand/WSPRadar-140x140.png',
    'content/generated/assets/brand/radar-hero-desktop-1024.png',
    'content/generated/assets/brand/radar-hero-desktop-1024.webp',
    'content/generated/assets/brand/radar-hero-desktop-1280.webp',
    'content/generated/assets/brand/radar-hero-desktop-1536.webp',
    'content/generated/assets/brand/radar-hero-desktop-1896.webp',
    'content/generated/assets/brand/radar-hero-desktop-768.webp',
    'content/generated/assets/brand/radar-hero-desktop-992.webp',
    'content/generated/assets/brand/radar-hero-desktop.png',
    'content/generated/assets/brand/radar-hero-mobile-400.webp',
    'content/generated/assets/brand/radar-hero-mobile-600.webp',
    'content/generated/assets/brand/radar-hero-mobile-888.webp',
    'content/generated/assets/brand/radar-hero-mobile.png',
    'content/generated/assets/brand/rajdhani-v17-600-normal-devanagari.woff2',
    'content/generated/assets/brand/rajdhani-v17-600-normal-latin-ext.woff2',
    'content/generated/assets/brand/rajdhani-v17-600-normal-latin.woff2',
    'content/generated/assets/brand/rajdhani-v17-700-normal-devanagari.woff2',
    'content/generated/assets/brand/rajdhani-v17-700-normal-latin-ext.woff2',
    'content/generated/assets/brand/rajdhani-v17-700-normal-latin.woff2',
    'content/generated/assets/brand/source-sans-3-v20-italic-latin-ext.woff2',
    'content/generated/assets/brand/source-sans-3-v20-italic-latin.woff2',
    'content/generated/assets/brand/source-sans-3-v20-normal-latin-ext.woff2',
    'content/generated/assets/brand/source-sans-3-v20-normal-latin.woff2',
    'content/generated/assets/brand/space-mono-v17-400-italic-latin-ext.woff2',
    'content/generated/assets/brand/space-mono-v17-400-italic-latin.woff2',
    'content/generated/assets/brand/space-mono-v17-400-italic-vietnamese.woff2',
    'content/generated/assets/brand/space-mono-v17-400-normal-latin-ext.woff2',
    'content/generated/assets/brand/space-mono-v17-400-normal-latin.woff2',
    'content/generated/assets/brand/space-mono-v17-400-normal-vietnamese.woff2',
    'content/generated/assets/brand/space-mono-v17-700-normal-latin-ext.woff2',
    'content/generated/assets/brand/space-mono-v17-700-normal-latin.woff2',
    'content/generated/assets/brand/space-mono-v17-700-normal-vietnamese.woff2',
    'content/generated/assets/figures/griffiths-figure3-comparison.png',
    'content/generated/assets/figures/griffiths-figure3-pairing-diagnostic.png',
    'content/generated/assets/figures/griffiths-figure6-comparison.png',
    'content/generated/assets/figures/landing-demo1-coverage.webp',
    'content/generated/assets/figures/landing-demo1-map.webp',
    'content/generated/assets/figures/landing-demo1-snr.webp',
    'content/generated/assets/figures/landing-demo1-temporal.webp',
    'content/generated/assets/figures/milazzo-figure6-rx-comparison.png',
    'content/generated/assets/figures/milazzo-figure7-tx-comparison.png',
    'content/generated/assets/figures/vanhamel-figure6-comparison.png',
    'content/generated/assets/figures/zander-figure4-comparison.png',
    'content/generated/assets/screenshots/demo-1-drilldown.jpg',
    'content/generated/assets/screenshots/demo-1-map.jpg',
    'content/generated/assets/screenshots/demo-1-segment.jpg',
    'content/generated/assets/screenshots/demo-1-stations.jpg',
    'content/generated/assets/screenshots/demo-1-temporal.jpg',
    'content/generated/assets/screenshots/demo-2-map.jpg',
    'content/generated/assets/screenshots/demo-2-temporal.jpg',
    'content/generated/assets/screenshots/demo-5-selected-evidence.jpg',
    'content/generated/assets/screenshots/demo-6-map.jpg',
    'content/generated/assets/screenshots/demo-6-segment.jpg',
    'content/generated/assets/screenshots/demo-7-drilldown.jpg',
    'content/generated/assets/screenshots/demo-7-stations.jpg',
    'content/generated/brand.json',
    'content/generated/configs/griffiths_squibb_fig3.config',
    'content/generated/configs/griffiths_squibb_fig6.config',
    'content/generated/configs/griffiths_squibb_rx_performance.config',
    'content/generated/configs/milazzo_tx_buddy.config',
    'content/generated/configs/vanhamel_rx_buddy.config',
    'content/generated/configs/vanhamel_rx_calibration.config',
    'content/generated/configs/zander_tx_buddy.config',
    'content/generated/demos.json',
    'content/generated/figures.json',
    'content/generated/manifest.json',
    'content/generated/manual.de.md',
    'content/generated/manual.en.md',
    'content/generated/screenshots.json',
    'content/generated/website.json',
    'docs/architecture.md',
    'requirements-site.txt',
    'scripts/build_site.py',
    'scripts/demo_walkthrough.py',
    'scripts/external_links.py',
    'scripts/landing_page.py',
    'scripts/prepare_landing_assets.py',
    'site/assets/flags/de.svg',
    'site/assets/flags/en.svg',
    'site/assets/landing/README.md',
    'site/assets/landing/manifest.json',
    'site/assets/landing/source/README.md',
    'site/assets/landing/source/brand/WSPRadar-Europe-world-network.png',
    'site/assets/landing/source/brand/WSPRadar-logo-lockup-concept.png',
    'site/assets/landing/source/brand/WSPRadar-radar-emblem-concept.png',
    'site/assets/landing/source/diagrams/how-it-works-flow.png',
    'site/assets/landing/source/diagrams/how-it-works-flow.svg',
    'site/assets/landing/source/fonts/Caveat-METADATA.pb',
    'site/assets/landing/source/fonts/Caveat-OFL.txt',
    'site/assets/landing/source/fonts/Caveat-variable.ttf',
    'site/assets/landing/source/fonts/README.md',
    'site/assets/landing/source/hero/Europe-signal-paths-art-transparent.png',
    'site/assets/landing/source/hero/Europe-signal-paths-hero-with-copy.png',
    'site/assets/landing/source/hero/WSPR-Insights-Across-Earth.png',
    'site/assets/landing/source/hero/WSPRadar-Global-Signal-Insights.png',
    'site/assets/landing/source/icon-contact-sheet.png',
    'site/assets/landing/source/icon-manifest.json',
    'site/assets/landing/source/icons/monochrome/analysis-laptop.svg',
    'site/assets/landing/source/icons/monochrome/evidence-chart.svg',
    'site/assets/landing/source/icons/monochrome/results-map.svg',
    'site/assets/landing/source/icons/monochrome/rx-benchmark.svg',
    'site/assets/landing/source/icons/monochrome/rx-performance.svg',
    'site/assets/landing/source/icons/monochrome/rx-station.svg',
    'site/assets/landing/source/icons/monochrome/try-demo.svg',
    'site/assets/landing/source/icons/monochrome/tx-benchmark.svg',
    'site/assets/landing/source/icons/monochrome/tx-performance.svg',
    'site/assets/landing/source/icons/monochrome/tx-station.svg',
    'site/assets/landing/source/icons/monochrome/vertical-antenna.svg',
    'site/assets/landing/source/icons/monochrome/world-paths.svg',
    'site/assets/landing/source/icons/monochrome/wspr-database.svg',
    'site/assets/landing/source/icons/monochrome/wspr-spot.svg',
    'site/assets/landing/source/icons/monochrome/yagi-antenna.svg',
    'site/assets/landing/source/icons/neon/analysis-laptop.svg',
    'site/assets/landing/source/icons/neon/evidence-chart.svg',
    'site/assets/landing/source/icons/neon/results-map.svg',
    'site/assets/landing/source/icons/neon/rx-benchmark.svg',
    'site/assets/landing/source/icons/neon/rx-performance.svg',
    'site/assets/landing/source/icons/neon/rx-station.svg',
    'site/assets/landing/source/icons/neon/try-demo.svg',
    'site/assets/landing/source/icons/neon/tx-benchmark.svg',
    'site/assets/landing/source/icons/neon/tx-performance.svg',
    'site/assets/landing/source/icons/neon/tx-station.svg',
    'site/assets/landing/source/icons/neon/vertical-antenna.svg',
    'site/assets/landing/source/icons/neon/world-paths.svg',
    'site/assets/landing/source/icons/neon/wspr-database.svg',
    'site/assets/landing/source/icons/neon/wspr-spot.svg',
    'site/assets/landing/source/icons/neon/yagi-antenna.svg',
    'site/assets/landing/source/icons/png-512/analysis-laptop.png',
    'site/assets/landing/source/icons/png-512/evidence-chart.png',
    'site/assets/landing/source/icons/png-512/results-map.png',
    'site/assets/landing/source/icons/png-512/rx-benchmark.png',
    'site/assets/landing/source/icons/png-512/rx-performance.png',
    'site/assets/landing/source/icons/png-512/rx-station.png',
    'site/assets/landing/source/icons/png-512/try-demo.png',
    'site/assets/landing/source/icons/png-512/tx-benchmark.png',
    'site/assets/landing/source/icons/png-512/tx-performance.png',
    'site/assets/landing/source/icons/png-512/tx-station.png',
    'site/assets/landing/source/icons/png-512/vertical-antenna.png',
    'site/assets/landing/source/icons/png-512/world-paths.png',
    'site/assets/landing/source/icons/png-512/wspr-database.png',
    'site/assets/landing/source/icons/png-512/wspr-spot.png',
    'site/assets/landing/source/icons/png-512/yagi-antenna.png',
    'site/assets/landing/web/fonts/Caveat-OFL.txt',
    'site/assets/landing/web/fonts/caveat-hand-latin.ttf',
    'site/assets/landing/web/hero-1280.png',
    'site/assets/landing/web/hero-1280.webp',
    'site/assets/landing/web/hero-1600.webp',
    'site/assets/landing/web/hero-2172.webp',
    'site/assets/landing/web/hero-480.webp',
    'site/assets/landing/web/hero-768.webp',
    'site/assets/landing/web/icons/analysis-laptop.svg',
    'site/assets/landing/web/icons/evidence-chart.svg',
    'site/assets/landing/web/icons/results-map.svg',
    'site/assets/landing/web/icons/rx-benchmark.svg',
    'site/assets/landing/web/icons/rx-performance.svg',
    'site/assets/landing/web/icons/rx-station.svg',
    'site/assets/landing/web/icons/try-demo.svg',
    'site/assets/landing/web/icons/tx-benchmark.svg',
    'site/assets/landing/web/icons/tx-performance.svg',
    'site/assets/landing/web/icons/tx-station.svg',
    'site/assets/landing/web/icons/vertical-antenna.svg',
    'site/assets/landing/web/icons/world-paths.svg',
    'site/assets/landing/web/icons/wspr-database.svg',
    'site/assets/landing/web/icons/wspr-spot.svg',
    'site/assets/landing/web/icons/yagi-antenna.svg',
    'site/assets/landing/web/logo-128.png',
    'site/assets/landing/web/logo-128.webp',
    'site/assets/landing/web/logo-64.webp',
    'site/assets/landing/web/network-1000.webp',
    'site/assets/landing/web/network-400.webp',
    'site/assets/landing/web/network-700.png',
    'site/assets/landing/web/network-700.webp',
    'site/demo-walkthrough.css',
    'site/demo-walkthrough.js',
    'site/demo_walkthroughs.json',
    'site/demos/README.md',
    'site/demos/griffiths_squibb_fig3/resources/WSPRadar_export_2026_10_15__10_39.zip',
    'site/demos/griffiths_squibb_fig3/resources/demo1_verified_export_summary.json',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_map_highres.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_segment_insight.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_segment_temporal_coverage.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_segment_temporal_evidence.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_selected_station_coverage.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/figure_selected_station_evidence.png',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/table_drilldown_all_stations_current_segment.csv',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/table_drilldown_selected_stations.csv',
    'site/demos/griffiths_squibb_fig3/resources/export/benchmark/table_station_insights_current_segment.csv',
    'site/demos/griffiths_squibb_fig3/resources/export/config/run_metadata.json',
    'site/demos/griffiths_squibb_fig3/resources/export/config/wspradar_config.config',
    'site/demos/griffiths_squibb_fig3/resources/fresh/WSPRadar_export_2026_10_15__17_39.zip',
    'site/demos/griffiths_squibb_fig3/resources/fresh/comparison_with_supplied_export.json',
    'site/demos/griffiths_squibb_fig3/resources/fresh/coverage.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/demo1_verified_export_summary.json',
    'site/demos/griffiths_squibb_fig3/resources/fresh/difference.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/export/benchmark/table_drilldown_all_stations_current_segment.csv',
    'site/demos/griffiths_squibb_fig3/resources/fresh/export/benchmark/table_drilldown_selected_stations.csv',
    'site/demos/griffiths_squibb_fig3/resources/fresh/export/benchmark/table_station_insights_current_segment.csv',
    'site/demos/griffiths_squibb_fig3/resources/fresh/export/config/run_metadata.json',
    'site/demos/griffiths_squibb_fig3/resources/fresh/export/config/wspradar_config.config',
    'site/demos/griffiths_squibb_fig3/resources/fresh/map.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/provenance.json',
    'site/demos/griffiths_squibb_fig3/resources/fresh/station-coverage.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/station.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/time.png',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/coverage-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/coverage-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/difference-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/difference-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/map-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/map-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/station-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/station-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/station-coverage-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/station-coverage-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/time-1200.webp',
    'site/demos/griffiths_squibb_fig3/resources/fresh/web/time-600.webp',
    'site/demos/griffiths_squibb_fig3/resources/manifest.json',
    'site/demos/griffiths_squibb_fig3/resources/setup/setup-network-1040.webp',
    'site/demos/griffiths_squibb_fig3/resources/setup/setup-network-1600.webp',
    'site/demos/griffiths_squibb_fig3/resources/setup/setup-network-520.webp',
    'site/demos/griffiths_squibb_fig3/source/2026-10-15-figure3-addition.de.md',
    'site/demos/griffiths_squibb_fig3/source/2026-10-15-figure3-addition.en.md',
    'site/demos/griffiths_squibb_fig3/source/2026-10-15-worked-example.en.md',
    'site/demos/griffiths_squibb_fig3/source/initial-layout-copy.json',
    'site/demos/griffiths_squibb_fig3/source/setup-network-original.png',
    'site/demos/griffiths_squibb_fig3/source/setup-network-provenance.json',
    'site/demos/griffiths_squibb_fig3/walkthrough.de.md',
    'site/demos/griffiths_squibb_fig3/walkthrough.en.md',
    'site/demos/griffiths_squibb_fig6/walkthrough.de.md',
    'site/demos/griffiths_squibb_fig6/walkthrough.en.md',
    'site/demos/griffiths_squibb_rx_performance/walkthrough.de.md',
    'site/demos/griffiths_squibb_rx_performance/walkthrough.en.md',
    'site/demos/milazzo_tx_buddy/walkthrough.de.md',
    'site/demos/milazzo_tx_buddy/walkthrough.en.md',
    'site/demos/vanhamel_rx_buddy/resources/WSPRadar_Demo_Vanhamel_Figure6.pdf',
    'site/demos/vanhamel_rx_buddy/resources/benchmark-evidence.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/benchmark-evidence.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/benchmark-evidence.en.png',
    'site/demos/vanhamel_rx_buddy/resources/manifest.json',
    'site/demos/vanhamel_rx_buddy/resources/map.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/map.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/map.en.png',
    'site/demos/vanhamel_rx_buddy/resources/rotation-evidence-provenance.json',
    'site/demos/vanhamel_rx_buddy/resources/selected-coverage.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/selected-coverage.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/selected-coverage.en.png',
    'site/demos/vanhamel_rx_buddy/resources/selected-evidence.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/selected-evidence.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/selected-evidence.en.png',
    'site/demos/vanhamel_rx_buddy/resources/temporal-coverage.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/temporal-coverage.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/temporal-coverage.en.png',
    'site/demos/vanhamel_rx_buddy/resources/temporal-evidence.en-1040.webp',
    'site/demos/vanhamel_rx_buddy/resources/temporal-evidence.en-520.webp',
    'site/demos/vanhamel_rx_buddy/resources/temporal-evidence.en.png',
    'site/demos/vanhamel_rx_buddy/source/README.md',
    'site/demos/vanhamel_rx_buddy/source/supplied-walkthrough.en.txt',
    'site/demos/vanhamel_rx_buddy/source/walkthrough.previous.de.md',
    'site/demos/vanhamel_rx_buddy/source/walkthrough.previous.en.md',
    'site/demos/vanhamel_rx_buddy/walkthrough.de.md',
    'site/demos/vanhamel_rx_buddy/walkthrough.en.md',
    'site/demos/vanhamel_rx_calibration/resources/benchmark-evidence.en-1040.webp',
    'site/demos/vanhamel_rx_calibration/resources/benchmark-evidence.en-520.webp',
    'site/demos/vanhamel_rx_calibration/resources/benchmark-evidence.en.png',
    'site/demos/vanhamel_rx_calibration/resources/calibration-evidence-provenance.json',
    'site/demos/vanhamel_rx_calibration/resources/figure1-dark-1040.webp',
    'site/demos/vanhamel_rx_calibration/resources/figure1-dark-520.webp',
    'site/demos/vanhamel_rx_calibration/resources/figure1-dark.png',
    'site/demos/vanhamel_rx_calibration/resources/figure1-dark.svg',
    'site/demos/vanhamel_rx_calibration/resources/figure1-provenance.json',
    'site/demos/vanhamel_rx_calibration/resources/manifest.json',
    'site/demos/vanhamel_rx_calibration/source/README.md',
    'site/demos/vanhamel_rx_calibration/source/figure1-pdf-decoded-raster.png',
    'site/demos/vanhamel_rx_calibration/source/figure1-pdf-original-raster.jpeg',
    'site/demos/vanhamel_rx_calibration/source/figure1-source.svg',
    'site/demos/vanhamel_rx_calibration/source/supplied-walkthrough.en.txt',
    'site/demos/vanhamel_rx_calibration/source/walkthrough.previous.de.md',
    'site/demos/vanhamel_rx_calibration/source/walkthrough.previous.en.md',
    'site/demos/vanhamel_rx_calibration/walkthrough.de.md',
    'site/demos/vanhamel_rx_calibration/walkthrough.en.md',
    'site/demos/walkthrough.template.md',
    'site/demos/zander_tx_buddy/resources/figure_map_highres-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_map_highres-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_map_highres.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_map_highres.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_map_highres.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_map_highres.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_insight.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_coverage.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_segment_temporal_evidence.png',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_coverage.png',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence.dark-1040.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence.dark-520.webp',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence.dark.png',
    'site/demos/zander_tx_buddy/resources/figure_selected_station_evidence.png',
    'site/demos/zander_tx_buddy/resources/manifest.json',
    'site/demos/zander_tx_buddy/resources/setup/setup-network-1040.webp',
    'site/demos/zander_tx_buddy/resources/setup/setup-network-1584.webp',
    'site/demos/zander_tx_buddy/resources/setup/setup-network-520.webp',
    'site/demos/zander_tx_buddy/resources/setup/setup-network.png',
    'site/demos/zander_tx_buddy/resources/zander-evidence-provenance.json',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/Source_and_Handoff_Notes.md',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/Zander_Portable_Vertical_Comparison.md',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_map_highres.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_segment_insight.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_segment_temporal_coverage.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_segment_temporal_evidence.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_selected_station_coverage.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/assets/figure_selected_station_evidence.png',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/export_disclaimer.txt',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/run_metadata.json',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/table_drilldown_all_stations_current_segment.csv',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/table_drilldown_selected_stations.csv',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/table_station_insights_current_segment.csv',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/sources/wspradar_config.config',
    'site/demos/zander_tx_buddy/source/supplied-2026-10-16/verification.json',
    'site/demos/zander_tx_buddy/source/walkthrough.before-supplied-2026-10-16.de.md',
    'site/demos/zander_tx_buddy/source/walkthrough.before-supplied-2026-10-16.en.md',
    'site/demos/zander_tx_buddy/walkthrough.de.md',
    'site/demos/zander_tx_buddy/walkthrough.en.md',
    'site/entry.js',
    'site/landing.css',
    'site/landing.json',
    'site/page.html',
    'site/print.css',
    'site/print.js',
    'site/site.css',
    'site/site.js',
    'tests/test_demo_walkthrough.py',
    'tests/test_entry.cjs',
    'tests/test_external_links.py',
    'tests/test_print.cjs',
    'tests/test_site_build.py'
)
$script:WebsiteCheckedTrees = @{}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & git -C $script:WebsiteRepositoryRoot @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Get-GitOutput {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $output = & git -C $script:WebsiteRepositoryRoot @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
    return $output
}

function Get-WebsiteGitConfig {
    param([string]$Name, [switch]$Boolean)
    $arguments = @('config')
    if ($Boolean) { $arguments += '--bool' }
    $output = & git -C $script:WebsiteRepositoryRoot @arguments --get-all $Name
    if ($LASTEXITCODE -eq 1) { return }
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect Git setting '$Name'." }
    return $output
}

function Assert-WebsiteGitEnvironment {
    $redirectingVariables = @(
        'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
        'GIT_NAMESPACE', 'GIT_SHALLOW_FILE', 'GIT_CONFIG',
        'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG_COUNT', 'GIT_REPLACE_REF_BASE',
        'GIT_GRAFT_FILE'
    )
    foreach ($variable in Get-ChildItem Env:) {
        if ($variable.Name -in $redirectingVariables -or $variable.Name -match '^GIT_CONFIG_(KEY|VALUE)_') {
            throw "Git environment override '$($variable.Name)' is set. Remove it before using the website workflow."
        }
    }
}

function Assert-WebsiteRepository {
    Assert-WebsiteGitEnvironment
    # Raw and expanded URLs are both checked: get-url expands insteadOf/pushInsteadOf.
    # Checking all push URLs is essential because Git can push to several destinations.
    $fetchUrls = @(Get-WebsiteGitConfig 'remote.origin.url')
    if ($fetchUrls.Count -eq 0) { throw 'Website origin is missing.' }
    $urls = @($fetchUrls)
    $urls += @(Get-WebsiteGitConfig 'remote.origin.pushurl')
    $urls += @(Get-GitOutput remote get-url --all origin)
    $urls += @(Get-GitOutput remote get-url --push --all origin)
    foreach ($url in $urls) {
        if ($url -notin $script:WebsiteRepositoryPolicy.AllowedUrls) {
            # Do not echo an unexpected URL: it might contain an embedded credential.
            throw 'Unapproved origin URL. Every fetch and push destination must be markusthemaker/WSPRadar on github.com.'
        }
    }
    if ('true' -in @(Get-WebsiteGitConfig 'remote.origin.mirror' -Boolean)) {
        throw 'Mirror pushes are forbidden in the website workflow.'
    }
    foreach ($setting in @('remote.origin.receivepack', 'remote.origin.uploadpack', 'remote.origin.vcs')) {
        if (@(Get-WebsiteGitConfig $setting).Count -gt 0) {
            throw "Custom Git transport setting '$setting' is not supported by the website workflow."
        }
    }

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw 'GitHub CLI (gh) is required to verify the public website repository. Authenticate to github.com before retrying.'
    }
    $metadataText = & gh api --hostname github.com "repos/$($script:WebsiteRepositoryPolicy.FullName)"
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot verify website repository identity and visibility. Check network access and gh authentication to github.com; no workflow changes were made by this check.'
    }
    try {
        $metadata = ($metadataText -join "`n") | ConvertFrom-Json -ErrorAction Stop
        $validIdentity = ($metadata.id -is [long] -or $metadata.id -is [int]) -and
            $metadata.id -eq $script:WebsiteRepositoryPolicy.Id -and
            $metadata.full_name -ceq $script:WebsiteRepositoryPolicy.FullName -and
            $metadata.private -is [bool] -and (-not $metadata.private)
    } catch {
        throw 'GitHub returned invalid repository metadata; refusing to continue.'
    }
    if (-not $validIdentity) {
        throw 'GitHub repository identity or public visibility does not match the website policy; refusing to continue.'
    }
}

function Initialize-WebsiteRepository {
    param([Parameter(Mandatory = $true)][string]$ScriptDirectory)
    Assert-WebsiteGitEnvironment
    $expectedRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDirectory '..')).TrimEnd([char[]]'\/')
    $scriptRoot = & git -C $expectedRoot rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw 'The workflow script is not inside an website checkout.' }
    $callerRoot = & git -C (Get-Location).ProviderPath rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw 'Run this script from inside its website checkout.' }
    $resolvedScriptRoot = [System.IO.Path]::GetFullPath(($scriptRoot | Select-Object -First 1)).TrimEnd([char[]]'\/')
    $resolvedCallerRoot = [System.IO.Path]::GetFullPath(($callerRoot | Select-Object -First 1)).TrimEnd([char[]]'\/')
    if ($resolvedScriptRoot -ne $expectedRoot -or $resolvedCallerRoot -ne $expectedRoot) {
        throw 'The current checkout differs from the workflow script checkout. Run the script inside the public WSPRadar website checkout, not WSPRadarApp or another checkout.'
    }
    $script:WebsiteRepositoryRoot = $resolvedScriptRoot
    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision HEAD
    Assert-WebsiteWorkingTree
    return $script:WebsiteRepositoryRoot
}

function Assert-WebsiteFile {
    param([string]$Path, [string]$Context)
    if ($Path -cnotin $script:WebsiteAllowedFiles) {
        throw "Unapproved public website file in ${Context}: '$Path'. Review it before explicitly extending WebsiteAllowedFiles; force options do not bypass this check."
    }
}

function Assert-WebsiteWorkingTree {
    # Include staged and tracked files even when ignore rules hide new files.
    # Git quotes unusual filenames; these cannot match the exact ASCII allowlist.
    $paths = @(Get-GitOutput -c core.quotepath=true ls-files --cached --others --exclude-standard)
    foreach ($path in $paths) {
        Assert-WebsiteFile -Path $path -Context 'working tree or index'
        $localPath = Join-Path $script:WebsiteRepositoryRoot $path
        if (Test-Path -LiteralPath $localPath) {
            $item = Get-Item -LiteralPath $localPath -Force
            if ($item.PSIsContainer) { throw "Expected a regular website file: '$path'." }
            # Check parent directories too: an allowed filename below a junction
            # must not silently stage content from outside the website checkout.
            while ($item.FullName -ne $script:WebsiteRepositoryRoot) {
                if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw "Symbolic links and junctions are forbidden in website content: '$path'."
                }
                $parentPath = Split-Path -Parent $item.FullName
                if ([string]::IsNullOrWhiteSpace($parentPath)) { throw 'Cannot resolve the website file parent.' }
                $item = Get-Item -LiteralPath $parentPath -Force
            }
        }
    }
    foreach ($entry in @(Get-GitOutput -c core.quotepath=true ls-files --stage)) {
        if ($entry -notmatch '^(100644|100755) [0-9a-f]+ [0-3]\t(.+)$') {
            throw 'The website index contains an unsupported entry; symbolic links and submodules are forbidden.'
        }
        Assert-WebsiteFile -Path $Matches[2] -Context 'index'
    }
}

function Assert-WebsiteHistory {
    param([Parameter(Mandatory = $true)][string]$Revision)
    # A truncated or replaced graph cannot prove which history will be public.
    if ((Get-GitOutput rev-parse --is-shallow-repository) -ne 'false') {
        throw 'A complete, non-shallow website history is required.'
    }
    if (@(Get-GitOutput for-each-ref '--format=%(refname)' refs/replace/).Count -gt 0 -or
        (Test-Path -LiteralPath (Get-WebsiteGitPath 'info/grafts'))) {
        throw 'Git replacement refs and grafts are forbidden in the website workflow.'
    }
    $commit = (Get-GitOutput rev-parse --verify "$Revision^{commit}" | Select-Object -First 1).Trim()
    $roots = @(Get-GitOutput rev-list --max-parents=0 $commit)
    if ($roots.Count -ne 1 -or $roots[0] -cne $script:WebsiteRepositoryPolicy.RootCommit) {
        throw "Unapproved website history at '$Revision'. Its sole root must be the original public website commit; application or unrelated history is forbidden."
    }
    # Check every reachable tree, not just the tip: deleted files are still public
    # in Git history. Identical immutable trees need inspection only once per run.
    $trees = @(Get-GitOutput log --format=%T --no-decorate --no-show-signature $commit -- | Select-Object -Unique)
    foreach ($tree in $trees) {
        if ($tree -notmatch '^[0-9a-f]{40,64}$') { throw 'Cannot verify a website history tree.' }
        if ($script:WebsiteCheckedTrees.ContainsKey($tree)) { continue }
        foreach ($entry in @(Get-GitOutput -c core.quotepath=true ls-tree -r --full-tree $tree)) {
            if ($entry -notmatch '^(100644|100755) blob [0-9a-f]+\t(.+)$') {
                throw 'Website history contains an unsupported entry; symbolic links and submodules are forbidden.'
            }
            Assert-WebsiteFile -Path $Matches[2] -Context "history at $Revision"
        }
        $script:WebsiteCheckedTrees[$tree] = $true
    }
}

function Fetch-WebsiteBranches {
    param([switch]$IncludeMain)
    $refspecs = @('+refs/heads/temp:refs/remotes/origin/temp')
    if ($IncludeMain) { $refspecs += '+refs/heads/main:refs/remotes/origin/main' }
    Assert-WebsiteRepository
    try {
        Invoke-Git fetch --no-tags --no-prune --no-prune-tags --no-recurse-submodules --refmap= origin @refspecs
    } catch {
        throw 'Could not fetch the required website branches. GitHub temp (and main for release) must already exist. Complete the reviewed one-time branch setup, or resolve the reported network/authentication error, then retry.'
    }
    Assert-WebsiteHistory -Revision refs/remotes/origin/temp
    if ($IncludeMain) { Assert-WebsiteHistory -Revision refs/remotes/origin/main }
}

function Get-WebsiteGitPath {
    param([string]$Name)
    return (Get-GitOutput rev-parse --path-format=absolute --git-path $Name | Select-Object -First 1).Trim()
}

function Assert-NoWebsiteGitOperation {
    foreach ($state in @('rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'sequencer')) {
        if (Test-Path -LiteralPath (Get-WebsiteGitPath $state)) {
            throw "A Git operation is in progress ($state). Complete or explicitly abort it before continuing."
        }
    }
}
