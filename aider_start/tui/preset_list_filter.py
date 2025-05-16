from typing import List, Any, Optional
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.widgets import TextArea


def update_filtered_list(
    filter_text_area: TextArea,
    original_display_items: List[str],
    original_descriptions: List[str],
    original_presets_plus_marker_obj: List[Any],
    CREATE_NEW_PRESET_MARKER: str,
    filtered_display_items: List[str],
    filtered_descriptions: List[str],
    filtered_presets_plus_marker_obj: List[Any],
    selected_index_ref: List[int],
    app_ref: dict,
):
    """
    Atualiza as listas filtradas de acordo com o termo de filtro.
    selected_index_ref deve ser uma lista de um elemento (para mutabilidade).
    """
    filter_term = filter_text_area.text.lower()

    new_display_items = []
    new_descriptions = []
    new_presets_obj = []

    for i, name in enumerate(original_display_items):
        desc = original_descriptions[i]
        preset_obj = original_presets_plus_marker_obj[i]
        desc_lower = desc.lower() if desc else ""
        if (
            (filter_term in name.lower())
            or (desc and filter_term in desc_lower)
            or (
                name == CREATE_NEW_PRESET_MARKER
                and (not filter_term or filter_term in CREATE_NEW_PRESET_MARKER.lower())
            )
        ):
            new_display_items.append(name)
            new_descriptions.append(desc)
            new_presets_obj.append(preset_obj)

    filtered_display_items[:] = new_display_items
    filtered_descriptions[:] = new_descriptions
    filtered_presets_plus_marker_obj[:] = new_presets_obj

    # Ajusta o índice selecionado
    selected_index_ref[0] = min(
        max(0, selected_index_ref[0]),
        len(filtered_display_items) - 1 if filtered_display_items else 0,
    )

    if app_ref.get("app") and hasattr(app_ref["app"], "invalidate"):
        app_ref["app"].invalidate()


def get_formatted_presets_text(
    filtered_display_items: List[str],
    filtered_descriptions: List[str],
    filtered_presets_plus_marker_obj: List[Any],
    selected_index: int,
    filter_text_area: TextArea,
    CREATE_NEW_PRESET_MARKER: str,
) -> FormattedText:
    result = []
    for i, item_name in enumerate(filtered_display_items):
        is_create_option = item_name == CREATE_NEW_PRESET_MARKER
        line_style = "class:selected" if i == selected_index else ""
        display_name_formatted: Any
        if is_create_option:
            display_name_formatted = (
                "class:key" if i != selected_index else "class:selected",
                f"  {item_name}\n",
            )
        else:
            display_name_formatted = (line_style, f"  {item_name}\n")
        result.append(display_name_formatted)

        if i < len(filtered_descriptions):
            current_description = filtered_descriptions[i]
            if current_description:
                desc_style = (
                    "class:description" if i != selected_index else "class:selected"
                )
                result.append((desc_style, f"    {current_description}\n"))
        result.append(("", "\n"))
    if not filtered_display_items:
        result.append(
            (
                "",
                (
                    "Nenhum preset corresponde ao seu filtro."
                    if filter_text_area.text
                    else "Nenhum preset disponível. Pressione 'C' para criar."
                ),
            )
        )
    return FormattedText(result)
