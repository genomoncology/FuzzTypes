import json

from fuzztype import load_source, Registry
from fuzztype.source import EntityAdapter

data = ["Apple", "Banana", "Cucumber"]
data_s = json.dumps(data)


def test_entity_adapter():
    assert EntityAdapter.validate_python(data) == data
    assert EntityAdapter.validate_json(data_s) == data


def test_load_lookup():
    load_source(data)
    assert Registry.lookup(key="apple") == "Apple"
