from typing import Union, List, Dict
from pathlib import Path

from pytailor.common.base import APIBase
from .project import Project
from pytailor.clients import RestClient, FileClient
from pytailor.models import FileSetDownload, FileSetUpload
from pytailor.utils import check_local_files_exist, get_basenames


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
                    error_msg="An error occurred during fileset creation.",
                )
        else:
            fileset_download = FileSetDownload()
            with RestClient() as client:
                fileset_model = self._handle_rest_client_call(
                    client.get_download_urls,
                    project.id,
                    fileset_id,
                    fileset_download,
                    error_msg=f"Could not retrieve fileset with id {fileset_id}",
                )
        self.id = fileset_model.id
        self.project = project

    def upload(self, **files: List[str]):
        """Upload files by specifying keyword arguments: tag=[path1, path2, ...]"""

        check_local_files_exist(files)
        file_basenames = get_basenames(files)
        fileset_upload = FileSetUpload(tags=file_basenames)

        with RestClient() as client:
            fileset_model = self._handle_rest_client_call(
                client.get_upload_urls,
                self.project.id,
                self.id,
                fileset_upload,
                error_msg="Error while getting upload urls from the backend.",
            )

        with FileClient() as client:
            client.upload_files(files, fileset_model)
