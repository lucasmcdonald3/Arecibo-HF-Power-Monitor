#!usr/bin/env python3

'''
    File: hf_gui_settings.py
    Description: GUI for the main program settings window. This does not
        contain any logic; all logic is handled by hf_gui_main.py.
    Author: Lucas McDonald
    Date created: June 26, 2017
    Date modified: July 10, 2017
    Python version: 3.6.1
'''

import tkinter

class HFSettingsGUI():
    
    def __init__(self, parent):
        '''
        Called by the main GUI window when the Program Settings button is pressed.
        Opens a window containing program settings.
        '''

        # parent is the main window
        self.parent = parent

        # create the window and its title
        self.settings_view = tkinter.Toplevel(master=self.parent.form)
        self.settings_view.title('Monitor Program Settings')

        # reload the program settings
        self.parent.load_settings()

        # create the main box
        self.transmitter_settings_box = tkinter.LabelFrame(self.settings_view, text=" Connection Settings ", \
            font=(None,self.parent.font_size))
        self.transmitter_settings_box.grid(row=0, columnspan=7, sticky='W', padx=10, pady=20, ipadx=5, ipady=5)

        # create checkboxes for getting power from transmitted and reflected meters
        self.transmitted_enabled_box = tkinter.Checkbutton(self.transmitter_settings_box, text = "Get Transmitted Power", \
            font=(None,self.parent.font_size), variable = self.parent.transmitted_enabled_variable)
        self.transmitted_enabled_box.grid(row = 0, column = 0, sticky='W', padx = self.parent.x_padding, pady = self.parent.y_padding)

        self.reflected_enabled_box = tkinter.Checkbutton(self.transmitter_settings_box, text = "Get Reflected Power", \
            font=(None,self.parent.font_size), variable = self.parent.reflect_enabled_variable)
        self.reflected_enabled_box.grid(row = 1, column = 0, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        # ip fields for the transmitted and reflected power meters as well as the RPi
        self.transmitted_ip_label = tkinter.Label(self.transmitter_settings_box, text = "Transmitted Power Meter IP: ", \
            font=(None,self.parent.font_size))
        self.transmitted_ip_label.grid(row=2, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.transmitted_ip_field = tkinter.Entry(self.transmitter_settings_box, textvariable = self.parent.transmitted_ip_variable)
        self.transmitted_ip_field.grid(row = 2, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        self.reflected_ip_label = tkinter.Label(self.transmitter_settings_box, text = "Reflected Power Meter IP: ", \
            font=(None,self.parent.font_size))
        self.reflected_ip_label.grid(row=3, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.reflected_ip_field = tkinter.Entry(self.transmitter_settings_box, textvariable = self.parent.reflected_ip_variable)
        self.reflected_ip_field.grid(row = 3, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        self.rpi_ip_label = tkinter.Label(self.transmitter_settings_box, text = "Raspberry Pi IP: ", font=(None,self.parent.font_size))
        self.rpi_ip_label.grid(row=4, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.rpi_ip_field = tkinter.Entry(self.transmitter_settings_box, textvariable = self.parent.rpi_ip_variable)
        self.rpi_ip_field.grid(row = 4, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        # settings for sampling, i.e. sampling period and power meter timeout
        self.data_settings_box = tkinter.LabelFrame(self.settings_view, text=" Data Settings ", font=(None,self.parent.font_size))
        self.data_settings_box.grid(row=1, columnspan=7, sticky='W', padx=10, pady=20, ipadx=5, ipady=5)

        self.sample_time_label = tkinter.Label(self.data_settings_box, text = "Sampling period (seconds): ", \
            font=(None,self.parent.font_size))
        self.sample_time_label.grid(row=0, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.sample_time_field = tkinter.Entry(self.data_settings_box, textvariable = self.parent.sample_time_variable)
        self.sample_time_field.grid(row = 0, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        self.local_filepath_label = tkinter.Label(self.data_settings_box, text = "Local Data Filepath: ", font=(None,self.parent.font_size))
        self.local_filepath_label.grid(row=1, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.local_filepath_field = tkinter.Entry(self.data_settings_box, textvariable = self.parent.data_filepath)
        self.local_filepath_field.grid(row = 1, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')

        self.sample_time_label = tkinter.Label(self.settings_view, text = "A sampling period lower than 0.5 seconds can lead to an inaccurate\nsample rate. Enter 0 to sample as quickly as possible.", \
            font=(None,self.parent.font_size))
        self.sample_time_label.grid(row=2, column=0, padx=self.parent.x_padding, pady=20)
        '''
        # For displaying timeout field. Removed as it wasn't exactly necessary for the user to modify.
        self.timeout_time_label = tkinter.Label(self.data_settings_box, text = "Timeout period (seconds): ", \
            font=(None,self.parent.font_size))
        self.timeout_time_label.grid(row=2, column=0, padx=self.parent.x_padding, pady=self.parent.y_padding, sticky='W')

        self.timeout_time_field = tkinter.Entry(self.data_settings_box, textvariable = self.parent.timeout_secs_variable)
        self.timeout_time_field.grid(row = 2, column = 1, padx = self.parent.x_padding, pady = self.parent.y_padding, sticky='W')
        '''