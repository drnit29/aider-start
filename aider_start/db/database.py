# Central DB API for aider-start

from .database_connection import (
    get_default_db_path,
    get_db_connection,
    setup_database,
)

from .database_presets import (
    create_preset,
    add_flag_to_preset,
    get_preset_by_id,
    list_presets,
    update_preset_details,
    delete_preset,
    delete_flag_from_preset,
    # Add re-exports for advanced settings functions
    add_or_update_model_settings,
    get_model_settings,
    add_or_update_model_metadata,
    get_model_metadata,
    get_all_advanced_settings_for_preset,
    delete_model_settings,  # Added
    delete_model_metadata,  # Added
)

from .database_flag_metadata import (
    populate_flag_metadata,
    get_flag_metadata,
    get_all_flag_metadata,
    update_flag_wizard_visibility,  # Added
)
