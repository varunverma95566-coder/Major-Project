"""BigFlow-NIDS-V2 Unified Dataset Loader.

Memory-efficient, partition-aware data loader for BigFlow-NIDS-V2 Parquet and CSV files.
Discovers numbered Parquet partitions, streams records in manageable batches,
validates schemas, preserves attack label distributions, and prevents memory exhaustion.
"""

import os
import re
import glob
import logging
from typing import List, Dict, Any, Optional, Iterator, Tuple
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from app.core.config import settings

logger = logging.getLogger(__name__)

# Essential columns expected in BigFlow-NIDS-V2
REQUIRED_BIGFLOW_COLUMNS = [
    "FLOW_DURATION_MILLISECONDS",
    "IN_BYTES",
    "OUT_BYTES",
    "IN_PKTS",
    "OUT_PKTS",
    "PROTOCOL",
    "L4_DST_PORT",
    "TCP_FLAGS",
    "Label",
    "Attack",
]


class BigFlowDataLoader:
    """Unified logical loader for BigFlow-NIDS-V2 partitioned Parquet dataset."""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or settings.BIGFLOW_NIDS_PARQUET_DIR
        self.parquet_files: List[str] = []
        self.is_csv: bool = False
        self.csv_path: Optional[str] = None
        self._discover_dataset()

    def _discover_dataset(self) -> None:
        """Safely discovers and orders Parquet partitions or verifies CSV fallback."""
        if not self.data_path:
            logger.warning("No dataset path configured for BigFlowDataLoader.")
            return

        # Resolve relative to BASE_DIR if needed
        resolved_path = self.data_path
        if not os.path.isabs(resolved_path) and not os.path.exists(resolved_path):
            candidate = os.path.join(settings.BASE_DIR, resolved_path)
            if os.path.exists(candidate):
                resolved_path = candidate
        self.data_path = resolved_path

        if os.path.isdir(self.data_path):
            # Discover merged_part_*.parquet files
            all_files = glob.glob(os.path.join(self.data_path, "merged_part_*.parquet"))
            # Sort numerically by part index
            def extract_index(filepath: str) -> int:
                match = re.search(r"merged_part_(\d+)\.parquet", os.path.basename(filepath))
                return int(match.group(1)) if match else 999999

            self.parquet_files = sorted(all_files, key=extract_index)
            self.is_csv = False
            logger.info(f"BigFlowDataLoader discovered {len(self.parquet_files)} parquet partitions in {self.data_path}")

        elif os.path.isfile(self.data_path):
            if self.data_path.endswith(".parquet"):
                self.parquet_files = [self.data_path]
                self.is_csv = False
            elif self.data_path.endswith(".csv"):
                self.is_csv = True
                self.csv_path = self.data_path
                self.parquet_files = []
                logger.info(f"BigFlowDataLoader configured with CSV file: {self.data_path}")

        # If empty folder and CSV fallback is available, check CSV path
        if not self.parquet_files and not self.is_csv:
            csv_candidate = settings.BIGFLOW_NIDS_CSV_PATH
            if not os.path.isabs(csv_candidate) and not os.path.exists(csv_candidate):
                candidate = os.path.join(settings.BASE_DIR, csv_candidate)
                if os.path.exists(candidate):
                    csv_candidate = candidate
            if os.path.exists(csv_candidate):
                logger.info(f"Parquet files not found in {self.data_path}, using CSV fallback: {csv_candidate}")
                self.is_csv = True
                self.csv_path = csv_candidate

    def get_dataset_summary(self) -> Dict[str, Any]:
        """Reads metadata across partitions without loading entire dataset into memory."""
        if not self.parquet_files and not self.is_csv:
            return {
                "status": "not_found",
                "message": f"BigFlow-NIDS dataset not found at {self.data_path}",
                "total_files": 0,
                "total_rows": 0,
                "total_size_bytes": 0,
                "columns": [],
                "format": "none",
            }

        if self.parquet_files:
            total_rows = 0
            total_size_bytes = 0
            for f in self.parquet_files:
                try:
                    meta = pq.read_metadata(f)
                    total_rows += meta.num_rows
                    total_size_bytes += os.path.getsize(f)
                except Exception as e:
                    logger.warning(f"Error reading metadata for {f}: {e}")

            # Inspect first file schema
            first_file = self.parquet_files[0]
            schema = pq.ParquetFile(first_file).schema_arrow
            columns = [
                {"name": name, "dtype": str(schema.field(name).type)}
                for name in schema.names
            ]

            return {
                "status": "ready",
                "format": "parquet_partitioned",
                "dataset_name": "BigFlow-NIDS-V2",
                "data_path": self.data_path,
                "total_files": len(self.parquet_files),
                "total_rows": total_rows,
                "total_size_bytes": total_size_bytes,
                "columns": columns,
                "primary_partitions": [os.path.basename(f) for f in self.parquet_files[:5]],
            }

        # CSV fallback summary
        if self.is_csv and self.csv_path and os.path.exists(self.csv_path):
            size_bytes = os.path.getsize(self.csv_path)
            # Read header only
            header_df = pd.read_csv(self.csv_path, nrows=5)
            columns = [{"name": c, "dtype": str(header_df[c].dtype)} for c in header_df.columns]
            return {
                "status": "ready",
                "format": "csv_large",
                "dataset_name": "BigFlow-NIDS-V2",
                "data_path": self.csv_path,
                "total_files": 1,
                "total_rows": -1,  # Full scan would be slow on 14GB CSV
                "total_size_bytes": size_bytes,
                "columns": columns,
            }

        return {"status": "error", "message": "Unable to determine dataset summary"}

    def validate_schema(self, columns: List[str]) -> Tuple[bool, List[str]]:
        """Validates that all essential columns are present."""
        cols_lower = {str(c).lower(): str(c) for c in columns}
        missing = []
        for req in REQUIRED_BIGFLOW_COLUMNS:
            if req.lower() not in cols_lower:
                missing.append(req)
        return (len(missing) == 0, missing)

    def load_stratified_sample(
        self,
        sample_size: int = 10000,
        random_state: int = 42,
        max_files_to_sample: int = 20,
    ) -> pd.DataFrame:
        """Loads a representative stratified sample across partitions without RAM explosion.

        Reads a proportional number of records across multiple Parquet partitions,
        retaining both binary (benign/malicious) and multiclass attack diversity.
        """
        if not self.parquet_files:
            if self.is_csv and self.csv_path:
                logger.info(f"Loading sample from CSV with chunksize: {self.csv_path}")
                return self._load_sample_from_csv(sample_size, random_state)
            raise FileNotFoundError(f"No BigFlow-NIDS parquet partitions found in {self.data_path}")

        files_to_use = self.parquet_files[:max_files_to_sample]
        rows_per_file = max(sample_size // len(files_to_use), 50)

        np.random.seed(random_state)
        collected_chunks = []
        total_collected = 0

        for f in files_to_use:
            if total_collected >= sample_size:
                break
            try:
                # Read selected rows from partition
                pf = pq.ParquetFile(f)
                num_rows = pf.metadata.num_rows
                if num_rows == 0:
                    continue

                take_rows = min(rows_per_file * 2, num_rows)
                # Read first row group or batch
                table = pf.read_row_group(0)
                df_chunk = table.to_pandas()

                # Sample randomly from this chunk
                if len(df_chunk) > rows_per_file:
                    df_chunk = df_chunk.sample(n=rows_per_file, random_state=random_state)

                collected_chunks.append(df_chunk)
                total_collected += len(df_chunk)
            except Exception as e:
                logger.warning(f"Error reading partition {f}: {e}")

        if not collected_chunks:
            raise RuntimeError("Failed to read any data from BigFlow-NIDS partitions.")

        full_df = pd.concat(collected_chunks, ignore_index=True)
        # Drop duplicates if any
        full_df = full_df.drop_duplicates()

        # If we collected more than desired, sample down to exact sample_size
        if len(full_df) > sample_size:
            # Attempt stratified sampling if multiclass labels present
            if "Attack" in full_df.columns:
                try:
                    full_df = full_df.groupby("Attack", group_keys=False).apply(
                        lambda g: g.sample(
                            min(len(g), max(1, int(sample_size * len(g) / len(full_df)))),
                            random_state=random_state
                        )
                    )
                except Exception:
                    full_df = full_df.sample(n=sample_size, random_state=random_state)
            else:
                full_df = full_df.sample(n=sample_size, random_state=random_state)

        logger.info(f"Loaded BigFlow-NIDS sample of {len(full_df):,} records successfully.")
        return full_df.reset_index(drop=True)

    def _load_sample_from_csv(self, sample_size: int, random_state: int) -> pd.DataFrame:
        """Memory-safe chunked reader for BigFlow-NIDS-V2.csv without loading the entire 14GB."""
        chunks = []
        collected = 0
        chunksize = 20000

        for chunk in pd.read_csv(self.csv_path, chunksize=chunksize, low_memory=False):
            sample_from_chunk = chunk.sample(min(len(chunk), sample_size // 4), random_state=random_state)
            chunks.append(sample_from_chunk)
            collected += len(sample_from_chunk)
            if collected >= sample_size:
                break

        res = pd.concat(chunks, ignore_index=True)
        if len(res) > sample_size:
            res = res.sample(n=sample_size, random_state=random_state)
        return res.reset_index(drop=True)

    def stream_batches(
        self,
        batch_size: int = 10000,
        columns: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> Iterator[pd.DataFrame]:
        """Yields records in manageable batches partition-by-partition."""
        total_yielded = 0
        for f in self.parquet_files:
            if max_records and total_yielded >= max_records:
                break
            try:
                parquet_file = pq.ParquetFile(f)
                for rg_idx in range(parquet_file.num_row_groups):
                    tbl = parquet_file.read_row_group(rg_idx, columns=columns)
                    df = tbl.to_pandas()
                    for start in range(0, len(df), batch_size):
                        batch = df.iloc[start:start + batch_size]
                        yield batch
                        total_yielded += len(batch)
                        if max_records and total_yielded >= max_records:
                            return
            except Exception as e:
                logger.error(f"Error streaming from {f}: {e}")

    def get_verified_categories(self, active_model_classes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Returns all 32 verified BigFlow-NIDS attack categories with model support annotations."""
        supported_set = set(active_model_classes or [])

        # Categorization taxonomy
        def get_category_group(cat: str) -> str:
            c_low = cat.lower()
            if cat == "Benign":
                return "Benign Traffic"
            if any(k in c_low for k in ["dos", "ddos"]):
                return "DoS & DDoS"
            if any(k in c_low for k in ["brute", "password"]):
                return "Brute Force & Auth"
            if any(k in c_low for k in ["injection", "xss", "sql", "web"]):
                return "Web & Injection"
            if any(k in c_low for k in ["reconnaissance", "scanning", "analysis"]):
                return "Reconnaissance & Probes"
            return "Malware & Exploits"

        categories_info = []
        for cat, part_idx in BIGFLOW_CATEGORY_PARTITION_MAP.items():
            is_supported = (cat in supported_set) if supported_set else True
            part_name = f"merged_part_{part_idx}.parquet" if part_idx < len(self.parquet_files) else "merged_part_0.parquet"
            categories_info.append({
                "name": cat,
                "group": get_category_group(cat),
                "is_attack": (cat != "Benign"),
                "is_supported": is_supported,
                "partition_file": part_name,
                "unsupported_reason": None if is_supported else f"Active model was trained on {len(supported_set)} classes and does not natively support '{cat}'. Model retraining required."
            })

        # Sort: Benign first, then alphabetically by group and name
        categories_info.sort(key=lambda x: (0 if x["name"] == "Benign" else 1, x["group"], x["name"]))
        return categories_info

    def get_category_sample_records(
        self,
        category: str,
        limit: int = 5,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Extracts real representative flow records from BigFlow-NIDS Parquet without loading large datasets into RAM."""
        from app.datasets.adapters import BigFlow_NIDS_Adapter
        adapter = BigFlow_NIDS_Adapter()

        if not self.parquet_files:
            # Fallback for environment without parquets
            logger.warning("No parquet files available; using sample dataset generator fallback.")
            from app.datasets.sample_generator import generate_synthetic_flow
            return [generate_synthetic_flow() for _ in range(limit)]

        # Determine target partition files
        target_files = []
        if category != "ALL" and category in BIGFLOW_CATEGORY_PARTITION_MAP:
            target_idx = BIGFLOW_CATEGORY_PARTITION_MAP[category]
            if target_idx < len(self.parquet_files):
                target_files.append(self.parquet_files[target_idx])
        
        # Add primary partitions as search space if needed
        for f in self.parquet_files[:6]:
            if f not in target_files:
                target_files.append(f)

        records = []
        limit = max(1, min(limit, 25))  # Safe bounds

        for f in target_files:
            if len(records) >= limit:
                break
            try:
                if category == "ALL":
                    tbl = pq.read_table(f).slice(offset, limit * 2)
                else:
                    tbl = pq.read_table(f, filters=[("Attack", "==", category)]).slice(offset, limit * 2)

                if len(tbl) == 0:
                    continue

                df_slice = tbl.to_pandas()
                features_df, metadata_df, y_bin, y_multi = adapter.adapt(df_slice)

                for i in range(len(features_df)):
                    if len(records) >= limit:
                        break
                    flow = features_df.iloc[i].to_dict()
                    meta = metadata_df.iloc[i].to_dict()
                    flow.update(meta)
                    flow["ground_truth_attack"] = str(y_multi.iloc[i])
                    flow["ground_truth_label"] = int(y_bin.iloc[i])
                    flow["dataset_source"] = f"BigFlow-NIDS-V2 ({os.path.basename(f)})"

                    # Sanitize all values for JSON serialization and model pipeline compatibility
                    clean_flow = {}
                    for k, v in flow.items():
                        if hasattr(v, "isoformat"):
                            clean_flow[k] = v.isoformat()
                        elif pd.isna(v):
                            clean_flow[k] = None
                        elif hasattr(v, "item"):
                            clean_flow[k] = v.item()
                        else:
                            clean_flow[k] = v
                    records.append(clean_flow)
            except Exception as e:
                logger.warning(f"Error reading records from {f} for category '{category}': {e}")

        logger.info(f"Retrieved {len(records)} BigFlow-NIDS records for category '{category}'")
        return records


# Exact partition map for instant index-directed retrieval across all 32 BigFlow-NIDS categories
BIGFLOW_CATEGORY_PARTITION_MAP: Dict[str, int] = {
    'DoS': 0,
    'DDoS': 0,
    'Benign': 0,
    'injection': 0,
    'scanning': 0,
    'xss': 1,
    'password': 1,
    'Backdoor': 2,
    'ransomware': 2,
    'mitm': 2,
    'DoS_attacks-Slowloris': 3,
    'FTP-BruteForce': 3,
    'SSH-Bruteforce': 3,
    'DoS_attacks-GoldenEye': 3,
    'Reconnaissance': 3,
    'Theft': 3,
    'Brute_Force_-XSS': 4,
    'DDOS_attack-HOIC': 4,
    'DoS_attacks-SlowHTTPTest': 4,
    'DDoS_attacks-LOIC-HTTP': 4,
    'Infilteration': 4,
    'DoS_attacks-Hulk': 4,
    'DDOS_attack-LOIC-UDP': 4,
    'SQL_Injection': 4,
    'Brute_Force_-Web': 4,
    'Shellcode': 5,
    'Fuzzers': 5,
    'Analysis': 5,
    'Generic': 5,
    'Worms': 5,
    'Bot': 5,
    'Exploits': 5
}

