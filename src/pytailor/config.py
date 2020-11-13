import os
import toml
from pathlib import Path

# set defaults
config = {
    "RUNDIR_TIME_FORMAT": "%Y-%m-%d-%H-%M-%S-%f",
    "LOGGING_FORMAT": "%(asctime)s %(levelname)s %(message)s",
    "API_BASE_URL": "https://api.tailor.wf/",
    "API_CLIENT_ID": "1ri1tr2uii1bfiqkr3eu9plu27",  # default to Tailor.wf
    "API_IDP_URL": "https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_AoW09D1ut",  # default to Tailor.wf
    "API_WORKER_ID": "",
    "API_SECRET_KEY": "",
    "SYNC_REQUEST_TIMEOUT": 30.0,
    "SYNC_CONNECT_TIMEOUT": 60.0,
    "ASYNC_REQUEST_TIMEOUT": 30.0,
    "ASYNC_CONNECT_TIMEOUT": 60.0,
    "REQUEST_RETRY_COUNT": 5,
    "WAIT_RETRY_COUNT": 10,
    "WAIT_SLEEP_TIME": 2.,
}

allowed_config_names = list(config.keys())


def check_config_names(config_dict):
    config_names = set(config_dict.keys())
    if not config_names.issubset(allowed_config_names):
        bad_names = config_names.difference(allowed_config_names)
        error_msg = "Unknown configuration names found when loading config:"
        for bad_name in bad_names:
            error_msg += f" {bad_name}"
        raise ValueError(error_msg)


def load_config_from_file(heading: str) -> dict:
    config_file = Path.home() / ".tailor" / "config.toml"
    if config_file.exists():
        return toml.load(str(config_file))[heading]
    else:
        return {}


def load_config_from_env() -> dict:
    env_cfg = {}
    for key in config:  # use keys in default config to search for valid config names
        if "PYTAILOR_" + key in os.environ:
            env_cfg[key] = os.getenv(key)
    return env_cfg


file_config = load_config_from_file("pytailor")
env_config = load_config_from_env()

config.update(file_config)
config.update(env_config)

check_config_names(config)

# put all config names directly under current namespace (tailor.config)
for k, v in config.items():
    globals()[k] = v

# load worker configurations
worker_configurations = load_config_from_file("worker")
