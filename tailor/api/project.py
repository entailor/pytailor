from tailor.models import Project as ProjectModel
from tailor.clients import ProjectClient


class Project:
    """
    Represents a Tailor.wf project.

    Parameters
    ----------
    project_uuid : str
        Must be the uuid of an existing Tailor.wf project

    """

    def __init__(self, project_uuid: str):
        self.uuid = project_uuid
        with ProjectClient() as client:
            self.__project_model: ProjectModel = client.get_project(self.uuid)
        self.name = self.__project_model.name
