#!usr/bin/env python3

'''
    File: hf_gui_main.py
    Description: Class for the main GUI window for the HF monitoring system.
        Shows power information and time information for each sample, as well
        as controls and settings buttons. Handles the logic for communicating
        with the Raspberry Pi and loading the main settings for the program.
    Author: Lucas McDonald
    Date created: June 6, 2017
    Date modified: August 2, 2017
    Python version: 3.6.1
'''

import tkinter
from tkinter import messagebox
import socket
import take_data
import threading
import math
from hf_gui_settings import HFSettingsGUI
from hf_gui_graph import HFGraphGUI
import pickle
import subprocess
import sys

class HFMainGUI():

    def __init__(self):
        '''
        Called at the end of this file. Loads the main window. 
        '''

        # form is the main window
        self.form = tkinter.Tk()
        # it should not be resizable
        self.form.resizable(False, False)
        # set title of main window
        self.form.wm_title('HF Power Monitor')

        # persistent program settings
        self.transmitted_enabled_variable = tkinter.IntVar()
        self.reflect_enabled_variable = tkinter.IntVar()
        self.transmitted_ip_variable = tkinter.StringVar()
        self.reflected_ip_variable = tkinter.StringVar()
        self.rpi_ip_variable = tkinter.StringVar()
        self.data_filepath = tkinter.StringVar()
        self.sample_time_variable = tkinter.DoubleVar()
        self.timeout_secs_variable = tkinter.DoubleVar()

        self.load_settings()

        # ui layout settings
        self.x_padding = 30
        self.y_padding = 5
        self.font_size = 15

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

        # initialized here for class scope
        self.data_array = []
        self.sample_num = [0]

        # initalized for class scope; allows graph to be called or not called as needed
        self.graph_enabled = False
        self.settings_open = False

        # set all initial text to '---'
        self.tx1_text = tkinter.StringVar()
        self.tx1_text.set('---')

        self.tx2_text = tkinter.StringVar()
        self.tx2_text.set('---')

        self.tx3_text = tkinter.StringVar()
        self.tx3_text.set('---')

        self.tx4_text = tkinter.StringVar()
        self.tx4_text.set('---')

        self.tx5_text = tkinter.StringVar()
        self.tx5_text.set('---')

        self.tx6_text = tkinter.StringVar()
        self.tx6_text.set('---')

        self.rx1_text = tkinter.StringVar()
        self.rx1_text.set('---')

        self.rx2_text = tkinter.StringVar()
        self.rx2_text.set('---')

        self.rx3_text = tkinter.StringVar()
        self.rx3_text.set('---')

        self.rx4_text = tkinter.StringVar()
        self.rx4_text.set('---')

        self.rx5_text = tkinter.StringVar()
        self.rx5_text.set('---')

        self.rx6_text = tkinter.StringVar()
        self.rx6_text.set('---')

        self.tx_sum_text = tkinter.StringVar()
        self.tx_sum_text.set('---')

        self.rx_sum_text = tkinter.StringVar()
        self.rx_sum_text.set('---')

        self.hms_text = tkinter.StringVar()
        self.hms_text.set('---')

        self.hms_ms_text = tkinter.StringVar()
        self.hms_text.set('---')

        self.time_taken_text = tkinter.StringVar()
        self.time_taken_text.set('---')

        # set buttons and dropdowns to appropriate titles
        self.take_data_title = tkinter.StringVar()
        self.take_data_title.set('Record Power')

        self.monitor_title = tkinter.StringVar()
        self.monitor_title.set('Monitor Power')

        self.set_units_var = tkinter.StringVar()
        self.set_units_var.set("kW")
        self.unit_choices = ['kW', 'dBm', 'W']

        self.transmitted_label_text = tkinter.StringVar()
        self.transmitted_label_text.set('Transmitted (' + self.set_units_var.get() + ')')

        self.reflected_label_text = tkinter.StringVar()
        self.reflected_label_text.set('Reflected (' + self.set_units_var.get() + ')')

        # box containing power information
        self.power_info_box = tkinter.LabelFrame(self.form, text=" Power Information ", font=(None,self.font_size))
        self.power_info_box.grid(row=0, columnspan=3, sticky='W', \
            padx=5, pady=10, ipadx=5, ipady=5)

        # text labels for each transmitter
        self.trans_label = tkinter.Label(self.power_info_box, text = "Transmitter Number", font=(None,self.font_size))
        self.trans_label.grid(row=0, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_1_label = tkinter.Label(self.power_info_box, text = "1", font=(None,self.font_size))
        self.trans_1_label.grid(row=1, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_2_label = tkinter.Label(self.power_info_box, text = "2", font=(None,self.font_size))
        self.trans_2_label.grid(row=2, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_3_label = tkinter.Label(self.power_info_box, text = "3", font=(None,self.font_size))
        self.trans_3_label.grid(row=3, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_4_label = tkinter.Label(self.power_info_box, text = "4", font=(None,self.font_size))
        self.trans_4_label.grid(row=4, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_5_label = tkinter.Label(self.power_info_box, text = "5", font=(None,self.font_size))
        self.trans_5_label.grid(row=5, column=0, padx=self.x_padding, pady=self.y_padding)

        self.trans_6_label = tkinter.Label(self.power_info_box, text = "6", font=(None,self.font_size))
        self.trans_6_label.grid(row=6, column=0, padx=self.x_padding, pady=self.y_padding)

        self.total_label = tkinter.Label(self.power_info_box, text = "Total Power", font=(None,self.font_size))
        self.total_label.grid(row=7, column=0, padx=self.x_padding, pady=self.y_padding)

        # transmitted power indicators
        self.tx_label = tkinter.Label(self.power_info_box, textvariable = self.transmitted_label_text, font=(None,self.font_size))
        self.tx_label.grid(row=0, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx1 = tkinter.Label(self.power_info_box, textvariable = self.tx1_text, font=(None,self.font_size))
        self.tx1.grid(row=1, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx2 = tkinter.Label(self.power_info_box, textvariable = self.tx2_text, font=(None,self.font_size))
        self.tx2.grid(row=2, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx3 = tkinter.Label(self.power_info_box, textvariable = self.tx3_text, font=(None,self.font_size))
        self.tx3.grid(row=3, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx4 = tkinter.Label(self.power_info_box, textvariable = self.tx4_text, font=(None,self.font_size))
        self.tx4.grid(row=4, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx5 = tkinter.Label(self.power_info_box, textvariable = self.tx5_text, font=(None,self.font_size))
        self.tx5.grid(row=5, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx6 = tkinter.Label(self.power_info_box, textvariable = self.tx6_text, font=(None,self.font_size))
        self.tx6.grid(row=6, column=1, padx=self.x_padding, pady=self.y_padding)

        self.tx_sum = tkinter.Label(self.power_info_box, textvariable = self.tx_sum_text, font=(None,self.font_size))
        self.tx_sum.grid(row=7, column=1, padx=self.x_padding, pady=self.y_padding)

        # reflected power indicators
        self.rx_label = tkinter.Label(self.power_info_box, textvariable = self.reflected_label_text, font=(None,self.font_size))
        self.rx_label.grid(row=0, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx1 = tkinter.Label(self.power_info_box, textvariable = self.rx1_text, font=(None,self.font_size))
        self.rx1.grid(row=1, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx2 = tkinter.Label(self.power_info_box, textvariable = self.rx2_text, font=(None,self.font_size))
        self.rx2.grid(row=2, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx3 = tkinter.Label(self.power_info_box, textvariable = self.rx3_text, font=(None,self.font_size))
        self.rx3.grid(row=3, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx4 = tkinter.Label(self.power_info_box, textvariable = self.rx4_text, font=(None,self.font_size))
        self.rx4.grid(row=4, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx5 = tkinter.Label(self.power_info_box, textvariable = self.rx5_text, font=(None,self.font_size))
        self.rx5.grid(row=5, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx6 = tkinter.Label(self.power_info_box, textvariable = self.rx6_text, font=(None,self.font_size))
        self.rx6.grid(row=6, column=2, padx=self.x_padding, pady=self.y_padding)

        self.rx_sum = tkinter.Label(self.power_info_box, textvariable = self.rx_sum_text, font=(None,self.font_size))
        self.rx_sum.grid(row=7, column=2, padx=self.x_padding, pady=self.y_padding)

        # information about the time taken during each sample
        self.time_info_box = tkinter.LabelFrame(self.form, text=" Time Information ", font=(None,self.font_size))
        self.time_info_box.grid(row=1, column = 0, columnspan=3, \
            padx=5, pady=10, ipadx=5, ipady=5)

        self.hms_label = tkinter.Label(self.time_info_box, text = "Time Sample Started:", font=(None,self.font_size))
        self.hms_label.grid(row=0, column=0, padx=self.x_padding, pady=self.y_padding)

        self.hms_frame = tkinter.Frame(self.time_info_box)
        self.hms_frame.grid(row=0, column=1, padx=0, pady=self.y_padding, ipadx=0)
        self.hms_frame.grid_columnconfigure(2, minsize=0, pad=0)  # Here

        self.hms_ms = tkinter.Label(self.hms_frame, textvariable = self.hms_ms_text, font=(None,self.font_size), foreground='gray')
        self.hms_ms.grid(row=0, column=1, padx=0, pady=self.y_padding, sticky='E')

        self.hms = tkinter.Label(self.hms_frame, textvariable = self.hms_text, font=(None,self.font_size))
        self.hms.grid(row=0, column=0, padx=0, pady=self.y_padding, sticky='W')
        
        self.time_taken_label = tkinter.Label(self.time_info_box, text = "Sample Duration:", font=(None,self.font_size))
        self.time_taken_label.grid(row=1, column=0, padx=self.x_padding, pady=self.y_padding)

        self.time_taken = tkinter.Label(self.time_info_box, textvariable = self.time_taken_text, font=(None,self.font_size))
        self.time_taken.grid(row=1, column=1, padx=self.x_padding, pady=self.y_padding)

        # controls box
        self.data_control_box = tkinter.LabelFrame(self.form, text=" Data Controls ", font=(None,self.font_size))
        self.data_control_box.grid(row=4, columnspan=7, sticky='W', \
            padx=10, pady=20, ipadx=5, ipady=5)

        # button to write data and monitor power
        self.take_data_button = tkinter.Button(self.data_control_box, textvariable = self.take_data_title, \
            command = self.record_power_pressed, font = (None,self.font_size))
        self.take_data_button.grid(row=0, column=0, padx=self.x_padding, pady=self.y_padding)

        # button to monitor power without writing data
        self.monitor_transmitters_button = tkinter.Button(self.data_control_box, textvariable = self.monitor_title, \
            command = self.monitor_power_pressed, font = (None,self.font_size))
        self.monitor_transmitters_button.grid(row=0, column=1, padx=self.x_padding, pady=self.y_padding)

        # allows user to select displayed unis
        self.set_units_menu = tkinter.OptionMenu(self.data_control_box, self.set_units_var, *self.unit_choices)
        self.set_units_menu.configure(font=(None,self.font_size))
        self.set_units_menu.grid(row = 0, column = 3, padx = self.x_padding, pady = self.y_padding)

        # program controls box
        self.program_control_box = tkinter.LabelFrame(self.form, text=" Program Controls ", font=(None,self.font_size))
        self.program_control_box.grid(row=5, columnspan=7, sticky='W', \
            padx=10, pady=20, ipadx=5, ipady=5)

        # button to copy data files
        self.copy_data = tkinter.Button(self.program_control_box, text = "Copy Recorded Data", font = (None,self.font_size), \
            command = self.get_data_pressed)
        self.copy_data.grid(row = 0, column = 0, padx = self.x_padding-15, pady = self.y_padding)

        # button to open the settings menu
        self.settings_button = tkinter.Button(self.program_control_box, text = "Program Settings", font = (None,self.font_size), \
            command = self.settings_pressed)
        self.settings_button.grid(row = 0, column = 1, padx = self.x_padding-15, pady = self.y_padding)

        # button to show a graph of the power
        self.graph_button = tkinter.Button(self.program_control_box, text = "View Power Graph", font = (None,self.font_size), \
            command = self.graph_pressed)
        self.graph_button.grid(row = 0, column = 2, padx = self.x_padding-15, pady = self.y_padding)

        self.form.mainloop()

    def update_ui(self, output_array, total_transmitted, total_reflected):
        '''
        Updates UI elements based on the output from take_data.py. Sets the text
        of labels and updates the plots.
        '''
        
        self.hms_text.set(output_array[0][:8])
        self.hms_ms_text.set(output_array[0][8:])

        # set the text of each power label. if the label shows no power, display it as grey text.
        self.tx1_text.set(output_array[1])
        if(output_array[1] == "-99.000" or output_array[1] == "0.000" or output_array[1] == "0.0"):
            self.tx1.configure(foreground="gray")
        else:
            self.tx1.configure(foreground="black")
        self.rx1_text.set(output_array[7])
        if(output_array[7] == "-99.000" or output_array[7] == "0.000" or output_array[7] == "0.0"):
            self.rx1.configure(foreground="gray")
        else:
            self.rx1.configure(foreground="black")
        self.tx2_text.set(output_array[2])
        if(output_array[2] == "-99.000" or output_array[2] == "0.000" or output_array[2] == "0.0"):
            self.tx2.configure(foreground="gray")
        else:
            self.tx2.configure(foreground="black")
        self.rx2_text.set(output_array[8])
        if(output_array[8] == "-99.000" or output_array[8] == "0.000" or output_array[8] == "0.0"):
            self.rx2.configure(foreground="gray")
        else:
            self.rx2.configure(foreground="black")
        self.tx3_text.set(output_array[3])
        if(output_array[3] == "-99.000" or output_array[3] == "0.000" or output_array[3] == "0.0"):
            self.tx3.configure(foreground="gray")
        else:
            self.tx3.configure(foreground="black")
        self.rx3_text.set(output_array[9])
        if(output_array[9] == "-99.000" or output_array[9] == "0.000" or output_array[9] == "0.0"):
            self.rx3.configure(foreground="gray")
        else:
            self.rx3.configure(foreground="black")
        self.tx4_text.set(output_array[4])
        if(output_array[4] == "-99.000" or output_array[4] == "0.000" or output_array[4] == "0.0"):
            self.tx4.configure(foreground="gray")
        else:
            self.tx4.configure(foreground="black")
        self.rx4_text.set(output_array[10])
        if(output_array[10] == "-99.000" or output_array[10] == "0.000" or output_array[10] == "0.0"):
            self.rx4.configure(foreground="gray")
        else:
            self.rx4.configure(foreground="black")
        self.tx5_text.set(output_array[5])
        if(output_array[5] == "-99.000" or output_array[5] == "0.000" or output_array[5] == "0.0"):
            self.tx5.configure(foreground="gray")
        else:
            self.tx5.configure(foreground="black")
        self.rx5_text.set(output_array[11])
        if(output_array[11] == "-99.000" or output_array[11] == "0.000" or output_array[11] == "0.0"):
            self.rx5.configure(foreground="gray")
        else:
            self.rx5.configure(foreground="black")
        self.tx6_text.set(output_array[6])
        if(output_array[6] == "-99.000" or output_array[6] == "0.000" or output_array[6] == "0.0"):
            self.tx6.configure(foreground="gray")
        else:
            self.tx6.configure(foreground="black")
        self.rx6_text.set(output_array[12])
        if(output_array[12] == "-99.000" or output_array[12] == "0.000" or output_array[12] == "0.0"):
            self.rx6.configure(foreground="gray")
        else:
            self.rx6.configure(foreground="black")

        # if there is some sort of an error, display nothing for the sum
        self.tx_sum_text.set(total_transmitted)
        for i in range (1, 7):
            if(output_array[i] == '      '):
                self.tx_sum_text.set('      ')

        self.rx_sum_text.set(total_reflected)
        for i in range (7, 13):
            if(output_array[i] == '      '):
                self.rx_sum_text.set('      ')
            
        # time taken is the last element
        self.time_taken_text.set(output_array[-1])

        self.transmitted_label_text.set('Transmitted (' + self.set_units_var.get() + ')')
        self.reflected_label_text.set('Reflected (' + self.set_units_var.get() + ')')

    def convert_units(self, output_array):
        '''
        Takes in an input array formatted as 
        [time sampling started, Tx1, Rx1, Tx2, Rx2, ... , Rx6, time for sample],
        converts each power value to the requested units, and updates the GUI accordingly.

        The input powers are in dBm.
        '''

        units = self.set_units_var.get()

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

        
        elif units == 'kW':
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

        elif units == 'W':
            for i in range(1, 13):
                if(str(output_array[i]).replace('.','',1).replace('-','').isdigit()):
                    output_array[i] = "%.1f" % (pow(10, float(output_array[i]) / 10) / 1000)

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

        return [total_transmitted, total_reflected]

    def get_power_array(self, cmd):
        '''
        This function calls the Raspberry Pi to get the power meters. It sets up
        a TCP connection that the RPi uses to send data. The RPi handles setting the
        HMC252 switches and reading the power meters. It returns the values via the
        socket, which the client program uses to update the UI.
        '''
        
        # create a socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            # connect to server
            sock.connect((self.rpi_ip_variable.get(), 12345))
        # handle server software not running on Raspberry Pi
        except ConnectionRefusedError:
            tkinter.messagebox.showwarning(
                    "Connection Refused",
                    "Connection Refused\n\nEnsure the server software is running on the Raspberry Pi."
                )
            self.monitor_title.set('Monitor Power')
            self.take_data_title.set('Record Power')
            return

        # handle Raspberry Pi not being on
        except socket.timeout:
            tkinter.messagebox.showwarning(
                    "Connection Timeout",
                    "Connection Timeout\n\nEnsure the Raspberry Pi is powered on and connected to the network."
                )
            self.monitor_title.set('Monitor Power')
            self.take_data_title.set('Record Power')
            return

        # handle any other errors
        except:
            tkinter.messagebox.showwarning(
                    (str(sys.exc_info()[0]).replace(">", "").replace("<","").split(" ")[1]),
                    (str(sys.exc_info()[0]).replace(">", "").replace("<","").split(" ")[1]) + ":\n\n" + str(sys.exc_info()[1])
                )
            self.monitor_title.set('Monitor Power')
            self.take_data_title.set('Record Power')
            return
 
        # array used to hold values from the RPi
        output_array = []

        # arguments sent to the RPi's monitor function
        args = [cmd, self.timeout_secs_variable.get(), \
        self.sample_time_variable.get(), self.decoder_pins, self.transmitted_ip_variable.get(), \
        self.reflected_ip_variable.get(), self.transmitted_enabled_variable.get(), \
        self.reflect_enabled_variable.get()]

        # transfer the arguments via a pickle file and send them
        pickled_args = pickle.dumps(args)
        sock.sendall(pickled_args)

        # do while indicating recording
        while self.monitor_title.get() == 'Stop Monitoring' or self.take_data_title.get() == 'Stop Recording':

            # receive data file from the server
            received = sock.recv(1024)

            # unpack data file into array
            try:
                output_array = pickle.loads(received)

                # convert the power to the requested units
                total_power = self.convert_units(output_array)

                # get the total power for transmitted and reflected
                total_transmitted = total_power[0]
                total_reflected = total_power[1]

                # update the UI according to the power and units
                ui_thread = threading.Thread(target = self.update_ui, args = [output_array, \
                    total_transmitted, total_reflected])
                ui_thread.start()

                # if the graph window is visible, graph the results
                if self.graph_enabled:
                    graph_thread = threading.Thread(target = self.graph_window.update_graph, args = [output_array])
                    graph_thread.start()
            except EOFError:
                print("The previous data output was corrupted. Only the last output was corrupted; future outputs should be successful.")
                if cmd == "rec_all":
                    print("The data array was written to file successfully.")
            except:
                pass

    def monitor_power_pressed(self):
        '''
        Called when the "Record Power" button is pressed. Gets power from each power meter
        and updates the UI accordingly.
        '''

        # if not already recording or monitoring, start monitoring
        if self.monitor_title.get() == 'Monitor Power' and self.take_data_title.get() == 'Record Power':

            # indicate that it is monitoring
            self.monitor_title.set('Stop Monitoring')

            # multithread this to ensure the UI is responsive
            t = threading.Thread(target = self.get_power_array, args = ['mon_all'])
            t.start()

        # if already recording or monitoring, do nothing or stop monitoring
        else:
            self.monitor_title.set('Monitor Power')

    def record_power_pressed(self):
        '''
        Called when the "Record Power" button is pressed. Gets power from each power meter,
        writes the power to a file, and updates the UI accordingly. Also writes to a datafile
        on the Raspberry Pi.
        '''

        # if not already recording or monitoring, start monitoring
        if self.take_data_title.get() == 'Record Power' and self.monitor_title.get() == 'Monitor Power':

            # indicate that it is recording
            self.take_data_title.set('Stop Recording')

            # multithread this to ensure the UI is responsive
            t = threading.Thread(target = self.get_power_array, args = ['rec_all'])
            t.start()

        # if already recording or monitoring, do nothing or stop monitoring
        else:
            self.take_data_title.set('Record Power')

    def graph_pressed(self):
        '''
        Called when the graph button is pressed. Opens a graph window.
        '''

        # if a graph window is already open, bring it into the top view but don't open a new window
        if self.graph_enabled:
            self.graph_window.graph_view.focus()

        # otherwise, create a new window
        else:
            self.graph_window = HFGraphGUI(self)

            # tell main window that a graph window is open, so another shouldn't be opened
            self.graph_enabled = True

            # call graph_closed on close to ensure proper closure
            self.graph_window.graph_view.protocol("WM_DELETE_WINDOW", self.graph_closed)

    def graph_closed(self):
        '''
        Called when the graph window is closed.
        '''

        # let the main window know that the graph is closed
        if not self.graph_enabled:
            self.graph_window.graph_view.destroy()
            self.graph_pressed()
            return
        else:
            self.graph_enabled = False
            # close the graph window
            self.graph_window.graph_view.destroy()
        return

        

    def get_data_pressed(self):

        tkinter.messagebox.showwarning(
                    "Check Terminal",
                    "Check the terminal.\n\nYou may need to enter the root password and the " + \
                    "Raspberry Pi password (\"raspberry\" by default)."
                )

        subprocess.call(['sudo', 'scp', '-r', "pi@" + self.rpi_ip_variable.get()+":/home/pi/hfmon/data", self.data_filepath.get()])

        tkinter.messagebox.showwarning(
                    "Data Copied",
                    "Check the terminal and the local file location to ensure data was successfully copied."
                )

    def settings_pressed(self):
        '''
        Called when the settings button is pressed. Creates a settings window.
        '''

        # settings window can only be opened if the program is not monitoring the power meters.
        # the program must resend the settings to the RPi, so the monitoring must be restarted.
        if self.take_data_title.get() == 'Record Power' and self.monitor_title.get() == 'Monitor Power':

            # if the window is already open, bring it into the top view but don't open a new window
            if self.settings_open:
                self.settings_window.settings_view.focus()

            # otherwise, create a new window
            else:
                self.settings_window = HFSettingsGUI(self)

                # ensure that data is saved on window close
                self.settings_window.settings_view.wm_protocol("WM_DELETE_WINDOW", self.settings_closed)

                # tell main window that a settings window is open, so another one shouldn't be opened
                self.settings_open = True

        # if monitoring the meters, tell the user to stop monitoring before opening settings
        else:
            tkinter.messagebox.showwarning(
                    "Settings Error",
                    "Please stop monitoring the power meters before changing program settings."
                )
            return

    def settings_closed(self):
        '''
        Sanitizes and saves the program settings on close of the settings window.
        '''

        # check that sample_time and timeout are both valid floats
        try:
            float(self.sample_time_variable.get())
            float(self.timeout_secs_variable.get())
        except:
            tkinter.messagebox.showwarning(
                    "Field Error",
                    "Enter a valid decimal number in each field."
                )
            return

        # check that sample_time and timeout are both greater than 0
        if self.sample_time_variable.get() < 0 or self.timeout_secs_variable.get() < 0:
            tkinter.messagebox.showwarning(
                    "Field Error",
                    "Enter a positive decimal number in each field."
                )
            return

        # save the data
        try:
            data = {
                "trans_en": self.transmitted_enabled_variable.get(),
                "ref_en": self.reflect_enabled_variable.get(),
                "trans_ip": self.transmitted_ip_variable.get(),
                "ref_ip": self.reflected_ip_variable.get(),
                "rpi_ip": self.rpi_ip_variable.get(),
                "data_filepath": self.data_filepath.get(),
                "sample": self.sample_time_variable.get(),
                "timeout": self.timeout_secs_variable.get(),
            }

            # dump the data into a settings file
            with open('gui_settings.pckl', "wb") as f:
                pickle.dump(data, f)

        # if there's an error, log it
        except Exception as e:
            tkinter.messagebox.showwarning(
                    "Save Error",
                    "Error saving values:\n\n" + str(e)
                )

        # remove the settings view
        self.settings_window.settings_view.destroy()

        # the settings window is closed, so let the main window know
        self.settings_open = False

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
            self.transmitted_enabled_variable.set(data["trans_en"])
            self.reflect_enabled_variable.set(data["ref_en"])
            self.transmitted_ip_variable.set(data["trans_ip"])
            self.reflected_ip_variable.set(data["ref_ip"])
            self.rpi_ip_variable.set(data["rpi_ip"])
            self.data_filepath.set(data["data_filepath"])
            self.sample_time_variable.set(data["sample"])
            self.timeout_secs_variable.set(data["timeout"])

        # if there is an error, load default values for the program
        except Exception as e:

            # display a warning to the user
            tkinter.messagebox.showwarning(
                    "Settings Error",
                    "Error loading saved values:\n\n" + str(e) + "\n\nResetting to default values."
                )

            # set values
            self.transmitted_enabled_variable.set(1)
            self.reflect_enabled_variable.set(1)
            self.transmitted_ip_variable.set("192.168.100.152")
            self.reflected_ip_variable.set("192.168.100.153")
            self.rpi_ip_variable.set("192.168.100.156")
            self.data_filepath.set("Desktop/")
            self.sample_time_variable.set(1)
            self.timeout_secs_variable.set(1)

# create the main window
main_gui = HFMainGUI()