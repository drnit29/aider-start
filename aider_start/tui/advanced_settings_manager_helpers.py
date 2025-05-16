from typing import Any, Optional, List, Dict, Tuple


def reload_data_for_list_view(
    database, conn, preset_id, app_ref_list, selected_model_index_list
):
    """
    Helper to load/reload data for the list view.
    Returns (preset_details_list, managed_models_info_list, selected_model_index_list) or (None, [], 0) on failure.
    """
    preset_details_list = database.get_preset_by_id(conn, preset_id)

    if not preset_details_list:
        if (
            app_ref_list.get("app")
            and hasattr(app_ref_list["app"], "is_running")
            and app_ref_list["app"].is_running
        ):
            app_ref_list["app"].exit(result=("exit_manager_due_to_error", None))
        return None, [], 0

    all_model_names = set(preset_details_list.advanced_model_settings.keys()) | set(
        preset_details_list.advanced_model_metadata.keys()
    )

    managed_models_info_list = []
    for model_name_key in sorted(list(all_model_names)):
        managed_models_info_list.append(
            {
                "name": model_name_key,
                "has_settings": model_name_key
                in preset_details_list.advanced_model_settings
                and bool(preset_details_list.advanced_model_settings[model_name_key]),
                "has_metadata": model_name_key
                in preset_details_list.advanced_model_metadata
                and bool(preset_details_list.advanced_model_metadata[model_name_key]),
                "settings_path": preset_details_list.advanced_model_settings_paths.get(
                    model_name_key
                ),
                "metadata_path": preset_details_list.advanced_model_metadata_paths.get(
                    model_name_key
                ),
            }
        )

    current_len = len(managed_models_info_list) + 1
    selected_model_index_list = (
        min(selected_model_index_list, current_len - 1) if current_len > 0 else 0
    )
    selected_model_index_list = max(0, selected_model_index_list)
    return preset_details_list, managed_models_info_list, selected_model_index_list


def get_display_items_for_list_view(managed_models_info_list, ADD_NEW_MODEL_MARKER):
    return [info["name"] for info in managed_models_info_list] + [ADD_NEW_MODEL_MARKER]


def get_formatted_text_for_list_view(
    preset_details_list,
    managed_models_info_list,
    selected_model_index_list,
    ADD_NEW_MODEL_MARKER,
    FormattedText,
):
    result = []
    display_items = get_display_items_for_list_view(
        managed_models_info_list, ADD_NEW_MODEL_MARKER
    )

    if not preset_details_list:
        result.append(
            FormattedText([("class:error", "Error: Preset details not available.")])
        )
        return FormattedText(result)

    for i, item_text in enumerate(display_items):
        is_add_new = item_text == ADD_NEW_MODEL_MARKER
        line_style = "class:selected" if i == selected_model_index_list else ""

        if is_add_new:
            result.append(
                (
                    (line_style if i == selected_model_index_list else "class:key"),
                    f"  {item_text}\n",
                )
            )
        else:
            if i < len(managed_models_info_list):
                model_info = managed_models_info_list[i]
                settings_status = (
                    "✓ Settings" if model_info["has_settings"] else "✗ Settings"
                )
                metadata_status = (
                    "✓ Metadata" if model_info["has_metadata"] else "✗ Metadata"
                )
                path_info_settings = (
                    f"(file: {model_info['settings_path']})"
                    if model_info["settings_path"]
                    else ""
                )
                path_info_metadata = (
                    f"(file: {model_info['metadata_path']})"
                    if model_info["metadata_path"]
                    else ""
                )

                result.append((line_style, f"  {model_info['name']}\n"))
                result.append(
                    (
                        line_style,
                        f"    {settings_status} {path_info_settings}\n",
                    )
                )
                result.append(
                    (
                        line_style,
                        f"    {metadata_status} {path_info_metadata}\n",
                    )
                )
            else:
                result.append(
                    (
                        line_style,
                        f"  Error: Data mismatch for item '{item_text}'\n",
                    )
                )
        result.append(("", "\n"))

    if not managed_models_info_list and (
        not display_items
        or (len(display_items) == 1 and display_items[0] == ADD_NEW_MODEL_MARKER)
    ):
        result.append(
            (
                "",
                "No advanced settings found for this preset. Press 'N' to add.",
            )
        )
    return FormattedText(result)
