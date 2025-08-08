'''
Filename: robot_controller.py
Description: This script controls a robotic arm to perform a series of actions for thermocycling experiments.
It includes functions to move the robot to specific coordinates and log actions.

Author: Akshit Gupta
Email: gupta@dwi.rwth-aachen.de
Affiliation: DWI - Leibniz Institute for Interactive Materials

Last Modified: 2025-07-08
Version: 1.0

License: MIT License

Notes:
Add coordinates for your experiment setup for thermomixer, liquid nitrogen and home position (RobotActions.__init__).
Some of the commented out / deleted code is used to connect to the backend server to get the settings and control the robot.
This code is designed to run on a Raspberry Pi with a MyCobot robotic arm.
'''

from pymycobot.mycobot import MyCobot
import time
import RPi.GPIO as GPIO
import numpy
import logger
import utils

######################## User Settings ##########################
# These settings are used to control the robot's actions and can be modified by the user. handelled by thebackend in the lab

Experiment_Name = "Experiment Name"
Person_Responsible = "Person Responsible"
Thermomixer_Time = 180                      # in seconds
Liquid_Nitrogen_Time = 60                   # in seconds
Waiting_Time = 5                            # in seconds (minimum 2 seconds)
Number_of_Cycles = 1                        # Number of cycles to run the experiment
Run_Number = 1                              # Run number of the experiment

Robot_Speed = 100                           # from 1 to 100, where 100 is the maximum speed

###################################################################


# User settings dictionary to be used in the robot actions
user_settings = {
    'experiment_name': Experiment_Name,
    'person_responsible': Person_Responsible,
    'thermomixer_time_s': Thermomixer_Time,
    'liquid_nitrogen_time_s': Liquid_Nitrogen_Time,
    'waiting_time_s': Waiting_Time,
    'number_of_cycles': Number_of_Cycles,
}


# Initialize logger
log = logger.setup_logger()

# Start Logging with the experiment parameters
log.info("Starting Robot Actions")
log.info("Experiment Parameters:")
log.info(f"Experiment Name: {Experiment_Name}")
log.info(f"Person Responsible: {Person_Responsible}")
log.info(f"Thermomixer Time: {Thermomixer_Time} seconds")
log.info(f"Liquid Nitrogen Time: {Liquid_Nitrogen_Time} seconds")
log.info(f"Waiting Time: {Waiting_Time} seconds")
log.info(f"Number of Cycles: {Number_of_Cycles}")
log.info(f"Run Number: {Run_Number}")


gripper_state = "Not Attached"

# Initialize the MyCobot robotic arm
mc = MyCobot("/dev/ttyAMA0", 1000000)
cobot_speed = Robot_Speed

def update_robot_log(message, cycle, gripper_state, error_info = None):
    """
    Function to update the robot log with the given message, cycle number, gripper state, and error information.
    It is conencted to our backend server to log the information. commented out for now.
    """
    pass


# Used to stop the cycle when the user manually stops it from the webapp
class StopCycleException(Exception):
    pass


# Class to handle robot actions
class RobotActions:


    global gripper_state, cobot_speed
    

    def __init__(self, mc):
        
        self.current_cycle = 1
        self.number_of_cycles = 1
        self.thermomixer_time = 1
        self.liquid_nitrogen_time = 1
        self.waiting_time = 1

        self.c1 = [0,0,0,0,0,0]                 # Coorninates for Liquid Nitrogen (Sample dipped in Liquid Nitrogen Dewar)
        self.c2 = [0,0,0,0,0,0]                 # Coorninates for Liquid Nitrogen (Sample above Liquid Nitrogen Dewar)
        self.a2 = [0,0,0,0,0,0]                 # Angles for Liquid Nitrogen (Sample above Liquid Nitrogen Dewar), same as c2
        
        self.c3 = [0,0,0,0,0,0]                 # Coorninates for Thermomixer (Sample above Thermomixer)
        self.c4 = [0,0,0,0,0,0]                 # Coorninates for Thermomixer (Sample inside Thermomixer)
        self.a4 = [0,0,0,0,0,0]                 # Angles for Thermomixer (Sample inside Thermomixer), same as c4

        self.cm = [0,0,0,0,0,0]                 # Coorninates for inbetween point close to robotics arm to prevent collisions when moving
        self.cr = [0,0,0,0,0,0]                 # Coorninates for Home Position (Resting on Base)


    ################################ Basic Coordinate Distance ##########################
    def distance(self, point1, point2):
        sum = 0
        for i in range(3):
            sum = sum + (point1[i] - point2[i])**2
        distance = numpy.sqrt(sum)
        return distance   

    ############################ check loction error ###################################

    def is_correct_position(self, expected_position = None, current_position = None, timeout = 5):
        
        position_value_flag = False
        
        if current_position == None: 
            start_time = time.monotonic() 
            
            while(time.monotonic() - start_time < timeout):
                current_position = mc.get_coords()
                if len(current_position) == 6:
                    position_value_flag = True
                    break
                time.sleep(0.1)
        
        if position_value_flag:
            distance_error = self.distance(expected_position, current_position)
            
            if distance_error <= 10:
                log.info(f"Distance Error is {distance_error}")
                return True
            elif 10 < distance_error <=15:
                log.info(f"Distance Error is {distance_error}")
                return True
            else:
                log.error(f"Distance Error is {distance_error}")
                log.error(f"Error Function returns {mc.get_error_information() =}")
                utils.play_notification_sound()
                return False
        else:
            log.error("Timeout, cannot detect current position")
            log.error(f"Error Function returns {mc.get_error_information() =}")
            utils.play_notification_sound()
            return False   
                
    ######################### move function #############################################
    def move(self, coordinate, speed = cobot_speed, mode = 1, mc = mc, exception = True):
        mc.send_coords(coordinate, speed, mode)
        if exception:
            self.delay(2)
        if not exception:
            time.sleep(2)
        while(not self.is_correct_position(coordinate)):
            mc.send_coords(coordinate, speed, mode)

        
    # def _check_staus(self):
    #     control = get_robot_control()
    #     if not control['running']:
    #         log.info("Stopping cycle, Raising Exception")
    #         raise StopCycleException("Stopped Manually using Webapp")
        
    
    def delay(self, delay, interval = 0.2):
        start_time = time.monotonic()
        while (time.monotonic() - start_time) < delay:
            # self._check_staus()
            time.sleep(interval)
            
    def init_experiment(self):
        # update_robot_log("Start", self.current_cycle, gripper_state, mc.get_error_information())
        log.info ("Starting Experiment")
        self.move(self.cr)    
        self.move(self.cm)

    def end_experiment(self):
        # update_robot_log("End of Experiment", self.current_cycle, gripper_state)
        # update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())
        log.info ("Ending Experiment")
        self.move(self.cm)
        self.move(self.cr)
        mc.release_all_servos()
        time.sleep(0.5)
        mc.release_all_servos()
        log.info ("Completed and relesed motors")
        self.current_cycle = 1
        
    def closest_point(self, position = mc.get_coords()):
        d1 = self.distance(position, self.c2)
        d2 = self.distance(position, self.c3)
        d3 = self.distance(position, self.cr)
    
        if d1 <= d2 and d1 <= d3:
            return self.c2
        
        if d2 <= d3 and d2 <= d1:
            return self.c3
    
        if d3 <= d1 and d3 <= d1:
            return self.cr
    
    def manual_stop(self, timeout = 5):
        
        close_point = None
        position_value_flag = False
        start_time = time.monotonic() 
        
        # update_robot_log("Manually Stopped", self.current_cycle-1, gripper_state, mc.get_error_information())
        log.info("Manually Stopped, Returning to Rest Position")
        
        while(time.monotonic() - start_time) < timeout:
            current_position = mc.get_coords()
            if len(current_position) == 6:
                position_value_flag = True
                break
            time.sleep(0.1)
        
        if position_value_flag:
            close_point = self.closest_point(current_position)
            log.info(f"Currently at {current_position}")
            log.info(f"Moving to {close_point}")
            self.move(close_point, cobot_speed, 1, mc, False)
            if close_point != self.cr:
                self.move(self.cm, cobot_speed, 1, mc, False)
            log.info("Moving to rest position")
            self.move(self.cr,cobot_speed, 1, mc, False)
            log.info("releasing all servos")
            mc.release_all_servos()
            time.sleep(0.5)
            mc.release_all_servos()
            # update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())
        
        else:
            log.error("Timeout, cannot detect current position")
            log.error(f"Error Function returns {mc.get_error_information() =}")
            utils.play_notification_sound()
            # update_robot_log("Error: Can't return to home", self.current_cycle-1, gripper_state, mc.get_error_information())
            # update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())


    def run_cycle(self):
        
        while self.current_cycle-1 < self.number_of_cycles:
            start_cycle_time = time.monotonic()
            mc.send_angles(self.a2, 100)
            self.delay(1)
            # update_robot_log("Moving to Liuid Nitrogen", self.current_cycle, gripper_state, mc.get_error_information())   
            self.move(self.c2)          
            # update_robot_log("Moving inside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            log.info("Moving inside LN2")
            start_ln2_time = time.monotonic()
            self.move(self.c1, 30)                                              #Lower Speed to prevent splashing
            self.delay(self.liquid_nitrogen_time - 2)
            end_ln2_time = time.monotonic()
            ln2_time = {start_ln2_time - end_ln2_time}
            log.info("Outside LN2")
            # update_robot_log("Outside outside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c2)
            # update_robot_log("Moving sample to Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c3)
            log.info(f"Water Temerature: {utils.read_temp()} C")
            log.info("Moving Inside Water Bath")
            start_water_bath_time = time.monotonic()
            # update_robot_log("Moving Inside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c4)
            self.delay(self.thermomixer_time -2)
            end_water_bath_time = time.monotonic()
            water_bath_time = start_water_bath_time - end_water_bath_time
            log.info("Moving outside Water Bath")
            log.info(f"Water Temerature: {utils.read_temp()} C")
            # update_robot_log("Moving outside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c3)
            log.info("Waiting")
            # update_robot_log("Waiting", self.current_cycle, gripper_state, mc.get_error_information())
            self.delay(self.waiting_time)
            end_cycle_time = time.monotonic()
            extra_cycle_time = end_cycle_time - start_cycle_time - self.liquid_nitrogen_time - self.thermomixer_time - self.waiting_time
            log.info(f"###################################### Cycle Completed: {self.current_cycle} ####################################################" )
            log.info(f"LN2 Time = {ln2_time} ")
            log.info(f"Water Bath = {water_bath_time} ")
            log.info(f"Extra Cycle Time = {extra_cycle_time}")
            log.info("######################################################################################################################")
            self.current_cycle += 1
                
        self.end_experiment()
        
    ################################################################################
        
if __name__ == "__main__":
    
    ra = RobotActions(mc)
    settings_old = None
    
    while True:
        
        controll = {"running": True}
        
        setting = user_settings   
        
        while controll['running']:
            ra.init_experiment()
            try:
                ra.run_cycle()
            except StopCycleException:
                ra.manual_stop()
            break
            
            
        
