import os
import toml
from pathlib import Path

# set defaults
config = {
    'RUNDIR_TIME_FORMAT': '%Y-%m-%d-%H-%M-%S-%f',
    'LOGGING_FORMAT': '%(asctime)s %(levelname)s %(message)s',
    'API_BASE_URL': 'http://localhost:8000/',
    'AUTH_KEY': None
}


def load_config_from_file() -> dict:
    homedir = Path.home()
    # homedir = os.path.expanduser('~')
    config_file_homedir = homedir / '.tailor' / 'config.toml'
    if config_file_homedir.exists():
        return toml.load(str(config_file_homedir))
    else:
        return {}


def load_config_from_env() -> dict:
    env_cfg = {}
    for key in config:  # use keys in default config to search for valid config names
        if 'PYTAILOR_' + key in os.environ:
            env_cfg[key] = os.getenv(key)
    return env_cfg


file_config = load_config_from_file()
env_config = load_config_from_env()

config.update(file_config)
config.update(env_config)

# put all config names directly under current namespace (tailor.config)
for k, v in config.items():
    globals()[k] = v
