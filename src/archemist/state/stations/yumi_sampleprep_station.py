from archemist.state.station import Station, Location, StationOpDescriptor, StationOutputDescriptor
from enum import Enum
from bson.objectid import ObjectId

class yumi_sampleprep_stationStatus(Enum):
    LOAD_STIR = 0
    LOAD_SHKR = 1
    LOAD_PLATE = 2
    CAPS = 3 


''' ==== Station Description ==== '''

class yumi_sampleprep_station(Station):
    def __init__(self, db_name: str, station_dict: dict, liquids: list, solids: list):
        if len(station_dict) > 1:
            station_dict['status'] = None

        super().__init__(db_name,station_dict)
        
    def status(self):
        return yumi_sampleprep_stationStatus(self.get_field('status'))

    @classmethod
    def from_dict(cls, db_name: str, station_dict):
        return cls(db_name, station_dict)

    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        station_dict = {'object_id':object_id}
        return cls(db_name, station_dict, None, None)

    @status.setter
    def status(self, status):
        if isinstance(status, yumi_sampleprep_stationStatus):
            self.update_field('status', status.value)
        else:
            raise ValueError

    # ika stir plate station descriptions 
    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        station_dict = {'object_id':object_id}
        return cls(db_name, station_dict, None, None)

    @property
    def set_stirring_speed(self):
        return self.get_field('set_stirring_speed')

    @set_stirring_speed.setter
    def set_stirring_speed(self, value):
        self.update_field('set_stirring_speed', value)

    @property
    def set_duration(self):
        return self.get_field('set_duration')

    @set_duration.setter
    def set_duration(self, value):
        self.update_field('set_duration', value)


    # ika shaker plate station descriptions 
    @classmethod
    def from_object_id(cls, db_name: str, object_id: ObjectId):
        station_dict = {'object_id':object_id}
        return cls(db_name, station_dict, None, None)

    @property
    def set_duration(self):
        return self.get_field('set_duration')

    @set_duration.setter
    def set_duration(self, value):
        self.update_field('set_duration', value)

''' ==== Station Operation Descriptors ==== '''

class YSLoadStirOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

class YSLoadShkrOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

class YSLoadPlateOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

class YSCapsOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

class YSStirOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

class YSShakeOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        output = StationOutputDescriptor()
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)

 # stir and shaker plate operation descriptors 

class IKAStirringOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)
        self._set_stirring_speed = properties['rpm']
        self._duration = properties['duration']

    @property
    def set_stirring_speed(self):
        return self._set_stirring_speed

    @property
    def mode(self):
        return self._mode

    @property
    def duration(self):
        return self._duration

class ShakerOpDescriptor(StationOpDescriptor):
    def __init__(self, properties: dict, output: StationOutputDescriptor):
        super().__init__(stationName=yumi_sampleprep_station.__class__.__name__, output=output)
        self._duration = properties['duration']

    @property
    def mode(self):
        return self._mode

    @property
    def duration(self):
        return self._duration

''' ==== Station Output Descriptors ==== '''

class YSJobOutputDescriptor(StationOutputDescriptor):
    def __init__(self):
        self._results_file_name = ''
        super().__init__()

    @property
    def results_file_name(self):
        return self._results_file_name

    @results_file_name.setter
    def results_file_name(self, file_name):
        self._results_file_name = file_name


class IKAStirOutputDescriptor(StationOutputDescriptor):
    def __init__(self):
        super().__init__()

class ShakerOutputDescriptor(StationOutputDescriptor):
    def __init__(self):
        super().__init__()



