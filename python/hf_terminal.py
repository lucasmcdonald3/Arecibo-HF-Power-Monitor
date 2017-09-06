#!usr/bin/env python3

'''
    File: hf_terminal.py
    Description: Terminal application for controlling the HF power monitoring system.
        Allows for the same utilities as the GUI application in a terminal window, i.e., 
        power monitoring, recording, and copying.
    Author: Lucas McDonald
    Date created: July 12, 2017
    Date modified: July 13, 2017
    Python version: 3.6.1
'''

import os
import time
import pickle
import socket
import sys
import threading
import math
import subprocess

class hf_terminal():

    def __init__(self):

        # Pins used on the RPi to control the HMC252 switches (board mode)
        # transmitted pins
        self.trans_pin_a = 11                 
        self.trans_pin_b = 12
        self.trans_pin_c = 13

        #reflected pins
        self.ref_pin_a = 15                 
        self.ref_pin_b = 16
        self.ref_pin_c = 18

        # pins array passed to take_data methods
        self.decoder_pins = [self.trans_pin_a, self.trans_pin_b, self.trans_pin_c, \
            self.ref_pin_a, self.ref_pin_b, self.ref_pin_c]
    
        print("\n\n\n")
        self.load_settings()
        self.offset = 0
        if self.sock_connect():
            print("Successfully connected to RPi at "+self.rpi_ip+" on port 12345")
        self.display_command_bar()
        self.sock.close()

        self.choice = ''

        while self.choice != 'quit':
            self.get_user_choice()

    def sock_connect(self):
        # create a socket
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            # connect to server
            self.sock.connect((self.rpi_ip, 12345))
            return True
        # handle server software not running on Raspberry Pi
        except ConnectionRefusedError:
            print("\nCONNECTION REFUSED\n\nEnsure the server software is running on the Raspberry Pi.")
            return False
        # handle Raspberry Pi not being on
        except socket.timeout:
            print("\nCONNECTION TIMEOUT\n\nEnsure the Raspberry Pi is powered on and connected to the network.")
            return False
        except BrokenPipeError:
            print("\nCONNECTION BROKEN\n\nThe connection pipe to the Raspberry Pi was broken.")
            return False
        # handle any other errors
        except:
            print("\n\n" + (str(sys.exc_info()[0]).replace(">", "").replace("<","").split(" ")[1]) + \
                "\n\n " + str(sys.exc_info()[1]))

            return False


    def sock_send(self, args):
        # transfer the arguments via a pickle file and send them
        try:
            pickled_args = pickle.dumps(args)
            self.sock.sendall(pickled_args)
            return True
        
        # handle server software not running on Raspberry Pi
        except ConnectionRefusedError:
            print("\nCONNECTION REFUSED\n\nEnsure the server software is running on the Raspberry Pi.")
            return False
        # handle Raspberry Pi not being on
        except socket.timeout:
            print("\nCONNECTION TIMEOUT\n\nEnsure the Raspberry Pi is powered on and connected to the network.")
            return False
        except BrokenPipeError:
            print("\nCONNECTION BROKEN\n\nThe connection pipe to the Raspberry Pi was broken.")
            return False
            
        
    def display_command_bar(self):
        # Clears the terminal screen, and displays a title bar.              
        print("\n\n**********************")
        print("** HF Power Monitor **")

        print("\nCommands:\n")
        print("\trecord [units]".ljust(20) + "Monitor and write data from each transmitter.\n\t\t\t\tIf units are ommitted, kW is used by default.")
        print("\tmonitor [units]".ljust(20) + "Monitor the power of each transmitter, \n\t\t\t\tbut don't write data.")
        print("\tswitch [t/r] [n]".ljust(20) + "Set the transmitted or reflected \n\t\t\t\tswitch to the nth input.")
        print("\tsettings".ljust(20) + "View and modify program settings.")
        print("\tcopy".ljust(20) + "Copy all data files from the Raspberry Pi \n\t\t\t\tto this computer.")
        print("\thelp".ljust(20) + "Display this menu again.")
        print("\tquit".ljust(20) + "Quit the program.")
    
    def get_user_choice(self):
        '''
        Gets user inputs and sanitizes it before calling commands.
        '''
            
        # get choice from user
        self.choice = input("\n\nInput a command: ")

        # check if it is record or monitor
        if self.choice.split(' ')[0] == 'record' or self.choice.split(' ')[0] == 'monitor':

            # get units
            units = ''
            try:
                if(self.choice.split(' ')[1].lower() == 'w'):
                    units = 'W'
                elif(self.choice.split(' ')[1].lower() == 'dbm'):
                    units = 'dBm'
                else:
                    print("\n\nInvalid units. Valid units are W, dBm, and kW.")

            # if no units are entered, use kW
            except:
                print("\n\nUsing kW as default units")
                units = "kW"

            print("\n\nPress Ctrl+C to stop " + self.choice.split(' ')[0] + "ing.\n\n")
                
            if self.choice.split(' ')[0] == 'record':
                self.record(units)
            else:
                self.monitor(units)

        # check if it is switch
        elif self.choice.split(' ')[0] == 'switch':

            # sanitize inputs
            try:
                direction = self.choice.split(' ')[1]
                transmitter = self.choice.split(' ')[2]
            except:
                print("\nInvalid values entered")
                return

            # check for any of the lots of possible choices for direction input
            if ((direction != 't') and \
                (direction != 'r') and \
                (direction != 'transmitted') and \
                (direction != 'reflected') and \
                (direction != 'forward') and \
                (direction != 'f') and \
                (direction != 'trans') and \
                (direction != 'ref')):
                    print("\nEnter either \'t\' or \'r\' to indicate which switch to set.")
                    return

            # ensure the transmitter is an input
            try:
                transmitter = int(transmitter)
            except:
                print("\nEnter a valid transmitter number.")
                return

            # ensure the transmitter is in range 1-6
            if transmitter < 1 or transmitter > 6:
                print("\nEnter a valid transmitter number.")
            
            # set the switch
            self.switch(direction, transmitter)

        # check if settings is called
        elif self.choice.split(' ')[0] == 'settings':

            # check if the user is trying to change settings
            try:
                if self.choice.split(' ')[1] == 'change':

                    # get the arguments after "change"
                    try:
                        self.change_settings(self.choice.split(' ')[2], self.choice.split(' ')[3])
                    # if arguments after "change" are invalid, end
                    except IndexError:
                        print("\n\nInvalid arguments")
                    # for any other errors, just open settings
                    except:
                        self.open_settings()
            # if change is not there, the user didn't enter it
            except IndexError:
                self.open_settings()

        # checks for copy input
        elif self.choice == 'copy':
            self.copy_recorded_data()
        # checks for help input
        elif self.choice == 'help':
            self.display_command_bar()
        # checks for quit
        elif self.choice == 'quit':
            quit()
        else:
            print("\n\nInvalid Command")

        return

    def record(self, units):
        # called when record is typed
        self.get_power_array("rec_all", units)

    def monitor(self, units):
        # called when monitor is typed
        self.get_power_array("mon_all", units)

    def get_power_array(self, cmd, units):
        '''
        Receives power readings from the Raspberry Pi and outputs the values to the display.
        '''

        # array used to hold values from the RPi
        output_array = []

        # arguments sent to the RPi's monitor function
        args = [cmd, self.timeout_secs, self.sample_time, self.decoder_pins, self.transmitted_ip, \
            self.reflected_ip, self.transmitted_enabled, self.reflect_enabled]

        if self.sock_connect():

            if self.sock_send(args):

                print("HH:MM:SS.SSS   |   Tx1   ,   Rx1     |   Tx2  ,   Rx2     |   Tx3  ,   Rx3     |   " + \
                    "Tx4  ,   Rx4     |   Tx5  ,  Rx5     |    Tx6  ,   Rx6     | sample duration")

                # do while indicating recording
                while True:
                    try:
                        # receive data file from the server
                        received = self.sock.recv(1024)

                        # unpack data file into array
                        output_array = pickle.loads(received)

                        # convert the power to the requested units
                        total_power = self.convert_units(output_array, units)

                        # get the total power for transmitted and reflected
                        total_transmitted = total_power[0]
                        total_reflected = total_power[1]

                        # time sample started
                        print(output_array[0] + "      ", end='')

                        # transmitted and reflected powers
                        for i in range(1, 7):
                            print(output_array[i].rjust(7) + ", ", end='')
                            print(output_array[i+6].rjust(7), end='')
                            print("     ", end='')

                        # sample duration
                        print(output_array[13])

                    # on Ctrl+C pressed, close socket and goto main
                    except KeyboardInterrupt:
                        self.sock.close()
                        return

    def switch(self, direction, transmitter):
        '''
        Sanitizes inputs and sends data to the RPi to switch the RF switch to an input.
        '''

        if self.sock_connect():
            if (direction == 't' or direction == 'transmitted' or direction == 'forward' or \
                direction == 'f' or direction == 'trans'):
                dir_str = "Transmitted"
                args = ['set_switch', transmitter, 11, 12, 13]
            else:
                dir_str = "Reflected"
                args = ['set_switch', transmitter, 15, 16, 18]

            # transfer the arguments via a pickle file and send them
            if self.sock_send(args):

                received = self.sock.recv(1024)
                output_array = pickle.loads(received)

                if output_array[0] == 'success':
                    print("\n" + dir_str + " switch set to " + str(transmitter))
                else:
                    print("\nError setting switch")

            # if the send failed
            else:
                print("Error communicating")

        # if the client could not connect to the Raspberry Pi
        else:
            print("Error communicating")
        
        return

    def open_settings(self):
        '''
        Prints out settings options when called.
        '''

        print("\n\n1) Get Transmitted Power: " + str(self.transmitted_enabled))
        print("2) Get Reflected Power: " + str(self.reflect_enabled))
        print("3) Transmitted Power Meter IP: " + self.transmitted_ip)
        print("4) Reflected Power Meter IP: " + self.reflected_ip)
        print("5) Raspberry Pi IP: " + self.rpi_ip)
        print("6) Local filepath to store data: " + self.data_filepath)
        print("7) Sampling Period: " + str(self.sample_time))

        print("\nTo modify a setting, type \"settings change [num] [desired value]\".")

    def change_settings(self, num, val):
        '''
        Called when the settings should be changed. Sanitizes input and converts settings.
        '''

        try:
            num = float(num)
            if (num < 1 or num > 7):
                print("\n\nInvalid number for [num] argument")
                return
        except:
            print("\n\nInvalid entry for [num] argument")
            return

        if num == 1:
            self.transmitted_enabled = (val.lower() == "true" or val.lower() == "1" or val.lower() == "t")
            print("\n\nGet Transmitted Power changed to "+str(self.transmitted_enabled))
        elif num == 2:
            self.reflect_enabled = (val.lower() == "true" or val.lower() == "1" or val.lower() == "t")
            print("\n\nGet Reflected Power changed to "+str(self.reflect_enabled))
        elif num == 3:
            self.transmitted_ip = val
            print("\n\nTransmitted Power Meter IP changed to "+self.transmitted_ip)
        elif num == 4:
            self.reflected_ip = val
            print("\n\nReflected Power Meter IP changed to "+self.reflected_ip)
        elif num == 5:
            self.rpi_ip = val
            print("\n\nRaspberry Pi IP changed to "+self.rpi_ip)
        elif num == 6:
            self.data_filepath = val
            print("\n\nLocal filepath changed to "+self.data_filepath)
        elif num == 7:
            self.sample_time = float(val)
            print("\n\nSampling period changed to "+str(self.sample_time))

        self.save_settings()
        self.load_settings()

    def load_settings(self):
        '''
        Loads values from a pickle file. This allows for settings to be modified from the GUI
        and be persistent at the next program launch.
        '''

        # attempt to read the saved data from the pickle file and load the values
        try:
            # read the file
            with open('gui_settings.pckl', "rb") as f:
                # data is a dictionary containing settings
                data = pickle.load(f)

            # load the settings into their proper variables
            self.transmitted_enabled = data["trans_en"] == 1
            self.reflect_enabled = data["ref_en"] == 1
            self.transmitted_ip = data["trans_ip"]
            self.reflected_ip = data["ref_ip"]
            self.rpi_ip = data["rpi_ip"]
            self.data_filepath = data["data_filepath"]
            self.sample_time = data["sample"]
            self.timeout_secs = data["timeout"]

        # if there is an error, load default values for the program
        except Exception as e:

            print("\n\nWARNING:\nError loading settings. Default settings loaded.\n")
            print("Check the program settings to ensure the settings are correct (\"settings\" command).")

            print(str(e))

            # set values
            self.transmitted_enabled = 1
            self.reflect_enabled = 1
            self.transmitted_ip = "192.168.100.152"
            self.reflected_ip = "192.168.100.153"
            self.rpi_ip = "192.168.100.156"
            self.data_filepath = "home/"
            self.sample_time = (1)
            self.timeout_secs = (1)

    def save_settings(self):
        '''
        Sanitizes and saves the program settings on close of the settings window.
        '''

        # check that sample_time and timeout are both valid floats
        try:
            float(self.sample_time)
            float(self.timeout_secs)
        except:
            print(
                    "Field Error" + \
                    "Enter a valid decimal number."
                )
            return

        # check that sample_time and timeout are both greater than 0
        if self.sample_time < 0 or self.timeout_secs < 0:
            print("FIELD ERROR: Enter a positive decimal number.")
            return

        # save the data
        try:
            data = {
                "trans_en": self.transmitted_enabled,
                "ref_en": self.reflect_enabled,
                "trans_ip": self.transmitted_ip,
                "ref_ip": self.reflected_ip,
                "rpi_ip": self.rpi_ip,
                "data_filepath": self.data_filepath,
                "sample": self.sample_time,
                "timeout": self.timeout_secs,
            }

            # dump the data into a settings file
            with open('gui_settings.pckl', "wb") as f:
                pickle.dump(data, f)

        except:
            print("SAVE ERROR: Error saving values: " + str(e))

    def copy_recorded_data(self):
        '''
        Copies data stored on the Raspberry Pi at /home/pi/hfmon/data to a directory specified
        on the user's computer via an scp call.
        '''

        print("\nYou may need to enter the system password and/or the Raspberry Pi password (\"raspberry\" by default).")

        subprocess.call(['sudo', 'scp', '-r', "pi@" + self.rpi_ip +":/home/pi/hfmon/data", self.data_filepath])

        print("\n\nData Copied to " + self.data_filepath + "data.")

    def convert_units(self, output_array, units):
        '''
        Takes in an input array formatted as 
        [time sampling started, Tx1, Rx1, Tx2, Rx2, ... , Rx6, time for sample],
        converts each power value to the requested units, and updates the GUI accordingly.

        The input powers are in dBm.
        '''

        if units == 'dBm':
            for i in range(1, 13):
                # ensure the value is a number (negative or decimal)
                try:
                    if(float(output_array[i])) < -35:
                        output_array[i] = "-99.000"
                    else:
                        output_array[i] = "%.3f" % float(output_array[i])
                except:
                    pass

            # set up calculations for the total transmitted power
            transmitted_array = output_array[1:7]
            total_transmitted = 0
            # iterate over all transmitted power elements (last value is time, ignore it)
            for power in transmitted_array:
                try:
                    # convert each power to watts to add them together
                    power = pow(10, float(power) / 10) / 1000
                    total_transmitted += float(power)
                except:
                    pass
            # if the power is sufficiently small, assume it is very close to 0
            if total_transmitted < .00001:
                transmitted_dbm = '%.3f' % -99.000

            # otherwise, convert from watts back to dBm
            else:
                transmitted_dbm = "%.3f" % (10 * math.log10(total_transmitted) + 30)

            # calculate the total reflected power in the same way as transmitted power
            reflected_array = output_array[7:13]
            total_reflected = 0
            for power in reflected_array:
                try:
                    power = pow(10, float(power) / 10) / 1000
                    total_reflected += float(power) 
                except:
                    pass
            if total_reflected < .00001:
                reflected_dbm = '%.3f' % -99.000
            else:
                reflected_dbm = "%.3f" % (10 * math.log10(total_reflected) + 30)

            total_transmitted = transmitted_dbm
            total_reflected = reflected_dbm

        elif units == 'W':
            for i in range(1, 13):
                if(str(output_array[i]).replace('.','',1).replace('-','').isdigit()):
                    output_array[i] = "%.0f" % (pow(10, float(output_array[i]) / 10) / 1000)

            transmitted_array = output_array[1:7]
            total_transmitted = 0

            for power in transmitted_array:
                try:
                    total_transmitted += float(power)
                except:
                   pass

            reflected_array = output_array[7:13]
            total_reflected = 0

            for power in reflected_array:
                try:
                    total_reflected += float(power)
                except:
                    pass

            total_transmitted = '%.1f' % total_transmitted
            total_reflected = '%.1f' % total_reflected

        # kW is the default case
        else:
            # if the value is a digit, convert it from dBm to kW
            for i in range(1, 13):
                if(str(output_array[i]).replace('.','').replace('-','').isdigit()):
                    output_array[i] = "%.3f" % (pow(10, float(output_array[i]) / 10) / 1000000)

            # add each individual power in kW to get the total power
            transmitted_array = output_array[1:7]
            total_transmitted = 0
            for power in transmitted_array:
                try:
                    total_transmitted += float(power)
                except:
                    pass

            # calculate reflected power the same way
            reflected_array = output_array[7:13]
            total_reflected = 0
            for power in reflected_array:
                try:
                    total_reflected += float(power)
                except:
                    pass

            total_transmitted = '%.3f' % total_transmitted
            total_reflected = '%.3f' % total_reflected

        return [total_transmitted, total_reflected]


terminal_window = hf_terminal()