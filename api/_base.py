import json
from enum import Enum
from typing import Tuple
from dataclasses import dataclass, field, fields, Field, asdict


@dataclass
class ZabbixEntity:
    def __post_init__(self):
        obj_fields: Tuple[Field, ...] = fields(self)
        for f in obj_fields:
            if isinstance(f.type, type) and issubclass(f.type, Enum):
                setattr(self, f.name, f.type(getattr(self, f.name)).value)

    def dump(self):
        return json.dumps(asdict(self), default=lambda x: x.value)
