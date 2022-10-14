import unittest
from archemist.state.material import Liquid
from archemist.state.robot import RobotTaskOpDescriptor, RobotTaskType
from mongoengine import connect
from archemist.state.station import StationState
from archemist.state.stations.peristaltic_liquid_dispensing import PeristalticLiquidDispensing, PeristalticPumpOpDescriptor
from archemist.state.batch import Batch
from archemist.util.location import Location
import yaml
from datetime import datetime

class StationTest(unittest.TestCase):

    def setUp(self):
        self.station_object_id = None

    def test_station(self):
        station_dict = {
            'class': 'PeristalticLiquidDispensing',
            'id': 23,
            'location': {'node_id': 1, 'graph_id': 7},
            'batch_capacity': 2,
            'process_state_machine': 
            {
                'type': 'StationLoadingSm',
                'args': {'batch_mode': True, 'load_frame': '/liquidStation/loadFrame'}
            },
            'parameters':
            {
                'liquid_pump_map': {'water': 'pUmP1'}
            }
        }
        liquid_dict = {
            'name': 'water',
            'id': 1235,
            'amount_stored': 400,
            'unit': 'ml',
            'density': 997,
            'pump_id': 'pUmP1',
            'expiry_date': datetime.fromisoformat('2025-02-11')
        }
        liquids_list = []
        liquids_list.append(Liquid.from_dict(liquid_dict))
        t_station = PeristalticLiquidDispensing.from_dict(station_document=station_dict, 
                        liquids=liquids_list, solids=[])

        # general properties
        self.assertEqual(t_station.id, 23)
        self.assertEqual(t_station.state, StationState.IDLE)
        self.assertEqual(t_station.batch_capacity, 2)
        self.assertEqual(t_station.operational, True)
        self.assertEqual(t_station.location, Location(1,7,''))
        self.assertEqual(t_station.process_sm_dict, station_dict['process_state_machine'])

        # Loaded samples
        self.assertEqual(t_station.loaded_samples, 0)
        t_station.load_sample()
        t_station.load_sample()
        self.assertEqual(t_station.loaded_samples, 2)
        t_station.unload_sample()
        t_station.unload_sample()
        self.assertEqual(t_station.loaded_samples, 0)

        # Batch
        self.assertFalse(t_station.assigned_batches)
        
        recipe_doc = dict()
        with open('resources/testing_recipe.yaml') as fs:
            recipe_doc = yaml.load(fs, Loader=yaml.SafeLoader)
        batch1 = Batch.from_arguments(31,2,Location(1,3,'table_frame'))
        batch1.attach_recipe(recipe_doc)
        batch2 = Batch.from_arguments(32,2,Location(1,3,'table_frame'))
        batch2.attach_recipe(recipe_doc)

        self.assertTrue(t_station.has_free_batch_capacity())
        t_station.add_batch(batch1)
        self.assertEqual(t_station.state, StationState.IDLE)
        t_station.add_batch(batch2)
        self.assertEqual(t_station.state, StationState.PROCESSING)
        self.assertFalse(t_station.has_free_batch_capacity())

        asigned_batches = t_station.assigned_batches
        self.assertEqual(len(asigned_batches),2)
        self.assertEqual(asigned_batches[0].id, batch1.id)
        self.assertEqual(asigned_batches[1].location, batch2.location)
        self.assertFalse(t_station.has_processed_batch())

        t_station.process_assigned_batches()
        self.assertFalse(t_station.assigned_batches)
        self.assertTrue(t_station.has_processed_batch())
        self.assertEqual(len(t_station.processed_batches),2)
        self.assertEqual(t_station.state, StationState.PROCESSING_COMPLETE)

        procssed_batch1 = t_station.get_processed_batch()
        self.assertTrue(procssed_batch1 is not None)
        self.assertEqual(procssed_batch1.id, batch1.id)
        self.assertEqual(procssed_batch1.location, batch1.location)
        self.assertEqual(t_station.state, StationState.PROCESSING_COMPLETE)

        procssed_batch2 = t_station.get_processed_batch()
        self.assertTrue(procssed_batch2 is not None)
        self.assertEqual(procssed_batch2.id, batch2.id)
        self.assertEqual(procssed_batch2.location, batch2.location)
        self.assertEqual(t_station.state, StationState.IDLE)
        self.assertTrue(t_station.get_processed_batch() is None)

        # Robot Job
        self.assertEqual(len(t_station.requested_robot_op_history), 0)
        self.assertFalse(t_station.has_robot_job())
        self.assertTrue(t_station.get_robot_job() is None)

        robot_op = RobotTaskOpDescriptor.from_args('test_task', parametrs=['False','1'])
        t_station.set_robot_job(robot_op, current_batch_id=31)
        self.assertTrue(t_station.has_robot_job())
        ret_robot_job = t_station.get_robot_job()
        self.assertTrue(ret_robot_job is not None)
        self.assertEqual(robot_op.name, ret_robot_job.name)
        self.assertEqual(robot_op.params, ret_robot_job.params)
        self.assertEqual(ret_robot_job.origin_station, t_station._model.id)
        self.assertEqual(ret_robot_job.related_batch_id, 31)
        self.assertEqual(ret_robot_job.task_type, RobotTaskType.MANIPULATION)
        self.assertEqual(t_station.state, StationState.WAITING_ON_ROBOT)

        t_station.finish_robot_job(robot_op)
        self.assertEqual(t_station.state, StationState.PROCESSING)
        self.assertFalse(t_station.has_robot_job())
        self.assertEqual(len(t_station.requested_robot_op_history), 1)

        # Station op
        self.assertEqual(len(t_station.station_op_history), 0)
        self.assertFalse(t_station.has_station_op())
        self.assertEqual(t_station.state,StationState.PROCESSING)
        station_op1 = PeristalticPumpOpDescriptor.from_args(liquid='water', volume=0.01)
        t_station.set_station_op(station_op1)
        self.assertTrue(t_station.has_station_op())
        self.assertEqual(t_station.state,StationState.WAITING_ON_OPERATION)
        
        current_op = t_station.get_station_op()
        self.assertEqual(current_op.liquid_name, station_op1.liquid_name)
        self.assertEqual(current_op.dispense_volume, station_op1.dispense_volume)
        t_station.finish_station_op(current_op)
        self.assertFalse(t_station.has_station_op())
        self.assertEqual(t_station.state,StationState.PROCESSING)
        station_history = t_station.station_op_history
        self.assertEqual(len(station_history), 1)
        

        station_op2 = PeristalticPumpOpDescriptor.from_args(liquid='water', volume=0.005)
        t_station.set_station_op(station_op2)
        self.assertTrue(t_station.has_station_op())
        t_station.finish_station_op(station_op2)

        station_history = t_station.station_op_history
        self.assertEqual(len(station_history), 2)
        self.assertEqual(station_history[-1].liquid_name, station_op2.liquid_name)
        self.assertEqual(station_history[-1].dispense_volume, station_op2.dispense_volume)

        self.station_object_id = t_station._model.id

        t_station2 = PeristalticLiquidDispensing.from_object_id(self.station_object_id)
        self.assertEqual(t_station2.id, 23)
        self.assertEqual(t_station2.state, StationState.PROCESSING)
        self.assertEqual(t_station2.batch_capacity, 2)
        self.assertEqual(t_station2.operational, True)
        self.assertEqual(t_station2.location, Location(1,7,''))
        self.assertEqual(len(t_station2.station_op_history), 2)
        self.assertEqual(len(t_station2.requested_robot_op_history), 1)
        self.assertTrue(t_station2.has_free_batch_capacity())
        self.assertFalse(t_station2.assigned_batches)
        self.assertFalse(t_station2.processed_batches)

    def test_specific_station(self):
        station_dict = {
            'class': 'PeristalticLiquidDispensing',
            'id': 23,
            'location': {'node_id': 1, 'graph_id': 7},
            'batch_capacity': 2,
            'process_state_machine': 
            {
                'type': 'StationLoadingSm',
                'args': {'batch_mode': True, 'load_frame': '/liquidStation/loadFrame'}
            },
            'parameters':
            {
                'liquid_pump_map': {'water': 'pUmP1'}
            }
        }
        liquid_dict = {
            'name': 'water',
            'id': 1235,
            'amount_stored': 400,
            'unit': 'ml',
            'density': 997,
            'pump_id': 'pUmP1',
            'expiry_date': datetime.fromisoformat('2025-02-11')
        }
        liquids_list = []
        liquids_list.append(Liquid.from_dict(liquid_dict))
        t_station = PeristalticLiquidDispensing.from_dict(station_document=station_dict, 
                        liquids=liquids_list, solids=[])

        liquid = t_station.get_liquid('pUmP1')
        self.assertEqual(liquid.name, 'water')
        self.assertEqual(liquid.id, 1235)
        self.assertEqual(liquid.volume, 0.4)

        pump_id = t_station.get_pump_id('water')
        self.assertEqual(pump_id, 'pUmP1')
        t_station.add_liquid('water', 0.05)
        self.assertEqual(t_station.get_liquid('pUmP1').volume, 0.40005)
        t_station.dispense_liquid('water', 0.1)
        self.assertEqual(t_station.get_liquid('pUmP1').volume, 0.39995)
    

        



if __name__ == '__main__':
    connect(db='archemist_test', host='mongodb://localhost:27017', alias='archemist_state')
    unittest.main()