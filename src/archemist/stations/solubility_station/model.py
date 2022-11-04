from archemist.core.models.station_op_model import StationOpDescriptorModel
from mongoengine import fields
from enum import Enum

class SolubilityState(Enum):
    UNDISSOLVED = 0
    # PARTIALLY_DISSOLVED = 1
    DISSOLVED = 1

class SolubilityOpDescriptorModel(StationOpDescriptorModel):
    solubility_state = fields.EnumField(SolubilityState)