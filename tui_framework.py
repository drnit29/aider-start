import curses

def display_menu(stdscr, menu_items, title="Select an option:"):
    """
    Displays a selectable menu in the terminal and returns the selected item.

    Args:
        stdscr: The curses screen object.
        menu_items: A list of strings representing the menu items.
        title: An optional title to display above the menu.

    Returns:
        The selected menu item (string), or None if the user exits (e.g., with 'q').
    """
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(True)  # Enable keypad mode for arrow keys, etc.
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected item
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal item

    current_row_idx = 0
    max_rows, max_cols = stdscr.getmaxyx()

    while True:
        stdscr.clear()
        
        # Display title
        if title:
            title_y = 1
            title_x = (max_cols - len(title)) // 2
            stdscr.addstr(title_y, title_x, title)

        # Display menu items
        menu_start_y = title_y + 2 if title else 1
        for idx, item in enumerate(menu_items):
            y = menu_start_y + idx
            x = (max_cols - len(item)) // 2
            if y >= max_rows -1: # Ensure we don't write outside screen
                break
            if idx == current_row_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(2))
        
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row_idx = (current_row_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_row_idx = (current_row_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.clear()
            stdscr.refresh()
            return menu_items[current_row_idx]
        elif key == ord('q') or key == 27: # 'q' or ESC to quit
            stdscr.clear()
            stdscr.refresh()
            return None

def main_menu_example(stdscr):
    """Example usage of the display_menu function."""
    menu_options = ["Option 1", "Option 2", "Option 3", "Exit"]
    selected_option = display_menu(stdscr, menu_options, title="Main Menu")

    # For demonstration, print the selected option outside curses window
    # In a real app, you'd use this return value to drive logic
    if selected_option:
        # Need to end curses window before printing to standard console
        curses.endwin() 
        print(f"You selected: {selected_option}")
        if selected_option == "Exit":
            print("Exiting application.")
        else:
            # Re-initialize for further TUI interaction if needed, or just exit
            input("Press Enter to continue (outside curses)...") 
    else:
        curses.endwin()
        print("No option selected or exited.")

if __name__ == '__main__':
    # curses.wrapper handles initialization and cleanup
    curses.wrapper(main_menu_example)