from typing import Dict, List, Union
from pathlib import Path, PurePath
import httpx
import requests
from pytailor.models import FileSetUpload, FileSet
import shutil
import os


class FileClient(httpx.Client):
    def upload_files(
        self, file_paths: Dict[str, List[Union[str, Path]]], fileset: FileSet
    ):

        for file_paths, fileset_links in zip(file_paths.values(), fileset.tags):
            for file_path, fileset_link in zip(file_paths, fileset_links.links):
                if os.stat(file_path).st_size == 0:
                    response = requests.put(fileset_link.url, data=b"")
                else:
                    with open(file_path, "rb") as f:
                        # alt 1 not working:
                        # response = self.put(fileset_link.url, data=f)

                        # alt 2 not working:
                        # request = self.build_request('PUT', fileset_link.url, data=f)
                        # del request.headers['Transfer-Encoding']
                        # response = self.send(request)

                        # fallback to requests
                        response = requests.put(fileset_link.url, data=f)

    def download_files(self, fileset: FileSet, use_storage_dirs: bool = True):
        for fileset_links in fileset.tags:
            for fileset_link in fileset_links.links:
                path = Path(fileset_link.filename)
                if use_storage_dirs:
                    local_filename = str(path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    local_filename = path.name
                with requests.get(fileset_link.url, stream=True) as r:
                    with open(local_filename, "wb") as f:
                        shutil.copyfileobj(r.raw, f)

    @staticmethod
    def _get_filename_prefix(scope_prefix, scope_indices):
        p = PurePath(scope_prefix)
        indices = [int(i) for i in p.parts[1:]]

        if len(indices) <= len(scope_indices):
            # downloading from a lower dup level
            return ""
        else:
            # downloading from a higher dup level
            target_indices = indices.copy()
            for i in range(len(scope_indices)):
                if indices[i] == scope_indices[i]:
                    target_indices.pop(0)
                else:
                    break

            filename_prefix = ""
            for index in target_indices:
                filename_prefix += str(index) + "_"
            return filename_prefix
