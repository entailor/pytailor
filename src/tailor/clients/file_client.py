from typing import Dict, List, Union
from pathlib import Path
import httpx
import requests
from tailor.models import FileSetUpload, FileSet


class FileClient(httpx.Client):

    def upload_files(self,
                     file_paths: Dict[str, List[Union[str, Path]]],
                     fileset: FileSet):

        for file_paths, fileset_links in zip(file_paths.values(),
                                             fileset.tags):
            for file_path, fileset_link in zip(file_paths, fileset_links.links):

                with open(file_path, 'rb') as f:
                    # alt 1 not working:
                    # response = self.put(fileset_link.url, data=f)

                    # alt 2 not working:
                    # request = self.build_request('PUT', fileset_link.url, data=f)
                    # del request.headers['Transfer-Encoding']
                    # response = self.send(request)

                    # fallback to requests due to missing support for put-upload in httpx
                    response = requests.put(fileset_link.url, data=f)

    def download_files(self):
        pass
