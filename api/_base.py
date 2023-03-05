import json
from enum import Enum
from typing import Tuple
from dataclasses import dataclass, fields, Field, asdict
from queue import SimpleQueue


class _ZbxMethod(Enum):
    version = 'appinfo.version'
    login = 'user.login'
    logout = 'user.logout'
    get_user = 'user.get'
    create_user = 'user.create'
    delete_user = 'user.delete'
    update_user = 'user.update'


@dataclass
class ZabbixEntity:
    def __post_init__(self):
        obj_fields: Tuple[Field, ...] = fields(self)
        for f in obj_fields:
            if isinstance(f.type, type) and issubclass(f.type, Enum):
                setattr(self, f.name, f.type(getattr(self, f.name)).value)

    def __prepare_for_dump(self, entity_dict) -> dict:
        result = {}

        for key in entity_dict:
            if isinstance(entity_dict[key], dict):
                entity_dict[key] = self.__prepare_for_dump(entity_dict[key])
            if entity_dict[key] is not None:
                if isinstance(key, Enum):
                    result[key.value] = entity_dict[key]
                else:
                    result[key] = entity_dict[key]

        return result

    def dump(self):
        entity_dict = self.__prepare_for_dump(asdict(self))
        return json.dumps(entity_dict, default=lambda x: x.value)


@dataclass
class _ZbxRequest(ZabbixEntity):
    method: _ZbxMethod
    params: object = None
    jsonrpc: str = '2.0'
    id: str = '1'
    auth: str = None
