from archemist.state.robot import Robot, RobotState, PickBatchToDeckOp, PlaceBatchFromDeckOp, PickAndPlaceBatchOp, MoveSampleOp
from archemist.state.robots.kukaLBRIIWA import KukaLBRTask, KukaNAVTask
from archemist.state.robots.pandaFranka import PandaFranka
from archemist.state.state import State


class RobotScheduler():
    def __init__(self):
        pass

    def schedule(self, job_station_queue: list, state:State):
        pass


class SimpleRobotScheduler(RobotScheduler):
    def __init__(self):
        super().__init__()

    def schedule(self, job_station_queue: list, state: State):
        unassigned_jobs = list()
        while job_station_queue:
            station_robot_job = job_station_queue.pop()
            job_assigned = False
            robot_job = station_robot_job.robot_op
            if isinstance(robot_job, PickBatchToDeckOp) or isinstance(robot_job, PlaceBatchFromDeckOp) or isinstance(robot_job, KukaNAVTask) or isinstance(robot_job, KukaLBRTask):
                robot = state.get_robot('KukaLBRIIWA',1) # this can be replaced by querying a list with robots that are KUKA
                if robot.state == RobotState.IDLE:
                    robot.assign_job(station_robot_job)
                    job_assigned = True
            elif isinstance(robot_job, MoveSampleOp):
                for robot in state.robots:
                    if robot.state == RobotState.IDLE and isinstance(robot,PandaFranka):
                        robot.assign_job(station_robot_job)
                        job_assigned = True
                        # if robot.location.get_map_coordinates() == robot_job.start_location.get_map_coordinates():
                        #     if robot_job.start_location.frame_name in robot.saved_frames and robot_job.target_location.frame_name in robot.saved_frames:
                        #         robot.assign_job(station_robot_job)
                        #         job_assigned = True
            if not job_assigned:
                unassigned_jobs.append(station_robot_job)
        
        job_station_queue.extend(unassigned_jobs)
            