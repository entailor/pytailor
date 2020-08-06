import os
import toml


# set defaults
config = {
    'RUNDIR_TIME_FORMAT': '%Y-%m-%d-%H-%M-%S-%f',
    'LOGGING_FORMAT': '%(asctime)s %(levelname)s %(message)s',
    'API_BASE_URL': 'http://localhost:8000/',
    'AUTH_KEY': None
}


def load_config_from_file() -> dict:
    homedir = os.path.expanduser('~')
    config_file_homedir = os.path.join(homedir, '.tailor', 'config.toml')
    if os.path.isfile(config_file_homedir):
        return toml.load(config_file_homedir)
    else:
        return {}


def load_config_from_env() -> dict:
    env_cfg = {}
    for key in config:  # use keys in default config to search for valid config names
        if key in os.environ:
            env_cfg[key] = os.getenv(key)
    return env_cfg


file_config = load_config_from_file()
env_config = load_config_from_env()

config.update(file_config)
config.update(env_config)

# put all config names directly under current namespace (tailor.internal.config)
for k, v in config.items():
    globals()[k] = v
