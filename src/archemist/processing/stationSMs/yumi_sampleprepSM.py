from transitions import Machine, State
from archemist.state.robot import MoveSampleOp, RobotOutputDescriptor
from archemist.state.robots.kukaLBRIIWA import KukaLBRTask
from archemist.state.station import Station


class yumi_sampleprepSM():

    def __init__(self, station: Station, args: dict):
        self._station = station
        self.batch_mode = args['batch_mode']


        ''' States '''

        states = [ State(name='start', on_enter='_print_state'), 
            State(name='kuka_load_rack', on_enter= ['request_load_rack','_print_state']), 
            State(name='load_stir', on_enter=['request_yumi_loadstir', '_print_state']),
            State(name='stir_plate', on_enter=['_print_state']),
            State(name='load_shake', on_enter=['request_yumi_loadshake', '_print_state']),
            State(name='shake_plate', on_enter=['_print_state']),
            State(name='unload_shake', on_enter=['request_yumi_loadrack', '_print_state']),
            State(name='uncap', on_enter= ['request_yumi_uncap ', '_print_state']),
            State(name='finish', on_enter=[ '_print_state'])]
        
        self.machine = Machine(self, states=states, initial='start')
       

        ''' Transitions '''

       
        # kuka load rack onto station
        self.machine.add_transition('process_state_transitions',source='start',dest='kuka_load_rack', conditions='is_batch_assigned', before='update_batch_loc_to_station')
        
        # yumi load vials into stir
        self.machine.add_transition('process_state_transitions', source='rack_to_station',dest='load_stir', conditions='is_station_job_ready', before='update_batch_loc_to_station')

        # stir plate 
        self.machine.add_transition('process_state_transitions', source='load_stir',dest='stir_plate', conditions='is_station_job_ready')

        # yumi load vials into shake
        self.machine.add_transition('process_state_transitions', source='stir_plate',dest='load_shake', conditions='is_station_job_ready', before='update_batch_loc_to_station')

        # shake plate
        self.machine.add_transition('process_state_transitions', source='load_shake',dest='shake_plate', conditions='is_station_job_ready')
 
        # yumi unload shaker plate and load rack 
        self.machine.add_transition('process_state_transitions', source='shake_plate',dest='unload_shake', conditions='is_station_job_ready', before='update_batch_loc_to_station')

        # yumi uncap
        self.machine.add_transition('process_state_transitions', source='unload_shake',dest='uncap', conditions='is_station_job_ready')

        # finish
        self.machine.add_transition('process_state_transitions', source='uncap',dest='finish', conditions='is_station_job_ready', before='update_batch_loc_to_station')

  
    def request_load_rack(self):
        self._station.set_robot_job(KukaLBRTask('YumiStationLoadRack',[], self._station.location, RobotOutputDescriptor())) 

    def update_batch_loc_to_station(self):
        self._station.assigned_batch.location = self._station.location

    def update_batch_loc_to_robot(self):
        last_executed_robot_op = self._station.requested_robot_op_history[-1]
        self._station.assigned_batch.location = Location(-1,-1,f'{last_executed_robot_op.output.executing_robot}/Deck')

    # kuka placeholder for yumi robot
    def request_yumi_loadstir(self):
        self._station.set_robot_job(KukaLBRTask('LoadStir',[], self._station.location, RobotOutputDescriptor())) 

    def request_yumi_loadshake(self):
        self._station.set_robot_job(KukaLBRTask('LoadShake', self._station.location, RobotOutputDescriptor()))

    def request_yumi_loadrack(self):
        self._station.set_robot_job(KukaLBRTask('LoadRack', self._station.location, RobotOutputDescriptor())) 

    def request_yumi_uncap(self):
        self._station.set_robot_job(KukaLBRTask('Uncap', self._station.location, RobotOutputDescriptor())) 

    def get_batch_mode(self):
        return self.batch_mode

    def is_batch_assigned(self):
        return self._station.assigned_batch is not None

    def is_station_job_ready(self):
        return not self._station.has_station_op() and not self._station.has_robot_job()

    def _print_state(self):
        print(f'[{self.__class__.__name__}]: current state is {self.state}')