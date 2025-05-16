CACHE_FLAGS = [
    {
        "name": "cache-prompts",
        "description": "Enable caching of prompts (default: False)",
        "category": "Cache settings",
        "value_type": "boolean_explicit",
        "choices": ["--cache-prompts", "--no-cache-prompts"],
        "default_value": False,
        "requires_value": False,
        "is_deprecated": False,
        "wizard_visible": True,
    },
    {
        "name": "cache-keepalive-pings",
        "description": "Number of times to ping at 5min intervals to keep prompt cache warm (default: 0)",
        "category": "Cache settings",
        "value_type": "integer",
        "requires_value": True,
        "default_value": "0",
        "is_deprecated": False,
        "wizard_visible": True,
    },
]
