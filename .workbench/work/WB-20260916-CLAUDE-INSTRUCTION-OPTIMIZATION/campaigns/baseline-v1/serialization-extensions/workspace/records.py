import copy


class Record:
    KNOWN_FIELDS = frozenset({"name"})

    def __init__(self, name, extensions=None):
        self.name = name
        self.extensions = copy.deepcopy(dict(extensions or {}))

    @classmethod
    def from_dict(cls, data):
        extensions = {
            key: value for key, value in data.items() if key not in cls.KNOWN_FIELDS
        }
        return cls(data["name"], extensions)

    def to_dict(self):
        result = {"name": self.name}
        for key, value in self.extensions.items():
            if key in self.KNOWN_FIELDS:
                continue
            result[key] = copy.deepcopy(value)
        return result
