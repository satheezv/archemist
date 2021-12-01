from datetime import datetime
from archemist.state.material import Solid, Liquid
from archemist.util import Location

class Sample():
    def __init__(self, id: int, rack_indx: int):
        self._id = id
        self._rack_indx = rack_indx
        self._liquids = []
        self._solids = []
        self._capped = False
        self._operation_ops = []

    @property
    def id(self):
        return self._id

    @property
    def rack_indx(self):
        return self._rack_indx

    @property
    def liquids(self):
        return self._liquids

    @property
    def solids(self):
        return self._solids

    def add_liquid(self, liquid: Liquid):
        self._liquids.append(liquid)

    def add_solid(self, solid: Solid):
        self._solids.append(solid)

    @property
    def capped(self):
        return self._capped

    @capped.setter
    def capped(self, value: bool):
        if isinstance(value, bool):
            self._capped = value
        else:
            raise ValueError

    def add_operation_op(self, opeation):
        self._operation_ops.append(opeation)

    @property
    def operation_ops(self):
        return self._operation_ops


    def get_total_mass(self):
        total_mass = 0
        for liquid in self._liquids:
            total_mass += liquid.mass
        for solid in self._solids:
            total_mass += solid.mass
        return total_mass


class Batch:

    def __init__(self, id: int, recipe, num_samples: int, location: Location):
        self._id = id
        self._location = location
        self._recipe = recipe
        self._recipe.advance_recipe_state(True) # to move out of start state
        self._samples = list()
        self._num_samples = 0
        for indx in range(0,num_samples):
            self._samples.append(Sample(id,indx))
            self._num_samples += 1
        
        self._assigned = False
        
        self._current_sample_index = 0
        self._all_processed = False
                
        self._station_history = []

    @property
    def id(self):
        return self._id

    @property
    def recipe(self):
        return self._recipe

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if isinstance(location, Location):
            self._location = location
        else:
            raise ValueError

    @property
    def assigned(self):
        return self._assigned

    @assigned.setter
    def assigned(self, value):
        if isinstance(value, bool):
            self._assigned = value
        else:
            raise ValueError

    # @property
    # def current_sample_index(self):
    #     return self._current_sample_index

    def get_current_sample(self):
        return self._samples[self._current_sample_index]

    def process_current_sample(self):
        self._current_sample_index += 1
        if (self._current_sample_index == (self._num_samples)):
            self._all_processed = True
            self._current_sample_index = 0
            self._logBatch('All samples have been processed. Batch index is reset to 0.')

    def add_station_stamp(self, station_stamp: str):
        self._station_history.append((datetime.now(), station_stamp))
        self._logBatch(f'stamp ({station_stamp}) added.')

    @property
    def station_history(self):
        return self._station_history

    def are_all_samples_processed(self):
        return self._all_processed

    @property
    def num_samples(self):
        return self._num_samples

    def _logBatch(self, message: str):
        print(f'Batch [{self._id}]: ' + message)

