"""
Environment loading utility for Start-Up Sahay Portal.
Supports python-dotenv if installed, with a robust fallback standard-library parser.
"""
import os
from pathlib import Path


def load_env_file(env_path: Path) -> None:
    """Load key-value pairs from .env into os.environ if not already present."""
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        return
    except ImportError:
        pass

    if not env_path.is_file():
        return

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                # Remove surrounding quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # Fall back gracefully if reading fails
        pass


def get_bool_env(key: str, default: bool = False) -> bool:
    """Retrieve an environment variable as a boolean."""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ('true', '1', 'yes', 'on')


def get_int_env(key: str, default: int = 0) -> int:
    """Retrieve an environment variable as an integer."""
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


def get_list_env(key: str, default: str = '') -> list[str]:
    """Retrieve an environment variable as a comma-separated list of strings."""
    val = os.environ.get(key, default)
    return [item.strip() for item in val.split(',') if item.strip()]
