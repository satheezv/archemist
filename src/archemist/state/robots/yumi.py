from archemist.state.robot import armRobot, SpecialJobOpDescriptor, RobotOutputDescriptor, RobotOpDescriptor
from archemist.util import Location
from bson.objectid import ObjectId


class YuMiTask(SpecialJobOpDescriptor):
    def __init__(self, job_name: str, job_params: list, job_location: Location, output: RobotOutputDescriptor):
        super().__init__(job_name, job_params, job_location, output=output)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} with task: {self._job_name} @{self._job_location}'

class YuMi(armRobot):
    def __init__(self, db_name: str, robot_document: dict):
        super().__init__(db_name, robot_document)

    @classmethod
    def from_dict(cls, db_name: str, robot_document: dict):
        return cls(db_name, robot_document)

    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        robot_dict = {'object_id':object_id}
        return cls(db_name, robot_dict)
