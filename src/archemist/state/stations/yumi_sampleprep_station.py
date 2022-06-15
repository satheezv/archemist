from archemist.state.station import Station, Location, StationOpDescriptor, StationOutputDescriptor
from enum import Enum
from bson.objectid import ObjectId

class YuMiSamplePrepStationStatus(Enum):
    LOAD_STIR = 0
    LOAD_SHKR = 1
    LOAD_PLATE = 2
    CAPS = 3 


''' ==== Station Description ==== '''

class YuMiSamplePrepStation(Station):
    def __init__(self, db_name: str, station_dict: dict, liquids: list, solids: list):
        if len(station_dict) > 1:
            station_dict['status'] = None

        super().__init__(db_name,station_dict)

    @property    
    def status(self):
        return YuMiSamplePrepStationStatus(self.get_field('status'))

    @classmethod
    def from_dict(cls, db_name: str, station_dict: dict, liquids: list, solids: list):
        return cls(db_name, station_dict, liquids, solids)

    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        station_dict = {'object_id':object_id}
        return cls(db_name, station_dict, None, None)

    @status.setter
    def status(self, status):
        if isinstance(status, YuMiSamplePrepStationStatus):
            self.update_field('status', status.value)
        else:
            raise ValueError

''' ==== Station Operation Descriptors ==== '''

class YSStirShakeOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=YuMiSamplePrepStation.__class__.__name__, output=output)
        self._set_stirring_speed = properties['rpm']
        self._stir_duration = properties['stir_duration']
        self._shake_duration = properties['shake_duration']

    @property
    def set_stirring_speed(self):
        return self._set_stirring_speed

    @property
    def stir_duration(self):
        return self._stir_duration

    @property
    def shake_duration(self):
        return self._shake_duration

class YSStirOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=YuMiSamplePrepStation.__class__.__name__, output=output)
        self._set_stirring_speed = properties['rpm']
        self._stir_duration = properties['stir_duration']

    @property
    def set_stirring_speed(self):
        return self._set_stirring_speed

    @property
    def stir_duration(self):
        return self._stir_duration

class YSShakeOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=YuMiSamplePrepStation.__class__.__name__, output=output)
        self._shake_duration = properties['shake_duration']

    @property
    def shake_duration(self):
        return self._shake_duration

''' ==== Station Output Descriptors ==== '''

class YSJobOutputDescriptor(StationOutputDescriptor):
    def __init__(self):
        super().__init__()



