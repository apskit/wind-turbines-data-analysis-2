import pandas as pd


class WindFarmDataset:
    def __init__(self, data_frame: pd.DataFrame, dataset_type: str):
        self.name = dataset_type
        self.data_frame = data_frame


    def get_dataframe(self):    
        return self.data_frame
