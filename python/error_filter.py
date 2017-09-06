import csv
import sys
import glob

def filter_file(input_file):
	# import data into array
	data = csv.reader(input_file, delimiter=',')
	table = [row for row in data]

	spike_ct = 0
	timeout_ct = 0

	print("filtering " + str(str(input_file).split("/")[2].split('\'')[0].split('.')[0]) + "... ")

	# open output file
	output_file = open("../data/filtered/" + str(str(input_file).split("/")[2].split('\'')[0].split('.')[0]) + "_filtered.data", 'w')

	# write the header rows
	line1_str = str(table[0]).replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")
	line2_str = str(table[1]).replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")
	line3_str = str(table[2]).replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

	output_file.write(line1_str + "\n")
	output_file.write(line2_str + "\n")
	output_file.write(line3_str + "\n")

	# write the first data row
	try:
		prev_row = table[3]
		cur_row = table[4]
		next_row = table[5]

		out_str = "%s\n" % prev_row
		out_str = out_str.replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

		output_file.write(out_str)
	except:
		print(str(str(input_file).split("/")[2].split('\'')[0].split('.')[0]) + " needs more data points")
		quit()

	# write the middle rows
	for row in range (5, len(table) - 1):

		try:
			for col in range (1, 13):
				# check for random power spikes -- commented out as a change in software fixed most of these.
				# uncomment if you wish to check for power spikes again
				'''
				if prev_row[col] == "000000" and next_row[col] == "000000" and cur_row[col] != "000000":
					try:
						# vast majority of observed error values were in this range
						if float(cur_row[col]) >= 1270 and float(cur_row[col <= 1320]):
							spike_ct += 1
							print("power spike removed at " + cur_row[0])
							cur_row[col] = "000000"
					except:
						pass
				'''
				# check for power meter timeouts
				if cur_row[col] == "      ":
					print("timeout removed at " + cur_row[0])
					timeout_ct += 1
					cur_row[col] = prev_row[col]
		except:
			print("not enough data in row at time " + cur_row[0] + " to filter. skipping this row")

		# write the modified string
		out_str = "%s\n" % cur_row
		out_str = out_str.replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

		output_file.write(out_str)

		# increment rows
		prev_row = cur_row
		cur_row = next_row
		next_row = table[row]

	# write the last few rows
	out_str = "%s\n" % cur_row
	out_str = out_str.replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

	output_file.write(out_str)

	out_str = "%s\n" % next_row
	out_str = out_str.replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

	output_file.write(out_str)

	out_str = "%s\n" % table[row + 1]
	out_str = out_str.replace("[", "").replace("\'", "").replace("]","").replace(", ", ",")

	output_file.write(out_str)

	print("filtered. number of power spikes removed: " + str(spike_ct) + ", number of timeouts removed: " + \
		str(timeout_ct) + "\n")

# open input file
try:
	if ".data" not in sys.argv[1]:
		try:
			input_file = open("../data/" + sys.argv[1] + ".data", 'r')
		except:
			print("Could not locate file")
	else:
		input_file = open("../data/" + sys.argv[1], 'r')
	filter_file(input_file)
except:
	file_list = glob.glob('../data/*.data')
	for file_name in file_list:
		input_file = open(file_name)
		filter_file(input_file)
