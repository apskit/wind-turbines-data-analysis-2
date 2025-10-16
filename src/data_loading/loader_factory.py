from .base_loader import BaseLoader
from .kelmarsh_loader import KelmarshLoader


class CareToCompareLoader(BaseLoader):
    def load_all(self):
        pass

class PenmanshielLoader(BaseLoader):
    def load_all(self):
        pass

def get_loader(dataset_name: str, path: str, columns_to_keep=None) -> BaseLoader:
    dataset_name = dataset_name.lower()

    if dataset_name == "kelmarsh":
        return KelmarshLoader(path, columns_to_keep)
    
    elif dataset_name.startswith("caretocompare"):
        return CareToCompareLoader(path, columns_to_keep)
    
    elif dataset_name == "penmanshiel":
        return PenmanshielLoader(path, columns_to_keep)
    
    else:
        raise ValueError(f"Unknown dataset type: {dataset_name}")
