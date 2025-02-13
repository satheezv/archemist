from typing import Dict
from transitions import Machine, State
from archemist.core.state.station import Station
from archemist.core.state.robot import RobotTaskType
from archemist.robots.kmriiwa_robot.state import KukaLBRTask
from archemist.core.processing.station_process_fsm import StationProcessFSM

class InputStationSm(StationProcessFSM):
    
    def __init__(self, station: Station, params_dict: Dict):
        super().__init__(station, params_dict)        

        ''' States '''
        states = [ State(name='init_state', on_enter='_print_state'), 
            State(name='pickup_batch', on_enter=['request_pickup_batch', '_print_state']),
            State(name='removed_batch_update', on_enter=['update_unloaded_batch', '_print_state']),
            State(name='final_state', on_enter=['finalize_batch_processing', '_print_state'])]
        
        self.machine = Machine(self, states=states, initial='init_state')

        ''' Transitions '''
        transitions = [
            {'trigger':self._trigger_function,'source':'init_state','dest':'pickup_batch', 'prepare':'update_assigned_batches', 'conditions':'all_batches_assigned'},
            {'trigger':self._trigger_function,'source':'pickup_batch','dest':'removed_batch_update', 'conditions':'is_station_job_ready'},
            {'trigger':self._trigger_function,'source':'removed_batch_update','dest':'pickup_batch', 'unless':'are_all_batches_unloaded', 'conditions':'is_station_job_ready'},
            {'trigger':self._trigger_function, 'source':'removed_batch_update','dest':'final_state', 'conditions':['is_station_job_ready','are_all_batches_unloaded']}
        ]

        self.init_state_machine(states=states, transitions=transitions)

    def update_assigned_batches(self):
        self._current_batches_count = len(self._station.assigned_batches)

    def request_pickup_batch(self):
        robot_job = KukaLBRTask.from_args(name='PickupInputRack',params=[False,self._current_batch_index+1],
                                        type=RobotTaskType.LOAD_TO_ROBOT, location=self._station.location)
        current_batch_id = self._station.assigned_batches[self._current_batch_index].id
        self._station.request_robot_op(robot_job, current_batch_id)

    def finalize_batch_processing(self):
        self._station.process_assigned_batches()
        self.to_init_state()

    def _print_state(self):
        print(f'[{self.__class__.__name__}]: current state is {self.state}')
        
class CrystalWorkflowInputStationSm(StationProcessFSM):
    
    def __init__(self, station: Station, params_dict: Dict):
        super().__init__(station, params_dict)        

        ''' States '''
        states = [ State(name='init_state', on_enter='_print_state'), 
            State(name='pickup_batch', on_enter=['request_pickup_batch', '_print_state']),
            State(name='pickup_pxrd_plate', on_enter=['request_pickup_pxrd_plate', '_print_state']),
            State(name='removed_batch_update', on_enter=['update_unloaded_batch', '_print_state']),
            State(name='final_state', on_enter=['finalize_batch_processing', '_print_state'])]
        
        self.machine = Machine(self, states=states, initial='init_state')

        ''' Transitions '''
        transitions = [
            {'trigger':self._trigger_function,'source':'init_state','dest':'pickup_batch', 'prepare':'update_assigned_batches', 'conditions':'all_batches_assigned'},
            {'trigger':self._trigger_function,'source':'pickup_batch','dest':'pickup_pxrd_plate', 'conditions':'is_station_job_ready'},
            {'trigger':self._trigger_function,'source':'pickup_pxrd_plate','dest':'removed_batch_update', 'conditions':'is_station_job_ready'},
            {'trigger':self._trigger_function,'source':'removed_batch_update','dest':'pickup_batch', 'unless':'are_all_batches_unloaded', 'conditions':'is_station_job_ready'},
            {'trigger':self._trigger_function, 'source':'removed_batch_update','dest':'final_state', 'conditions':['is_station_job_ready','are_all_batches_unloaded']}
        ]

        self.init_state_machine(states=states, transitions=transitions)

    def update_assigned_batches(self):
        self._current_batches_count = len(self._station.assigned_batches)

    def request_pickup_batch(self):
        robot_job = KukaLBRTask.from_args(name='PickupInputRack',params=[False,self._current_batch_index+1],
                                        type=RobotTaskType.LOAD_TO_ROBOT, location=self._station.location)
        current_batch_id = self._station.assigned_batches[self._current_batch_index].id
        self._station.request_robot_op(robot_job, current_batch_id)

    def request_pickup_pxrd_plate(self):
        robot_job = KukaLBRTask.from_args(name='PickupPXRDRack',params=[False],
                                        type=RobotTaskType.MANIPULATION, location=self._station.location)
        self._station.request_robot_op(robot_job)

    def finalize_batch_processing(self):
        self._station.process_assigned_batches()
        self.to_init_state()

    def _print_state(self):
        print(f'[{self.__class__.__name__}]: current state is {self.state}')