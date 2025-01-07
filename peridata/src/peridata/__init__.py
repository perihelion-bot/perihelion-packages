import os, json, copy
from typing import Any, Dict, List, TypeVar, Generic, Type
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class Property(Generic[T]):
    """
    A property that should be saved.
    """
    default: T
    protected: bool = field(default=False)

    @property
    def type(self) -> Type[T]:
        return type(self.default)

class PersistentStorage:
    """
    Handles data like a dictionary. You cannot write new keys, but setting pre-existing keys and getting them works.

    For writes that shouldn't bypass protection, use `write_unprivileged()` to throw when trying to protected values.
    """
    def __init__(self, property_list: Dict[str, Property[Any]], file_path: str | bytes | os.PathLike):
        self.property_list = property_list
        self.file_path = file_path
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                properties = json.load(f)
            # Check for and add any new fields
            updated = False
            for key, value in self.property_list.items():
                if key not in properties:
                    properties[key] = copy.deepcopy(value.default)
                    updated = True
            if updated:
                self._save_data(properties)
            return properties
        else:
            # Create new entity with default properties
            properties = {k: copy.deepcopy(v.default) for k, v in self.property_list.items()}
            self._save_data(properties)
            return properties

    def _save_data(self, properties: Dict[str, Any]) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(properties, f, indent=2)

    def save_to_disk(self) -> None:
        """Directly save the data to disk."""
        self._save_data(self._data)
    
    def __getitem__(self, key: str) -> Any:
        if key not in self.property_list:
            raise KeyError(f"Invalid property: {key}")
        return self._data[key]

    def __setitem__(self, key: str, value: object) -> None:
        if key not in self.property_list:
            raise KeyError(f"Invalid property: {key}")

        expected_type = self.property_list[key].type
        if not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for property '{key}'. Expected {expected_type.__name__}, got {type(value).__name__}")

        self._data[key] = value
        self._save_data(self._data)

    def write_unprivileged(self, key: str, value: object) -> None:
        """Same as a direct write, but protected data fails to write."""
        if key not in self.property_list:
            raise KeyError(f"Invalid property: {key}")

        expected_type = self.property_list[key].type
        if not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for property '{key}'. Expected {expected_type.__name__}, got {type(value).__name__}")

        if self.property_list[key].protected:
            raise PermissionError(f"The property '{key}' is protected and cannot be modified from write_unprivileged().")

        self._data[key] = value
        self._save_data(self._data)

    def get_available_data_keys(self, bypass_locked: bool = True) -> List[str]:
        """Gets all keys of the PersistentStorage instance."""
        if bypass_locked:
            return list(self.property_list.keys())
        else:
            return [key for key, value in self.property_list.items() if not value.protected]

    def get_data_type(self, property: str) -> type:
        """Gets the type of a property by its name."""
        if property not in self.property_list:
            raise KeyError(f"Invalid property: {property}")
        return self.property_list[property].type

    def get_data(self) -> Dict[str, Any]:
        """Gets a direct copy of the data in dictionary form."""
        return self._data.copy()

    def clear_data(self, overwrite_protected: bool = True) -> None:
        """Clear the entire dictionary (or non-protected only with overwrite_protected set to false)."""
        if overwrite_protected:
            # Create new entity with default properties
            properties = {k: copy.deepcopy(v.default) for k, v in self.property_list.items()}
            self._save_data(properties)
            return
        with open(self.file_path, 'r') as f:
            properties = json.load(f)
        for key, value in self.property_list.items(): # overwrite_protected is false here so we just clear
            if not value.protected:
                properties[key] = copy.deepcopy(value.default)
        self._save_data(properties)
        return

