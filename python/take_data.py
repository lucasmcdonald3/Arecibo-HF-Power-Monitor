#!usr/bin/env python3

'''
	File: take_data.py
	Description: A set of methods for writing and recording data
		from each of the 6 HF transmitters.
	Author: Lucas McDonald
	Date created: June 2, 2017
	Date modified: August 2, 2017
	Python version: 3.6.1
'''

from urllib.request import urlopen
from datetime import datetime, timedelta
from set_switches import set_switch
import os.path
import time
from socket import timeout
import threading
import telnetlib
import sys

def str_To_dBm(input_str, correction):
	'''
	Converts the received power in dBm from HTML format to
	dBm in a String format with six digits.
	'''

	power_dbm = ""
	try:
		# power is "-99.000 dBm\n\r", so get the number only
		power_dbm = input_str.split(' ')[0]
		power_dbm = str(float(power_dbm) + correction)
	# if there are any errors, return the error string of spaces
	except:
		power_dbm = "      "

	return power_dbm

def open_PM_URL(url, given_timeout, enabled):
	'''
	Opens the URL to a power meter and handles
	any issues with opening that URL (timeout, etc.)
	'''

	if enabled:
		try:
			# open URL, return HTML from that webpage
			return urlopen(url, data = None, timeout = given_timeout)
		except:
			# print the error and quit the program
			print("Unable to connect to the power meter with IP " + url.split('/')[2])
			return "      "
			enabled = False

def get_PM_power_tn(tn, timeout, enabled):
	'''
	Sends the power request to the power meter via Telnet. Retrieves a bytestring and
	returns its ASCII representation.
	'''

	tn.sendall(b':POWER?\n\r')
	output = tn.recv(1024).decode()
	print(output)
	return output

	'''
	tn.write(":POWER?\r\n".encode("ascii"))
	output = tn.read_eager().decode()
	print(output)
	return output
	'''

def record_power(timeout_secs, sample_time, decoder_pins, transmitted_tn, reflected_tn, \
	trans_enabled, reflect_enabled):
	'''
	Writes to a file located at ../data/[todaysdate].data and returns an array
	containing [time measurement started, Tx1, Rx1, Tx2, Rx2, .... Rx6, time taken to sample all 6].
	'''

	# YMD format for dating
	# start the line with the current time in HH:MM:SS.SSS
	cycle_start_time = datetime.now() - timedelta(hours = 4)
	cur_time = str(cycle_start_time).split(' ')[1][0:12]

	todays_date = str(cycle_start_time).split(' ')[0].replace('-', '')

	# if there isn't already a data file, make a new file
	if not os.path.isfile('/home/pi/hfmon/data/' + todays_date + '.data'):

		#create a new file
		data_file = open('/home/pi/hfmon/data/' + todays_date + '.data', 'w+')

		# write some header info
		data_file.write('#HF transmitted power data for ' + str(cycle_start_time).split(' ')[0] + '\n')
		data_file.write('#HH:MM:SS.SSS, Tx1 , Tx2  , Tx3  , Tx4  , Tx5  , Tx6  , Rx1  , Rx2  , Rx3  , Rx4  , Rx5  , Rx6  , time to take sample\n')

	# open file with today's date in format YY:MM:DD
	data_file = open('/home/pi/hfmon/data/' + todays_date + '.data', 'a')

	# get output array
	output = []

	data_file.write('\n')

	data_file.write(cur_time + ',')
	output.append(cur_time)

	# get forward and reflected power from individal threads
	threads = []

	trans_out = []
	if trans_enabled:
		transmitted_thread = threading.Thread(target = get_direction_power_array, args = [cycle_start_time, trans_out, 'forward', \
			timeout_secs, decoder_pins[0], decoder_pins[1], decoder_pins[2], transmitted_tn])
		threads.append(transmitted_thread)
		transmitted_thread.start()
	else:
		trans_out = ['      ', '      ', '      ', '      ', '      ', '      ', ]

	ref_out = []
	if reflect_enabled:
		reflected_thread = threading.Thread(target = get_direction_power_array, args = [cycle_start_time, ref_out, 'reflected', \
			timeout_secs, decoder_pins[3], decoder_pins[4], decoder_pins[5], reflected_tn])
		threads.append(reflected_thread)
		reflected_thread.start()
	else:
		ref_out = ['      ', '      ', '      ', '      ', '      ', '      ', ]

	# check to see if both forward and reflected power threads are done
	while len(threads) != 0:
		for t in threads:
			if not t.isAlive():
				threads.remove(t)

	# put each element into the output array
	for element in trans_out:
		output.append(element)
		try:
			power_watts = int(pow(10, float(element) / 10) / 1000)
			data_file.write(str(power_watts).zfill(6) + ',')
		except:
			data_file.write('      ,')

	for element in ref_out:
		output.append(element)
		try:
			power_watts = int(pow(10, float(element) / 10) / 1000)
			data_file.write(str(power_watts).zfill(6) + ',')
		except:
			data_file.write('      ,')

	# add the amount of time needed to complete the cycle
	time_for_cycle = str(datetime.now() - timedelta(hours = 4) - cycle_start_time)[6:13]
	print(str(datetime.now() - timedelta(hours = 4) - cycle_start_time)[6:13])
	output.append(time_for_cycle)
	data_file.write(time_for_cycle)

	return output

def monitor_power(timeout_secs, sample_time, decoder_pins, transmitted_tn, \
			reflected_tn, trans_enabled, reflect_enabled):
	'''
	Called by the monitor power button. Gets the power from each transmitter (and reflected)
	and returns an array containing
	[time started, Tx1, Tx2, ..., Tx6, Rx1, Rx2, ..., Rx6, time taken to sample power].
	'''

	cycle_start_time = datetime.now() - timedelta(hours = 4)
	cur_time = str(cycle_start_time).split(' ')[1][0:12]

	# get output array
	output = []

	output.append(cur_time)

	# get forward and reflected power from individal threads
	threads = []

	trans_out = []
	if trans_enabled:
		transmitted_thread = threading.Thread(target = get_direction_power_array, args = [cycle_start_time, trans_out,'forward', \
			timeout_secs, decoder_pins[0], decoder_pins[1], decoder_pins[2], transmitted_tn])
		threads.append(transmitted_thread)
		transmitted_thread.start()
	else:
		trans_out = ['      ', '      ', '      ', '      ', '      ', '      ', ]

	ref_out = []
	if reflect_enabled:
		reflected_thread = threading.Thread(target = get_direction_power_array, args = [cycle_start_time, ref_out, 'reflected', \
			timeout_secs, decoder_pins[3], decoder_pins[4], decoder_pins[5], reflected_tn])
		threads.append(reflected_thread)
		reflected_thread.start()
	else:
		ref_out = ['      ', '      ', '      ', '      ', '      ', '      ', ]

	# check to see if both forward and reflected power threads are done
	while len(threads) != 0:
		for t in threads:
			if not t.isAlive():
				threads.remove(t)

	# put each element into the output array
	for element in trans_out:
		output.append(element)
	for element in ref_out:
		output.append(element)

	# add the amount of time needed to complete the cycle
	time_for_cycle = str(datetime.now() - timedelta(hours = 4) - cycle_start_time)[6:13]
	output.append(time_for_cycle)

	return output

def get_direction_power(cycle_start_time, transmitter, direction, timeout_secs, decoderBitA, decoderBitB, \
	decoderBitC, tn):
	'''
	Takes in the number of the transmitter as an argument and returns the power at that transmitter.
	Returns an array containing [forward power for transmitter, reflected power for transmitter] in dBm,
	or if there is an error taking the reading, returns '      ' (6 spaces (for formatting)).
	'''

	'''
	Correction factors for each transmitter in dB.
	First element is the transmitted power correction, second element is reflected power correction.
	Each transmitted input has a 10 dB attenuator.
	Reflected inputs 1, 2, and 3 have 8 dB attenuators, while 4, 5, and 6 have 5 dB attenuators.
	'''
	correction_dict = {1: [73, 61], 2: [73, 61], 3: [73, 61], 4: [73, 51.157], 5: [73, 61], 6: [73, 61]}

	# set the HMC252 to the correct transmitter
	set_switch(transmitter, decoderBitA, decoderBitB, decoderBitC)

	# sleeping briefly reduces errors due to switches taking a while to switch
	# time.sleep(.01)

	# get the correction factor for the transmitter/direction
	if direction == 'forward':
		correction = correction_dict[transmitter][0]
	else:
		correction = correction_dict[transmitter][1]

	# open the URL to the power meter whose HTML contains the power in dBm
	#url = open_PM_URL(ip + '/:POWER?', timeout_secs, True)
	output = get_PM_power_tn(tn, timeout_secs, True)
	print(output)

	'''
	If the reading errored, '      ' is produced. This is due to consistency in formatting
	with the recording file.
	'''

	# convert the HTML to a value in dBm
	return str_To_dBm(output, correction)

def get_direction_power_array(cycle_start_time, output, direction, timeout_secs, decoderBitA, decoderBitB, \
	decoderBitC, tn):
	'''
	Returns an array containing the power in a single direction for each transmitter.
	i.e., if direction == 'transmitted', returns [Tx1, Tx2, Tx3, Tx4, Tx5, Tx6].
	'''

	for transmitter in range (1, 7):
		output.append(get_direction_power(cycle_start_time, transmitter, direction, timeout_secs, \
		  decoderBitA, decoderBitB, decoderBitC, tn))
