# Dataset Preparation & Ingestion Guide

The platform provides dedicated, modular adapters for research NetFlow datasets without imposing rigid schema uniformity.

## Supported Dataset Formats

1. **BigFlow-NIDS-V2 (Primary Dataset)**:
   - Enterprise-scale NetFlow/IPFIX dataset comprising 66,935,021 flows partitioned across 67 Parquet files (`merged_part_0.parquet` to `merged_part_66.parquet`, ~2.83 GB uncompressed).
   - 55 attributes including bi-directional throughput, packet length quantiles, inter-arrival time (IAT) statistics, TCP flags, TTL bounds, and DNS/FTP application indicators.
   - 54.67% Benign (36,596,560 flows) and 45.33% Malicious (30,338,461 flows) with 32 distinct attack categories.
   - Loaded via memory-efficient columnar streaming (`BigFlowDataLoader`) with zero out-of-memory overhead.
2. **NF-UNSW-NB15-v2**:
   - Standard NetFlow representation of the UNSW-NB15 dataset (optional legacy sample provided).
   - Key fields: `IPV4_SRC_ADDR`, `L4_SRC_PORT`, `IPV4_DST_ADDR`, `L4_DST_PORT`, `PROTOCOL`, `IN_BYTES`, `OUT_BYTES`, `IN_PKTS`, `OUT_PKTS`, `FLOW_DURATION_MILLISECONDS`, `TCP_FLAGS`, `Attack`, `Label`.
3. **NF-BoT-IoT-v2**:
   - IoT and botnet telemetry captured in standardized NetFlow format.
4. **Edge-IIoTset**:
   - Multi-layer Industrial IoT telemetry dataset with varied protocol representations.
5. **Generic CSV Adapter**:
   - Universal fallback adapter that auto-detects label columns (`attack`, `label`, `class`, `is_attack`) and maps present numeric flow metrics while setting defaults for missing dimensions.

## Ingestion Rules & Data Integrity

- **Leakage Prevention**: Identifiers (`src_ip`, `dst_ip`, `timestamp`) and ground truth labels are strictly isolated from the numerical feature matrix fed into the neural network.
- **Outlier & NaN Handling**: Infinite values (`inf`, `-inf`) and nulls are cleanly imputed using median values fitted exclusively on training splits.
- **Reproducible Partitioning**: A 70% Train / 15% Validation / 15% Test stratified split is applied to guarantee unbiased model evaluation.
