'''
Filename: utils.py
Description: Utility functions for robot_controller.py
This module contains utility functions for reading temperature from a sensor and playing notification sounds.

Author: Akshit Gupta
Email: gupta@dwi.rwth-aachen.de
Affiliation: DWI - Leibniz Institute for Interactive Materials

Last Modified: 2025-07-08
Version: 1.0

License: MIT License

Notes: 
Need to setup temperature senser as 1wire with the cobot, before using the read_temp function.
Add the notification sound file path in the play_notification_sound function.
'''

import os
import glob
import time
import pygame



#################### Temperature Sensor Code ####################
#uses 1wire protocol to read temperature from a sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
    
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':       #check if it is a valid reading
        time.sleep(0.2)
        lines = read_temp_raw()
    equal_pos = lines[1].find('t=')
    if equal_pos != -1:
        temp_strings = lines[1][equal_pos+2:]
        temp_c = float(temp_strings)/1000.0
        return temp_c
    else:
        return "Error: Invalid temperature reading"
    
##################### Notification Sound #####################
# Plays a notification sound when called
def play_notification_sound():
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound('add motification sound file path here')
    beep_sound.play()