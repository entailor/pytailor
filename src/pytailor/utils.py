import uuid
import platform
import copy
import fnmatch
import logging
import os
import pathlib
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import List, Dict, Union
from pytailor.config import RUNDIR_TIME_FORMAT, LOGGING_FORMAT


def default_worker_name():
    machine_id = hex(uuid.getnode())[2:-4]
    short_hostname = platform.node().split(".", 1)[0]
    return f"{short_hostname}_{machine_id}"


def walk_and_apply(
    d,
    key_cond=None,
    key_apply=None,
    val_cond=None,
    val_apply=None,
    key_apply_on="key_cond",
    val_apply_on="val_cond",
):
    """
    Walk a nested data structure *d* (think JSON) and apply conditional transformations
    to keys and/or values. Returns a new version of *d* with applied
    transformations.
    """

    def update_dict_key(d, old_k, new_k, new_v=None):
        # use this to keep order when replacing keys
        # inplace update of d
        for k in list(d.keys()):
            v = d.pop(k)
            if k == old_k:
                d[new_k] = new_v
            else:
                d[k] = v

    def recursive_func(d, d_out):

        if isinstance(d, dict):
            for k, v in d.items():

                # apply transformations
                new_key = k
                new_val = v
                if key_cond and key_cond(k):
                    if key_apply_on == "key_cond":
                        new_key = key_apply(k)
                    if val_apply_on == "key_cond":
                        new_val = val_apply(v)

                if val_cond and val_cond(v):
                    if key_apply_on == "val_cond":
                        new_key = key_apply(k)
                    if val_apply_on == "val_cond":
                        new_val = val_apply(v)

                # update d_out
                if not new_val is v:
                    if not new_key is k:
                        update_dict_key(d_out, k, new_key, new_val)
                    else:
                        d_out[k] = new_val
                elif not new_key is k:
                    update_dict_key(d_out, k, new_key, d_out[k])

                # go deeper if v has not been transformed and v is a data structure
                if new_val is v and isinstance(v, (dict, list)):
                    recursive_func(v, d_out[new_key])

        elif isinstance(d, list):
            for i, v in enumerate(d):

                # apply transformations
                if val_cond and val_cond(v):
                    d_out[i] = val_apply(v)

                # go deeper if v has not been transformed and v is a data structure
                elif isinstance(v, (dict, list)):
                    recursive_func(v, d_out[i])

    if val_cond and val_cond(d):
        return val_apply(d)

    d_out = copy.deepcopy(d)
    recursive_func(d, d_out)

    return d_out


def dict_keys_int_to_str(d):
    """
    Get a copy of *d* where integer keys are replace with string representation
    of the same key.
    """
    key_cond = lambda k: isinstance(k, int)
    key_apply = lambda k: str(k)
    return walk_and_apply(d, key_cond, key_apply)


def dict_keys_str_to_int(d):
    """
    Get a copy of *d* where string represented integer keys are converted to
    integers.
    """
    key_cond = lambda k: isinstance(k, str) and k.isdigit()
    key_apply = lambda k: int(k)
    return walk_and_apply(d, key_cond, key_apply)


def list_files(path: Path = None, pattern: str = None):
    use_pattern = pattern or "*"
    use_path = path or pathlib.Path.cwd()
    return sorted(use_path.rglob(use_pattern))


def create_rundir(root_dir=".", friendly_name=None, logger=None):
    """
    Creates a directory for a task run and returns the full path.
    """
    friendly_name_part = friendly_name + "_" if friendly_name else ""
    rundir = (
        "taskrun_" + friendly_name_part + datetime.utcnow().strftime(RUNDIR_TIME_FORMAT)
    )
    root_dir = Path(root_dir).absolute() or Path.cwd()
    p = root_dir / rundir
    p.mkdir()
    if logger:
        logger.info(f"Created dir {p.absolute().as_posix()}")
    return p


def flatten_dictvals_or_list(container):
    """Iterate values of in an arbitrary nested dict/list/tuple"""
    if isinstance(container, Mapping):
        container = container.values()
    for i in container:
        if isinstance(i, (list, tuple, Mapping)):
            for j in flatten_dictvals_or_list(i):
                yield j
        else:
            yield i


def extract_real_filenames(data):
    """Get a list of existing filenames contained in *data* where
    *data* is a str or json-compatible data structure
    """
    if isinstance(data, str) and os.path.isfile(data):
        return [data]
    elif isinstance(data, (list, dict, tuple)):
        for out in flatten_dictvals_or_list(data):
            if isinstance(out, str) and os.path.isfile(out):
                return data
    return None


def get_logger(name, stream_level="DEBUG", formatter=None):
    # TODO: file loggers
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stream_level = getattr(logging, stream_level)
    formatter = formatter or logging.Formatter(LOGGING_FORMAT)

    # check if handler exist with name and stream_level
    for sh in logger.handlers:
        if sh.level == stream_level:
            return logger

    # add stream handler
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(stream_level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger


def format_traceback(exc: Exception) -> List[str]:
    return traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)


def check_local_files_exist(tag_filename_mapping: Dict[str, List[Union[str, Path]]]):
    for filenames in tag_filename_mapping.values():
        for filename in filenames:
            p = Path(filename)
            if not p.exists():
                raise FileNotFoundError(f"Could not find local file: {filename}.")


def get_basenames(
    tag_filename_mapping: Dict[str, List[Union[str, Path]]]
) -> Dict[str, List[Union[str, Path]]]:
    tag_basename_mapping = {}
    for tag, filenames in tag_filename_mapping.items():
        tag_basename_mapping[tag] = [Path(fn).name for fn in filenames]
    return tag_basename_mapping


def as_query(arg):
    if isinstance(arg, str) and arg.startswith("<%") and arg.endswith("%>"):
        return arg[2:-2].strip()
    else:
        return False
