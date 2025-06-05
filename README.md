# Aider Start

A command-line interface tool for managing and executing Aider command presets. Simplify your Aider workflow by saving frequently used commands as presets and accessing them through an interactive menu.

## Features

- 🚀 **Preset Management**: Save, edit, and remove Aider command presets
- 🔄 **Interactive Menu**: Easy-to-use CLI interface with navigation menus
- 💾 **Persistent Storage**: Presets are saved in your home directory
- ⚡ **Quick Execution**: Run your favorite Aider commands with just a few keystrokes

## Installation

### From PyPI (Recommended)

```bash
pip install aider-start
```

### From Source

```bash
git clone https://github.com/yourusername/aider-start.git
cd aider-start
pip install -e .
```

## Usage

After installation, run the application:

```bash
aider-start
```

Or run directly with Python:

```bash
python -m aider_start
```

### Main Menu Options

1. **Run Preset**: Execute a previously saved Aider command
2. **Configure Preset**: Manage your saved presets
3. **Exit**: Close the application

### Managing Presets

From the "Configure Preset" menu, you can:

- **Add new preset**: Create a new command preset
- **Edit existing preset**: Modify an existing preset
- **Remove preset**: Delete a preset you no longer need

### Example Presets

Here are some example presets you might want to create:

```
Name: "GPT-4 Default"
Command: aider --model openai/gpt-4

Name: "Claude Sonnet"
Command: aider --model anthropic/claude-3-sonnet-20240229

Name: "Local Model"
Command: aider --model ollama/codellama:7b

Name: "GPT-4 with Auto Commit"
Command: aider --model openai/gpt-4 --auto-commits
```

## Configuration

Presets are automatically saved to `~/.aider-start/presets.json` in your home directory. The configuration directory is created automatically on first use.

## Requirements

- Python 3.6+
- InquirerPy
- Aider (for the commands you'll be running)

## Development

### Setting up for Development

```bash
git clone https://github.com/yourusername/aider-start.git
cd aider-start
pip install -e .
```

### Project Structure

```
aider_start/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for python -m aider_start
├── cli.py               # Main CLI interface and menu logic
├── config_manager.py    # Configuration file management
└── presets.json         # Default presets (unused in current version)
```

### Building

```bash
python setup.py sdist bdist_wheel
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Related Projects

- [Aider](https://github.com/paul-gauthier/aider) - AI pair programming in your terminal