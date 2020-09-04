from typing import Union, List
from pathlib import Path

from tailor.common.base import APIBase
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
        file_basenames = []
        for file in files:
            p = Path(file)
            if not p.exists():
                raise FileNotFoundError(f'Could not find local file: {file}.'
                                        f'Upload aborted.')
            file_basenames.append(p.name)
        fileset_upload = FileSetUpload(tags={tag: file_basenames})

        with RestClient() as client:
            fileset_model = self._handle_rest_client_call(
                client.get_upload_urls,
                self.project.id,
                self.id,
                fileset_upload,
                error_msg='Error while getting upload urls from the backend.'
            )

        with FileClient() as client:
            client.upload_files({tag: files}, fileset_model)
