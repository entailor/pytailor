from typing import Union, List, Dict
from pathlib import Path

from tailor.common.base import APIBase
from .project import Project
from tailor.clients import RestClient, FileClient
from tailor.models import FileSetDownload, FileSetUpload
from tailor.utils import check_local_files_exist, get_basenames


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

    def upload(self, **kwargs: Union[str, List[str]]):
        """Upload files by specifying keyword arguments."""

        # kwargs is now a dict on the format {tag: filename(s)}
        # ensure values are lists
        for k in kwargs:
            if isinstance(kwargs[k], str):
                kwargs[k] = [kwargs[k]]

        check_local_files_exist(kwargs)
        file_basenames = get_basenames(kwargs)
        fileset_upload = FileSetUpload(tags=file_basenames)

        with RestClient() as client:
            fileset_model = self._handle_rest_client_call(
                client.get_upload_urls,
                self.project.id,
                self.id,
                fileset_upload,
                error_msg='Error while getting upload urls from the backend.'
            )

        with FileClient() as client:
            client.upload_files(kwargs, fileset_model)
