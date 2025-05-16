from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import FormattedText

from .style.themes import default_style


def make_preset_list_keybindings(
    filter_text_area,
    list_body_control,
    filtered_display_items,
    filtered_presets_plus_marker_obj,
    selected_index_ref,
    app_ref,
    CREATE_NEW_PRESET_MARKER,
    filter_active_state,
):
    kb_global = KeyBindings()

    def is_filter_not_focused():
        """Check if the filter text area is not currently focused."""
        try:
            app = get_app()
            return not app.layout.has_focus(filter_text_area)
        except Exception:
            # Fallback if we can't get the app or layout
            return True

    filter_not_focused_condition = Condition(is_filter_not_focused)

    def show_status_message(app, message, duration=1.0):
        """
        Display a temporary status message.
        This function can be added to the app object for reuse.
        """
        if not hasattr(app, "_status_message"):
            app._status_message = None
            app._status_message_time = 0

        app._status_message = message
        app._status_message_time = duration
        app.invalidate()

    # Add the status message function to the app when it's available
    def ensure_app_has_status_message_func():
        app = get_app()
        if not hasattr(app, "show_message"):
            app.show_message = lambda msg, duration=1.0: show_status_message(
                app, msg, duration
            )

    # Navigation: Up
    @kb_global.add("up")
    def _(event):
        ensure_app_has_status_message_func()

        if event.app.layout.has_focus(filter_text_area):
            event.app.layout.focus(list_body_control)
            event.app.show_message("Navegação ativada", 0.5)
        else:
            old_index = selected_index_ref[0]
            selected_index_ref[0] = max(0, selected_index_ref[0] - 1)

            # Show feedback only if the selection actually changed
            if old_index != selected_index_ref[0]:
                if selected_index_ref[0] < len(filtered_display_items):
                    item_name = filtered_display_items[selected_index_ref[0]]
                    if item_name == CREATE_NEW_PRESET_MARKER:
                        event.app.show_message(
                            "Opção de criar novo preset selecionada", 0.5
                        )
                    else:
                        event.app.show_message(f"Preset '{item_name}' selecionado", 0.5)

        event.app.invalidate()

    # Navigation: Down
    @kb_global.add("down")
    def _(event):
        ensure_app_has_status_message_func()

        if event.app.layout.has_focus(filter_text_area):
            event.app.layout.focus(list_body_control)
            event.app.show_message("Navegação ativada", 0.5)
        else:
            old_index = selected_index_ref[0]
            max_index = len(filtered_display_items) - 1 if filtered_display_items else 0
            selected_index_ref[0] = min(max_index, selected_index_ref[0] + 1)

            # Show feedback only if the selection actually changed
            if old_index != selected_index_ref[0] and filtered_display_items:
                item_name = filtered_display_items[selected_index_ref[0]]
                if item_name == CREATE_NEW_PRESET_MARKER:
                    event.app.show_message(
                        "Opção de criar novo preset selecionada", 0.5
                    )
                else:
                    event.app.show_message(f"Preset '{item_name}' selecionado", 0.5)

        event.app.invalidate()

    # Navigation: Home (go to first item)
    @kb_global.add("home")
    def _(event):
        ensure_app_has_status_message_func()

        if not event.app.layout.has_focus(filter_text_area) and filtered_display_items:
            old_index = selected_index_ref[0]
            selected_index_ref[0] = 0

            if old_index != selected_index_ref[0]:
                item_name = filtered_display_items[0]
                event.app.show_message(f"Primeiro item selecionado: '{item_name}'", 0.5)

        event.app.invalidate()

    # Navigation: End (go to last item)
    @kb_global.add("end")
    def _(event):
        ensure_app_has_status_message_func()

        if not event.app.layout.has_focus(filter_text_area) and filtered_display_items:
            old_index = selected_index_ref[0]
            selected_index_ref[0] = len(filtered_display_items) - 1

            if old_index != selected_index_ref[0]:
                item_name = filtered_display_items[selected_index_ref[0]]
                event.app.show_message(f"Último item selecionado: '{item_name}'", 0.5)

        event.app.invalidate()

    # Action: Enter (select/confirm)
    @kb_global.add("enter")
    def _(event):
        ensure_app_has_status_message_func()

        if event.app.layout.has_focus(filter_text_area):
            if filtered_display_items:
                event.app.layout.focus(list_body_control)
                event.app.show_message("Navegação ativada", 0.5)
        elif (
            app_ref.get("app")
            and filtered_display_items
            and selected_index_ref[0] < len(filtered_presets_plus_marker_obj)
        ):
            selected_obj = filtered_presets_plus_marker_obj[selected_index_ref[0]]
            if selected_obj.name == CREATE_NEW_PRESET_MARKER:
                event.app.show_message("Criando novo preset...", 0.5)
                app_ref["app"].exit(result=("create", None))
            else:
                event.app.show_message(
                    f"Selecionando preset '{selected_obj.name}'...", 0.5
                )
                app_ref["app"].exit(result=("select", selected_obj.id))

    # Action: Create new preset
    @kb_global.add("c", filter=filter_not_focused_condition)
    def _(event):
        ensure_app_has_status_message_func()

        if app_ref.get("app"):
            event.app.show_message("Criando novo preset...", 0.5)
            app_ref["app"].exit(result=("create", None))

    # Action: Edit preset
    @kb_global.add("e", filter=filter_not_focused_condition)
    def _(event):
        ensure_app_has_status_message_func()

        if (
            app_ref.get("app")
            and filtered_display_items
            and selected_index_ref[0] < len(filtered_presets_plus_marker_obj)
        ):
            selected_obj = filtered_presets_plus_marker_obj[selected_index_ref[0]]
            if (
                selected_obj.name != CREATE_NEW_PRESET_MARKER
                and selected_obj.id is not None
            ):
                event.app.show_message(f"Editando preset '{selected_obj.name}'...", 0.5)
                app_ref["app"].exit(result=("edit", selected_obj.id))
            elif selected_obj.name == CREATE_NEW_PRESET_MARKER:
                message_dialog(
                    title="Informação",
                    text="Não é possível editar '[+] Create New Preset'. Use 'C' ou Enter para criar um novo.",
                    style=default_style,
                ).run()
            else:
                message_dialog(
                    title="Informação",
                    text="Não existem presets para editar. Crie um primeiro.",
                    style=default_style,
                ).run()
        else:
            message_dialog(
                title="Informação",
                text="Não existem presets para editar. Crie um primeiro.",
                style=default_style,
            ).run()

    # Action: Delete preset
    @kb_global.add("d", filter=filter_not_focused_condition)
    def _(event):
        ensure_app_has_status_message_func()

        if (
            app_ref.get("app")
            and filtered_display_items
            and selected_index_ref[0] < len(filtered_presets_plus_marker_obj)
        ):
            selected_obj = filtered_presets_plus_marker_obj[selected_index_ref[0]]
            if (
                selected_obj.name != CREATE_NEW_PRESET_MARKER
                and selected_obj.id is not None
            ):
                event.app.show_message(
                    f"Confirmando exclusão do preset '{selected_obj.name}'...", 0.5
                )
                app_ref["app"].exit(result=("confirm_delete", selected_obj.id))
            elif selected_obj.name == CREATE_NEW_PRESET_MARKER:
                event.app.show_message(
                    "Não é possível excluir a opção de criar novo preset", 1.0
                )
            else:
                event.app.show_message(
                    "Nenhum preset válido selecionado para excluir", 1.0
                )
        else:
            event.app.show_message("Não há presets disponíveis para excluir", 1.0)

        event.app.invalidate()

    # Action: Advanced settings
    @kb_global.add("a", filter=filter_not_focused_condition)
    async def _(event):
        ensure_app_has_status_message_func()

        if (
            app_ref.get("app")
            and filtered_display_items
            and selected_index_ref[0] < len(filtered_presets_plus_marker_obj)
        ):
            selected_obj = filtered_presets_plus_marker_obj[selected_index_ref[0]]
            if (
                selected_obj.name != CREATE_NEW_PRESET_MARKER
                and selected_obj.id is not None
            ):
                event.app.show_message(
                    f"Abrindo configurações avançadas para '{selected_obj.name}'...",
                    0.5,
                )
                app_ref["app"].exit(result=("advanced_settings", selected_obj.id))
            elif selected_obj.name == CREATE_NEW_PRESET_MARKER:
                await message_dialog(
                    title="Informação",
                    text="Selecione um preset para utilizar a funcionalidade.",
                    style=default_style,
                )
            else:
                await message_dialog(
                    title="Informação",
                    text="Selecione um preset para utilizar a funcionalidade.",
                    style=default_style,
                )
        else:
            await message_dialog(
                title="Informação",
                text="Selecione um preset para utilizar a funcionalidade.",
                style=default_style,
            )

    # Action: Exit/Cancel
    @kb_global.add("q")
    @kb_global.add("escape")
    def _(event):
        ensure_app_has_status_message_func()

        if filter_active_state[0]:
            if event.app.layout.has_focus(filter_text_area):
                if filter_text_area.text:
                    filter_text_area.text = ""
                    event.app.show_message("Filtro limpo", 0.5)
                else:
                    filter_active_state[0] = False
                    event.app.show_message("Modo de filtro desativado", 0.5)
            else:
                filter_active_state[0] = False
                if filter_text_area.text:
                    filter_text_area.text = ""
                    event.app.show_message(
                        "Filtro limpo e modo de filtro desativado", 0.5
                    )
                else:
                    event.app.show_message("Modo de filtro desativado", 0.5)
            event.app.layout.focus(list_body_control)
        else:
            if app_ref.get("app"):
                event.app.show_message("Saindo...", 0.3)
                app_ref["app"].exit(result=(None, None))

        event.app.invalidate()

    # Action: Toggle filter mode
    @kb_global.add("c-f")
    def _(event):
        ensure_app_has_status_message_func()

        filter_active_state[0] = not filter_active_state[0]
        if filter_active_state[0]:
            event.app.layout.focus(filter_text_area)
            event.app.show_message("Modo de filtro ativado", 0.5)
        else:
            filter_text_area.text = ""
            event.app.layout.focus(list_body_control)
            event.app.show_message("Modo de filtro desativado", 0.5)

        event.app.invalidate()

    # Action: Page Up (move selection up by 5 items)
    @kb_global.add("pageup")
    def _(event):
        ensure_app_has_status_message_func()

        if not event.app.layout.has_focus(filter_text_area) and filtered_display_items:
            old_index = selected_index_ref[0]
            selected_index_ref[0] = max(0, selected_index_ref[0] - 5)

            if old_index != selected_index_ref[0]:
                item_name = filtered_display_items[selected_index_ref[0]]
                event.app.show_message(f"Movido para '{item_name}'", 0.5)

        event.app.invalidate()

    # Action: Page Down (move selection down by 5 items)
    @kb_global.add("pagedown")
    def _(event):
        ensure_app_has_status_message_func()

        if not event.app.layout.has_focus(filter_text_area) and filtered_display_items:
            old_index = selected_index_ref[0]
            max_index = len(filtered_display_items) - 1 if filtered_display_items else 0
            selected_index_ref[0] = min(max_index, selected_index_ref[0] + 5)

            if old_index != selected_index_ref[0]:
                item_name = filtered_display_items[selected_index_ref[0]]
                event.app.show_message(f"Movido para '{item_name}'", 0.5)

        event.app.invalidate()

    @kb_global.add(
        "c-g", filter=filter_not_focused_condition
    )  # Ctrl+G for Wizard Flag Config
    def _(event):
        ensure_app_has_status_message_func()
        if app_ref.get("app"):
            event.app.show_message("Abrindo configuração de flags do wizard...", 0.5)
            app_ref["app"].exit(result=("wizard_flag_config", None))

    return kb_global
