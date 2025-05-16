import yaml
import json
from pathlib import Path


def get_user_data_dir_for_preset_configs(preset_id_for_path: int):
    try:
        from ..db.database_connection import get_default_db_path
    except ImportError:
        from aider_start.db.database_connection import get_default_db_path

    base_app_data_dir = get_default_db_path().parent
    presets_config_dir = base_app_data_dir / "presets_config" / str(preset_id_for_path)
    presets_config_dir.mkdir(parents=True, exist_ok=True)
    return presets_config_dir


def process_settings_yaml(
    settings_str, model_name, preset_id, file_handlers_module, settings_path_area
):
    final_settings_json_str = None
    final_settings_path = settings_path_area.text.strip() or None

    if settings_str.strip():
        parsed_settings = yaml.safe_load(settings_str)
        if not isinstance(parsed_settings, dict):
            raise ValueError("Settings YAML must be a dictionary (mapping).")
        final_settings_json_str = json.dumps(parsed_settings)
        if not final_settings_path:
            base_path = get_user_data_dir_for_preset_configs(preset_id)
            final_settings_path = str(base_path / f"{model_name}.model.settings.yml")
        if not file_handlers_module.save_yaml_file(
            parsed_settings, Path(final_settings_path)
        ):
            raise IOError(f"Failed to save settings YAML to {final_settings_path}")
    elif final_settings_path:
        loaded_s = file_handlers_module.load_yaml_file(Path(final_settings_path))
        if loaded_s and isinstance(loaded_s, dict):
            final_settings_json_str = json.dumps(loaded_s)
        else:
            raise ValueError(
                f"Content empty and failed to load valid YAML from {final_settings_path}"
            )
    return final_settings_json_str, final_settings_path


def process_metadata_json(
    metadata_str, model_name, preset_id, file_handlers_module, metadata_path_area
):
    final_metadata_json_str = None
    final_metadata_path = metadata_path_area.text.strip() or None

    if metadata_str.strip():
        parsed_metadata = json.loads(metadata_str)
        if not isinstance(parsed_metadata, dict):
            raise ValueError("Metadata JSON must be a dictionary (object).")
        final_metadata_json_str = json.dumps(parsed_metadata)
        if not final_metadata_path:
            base_path = get_user_data_dir_for_preset_configs(preset_id)
            final_metadata_path = str(base_path / f"{model_name}.model.metadata.json")
        if not file_handlers_module.save_json_file(
            parsed_metadata, Path(final_metadata_path)
        ):
            raise IOError(f"Failed to save metadata JSON to {final_metadata_path}")
    elif final_metadata_path:
        loaded_m = file_handlers_module.load_json_file(Path(final_metadata_path))
        if loaded_m and isinstance(loaded_m, dict):
            final_metadata_json_str = json.dumps(loaded_m)
        else:
            raise ValueError(
                f"Content empty and failed to load valid JSON from {final_metadata_path}"
            )
    return final_metadata_json_str, final_metadata_path
