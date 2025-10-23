from data_loading.care_to_compare_loader import CareToCompareLoader
from .base_loader import BaseLoader
from .cubico_loader import CubicoLoader


def get_loader(dataset_name: str, path: str, columns_to_keep=None) -> BaseLoader:
    dataset_name = dataset_name.lower()

    if dataset_name == "kelmarsh":
        return CubicoLoader(path, dataset_name, columns_to_keep)
      
    elif dataset_name == "penmanshiel":
        return CubicoLoader(path, dataset_name, columns_to_keep)
    
    elif dataset_name.startswith("caretocompare"):
        return CareToCompareLoader(path, dataset_name, columns_to_keep)    
    
    else:
        raise ValueError(f"Unknown dataset type: {dataset_name}")
