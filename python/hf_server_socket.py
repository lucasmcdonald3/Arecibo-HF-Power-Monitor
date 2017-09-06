#!usr/bin/env python3

'''
    File: hf_server_socket.py
    Description: File to be run on the RPi. Handles send/receive requests to
        read the power meters/write data. Server is hosted on port 12345.
    Author: Lucas McDonald
    Date created: June 26, 2017
    Date modified: August 2, 2017
    Python version: 3.6.1
'''

import socketserver
import socket
import set_switches
import pickle
import time
import threading
import take_data
import sys

class RPiServer(socketserver.BaseRequestHandler):

    def receive_data(self):
        # receive data file from the server
        try:

            received = self.request.recv(1024).strip()
            print(str(received))

            # unpack data file into array
            output_array = pickle.loads(received)
            for element in output_array:
                print(element)

            return received

        except EOFError:
            print("No data received")
            return 
        

    def handle(self):
        '''
        Handles the request made by the client. Retrieves the command from the input and
        calls the approprite method.
        '''

        # put the data from the transmitted pickle file into an array
        self.data = self.receive_data()
        self.sock_open = True

        try:
            self.data_arr = pickle.loads(self.data)
        except:
            self.data_arr = ["none"]

        # call the appropriate method from the command. The command is sent in the 0th element of the array.
        if(self.data_arr[0] == 'mon_all'):
            self.rpi_monitor()
        elif(self.data_arr[0] == 'rec_all'):
            self.rpi_record()
        elif(self.data_arr[0] == 'set_switch'):
            self.rpi_switch()
        else:
            pass
        print("Request handled")

    def send_output(self, output_array):
        # send the array as a pickle file
        self.pickled_output = pickle.dumps(self.output_array)
        try:
            self.request.sendall(self.pickled_output)
        except:
            self.sock_open = False
        return

        
    def rpi_monitor(self):
        '''
        Monitors the power from the power meters and sends the data to the client.
        '''

        # put the power meters into fast sampling mode
        take_data.open_PM_URL("http://" + str(self.data_arr[4]) + '/:MODE:1', 2.0, True)
        take_data.open_PM_URL("http://" + str(self.data_arr[5]) + '/:MODE:1', 2.0, True)

        pi_to_tx_tn = []
        pi_to_rx_tn = []

        if(self.data_arr[6]):
            pi_to_tx_tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pi_to_tx_tn.settimeout(.5)
            # connect to server
            pi_to_tx_tn.connect((str(self.data_arr[4]), 23))
            # clear the input to the telnet console (tends to start with some input)
            pi_to_tx_tn.sendall(b':POWER?\n\r')

        if(self.data_arr[7]):
            pi_to_rx_tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pi_to_rx_tn.settimeout(.5)
            # connect to server
            pi_to_rx_tn.connect((str(self.data_arr[5]), 23))
            # clear the input to the telnet console (tends to start with some input)
            pi_to_rx_tn.sendall(b':POWER?\n\r')

        while self.sock_open:

            try:
                # get the output from monitor_power
                self.output_array = take_data.monitor_power(self.data_arr[1], self.data_arr[2], \
                    self.data_arr[3], pi_to_tx_tn, pi_to_rx_tn, self.data_arr[6], self.data_arr[7])

                for element in self.output_array:
                    print(element)

                # update the UI according to the power and units
                send_thread = threading.Thread(target = self.send_output, args = [self.output_array])
                send_thread.start()

                # sleep for the designated time
                sample_period = float(self.data_arr[2])
                time_for_cycle = float(self.output_array[-1])
                if sample_period > time_for_cycle - .02:
                    time.sleep(sample_period - time_for_cycle - .02)
                if not self.sock_open:
                    return
            
            except:
                print("Socket closed unexpectedly")
                pi_to_tx_tn.close()
                pi_to_rx_tn.close()
                return

        pi_to_tx_tn.close()
        pi_to_rx_tn.close()
                
    def rpi_record(self):
        '''
        Monitors the power from the power meters and sends the data to the client. Also writes the
        data to a file stored on the RPi in /home/pi/hfmon/data.
        '''

        # put the power meters into 'faster' sampling mode
        take_data.open_PM_URL("http://" + str(self.data_arr[4]) + '/:MODE:1', 2.0, True)
        take_data.open_PM_URL("http://" + str(self.data_arr[5]) + '/:MODE:1', 2.0, True)

        # telnet socket variables
        pi_to_tx_tn = []
        pi_to_rx_tn = []

        # open socket if the devices should connected
        if(self.data_arr[6]):
            pi_to_tx_tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pi_to_tx_tn.settimeout(.5)
            # connect to server
            pi_to_tx_tn.connect((str(self.data_arr[4]), 23))
            # clear the input to the telnet console (tends to start with some input)
            pi_to_tx_tn.sendall(b':POWER?\n\r')

        if(self.data_arr[7]):
            pi_to_rx_tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pi_to_rx_tn.settimeout(.5)
            # connect to server
            pi_to_rx_tn.connect((str(self.data_arr[5], 23)))
            pi_to_rx_tn.sendall(b':POWER?\n\r')

        while self.sock_open:
            try:
                # get the output from monitor_power
                self.output_array = take_data.record_power(self.data_arr[1], self.data_arr[2], \
                    self.data_arr[3], pi_to_tx_tn, pi_to_rx_tn, self.data_arr[6], self.data_arr[7])

                # update the UI according to the power and units
                send_thread = threading.Thread(target = self.send_output, args = [self.output_array])
                send_thread.start()

                # sleep for the designated time
                sample_period = float(self.data_arr[2])
                time_for_cycle = float(self.output_array[-1])
                if sample_period > time_for_cycle - .02:
                    time.sleep(sample_period - time_for_cycle - .019)
                if not self.sock_open:
                    return
            except:
                print("Socket closed unexpectedly")
                pi_to_tx_tn.close()
                pi_to_rx_tn.close()
                return

        pi_to_tx_tn.close()
        pi_to_rx_tn.close()

    def rpi_switch(self):
        '''
        Sets the RF switch to the specified input.
        '''
        
        set_switches.set_switch(self.data_arr[1], self.data_arr[2], self.data_arr[3], self.data_arr[4])
        output_array = ["success"]
        self.pickled_output = pickle.dumps(output_array)
        self.request.sendall(self.pickled_output)

if __name__ == "__main__":

    try:
        # read the file
        with open('/home/pi/hfmon/python/gui_settings.pckl', "rb") as f:
            # data is a dictionary containing settings
            data = pickle.load(f)

        rpi_ip = data["rpi_ip"]
        print(rpi_ip)

    # if there is an error, load default values for the program
    except Exception as e:

        print("\n\nWARNING:\nError loading settings. Default settings loaded.\n")
        print("Check the program settings to ensure the settings are correct (\"settings\" command).")

        rpi_ip = "192.168.100.153"

    server = socketserver.TCPServer((rpi_ip, 12345), RPiServer)

    # activate the server
    server.serve_forever()

server = RPiServer