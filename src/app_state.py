class AppState:
    def __init__(self):
        self.dataset = None


    def load_dataset(self, dataset_type: str, path: str, columns_to_keep=None):
        from data_loading.loader_factory import get_loader
        from wind_farm_data import WindFarmDataset

        loader = get_loader(dataset_type, path, columns_to_keep)
        data_frame= loader.load_all()
        self.dataset = WindFarmDataset(data_frame, dataset_type=dataset_type)
        

    def get_dataset(self):    
        return self.dataset
