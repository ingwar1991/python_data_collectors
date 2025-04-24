import yaml
import importlib
from pathlib import Path
from typing import List, Optional, Union, Any, Dict
from .base_collector import BaseCollector


VENDORS_PATH = Path(__file__).parent / 'vendors'


def get_vendor_dirs() -> List[Path]:
    return [p for p in VENDORS_PATH.iterdir() if not p.name.startswith('_') and p.is_dir()]


def get_vendor_names() -> List[str]:
    return [p.name for p in get_vendor_dirs()]


def read_yaml(filepath: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Reads and parses a YAML configuration file.

    If no path is provided, it defaults to a base 'config.yaml'
    """

    config_path: Path = Path(filepath) if filepath else Path(__file__).parent / 'config.yaml'

    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    try:
        with config_path.open('r', encoding='utf-8') as f:
            config: dict[str, Any] = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ValueError("YAML file must contain a top-level dictionary.")

            return config

    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML file: {e}")

def create_collector(collector_type: str) -> BaseCollector:
    collector_file = VENDORS_PATH / collector_type / 'collector.py'
    config_file = VENDORS_PATH / collector_type / 'config.yaml'

    if not collector_file.exists() or not config_file.exists():
        raise FileNotFoundError(f"Skipping {vendor_dir.name}: missing collector.py or config.yaml")
        print(f"Skipping {vendor_dir.name}: missing collector.py or config.yaml")

        return None

    module_path = f"app.collectors.vendors.{collector_type}.collector"

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not import collector module from {module_path}: {e}")
        print(f"Could not import collector module from {module_path}: {e}")

        return None

    try:
        CollectorClass = getattr(module, 'Collector')
    except AttributeError:
        raise AttributeError(f"Skipping {collector_type}: no 'Collector' class found")
        print(f"Skipping {collector_type}: no 'Collector' class found")

        return None

    try:
        config = read_yaml(config_file)
    except Exception as e:
        raise Exception(f"Failed to read yaml config: {config_file}: {e}")
        print(f"Failed to read yaml config: {config_file}: {e}")

        return None

#    with open(config_file, 'r') as f:
#        config = yaml.safe_load(f)

    return CollectorClass(config)


def load_all_collectors() -> List[BaseCollector]:
    collectors = []

    for vendor_dir in get_vendor_dirs():
        try:
            collector_instance = create_collector(vendor_dir.name)
            collectors.append(collector_instance)
        except Exception as e:
            print(f"failed to build collector: {e}")
            continue

    return collectors
