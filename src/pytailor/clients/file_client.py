from typing import Dict, List, Union
from pathlib import Path
import requests
from pytailor.models import FileSet
import shutil
import os


class FileClient(requests.Session):
    def upload_files(
        self, file_paths: Dict[str, List[Union[str, Path]]], fileset: FileSet
    ):
        for file_paths, fileset_links in zip(file_paths.values(), fileset.tags):
            for file_path, fileset_link in zip(file_paths, fileset_links.links):
                if os.stat(file_path).st_size == 0:
                    response = requests.put(fileset_link.url, data=b"")
                else:
                    with open(file_path, "rb") as f:
                        response = self.put(fileset_link.url, data=f)
                if not response.status_code == requests.codes.OK:
                    response.raise_for_status()

    def download_files(self, fileset: FileSet, use_storage_dirs: bool = True):
        for fileset_links in fileset.tags:
            for fileset_link in fileset_links.links:
                path = Path(fileset_link.filename)
                if use_storage_dirs:
                    local_filename = str(path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    local_filename = path.name
                with self.get(fileset_link.url, stream=True) as r:
                    with open(local_filename, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
