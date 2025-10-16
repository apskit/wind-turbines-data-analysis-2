import re
import pandas as pd
from .base_loader import BaseLoader


class KelmarshLoader(BaseLoader):
    column_mapping = {
        "Date and time": "timestamp",
        "Wind speed (m/s)": "wind_speed",
    }

    def load_all(self) -> pd.DataFrame:
        all_dfs = []
        csv_files = self.path.glob("*.csv")

        if not csv_files:
            raise FileNotFoundError(f"No CSV files in folder: {self.path}")

        for file in csv_files:
            if "Data" in file.name:
                turbine_number = re.search(r'(\d+)', file.stem)
                turbine_id = turbine_number.group(1) if turbine_number else "unknown"

                data_frame = pd.read_csv(
                    file,
                    skiprows=9,
                    low_memory=False,
                    index_col="# Date and time"
                )

                data_frame.index = pd.to_datetime(data_frame.index, utc=True, errors='coerce')
                data_frame = data_frame[data_frame["Data Availability"] == 1]
                data_frame = data_frame.dropna(axis=1, how='all')

                data_frame = self.standardize_columns(data_frame, self.column_mapping)
                data_frame = self.add_anomaly_column(data_frame)
                data_frame["turbine_id"] = f"T{int(turbine_id):02d}"

                data_frame = self.select_columns(data_frame)
                all_dfs.append(data_frame)

        return pd.concat(all_dfs, ignore_index=False)
