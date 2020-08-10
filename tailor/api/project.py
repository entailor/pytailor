from tailor.models import Project as ProjectModel


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
        # self.__project_model: ProjectModel = get_project_by_uuid(self.uuid)
