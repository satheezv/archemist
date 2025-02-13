import rospy
from typing import Tuple, Dict
from archemist.core.state.station import Station
from .state import PXRDAnalysisOpDescriptor
from archemist.core.processing.handler import StationHandler
from std_msgs.msg import String

class PXRDStationROSHandler(StationHandler):
    def __init__(self, station: Station):
        super().__init__(station)
        self._current_cs_status = 'PXRDStatus.IDLE'
        self._desired_cs_status = None
        rospy.init_node(f'{self._station}_handler')
        self.PXRD_pub = rospy.Publisher("/PXRD/command", String, queue_size=1)
        rospy.Subscriber('/PXRD/status', String, self._cs_state_update, queue_size=1)
        rospy.sleep(1)
        

    def run(self):
        rospy.loginfo(f'{self._station}_handler is running')
        try:
            while not rospy.is_shutdown():
                self.handle()
                rospy.sleep(2)
        except KeyboardInterrupt:
            rospy.loginfo(f'{self._station}_handler is terminating!!!')

    def execute_op(self):
        current_op = self._station.get_assigned_station_op()
        if (isinstance(current_op,PXRDAnalysisOpDescriptor)):
            rospy.loginfo('opening chemspeed door')
            for i in range(10):
                self.PXRD_pub.publish('start_analysis')
            self._desired_cs_status = 'PXRDStatus.JOB_COMPLETE'
        else:
            rospy.logwarn(f'[{self.__class__.__name__}] Unkown operation was received')

    def is_op_execution_complete(self) -> bool:
        if self._desired_cs_status == self._current_cs_status:
            self._desired_cs_status = None
            return True
        else:
            return False

    def get_op_result(self) -> Tuple[bool, Dict]:
        if self._current_cs_status != 'CSFlexStatus.ERROR':
            return True, {}
        else:
            return False

    def _cs_state_update(self, msg):
        if self._current_cs_status != msg.data:
            self._current_cs_status = msg.data