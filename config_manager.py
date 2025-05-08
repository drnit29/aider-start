import json
import os
from pathlib import Path

CONFIG_DIR_NAME = ".aider-start"
CONFIG_FILE_NAME = "config.json"

def get_config_path() -> Path:
    """
    Returns the absolute path to the configuration file.
    """
    home_dir = Path.home()
    config_dir = home_dir / CONFIG_DIR_NAME
    return config_dir / CONFIG_FILE_NAME

def generate_default_config() -> dict:
    """
    Generates a default/empty configuration structure.
    """
    return {
        "profiles": {},
        "providers": {
            "openai": {
                "api_key": "",
                "models": []
            },
            "anthropic": {
                "api_key": "",
                "models": []
            }
        },
        "custom_endpoints": {}
    }

def save_config(config: dict) -> None:
    """
    Saves the configuration to the config file.
    Ensures the configuration directory is created if it doesn't exist.
    """
    config_file_path = get_config_path()
    try:
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_file_path}")
    except IOError as e:
        print(f"Error saving configuration to {config_file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving configuration: {e}")

def load_config() -> dict:
    """
    Loads the configuration from the config file.
    If the file doesn't exist or is invalid, returns a default configuration.
    """
    config_file_path = get_config_path()
    if not config_file_path.exists():
        print(f"Configuration file not found at {config_file_path}. Returning default config.")
        return generate_default_config()

    try:
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        
        # Basic validation
        required_keys = ["profiles", "providers", "custom_endpoints"]
        if not all(key in config for key in required_keys):
            print("Invalid configuration file: missing one or more main keys. Returning default config.")
            return generate_default_config()
        
        print(f"Configuration loaded from {config_file_path}")
        return config
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {config_file_path}. Returning default config.")
        return generate_default_config()
    except IOError as e:
        print(f"Error loading configuration from {config_file_path}: {e}. Returning default config.")
        return generate_default_config()
    except Exception as e:
        print(f"An unexpected error occurred while loading configuration: {e}. Returning default config.")
        return generate_default_config()

if __name__ == '__main__':
    # Example usage (for testing purposes)
    print("--- Testing Configuration Manager ---")

    # 1. Generate default config
    default_cfg = generate_default_config()
    print("\n1. Generated Default Configuration:")
    print(json.dumps(default_cfg, indent=2))

    config_file = get_config_path()
    print(f"\n   Config file path: {config_file}")

    # Clean up existing config file for a fresh test run
    if config_file.exists():
        print(f"   Removing existing config file: {config_file}")
        os.remove(config_file)
    if config_file.parent.exists() and not any(config_file.parent.iterdir()): # remove dir if empty
        print(f"   Removing empty config directory: {config_file.parent}")
        os.rmdir(config_file.parent)


    # 2. Load config (should return default as file doesn't exist yet)
    print("\n2. Attempting to load config (file should not exist yet):")
    loaded_cfg_before_save = load_config()
    print("   Loaded config (before save):")
    print(json.dumps(loaded_cfg_before_save, indent=2))
    assert loaded_cfg_before_save == default_cfg, "Load before save should return default config"

    # 3. Save a modified config
    print("\n3. Modifying and saving configuration:")
    my_config = generate_default_config()
    my_config["profiles"]["test_profile"] = "some parameters"
    my_config["providers"]["openai"]["api_key"] = "sk-test123"
    save_config(my_config)

    # 4. Load the saved config
    print("\n4. Loading the saved configuration:")
    loaded_cfg_after_save = load_config()
    print("   Loaded config (after save):")
    print(json.dumps(loaded_cfg_after_save, indent=2))
    assert loaded_cfg_after_save == my_config, "Loaded config should match the saved one"

    # 5. Test invalid config file (missing keys)
    print("\n5. Testing invalid configuration file (missing 'profiles' key):")
    invalid_data = {
        "providers": {"test": "data"},
        "custom_endpoints": {}
    }
    # Create parent directory if it doesn't exist for this test
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(invalid_data, f, indent=2)
    
    loaded_invalid_cfg = load_config()
    print("   Loaded config (from invalid file):")
    print(json.dumps(loaded_invalid_cfg, indent=2))
    assert loaded_invalid_cfg == default_cfg, "Loading invalid config should return default config"

    # 6. Test malformed JSON
    print("\n6. Testing malformed JSON file:")
    with open(config_file, 'w') as f:
        f.write("this is not json")
    
    loaded_malformed_cfg = load_config()
    print("   Loaded config (from malformed file):")
    print(json.dumps(loaded_malformed_cfg, indent=2))
    assert loaded_malformed_cfg == default_cfg, "Loading malformed JSON should return default config"

    print("\n--- Configuration Manager Tests Completed ---")
    # Clean up after tests
    if config_file.exists():
        os.remove(config_file)
    if config_file.parent.exists() and not any(config_file.parent.iterdir()):
        os.rmdir(config_file.parent)
    print("Cleaned up test config file and directory.")