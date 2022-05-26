from archemist.state.stations.pxrd_analyser import pxrdProcessingOpDescriptor, pxrdJobOutputDescriptor
from transitions import Machine, State
from archemist.state.robot import MoveSampleOp, RobotOutputDescriptor
from archemist.state.robots.kukaLBRIIWA import KukaLBRTask
from archemist.util import Location



class pxrdSM():

    def __init__(self, args: dict):
        self._station = pxrd_analyser
        self.batch_mode = args['batch_mode']

        ''' States '''

    
        states = [ State(name='start', on_enter='_print_state'), 
            State(name='openpxrddoors', on_enter= ['request_openpxrd','_print_state']), 
            State(name='load_plate', on_enter=['request_loadpxrdplate', '_print_state']),
            State(name='close_pxrddoors', on_enter=['request_closepxrd','_print_state']),
            State(name='analyse_samples', on_enter=['request_analyse_samples', '_print_state']),
            State(name='unload_plate', on_enter=['request_unloadpxrdplate','_print_state']), 
            State(name='finish', on_enter=['_print_state'])]

        self.machine = Machine(self, states=states, initial='start')
        

        ''' Transitions '''

       
        # open pxrd doors
        self.machine.add_transition('process_state_transitions',source='start',dest='open_pxrddoors', conditions='is_batch_assigned')
        
        # load rack into the pxrd
        self.machine.add_transition('process_state_transitions', source='open_pxrddoors',dest='load_plate', conditions='is_station_job_ready', before='update_batch_loc_to_station')

        # close pxrd doors
        self.machine.add_transition('process_state_transitions', source='load_plate',dest='close_pxrddoors', conditions='is_station_job_ready')

        # analyse samples
        self.machine.add_transition('process_state_transitions', source='close_pxrddoors',dest='analyse_samples', conditions='is_station_job_ready')

        # re-open pxrd doors
        self.machine.add_transition('process_state_transitions',source='analyse_samples',dest='open_pxrddoors', conditions='is_station_job_ready', before='process_batch')
        
        # unload rack onto kuka deck
        self.machine.add_transition('process_state_transitions', source='open_pxrddoors',dest='unload_plate', conditions='is_station_job_ready')
        
        # close pxrd doors 
        self.machine.add_transition('process_state_transitions', source='unload_plate',dest='close_pxrddoors', conditions='is_station_job_ready', before='update_batch_loc_to_robot')

        # complete
        self.machine.add_transition('process_state_transitions', source='close_pxrddoors',dest='finish', conditions= 'is_station_job_ready')


    # functions for LBR kuka
    # TODO: add functions for KMR which moves closer between open/close and load/unload

    def request_openpxrd(self):
        self._station.set_robot_job(KukaLBRTask('OpenPXRD', self._station.location, RobotOutputDescriptor())) 

    def request_loadpxrdplate(self):
        self._station.set_robot_job(KukaLBRTask('LoadPXRD', self._station.location, RobotOutputDescriptor())) 

    def request_closepxrd(self):
        self._station.set_robot_job(KukaLBRTask('ClosePXRD', self._station.location, RobotOutputDescriptor())) 

    def request_analyse_samples(self):
        self._station.set_station_op(pxrdProcessingOpDescriptor(dict(), pxrdJobOutputDescriptor()))

    def request_unloadpxrdplate(self):
        self._station.set_robot_job(KukaLBRTask('UnloadPXRD', self._station.location, RobotOutputDescriptor())) 



    def get_batch_mode(self):
        return self.batch_mode

    def is_batch_assigned(self):
        return self._station.assigned_batch is not None

    def is_station_job_ready(self):
        return not self._station.has_station_op() and not self._station.has_robot_job()

    def update_batch_loc_to_station(self):
        self._station.assigned_batch.location = self._station.location

    def update_batch_loc_to_robot(self):
        last_executed_robot_op = self._station.requested_robot_op_history[-1]
        self._station.assigned_batch.location = Location(-1,-1,f'{last_executed_robot_op.output.executing_robot}/Deck')

    def process_batch(self):
        last_operation_op = self._station.station_op_history[-1]
        #TODO if we have multiple racks loop through them
        for _ in range(0, self._station.assigned_batch.num_samples):
                self._station.assigned_batch.add_station_op_to_current_sample(last_operation_op)
                self._station.assigned_batch.process_current_sample()
        self.operation_complete = True

    def _print_state(self):
        print(f'[{self.__class__.__name__}]: current state is {self.state}')