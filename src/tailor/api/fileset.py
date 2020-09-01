from typing import Dict, Union, List
from pathlib import Path

from .base import APIBase
from .project import Project
from tailor.clients import RestClient, FileClient
from tailor.models import FileSetDownload, FileSetUpload


class FileSet(APIBase):
    """
    Get a new or existing fileset.
    """

    def __init__(self, project: Project, fileset_id: str = None):
        if fileset_id is None:
            with RestClient() as client:
                fileset_model = self._handle_rest_client_call(
                    client.new_fileset,
                    project.id,
                    error_msg='An error occurred during fileset creation.'
                )
        else:
            fileset_download = FileSetDownload()
            with RestClient() as client:
                fileset_model = self._handle_rest_client_call(
                    client.get_download_urls,
                    project.id,
                    fileset_id,
                    fileset_download,
                    error_msg=f'Could not retrieve fileset with id {fileset_id}'
                )
        self.id = fileset_model.id
        self.project = project

    def upload(self, tag: str, files: Union[str, List[str]]):
        """Upload one or more files under the given *tag*"""
        if isinstance(files, str):
            files = [files]

        for file in files:
            if not Path(file).exists():
                raise FileNotFoundError(f'Could not find local file: {file}.'
                                        f'Upload aborted.')

        fileset_upload = FileSetUpload(tags={tag: files})

        with RestClient() as client:
            fileset_model = self._handle_rest_client_call(
                client.get_upload_urls,
                self.project.id,
                self.id,
                fileset_upload,
                error_msg='Error while getting upload urls from the backend.'
            )

        with FileClient() as client:
            client.upload_files(fileset_upload, fileset_model)
