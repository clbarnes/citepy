from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import logging

from jsonschema import Draft3Validator as Validator


logger = logging.getLogger(__name__)


class DummyValidator:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def is_valid(self, *args, **kwargs):
        return True

    def validate(self, *args, **kwargs):
        return True


# todo: remove this
Validator = DummyValidator


here = Path(__file__).absolute().parent

with open(here / 'csl-data.json') as f:
    data_schema = json.load(f)

data_validator = Validator(data_schema)

common_elements = {"$schema": data_schema["$schema"]}

item_schema = deepcopy(data_schema["items"])
item_schema.update(common_elements)
item_validator = Validator(item_schema)

type_schema = deepcopy(item_schema["properties"]["type"])
type_schema.update(common_elements)
type_validator = Validator(type_schema)

name_schema = deepcopy(item_schema["properties"]["author"]["items"]["type"][0])
name_schema.update(common_elements)
name_validator = Validator(name_schema)

date_schema = deepcopy(item_schema["properties"]["accessed"]["type"][0])
date_schema.update(common_elements)
date_validator = Validator(date_schema)
