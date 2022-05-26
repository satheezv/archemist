from archemist.state.station import Station, Location, StationOpDescriptor, StationOutputDescriptor
from enum import Enum
from bson.objectid import ObjectId

class pxrd_analyserStatus(Enum):
    RUNNING_JOB = 0
    JOB_COMPLETE = 1

''' ==== Station Description ==== '''

class pxrd_analyser(Station):
    def __init__(self, id: int, loc: Location):
        super().__init__(id, loc)

    @classmethod
    def from_dict(cls, db_name: str, station_dict):
        return cls(db_name, station_dict)

    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        station_dict = {'object_id':object_id}
        return cls(db_name, station_dict, None, None)

    @property
    def status(self):
        return pxrd_analyserStatus(self.get_field('status'))

    @status.setter
    def status(self, status):
        if isinstance(status, pxrd_analyserStatus):
            self.update_field('status', status.value)
        else:
            raise ValueError

     

''' ==== Station Operation Descriptors ==== '''

class pxrdProcessingOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=pxrd_analyser.__class__.__name__, output=output)


''' ==== Station Output Descriptors ==== '''

class pxrdJobOutputDescriptor(StationOutputDescriptor):
    def __init__(self):
        self._results_file_name = ''
        super().__init__()

    @property
    def results_file_name(self):
        return self._results_file_name

    @results_file_name.setter
    def results_file_name(self, file_name):
        self._results_file_name = file_name