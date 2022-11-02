import rospy
from typing import Tuple, Dict
from archemist.core.state.station import Station
from .state import ShakeOpDescriptor
from archemist.core.processing.handler import StationHandler
from shaker_plate_msgs.msg import ShakerCommand,ShakerStatus

class ShakePlateROSHandler(StationHandler):
    def __init__(self, station: Station):
        super().__init__(station)
        self._waiting_for = False
        self._task_finished = False
        rospy.init_node(f'{self._station}_handler')
        self._shaker_plate_pu = rospy.Publisher("/shaker_plate/cmd", ShakerCommand, queue_size=1)
        rospy.Subscriber('/shaker_plate/status', ShakerStatus, self._cs_state_update, queue_size=1)
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
        if (isinstance(current_op,ShakeOpDescriptor)):
            rospy.loginfo('starting shaker plate')
            self._waiting_for = True
            self._task_finished = False
            msg = ShakerCommand(shake_duration=current_op.duration)
            for i in range(10):
                self._shaker_plate_pu.publish(msg)

        else:
            rospy.logwarn(f'[{self.__class__.__name__}] Unkown operation was received')

    def is_op_execution_complete(self) -> bool:
        return self._task_finished

    def get_op_result(self) -> Tuple[bool, Dict]:
        return True

    def _cs_state_update(self, msg):
        if self._waiting_for and msg.state == ShakerStatus.NOT_SHAKING:
            self._task_finished = True