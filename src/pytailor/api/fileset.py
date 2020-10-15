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
                fileset_model = self._handle_request(
                    client.new_fileset,
                    project.id,
                    error_msg="An error occurred during fileset creation.",
                )
        else:
            fileset_download = FileSetDownload()
            with RestClient() as client:
                fileset_model = self._handle_request(
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
            fileset_model = self._handle_request(
                client.get_upload_urls,
                self.project.id,
                self.id,
                fileset_upload,
                error_msg="Error while getting upload urls from the backend.",
            )

        with FileClient() as client:
            self._handle_request(
                client.upload_files,
                files,
                fileset_model
            )

    def download(
        self, task_id: str = None, tags: List[str] = None, use_storage_dirs: bool = True
    ):
        """
        Download files with specified filenames, task_id and/or tags.

        If use_storage_dirs=False all files are downloaded to the current directory
        """

        fileset_download = FileSetDownload(task_id=task_id, tags=tags)

        with RestClient() as client:
            fileset_model = self._handle_request(
                client.get_download_urls,
                self.project.id,
                self.id,
                fileset_download,
                error_msg="Error while getting download urls from the backend.",
            )

        with FileClient() as client:
            self._handle_request(
                client.download_files,
                fileset_model,
                use_storage_dirs
            )

    def list_files(self, task_id: str = None, tags: List[str] = None):
        """List files with specified task_id and/or tags"""

        fileset_download = FileSetDownload(task_id=task_id, tags=tags)

        with RestClient() as client:
            fileset_model = self._handle_request(
                client.get_download_urls,
                self.project.id,
                self.id,
                fileset_download,
                error_msg="Error while getting upload urls from the backend.",
            )
        files = []
        for tags in fileset_model.tags:
            files_in_tag = []
            for link in tags.links:
                files_in_tag.append(link.filename)
            files.append({"tag": tags.tag_name, "filenames": files_in_tag})
        return files
