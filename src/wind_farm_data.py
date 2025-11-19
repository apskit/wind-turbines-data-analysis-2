import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster

from utils.file_handler import load_signal_ranges


class WindFarmDataset:
    def __init__(self, data_frame: pd.DataFrame, dataset_type: str):
        self.name = dataset_type
        self.data_frame = data_frame
        self.normalized_data_frame = None
        self.correlation_matrix = None
        self.id_cols = ["turbine_id", "record_id", "status_type_id"]
        self.core_features = ["timestamp", "turbine_id", "is_invalid", "event"]


    def get_dataframe(self) -> pd.DataFrame:    
        return self.data_frame
    

    def get_dataframe_normalized(self) -> pd.DataFrame:    
        return self.normalized_data_frame
    

    def get_turbines_list(self) -> list:
        return self.data_frame["turbine_id"].unique().tolist()
    

    def get_numeric_cols_list(self) -> list[str]:
        num_cols = self.data_frame.select_dtypes(include=[np.number]).columns
        num_cols = [col for col in num_cols if col not in self.id_cols]
        
        return num_cols
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        return self.correlation_matrix


    def analyze_availability(self) -> pd.DataFrame:
        df = self.data_frame
        analysis_results = []

        group_col = "turbine_id"
        groups = df.groupby(group_col)

        for turbine_id, turbine_data in groups:
            total_parameters = len(turbine_data.columns)
            missing_values = turbine_data.isna().sum().sum()

            total_values = turbine_data.size
            missing_percent = 100 * missing_values / total_values

            total_datapoints = len(turbine_data)

            invalid_datapoints = (turbine_data["is_invalid"]).sum()
            invalid_percent = 100 * invalid_datapoints / total_datapoints

            first_timestamp = turbine_data.index[0]
            last_timestamp = turbine_data.index[-1]

            expected_datapoints = int((first_timestamp - last_timestamp) / np.timedelta64(10, 'm')) * (-1) + 1
            uptime_percent = 100 * total_datapoints / expected_datapoints

            analysis_results.append({
                "turbine_id": turbine_id,
                "first_timestamp": first_timestamp,
                "last_timestamp": last_timestamp,
                "sampling_frequency_min": 10,
                "parameters": total_parameters,   
                "missing_values_%": round(missing_percent, 2),
                "datapoints": total_datapoints,
                "data_uptime_%": round(uptime_percent, 2),
                "invalid_datapoints_%": round(invalid_percent, 2)
            })

        return pd.DataFrame(analysis_results)


    def analyze_variable_ranges(self, turbine_id: str | None = None) -> pd.DataFrame:
        df = self.data_frame

        if turbine_id and turbine_id.lower() != "all":
            df = df[df["turbine_id"] == int(turbine_id)]

        num_cols = self.get_numeric_cols_list()
        df_numbers = df[num_cols]
        variable_ranges = df_numbers.describe().transpose()
        variable_ranges = variable_ranges[["min", "max", "mean", "std"]]
        variable_ranges.reset_index(inplace=True)
        variable_ranges.rename(columns={"index": "parameter"}, inplace=True)
        return variable_ranges


    def analyze_overview(self, turbine_id: str | None = None) -> dict:
        overview = {
            "availability_and_time_ranges": self.analyze_availability(),
            "variable_ranges": self.analyze_variable_ranges(turbine_id),
        }
        return overview
    

    def create_outliers_mask(self):
        df = self.data_frame
        signals_ranges = load_signal_ranges()
        self.outliers_mask = pd.DataFrame(False, index=df.index, columns=df.columns)

        for col, (min_val, max_val) in signals_ranges.items():
            if col in df.columns:
                valid_mask = df[col].notna() & (df[col] >= min_val) & (df[col] <= max_val)
                self.outliers_mask[col] = ~valid_mask
    

    def normalize_data(self, normalization_type: str):
        self.create_outliers_mask()

        df_scaled = self.data_frame.copy()
        num_cols = self.get_numeric_cols_list()

        for col in num_cols:
            outlier_mask = self.outliers_mask[col]
            df_scaled.loc[outlier_mask, col] = np.nan

        if (normalization_type == "robust"):
            for col in num_cols:
                col_vals = df_scaled[col]
                mask_valid = (~col_vals.isna())

                median = col_vals[mask_valid].median()
                q1 = col_vals[mask_valid].quantile(0.25)
                q3 = col_vals[mask_valid].quantile(0.75)
                iqr = q3 - q1
                if iqr == 0:
                    iqr = col_vals[mask_valid].std()

                df_scaled.loc[mask_valid, col] = (col_vals[mask_valid] - median) / iqr

        elif (normalization_type == "z_score"):
            for col in num_cols:
                col_vals = df_scaled[col]
                mask_valid = (~col_vals.isna())

                mean = col_vals[mask_valid].mean()
                std = col_vals[mask_valid].std()
                if std == 0:
                    continue

                df_scaled.loc[mask_valid, col] = (col_vals[mask_valid] - mean) / std

        elif (normalization_type == "min_max"):
            for col in num_cols:
                col_vals = df_scaled[col]
                mask_valid = (~col_vals.isna())

                min_val = col_vals[mask_valid].min()
                max_val = col_vals[mask_valid].max()

                df_scaled.loc[mask_valid, col] = (
                    (col_vals[mask_valid] - min_val) / (max_val - min_val)
                )

        else:
            raise ValueError(f"Unknown normalization type: {normalization_type}")

        self.normalized_data_frame = df_scaled

    
    def set_correlation_matrix(self, method: str = "pearson"):
        if method == "pearson":
            num_cols = self.get_numeric_cols_list()
            self.correlation_matrix = self.data_frame[num_cols].corr(method=method, min_periods=500)


    def remove_correlated_signals(self, threshold: float = 0.95, preview: bool = True):
        numeric_cols = self.get_numeric_cols_list()
        df = self.data_frame[numeric_cols].copy()
        cols = df.columns

        if not isinstance(self.correlation_matrix, pd.DataFrame) or self.correlation_matrix.empty:
            self.set_correlation_matrix()

        corr = self.get_correlation_matrix().abs()

        corr = corr.dropna(axis=0, how='all').dropna(axis=1, how='all')
        corr = corr.fillna(0)
        np.fill_diagonal(corr.values, 1.0)
        cols = corr.columns

        # passing hierarchical clustering
        dist_matrix = 1 - corr
        np.fill_diagonal(dist_matrix.values, 0.0)

        # upper triangle
        condensed = dist_matrix.values[np.triu_indices_from(dist_matrix.values, k=1)]
        condensed[condensed < 0] = 0

        linkage_matrix = linkage(condensed, method='average')

        # clusters forming
        cluster_labels = fcluster(linkage_matrix, t=1 - threshold, criterion='distance')

        representatives = []
        to_remove = []
        representatives_map = {}

        for cluster_id in np.unique(cluster_labels):
            members = cols[cluster_labels == cluster_id].tolist()

            if len(members) == 1:
                representatives.append(members[0])
                continue

            # best signal choice
            sub_df = df[members]

            # highest variance
            rep = sub_df.var().idxmax()

            to_remove_in_cluster = [c for c in members if c != rep]
            representatives_map[rep] = to_remove_in_cluster

            representatives.append(rep)
            to_remove.extend([c for c in members if c != rep])

        result = {
            "n_clusters": len(np.unique(cluster_labels)),
            "representatives_map": representatives_map,
            "representatives": representatives,
            "to_remove": to_remove,
            "threshold": threshold
        }

        if not preview:
            to_remove = [c for c in to_remove if c not in self.core_features]
            self.data_frame.drop(columns=to_remove, inplace=True)

        return result
