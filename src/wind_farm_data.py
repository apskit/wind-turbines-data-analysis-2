import numpy as np
import pandas as pd


class WindFarmDataset:
    def __init__(self, data_frame: pd.DataFrame, dataset_type: str):
        self.name = dataset_type
        self.data_frame = data_frame


    def get_dataframe(self) -> pd.DataFrame:    
        return self.data_frame


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
                "data_uptime_%": round(uptime_percent, 2)
            })

        return pd.DataFrame(analysis_results)


    def analyze_variable_ranges(self, turbine_id: str | None = None) -> pd.DataFrame:
        df = self.data_frame

        if turbine_id and turbine_id.lower() != "all":
            df = df[df["turbine_id"] == int(turbine_id)]

        df_numbers = df.select_dtypes(include=[np.number])
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
    