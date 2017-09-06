#!usr/bin/env python3

'''
    File: hf_gui_graph.py
    Description: Class for the GUI window displaying a matplotlib graph of power over time
        for the HF transmitters.
    Author: Lucas McDonald
    Date created: June 26, 2017
    Date modified: August 2, 2017
    Python version: 3.6.1
'''

import tkinter
import matplotlib
matplotlib.use("TKAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter
from hf_gui_graph_settings import HFGraphSettingsGUI
import pickle
import threading
from datetime import datetime
import time

class HFGraphGUI():

    def __init__(self, parent):
        '''
        Called when the View Graph button on the main windowis pressed. Loads a new window with
        a matplotlib figure.Can plot transmitted and reflected power for each of the 6
        transmitters. Settings are controlled by the Graph Settings button on this menu.
        '''

        # parent is the main window
        self.parent = parent

        # start window by viewing each plot
        self.tx1_plot_enabled = tkinter.IntVar()
        self.tx2_plot_enabled = tkinter.IntVar()
        self.tx3_plot_enabled = tkinter.IntVar()
        self.tx4_plot_enabled = tkinter.IntVar()
        self.tx5_plot_enabled = tkinter.IntVar()
        self.tx6_plot_enabled = tkinter.IntVar()
        self.rx1_plot_enabled = tkinter.IntVar()
        self.rx2_plot_enabled = tkinter.IntVar()
        self.rx3_plot_enabled = tkinter.IntVar()
        self.rx4_plot_enabled = tkinter.IntVar()
        self.rx5_plot_enabled = tkinter.IntVar()
        self.rx6_plot_enabled = tkinter.IntVar()
        self.time_shown_variable = tkinter.StringVar()
        self.graph_update_interval = tkinter.DoubleVar()

        self.graph_settings_open = False

        self.load_graph_settings()

        self.tx1_plot_bool = self.tx1_plot_enabled.get() == 1
        self.tx2_plot_bool = self.tx2_plot_enabled.get() == 1
        self.tx3_plot_bool = self.tx3_plot_enabled.get() == 1
        self.tx4_plot_bool = self.tx4_plot_enabled.get() == 1
        self.tx5_plot_bool = self.tx5_plot_enabled.get() == 1
        self.tx6_plot_bool = self.tx6_plot_enabled.get() == 1
        self.rx1_plot_bool = self.rx1_plot_enabled.get() == 1
        self.rx2_plot_bool = self.rx2_plot_enabled.get() == 1
        self.rx3_plot_bool = self.rx3_plot_enabled.get() == 1
        self.rx4_plot_bool = self.rx4_plot_enabled.get() == 1
        self.rx5_plot_bool = self.rx5_plot_enabled.get() == 1
        self.rx6_plot_bool = self.rx6_plot_enabled.get() == 1

        self.plot_bool_array = [self.tx1_plot_bool, self.tx2_plot_bool, self.tx3_plot_bool, \
                                self.tx4_plot_bool, self.tx5_plot_bool, self.tx6_plot_bool, \
                                self.rx1_plot_bool, self.rx2_plot_bool, self.rx3_plot_bool, \
                                self.rx4_plot_bool, self.rx5_plot_bool, self.rx6_plot_bool]

        self.tx_graph_bool = False
        self.rx_graph_bool = False

        if (self.tx1_plot_bool or self.tx2_plot_bool or self.tx3_plot_bool or \
            self.tx4_plot_bool or self.tx5_plot_bool or self.tx6_plot_bool):
            self.tx_graph_bool = True

        if (self.rx1_plot_bool or self.rx2_plot_bool or self.rx3_plot_bool or \
            self.rx4_plot_bool or self.rx5_plot_bool or self.rx6_plot_bool):
            self.rx_graph_bool = True

        #create the graph window
        self.graph_view = tkinter.Toplevel(master=self.parent.form)
        self.graph_view.title = 'HF Power Graph'

        # create the graph figure
        self.prev_units = self.parent.set_units_var.get()

        self.reset_graph()

        self.sample_num = []
        # data_array holds the output values from monitor_power or record_power
        self.data_array = [[] for _ in range(14)]

        # button to open the settings menu
        self.graph_settings_button = tkinter.Button(self.graph_view, text = "Graph Settings", font = (None,self.parent.font_size), \
            command = self.graph_settings_pressed)
        self.graph_settings_button.grid(row = 2, column = 0, padx = 10, pady = 20)

    def create_plots(self):
        self.length_shown = float(self.time_shown_variable.get())
        if self.tx_graph_bool:
            self.create_tx_plot()
        if self.rx_graph_bool:
            self.create_rx_plot()

    def create_tx_plot(self):
        self.trans_figure = Figure(facecolor='white')

        if self.rx_graph_bool:
            self.trans_figure.set_size_inches(8, 5, forward=True)
        else:
            self.trans_figure.set_size_inches(12, 8, forward=True)

        # add the plot of each power
        self.trans_plot = self.trans_figure.add_subplot(111)

        # set the axes and title
        self.trans_plot.set_title('Transmitted Power')
        self.trans_plot.set_xlabel('Time (HH:MM:SS)')
        self.trans_plot.set_ylabel('Power ('+self.prev_units+')')
        self.trans_plot.grid(b=True, which='major', color='b', alpha=.3, linestyle='-')
        self.trans_plot.grid(b=True, which='minor', color='b', alpha=.3, linestyle='--')

        if self.tx1_plot_bool:
            self.tx1_plot, = self.trans_plot.plot([],[],'r', label = 'Tx1')
        if self.tx2_plot_bool:
            self.tx2_plot, = self.trans_plot.plot([],[], color = '#FF8C00', label = 'Tx2')
        if self.tx3_plot_bool:
            self.tx3_plot, = self.trans_plot.plot([],[],'y', label = 'Tx3')
        if self.tx4_plot_bool:
            self.tx4_plot, = self.trans_plot.plot([],[],'g', label = 'Tx4')
        if self.tx5_plot_bool:
            self.tx5_plot, = self.trans_plot.plot([],[],'b', label = 'Tx5')
        if self.tx6_plot_bool:
            self.tx6_plot, = self.trans_plot.plot([],[],'m', label = 'Tx6')

        self.tx_axes = self.trans_figure.gca()

        # a tk.DrawingArea
        self.trans_canvas = FigureCanvasTkAgg(self.trans_figure, master=self.graph_view)
        self.trans_canvas.show()
        self.trans_canvas.get_tk_widget().grid(row = 0, column = 0, padx=0)

    def create_rx_plot(self):
        self.ref_figure = Figure(facecolor='white')
        
        if self.tx_graph_bool:
            self.ref_figure.set_size_inches(8, 5, forward=True)
        else:
            self.ref_figure.set_size_inches(12, 8, forward=True)

        
        self.ref_plot = self.ref_figure.add_subplot(111)

        self.ref_plot.set_title('Reflected Power')
        self.ref_plot.set_xlabel('Time (HH:MM:SS)')
        self.ref_plot.set_ylabel('Power ('+self.prev_units+')')
        self.ref_plot.grid(b=True, which='major', color='b', alpha=.3, linestyle='-')
        self.ref_plot.grid(b=True, which='minor', color='b', alpha=.3, linestyle='--')

        if self.rx1_plot_bool:
            self.rx1_plot, = self.ref_plot.plot([],[],'r', label = 'Rx1')
        if self.rx2_plot_bool:
            self.rx2_plot, = self.ref_plot.plot([],[], color = '#FF8C00', label = 'Rx2')
        if self.rx3_plot_bool:
            self.rx3_plot, = self.ref_plot.plot([],[],'y', label = 'Rx3')
        if self.rx4_plot_bool:
            self.rx4_plot, = self.ref_plot.plot([],[],'g', label = 'Rx4')
        if self.rx5_plot_bool:
            self.rx5_plot, = self.ref_plot.plot([],[],'b', label = 'Rx5')
        if self.rx6_plot_bool:
            self.rx6_plot, = self.ref_plot.plot([],[],'m', label = 'Rx6')

        self.rx_axes = self.ref_figure.gca()

        # a tk.DrawingArea
        self.ref_canvas = FigureCanvasTkAgg(self.ref_figure, master=self.graph_view)
        self.ref_canvas.show()
        self.ref_canvas.get_tk_widget().grid(row = 1, column = 0, padx=10)

    def reset_graph(self):
        '''
        Resets the graph to initial settings. Called when the graph settings or the
        power units are changed.
        '''

        self.length_shown = float(self.time_shown_variable.get())

        # reset data as length has changed
        self.sample_num = []
        self.data_array = [[] for _ in range(15)]

        # done here as .get() can sometimes take a long time
        self.tx1_plot_bool = self.tx1_plot_enabled.get() == 1
        self.tx2_plot_bool = self.tx2_plot_enabled.get() == 1
        self.tx3_plot_bool = self.tx3_plot_enabled.get() == 1
        self.tx4_plot_bool = self.tx4_plot_enabled.get() == 1
        self.tx5_plot_bool = self.tx5_plot_enabled.get() == 1
        self.tx6_plot_bool = self.tx6_plot_enabled.get() == 1
        self.rx1_plot_bool = self.rx1_plot_enabled.get() == 1
        self.rx2_plot_bool = self.rx2_plot_enabled.get() == 1
        self.rx3_plot_bool = self.rx3_plot_enabled.get() == 1
        self.rx4_plot_bool = self.rx4_plot_enabled.get() == 1
        self.rx5_plot_bool = self.rx5_plot_enabled.get() == 1
        self.rx6_plot_bool = self.rx6_plot_enabled.get() == 1
        self.graph_update_interval_int = self.graph_update_interval.get()

        self.plot_bool_array = [self.tx1_plot_bool, self.tx2_plot_bool, self.tx3_plot_bool, \
                                self.tx4_plot_bool, self.tx5_plot_bool, self.tx6_plot_bool, \
                                self.rx1_plot_bool, self.rx2_plot_bool, self.rx3_plot_bool, \
                                self.rx4_plot_bool, self.rx5_plot_bool, self.rx6_plot_bool]

        if ((self.tx1_plot_bool or self.tx2_plot_bool or self.tx3_plot_bool or \
            self.tx4_plot_bool or self.tx5_plot_bool or self.tx6_plot_bool) != self.tx_graph_bool):
            self.parent.graph_enabled = False
            self.parent.graph_closed()
            return

        if ((self.rx1_plot_bool or self.rx2_plot_bool or self.rx3_plot_bool or \
            self.rx4_plot_bool or self.rx5_plot_bool or self.rx6_plot_bool) != self.rx_graph_bool):
            self.parent.graph_enabled = False
            self.parent.graph_closed()
            return

        self.create_plots()

        self.time_between_updates = 0

        # clear the previous plot as values/plots have changed
        if self.tx_graph_bool:
            self.trans_plot.clear()
        if self.rx_graph_bool:
            self.ref_plot.clear()

        self.create_plots()

    def update_graph(self, output_array):
        '''
        Plots a specified number of the last power recordings on a graph.
        The plot is realtime and displays both transmitted and reflected power.
        '''

        # if the units changed, reset the graph
        if not (self.prev_units == self.parent.set_units_var.get()):
            self.prev_units = self.parent.set_units_var.get()
            self.reset_graph()

        # update sample_num arrays
        try:
            # set new element to previous element + 1
            self.sample_num.append(self.sample_num[-1]+1)
        except:
            # if the array was just reinitalized, set first element to 0
            self.sample_num.append(0)                

        self.update_data_array(output_array, 0)

        # append the most recent output to each dataset
        for i in range(1, len(output_array)-2):
            if(self.plot_bool_array[i-1]):
                try:
                    float(output_array[i])
                except:
                    # if it isn't a number, set power to most recent power reading from transmitter
                    try:
                        output_array[i] = self.data_array[i][-1]
                    # if there's an error with this (e.g. no previous power readings), just set to 0
                    except:
                        output_array[i] = "0.000"

                self.update_data_array(output_array, i)

        self.update_data_array(output_array, -1)

        if self.length_shown < (datetime.strptime(self.data_array[0][-1], "%H:%M:%S.%f") - \
            datetime.strptime(self.data_array[0][0], "%H:%M:%S.%f")).total_seconds():
            del self.sample_num[0]
            del self.data_array[0][0] 
            for i in range(1, len(self.data_array)-2):
                if(self.plot_bool_array[i-1]):
                    del self.data_array[i][0] 
            del self.data_array[-1][0]


        if(self.time_between_updates < self.graph_update_interval_int):
            self.time_between_updates += float(self.data_array[-1][-1])
        else:
            self.time_between_updates = 0   
            if self.tx_graph_bool:
                # update the UI according to the power and units
                trans_thread = threading.Thread(target = self.update_tx_graph)
                trans_thread.start()
            if self.rx_graph_bool:
                ref_thread = threading.Thread(target = self.update_rx_graph)
                ref_thread.start()

    def update_data_array(self, output_array, i):  
        self.data_array[i].append(output_array[i])

    def update_tx_graph(self):

        if self.tx1_plot_bool:
            self.tx1_plot.set_xdata(self.sample_num)
            self.tx1_plot.set_ydata(self.data_array[1])
        if self.tx2_plot_bool:
            self.tx2_plot.set_xdata(self.sample_num)
            self.tx2_plot.set_ydata(self.data_array[2])
        if self.tx3_plot_bool:
            self.tx3_plot.set_xdata(self.sample_num)
            self.tx3_plot.set_ydata(self.data_array[3])
        if self.tx4_plot_bool:
            self.tx4_plot.set_xdata(self.sample_num)
            self.tx4_plot.set_ydata(self.data_array[4])
        if self.tx5_plot_bool:
            self.tx5_plot.set_xdata(self.sample_num)
            self.tx5_plot.set_ydata(self.data_array[5])
        if self.tx6_plot_bool:
            self.tx6_plot.set_xdata(self.sample_num)
            self.tx6_plot.set_ydata(self.data_array[6])

        self.tx_axes.relim()
        self.tx_axes.autoscale_view()

        self.trans_plot.set_xticks([self.sample_num[0],self.sample_num[int(len(self.sample_num)/3)],\
            self.sample_num[int(2*len(self.sample_num)/3)],self.sample_num[-1]])

        self.trans_plot.set_xticklabels([self.data_array[0][0].split('.')[0], \
            self.data_array[0][int(len(self.sample_num)/3)].split('.')[0], \
            self.data_array[0][int(2*len(self.sample_num)/3)].split('.')[0], \
            self.data_array[0][-1].split('.')[0]])

        # show a legend
        self.trans_plot.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True)

        self.trans_canvas.draw()
        self.trans_canvas.flush_events()

    def update_rx_graph(self):

        if self.rx1_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[7])
        if self.rx2_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[8])
        if self.rx3_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[9])
        if self.rx4_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[10])
        if self.rx5_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[11])
        if self.rx6_plot_bool:
            self.rx1_plot.set_xdata(self.sample_num)
            self.rx1_plot.set_ydata(self.data_array[12])

        self.rx_axes.relim()
        self.rx_axes.autoscale_view()

        self.ref_plot.set_xticks([self.sample_num[0],self.sample_num[int(len(self.sample_num)/3)],\
            self.sample_num[int(2*len(self.sample_num)/3)],self.sample_num[-1]])

        self.ref_plot.set_xticklabels([self.data_array[0][0].split('.')[0], \
            self.data_array[0][int(len(self.sample_num)/3)].split('.')[0], \
            self.data_array[0][int(2*len(self.sample_num)/3)].split('.')[0], \
            self.data_array[0][-1].split('.')[0]])

        self.ref_plot.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True)

        self.ref_canvas.draw()

    def graph_settings_pressed(self):
        '''
        Called when the graph settings window is pressed.
        Loads values and updates window-open variables.
        '''
        # if a window is already open, just bring it into focus
        if self.graph_settings_open:
            self.graph_settings_window.graph_settings_view.focus()
        # otherwise, update variables and create a window
        else:
            self.parent.graph_enabled = False
            self.graph_settings_window = HFGraphSettingsGUI(self)
            self.graph_settings_open = True

            # ensure that data is saved on window close
            self.graph_settings_window.graph_settings_view.wm_protocol("WM_DELETE_WINDOW", self.graph_settings_closed)

    def load_graph_settings(self):
        '''
        Loads values from a pickle file. This allows for settings to be modified from the GUI
        and be persistent at the next program launch.
        '''

        # attempt to read the saved data from the pickle file and load the values
        try:
            # read the file
            with open('graph_settings.pckl', "rb") as f:
                # data is a dictionary containing settings
                data = pickle.load(f)

            # load the settings into their proper variables
            self.tx1_plot_enabled.set(data['tx1'])
            self.tx2_plot_enabled.set(data['tx2'])
            self.tx3_plot_enabled.set(data['tx3'])
            self.tx4_plot_enabled.set(data['tx4'])
            self.tx5_plot_enabled.set(data['tx5'])
            self.tx6_plot_enabled.set(data['tx6'])
            self.rx1_plot_enabled.set(data['rx1'])
            self.rx2_plot_enabled.set(data['rx2'])
            self.rx3_plot_enabled.set(data['rx3'])
            self.rx4_plot_enabled.set(data['rx4'])
            self.rx5_plot_enabled.set(data['rx5'])
            self.rx6_plot_enabled.set(data['rx6'])
            self.time_shown_variable.set(data['time_shown'])
            self.graph_update_interval.set(data['update_interval'])


        # if there is an error, load default values for the program
        except Exception as e:
            print("error loading saved state:", str(e))
            print("loading default values")

            tkinter.messagebox.showwarning(
                    "Graph Settings Error",
                    "Error loading saved values.\nResetting to default values.\n\n" + \
                    "Please check the graph settings to ensure values are correct."
                )
            return

            self.tx1_plot_enabled.set(1)
            self.tx2_plot_enabled.set(1)
            self.tx3_plot_enabled.set(1)
            self.tx4_plot_enabled.set(1)
            self.tx5_plot_enabled.set(1)
            self.tx6_plot_enabled.set(1)
            self.rx1_plot_enabled.set(1)
            self.rx2_plot_enabled.set(1)
            self.rx3_plot_enabled.set(1)
            self.rx4_plot_enabled.set(1)
            self.rx5_plot_enabled.set(1)
            self.rx6_plot_enabled.set(1)
            self.time_shown_variable.set('10')
            self.graph_update_interval.set('1')

    def graph_settings_closed(self):
        '''
        Saves the program settings on close of the settings window.
        '''

        # ensure the sample time is a valid int greater than 1
        try:
            if int(self.time_shown_variable.get()) <= 1:
                tkinter.messagebox.showwarning(
                        "Field Error",
                        "Enter an integer greater than 1 in the field."
                    )
                return
        except:
            tkinter.messagebox.showwarning(
                    "Field Error",
                    "Enter a valid integer greater than 1 in the field."
                )
            return

        # if inputs are valid, store the data as a dictionary
        try:
            data = {
                'tx1': self.tx1_plot_enabled.get(),
                'tx2': self.tx2_plot_enabled.get(),
                'tx3': self.tx3_plot_enabled.get(),
                'tx4': self.tx4_plot_enabled.get(),
                'tx5': self.tx5_plot_enabled.get(),
                'tx6': self.tx6_plot_enabled.get(),
                'rx1': self.rx1_plot_enabled.get(),
                'rx2': self.rx2_plot_enabled.get(),
                'rx3': self.rx3_plot_enabled.get(),
                'rx4': self.rx4_plot_enabled.get(),
                'rx5': self.rx5_plot_enabled.get(),
                'rx6': self.rx6_plot_enabled.get(),
                'time_shown': self.time_shown_variable.get(),
                'update_interval': self.graph_update_interval.get(),
            }

            # dump the data into a settings file
            with open('graph_settings.pckl', "wb") as f:
                pickle.dump(data, f)

        # if there's an error, log it
        except Exception as e:
            print("error saving state:", str(e))

        # remove the settings view
        self.graph_settings_window.graph_settings_view.destroy()

        # update window-open variables
        self.graph_settings_open = False
        self.parent.graph_enabled = True

        # reset the graph to update changes
        self.reset_graph()