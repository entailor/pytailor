from .project import Project
from tailor.clients import RestClient
from tailor.models import FileSetDownload


class FileSet:
    """
    Get a new or existing fileset.
    """

    def __init__(self, project: Project, fileset_id: str = None):
        if fileset_id is None:
            with RestClient() as client:
                fileset = client.new_fileset(project.id)
        else:
            fileset_download = FileSetDownload()
            with RestClient() as client:
                fileset = client.get_download_urls(project.id, fileset_id,
                                                   fileset_download)
        if fileset:
            self.id = fileset.id
        else:
            raise ValueError(f'Fileset with id "{fileset_id}" not found for project ' 
                             f'"{project.name}"')
