import numpy as np
import pandas as pd


class AnomalyDetector:
    def __init__(self, dataset):
        self.dataset = dataset
        self.df = dataset.get_dataframe()

        self.masks: dict[str, pd.Series] = {}
        self.stats: dict[str, dict] = {}


    def detect_outliers_iqr(self, factor: float = 1.5) -> tuple[pd.Series, pd.DataFrame]:
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


    def detect_isolation_forest(self) -> pd.Series:
        pass


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
