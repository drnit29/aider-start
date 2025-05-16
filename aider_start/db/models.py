# Data models for aider-start database
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any  # Added Any
from datetime import datetime


@dataclass
class Flag:
    """Represents a single command-line flag and its value for a preset."""

    name: str
    value: Optional[str] = None  # Value can be None for boolean flags


@dataclass
class Preset:
    """Represents a configuration preset for aider."""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    flags: Dict[str, Optional[str]] = field(
        default_factory=dict
    )  # Stores flag_name: flag_value

    # Stores {model_name: settings_dict}
    advanced_model_settings: Dict[str, Dict[Any, Any]] = field(default_factory=dict)
    # Stores {model_name: file_path_str}
    advanced_model_settings_paths: Dict[str, str] = field(default_factory=dict)

    # Stores {model_name: metadata_dict}
    advanced_model_metadata: Dict[str, Dict[Any, Any]] = field(default_factory=dict)
    # Stores {model_name: file_path_str}
    advanced_model_metadata_paths: Dict[str, str] = field(default_factory=dict)

    # The following fields seem redundant if we use the dicts above, keeping for now if used elsewhere.
    model_settings_file: Optional[str] = (
        None  # Potentially for a default/primary settings file?
    )
    model_metadata_file: Optional[str] = (
        None  # Potentially for a default/primary metadata file?
    )

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def add_flag(self, name: str, value: Optional[str] = None):
        self.flags[name] = value
        self.updated_at = datetime.now()

    def remove_flag(self, name: str):
        if name in self.flags:
            del self.flags[name]
            self.updated_at = datetime.now()


# Example of how you might represent flag metadata if needed in models
# (though this is also planned for a separate flag_metadata table)
@dataclass
class FlagMetadata:
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    value_type: str = "string"  # E.g., "string", "boolean", "integer", "path"
    default_value: Optional[str] = None
    requires_value: bool = (
        True  # True if flag needs a value (e.g. --model name), False if standalone (e.g. --stream)
    )
    is_deprecated: bool = False
