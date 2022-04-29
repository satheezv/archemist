from transitions import Machine, State
from archemist.state.robot import MoveSampleOp, RobotOutputDescriptor
from archemist.state.robots.kukaLBRIIWA import KukaLBRTask


class yumi_sampleprepSM():

    def __init__(self, args: dict):
        self._station = yumi_sampleprep_station
        self.batch_mode = args['batch_mode']


        ''' States '''

        states = [ State(name='start', on_enter='_print_state'), 
            State(name='rack_to_station', on_enter= ['request_load_rack','_print_state']), 
            State(name='load_stir', on_enter=['request_yumi_loadstir', '_print_state']),
            State(name='stir_on', on_enter=['_print_state']),
            State(name='stir_off', on_enter=['_print_state']), 
            State(name='load_shake', on_enter=['request_yumi_loadshake', '_print_state']),
            State(name='shake_on', on_enter=['_print_state']),
            State(name='shake_off', on_enter=['_print_state']),
            State(name='load_rack', on_enter=['request_yumi_loadrack', '_print_state']),
            State(name='uncap', on_enter= ['request_yumi_uncap ', '_print_state']),
            State(name='finish', on_enter=[ '_print_state'])]
        
        self.machine = Machine(self, states=states, initial='start')
       

        ''' Transitions '''

       
        # kuka load rack onto station
        self.machine.add_transition('process_state_transitions',source='start',dest='rack_to_station', conditions='is_batch_assigned')
        
        # yumi load vials into stir
        self.machine.add_transition('process_state_transitions', source='rack_to_station',dest='load_stir', conditions='is_station_job_ready')

        # stir on TODO set condition :is yumi in home position
        self.machine.add_transition('process_state_transitions', source='load_stir',dest='stir_on', conditions='is_station_job_ready')

        # stir off
        self.machine.add_transition('process_state_transitions', source='stir_on',dest='stir_off', conditions='is_station_job_ready')

        # yumi load vials into shake
        self.machine.add_transition('process_state_transitions', source='stir_off',dest='load_shake', conditions='is_station_job_ready')

        # shake on TODO set condition :is yumi in home position
        self.machine.add_transition('process_state_transitions', source='load_shake',dest='shake_on', conditions='is_station_job_ready')
 
        # shake off
        self.machine.add_transition('process_state_transitions', source='shake_on',dest='shake_off', conditions='is_station_job_ready')

        # yumi load rack 
        self.machine.add_transition('process_state_transitions', source='shake_off',dest='load_rack', conditions='is_station_job_ready')

        # yumi uncap
        self.machine.add_transition('process_state_transitions', source='load_rack',dest='uncap', conditions='is_station_job_ready')

        # finish TODO set condition :is yumi in home position
        self.machine.add_transition('process_state_transitions', source='uncap',dest='finish', conditions='is_station_job_ready')




  
    def request_load_rack(self):
        self._station.set_robot_job(KukaLBRTask('YumiStationLoadRack', self._station.location, RobotOutputDescriptor())) 

    # kuka placeholder for yumi robot
    def request_yumi_loadstir(self):
        self._station.set_robot_job(KukaLBRTask('LoadStir', self._station.location, RobotOutputDescriptor())) 

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