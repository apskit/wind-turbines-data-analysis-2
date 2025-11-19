import pandas as pd
from .base_loader import BaseLoader

class CareToCompareLoader(BaseLoader):

    def load_all(self) -> pd.DataFrame:
        all_dfs = []
        csv_files = sorted(f for f in self.path.glob("*.csv") if f.stem.isdigit())
        
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

            data_frame = self.standarize_dataset(data_frame)

            data_frame = self.select_columns(data_frame)
            all_dfs.append(data_frame)

        all_dfs = pd.concat(all_dfs, ignore_index=False)

        all_dfs["event"] = False

        event_info_path = self.path / "event_info.csv"

        if event_info_path:
            events = self.load_event_file(event_info_path)
            all_dfs = self.apply_event_labels(all_dfs, events)

        return all_dfs
    

    def load_event_file(self, path: str) -> pd.DataFrame:
        events = pd.read_csv(path, sep=";", low_memory=False)

        events["event_start"] = pd.to_datetime(events["event_start"], format="%Y-%m-%d  %H:%M:%S", errors="coerce")
        events["event_end"] = pd.to_datetime(events["event_end"], format="%Y-%m-%d  %H:%M:%S", errors="coerce")

        events.rename(columns={"asset": "turbine_id"}, inplace=True)

        return events


    def apply_event_labels(self, df: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for _, row in events.iterrows():
            if row["event_label"] != "anomaly":
                continue

            turbine_id = row["turbine_id"]
            start = row["event_start"]
            end = row["event_end"]

            mask = (
                (df["turbine_id"] == turbine_id) &
                (df.index >= start) &
                (df.index <= end)
            )

            df.loc[mask, "event"] = True

        return df

