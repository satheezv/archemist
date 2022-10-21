from archemist.state.station import Station
from archemist.processing.handler import StationHandler
from threading import Thread
import time

class GenericStation_Handler(StationHandler):
    def __init__(self, station: Station):
        super().__init__(station)
        self._thread = None

    def execute_op(self):
        current_op = self._station.get_assigned_station_op()
        current_op.add_start_timestamp()   
        print(f'performing operation {current_op}')    
        self._thread = Thread(target=self._mock_execution)
        self._thread.start()

    def is_op_execution_complete(self):
        if self._thread.is_alive():
            return False
        else:
            return True

    def run(self):
        print(f'{self._station}_handler is running')
        try:
            while True:
                self.handle()
                time.sleep(2)
        except KeyboardInterrupt:
            print(f'{self._station}_handler is terminating!!!')

    def _mock_execution(self):
        time.sleep(1)
        self._execution_result = True
        self._results = {}