import pytest
import importlib
import yaml
from app.collectors.utils import get_vendor_dirs, get_vendor_names, read_yaml

vendor_dirs = get_vendor_dirs()
vendor_ids = get_vendor_names()


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_has_config_yaml(vendor_dir):
    config_file = vendor_dir / "config.yaml"

    assert config_file.exists(), f"{vendor_dir.name} is missing config.yaml"


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test__config_is_yaml_and_readable(vendor_dir):
    config_file = vendor_dir / "config.yaml"
    if not config_file.exists():
        pytest.skip(f"{vendor_dir.name} has no config.yaml")

    with open(config_file, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"{vendor_dir.name} has invalid YAML: {e}")

    assert isinstance(config, dict), f"{vendor_dir.name}: config should be a dictionary"


def _open_config(vendor_dir):
    config_file = vendor_dir / "config.yaml"

    if not config_file.exists():
        pytest.skip(f"{vendor_dir.name} has no config.yaml")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        pytest.skip(f"{vendor_dir.name} config.yaml must contain a YAML dictionary")

    return config

@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_config_has_required_base_fields(vendor_dir):
    config = read_yaml(vendor_dir / "config.yaml")

    assert 'vendor_name' in config, f"{vendor_dir.name}: config.yaml missing required 'vendor_name' field"
    assert 'base_url' in config, f"{vendor_dir.name}: config.yaml missing required 'base_url' field"
    assert 'endpoint' in config, f"{vendor_dir.name}: config.yaml missing required 'endpoint' field"
    assert 'response_type' in config, f"{vendor_dir.name}: config.yaml missing required 'response_type' field"


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_config_vendor_name_matcher_dir_name(vendor_dir):
    config = read_yaml(vendor_dir / "config.yaml")

    assert config['vendor_name'] == vendor_dir.name, f"{vendor_dir.name}: config.yaml 'vendor_name' doesn't match dir name"


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_config_has_required_auth_fields(vendor_dir):
    config = read_yaml(vendor_dir / "config.yaml")

    assert 'auth_type' in config, f"{vendor_dir.name}: config.yaml missing required 'auth_type' field"

    auth_type = config['auth_type']
    match auth_type:
        case 'basic':
            missing = [field for field in ('username', 'password') if not config.get(field)]
            assert not missing, f"{vendor_dir.name}: missing fields for 'basic' auth_type: {', '.join(missing)}"

        case 'token' | 'token_bearer':
            assert config.get('token'), f"{vendor_dir.name}: missing 'token' for '{auth_type}' auth_type"

        case 'oauth':
            missing = [field for field in ('token_url', 'client_id', 'client_secret') if not config.get(field)]
            assert not missing, f"{vendor_dir.name}: missing fields for 'oauth' auth_type: {', '.join(missing)}"

        case _:
            pytest.fail(f"{vendor_dir.name}: unknown auth_type '{auth_type}'")


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_has_collector_class(vendor_dir):
    collector_file = vendor_dir / "collector.py"

    assert collector_file.exists(), f"{vendor_dir.name} is missing collector.py"

    module_path = f"app.collectors.vendors.{vendor_dir.name}.collector"
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        pytest.fail(f"{vendor_dir.name}: Failed to import collector module: {e}")

    assert hasattr(module, "Collector"), f"{vendor_dir.name}: 'Collector' class not found"


@pytest.mark.parametrize("vendor_dir", vendor_dirs, ids=vendor_ids)
def test_collector_instantiation(vendor_dir):
    collector_file = vendor_dir / "collector.py"

    if not collector_file.exists():
        pytest.skip(f"{vendor_dir.name} is missing collector.py or config.yaml")

    module_path = f"app.collectors.vendors.{vendor_dir.name}.collector"

    try:
        module = importlib.import_module(module_path)
        CollectorClass = getattr(module, "Collector")
    except Exception as e:
        pytest.skip(f"{vendor_dir.name}: Cannot import or find Collector: {e}")

    config = read_yaml(vendor_dir / "config.yaml")
    try:
        _ = CollectorClass(config)
    except Exception as e:
        pytest.fail(f"{vendor_dir.name}: Collector instantiation failed: {e}")
