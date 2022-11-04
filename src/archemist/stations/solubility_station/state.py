from .model import SolubilityState,SolubilityOpDescriptorModel
from archemist.core.models.station_model import StationModel
from archemist.core.state.station import Station
from archemist.core.state.station_op import StationOpDescriptor
from typing import Dict, List
from archemist.core.state.material import Liquid, Solid
from datetime import datetime


''' ==== Station Description ==== '''
class SolubilityStation(Station):
    def __init__(self, station_model: StationModel) -> None:
        self._model = station_model

    @classmethod
    def from_dict(cls, station_dict: Dict, liquids: List[Liquid], solids: List[Solid]):
        model = StationModel()
        cls._set_model_common_fields(station_dict,model)
        model._module = cls.__module__
        model.save()
        return cls(model)

''' ==== Station Operation Descriptors ==== '''
class SolubilityOpDescriptor(StationOpDescriptor):
    def __init__(self, op_model: SolubilityOpDescriptorModel):
        self._model = op_model

    @classmethod
    def from_args(cls, **kwargs):
        model = SolubilityOpDescriptorModel()
        model._type = cls.__name__
        model._module = cls.__module__
        return cls(model)

    @property
    def solubility_state(self) -> SolubilityState:
        if self._model.has_result and self._model.was_successful:
            return self._model.solubility_state

    def complete_op(self, success: bool, **kwargs):
        self._model.has_result = True
        self._model.was_successful = success
        self._model.end_timestamp = datetime.now()
        if 'solubility_state' in kwargs:
            self._model.solubility_state = kwargs['solubility_state']
        else:
            pass #print('missing read weight!!')
