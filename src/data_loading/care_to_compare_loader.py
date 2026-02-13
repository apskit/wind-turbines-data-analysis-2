import pandas as pd
from .base_loader import BaseLoader

class CareToCompareLoader(BaseLoader):

    def load_all(self) -> pd.DataFrame:
        all_dfs = []
        csv_files = sorted(self.path.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files in folder: {self.path}")

        for file in csv_files:
            data_frame = pd.read_csv(
                file, 
                sep=";", 
                low_memory=False)
        
            data_frame["time_stamp"] = pd.to_datetime(data_frame["time_stamp"], format="%Y-%m-%d  %H:%M:%S", errors="coerce")
            data_frame = data_frame.dropna(subset=["time_stamp"])
            data_frame = data_frame.set_index("time_stamp")

            mapping = self.load_column_mapping(self.dataset_type)
            data_frame = self.standardize_columns(data_frame, mapping)
            data_frame = self.add_anomaly_column(data_frame)

            data_frame = self.select_columns(data_frame)
            all_dfs.append(data_frame)

        return pd.concat(all_dfs, ignore_index=False)
