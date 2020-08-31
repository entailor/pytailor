from typing import Dict, Union, List
from pathlib import Path

from .project import Project
from tailor.clients import RestClient, S3Client
from tailor.models import FileSetDownload, FileSetUpload


class FileSet:
    """
    Get a new or existing fileset.
    """

    def __init__(self, project: Project, fileset_id: str = None):
        if fileset_id is None:
            with RestClient() as client:
                fileset_model = client.new_fileset(project.id)
        else:
            fileset_download = FileSetDownload()
            with RestClient() as client:
                fileset_model = client.get_download_urls(project.id, fileset_id,
                                                         fileset_download)
        if fileset_model:
            self.id = fileset_model.id
        else:
            raise ValueError(f'Fileset with id "{fileset_id}" not found for project '
                             f'"{project.name}"')
        self.project = project

    def upload(self, tag: str, files: Union[str, List[str]]):

        if isinstance(files, str):
            files = [files]

        for file in files:
            if not Path(file).exists():
                FileNotFoundError(f'Could not find file: {file}')

        fileset_upload = FileSetUpload(tags={tag: files})
        with RestClient() as client:
            fileset_model = client.get_upload_urls(
                self.project.id, self.id, fileset_upload)

        with S3Client() as client:
            client.upload_files(fileset_upload, fileset_model)
