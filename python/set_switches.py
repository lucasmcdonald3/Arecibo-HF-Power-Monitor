try:
	import RPi.GPIO as GPIO
except:
	pass

# default pins are for transmitted meter
def set_switch(num, decoderBitA = 11, decoderBitB = 12, decoderBitC = 13):
	'''
	Converts the selected transmitter input into three bits
	to control the decoder on the HMC252.
	'''

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(decoderBitA, GPIO.OUT)                        
	GPIO.setup(decoderBitB, GPIO.OUT)
	GPIO.setup(decoderBitC, GPIO.OUT)

	if num == 1:
		GPIO.output(decoderBitA, GPIO.LOW)         
		GPIO.output(decoderBitB, GPIO.LOW)
		GPIO.output(decoderBitC, GPIO.LOW)
	# Set the second input (etc.)
	elif num == 2:
		GPIO.output(decoderBitA, GPIO.HIGH)
		GPIO.output(decoderBitB, GPIO.LOW)
		GPIO.output(decoderBitC, GPIO.LOW)
	elif num == 3:
		GPIO.output(decoderBitA, GPIO.LOW)
		GPIO.output(decoderBitB, GPIO.HIGH)
		GPIO.output(decoderBitC, GPIO.LOW)
	elif num == 4:
		GPIO.output(decoderBitA, GPIO.HIGH)
		GPIO.output(decoderBitB, GPIO.HIGH)
		GPIO.output(decoderBitC, GPIO.LOW)
	elif num == 5:
		GPIO.output(decoderBitA, GPIO.LOW)
		GPIO.output(decoderBitB, GPIO.LOW)
		GPIO.output(decoderBitC, GPIO.HIGH)
	elif num == 6:
		GPIO.output(decoderBitA, GPIO.HIGH)
		GPIO.output(decoderBitB, GPIO.LOW)
		GPIO.output(decoderBitC, GPIO.HIGH)
	# 7 and 8 both correspond to the ALL OFF state (i.e. nothing connected
	# to the output)
	elif num == 7 or num == 8:
		GPIO.output(decoderBitA, GPIO.HIGH)
		GPIO.output(decoderBitB, GPIO.HIGH)
		GPIO.output(decoderBitC, GPIO.HIGH)