from pathlib import Path
import pandas as pd
from sklearn.impute import KNNImputer

from utils.file_handler import load_column_mapping, load_signal_ranges


class BaseLoader:
    def __init__(self, path, dataset_type, columns_to_keep=None):
        self.path = Path(path)
        self.dataset_type = dataset_type
        self.columns_to_keep = columns_to_keep


    def load_all(self) -> pd.DataFrame:
        pass


    def standarize_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        mapping = load_column_mapping(self.dataset_type)

        df = self.unify_signal_names(df, mapping)
        df = self.mark_invalid_data(df)
        df = self.add_anomaly_column(df)
        df = self.fill_missing_values(df)

        return df


    def unify_signal_names(self, df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        return df.rename(columns=mapping)
    

    def add_anomaly_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df["anomaly"] = False
        return df


    def mark_invalid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        signals_ranges = load_signal_ranges()
        invalid_mask = pd.Series(False, index=df.index)

        for col, (min_val, max_val) in signals_ranges.items():
            if col in df.columns:
                valid_mask = df[col].notna() & (df[col] >= min_val) & (df[col] <= max_val)
                invalid_mask |= ~valid_mask

        df["is_invalid"] = invalid_mask
        return df
    

    def select_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.columns_to_keep:
            selected_columns = [col for col in self.columns_to_keep if col in dataframe.columns]
            return dataframe[selected_columns]
        
        return dataframe


    def create_imputation_mask(self, df: pd.DataFrame, max_nan_sequence_length: int) -> pd.DataFrame:
        df_to_impute_mask = pd.DataFrame(False, index=df.index, columns=df.columns)

        for col in df.select_dtypes(include='number').columns:
            is_nan = df[col].isna()

            # Next group starts when value change
            group_id = (is_nan != is_nan.shift(1)).cumsum()

            group_lengths = group_id.groupby(group_id).transform('count')

            imputation_mask = is_nan & (group_lengths <= max_nan_sequence_length)        
            df_to_impute_mask[col] = imputation_mask

        return df_to_impute_mask
    

    def fill_missing_values(self, df: pd.DataFrame, method="interpolation", n_neighbors=3, max_nan_sequence_length=3) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include='number').columns

        if method == "interpolation":
            df_imputed = df[numeric_cols].interpolate(method='linear', limit=2, limit_direction='both')

        elif method == "knn":
            imputer = KNNImputer(n_neighbors=n_neighbors, weights='distance')

            imputed_values = imputer.fit_transform(df[numeric_cols])
            df_imputed = pd.DataFrame(
                imputed_values, 
                index=df.index,
                columns=numeric_cols
            )

        imputation_mask = self.create_imputation_mask(df, max_nan_sequence_length)
        imputation_mask_numeric = imputation_mask[numeric_cols]

        for col in numeric_cols:
            df.loc[imputation_mask_numeric[col], col] = df_imputed.loc[imputation_mask_numeric[col], col]

        return df
