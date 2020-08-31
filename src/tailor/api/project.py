from tailor.clients import RestClient


class Project:
    """
    Represents a Tailor.wf project.

    Parameters
    ----------
    project_id : str
        Must be the id of an existing Tailor.wf project

    """

    def __init__(self, project_id: str):
        self.id = project_id
        with RestClient() as client:
            self.__project_model = client.get_project(self.id)
            if self.__project_model is None:
                raise ValueError(f'Could not find project with id {project_id}')
        self.name = self.__project_model.name

    @classmethod
    def from_name(cls, project_name: str) -> 'Project':
        """Get project with name *project_name*."""
        with RestClient() as client:
            for prj in client.get_projects():
                if project_name == prj.name:
                    return Project(prj.id)
            raise ValueError(f'Could not find project with name {project_name}')
