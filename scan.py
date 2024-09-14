#!/usr/bin/env python3
import serial
# import numpy as np
# import pylab as pl
# import struct
import os
from serial.tools import list_ports
from bin_to_csv import bin_to_csv

VID = 0x0483 #1155
PID = 0x5740 #22336

# Get tinysa device automatically
def getport() -> str:
	device_list = list_ports.comports()
	for device in device_list:
		if device.vid == VID and device.pid == PID:
			return device.device
	raise OSError("device not found")

# REF_LEVEL = (1<<9)

class tinySA:
	def __init__(self, dev = None):
		self.dev = dev or getport()
		self.serial = None
		self.points = 101

	def open(self):
		if self.serial is None:
			self.serial = serial.Serial(self.dev)

	def close(self):
		if self.serial:
			self.serial.close()
		self.serial = None

	def send_command(self, cmd):
		self.open()
		self.serial.write(cmd.encode())
		self.serial.readline() # discard empty line

	def sweep(self, mode):
		self.open()
		self.serial.write(f"sweep {mode}\r".encode())
		self.serial.readline()

	def spur(self, onof):
		self.open()
		if onof:
			self.serial.write("spur on\r".encode())
		else:
			self.serial.write("spur off\r".encode())

		self.serial.readline()

	def abort(self, command=None):
		if (command):
			self.send_command(f"abort {command}\r")
		else:
			self.send_command(f"abort\r")

	def resume(self):
		self.send_command("resume\r")

	def scanraw(self, start_freq, end_freq, points):
		"""
		A generator that reads signal data from TinySA using scanraw command and yields one byte at a time.
		"""

		# Send the scanraw command to TinySA
		self.send_command(f"scanraw {start_freq} {end_freq} {points} 3\r")

		try:
			while True:
				# Read data from the serial port in chunks
				data = self.serial.read(50*points * 3 + 2)  # Reading 50 snapshot at a time
				
				if not data:
					break  # Stop reading if no data is returned
				
				# Yield each byte from the data chunk
				for byte in data:
					yield byte  # Yield one byte at a time

		except KeyboardInterrupt:
			print("Data reading interrupted by user.")
			self.abort()
			self.resume()

		print("Finished reading data")

	def save_signal_data(self, filename, start_freq, end_freq, points, buffer_size=4096):
		"""
		Capture signal data and save it to a binary file using buffered writing.
		:param filename: The name of the file to save the signal data.
		:param buffer_size: The size of the buffer (in bytes) for writing to the file.
		"""
		buffer = bytearray()  # Create an in-memory buffer
		with open(filename, "wb") as f:
			for byte in self.scanraw(start_freq, end_freq, points):
				buffer.append(byte)  # Add the chunk to the buffer
				
				# If the buffer exceeds the buffer_size, write it to the file
				if len(buffer) >= buffer_size:
					f.write(buffer)
					buffer.clear()  # Clear the buffer after writing
				
			# Write any remaining data in the buffer to the file
			if buffer:
				f.write(buffer)
		
		print(f"Signal data saved to {filename}.")
		# Remove .bin extension and add .csv extension
		csvfilename = filename[:-4] + ".csv"
		bin_to_csv(filename, csvfilename, points, start_freq, end_freq)

if __name__ == '__main__':
	from optparse import OptionParser
	parser = OptionParser(usage="%prog: [options]")
	parser.add_option("-S", "--start", 
					  	dest="start",
					  	type="float",
					  	default=100e6,
					  	help="start frequency", 
					  	metavar="START")
	parser.add_option("-E", "--stop", dest="stop",
					  	type="float",
					  	default=800e6,
					  	help="stop frequency", 
					  	metavar="STOP")
	parser.add_option("-N", "--points", dest="points",
					  	type="int", 
					  	default=100,
					  	help="scan points", 
					  	metavar="POINTS")
	parser.add_option("-o", "--output", 
					  	dest="save",
					  	help="write CSV file", 
					  	metavar="SAVE")
	parser.add_option("-f", "--fast", 
						dest="fast_scan",
					  	action="store_true", default=False,
					  	help="perform fast scan")

	(opt, args) = parser.parse_args()

	nv = tinySA(getport())

	print("Scan scanning")
	print(f"Start frequency {opt.start}")
	print(f"Stop frequency {opt.stop}")
	print(f"Number of points {opt.points}")
	# Create recordings directory if it doesn't exist
	recordings_dir = 'recordings'
	if not os.path.exists(recordings_dir):
		os.makedirs(recordings_dir)
	
	file_name = os.path.join(recordings_dir, f"{opt.save}_start{opt.start}_stop{opt.stop}_points{opt.points}.bin")
	# Enable abort
	nv.abort("on")
	if (opt.fast_scan):
		print("Fast scanning")
		nv.spur(False)
		nv.sweep("fast")
	
	print("Press Ctrl+C to stop scanning")
	nv.save_signal_data(file_name, opt.start, opt.stop, opt.points)
	print("Scanning finished")