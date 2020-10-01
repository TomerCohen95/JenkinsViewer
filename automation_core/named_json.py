import json
from abc import ABC
from abc import ABCMeta
from enum import Enum


class NamedJson(ABC):
    """
    This is a superclass for data containers that are initialized from a JSON. Instead of parsing everything,
    just create the relevant type-hinting
    """

    def __init__(self, json_obj):
        vars(self).update(json_obj)
        for key, value in self.__dict__.items():
            if isinstance(value, dict):
                self.__setitem__(key=key, value=NamedJson(value))
            elif isinstance(value, list):
                for index, content in enumerate(value):
                    if isinstance(content, dict):
                        value[index] = NamedJson(content)

    def __getattr__(self, key: str):
        if key not in self.__dict__:
            if key.startswith('__'):
                # noinspection PyCallByClass
                return ABCMeta.__getattribute__(self.__class__, key)
            raise AttributeError(key)
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __setitem__(self, key, value):
        self.__dict__.__setitem__(key, value)

    def __ne__(self, other) -> bool:
        other = other.__dict__
        compare = self.__dict__
        for filed in other:
            if other[filed] != compare[filed]:
                return True
        return False

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return type(other) == type(self) and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.dumps(sort_keys=True))

    def dumps(self, sort_keys: bool = False):
        d = self._to_serializable()
        return json.dumps(d, sort_keys=sort_keys)

    @staticmethod
    def _serialize_item(item):
        if isinstance(item, NamedJson):
            return item._to_serializable()
        elif isinstance(item, dict):
            for key, value in item.items():
                item[key] = NamedJson._serialize_item(value)
        elif isinstance(item, list):
            for i, value in enumerate(item):
                item[i] = NamedJson._serialize_item(value)
        elif isinstance(item, Enum):
            return NamedJson._serialize_item(item.value)
        return item

    def _to_serializable(self):
        d = self.__dict__
        for key, value in d.items():
            d[key] = NamedJson._serialize_item(value)
        return d

    def is_object_matches(self, obj_to_compare: 'NamedJson') -> bool:
        self_dict = self.__dict__
        other = obj_to_compare.__dict__
        for field in self_dict:
            if self_dict[field] is not None:
                if field not in other or other[field] != self_dict[field]:  # NOSONAR Merge if statement
                    return False
        return True
