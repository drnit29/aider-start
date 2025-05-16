# aider-start

**Version:** 0.1.0
**Python Requirement:** >=3.8
**License:** MIT (Placeholder - please choose an appropriate license)

## What is aider-start?

`aider-start` is a command-line interface (CLI) tool designed to simplify the management of configuration presets for [aider](https://github.com/paul-gauthier/aider), the chat-based AI pair programming tool in your terminal.

With `aider-start`, you can easily create, edit, select, and run different configurations for `aider` through an interactive Text User Interface (TUI), making it more efficient to work with `aider` in various contexts or projects.

## Key Features

*   **Preset Management:** Create, list, edit, and delete your `aider` configuration presets.
*   **Easy Execution:** Select a preset from the TUI to build and run the corresponding `aider` command.
*   **Configuration Wizard:** A guided assistant to help you create new presets intuitively.
*   **Text User Interface (TUI):** A user-friendly terminal interface for all preset management operations.
*   **Advanced Settings:** Fine-tune settings for each preset.
*   **Command Preview:** Review the generated `aider` command before execution.

## Installation

You can install `aider-start` using pip:

```bash
pip install aider-start
```

(Note: Currently, the package may not be on PyPI. Refer to the "Development" section for local installation.)

## Usage

To start the Text User Interface (TUI) and manage your presets, run:

```bash
aider-start
```

Or explicitly:

```bash
aider-start tui
```

The TUI will allow you to navigate, create, edit, delete, and run `aider` presets.

### Test Command

To check if the installation is working, you can use the `hello` command:

```bash
aider-start hello
# Expected output: Hello World from aider-start!

aider-start hello --name YourName
# Expected output: Hello YourName from aider-start!
```

## How It Works (Overview)

*   **CLI Framework:** Built with [Typer](https://typer.tiangolo.com/) for a robust command-line interface.
*   **Text User Interface (TUI):** Uses [python-prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) to create the interactive terminal experience.
*   **Data Storage:** Presets and their configurations are stored locally in an SQLite database.
*   **Command Execution:** `aider-start` builds and executes `aider` commands based on the selected presets.

## Development

If you want to contribute or run the development version:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/aider-start # Update with the actual URL
    cd aider-start
    ```

2.  **Build and install locally:**
    ```bash
    python build_and_test.py
    ```
    This script will clean previous builds, build the package, install it in development mode (`pip install -e .`), and run a basic test.

    To manually install the generated wheel (after running `python -m build`):
    ```bash
    pip install --force-reinstall dist/*.whl
    ```

## Main Dependencies

*   [typer[all]](https://typer.tiangolo.com/)
*   [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/)
*   [PyYAML](https://pyyaml.org/) (for handling `aider` configuration files)

## Project Details

*   **Repository:** https://github.com/drnit29/aider-start
*   **Authors:** Diogo Soares Rodrigues

---
