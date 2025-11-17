import time
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors


class AnomalyDetector:
    def __init__(self, dataset):
        self.dataset = dataset
        self.df = dataset.get_dataframe()

        self.masks: dict[str, pd.Series] = {}
        self.stats: dict[str, dict] = {}


    def detect_outliers_iqr(self, factor: float = 1.5) -> tuple[pd.Series, pd.DataFrame]:
        self.df = self.dataset.get_dataframe()
        num_cols = self.dataset.get_numeric_cols_list()

        anomaly_mask_rows = pd.Series(False, index=self.df.index)
        anomaly_mask_cells = pd.DataFrame(False, index=self.df.index, columns=num_cols)

        for turbine_id, group in self.df.groupby("turbine_id"):
            group_index = group.index
            df_num = group[num_cols]

            turbine_row_mask = pd.Series(False, index=group_index)
            turbine_cell_mask = pd.DataFrame(False, index=group_index, columns=num_cols)

            for col in df_num.columns:
                series = df_num[col]

                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1

                lower_bound = q1 - factor * iqr
                upper_bound = q3 + factor * iqr

                col_mask = (series < lower_bound) | (series > upper_bound)
                
                turbine_row_mask |= col_mask
                turbine_cell_mask[col] = col_mask

            anomaly_mask_rows.loc[group_index] = anomaly_mask_rows.loc[group_index] | turbine_row_mask
            anomaly_mask_cells.loc[group_index, :] = turbine_cell_mask

        self.df["anomaly"] |= anomaly_mask_rows

        self.masks["iqr_row"] = anomaly_mask_rows
        self.masks["iqr_cell"] = anomaly_mask_cells

        num_anomalies = anomaly_mask_rows.sum()
        total_rows = len(anomaly_mask_rows)

        self.stats["iqr"] = {
            "total_rows": total_rows,
            "anomalous_rows": int(num_anomalies),
            "percentage_anomalous_rows": float(num_anomalies / total_rows * 100),
            "anomalous_cells": int(anomaly_mask_cells.sum().sum()),
            "factor": factor
        }

        return anomaly_mask_rows, anomaly_mask_cells


    def detect_isolation_forest(self, contamination: float = 0.01) -> tuple[pd.Series, pd.DataFrame]:
        self.df = self.dataset.get_dataframe()
        num_cols = self.dataset.get_numeric_cols_list()
        anomaly_mask_rows = pd.Series(False, index=self.df.index)
        anomaly_mask_cells = pd.DataFrame(False, index=self.df.index, columns=num_cols)
        
        for turbine_id, group in self.df.groupby("turbine_id"):
            group_index = group.index
            input_sample = group[num_cols]
            # input_sample = input_sample.fillna(input_sample.median())

            model = IsolationForest(
                contamination=contamination, # 'auto'
                random_state=42,
                n_estimators=200,
                bootstrap=False,
                )
            
            preds = model.fit_predict(input_sample)
            
            row_mask = pd.Series(preds == -1, index=group_index)
            anomaly_mask_rows.loc[group_index] |= row_mask

            cell_mask_local = pd.DataFrame(False, index=group_index, columns=num_cols)
            cell_mask_local.loc[row_mask.index[row_mask], :] = True
            anomaly_mask_cells.loc[group_index, num_cols] = cell_mask_local[num_cols]

        self.df["anomaly"] |= anomaly_mask_rows

        self.masks["iforest_row"] = anomaly_mask_rows
        self.masks["iforest_cell"] = anomaly_mask_cells

        self.stats["iforest"] = {
            "total_rows": len(self.df),
            "anomalous_rows": int(anomaly_mask_rows.sum()),
            "percentage_anomalous_rows": float(anomaly_mask_rows.sum() / len(self.df) * 100),
            "anomalous_cells": int(anomaly_mask_cells.sum().sum()),
        }

        return anomaly_mask_rows, anomaly_mask_cells


    def estimate_eps(self, sample, min_samples):
        neighbors = NearestNeighbors(n_neighbors=min_samples)
        neighbors.fit(sample)
        distances, _ = neighbors.kneighbors(sample)
        k_dist = np.sort(distances[:, -1])

        eps = np.percentile(k_dist, 95)
        return eps


    def detect_dbscan(self, eps: float = 0.5, min_samples: int = 100) -> tuple[pd.Series, pd.DataFrame]:
        self.df = self.dataset.get_dataframe()
        num_cols = self.dataset.get_numeric_cols_list()

        anomaly_mask_rows = pd.Series(False, index=self.df.index)
        anomaly_mask_cells = pd.DataFrame(False, index=self.df.index, columns=num_cols)

        for turbine_id, group in self.df.groupby("turbine_id"):
            group_index = group.index
            input_sample = group[num_cols].copy()

            group_medians = input_sample.median().fillna(0)
            input_sample.fillna(group_medians, inplace=True)

            scaler = StandardScaler()
            input_sample = scaler.fit_transform(input_sample)

            # pca = PCA(n_components=3, random_state=42)
            pca = PCA(n_components=0.95, random_state=42)
            input_sample = pca.fit_transform(input_sample)

            n_components = pca.n_components_
            min_samples = n_components*2

            eps = self.estimate_eps(input_sample, min_samples)

            model = DBSCAN(
                eps=eps,
                min_samples=min_samples,
                n_jobs=-1
            )

            labels = model.fit_predict(input_sample)

            row_mask_series = pd.Series(labels == -1, index=group_index)
            anomaly_mask_rows.loc[group_index] = row_mask_series

            anomalous_indices = row_mask_series[row_mask_series].index       
            anomaly_mask_cells.loc[anomalous_indices, :] = True

        self.df["anomaly"] |= anomaly_mask_rows

        self.masks["dbscan_row"] = anomaly_mask_rows
        self.masks["dbscan_cell"] = anomaly_mask_cells

        self.stats["dbscan"] = {
            "total_rows": len(self.df),
            "anomalous_rows": int(anomaly_mask_rows.sum()),
            "percentage_anomalous_rows": float(anomaly_mask_rows.sum() / len(self.df) * 100),
            "anomalous_cells": int(anomaly_mask_cells.sum().sum()),
            "eps": eps,
            "min_samples": min_samples
        }

        return anomaly_mask_rows, anomaly_mask_cells


    def apply_mask(self, mask_name: str) -> int:
        if mask_name not in self.masks:
            raise ValueError(f"Mask '{mask_name}' not found in anomaly masks.")

        mask = self.masks[mask_name]

        if not mask.index.equals(self.df.index):
            raise ValueError("Mask index does not match DataFrame index.")
        
        if not all(col in self.df.columns for col in mask.columns):
            raise ValueError("Mask columns do not match DataFrame columns.")

        removed_count = int(mask.sum().sum())

        self.df.loc[:, mask.columns] = self.df.loc[:, mask.columns].mask(mask, np.nan)

        return removed_count


    def get_stats(self, mask_name: str) -> dict:
        return self.stats.get(mask_name, None)
