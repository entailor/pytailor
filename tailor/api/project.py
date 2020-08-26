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

    def __repr__(self):
        return f'Project(uuid={self.uuid})'

    @classmethod
    def from_name(cls, project_name: str) -> 'Project':
        """Get project with name *project_name*."""
        with ProjectClient() as client:
            for prj in client.get_projects():
                if project_name == prj.name:
                    return Project(prj.uuid)
            raise ValueError(f'Could not find project with name {project_name}')
