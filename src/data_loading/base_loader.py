import json
from pathlib import Path
import pandas as pd


class BaseLoader:
    def __init__(self, path, dataset_type, columns_to_keep=None):
        self.path = Path(path)
        self.dataset_type = dataset_type
        self.columns_to_keep = columns_to_keep


    def load_all(self) -> pd.DataFrame:
        pass


    def unify_signal_names(self, df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        return df.rename(columns=mapping)
    

    def load_column_mapping(self, dataset_name: str) -> dict:
        dict_path = "config/signals_dict.json"

        with open(dict_path, "r", encoding="utf-8") as signals_dict:
            mappings = json.load(signals_dict)
            
        return mappings.get(dataset_name.lower(), {})
    

    def load_signal_ranges(self) -> dict[str, list[float]]:
        path = "config/signals_ranges.json"

        with open(path, 'r', encoding="utf-8") as signals_ranges:
            ranges = json.load(signals_ranges)

        return ranges


    def add_anomaly_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df["anomaly"] = False
        return df


    def mark_invalid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        signals_ranges = self.load_signal_ranges()
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
