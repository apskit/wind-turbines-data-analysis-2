import json


def load_column_mapping(dataset_name: str) -> dict:
    path = "config/signals_dict.json"

    with open(path, "r", encoding="utf-8") as signals_dict:
        mappings = json.load(signals_dict)
        
    return mappings.get(dataset_name.lower(), {})


def load_signal_ranges() -> dict[str, list[float]]:
    path = "config/signals_ranges.json"

    with open(path, "r", encoding="utf-8") as signals_ranges:
        ranges = json.load(signals_ranges)

    return ranges