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


    def standardize_columns(self, df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        return df.rename(columns=mapping)
    

    def load_column_mapping(self, dataset_name: str) -> dict:
        dict_path = "config/signals_dict.json"

        with open(dict_path, "r", encoding="utf-8") as signals_dict:
            mappings = json.load(signals_dict)
            
        return mappings.get(dataset_name.lower(), {})


    def add_anomaly_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df["anomaly"] = False
        return df
    

    def select_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.columns_to_keep:
            selected_columns = [col for col in self.columns_to_keep if col in dataframe.columns]
            return dataframe[selected_columns]
        
        return dataframe
