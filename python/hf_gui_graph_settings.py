#!usr/bin/env python3

'''
    File: hf_gui_graph_settings.py
    Description: GUI for the graph settings window. This does not
        contain any logic; all logic is handled by hf_gui_graph.py.
    Author: Lucas McDonald
    Date created: June 26, 2017
    Date modified: August 2, 2017
    Python version: 3.6.1
'''

import tkinter

class HFGraphSettingsGUI():

    def __init__(self, parent):
        '''
        Called when the Graph Settings button is pressed. Gives options for plotting each
        power and displaying length of the graph's x-axis.
        '''

        # parent is the graph GUI window
        self.parent = parent

        # create the graph settings window
        self.graph_settings_view = tkinter.Toplevel(master=self.parent.graph_view)
        self.graph_settings_view.title = 'Graph Settings'

        self.parent.load_graph_settings()

        # text labels for each transmitter
        self.trans_label = tkinter.Label(self.graph_settings_view, text = "Transmitter Number", font=(None,self.parent.parent.font_size))
        self.trans_label.grid(row=0, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_1_label = tkinter.Label(self.graph_settings_view, text = "1", font=(None,self.parent.parent.font_size))
        self.trans_1_label.grid(row=1, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_2_label = tkinter.Label(self.graph_settings_view, text = "2", font=(None,self.parent.parent.font_size))
        self.trans_2_label.grid(row=2, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_3_label = tkinter.Label(self.graph_settings_view, text = "3", font=(None,self.parent.parent.font_size))
        self.trans_3_label.grid(row=3, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_4_label = tkinter.Label(self.graph_settings_view, text = "4", font=(None,self.parent.parent.font_size))
        self.trans_4_label.grid(row=4, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_5_label = tkinter.Label(self.graph_settings_view, text = "5", font=(None,self.parent.parent.font_size))
        self.trans_5_label.grid(row=5, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.trans_6_label = tkinter.Label(self.graph_settings_view, text = "6", font=(None,self.parent.parent.font_size))
        self.trans_6_label.grid(row=6, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        # transmitted checkboxes
        self.tx_label = tkinter.Label(self.graph_settings_view, text = 'Transmitted', font=(None,self.parent.parent.font_size))
        self.tx_label.grid(row=0, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx1 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx1_plot_enabled)
        self.tx1.grid(row=1, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx2 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx2_plot_enabled)
        self.tx2.grid(row=2, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx3 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx3_plot_enabled)
        self.tx3.grid(row=3, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx4 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx4_plot_enabled)
        self.tx4.grid(row=4, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx5 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx5_plot_enabled)
        self.tx5.grid(row=5, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.tx6 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.tx6_plot_enabled)
        self.tx6.grid(row=6, column=1, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        # reflected checkboxes
        self.rx_label = tkinter.Label(self.graph_settings_view, text = 'Reflected', font=(None,self.parent.parent.font_size))
        self.rx_label.grid(row=0, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx1 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx1_plot_enabled)
        self.rx1.grid(row=1, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx2 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx2_plot_enabled)
        self.rx2.grid(row=2, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx3 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx3_plot_enabled)
        self.rx3.grid(row=3, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx4 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx4_plot_enabled)
        self.rx4.grid(row=4, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx5 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx5_plot_enabled)
        self.rx5.grid(row=5, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        self.rx6 = tkinter.Checkbutton(self.graph_settings_view, text = '', \
            font=(None,self.parent.parent.font_size), variable = self.parent.rx6_plot_enabled)
        self.rx6.grid(row=6, column=2, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding)

        # time shown label (x-axis length)
        self.time_shown_label = tkinter.Label(self.graph_settings_view, text = "Length of graph (sec): ", font=(None,self.parent.parent.font_size))
        self.time_shown_label.grid(row=7, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding, sticky='W')

        self.time_shown_field = tkinter.Entry(self.graph_settings_view, textvariable = self.parent.time_shown_variable)
        self.time_shown_field.grid(row = 7, column = 1, padx = self.parent.parent.x_padding, pady = self.parent.parent.y_padding, sticky='W')

        # update interval label (x-axis length)
        self.update_interval_label = tkinter.Label(self.graph_settings_view, text = "Graph update interval (sec): ", font=(None,self.parent.parent.font_size))
        self.update_interval_label.grid(row=8, column=0, padx=self.parent.parent.x_padding, pady=self.parent.parent.y_padding, sticky='W')

        self.update_interval_field = tkinter.Entry(self.graph_settings_view, textvariable = self.parent.graph_update_interval)
        self.update_interval_field.grid(row = 8, column = 1, padx = self.parent.parent.x_padding, pady = self.parent.parent.y_padding, sticky='W')