from pathlib import Path
import pandas as pd

class BaseLoader:
    def __init__(self, path, columns_to_keep=None):
        self.path = Path(path)
        self.columns_to_keep = columns_to_keep

    def load_all(self) -> pd.DataFrame:
        pass

    def standardize_columns(self, df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        return df.rename(columns=mapping)

    def add_anomaly_column(self, df: pd.DataFrame) -> pd.DataFrame:
        df["anomaly"] = False
        return df
    
    def select_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.columns_to_keep:
            selected_columns = [col for col in self.columns_to_keep if col in dataframe.columns]
            return dataframe[selected_columns]
        
        return dataframe
